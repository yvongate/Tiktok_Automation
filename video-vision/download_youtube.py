"""
Telecharge une ou plusieurs videos YouTube dans tutorials/downloads/,
via yt-dlp (utilise le FFmpeg deja installe sur la machine).

Usage:
    python download_youtube.py <url> [<url2> ...]
"""

import subprocess
import sys
from pathlib import Path

DEST = Path(__file__).parent / "tutorials" / "downloads"


def main():
    if len(sys.argv) < 2:
        print("Usage: python download_youtube.py <url> [<url2> ...]")
        sys.exit(1)

    DEST.mkdir(parents=True, exist_ok=True)
    urls = sys.argv[1:]

    for i, url in enumerate(urls, 1):
        print(f"\n=== [{i}/{len(urls)}] Telechargement : {url} ===")
        result = subprocess.run(
            [
                sys.executable, "-m", "yt_dlp",
                "-f", "best[height<=1080]/best",
                "--extractor-args", "youtube:player_client=android,web",
                "--merge-output-format", "mp4",
                "--write-info-json",
                "--no-playlist",
                "-o", str(DEST / "%(id)s.%(ext)s"),
                url,
            ],
            check=False,
        )
        if result.returncode != 0:
            print(f"  ATTENTION : echec sur {url} (code {result.returncode})")

    print(f"\nTermine. Videos dans : {DEST}")


if __name__ == "__main__":
    main()
