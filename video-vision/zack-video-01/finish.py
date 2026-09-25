"""
Termine la video (voix + montage final) en reutilisant concat.mp4 deja genere,
sans refaire les 8 scenes.
"""
import json
import subprocess
import time
import urllib.request
import urllib.error
from pathlib import Path

API_KEY = Path(r"F:\Tiktok\api.txt").read_text(encoding="utf-8").strip().split(":")[-1].strip()
OUT_DIR = Path(__file__).parent
script = (OUT_DIR / "script.txt").read_text(encoding="utf-8").strip()


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


def create_task(model, input_body):
    result = http_json(
        "https://api.kie.ai/api/v1/jobs/createTask",
        {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        {"model": model, "input": input_body},
        method="POST",
    )
    if result and result.get("data"):
        return result["data"]["taskId"]
    print(f"  createTask -> {result}")
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


print("=== Voix off (Gemini 3.1 Flash TTS, style corrige) ===")
voice_task = create_task(
    "google/gemini-3-1-flash-tts",
    {
        "speakers": [
            {"speaker_id": "Speaker 1", "voice_name": "Zephyr", "audio_profile": "dramatic narrator",
             "style": "Deadpan", "pace": "Natural", "accent": "Neutral"}
        ],
        "dialogue_turns": [{"speaker_id": "Speaker 1", "text": script}],
    },
)
audio_path = OUT_DIR / "voice.wav"
if voice_task:
    voice_data = wait_for_result(voice_task)
    if voice_data:
        url = json.loads(voice_data["resultJson"])["resultUrls"][0]
        urllib.request.urlretrieve(url, audio_path)
        print(f"  Voix OK -> {audio_path}")
    else:
        print("  Echec generation voix, on continue sans audio.")
else:
    print("  Echec creation tache voix, on continue sans audio.")

concat_video = OUT_DIR / "concat.mp4"
final_video = OUT_DIR / "final.mp4"
if audio_path.exists():
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(concat_video), "-i", str(audio_path),
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", str(final_video)],
        check=False,
    )
    print(f"Fusion audio OK -> {final_video}")
else:
    final_video = concat_video

print(f"=== TERMINE : {final_video} ===")
