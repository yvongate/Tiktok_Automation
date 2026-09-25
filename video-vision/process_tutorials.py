"""
Traite les videos telechargees dans tutorials/downloads/ -> tutorials/library/<id>/
(frames + audio + transcription), avec un nombre de frames ADAPTE A LA DUREE :
les vidéos tuto sont plus longues que les clips TikTok, donc plus de frames,
mais plafonnees pour rester lisibles.

Usage:
    python process_tutorials.py [--frames-per-min 2] [--max-frames 60] [--model base]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SOURCE = Path(__file__).parent / "tutorials" / "downloads"
DEST = Path(__file__).parent / "tutorials" / "library"


def get_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def frame_count_for(duration, frames_per_min, max_frames, min_frames=12):
    n = int(duration / 60 * frames_per_min)
    return max(min_frames, min(max_frames, n))


def get_title(path):
    info_path = path.with_suffix(".info.json")
    if info_path.exists():
        try:
            info = json.loads(info_path.read_text(encoding="utf-8"))
            return info.get("title"), info.get("uploader")
        except Exception:
            pass
    return None, None


def process_video(path, model, frames_per_min, max_frames):
    vid_id = path.stem
    out_dir = DEST / vid_id
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    duration = get_duration(path)
    n_frames = frame_count_for(duration, frames_per_min, max_frames)
    fps = (n_frames / duration) if duration > 0 else 1

    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(path), "-vf", f"fps={fps}", "-q:v", "2",
         str(frames_dir / "frame_%03d.jpg")],
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
            lines = [f"[{s.start:7.1f}s->{s.end:7.1f}s] {s.text.strip()}" for s in segments]
            text = "\n".join(lines) if lines else "(aucune parole detectee)"
            transcript_path.write_text(text, encoding="utf-8")
        except Exception as e:
            transcript_path.write_text(f"(transcription echouee: {e})", encoding="utf-8")
    else:
        transcript_path.write_text("(pas de piste audio)", encoding="utf-8")

    title, uploader = get_title(path)
    meta = {
        "id": vid_id,
        "title": title,
        "uploader": uploader,
        "source_file": str(path),
        "duration_seconds": duration,
        "source_size_bytes": path.stat().st_size,
        "frame_count": len(list(frames_dir.glob("frame_*.jpg"))),
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return vid_id, duration, title


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames-per-min", type=float, default=2, help="Frames par minute (defaut: 2)")
    parser.add_argument("--max-frames", type=int, default=60, help="Plafond de frames par video (defaut: 60)")
    parser.add_argument("--model", default="base", help="Modele faster-whisper (defaut: base)")
    args = parser.parse_args()

    if not SOURCE.is_dir() or not any(SOURCE.glob("*.mp4")):
        print(f"Aucune video dans {SOURCE}. Lance d'abord download_youtube.py.", file=sys.stderr)
        sys.exit(1)

    from faster_whisper import WhisperModel
    print(f"Chargement du modele Whisper '{args.model}'...")
    model = WhisperModel(args.model, device="cpu", compute_type="int8")

    videos = sorted(SOURCE.glob("*.mp4"))
    print(f"{len(videos)} videos trouvees dans {SOURCE}")
    DEST.mkdir(parents=True, exist_ok=True)

    index = []
    for i, v in enumerate(videos, 1):
        print(f"[{i}/{len(videos)}] {v.name}", flush=True)
        try:
            vid_id, duration, title = process_video(v, model, args.frames_per_min, args.max_frames)
            print(f"  -> {title or vid_id} ({duration:.0f}s, {frame_count_for(duration, args.frames_per_min, args.max_frames)} frames)", flush=True)
            index.append({"id": vid_id, "title": title, "duration_seconds": duration, "status": "ok"})
        except Exception as e:
            print(f"  ERREUR sur {v.name}: {e}", flush=True)
            index.append({"id": v.stem, "status": "error", "error": str(e)})

    (DEST / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    ok = sum(1 for x in index if x["status"] == "ok")
    print(f"\nTermine : {ok}/{len(videos)} videos traitees.")
    print(f"Resultats dans : {DEST}")


if __name__ == "__main__":
    main()
