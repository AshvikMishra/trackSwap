import pyautogui
import pyperclip
import time
import subprocess
import os
import sys

# Folder setup
SCRAPE_FOLDER = "music_data"
os.makedirs(SCRAPE_FOLDER, exist_ok=True)

RAW_TEXT_FILE = os.path.join(SCRAPE_FOLDER, "amazon_playlist_raw.txt")

def open_incognito_chrome(url):
    chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    try:
        subprocess.Popen([chrome_path, "--incognito", url])
    except FileNotFoundError:
        print("❌ Chrome not found at the specified path.")
        sys.exit(1)

def main():
    playlist_url = input("🔗 Paste your Amazon Music playlist URL: ").strip()

    print("🌐 Opening playlist in incognito Chrome...")
    open_incognito_chrome(playlist_url)
    time.sleep(20)

    print("⌨️ Copying playlist content...")
    pyautogui.hotkey("ctrl", "a")
    time.sleep(1)
    pyautogui.hotkey("ctrl", "c")
    time.sleep(1)

    print("🔒 Closing browser tab and switching to VSCode...")
    pyautogui.hotkey("ctrl", "w")
    time.sleep(1)

    raw_text = pyperclip.paste()
    with open(RAW_TEXT_FILE, "w", encoding="utf-8") as f:
        f.write(raw_text)
    print(f"📝 Raw text saved to {RAW_TEXT_FILE}")

if __name__ == "__main__":
    main()