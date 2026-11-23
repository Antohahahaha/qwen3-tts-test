"""Qwen3-TTS-12Hz-1.7B-VoiceDesign на CPU (GitHub Actions). Тест ~14 с: 5 реплик сценария + проверка «дома́»."""
import time, numpy as np, torch, soundfile as sf
from qwen_tts import Qwen3TTSModel

BASE = ("Male Russian voice, 19 years old, light soft tenor, no deep bass, young and warm, natural conversational "
        "storytelling as if telling a friend, not an announcer. Restrained emotions: no laughter, no smile in the voice, "
        "no cheerful or excited tone, no theatrical acting. ")
LINES = [
 ("Горный посёлок. Всего за пять рублей!", "Mild curiosity with a light touch of surprise, understated."),
 ("Дома пусты. Все давно уехали...", "Serious and slightly tense, subdued, a little slower."),
 ("Рабочие прокладывают трубы, метр за метром.", "Concentrated and matter-of-fact, steady even pace."),
 ("Но из одной трубы идёт дым!", "Sincere genuine surprise, taken aback, restrained, not happy."),
 ("Что строим? Один: мини-гэс. Два: ветряки.", "Quiet intrigue, slightly lowered voice, calm questioning tone."),
]
EXTRA = [("Все дома в посёлке пустуют.", "Calm and clear."), ("Все дома́ в посёлке пустуют.", "Calm and clear.")]

torch.set_num_threads(__import__("os").cpu_count())
t0 = time.time()
m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign", device_map="cpu", dtype=torch.float32)
print(f"model loaded {time.time()-t0:.0f}s", flush=True)

def gen(items, tag):
    out = []
    for i, (t, e) in enumerate(items, 1):
        t1 = time.time()
        w, sr = m.generate_voice_design(text=t, language="Russian", instruct=BASE + e)
        sf.write(f"out/{tag}{i}.wav", w[0], sr); out.append(w[0])
        print(f"{tag}{i}: {len(w[0])/sr:.1f}s audio in {time.time()-t1:.0f}s", flush=True)
    return out, sr

import os; os.makedirs("out", exist_ok=True)
parts, sr = gen(LINES, "line")
gap = np.zeros(int(sr * 0.2), dtype=parts[0].dtype)
full = np.concatenate([x for p in parts for x in (p, gap)][:-1])
sf.write("out/test_full.wav", full, sr); print(f"TOTAL {len(full)/sr:.1f}s", flush=True)
gen(EXTRA, "stress_")
