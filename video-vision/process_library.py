"""
Traitement en masse : dossier de videos source -> bibliotheque locale
(frames + audio + transcription) dans video-vision/library/<id>/.

Usage:
    python process_library.py <dossier_source> [--frames 12] [--model base]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

DEST = Path(__file__).parent / "library"


def get_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def process_video(path, model, n_frames):
    vid_id = path.stem
    out_dir = DEST / vid_id
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    duration = get_duration(path)
    fps = (n_frames / duration) if duration > 0 else 1

    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(path), "-vf", f"fps={fps}", "-q:v", "2",
         str(frames_dir / "frame_%02d.jpg")],
        check=False,
    )

    audio_path = out_dir / "audio.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(path), "-vn", "-acodec", "libmp3lame", "-q:a", "2", str(audio_path)],
        check=False,
    )

    transcript_path = out_dir / "transcript.txt"
    if audio_path.exists():
        try:
            segments, info = model.transcribe(str(audio_path))
            lines = [f"[{s.start:5.1f}s->{s.end:5.1f}s] {s.text.strip()}" for s in segments]
            text = "\n".join(lines) if lines else "(aucune parole detectee)"
            transcript_path.write_text(text, encoding="utf-8")
        except Exception as e:
            transcript_path.write_text(f"(transcription echouee: {e})", encoding="utf-8")
    else:
        transcript_path.write_text("(pas de piste audio)", encoding="utf-8")

    meta = {
        "id": vid_id,
        "source_file": str(path),
        "duration_seconds": duration,
        "source_size_bytes": path.stat().st_size,
        "frame_count": len(list(frames_dir.glob("frame_*.jpg"))),
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return vid_id, duration


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Dossier contenant les .mp4 a traiter")
    parser.add_argument("--frames", type=int, default=12, help="Frames par video (defaut: 12)")
    parser.add_argument("--model", default="base", help="Modele faster-whisper (defaut: base)")
    parser.add_argument("--dest", default=None, help="Dossier de sortie (defaut: video-vision/library)")
    args = parser.parse_args()

    global DEST
    if args.dest:
        DEST = Path(args.dest)

    source = Path(args.source)
    if not source.is_dir():
        print(f"Dossier introuvable : {source}", file=sys.stderr)
        sys.exit(1)

    from faster_whisper import WhisperModel
    print(f"Chargement du modele Whisper '{args.model}'...")
    model = WhisperModel(args.model, device="cpu", compute_type="int8")

    videos = sorted(source.glob("*.mp4"))
    print(f"{len(videos)} videos trouvees dans {source}")
    DEST.mkdir(parents=True, exist_ok=True)

    index = []
    for i, v in enumerate(videos, 1):
        print(f"[{i}/{len(videos)}] {v.name}", flush=True)
        try:
            vid_id, duration = process_video(v, model, args.frames)
            index.append({"id": vid_id, "duration_seconds": duration, "status": "ok"})
        except Exception as e:
            print(f"  ERREUR sur {v.name}: {e}", flush=True)
            index.append({"id": v.stem, "status": "error", "error": str(e)})

    (DEST / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    ok = sum(1 for x in index if x["status"] == "ok")
    print(f"\nTermine : {ok}/{len(videos)} videos traitees avec succes.")
    print(f"Resultats dans : {DEST}")


if __name__ == "__main__":
    main()
