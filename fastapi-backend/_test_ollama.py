import httpx, json, os

# Bypass proxy for localhost requests
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

# Check Ollama models
try:
    r = httpx.get("http://localhost:11434/api/tags", timeout=10)
    print("=== Ollama Models ===")
    models = r.json().get("models", [])
    for m in models:
        print(f"  - {m['name']} ({m.get('size','?')})")
    print(f"Total: {len(models)} models")
except Exception as e:
    print(f"Ollama tags error: {e}")

# Test generation
print()
try:
    r = httpx.post("http://localhost:11434/api/generate", json={
        "model": "qwen3.5:latest",
        "prompt": "Say hello in one word",
        "stream": False
    }, timeout=30)
    print(f"=== Test Generation (qwen3.5:latest) ===")
    print(f"Status: {r.status_code}")
    resp = r.json()
    print(f"Response: {resp.get('response','')[:300]}")
    if resp.get('response'):
        print("Ollama generation: OK")
    else:
        print("Ollama generation: EMPTY response - model may have issues")
        print(f"Full keys: {list(resp.keys())}")
except Exception as e:
    print(f"Generation error: {e}")
