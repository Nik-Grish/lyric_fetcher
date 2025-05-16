# 🎧 Lyrics Adder & Audio Analyzer

A Python tool to **automatically fetch and embed lyrics** into your music files and **analyze ReplayGain loudness** across your library.

---

## 🚀 Features

- ✅ Search and embed lyrics using the **Genius API**
- ✅ Analyze and tag **ReplayGain** loudness using [`rsgain`](https://github.com/complexlogic/rsgain)
- 🛑 *(DR14 Dynamic Range functionality is currently disabled by default)*

**Supported audio formats:**
`.mp3`, `.flac`, `.m4a`, `.wav`, `.aiff`, `.ape`, `.wv`, `.ogg`

---

## 📦 Installation

1. **Clone this repository:**

```bash
git clone https://github.com/yourusername/lyrics-adder.git
cd lyrics-adder
```

2. **Set up a virtual environment and install dependencies:**

```bash
python -m venv lyrics-env
source lyrics-env/bin/activate  # On Windows: lyrics-env\Scripts\activate
pip install -r requirements.txt
```

3. **Install `rsgain`:**

```bash
pip install rsgain
```

---

## ⚙️ Configuration

The first time you run the script, it will generate a `config.txt` file:

```
GENIUS_TOKEN=YOUR_GENIUS_API_TOKEN
MUSIC_ROOT=./music
LOG_PATH=
```

- Replace `YOUR_GENIUS_API_TOKEN` with your Genius API token.
- Set `MUSIC_ROOT` to the path where your audio files are stored.
- If `LOG_PATH` is empty, the log will be saved inside the music directory.

---

## 🧠 Usage

Run the script:

```bash
python lyrics_adder.py
```

You will see a prompt like this:

```
What would you like to do?
0 = Open config file
1 = Add lyrics
2 = Add ReplayGain
q = Quit
```

You can combine actions: `12`, `21`, `1`, `2`, etc.

---

## 🔁 Automatic Retry on API Errors

If the Genius API returns a temporary connection error (e.g. `ConnectionResetError` or `ReadTimeout`), the script will **automatically retry only the failed tracks** at the end of the run.

---

## 🔇 Disabled Functionality

The `3 = Add Dynamic Range (DR14)` option is currently disabled, since [`dr14tool`](https://github.com/markbaaijens/dr14tool) requires manual installation and setup. You can re-enable it once the tool is installed.

---

## 📝 Logging

All failed lookups and API errors will be recorded in `lyrics_log.txt`.

---

## 📄 License

MIT License.