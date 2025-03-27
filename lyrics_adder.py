import os
import time
import subprocess
from mutagen.id3 import ID3, USLT, ID3NoHeaderError
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis
from mutagen.apev2 import APEv2File
from mutagen.wave import WAVE
from mutagen.aiff import AIFF
import lyricsgenius
from datetime import datetime
from tqdm import tqdm

# --- INTRODUCTION ---
print("""
🎧 Lyrics Adder & Audio Analyzer

This tool helps you:
1. Search and embed lyrics using Genius API
2. Measure and tag ReplayGain (track gain/peak)
3. Measure and tag Dynamic Range (DR14)
4. Open config file directly (option 0)

Supports: .mp3, .flac, .m4a, .wav, .aiff, .ape, .wv, .ogg
""")

# --- CONFIGURATION ---
CONFIG_PATH = "./config.txt"

def create_default_config():
    """
    Создаёт config.txt, в котором есть комментарии по поводу LOG_PATH:
    Если LOG_PATH оставите пустым, лог будет складываться в папку music_root.
    """
    with open(CONFIG_PATH, "w") as f:
        f.write(
            "# GENIUS_TOKEN=YOUR_GENIUS_API_TOKEN\n"
            "# MUSIC_ROOT=./music\n"
            "# LOG_PATH=./lyrics_log.txt\n"
            "# Если оставить LOG_PATH пустым, логи будут складываться в MUSIC_ROOT.\n\n"
        )
        f.write("GENIUS_TOKEN=YOUR_GENIUS_API_TOKEN\n")
        f.write("MUSIC_ROOT=./music\n")
        f.write("LOG_PATH=\n")
    print("Created config.txt. Please fill in your Genius token and paths before proceeding.")

if not os.path.exists(CONFIG_PATH):
    create_default_config()
    exit()

# Load config
config = {}
with open(CONFIG_PATH, "r") as f:
    for line in f:
        line = line.strip()
        if line and '=' in line and not line.startswith('#'):
            key, val = line.split('=', 1)
            key = key.strip()
            val = val.strip().strip('"')
            config[key] = val

genius_token = config.get("GENIUS_TOKEN")
music_root = config.get("MUSIC_ROOT")
log_path = config.get("LOG_PATH")

# Validate paths and token
if not genius_token or genius_token == "YOUR_GENIUS_API_TOKEN":
    print("❌ GENIUS_TOKEN is missing or empty in config.txt")
    exit()

if not music_root:
    print("❌ MUSIC_ROOT is missing or empty in config.txt")
    exit()

# Если LOG_PATH отсутствует или пуст, кладём лог в ту же папку, что и MUSIC_ROOT
if not log_path:
    log_path = os.path.join(music_root, "lyrics_log.txt")

# Создадим папки, если их нет
os.makedirs(music_root, exist_ok=True)
os.makedirs(os.path.dirname(log_path), exist_ok=True)

# Инициализация Genius
genius = lyricsgenius.Genius(genius_token)

# Лог-функция
def log_error(message: str):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(message + "\n")

from datetime import datetime
log_error(f"\n=== Session started {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")

# Поддерживаемые форматы
supported_exts = ["mp3", "flac", "m4a", "ogg", "ape", "wv", "wav", "aiff"]

def scan_audio_files():
    audio_files = []
    for root, dirs, files in os.walk(music_root):
        for file in files:
            ext = file.lower().split(".")[-1]
            if ext in supported_exts:
                audio_files.append(os.path.join(root, file))
    return audio_files

