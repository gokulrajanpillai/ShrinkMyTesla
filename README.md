# ShrinkMyTesla 🚗💨

**ShrinkMyTesla** is a desktop and CLI tool that automatically **compresses and cleans Tesla Dashcam & Sentry Mode videos**.  
Keep the important footage, lose the unnecessary gigabytes.

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
Built with **Electron + FFmpeg + Node.js**, designed for privacy and local processing.  
No uploads, no accounts, no data leaves your drive.

### 🪄 Example use (CLI)
```bash
shrinkmytesla --source /Volumes/TESLADRIVE/TeslaCam --delete-originals --preset balanced
