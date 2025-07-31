# 🎵 Amazon Music to Spotify Playlist Converter

Amazon Music does not currently offer a public API for developers, making it difficult to programmatically access or transfer playlists. To work around this limitation, this project uses GUI automation to scrape song data directly from public Amazon Music playlist web pages. Once extracted and cleaned, the script leverages Spotify’s robust Web API to recreate the exact same playlist on the user’s Spotify account — enabling seamless migration between platforms.

<p align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=py,github" />
  </a>
</p>



## Features

- Scrapes song titles and artists from Amazon Music using simulated GUI actions.
- Cleans and formats raw data for accuracy.
- Recreates the playlist on Spotify with real track matching.
- Logs unfound songs for review.
- Multithreaded search for faster execution.
- Organized output folders: `scraping_data/`, `not_found_songs/`



## Tools & Libraries Used

- `pyautogui`, `pyperclip` – GUI automation
- `spotipy` – Spotify Web API wrapper
- `pandas`, `csv`, `re` – Data parsing and cleaning
- `requests`, `dotenv`, `concurrent.futures`, `logging`, `os`, `sys`, `subprocess`, `time`, `random` – Utility & network handling



## Installation

```bash
git clone https://github.com/your-username/amazon-to-spotify
cd amazon-to-spotify
pip install -r requirements.txt
```

## Environment Setup

Create a `.env` file in your project directory and add the following:

```env
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8000/callback
```

## Usage

```bash
python main.py
```


1. Paste your Amazon Music **public** playlist link when prompted.  
2. The script scrapes songs and saves raw data.  
3. It cleans and processes the data.  
4. You’ll be prompted to name the Spotify playlist (defaults to the original).  
5. It will create the playlist and upload the found tracks.  



## Output Folders

- `scraping_data/amazon_playlist_raw.txt`: Raw extracted text  
- `scraping_data/amazon_playlist.csv`: Cleaned playlist data  
- `not_found_songs/`: Songs that couldn’t be matched on Spotify  



## Troubleshooting

- Ensure your Amazon Music playlist is **public** and fully loaded before scraping.  
- Run in a clean desktop environment to avoid interference with GUI automation.  
- Use a fresh Spotify token if facing authentication errors.  



## License

MIT License