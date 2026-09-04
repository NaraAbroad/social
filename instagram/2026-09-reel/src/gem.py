"""Small helper around the Gemini API. Reads the key from .gemini_key so no
credential ever appears on a command line."""
import json, os, urllib.request

BASE = "https://generativelanguage.googleapis.com/v1beta"
KEY = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".gemini_key")).read().strip()


def call(path, payload=None, method=None):
    url = f"{BASE}/{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method or ("POST" if data else "GET"))
    req.add_header("x-goog-api-key", KEY)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")


if __name__ == "__main__":
    st, d = call("models?pageSize=200")
    models = d.get("models", [])
    tts = [m for m in models if "tts" in m["name"].lower()]
    print(f"HTTP {st} — {len(models)} models, {len(tts)} TTS:")
    for m in tts:
        print("  ", m["name"], "|", m.get("displayName"),
              "|", ",".join(m.get("supportedGenerationMethods", [])))