# --- MAIN LOOP ---
while True:
    choice = input(
        "\nWhat would you like to do?\n"
        "0 = Open config file\n"
        "1 = Add lyrics\n"
        "2 = Add ReplayGain\n"
        "3 = Add Dynamic Range (DR14)\n"
        "q = Quit\n"
        "You can combine: 12, 23, 123, etc.\n"
        "Enter your choice (e.g. 1, 12, 123, 0): "
    )

    if choice == "q":
        print("👋 Exiting...")
        break

    if choice == "0":
        print(f"🛠 Opening config file: {CONFIG_PATH}")
        import platform
        if platform.system() == "Darwin":
            os.system(f"open {CONFIG_PATH}")
        elif platform.system() == "Windows":
            os.startfile(CONFIG_PATH)
        else:
            os.system(f"xdg-open {CONFIG_PATH}")
        continue

    selected = set(choice)
    valid = {"1", "2", "3"}
    if not selected.issubset(valid):
        print("❌ Invalid choice. Please enter a combination of 1, 2, and 3.")
        continue

    print(
        f"✅ Selected options: "
        f"{'Lyrics ' if '1' in selected else ''}"
        f"{'ReplayGain ' if '2' in selected else ''}"
        f"{'DR ' if '3' in selected else ''}"
    )

    print("⏳ Starting in 3 seconds...")
    time.sleep(3)

    # --- SCAN FILES ---
    print("🎵 Scanning your music library...\n")
    audio_files = scan_audio_files()
    if not audio_files:
        print("No supported audio files found.")
        log_error("[ERROR] No supported audio files found in the specified folder.")
        continue

    print(f"🎼 Found {len(audio_files)} supported audio files.\n")

    # --- 2) ReplayGain на всю папку (rsgain easy --per-track / --peralbum / etc.) ---
    if "2" in selected:
        print("🎚 Applying per-track ReplayGain to entire music library...")
        # Пример: rsgain easy --per-track /путь
        # (Если нужно перезаписывать, добавьте --force)
        result = subprocess.run(
            [
                "rsgain", "easy",
                "--per-track",
                # "--force",  # <-- если хочешь перезапись тегов
                music_root
            ],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"❌ Error with ReplayGain: {result.stderr}")
            log_error(f"[ERROR] ReplayGain failed: {result.stderr}")
        else:
            print(f"🎚 ReplayGain analysis and tagging complete:\n{result.stdout}")
            print("📝 writing to tags")

    # --- PROCESS FILES (Lyrics and DR) ---
    from mutagen.id3 import ID3NoHeaderError, USLT
    from mutagen.easyid3 import EasyID3
    for filepath in tqdm(audio_files, desc="Processing tracks", unit="track"):
        file = os.path.basename(filepath)
        ext = file.lower().split(".")[-1]
        print(f"\n📂 Processing: {file}")

        try:
            audio = None
            lyrics_exist = False
            title, artist = None, None

            if ext == "mp3":
                audio = MP3(filepath, ID3=ID3)
                tags = EasyID3(filepath)
                title = tags.get("title", [None])[0]
                artist = tags.get("artist", [None])[0]
                lyrics_exist = any(isinstance(f, USLT) and f.text.strip() for f in audio.tags.values())

            elif ext == "flac":
                audio = FLAC(filepath)
                title = audio.get("title", [None])[0]
                artist = audio.get("artist", [None])[0]
                lyrics_exist = "LYRICS" in audio and audio["LYRICS"][0].strip()

            elif ext == "m4a":
                audio = MP4(filepath)
                title = audio.tags.get("\xa9nam", [None])[0]
                artist = audio.tags.get("\xa9ART", [None])[0]
                lyrics_exist = "\u00a9lyr" in audio and audio["\u00a9lyr"][0].strip()

            elif ext == "ogg":
                audio = OggVorbis(filepath)
                title = audio.get("title", [None])[0]
                artist = audio.get("artist", [None])[0]
                lyrics_exist = "LYRICS" in audio and audio["LYRICS"][0].strip()

            elif ext in ["ape", "wv"]:
                audio = APEv2File(filepath)
                title = audio.get("Title", [None])[0]
                artist = audio.get("Artist", [None])[0]
                lyrics_exist = "Lyrics" in audio and audio["Lyrics"].strip()

            elif ext in ["wav", "aiff"]:
                audio = WAVE(filepath) if ext == "wav" else AIFF(filepath)
                title = audio.get("title", [None])[0]
                artist = audio.get("artist", [None])[0]
                lyrics_exist = "LYRICS" in audio and audio["LYRICS"][0].strip()

            # 1) Lyrics
            if "1" in selected:
                if lyrics_exist:
                    print(f"⏩ Skipped (lyrics already present): {file}")
                elif title and artist:
                    print(f"🔍 Searching lyrics for: {artist} – {title}")
                    song = genius.search_song(title, artist)
                    if song and song.lyrics:
                        lyrics = song.lyrics.replace("Embed", "").strip()
                        if ext == "mp3":
                            try:
                                audio.add_tags()
                            except ID3NoHeaderError:
                                pass
                            audio.tags.add(USLT(encoding=3, lang='eng', desc='desc', text=lyrics))
                        elif ext == "flac":
                            audio["LYRICS"] = lyrics
                        elif ext == "m4a":
                            audio["\u00a9lyr"] = [lyrics]
                        elif ext == "ogg":
                            audio["LYRICS"] = [lyrics]
                        elif ext in ["ape", "wv"]:
                            audio["Lyrics"] = lyrics
                        elif ext in ["wav", "aiff"]:
                            audio["LYRICS"] = lyrics

                        audio.save()
                        print(f"✅ Lyrics added: {file}")
                    else:
                        print(f"❌ Lyrics not found: {artist} – {title}")
                        log_error(f"[NOT FOUND] {artist} – {title} ({file})")

            # 3) Dynamic Range (DR14, per file)
            if "3" in selected and ext in ["mp3", "flac", "wav"]:
                if "DYNAMIC RANGE" in audio:
                    print("⏩ Dynamic Range already present, skipping.")
                else:
                    result = subprocess.run(["dr14tool", "-w", filepath], capture_output=True, text=True)
                    if result.returncode != 0:
                        print(f"❌ Error with DR14: {result.stderr}")
                        log_error(f"[ERROR] {filepath} DR14 failed: {result.stderr}")
                    else:
                        print(f"🎛 Dynamic Range analysis: {result.stdout}")
                        print("📝 writing to tags")

        except Exception as e:
            print(f"💥 Error with file {file}: {e}")
            log_error(f"[ERROR] {file} — {e}")
