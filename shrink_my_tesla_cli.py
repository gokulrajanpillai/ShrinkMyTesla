import os
import argparse
from pathlib import Path
try:
    from tqdm import tqdm  # type: ignore
except Exception:
    tqdm = None  # type: ignore
import shutil

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
    """Downscale video to 720p using ffmpeg-python (no external exe path)."""
    try:
        # Lazy import to avoid requiring ffmpeg for --help
        import ffmpeg
        (
            ffmpeg
            .input(str(input_path))
            .output(
                str(output_path),
                vf='scale=1280:720',
                vcodec='libx264',
                crf=28,
                preset='slower',
                acodec='copy'
            )
            .run(
                capture_stdout=True,
                capture_stderr=True,
                overwrite_output=True
            )
        )
    except ffmpeg.Error as e:
        print(f"Error processing {input_path}: {e.stderr.decode() if e.stderr else e}")
        raise


def process_videos(drive_path, backup_dir):
    """Process all Tesla videos, back them up, and replace with downscaled versions."""
    drive_path = Path(drive_path)
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)

    videos = find_tesla_videos(drive_path)
    if not videos:
        print("No Tesla videos found.")
        return

    total = len(videos)
    print(f"Found {total} video(s). Starting conversion...")

    # Choose progress iterator
    if tqdm:
        iterator = tqdm(videos, total=total, unit="video", desc="Converting", dynamic_ncols=True, leave=True)
    else:
        iterator = enumerate(videos, start=1)

    for item in iterator:
        if tqdm:
            video = item
            idx = None
        else:
            idx, video = item
        relative_path = video.relative_to(drive_path)
        backup_path = backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        # Skip if already backed up (optional)
        if backup_path.exists():
            if idx is not None:
                print(f"[{idx}/{total}] Skipping (already backed up): {relative_path}")
            else:
                # Keep the bar concise and print the full message on a new line
                iterator.set_postfix_str("skip", refresh=True)
                tqdm.write(f"skip: {relative_path}")
            continue

        # Step 1: Move original to backup
        if idx is not None:
            print(f"[{idx}/{total}] Backing up: {relative_path}")
        else:
            iterator.set_postfix_str("backup", refresh=True)
            tqdm.write(f"backup: {relative_path}")
        shutil.move(str(video), str(backup_path))

        # Step 2: Convert backup to HD and replace original path
        try:
            if idx is not None:
                print(f"[{idx}/{total}] Converting to HD: {relative_path}")
            else:
                iterator.set_postfix_str("convert", refresh=True)
                tqdm.write(f"convert: {relative_path}")
            downscale_video(backup_path, video)
        except Exception as e:
            print(f"Failed to convert {relative_path}, restoring original.")
            shutil.move(str(backup_path), str(video))  # Restore original if conversion fails


def main():
    description = (
        "Shrink My Tesla — safely shrink TeslaCam videos by downscaling them to a"
        " smaller resolution (default 720p) to save space, while keeping a full"
        " backup of originals in a separate folder."
    )

    epilog = (
        "Examples:\n"
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

    parser.add_argument('--drive-path', required=True, help="Path to Tesla USB drive (e.g., /media/user/TESLACAM)")
    parser.add_argument('--backup-dir', required=True, help="Directory to move original videos before replacing with HD versions")
    args = parser.parse_args()

    process_videos(args.drive_path, args.backup_dir)


if __name__ == '__main__':
    main()
