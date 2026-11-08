"""Audio del Ep. 10e: voz (con 2 respiros agregados) + koto sintetizado (Karplus-Strong, escala in en Re) sobre un bordón grave,
campana en "Flor de cerezo" y en la última "flor", taiko en "dioses", silencio en la almohada, fuego en las cartas
→ <salida>/mix.wav a −14 LUFS."""
import json, os, subprocess, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, lfilter

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else AQUI
sys.argv = sys.argv[:1]
sys.path.insert(0, AQUI)
import video as VV

SR = 48000
DUR = VV.DUR
N = int(DUR * SR)
rng = np.random.default_rng(11)
T, tw = VV.T, VV.tw


def filt(x, lo=None, hi=None, o=2):
    if lo and hi:
        return sosfilt(butter(o, [lo, hi], btype="band", fs=SR, output="sos"), x)
    if lo:
        return sosfilt(butter(o, lo, btype="high", fs=SR, output="sos"), x)
    return sosfilt(butter(o, hi, btype="low", fs=SR, output="sos"), x)


def tt(d):
    return np.arange(int(d * SR)) / SR


def env(n, a=0.004, d=0.1):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def add(buf, x, at, g=1.0):
    i = int(at * SR)
    if i < 0:
        x = x[-i:]; i = 0
    j = min(len(buf), i + len(x))
    if i < len(buf):
        buf[i:j] += g * x[: j - i]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def koto(m, d=2.6, brillo=0.6):
    f = hz(m)
    L = int(SR / f)
    n = int(d * SR)
    x = np.zeros(n)
    x[:L] = filt(rng.uniform(-1, 1, L), None, 2000 + 5000 * brillo)
    g = 0.996
    a = np.zeros(L + 2); a[0] = 1; a[L] = -g / 2; a[L + 1] = -g / 2
    y = lfilter([1.0], a, x)
    y = y + 0.3 * np.diff(y, prepend=0)          # ataque de uña
    return y / (np.abs(y).max() + 1e-9) * np.minimum(1, np.arange(n) / (0.002 * SR))


def bordon(d, notas=(38, 45), g=1.0):
    t = tt(d)
    x = sum(np.sin(2 * np.pi * hz(m) * t) + 0.3 * np.sin(4 * np.pi * hz(m) * t + 0.4) for m in notas)
    x *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.08 * t)
    return filt(x, 30, 800) * np.minimum(1, t / 1.5) * np.minimum(1, np.maximum(0, d - t) / 1.5) * g


def campana(g=1.0):
    d = 3.0
    t = tt(d)
    x = sum(a_ * np.sin(2 * np.pi * f * t) * np.exp(-t / dec) for f, a_, dec in ((880, 1.0, 1.4), (2 * 880 * 1.004, 0.4, 0.8), (3.01 * 880, 0.25, 0.5), (4.2 * 880, 0.12, 0.3)))
    return x * np.minimum(1, t / 0.002) * 0.35 * g


def taiko(g=1.0):
    d = 1.6
    t = tt(d)
    x = np.sin(2 * np.pi * np.cumsum(np.linspace(95, 42, len(t))) / SR) * np.exp(-t / 0.35)
    n = int(0.06 * SR)
    x[:n] += filt(rng.standard_normal(n), 100, 1500) * env(n, 0.001, 0.02) * 0.7
    return x * g


def viento(d, g=1.0):
    n = int(d * SR)
    x = filt(rng.standard_normal(n), 80, 700) * 0.05 + filt(rng.standard_normal(n), 700, 3000) * 0.008
    return x * (0.75 + 0.25 * np.sin(2 * np.pi * 0.11 * tt(d))) * g


