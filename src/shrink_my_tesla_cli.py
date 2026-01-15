import argparse
from shrinkmytesla.processing import process_videos

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
