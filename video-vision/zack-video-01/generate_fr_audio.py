"""
Genere une voix off en francais (Gemini 3.1 Flash TTS) a partir de
script_60s_fr.txt, et la fusionne sur concat_60s.mp4 deja genere,
sans refaire les 13 scenes. Produit final_60s_fr.mp4 (fichier separe,
ne touche pas a final_60s.mp4 en anglais).
"""
import json
import subprocess
import urllib.request
import urllib.error
import time
from pathlib import Path

API_KEY = Path(r"F:\Tiktok\api.txt").read_text(encoding="utf-8").strip().split(":")[-1].strip()
OUT_DIR = Path(__file__).parent
script_fr = (OUT_DIR / "script_60s_fr.txt").read_text(encoding="utf-8").strip()


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


print("=== Voix off FRANCAISE (Gemini 3.1 Flash TTS) ===")
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
audio_path = OUT_DIR / "voice_60s_fr.wav"
if voice_task:
    voice_data = wait_for_result(voice_task)
    if voice_data:
        url = json.loads(voice_data["resultJson"])["resultUrls"][0]
        urllib.request.urlretrieve(url, audio_path)
        print(f"  Voix OK -> {audio_path}")
    else:
        print("  Echec generation voix.")
        raise SystemExit(1)
else:
    print("  Echec creation tache voix.")
    raise SystemExit(1)

# Duree comparee video (fixe, 13 scenes x 5s) vs audio FR genere.
concat_video = OUT_DIR / "concat_60s.mp4"


def get_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    return float(out.stdout.strip())


video_dur = get_duration(concat_video)
audio_dur = get_duration(audio_path)
print(f"\n  Duree video (image) : {video_dur:.1f}s")
print(f"  Duree audio FR      : {audio_dur:.1f}s")
print(f"  Ecart               : {audio_dur - video_dur:+.1f}s")

final_video = OUT_DIR / "final_60s_fr.mp4"
subprocess.run(
    ["ffmpeg", "-y", "-v", "error", "-i", str(concat_video), "-i", str(audio_path),
     "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
     "-shortest", str(final_video)],
    check=False,
)
print(f"\n=== TERMINE : {final_video} ===")