def motor_lejos(d, g=1.0):
    t = tt(d)
    f = np.linspace(42, 50, len(t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.tanh(sum(np.sin(ph * k) / k ** 0.8 for k in range(1, 12)) * 0.4)
    return filt(x, 40, 900) * np.minimum(1, t / 0.3) * np.maximum(0, 1 - t / d) ** 1.5 * g


def gota(g=1.0):
    d = 0.25
    t = tt(d)
    return np.sin(2 * np.pi * np.cumsum(np.linspace(1400, 700, len(t))) / SR) * np.exp(-t / 0.04) * 0.3 * g


def fuego(d, g=1.0):
    n = int(d * SR)
    x = filt(rng.standard_normal(n), 60, 600) * 0.12
    for _ in range(int(d * 28)):
        i = rng.integers(0, n - 2000)
        m = rng.integers(200, 1500)
        x[i:i + m] += filt(rng.standard_normal(m), 1500, 9000) * env(m, 0.0003, 0.004) * rng.uniform(0.2, 1.0)
    t = tt(d)
    return x * np.minimum(1, t / 0.6) * g


# ---------------------------------------------------------------- voz con respiros
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.abspath(os.path.join(AQUI, "../../../../out/tts/ep10e-kamikaze-cerezo.mp3")),
                      "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
v0 = np.frombuffer(raw, np.float32).copy()
w0 = json.load(open(os.path.join(VV.EPI, "words.json")))
partes, i_ant = [], 0
for p, d in VV.PAUSAS:
    antes = max(w["e"] for w in w0 if w["e"] <= p + 0.02)
    despues = min(w["s"] for w in w0 if w["s"] >= p - 0.02)
    assert antes <= p <= despues, (p, antes, despues)
    i = int(p * SR)
    partes += [v0[i_ant:i], np.zeros(int(d * SR), np.float32)]
    i_ant = i
partes.append(v0[i_ant:])
v = np.concatenate(partes)
v = np.pad(v, (0, max(0, N - len(v))))[:N]
v = v / (np.abs(v).max() + 1e-9) * 0.9

# ---------------------------------------------------------------- koto
ESC = [50, 51, 55, 57, 58, 62, 63, 67, 69, 70, 74]     # in en Re
NEG = 60 / 72
m = np.zeros(N)
frases = [[5, 7, 8, 7, 5, 4, 3], [5, 6, 8, 9, 8, 6, 5], [4, 5, 7, 5, 4, 2, 0], [7, 8, 10, 9, 8, 7, 5]]


def tocar(t0, t1, densidad=1.0, g=1.0, base=0):
    k, fi = 0, 0
    t = t0
    while t < t1:
        fr = frases[(fi + base) % len(frases)]
        for j, idx in enumerate(fr):
            tn = t + j * NEG / 2 / densidad
            if tn >= t1:
                break
            add(m, koto(ESC[idx], 2.4, 0.5) * (0.9 if j == 0 else 0.6), tn, g)
            if j == 0:
                add(m, koto(ESC[idx] - 12, 2.8, 0.3) * 0.5, tn, g)
        t += len(fr) * NEG / 2 / densidad + NEG
        fi += 1


tocar(0.0, T[3][0], 0.8, 0.8)
tocar(T[3][0], T[8][0], 1.0, 1.0, 1)
tocar(T[9][0], T[11][0], 1.0, 0.8, 3)
tocar(T[12][0] + 0.3, T[15][0], 0.6, 0.6, 2)
for j, idx in enumerate([8, 7, 5, 4, 2, 0]):            # cierre: baja y resuelve en Re
    add(m, koto(ESC[idx], 3.0, 0.4) * 0.7, T[15][0] + 0.2 + j * NEG * 0.7)
add(m, koto(50, 4.0, 0.3), tw("flor", 47) + 0.05, 0.9)
add(m, koto(38, 4.0, 0.3), tw("flor", 47) + 0.05, 0.7)
m = filt(m, 60, 9000)
dron = np.zeros(N)
add(dron, bordon(T[11][0] + 1.0), 0.0, 1.0)
add(dron, bordon(T[15][0] - T[11][0] + 0.5, (38, 45, 50)), T[11][0], 0.9)
add(dron, bordon(DUR - T[15][0], (38, 45, 50, 57)), T[15][0] - 0.3, 1.1)
m = m / (np.abs(m).max() + 1e-9) + dron / (np.abs(dron).max() + 1e-9) * 0.45
envv = np.convolve(np.abs(v), np.ones(int(0.08 * SR)) / int(0.08 * SR), mode="same")
m *= 1.0 - 0.45 * np.clip(envv / 0.15, 0, 1)
vr = np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2)); mr = np.sqrt(np.mean(m[np.abs(m) > 1e-4] ** 2) + 1e-12)
m *= (vr / 10 ** (14.0 / 20)) / mr

# ---------------------------------------------------------------- efectos
fx = np.zeros(N)
add(fx, motor_lejos(T[2][0] + 1.5, 0.5), 0.0)
add(fx, viento(T[3][0] + 0.5, 0.7), 0.0)
add(fx, viento(T[11][0] - T[8][0], 0.4), T[8][0])
add(fx, campana(0.9), tw("Flor", 23.5) - 0.02)
add(fx, taiko(1.0), tw("dioses") - 0.03)
for i in range(5):
    add(fx, gota(0.8), T[11][0] + 0.5 + i * 0.55)
add(fx, taiko(0.6), T[12][0])
add(fx, fuego(T[15][0] - T[13][0], 0.9), T[13][0])
add(fx, campana(0.8), tw("flor", 47) + 0.05)
add(fx, viento(DUR - T[15][0], 0.5), T[15][0])

mix = v + m * 0.55 + fx * 0.5
mix = np.tanh(mix * 1.1) / 1.1
mix = mix / (np.abs(mix).max() + 1e-9) * 0.9
os.makedirs(OUT, exist_ok=True)
tmp = os.path.join(OUT, "pre.wav")
wavfile.write(tmp, SR, (mix * 32767).astype(np.int16))
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "alimiter=limit=0.6:level=false,loudnorm=I=-14:TP=-2.0:LRA=11",
                "-ar", "48000", os.path.join(OUT, "mix.wav")], check=True)
print("ok audio", os.path.join(OUT, "mix.wav"))
