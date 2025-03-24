# Lyrics Adder

A Python script that automatically fetches lyrics from the Genius API and embeds them into your audio files' metadata tags stored on your computer.

## ✅ Features

- Supports multiple audio formats: `.mp3`, `.flac`, `.m4a`, `.ogg`, `.ape`, `.wv`, `.wav`, `.aiff`
- Skips files that already contain lyrics
- Logs missing lyrics and errors into a log file
- Displays progress bar with per-track status
- Compatible with tag editors (e.g., Mp3tag, Poweramp)

## 🚀 Requirements

- Python 3.8+
- Genius API token
- Install dependencies:

```bash
pip install mutagen lyricsgenius tqdm
```

## 🔧 Usage

1. Clone this repo or download the script.
2. Replace `"YOUR_GENIUS_API_TOKEN"` with your Genius API token.
3. Set the path to your music folder and the desired log file location.
4. Run the script:

```bash
python lyrics_adder.py
```

## 📁 Output

- Lyrics will be embedded in the respective tag field depending on format (`USLT`, `LYRICS`, etc.)
- Log file will be generated (default: `lyrics_log.txt`) with missing lyrics or errors.

## 💡 Example log

```
=== Session started 2025-03-24 21:30:02 ===

[NOT FOUND] Linkin Park – Numb (03 - Numb.mp3)
[ERROR] 07 - Broken.m4a — 401 Client Error: Unauthorized for url: ...
```

## 🛡 License

MIT — use freely with attribution.
