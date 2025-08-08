import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import re
import time
import random
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import HTTPError
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def main():
    # Enable logging
    logging.basicConfig(level=logging.INFO)

    # Load environment variables
    load_dotenv()

    # Spotify authentication with retry-capable session
    scope = "playlist-modify-public"
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope), requests_session=session)

    # Extract playlist name from line 9 of the raw Amazon file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    raw_file_path = os.path.join(BASE_DIR, "music_data", "amazon_playlist_raw.txt")

    try:
        with open(raw_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            playlist_name = lines[8].strip() if len(lines) >= 9 else "Converted from Amazon Music"
    except Exception as e:
        print(f"⚠️ Could not read playlist name from file: {e}")
        playlist_name = "Converted from Amazon Music"

    if not playlist_name:
        playlist_name = "Converted from Amazon Music"

    def sanitize_filename(name):
        return re.sub(r'[^\w\-_. ]', '_', name)

    # Read CSV
    csv_path = os.path.join(BASE_DIR, "music_data", "amazon_playlist.csv")
    df = pd.read_csv(csv_path)

    # Create playlist
    user_id = sp.current_user()["id"]
    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True)
    playlist_id = playlist["id"]

    def clean_track_name(name):
        name = re.sub(r"\s*\([^)]*\)", "", name)  # remove (parentheses)
        name = re.sub(r"\s*\[[^]]*\]", "", name)  # remove [brackets]
        name = re.sub(r"(?i)(Original Motion Picture Soundtrack|From.*Album)", "", name)
        return name.lower().strip()

    def clean_artist_name(name):
        return re.sub(r"(?i)( - topic|official|music|audio)", "", name.lower()).strip()

    def expand_artists(artist):
        parts = re.split(r",|&|feat\.|Feat\.|featuring|Featuring", artist)
        return [clean_artist_name(p) for p in parts if p.strip()]

    UNWANTED_KEYWORDS = [
        "remix", "lofi", "lo-fi", "chill", "version", "cover", "mix", "edit",
        "acoustic", "reverb", "slowed", "speedup", "sped up", "nightcore", "karaoke", "reprise"
    ]

    def normalize_text(s):
        """
        Lowercase, remove punctuation except spaces, and collapse multiple spaces.
        """
        s = s.lower()
        s = re.sub(r"[^\w\s]", " ", s)  # replace punctuation with space
        s = re.sub(r"\s+", " ", s)      # collapse spaces
        return s.strip()

    def is_unwanted_version(track_name, raw_track):
        """
        Return True if track_name looks like an unwanted variant
        BUT allow if the original/raw track explicitly mentions the same keyword
        (punctuation/spacing differences ignored).
        """
        norm_name = normalize_text(track_name)
        norm_raw = normalize_text(raw_track)
        for bad in UNWANTED_KEYWORDS:
            bad_norm = normalize_text(bad)
            if bad_norm in norm_name and bad_norm not in norm_raw:
                return True
        return False

    def search_track(raw_track, clean_track, artist):
        clean_track = clean_track.lower()
        artist_variants = expand_artists(artist)
        query_variants = [
            f"track:{clean_track} artist:{artist}",
            f"{clean_track} {artist}",
            f"{clean_track}",
            f"{clean_track.split('-')[0].strip()} {artist}"
        ]
        for alt_artist in artist_variants:
            query_variants.append(f"track:{clean_track} artist:{alt_artist}")
            query_variants.append(f"{clean_track} {alt_artist}")

        for query in query_variants:
            try:
                results = sp.search(q=query, type="track", limit=5)
                time.sleep(random.uniform(0.1, 0.3))  # throttle
                items = results["tracks"]["items"]
                for item in items:
                    if not is_unwanted_version(item["name"], raw_track):
                        return (True, item["uri"], raw_track, artist)
            except HTTPError as e:
                if e.response.status_code == 429:
                    retry_after = int(e.response.headers.get("Retry-After", 1))
                    print(f"⚠️ Rate limited. Retrying in {retry_after}s for: {raw_track}...")
                    time.sleep(retry_after + random.uniform(0.5, 1.5))
                else:
                    break
            except Exception as e:
                print(f"❌ Error searching {raw_track}: {e}")
                break
        return (False, None, raw_track, artist)

    def safe_add_items(sp, playlist_id, items):
        retries = 3
        while retries > 0:
            try:
                sp.playlist_add_items(playlist_id, items)
                return
            except HTTPError as e:
                if e.response.status_code == 429:
                    retry_after = int(e.response.headers.get("Retry-After", 1))
                    print(f"⚠️ Rate limited while adding items. Retrying in {retry_after}s...")
                    time.sleep(retry_after + random.uniform(0.5, 1.5))
                    retries -= 1
                else:
                    raise
            except Exception as e:
                print(f"❌ Unexpected error adding items: {e}")
                break

    # Prepare search inputs
    queries = []
    for _, row in df.iterrows():
        raw_track = str(row["Title"]).strip()
        clean_track = clean_track_name(raw_track)
        artist = str(row["Artist"]).strip()
        queries.append((raw_track, clean_track, artist))

    track_uris = []
    not_found = []

    # Search tracks with controlled concurrency
    print("🔍 Searching for tracks on Spotify...")
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_query = {executor.submit(search_track, *q): q for q in queries}
        for future in as_completed(future_to_query):
            found, uri, raw_track, artist = future.result()
            if found:
                track_uris.append(uri)
            else:
                not_found.append(f"{raw_track} by {artist}")

    # Add found tracks to the playlist in batches
    print(f"🎧 Adding {len(track_uris)} tracks to playlist...")
    for i in range(0, len(track_uris), 100):
        safe_add_items(sp, playlist_id, track_uris[i:i + 100])

    # Final report
    print(f"\n✅ Playlist '{playlist_name}' created with {len(track_uris)} tracks.")

    if not_found:
        print("\n⚠️ Some songs were not found:")
        for line in not_found:
            print(" -", line)

        folder = "not_found_songs"
        os.makedirs(folder, exist_ok=True)
        safe_name = sanitize_filename(playlist_name)
        not_found_file = os.path.join(folder, f"{safe_name}_tracks_not_found.txt")

        with open(not_found_file, "w", encoding="utf-8") as f:
            for line in not_found:
                f.write(line + "\n")

        print(f"📄 Not-found songs saved to '{not_found_file}'")
    else:
        print("\n🎉 All songs were successfully added!")

if __name__ == "__main__":
    main()
