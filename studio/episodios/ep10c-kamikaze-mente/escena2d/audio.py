"""Audio del Ep. 10c: voz + música sintetizada (Re menor lento: pad oscuro, pulso grave, golpes en los giros) + efectos
puntuales (viento, motor en picada, antiaéreos, papel, golpe en "vergüenza") → <salida>/mix.wav a −14 LUFS."""
import json, os, subprocess, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.argv = sys.argv[:2] if len(sys.argv) > 1 else sys.argv
import video as VV

OUT = sys.argv[1] if len(sys.argv) > 1 else AQUI
SR = 48000
DUR = VV.DUR
N = int(DUR * SR)
rng = np.random.default_rng(3)
T = VV.T
tw = VV.tw


def filt(x, lo=None, hi=None):
    if lo and hi:
        return sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), x)
    if lo:
        return sosfilt(butter(2, lo, btype="high", fs=SR, output="sos"), x)
    return sosfilt(butter(2, hi, btype="low", fs=SR, output="sos"), x)


def tt(d):
    return np.arange(int(d * SR)) / SR


def env(n, a=0.004, d=0.1):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def tono(f, d, a=0.003, dec=0.2):
    t = tt(d)
    ph = 2 * np.pi * np.cumsum(np.broadcast_to(np.asarray(f, float), t.shape)) / SR if np.ndim(f) else 2 * np.pi * f * t
    return np.sin(ph) * env(len(t), a, dec)


def add(buf, x, at, g=1.0):
    i = int(at * SR)
    j = min(len(buf), i + len(x))
    if 0 <= i < len(buf):
        buf[i:j] += g * x[: j - i]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def sierra(f, d, k=8):
    t = tt(d)
    return sum(np.sin(2 * np.pi * f * n * t) / n for n in range(1, k + 1) if f * n < 12000) * 0.6


def pad(notas, d, corte=800):
    t = tt(d)
    x = np.zeros(len(t))
    for m in notas:
        for dt in (-0.004, 0.0, 0.005):
            x += sierra(hz(m) * (1 + dt), d)[: len(t)]
    x = filt(x / (3 * len(notas)), 40, corte)
    return x * np.minimum(1, t / 0.5) * np.minimum(1, np.maximum(0, d - t) / 0.5)


def golpe(g=1.0, cola=1.6):
    n = int(cola * SR)
    x = tono(np.linspace(70, 38, n), cola, 0.002, cola * 0.35) * 1.1
    m = int(0.25 * SR)
    x[:m] += filt(rng.standard_normal(m), 200, 5000) * env(m, 0.001, 0.05) * 0.6
    return x * g


def latido(g=1.0):
    out = np.zeros(int(0.8 * SR))
    for at, gg in ((0.0, 1.0), (0.24, 0.7)):
        add(out, tono(np.linspace(65, 40, int(0.3 * SR)), 0.3, 0.003, 0.08) * gg, at)
    return out * g


def viento(d, g=1.0):
    n = int(d * SR)
    x = filt(rng.standard_normal(n), 80, 900) * 0.06 + filt(rng.standard_normal(n), 900, 4000) * 0.012
    return x * (0.75 + 0.25 * np.sin(2 * np.pi * 0.13 * tt(d))) * g


