"""Test: upload raw WAV bytes directly (multipart) to Qwen ASR."""
import os, time, wave, struct, requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")

# Create a tiny synthetic 3-second WAV (440Hz tone, 16kHz mono)
def make_wav(path, duration_s=3, sample_rate=16000):
    n = int(sample_rate * duration_s)
    with wave.open(path, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        import math
        frames = struct.pack(f'<{n}h', *[
            int(32767 * math.sin(2 * math.pi * 440 * i / sample_rate))
            for i in range(n)
        ])
        f.writeframes(frames)

wav_path = "test_chunk.wav"
make_wav(wav_path)
print(f"Created test WAV: {os.path.getsize(wav_path)} bytes")

print("\n[1] Trying multipart binary upload...")
with open(wav_path, "rb") as f:
    resp = requests.post(
        "https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "X-DashScope-Async": "enable",
        },
        files={
            "file": ("test_chunk.wav", f, "audio/wav"),
        },
        data={
            "model": "qwen-audio-3.0-asr-flash-filetrans",
        },
        timeout=30,
    )

print(f"HTTP {resp.status_code}")
print(resp.text[:600])

if resp.ok:
    data = resp.json()
    task_id = data.get("output", {}).get("task_id")
    print(f"\nTask ID: {task_id} — multipart upload WORKS!")

    for i in range(30):
        time.sleep(2)
        poll = requests.get(
            f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}",
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=15,
        )
        pdata = poll.json()
        status = pdata.get("output", {}).get("task_status")
        print(f"  [{i*2}s] {status}")
        if status == "SUCCEEDED":
            print("SUCCESS: chunk-by-chunk mode is possible!")
            break
        elif status in ("FAILED", "CANCELED"):
            print(f"FAILED: {pdata}")
            break
else:
    print("Multipart upload not supported — URL-only mode needed.")
