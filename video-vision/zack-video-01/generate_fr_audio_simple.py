"""
Genere la voix off FR simplifiee (script_60s_fr_simple.txt) et la fusionne
sur la video (avec extension figee si besoin, comme pour la 1ere version FR).
Produit final_60s_fr_simple.mp4.
"""
import json
import subprocess
import urllib.request
import urllib.error
import time
from pathlib import Path

API_KEY = Path(r"F:\Tiktok\api.txt").read_text(encoding="utf-8").strip().split(":")[-1].strip()
OUT_DIR = Path(__file__).parent
script_fr = (OUT_DIR / "script_60s_fr_simple.txt").read_text(encoding="utf-8").strip()


def http_json(url, headers, body=None, method="GET"):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    for k, v in headers.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.read().decode('utf-8')[:500]}")
        return None
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print(f"  Erreur reseau ({type(e).__name__}): {e}")
        return None


def create_task(model, input_body, retries=3):
    for attempt in range(1, retries + 1):
        result = http_json(
            "https://api.kie.ai/api/v1/jobs/createTask",
            {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            {"model": model, "input": input_body},
            method="POST",
        )
        if result and result.get("data"):
            return result["data"]["taskId"]
        print(f"  createTask {model} -> {result}")
        time.sleep(5 * attempt)
    return None


def wait_for_result(task_id, max_wait=120, interval=6):
    elapsed = 0
    while elapsed < max_wait:
        result = http_json(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            {"Authorization": f"Bearer {API_KEY}"},
        )
        if result:
            data = result.get("data", {})
            state = data.get("state")
            if state == "success":
                return data
            if state == "fail":
                print(f"  ECHEC : {data.get('failMsg')}")
                return None
        time.sleep(interval)
        elapsed += interval
    return None


def get_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    return float(out.stdout.strip())


print("=== Voix off FRANCAISE SIMPLIFIEE (Gemini 3.1 Flash TTS) ===")
voice_task = create_task(
    "google/gemini-3-1-flash-tts",
    {
        "speakers": [
            {"speaker_id": "Speaker 1", "voice_name": "Zephyr", "audio_profile": "dramatic French narrator",
             "style": "Deadpan", "pace": "Natural", "accent": "Neutral"}
        ],
        "dialogue_turns": [{"speaker_id": "Speaker 1", "text": script_fr}],
    },
)
audio_path = OUT_DIR / "voice_60s_fr_simple.wav"
if not voice_task:
    print("  Echec creation tache voix.")
    raise SystemExit(1)
voice_data = wait_for_result(voice_task)
if not voice_data:
    print("  Echec generation voix.")
    raise SystemExit(1)
url = json.loads(voice_data["resultJson"])["resultUrls"][0]
urllib.request.urlretrieve(url, audio_path)
print(f"  Voix OK -> {audio_path}")

audio_dur = get_duration(audio_path)
concat_video = OUT_DIR / "concat_60s.mp4"
video_dur = get_duration(concat_video)
print(f"\n  Duree video de base : {video_dur:.1f}s")
print(f"  Duree audio FR      : {audio_dur:.1f}s")
print(f"  Ecart               : {audio_dur - video_dur:+.1f}s")

# Reconstruit une extension figee sur mesure (marge de 1s) a partir de la
# derniere image de la video de base, pour couvrir exactement cet audio.
extra = max(0.0, audio_dur - video_dur) + 1.0
last_frame = OUT_DIR / "last_frame.jpg"
subprocess.run(
    ["ffmpeg", "-y", "-v", "error", "-sseof", "-1", "-i", str(concat_video),
     "-vframes", "1", "-q:v", "2", str(last_frame)],
    check=False,
)
freeze_tail = OUT_DIR / "freeze_tail_simple.mp4"
subprocess.run(
    ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(last_frame),
     "-t", f"{extra:.2f}", "-r", "24", "-vf", "scale=720:1280", "-pix_fmt", "yuv420p", str(freeze_tail)],
    check=False,
)

concat_list = OUT_DIR / "concat_extended_simple_list.txt"
concat_list.write_text(f"file '{concat_video.name}'\nfile '{freeze_tail.name}'\n", encoding="utf-8")
concat_extended = OUT_DIR / "concat_60s_extended_simple.mp4"
subprocess.run(
    ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
     "-i", str(concat_list.name), "-c", "copy", str(concat_extended.name)],
    check=False, cwd=OUT_DIR,
)

final_video = OUT_DIR / "final_60s_fr_simple.mp4"
subprocess.run(
    ["ffmpeg", "-y", "-v", "error", "-i", str(concat_extended), "-i", str(audio_path),
     "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
     "-shortest", str(final_video)],
    check=False,
)
print(f"\n=== TERMINE : {final_video} ===")
