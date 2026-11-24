"""Chatterbox Multilingual (ru), 3 варианта подачи A/B/C на одном референсе. Референс только из секрета."""
import os, sys, time
import numpy as np
import soundfile as sf
import torch
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
from refaudio import ref_to_path
from fragment import SEGMENTS, VARIANTS
from assemble import assemble

b64 = os.environ.get("REF_AUDIO_B64", "")
if not b64:
    sys.exit("REF_AUDIO_B64 secret is empty")
os.makedirs("out", exist_ok=True)
torch.set_num_threads(os.cpu_count() or 2)
_orig = torch.load
torch.load = lambda *a, **k: _orig(*a, **{**k, "map_location": torch.device("cpu")})   # веса на CPU
ref = ref_to_path(b64)
t0 = time.time()
model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
print(f"model loaded in {time.time() - t0:.0f}s, sr={model.sr}", flush=True)

for name, v in VARIANTS.items():
    parts = []
    for i, (emo, text) in enumerate(SEGMENTS, 1):
        torch.manual_seed(1234 + i)
        t1 = time.time()
        wav = model.generate(text, language_id="ru", audio_prompt_path=ref,
                             exaggeration=v["ex"][emo], cfg_weight=v["cfg"])
        parts.append(wav.squeeze().cpu().numpy())
        print(f"{name} seg{i} [{emo}] {len(parts[-1]) / model.sr:.1f}s in {time.time() - t1:.0f}s", flush=True)
    y = assemble(parts, v["gaps"], model.sr)
    sf.write(f"out/{name}.wav", y, model.sr)
    print(f"== {name}: {len(y) / model.sr:.1f}s saved", flush=True)
