"""Декодирование референса из секрета GitHub (base64) во временную папку ВНЕ репозитория. Файл наружу не пишется."""
import atexit, base64, os, shutil, subprocess, sys, tempfile, wave
import numpy as np


def load_ref(b64: str, min_s: float = 2.0, max_s: float = 15.0):
    raw = base64.b64decode("".join(b64.split()))
    with tempfile.TemporaryDirectory(prefix="ref_") as d:      # /tmp, не рабочая папка и не out/
        src, dst = os.path.join(d, "in.bin"), os.path.join(d, "ref.wav")
        with open(src, "wb") as f:
            f.write(raw)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-t", str(max_s), "-ac", "1", "-ar", "24000", dst], check=True)
        with wave.open(dst) as w:
            sr, n = w.getframerate(), w.getnframes()
            x = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float32) / 32768.0
    dur = len(x) / sr
    if dur < min_s:
        raise ValueError(f"reference too short: {dur:.1f}s (need >= {min_s}s)")
    if float(np.sqrt((x ** 2).mean())) < 0.005:
        raise ValueError("reference is almost silent")
    return x, sr


def ref_to_path(b64: str, max_s: float = 12.0) -> str:
    """Для моделей, которым нужен путь к файлу: wav во временной папке вне репозитория, удаляется при выходе."""
    x, sr = load_ref(b64, max_s=max_s)
    d = tempfile.mkdtemp(prefix="ref_"); atexit.register(shutil.rmtree, d, ignore_errors=True)
    p = os.path.join(d, "ref.wav")
    with wave.open(p, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((x * 32767).astype("<i2").tobytes())
    return p


if __name__ == "__main__":      # самопроверка без torch: python refaudio.py файл_base64.txt
    x, sr = load_ref(open(sys.argv[1]).read())
    print(f"ok: {len(x) / sr:.1f}s @ {sr} Hz")
