"""
Anime les 2 images nano-banana (base + 2) avec Seedance 1.5 Pro,
pour comparer le rendu final en video.

Usage:
    python test_seedance_animate.py
"""

import json
import time
import urllib.request
import urllib.error
from pathlib import Path

API_KEY = Path(r"F:\Tiktok\api.txt").read_text(encoding="utf-8").strip().split(":")[-1].strip()
BASE_URL = "https://api.kie.ai/api/v1/jobs"
OUT_DIR = Path(__file__).parent

# taskId des 2 images deja generees (pour recuperer leur URL hebergee)
IMAGE_TASKS = {
    "base": "05e6b78fb5a29365592d9ed74b1678d8",
    "nano2": "0a8ad80d461831782844edb397a30f38",
}

ANIMATION_PROMPT = (
    "Camera: slow push-in toward the man's face with a slight handheld shake. "
    "Subject: his chest rises sharply, eyes widen, boot trembles mid-air without "
    "moving forward; the rattlesnake's tail vibrates faster, tongue flicking. "
    "Environment: fine sand drifts in the heat shimmer. Mood: frozen, tense, "
    "suspenseful pace."
)


def request(method, path, body=None):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.read().decode('utf-8')}")
        return None


def get_image_url(task_id):
    result = request("GET", f"/recordInfo?taskId={task_id}")
    if not result:
        return None
    data = result.get("data", {})
    result_json = data.get("resultJson")
    if not result_json:
        return None
    urls = json.loads(result_json).get("resultUrls", [])
    return urls[0] if urls else None


def create_task(model, input_body):
    result = request("POST", "/createTask", {"model": model, "input": input_body})
    if not result or not result.get("data"):
        return None
    print(" ", json.dumps(result, ensure_ascii=False)[:300])
    return result["data"]["taskId"]


def wait_for_result(task_id, max_wait=300, interval=10):
    elapsed = 0
    while elapsed < max_wait:
        result = request("GET", f"/recordInfo?taskId={task_id}")
        if result:
            data = result.get("data", {})
            state = data.get("state")
            print(f"  [{elapsed}s] state={state}")
            if state == "success":
                return data
            if state == "fail":
                print("  ECHEC :", data.get("failMsg"))
                return None
        time.sleep(interval)
        elapsed += interval
    print("  Timeout.")
    return None


def download_result(data, out_path):
    result_json = data.get("resultJson")
    if not result_json:
        print("  Pas de resultJson.")
        return
    urls = json.loads(result_json).get("resultUrls", [])
    if not urls:
        print("  Pas d'URL de resultat.")
        return
    print(f"  Telechargement -> {out_path}")
    urllib.request.urlretrieve(urls[0], out_path)


def run(label, image_task_id, out_filename):
    print(f"\n=== {label} ===")
    image_url = get_image_url(image_task_id)
    if not image_url:
        print("  Impossible de recuperer l'URL de l'image source.")
        return
    print(f"  Image source : {image_url}")

    task_id = create_task(
        "bytedance/seedance-1.5-pro",
        {
            "prompt": ANIMATION_PROMPT,
            "input_urls": [image_url],
            "aspect_ratio": "9:16",
            "resolution": "720p",
            "duration": 5,
            "fixed_lens": False,
            "generate_audio": False,
        },
    )
    if not task_id:
        print("  Echec de creation de tache.")
        return

    data = wait_for_result(task_id)
    if data:
        download_result(data, OUT_DIR / out_filename)
        print(f"  OK -> {out_filename}")


if __name__ == "__main__":
    run("Nano Banana (base) -> Seedance 1.5 Pro", IMAGE_TASKS["base"], "video-base-seedance.mp4")
    run("Nano Banana 2 -> Seedance 1.5 Pro", IMAGE_TASKS["nano2"], "video-nano2-seedance.mp4")
    print("\nTermine. Verifie les fichiers dans", OUT_DIR)
