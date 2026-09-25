"""
Transcription locale et gratuite avec faster-whisper (CPU, sans cle API).

Usage:
    python transcribe_local.py <audio.mp3> [--model tiny|base|small|medium] [--out transcript.txt]

Le premier lancement telecharge le modele choisi (quelques dizaines a
quelques centaines de Mo selon la taille) puis le reutilise localement.
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Transcription audio locale (faster-whisper)")
    parser.add_argument("audio", help="Chemin vers le fichier audio (mp3, wav, ...)")
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Taille du modele. 'tiny'/'base' = rapide sur CPU modeste. "
             "'small'/'medium' = plus precis mais plus lent. Defaut: base",
    )
    parser.add_argument("--out", default=None, help="Fichier de sortie (defaut: transcript.txt a cote de l'audio)")
    parser.add_argument("--lang", default=None, help="Code langue (ex: fr, en). Defaut: detection automatique")
    args = parser.parse_args()

    audio_path = Path(args.audio)
    if not audio_path.exists():
        print(f"Fichier introuvable : {audio_path}", file=sys.stderr)
        sys.exit(1)

    out_path = Path(args.out) if args.out else audio_path.parent / "transcript.txt"

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("faster-whisper n'est pas installe. Lance : pip install faster-whisper", file=sys.stderr)
        sys.exit(1)

    print(f"Chargement du modele '{args.model}' (telechargement au premier lancement)...")
    model = WhisperModel(args.model, device="cpu", compute_type="int8")

    print(f"Transcription de {audio_path.name}...")
    segments, info = model.transcribe(str(audio_path), language=args.lang)

    print(f"Langue detectee : {info.language} (confiance {info.language_probability:.2f})")

    lines = []
    for seg in segments:
        line = f"[{seg.start:6.1f}s -> {seg.end:6.1f}s] {seg.text.strip()}"
        print(line)
        lines.append(line)

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nTranscription enregistree -> {out_path}")


if __name__ == "__main__":
    main()
