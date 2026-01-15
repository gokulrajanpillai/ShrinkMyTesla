# ShrinkMyTesla 🚗💨

**ShrinkMyTesla** is a CLI tool that automatically **compresses and cleans Tesla Dashcam & Sentry Mode videos**.  
Keep the important footage, lose the unnecessary gigabytes.

![Main branch: stable](https://img.shields.io/badge/main-stable-2ea44f)

### 🧠 Why it exists
Tesla’s built-in dashcam records in high-bitrate MP4 files across four cameras.  
A single day of driving can fill your USB or SSD. ShrinkMyTesla reduces video size by up to **70%**, while keeping license-plate-level clarity.

### ⚙️ What it does
- 🔍 Auto-detects TeslaCam folder on your thumb drive or SSD  
- 🎞️ Batch-compresses videos using efficient H.265/HEVC  
- 📂 Organizes clips by date & camera angle  
- 🧹 Optional cleanup of original large files after compression  
- 💻 Works offline — Windows, macOS, and Linux  

### 🧰 Tech
Built with **Python + FFmpeg**, designed for privacy and local processing.  
No uploads, no accounts, no data leaves your drive.

### Project layout
- CLI (first productive version): `src/shrink_my_tesla_cli.py` and `src/shrinkmytesla/` library

### 🪄 Example use (CLI)
```bash
python src/shrink_my_tesla_cli.py --drive-path /Volumes/TESLADRIVE --backup-dir "$HOME/TeslaBackups"
```

CLI (Python) quick start
- Prereqs: Python 3.8+ and ffmpeg installed (on PATH), or set `FFMPEG_PATH` to your ffmpeg binary
- Install deps:
	```bash
	pip install -r requirements.txt
	```
- Linux example:
	```bash
	python src/shrink_my_tesla_cli.py --drive-path /media/$USER/TESLACAM --backup-dir "$HOME/TeslaBackups"
	```
- Windows (PowerShell):
	```powershell
	python .\src\shrink_my_tesla_cli.py --drive-path E:\ --backup-dir D:\TeslaBackups
	```
- Note: Scans TeslaCam/RecentClips, SavedClips, SentryClips; moves originals to the backup dir and writes 720p H.264 files back in place.
