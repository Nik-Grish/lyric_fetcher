import os
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

# Replace with your Genius API token
genius = lyricsgenius.Genius("YOUR_GENIUS_API_TOKEN")

# Root directory containing your audio library
music_root = "./music"

# Path to the log file
log_path = "./lyrics_log.txt"

# Supported audio file extensions
supported_exts = ["mp3", "flac", "m4a", "ogg", "ape", "wv", "wav", "aiff"]

# Create or append log entry
def log_error(message):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(message + "\n")

# Start of session log
log_error(f"\n=== Session started {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")

print("🎵 Scanning your music library...\n")

# Gather all audio files
audio_files = []
for root, dirs, files in os.walk(music_root):
    for file in files:
        ext = file.lower().split(".")[-1]
        if ext in supported_exts:
            audio_files.append(os.path.join(root, file))

if not audio_files:
    print("No supported audio files found.")
    log_error("[ERROR] No supported audio files found in the specified folder.")
    exit()

# Main processing loop
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
            title = audio.tags.get("©nam", [None])[0]
            artist = audio.tags.get("©ART", [None])[0]
            lyrics_exist = "©lyr" in audio and audio["©lyr"][0].strip()

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

        if lyrics_exist:
            print(f"⏩ Skipped (lyrics already present): {file}")
            continue

        if not title or not artist:
            print(f"⚠️ Skipped (missing title or artist tags): {file}")
            log_error(f"[MISSING TAGS] {file}")
            continue

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
                audio["©lyr"] = [lyrics]

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

    except Exception as e:
        print(f"💥 Error with file {file}: {e}")
        log_error(f"[ERROR] {file} — {e}")
