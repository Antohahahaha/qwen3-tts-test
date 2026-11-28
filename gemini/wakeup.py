"""Gemini TTS: шёпот -> обычный голос -> крик. Ключ: GEMINI_API_KEY (или подставляется прокси)."""
import base64, json, os, sys, urllib.error, urllib.request, wave

MODEL = os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
VOICE = os.environ.get("GEMINI_VOICE", "puck").lower()
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
    "model": MODEL,
    "modalities": ["audio"],
    "audio": {"voice": VOICE, "format": os.environ.get("GEMINI_FMT", "wav")},
    "messages": [{"role": "user", "content": PROMPT}],
}
# OpenAI-совместимый эндпоинт Gemini: ключ в Authorization: Bearer
key = os.environ.get("GEMINI_API_KEY")
req = urllib.request.Request(
    "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
    data=json.dumps(body).encode(),
    headers={"Content-Type": "application/json",
             **({"Authorization": f"Bearer {key}"} if key else {})},
)
try:
    with urllib.request.urlopen(req, timeout=300) as r:
        resp = json.load(r)
except urllib.error.HTTPError as e:
    sys.exit(f"HTTP {e.code}: {e.read().decode()[:500]}")
if isinstance(resp, list):
    resp = resp[0]
msg = resp["choices"][0]["message"]
if "audio" not in msg:
    sys.exit(f"Нет аудио в ответе: {json.dumps(msg, ensure_ascii=False)[:400]}")
data = base64.b64decode(msg["audio"]["data"])
if data[:4] == b"RIFF":
    open(OUT, "wb").write(data)
else:  # сырой PCM 24 кГц 16 бит моно
    with wave.open(OUT, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(data)
with wave.open(OUT) as w:
    dur = w.getnframes() / w.getframerate()
print(f"OK {OUT} {dur:.1f}s")