def motor(d, f0, f1, g=1.0):
    t = tt(d)
    f = np.linspace(f0, f1, len(t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.tanh(sum(np.sin(ph * k) / k ** 0.8 for k in range(1, 16)) * 0.45) * 0.5
    x += filt(rng.standard_normal(len(t)), 200, 4000) * 0.08
    return filt(x, 30, 5000) * g * np.minimum(1, t / 0.2)


def flak(d, g=1.0):
    out = np.zeros(int((d + 1.0) * SR))
    for k in range(int(d * 5)):
        n = int(0.6 * SR)
        s = filt(rng.standard_normal(n), 60, 1500) * env(n, 0.002, 0.15) + tono(np.linspace(80, 40, n), 0.6, 0.002, 0.12) * 0.6
        add(out, s * rng.uniform(0.4, 1.0), k / 5 + rng.uniform(0, 0.1))
    return out * g


def papel(d=0.6):
    n = int(d * SR)
    return filt(rng.standard_normal(n), 1200, 8000) * (0.4 + 0.6 * np.abs(np.sin(np.linspace(0, 9, n)))) * env(n, 0.05, 0.3) * 0.25


# voz
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.abspath(os.path.join(AQUI, "../../../../out/tts/ep10c-kamikaze-mente.mp3")),
                      "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
v = np.frombuffer(raw, np.float32).copy()
v = np.pad(v, (0, max(0, N - len(v))))[:N]
v = v / (np.abs(v).max() + 1e-9) * 0.9

# música: Dm Bb Gm A en negras a 64 bpm; pulso grave desde la guerra (plano 7) hasta Okinawa; se abre al final
m = np.zeros(N)
NEG = 60 / 64; COMP = 4 * NEG
prog = [(50, 53, 57), (46, 50, 53), (43, 46, 50), (45, 49, 52)]
raiz = [38, 34, 31, 33]
for b in range(int(DUR / COMP) + 1):
    add(m, pad(prog[b % 4], COMP + 0.6, 700), b * COMP, 0.5)
k = 0
while k * NEG / 2 < DUR:
    t = k * NEG / 2
    if T[7][0] <= t < T[17][0]:
        n = int(NEG / 2 * SR)
        add(m, filt(sierra(hz(raiz[int(t / COMP) % 4]), NEG / 2, 12)[:n], 30, 600) * env(n, 0.004, 0.16), t, 0.6 if k % 2 == 0 else 0.4)
    k += 1
for t0 in (T[4][0], T[7][0], T[10][0], T[15][0], T[18][0]):
    add(m, golpe(0.7), t0 - 0.02)
m = filt(m, 30, 9000)
m /= np.abs(m).max() + 1e-9
envv = np.convolve(np.abs(v), np.ones(int(0.08 * SR)) / int(0.08 * SR), mode="same")
m *= 1.0 - 0.55 * np.clip(envv / 0.15, 0, 1)
vr = np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2)); mr = np.sqrt(np.mean((m * 0.45)[m != 0] ** 2) + 1e-12)
m *= (vr / 10 ** (15.0 / 20)) / mr

fx = np.zeros(N)
add(fx, viento(T[4][0]), 0.0, 0.8)
add(fx, viento(T[10][0] - T[8][0]), T[8][0], 0.6)
add(fx, motor(T[10][0] - T[9][0], 30, 46, 0.6), T[9][0])
add(fx, flak(T[10][0] - T[9][0], 0.4), T[9][0] + 0.2)
for k in (10, 11, 12):
    add(fx, papel(0.4), T[k][0] + 0.05, 0.5)
for i in range(6):
    add(fx, tono(900 + 40 * i, 0.08, 0.001, 0.03) * 0.25, T[13][0] + 0.5 + i * 0.32, 0.6)     # gotas
add(fx, papel(0.8), T[14][0] + 0.1, 0.8)
add(fx, golpe(0.9, 2.0), tw("vergüenza") - 0.05)
add(fx, latido(0.9), T[16][0] + 0.2); add(fx, latido(0.9), T[16][0] + 1.1)
add(fx, papel(0.6), T[18][0] + 0.1, 0.6)
mix = v + m * 0.45 + fx * 0.45
mix = np.tanh(mix * 1.1) / 1.1
mix = mix / (np.abs(mix).max() + 1e-9) * 0.9
os.makedirs(OUT, exist_ok=True)
tmp = os.path.join(OUT, "pre.wav")
wavfile.write(tmp, SR, (mix * 32767).astype(np.int16))
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "alimiter=limit=0.6:level=false,loudnorm=I=-14:TP=-2.0:LRA=11",
                "-ar", "48000", os.path.join(OUT, "mix.wav")], check=True)
print("ok audio", os.path.join(OUT, "mix.wav"))
