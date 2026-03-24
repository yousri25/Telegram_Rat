# ⚠️ Telegram RAT (Educational Project)

## ⚠️ Disclaimer
This project is intended for **educational and cybersecurity research purposes only**.

- Do NOT use this software on systems you do not own or have explicit permission to test.
- The author does NOT support or encourage malicious activity.
- You are solely responsible for any misuse or damage caused.

⚠️ Always run this project in a **safe and isolated environment** (e.g., virtual machines).

---

## 📖 Overview
This project demonstrates a **Remote Access Trojan (RAT)** that uses Telegram as a Command & Control (C2) channel.

Instead of using a traditional server, the RAT communicates through a Telegram bot, allowing remote interaction with an infected system.

This technique is commonly observed in real-world malware, where attackers leverage legitimate platforms to avoid detection and simplify infrastructure :contentReference[oaicite:0]{index=0}.

---

## 🎯 Educational Objectives
This project helps cybersecurity learners:

- Understand how RATs operate
- Learn about C2 communication using messaging platforms
- Analyze common malware behaviors
- Practice malware detection and analysis
- Improve incident response skills

---

## 🔧 Features

### 🕵️ Surveillance Capabilities
- System information gathering
- Screenshot capture
- Process monitoring
- (Optional) Keylogging functionality

### 📁 File System Operations
- File upload/download via Telegram
- Directory navigation
- File listing

### ⚡ System Control
- Remote command execution
- System control (shutdown/reboot)
- Message display on target machine

---

## 🔄 How It Works
1. A Telegram bot is created
2. The RAT connects to the bot using a token
3. Commands are sent via Telegram chat
4. The infected machine executes commands and sends results back

This removes the need for a dedicated C2 server and leverages Telegram’s infrastructure for communication.

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.x
- Telegram Bot Token (via @BotFather)
- Telegram Chat ID

### 1. Clone the Repository
```bash
git clone https://github.com/yousri25/telegram_rat.git
cd telegram_rat
```

### 2. Configure the Bot
Edit the script and add:

```python
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
```

### 3. Run the Script
```bash
python main.py
```

---

## 🎮 Example Commands
```
/info          - Get system information
/screenshot    - Capture screen
/cmd <command> - Execute command
/ls            - List files
/download      - Download file
/upload        - Upload file
```

---

## 🛡️ Security & Ethics
Remote Access Trojans (RATs) are widely used in cyberattacks to:

- Steal sensitive data
- Monitor user activity
- Control infected systems remotely :contentReference[oaicite:1]{index=1}  

Understanding how they work is essential for building effective defenses and improving cybersecurity awareness.

---

## 🚧 Limitations
- Basic implementation (not production-level)
- Limited stealth and evasion techniques
- Intended for learning, not real-world deployment

---

## 📜 License
This project is open-source and intended strictly for **educational use only**.
