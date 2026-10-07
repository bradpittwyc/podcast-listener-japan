"""Test: DashScope file upload API → get URL → submit transcription."""
import os, time, wave, struct, requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")

# Reuse the WAV from previous test
wav_path = "test_chunk.wav"
if not os.path.exists(wav_path):
    def make_wav(path, duration_s=3, sample_rate=16000):
        import math
        n = int(sample_rate * duration_s)
        with wave.open(path, 'w') as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(sample_rate)
            frames = struct.pack(f'<{n}h', *[int(32767 * math.sin(2*math.pi*440*i/sample_rate)) for i in range(n)])
            f.writeframes(frames)
    make_wav(wav_path)

print("[1] Uploading file to DashScope storage...")
with open(wav_path, "rb") as f:
    upload_resp = requests.post(
        "https://dashscope.aliyuncs.com/api/v1/uploads",
        headers={"Authorization": f"Bearer {API_KEY}"},
        files={"files": ("test_chunk.wav", f, "audio/wav")},
        data={"model": "qwen-audio-3.0-asr-flash-filetrans"},
        timeout=30,
    )
print(f"HTTP {upload_resp.status_code}")
print(upload_resp.text[:600])

if not upload_resp.ok:
    print("Upload failed, trying alternative endpoint...")
    # Try DashScope batch file upload
    with open(wav_path, "rb") as f:
        upload_resp = requests.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/files",
            headers={"Authorization": f"Bearer {API_KEY}"},
            files={"file": ("test_chunk.wav", f, "audio/wav")},
            data={"purpose": "assistants"},
            timeout=30,
        )
    print(f"Alt endpoint HTTP {upload_resp.status_code}")
    print(upload_resp.text[:600])
