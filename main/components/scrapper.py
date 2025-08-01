import pyautogui
import pyperclip
import time
import subprocess
import os
import sys
import platform

# Determine OS-specific modifier key
if platform.system() == "Darwin":
    modifier = "command"
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif platform.system() == "Windows":
    modifier = "ctrl"
    chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
else:
    print("❌ Unsupported operating system.")
    sys.exit(1)

# Folder setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRAPE_FOLDER = os.path.join(BASE_DIR, "music_data")
os.makedirs(SCRAPE_FOLDER, exist_ok=True)

RAW_TEXT_FILE = os.path.join(SCRAPE_FOLDER, "amazon_playlist_raw.txt")

def open_incognito_chrome(url):
    try:
        subprocess.Popen([chrome_path, "--incognito", url])
    except FileNotFoundError:
        print("❌ Chrome not found at the specified path.")
        sys.exit(1)

def main():
    playlist_url = input("🔗 Paste your Amazon Music playlist URL: ").strip()

    print("🌐 Opening playlist in incognito Chrome...")
    open_incognito_chrome(playlist_url)
    time.sleep(20)  # Let page load

    print("⌨️ Copying playlist content...")
    pyautogui.hotkey(modifier, "a")
    time.sleep(1)
    pyautogui.hotkey(modifier, "c")
    time.sleep(1)

    print("🔒 Closing browser tab and switching to VSCode...")
    pyautogui.hotkey(modifier, "w")
    time.sleep(1)

    raw_text = pyperclip.paste()
    with open(RAW_TEXT_FILE, "w", encoding="utf-8") as f:
        f.write(raw_text)
    print(f"📝 Raw text saved to {RAW_TEXT_FILE}")

if __name__ == "__main__":
    main()