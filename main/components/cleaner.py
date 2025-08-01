import os
import csv
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRAPE_FOLDER = os.path.join(BASE_DIR, "music_data")
RAW_TEXT_FILE = os.path.join(SCRAPE_FOLDER, "amazon_playlist_raw.txt")
CLEAN_CSV_FILE = os.path.join(SCRAPE_FOLDER, "amazon_playlist.csv")

BAD_VALUES = {"Search", "Contact Us", "Sorry, something went wrong"}

def is_valid_artist(artist):
    return artist not in BAD_VALUES and not artist.lower().endswith("soundtrack")

def clean_amazon_playlist(input_file_path, output_file_path):
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ Error: The file '{input_file_path}' was not found.")
        return False

    playlist_data = [["Number", "Title", "Artist"]]
    i = 0
    while i + 2 < len(lines):
        if lines[i].isdigit():
            number = lines[i]
            title = lines[i + 1]
            artist = lines[i + 3]

            if title and artist:
                playlist_data.append([number, title, artist])
                i += 3
            else:
                i += 1
        else:
            i += 1

    if len(playlist_data) > 1:
        try:
            with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
                writer.writerows(playlist_data)
            print(f"✅ Successfully saved {len(playlist_data)-1} songs to: {output_file_path}")
            return True
        except IOError as e:
            print(f"❌ Write error: {e}")
            return False
    else:
        print("⚠️ No valid songs found.")
        return False

def main():
    print("🧼 Cleaning Amazon playlist data...")
    clean_amazon_playlist(RAW_TEXT_FILE, CLEAN_CSV_FILE)