# 🎧 Lyrics Adder & Audio Analyzer

A flexible Python tool to automatically:

- 🔍 Search and embed lyrics using the Genius API
- 🎚 Measure ReplayGain (EBU R128 standard) and tag it (beta)
- 🎛 Measure Dynamic Range (DR14 algorithm) and tag it (beta)

Supports `.mp3`, `.flac`, `.wav`, `.m4a`, `.ogg`, `.wv`, `.ape`, `.aiff`.

---

## ✅ Features

- Skips files that already have lyrics, RG, or DR
- Optionally runs lyrics only, RG only, DR only — or in any combination
- All results logged to a file
- Interactive prompt with confirmation
- Progress bar for bulk processing
- Automatically generates and updates config file

---

## 🔧 Configuration

When you first run the script, it will generate a `config.txt` file in the same folder:

```ini
GENIUS_TOKEN=YOUR_GENIUS_API_TOKEN
MUSIC_ROOT=./music
LOG_PATH=./lyrics_log.txt
```

💡 Please edit this file before proceeding with your Genius API token and correct paths.

---

## 🚀 Usage

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Install external tools:

   - [ffmpeg](https://ffmpeg.org):
     ```bash
     brew install ffmpeg
     ```

   - [r128gain](https://github.com/slhck/r128gain):
     ```bash
     brew install r128gain
     ```

   - [dr14tool](https://github.com/markbaaijens/dr14tool):
     ```bash
     pip install dr14tool
     ```

3. Run the script:
   ```bash
   python lyrics_adder.py
   ```

---

## 🕹 Options

At runtime, choose which parts of the workflow to run:

```
1 = Add lyrics
2 = Add ReplayGain
3 = Add Dynamic Range (DR14)

You can combine:
 - 12 or 21: lyrics + RG
 - 13 or 31: lyrics + DR
 - 23 or 32: RG + DR
 - 123 or 321: all steps
```

---

## 📝 Log

A log file is created at the path you define in `LOG_PATH`.  
It records any missing tags, errors, or failed lyric lookups.

---

## 💡 Example log

```
=== Session started 2025-03-24 21:30:02 ===

[NOT FOUND] Linkin Park – Numb (03 - Numb.mp3)
[ERROR] 07 - Broken.m4a — 401 Client Error: Unauthorized for url: ...
```

---

## 📃 License

MIT — use freely with attribution.
