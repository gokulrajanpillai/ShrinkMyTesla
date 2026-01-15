from pathlib import Path

import pytest

from shrinkmytesla import processing


def _make_video(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"fake mp4 data")


def test_find_tesla_videos_scans_known_folders(tmp_path):
    drive = tmp_path / "drive"
    expected = [
        drive / "TeslaCam" / "RecentClips" / "clip1.mp4",
        drive / "TeslaCam" / "SavedClips" / "clip2.mp4",
        drive / "TeslaCam" / "SentryClips" / "clip3.mp4",
    ]
    for video in expected:
        _make_video(video)

    found = processing.find_tesla_videos(drive)
    found_set = {Path(p) for p in found}

    for video in expected:
        assert video in found_set


def test_process_videos_moves_and_recreates(tmp_path, monkeypatch):
    drive = tmp_path / "drive"
    backup = tmp_path / "backup"
    original = drive / "TeslaCam" / "SavedClips" / "clip1.mp4"
    _make_video(original)

    def fake_downscale(input_path, output_path):
        output_path.write_bytes(b"downscaled data")

    monkeypatch.setattr(processing, "downscale_video", fake_downscale)

    processing.process_videos(drive, backup)

    backup_copy = backup / "TeslaCam" / "SavedClips" / "clip1.mp4"
    assert backup_copy.exists()
    assert original.exists()
    assert original.read_bytes() == b"downscaled data"
