"""Gemini TTS: шёпот -> обычный голос -> крик. Ключ: GEMINI_API_KEY (или подставляется прокси)."""
import base64, json, os, sys, urllib.error, urllib.request, wave

MODEL = os.environ.get("GEMINI_TTS_MODEL", "gemini-2.5-flash-preview-tts")
VOICE = os.environ.get("GEMINI_VOICE", "Puck")
OUT = sys.argv[1] if len(sys.argv) > 1 else "wakeup.wav"

PROMPT = """Озвучь сценку на русском языке одним голосом, строго следуя пометкам в квадратных скобках (их не произносить).
Это игривая сцена: человек будит друга утром.

[тихим шёпотом, на ухо, медленно] Эй... ты ещё спишь?..
[шёпотом, хитро] Ну ладно... я дала тебе шанс...
[обычным голосом, бодро и строго] Так! Вставай! Я считаю до трёх.
[обычным голосом, с паузой] Раз...
[громче, с нажимом] Два...
[громко кричит изо всех сил] ТРИ!!! ПОДЪЁМ!!! ВСТАВАЙ СЕЙЧАС ЖЕ!!!
"""

body = {
    "contents": [{"parts": [{"text": PROMPT}]}],
    "generationConfig": {
        "responseModalities": ["AUDIO"],
        "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}},
    },
}
req = urllib.request.Request(
    f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
    data=json.dumps(body).encode(),
    headers={"Content-Type": "application/json",
             "x-goog-api-key": os.environ.get("GEMINI_API_KEY", "dummy")},
)
try:
    with urllib.request.urlopen(req, timeout=300) as r:
        resp = json.load(r)
except urllib.error.HTTPError as e:
    sys.exit(f"HTTP {e.code}: {e.read().decode()[:500]}")
pcm = base64.b64decode(resp["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
with wave.open(OUT, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
print(f"OK {OUT} {len(pcm)/48000:.1f}s")
