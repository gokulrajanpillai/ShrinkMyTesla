# Changelog

## Unreleased
- Added MIT license.
- Added the initial Python CLI to scan and shrink TeslaCam videos.
- Created devcontainer support, including host SSH mounting and OpenSSH client setup.
- Removed dependency on ffmpeg.exe in favor of a Python-based approach and updated devcontainer config.
- Made the CLI more user friendly.
- Updated README, documented `FFMPEG_PATH`, and added `requirements.txt`.
- Optimized Python CLI tooling dependencies using `uv`.
- Added the `shrinkmytesla` library package and CLI wiring.
- Added CI workflows for main and PRs.
- Added pytest coverage for core processing flow.
- Moved Python sources into a `src/` layout.
- Added LF normalization via `.gitattributes`.
- Documented main branch stability in README.
- Removed UI assets and release workflow to keep the repo CLI-only.
