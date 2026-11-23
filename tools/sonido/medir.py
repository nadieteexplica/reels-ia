"""Medidas de audio compartidas por generar.py, mezclar.py y ver.py.

Loudness: implementación propia de ITU-R BS.1770-4 (la misma norma que usa el filtro `ebur128` de ffmpeg):
  - ponderación K (estante de agudos + pasa-altos) con los coeficientes oficiales para 48 kHz,
  - bloques de 400 ms con 75 % de traslape, compuerta absoluta de −70 LUFS y relativa de −10 LU.
  - Diferencia con ffmpeg: si el clip dura menos de 400 ms, ffmpeg no alcanza a armar ni un bloque y entrega
    −70 LUFS; acá se mide el clip completo como un solo bloque (sirve para clicks y ticks cortos).
  `generar.py --verificar` compara esta medida con `ffmpeg ebur128` en los clips de 0,4 s o más.
Peak: true peak aproximado (sobremuestreo ×4, como pide BS.1770 para dBTP).
Todo trabaja a 48 kHz, arreglos float (n,) mono o (n, canales).
"""
import json
import re
import subprocess

import numpy as np
from scipy.signal import lfilter, resample_poly

SR = 48000

# Coeficientes BS.1770-4 para 48 kHz
_K1_B = [1.53512485958697, -2.69169618940638, 1.19839281085285]
_K1_A = [1.0, -1.69065929318241, 0.73248077421585]
_K2_B = [1.0, -2.0, 1.0]
_K2_A = [1.0, -1.99004745483398, 0.99007225036621]


def como_2d(x):
    x = np.asarray(x, dtype=np.float64)
    return x[:, None] if x.ndim == 1 else x


def ponderar_k(x):
    x = como_2d(x)
    y = lfilter(_K1_B, _K1_A, x, axis=0)
    return lfilter(_K2_B, _K2_A, y, axis=0)


def lufs(x, sr=SR):
    """Loudness integrado (LUFS) según BS.1770-4. Clips < 400 ms: un solo bloque con todo el clip."""
    assert sr == SR, "medir.lufs sólo trae coeficientes para 48 kHz"
    y = ponderar_k(x)
    n = len(y)
    pot = np.sum(y ** 2, axis=1)                       # suma de canales (pesos 1,0 para L/R/mono)
    bl = int(0.4 * sr)
    if n < bl:
        m = pot.mean() if n else 0.0
        return -0.691 + 10 * np.log10(m + 1e-20)
    paso = int(0.1 * sr)
    acum = np.concatenate([[0.0], np.cumsum(pot)])
    ini = np.arange(0, n - bl + 1, paso)
    z = (acum[ini + bl] - acum[ini]) / bl
    l_bl = -0.691 + 10 * np.log10(z + 1e-20)
    z1 = z[l_bl > -70]
    if not len(z1):
        return -70.0
    rel = -0.691 + 10 * np.log10(z1.mean()) - 10
    z2 = z[(l_bl > -70) & (l_bl > rel)]
    return -0.691 + 10 * np.log10(z2.mean())


def true_peak_db(x):
    x = como_2d(x)
    if not len(x):
        return -120.0
    up = resample_poly(x, 4, 1, axis=0)
    return 20 * np.log10(max(np.abs(up).max(), np.abs(x).max()) + 1e-12)


def rms_db(x):
    x = como_2d(x)
    if not len(x):
        return -120.0
    return 10 * np.log10(np.mean(np.sum(x ** 2, axis=1) / x.shape[1]) + 1e-12)


def leer_audio(ruta, canales=1, sr=SR):
    """Decodifica cualquier formato con ffmpeg a float32 (n,) o (n, canales)."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ruta), "-ac", str(canales), "-ar", str(sr),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32).astype(np.float64)
    return a if canales == 1 else a.reshape(-1, canales)


def ebur128_ffmpeg(ruta):
    """Mide con ffmpeg ebur128 (integrado y true peak). Devuelve (I_lufs, TP_dbtp)."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(ruta), "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True, text=True)
    txt = r.stderr
    resumen = txt[txt.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+|-inf) LUFS", resumen)
    tp = re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", resumen)
    f = lambda m: float(m.group(1)) if m and m.group(1) != "-inf" else float("-inf")
    return f(i), f(tp)


def leer_json(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def escribir_json(ruta, obj):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")
