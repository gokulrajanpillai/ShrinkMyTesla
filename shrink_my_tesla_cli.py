import os
import argparse
import subprocess
from pathlib import Path
from tqdm import tqdm
import shutil

TESLA_FOLDER_NAMES = ['TeslaCam', 'TeslaCam/RecentClips', 'TeslaCam/SavedClips', 'TeslaCam/SentryClips']

def find_tesla_videos(drive_path):
    video_files = []
    for folder_name in TESLA_FOLDER_NAMES:
        folder_path = Path(drive_path) / folder_name
        if folder_path.exists():
            video_files.extend(folder_path.rglob("*.mp4"))
    return video_files

def downscale_video(input_path, output_path):
    """ffmpeg resolution/quality settings:
    - scale: 1280x720 (YouTube HD)
    - codec: H.264 (libx264)
    - crf: 28 (lower = better quality, bigger files)
    - preset: slower (better compression)
    """

    ffmpeg_path = os.environ.get('FFMPEG_PATH', 'ffmpeg')
    cmd = [
        ffmpeg_path,
        '-i', str(input_path),
        '-vf', 'scale=1280:720',
        '-c:v', 'libx264',
        '-crf', '28',
        '-preset', 'slower',
        '-c:a', 'copy',
        str(output_path)
    ]
    print("Downscaling video ...")
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except FileNotFoundError:
        raise RuntimeError(
            "ffmpeg not found. Install ffmpeg and ensure it's on PATH, or set FFMPEG_PATH to the ffmpeg binary."
        )

def process_videos(drive_path, backup_dir):
    drive_path = Path(drive_path)
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)

    videos = find_tesla_videos(drive_path)
    if not videos:
        print("No Tesla videos found.")
        return

    print(f"Found {len(videos)} video(s). Starting conversion...")

    for video in tqdm(videos):
        relative_path = video.relative_to(drive_path)
        backup_path = backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        # Skip if already backed up (optional)
        if backup_path.exists():
            print(f"Skipping (already backed up): {relative_path}")
            continue

        # Step 1: Move original to backup
        shutil.move(str(video), str(backup_path))

        # Step 2: Convert backup to HD and replace original path
        try:
            downscale_video(backup_path, video)
        except subprocess.CalledProcessError:
            print(f"Failed to convert {relative_path}, restoring original.")
            shutil.move(str(backup_path), str(video))  # Restore original if conversion fails

def main():
    parser = argparse.ArgumentParser(
        description="TeslaCam Video Downscaler to YouTube HD (720p) with Backup"
    )
    parser.add_argument(
        '--drive-path',
        type=str,
        required=True,
        help="Path to Tesla USB drive root (contains TeslaCam folder), e.g., /media/$USER/TESLACAM"
    )
    parser.add_argument(
        '--backup-dir',
        type=str,
        required=True,
        help="Directory where original videos are moved before replacing with downscaled versions"
    )
    args = parser.parse_args()

    process_videos(args.drive_path, args.backup_dir)

if __name__ == '__main__':
    main()
