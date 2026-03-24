import pyautogui

def capture_screenshot(path='screenshot.png'):
    image = pyautogui.screenshot()
    image.save(path)
    return path
