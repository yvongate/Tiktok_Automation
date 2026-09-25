"""
Test rapide : genere 2 images via l'API KIE.AI (nano-banana base + nano-banana 2)
pour comparer prix/qualite avant d'integrer au workflow.

Usage:
    python test_nano_banana.py
"""

import json
import time
import urllib.request
import urllib.error
from pathlib import Path

API_KEY = Path(r"F:\Tiktok\api.txt").read_text(encoding="utf-8").strip().split(":")[-1].strip()
BASE_URL = "https://api.kie.ai/api/v1/jobs"
OUT_DIR = Path(__file__).parent

PROMPT = (
    "A young man with light brown sun-tanned skin, short dark messy hair, wearing "
    "a faded beige long-sleeve hiking shirt and worn olive-green cargo pants, no "
    "logos or branding, is frozen mid-step on a cracked red desert trail. His "
    "right boot hovers inches above the ground, where a coiled rattlesnake with "
    "tan and dark brown diamond-patterned scales sits half-hidden in the sand, "
    "tail raised and vibrating. The environment is a harsh midday desert: cracked "
    "reddish-orange earth, scattered dry thorny shrubs, a few weathered grey "
    "rocks, and a distant flat mesa on the horizon under a pale blue sky. Camera "
    "is a low ground-level wide shot looking up along the man's leg toward the "
    "snake in the foreground, with his tense, wide-eyed face visible in the "
    "upper part of the frame. Lighting is harsh natural midday sunlight from "
    "directly above, casting short sharp shadows. Mood: frozen tension, sudden "
    "fear.\n\nsemi-realistic 3D CGI, GTA V / The Last of Us cutscene quality, "
    "realistic skin texture with visible pores, natural cinematic lighting, "
    "detailed real-world environment, photorealistic 3D render, no cartoon, no "
    "cel shading, no Pixar, no simple background, no studio backdrop"
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


def create_task(model, input_body):
    print(f"Envoi de la tache : {model}")
    result = request("POST", "/createTask", {"model": model, "input": input_body})
    if not result or not result.get("data"):
        return None
    print(" ", json.dumps(result, ensure_ascii=False)[:300])
    return result.get("data", {}).get("taskId")


def wait_for_result(task_id, max_wait=180, interval=6):
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
    url = urls[0]
    print(f"  Telechargement -> {out_path}")
    urllib.request.urlretrieve(url, out_path)


def run(label, model, input_body, out_filename):
    print(f"\n=== {label} ===")
    task_id = create_task(model, input_body)
    if not task_id:
        print("  Echec de creation de tache.")
        return
    data = wait_for_result(task_id)
    if data:
        download_result(data, OUT_DIR / out_filename)
        print(f"  OK -> {out_filename}")


if __name__ == "__main__":
    # 2. nano-banana 2 (slug confirme via kie.ai/nano-banana-2 : "nano-banana-2")
    run(
        "Nano Banana 2 (1K)",
        "nano-banana-2",
        {"prompt": PROMPT, "image_size": "9:16", "output_format": "png", "resolution": "1K"},
        "nano-banana-2.png",
    )

    print("\nTermine. Verifie les fichiers dans", OUT_DIR)
