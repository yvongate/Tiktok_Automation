"""
Test isole : genere une image (nano-banana, meme style que le pipeline
principal) puis l'anime avec Runway au lieu de Seedance, pour comparer
qualite/prix. Meme pattern createTask + polling que generate.py.
"""
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

API_KEY = Path(r"F:\Tiktok\api.txt").read_text(encoding="utf-8").strip().split(":")[-1].strip()
OUT_DIR = Path(__file__).parent

STYLE_LOCK = (
    "semi-realistic 3D CGI, GTA V / The Last of Us cutscene quality, realistic skin "
    "texture with visible pores, natural cinematic lighting, detailed real-world "
    "environment, photorealistic 3D render, no cartoon, no cel shading, no Pixar, "
    "no simple background, no studio backdrop"
)

IMAGE_PROMPT = (
    "Tom, a middle-aged man with light skin, short dark-brown hair, wearing a navy-blue "
    "sweater, stands in a modern office at night, arms crossed, confident held pose, "
    "in front of a glass wall overlooking a lit city skyline, dramatic low-key lighting, "
    "medium shot, " + STYLE_LOCK
)
ANIMATION_PROMPT = (
    "Camera static, locked wide shot. Subject motion: Tom slowly blinks and takes a slow, "
    "calm breath, slight natural sway - no camera movement."
)


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


def wait_for_result(task_id, max_wait=300, interval=8):
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
                print(f"    ECHEC : {data.get('failMsg')}")
                return None
        time.sleep(interval)
        elapsed += interval
    print("    Timeout.")
    return None


def get_result_url(data):
    result_json = data.get("resultJson")
    if not result_json:
        return None
    urls = json.loads(result_json).get("resultUrls", [])
    return urls[0] if urls else None


print("=== 1. Image (nano-banana) ===")
img_task = create_task(
    "google/nano-banana",
    {"prompt": IMAGE_PROMPT, "image_size": "9:16", "output_format": "png"},
)
if not img_task:
    raise SystemExit("Echec creation tache image.")
img_data = wait_for_result(img_task)
if not img_data:
    raise SystemExit("Echec generation image.")
img_url = get_result_url(img_data)
print(f"  Image OK : {img_url}")
urllib.request.urlretrieve(img_url, OUT_DIR / "runway_test_source.png")

print("\n=== 2. Animation (Runway, 720p, 9:16, 5s, sans watermark) ===")
vid_task = create_task(
    "runway",
    {
        "prompt": ANIMATION_PROMPT,
        "image_url": img_url,
        "duration": "5",
        "quality": "720p",
        "aspect_ratio": "9:16",
        "watermark": "",
    },
)
if not vid_task:
    raise SystemExit("Echec creation tache video Runway.")
vid_data = wait_for_result(vid_task, max_wait=300)
if not vid_data:
    raise SystemExit("Echec animation Runway.")
vid_url = get_result_url(vid_data)
print(f"  Video Runway OK : {vid_url}")
out_path = OUT_DIR / "runway_test_clip.mp4"
urllib.request.urlretrieve(vid_url, out_path)
print(f"\n=== TERMINE : {out_path} ===")
