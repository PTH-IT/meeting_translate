import asyncio
import base64
import json
import sys
import numpy as np
import websockets


async def test_ws(url: str):
    print(f"Connecting to {url}")
    async with websockets.connect(url) as ws:
        print("Connected")

        duration_sec = 2
        sample_rate = 16000
        t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
        audio = (0.3 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
        b64 = base64.b64encode(audio.tobytes()).decode("utf-8")

        payload = {
            "audio": b64,
            "target_langs": ["vi"],
            "sample_rate": sample_rate,
            "chunk_id": 1
        }
        await ws.send(json.dumps(payload))
        print("Sent audio chunk")

        raw = await ws.recv()
        data = json.loads(raw)
        print("Response:", json.dumps(data, ensure_ascii=False, indent=2))


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "ws://localhost:8000/api/ws/multi-lang"
    asyncio.run(test_ws(url))


if __name__ == "__main__":
    main()
