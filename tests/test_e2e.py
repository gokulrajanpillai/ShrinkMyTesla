"""End-to-end tests: real Tesla pendrive folder structure + real ffmpeg encoding."""

import shutil
import subprocess
from pathlib import Path

import pytest

from shrinkmytesla import processing


def _has_ffmpeg():
    return shutil.which("ffmpeg") is not None


def _make_real_video(path):
    """Create a small valid MP4 file (1 second, 320x240) using ffmpeg."""
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "color=c=blue:s=320x240:d=1",
            "-c:v", "libx264",
            "-t", "1",
            str(path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


@pytest.mark.skipif(not _has_ffmpeg(), reason="ffmpeg not available")
def test_e2e_tesla_pendrive_structure(tmp_path):
    """Full end-to-end: Tesla pen drive folders are scanned, videos detected,
    backed up, and replaced with downscaled versions."""
    drive = tmp_path / "TeslaDrive"
    backup = tmp_path / "Backup"

    # Mirror the folder structure found on a real Tesla USB drive
    video_paths = [
        drive / "TeslaCam" / "RecentClips" / "recent_clip.mp4",
        drive / "TeslaCam" / "SavedClips" / "saved_clip.mp4",
        drive / "TeslaCam" / "SentryClips" / "sentry_clip.mp4",
    ]
    for video_path in video_paths:
        _make_real_video(video_path)

    original_sizes = {p: p.stat().st_size for p in video_paths}

    # Run the full processing pipeline
    processing.process_videos(drive, backup)

    for video_path in video_paths:
        relative = video_path.relative_to(drive)

        # Original video must have been backed up
        backup_copy = backup / relative
        assert backup_copy.exists(), f"Backup not created for {relative}"
        assert backup_copy.stat().st_size == original_sizes[video_path], (
            f"Backup size mismatch for {relative}"
        )

        # Downscaled video must exist at the original location
        assert video_path.exists(), f"Downscaled video missing at {video_path}"
