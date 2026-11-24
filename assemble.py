"""Склейка реплик: единый уровень, короткие фейды, паузы. Без эффектов и компрессии. Только numpy."""
import numpy as np

def assemble(parts, gaps, sr, target_rms=0.085):
    out = []
    for i, x in enumerate(parts):
        x = np.asarray(x, dtype=np.float32).copy()
        idx = np.where(np.abs(x) > 0.01)[0]
        if len(idx):
            x = x[max(idx[0] - int(.03 * sr), 0): idx[-1] + int(.08 * sr)]
        r = float(np.sqrt((x ** 2).mean())) + 1e-9
        x *= target_rms / r
        n = min(int(.012 * sr), len(x) // 2)
        x[:n] *= np.linspace(0, 1, n); x[-n:] *= np.linspace(1, 0, n)
        out.append(x)
        if i < len(parts) - 1:
            out.append(np.zeros(int(gaps[i] * sr), dtype=np.float32))
    y = np.concatenate(out)
    pk = float(np.abs(y).max())
    return y * (0.89 / pk) if pk > 0.89 else y
