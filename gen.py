"""Qwen3-TTS-12Hz-1.7B-VoiceDesign на CPU (GitHub Actions): ОДИН непрерывный тест ~10-15 с, один голос."""
import os, time
import numpy as np
import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel

TEXT = ("Горный посёлок. Всего за пять рублей! Все здания пустуют. "
        "Рабочие прокладывают трубы, метр за метром. Но из одной трубы идёт дым! "
        "Что строим? Один: мини-гэс. Два: ветряки.")

INSTRUCT = (
    "A young Russian man, 19 years old. Soft, light, warm tenor voice, no deep bass, not a broadcaster or announcer. "
    "Natural conversational storytelling in quiet, close, relaxed tone, like telling a friend a story. "
    "Emotions are restrained and follow the meaning: mild curiosity with a light touch of surprise at the start, "
    "serious and slightly tense when describing the empty buildings, concentrated and matter-of-fact about the work, "
    "sincere genuine surprise at the smoke, quiet intrigue at the final question. "
    "No laughter, no giggling, no smile in the voice, no cheerful or excited tone, no theatrical acting, no shouting."
)

os.makedirs("out", exist_ok=True)
torch.set_num_threads(os.cpu_count() or 2)
t0 = time.time()
model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign", device_map="cpu", dtype=torch.float32
)
print(f"model loaded in {time.time() - t0:.0f}s", flush=True)

t1 = time.time()
wavs, sr = model.generate_voice_design(
    text=TEXT, language="Russian", instruct=INSTRUCT, max_new_tokens=400
)
audio = np.asarray(wavs[0], dtype=np.float32)
sf.write("out/test.wav", audio, sr)
print(f"generated {len(audio) / sr:.1f}s audio in {time.time() - t1:.0f}s -> out/test.wav", flush=True)
