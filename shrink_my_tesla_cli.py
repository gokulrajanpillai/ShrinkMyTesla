import os
import argparse
from pathlib import Path
try:
    from tqdm import tqdm  # type: ignore
except Exception:
    tqdm = None  # type: ignore
import shutil
import concurrent.futures

TESLA_FOLDER_NAMES = [
    'TeslaCam',
    'TeslaCam/RecentClips',
    'TeslaCam/SavedClips',
    'TeslaCam/SentryClips'
]

def find_tesla_videos(drive_path):
    """Recursively find all TeslaCam .mp4 videos."""
    video_files = []
    for folder_name in TESLA_FOLDER_NAMES:
        folder_path = Path(drive_path) / folder_name
        if folder_path.exists():
            video_files.extend(folder_path.rglob("*.mp4"))
    return video_files


def downscale_video(input_path, output_path):
    cmd = [
        r'C:\ffmpeg-8.0-essentials_build\bin\ffmpeg.exe',
        '-i', str(input_path),
        '-vf', 'scale=1280:720',
        '-c:v', 'libx264',
        '-crf', '28',
        '-preset', 'slower',
        '-c:a', 'copy',
        str(output_path)
    ]
    print(f"Downscaling video: {input_path}")
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def compress_and_replace(args):
    video, drive_path, backup_dir = args
    relative_path = video.relative_to(drive_path)
    backup_path = backup_dir / relative_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)

    if backup_path.exists():
        print(f"Skipping (already backed up): {relative_path}")
        return

    shutil.move(str(video), str(backup_path))

    try:
        downscale_video(backup_path, video)
    except subprocess.CalledProcessError:
        print(f"Failed to convert {relative_path}, restoring original.")
        shutil.move(str(backup_path), str(video))

def process_videos(drive_path, backup_dir):
    """Process all Tesla videos, back them up, and replace with downscaled versions."""
    drive_path = Path(drive_path)
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)

    videos = find_tesla_videos(drive_path)
    if not videos:
        print("No Tesla videos found.")
        return

    print(f"Found {len(videos)} video(s). Starting parallel conversion...")

    args_list = [(video, drive_path, backup_dir) for video in videos]
    with concurrent.futures.ProcessPoolExecutor() as executor:
        list(tqdm(executor.map(compress_and_replace, args_list), total=len(videos)))


def main():
    description = (
        "Shrink My Tesla — safely shrink TeslaCam videos by downscaling them to a"
        " smaller resolution (default 720p) to save space, while keeping a full"
        " backup of originals in a separate folder. Use -p/--drive-path and -b/--backup-dir."
    )

    epilog = (
        "Examples:\n"
        "  python shrink_my_tesla_cli.py -p /Volumes/TESLACAM -b ~/Backups/TeslaCam\n"
        "  python shrink_my_tesla_cli.py --drive-path /Volumes/TESLACAM \\\n+    --backup-dir ~/Backups/TeslaCam\n\n"
        "Notes:\n"
        "- Originals are moved to the backup folder first, then converted back into\n"
        "  the original locations. If anything fails, the original file is restored.\n"
    )

    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument('-p', '--drive-path', required=True, help="Path to Tesla USB drive (e.g., /media/user/TESLACAM)")
    parser.add_argument('-b', '--backup-dir', required=True, help="Directory to move original videos before replacing with HD versions")
    args = parser.parse_args()

    process_videos(args.drive_path, args.backup_dir)


if __name__ == '__main__':
    main()
