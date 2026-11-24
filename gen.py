"""Qwen3-TTS Base: клон голоса по настоящей русской речи (ref_audio + точный ref_text). CPU, GitHub Actions.
Референс и его текст приходят ТОЛЬКО из секретов (env), в репозиторий не попадают."""
import os, sys, time
import numpy as np
import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel
from refaudio import load_ref

TEXT = ("Горный посёлок. Всего за пять рублей! Все здания пустуют. "
        "Рабочие прокладывают трубы, метр за метром. Но из одной трубы идёт дым! "
        "Что строим? Один: мини-гэс. Два: ветряки.")

size = os.environ.get("MODEL_SIZE", "1.7B")
xvec = os.environ.get("X_VECTOR_ONLY", "false").lower() == "true"
ref_b64, ref_text = os.environ.get("REF_AUDIO_B64", ""), os.environ.get("REF_TEXT", "").strip()
if not ref_b64:
    sys.exit("REF_AUDIO_B64 secret is empty")
if not xvec and not ref_text:
    sys.exit("REF_TEXT secret is empty (required when x_vector_only=false)")

os.makedirs("out", exist_ok=True)
torch.set_num_threads(os.cpu_count() or 2)
ref_audio = load_ref(ref_b64)                     # (np.ndarray, sr)
print(f"reference loaded: {len(ref_audio[0]) / ref_audio[1]:.1f}s; model={size}; x_vector_only={xvec}", flush=True)

t0 = time.time()
model = Qwen3TTSModel.from_pretrained(f"Qwen/Qwen3-TTS-12Hz-{size}-Base", device_map="cpu", dtype=torch.float32)
print(f"model loaded in {time.time() - t0:.0f}s", flush=True)

t1 = time.time()
wavs, sr = model.generate_voice_clone(
    text=TEXT, language="Russian",
    ref_audio=ref_audio, ref_text=(ref_text or None), x_vector_only_mode=xvec,
    max_new_tokens=400,
)
audio = np.asarray(wavs[0], dtype=np.float32)
sf.write("out/test.wav", audio, sr)
print(f"generated {len(audio) / sr:.1f}s audio in {time.time() - t1:.0f}s -> out/test.wav", flush=True)
