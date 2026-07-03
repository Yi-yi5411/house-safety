import asyncio, httpx, json

async def test():
    payload = {
        "model": "qwen3.5:latest",
        "messages": [
            {"role": "system", "content": "You must output in Chinese."},
            {"role": "user", "content": "Say hello in Chinese, 10 words max."}
        ],
        "stream": False,
        "think": False,
        "options": {"temperature": 0.3, "num_predict": 512}
    }
    print("Payload:", json.dumps(payload, indent=2))
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post("http://host.docker.internal:11434/api/chat", json=payload)
        result = r.json()
        msg = result.get("message", {})
        print(f"content: {repr(msg.get('content', ''))}")
        print(f"thinking_len: {len(msg.get('thinking', ''))}")
        print(f"eval_count: {result.get('eval_count')}")
        print(f"done_reason: {result.get('done_reason')}")

asyncio.run(test())
