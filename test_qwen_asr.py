"""Quick test: submit a public audio URL to Qwen ASR and poll for result."""
import os, time, requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
print(f"Key loaded: {API_KEY[:20]}...")

# Use a short public English audio sample
TEST_URL = "https://dashscope.oss-cn-beijing.aliyuncs.com/samples/audio/paraformer/hello_world_male2.wav"

print("\n[1] Submitting task...")
resp = requests.post(
    "https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable",
    },
    json={
        "model": "qwen-audio-3.0-asr-flash-filetrans",
        "input": {
            "file_urls": [TEST_URL],
        },
    },
    timeout=30,
)
print(f"HTTP {resp.status_code}")
print(resp.text[:800])

if not resp.ok:
    print("FAILED: Could not submit task")
    exit(1)

data = resp.json()
task_id = data.get("output", {}).get("task_id")
print(f"\nTask ID: {task_id}")

if not task_id:
    print("FAILED: No task_id in response")
    exit(1)

print("\n[2] Polling for completion...")
for i in range(60):
    time.sleep(2)
    poll = requests.get(
        f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=15,
    )
    pdata = poll.json()
    status = pdata.get("output", {}).get("task_status")
    print(f"  [{i*2}s] status={status}")

    if status == "SUCCEEDED":
        results = pdata.get("output", {}).get("results", [])
        tr_url = results[0].get("transcription_url") if results else None
        print(f"\n[3] Fetching transcription from: {tr_url}")
        tr = requests.get(tr_url, timeout=15)
        trdata = tr.json()
        print("\n=== Full transcription JSON ===")
        import json; print(json.dumps(trdata, ensure_ascii=False, indent=2)[:2000])
        break
    elif status in ("FAILED", "CANCELED"):
        print(f"FAILED: Task {status}")
        print(pdata)
        break
else:
    print("TIMEOUT: Task did not complete in 120s")
