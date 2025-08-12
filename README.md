# 🎵 Amazon Music to Spotify Playlist Converter

Amazon Music does not currently offer a public API for developers, making it difficult to programmatically access or transfer playlists. To work around this limitation, this project uses **GUI automation** to scrape song data directly from public Amazon Music playlist web pages. Once extracted and cleaned, the script leverages **Spotify’s Web API** to recreate the exact same playlist on the user’s Spotify account — enabling seamless migration between platforms.

The tool now includes **two main workflows**:
- **main.py** – Interactive mode where the user pastes a playlist URL and can choose to:
  - Create a new Spotify playlist
  - Sync (update) an existing playlist if one with the same name is found  
- **sync.py** – Automated mode that reads playlist URLs from a text file and syncs them all without user prompts.

In addition to the command-line interface, the project now includes a **desktop GUI**, which provides:
- A visually styled interface with dark mode
- Real-time logs of scraping and uploading processes  
- Prompted input collection through popup dialogs  
- Easy-to-use buttons for starting or exiting the conversion  

This makes the entire playlist transfer experience more user-friendly and accessible.


<p align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=py,github" />
  </a>
</p>



## Features

- Works on **Windows** and **macOS** with automatic Chrome path detection.
- Scrapes song titles and artists from Amazon Music using simulated GUI actions.
- Cleans and formats raw data for accuracy.
- Recreates the playlist on Spotify with real track matching.
- Detects duplicate playlist names and gives the option to sync instead of creating a duplicate.
- Batch-sync multiple playlists from a `.txt` file using `sync.py`.
- Logs unfound songs for review.
- Multithreaded search for faster execution.
- Organized output folders: `music_data/`, `not_found_songs/`



## Tools & Libraries Used

- `pyautogui`, `pyperclip` – GUI automation
- `spotipy` – Spotify Web API wrapper
- `pandas`, `csv`, `re` – Data parsing and cleaning
- `requests`, `dotenv`, `concurrent.futures`, `logging`, `os`, `sys`, `subprocess`, `time`, `random` – Utility & network handling
- `PyQt5` – Desktop GUI for visual control and user input



## Installation

```bash
git clone https://github.com/AshvikMishra/trackSwap
cd trackSwap
pip install -r requirements.txt
```



## Environment Setup

Create a `.env` file in your project directory and add the following:

```env
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8000/callback
```

Get these details by making a spotify developer account and application [here](https://developer.spotify.com/dashboard).



## Usage
### Interactive Mode

```bash
python main.py
```

1. Paste your Amazon Music **public** playlist link when prompted.
2. The script scrapes songs and saves raw data.
3. It cleans and processes the data.
4. It will create the playlist and upload the found tracks.

### Automatic Mode
```bash
python sync.py
```
1. Add one playlist URL per line in playlists.txt.
2. The script will automatically scrape, process, and sync all listed playlists.



## Output Folders

- `music_data/amazon_playlist_raw.txt` : Raw extracted text  
- `music_data/amazon_playlist.csv` : Cleaned playlist data  
- `not_found_songs/` : Songs that couldn’t be matched on Spotify  



## Troubleshooting

- Ensure your Amazon Music playlist is **public** and fully loaded before scraping (increase the time.sleep() on slower connections).
- Run in a clean desktop environment to avoid interference with GUI automation.  
- Use a fresh Spotify token if facing authentication errors. 
- If browser is not found then change it's directory in `scraper.py`



## License

MIT License