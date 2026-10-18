"""Audio del Ep. 1: voz + música sintetizada con ducking + efectos por evento -> out/ep01_mix.wav (-14 LUFS, TP <= -1 dBTP)."""
import json, os, subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUT", os.path.join(HERE, "out"))  # en el repo se usa OUT fuera del árbol
REPO = os.environ.get("REPO", os.path.abspath(os.path.join(HERE, "../../../..")))
EPI = os.path.abspath(os.path.join(HERE, ".."))
SR = 48000
meta = json.load(open(os.path.join(OUT, "ep01_planos.json")))
FR = {int(k): tuple(v) for k, v in meta["FR"].items()}
words = json.load(open(os.path.join(EPI, "words.json")))
DUR = (meta["END"] - 1) / 30
N = int(DUR * SR)
rng = np.random.default_rng(11)


def T(k, off=0.0):
    return (FR[k][0] - 1) / 30 + off


def W(prefix, after=0.0):
    for w in words:
        if w["s"] >= after and w["w"].lower().strip("¡!¿?.,:").startswith(prefix):
            return w["s"]
    raise KeyError(prefix)


def voice():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(REPO, "out/tts/ep01-congelamiento-cerebral.mp3"), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    v = np.frombuffer(raw, np.float32).copy()
    v = np.pad(v, (0, max(0, N - len(v))))[:N]
    return v / (np.abs(v).max() + 1e-9) * 0.9


def filt(x, lo=None, hi=None, order=2):
    if lo and hi:
        return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)
    if lo:
        return sosfilt(butter(order, lo, btype="high", fs=SR, output="sos"), x)
    return sosfilt(butter(order, hi, btype="low", fs=SR, output="sos"), x)


def env(n, a=0.004, d=0.1):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def tt(d):
    return np.arange(int(d * SR)) / SR


# ---------- efectos ----------
def chomp():
    t = tt(0.22)
    boop = np.sin(2 * np.pi * (260 * t - 330 * t * t)) * env(len(t), 0.003, 0.05)
    crunch = filt(rng.standard_normal(len(t)), 1500, 5500) * env(len(t), 0.002, 0.03)
    return 0.8 * boop + 0.6 * crunch


def pop():
    t = tt(0.12)
    return np.sin(2 * np.pi * (500 * t + 4000 * t * t)) * env(len(t), 0.002, 0.03)


def whoosh(d=0.35, up=True):
    n = int(d * SR)
    x = rng.standard_normal(n)
    out = np.zeros(n)
    seg = 1200
    for k in range(0, n, seg):
        c = 400 + 2600 * (k / n if up else 1 - k / n)
        out[k:k + seg] = filt(x[k:k + seg], c * 0.7, min(c * 1.6, 20000))
    return out * np.sin(np.pi * np.arange(n) / n) ** 2


def ice_crack():
    n = int(0.5 * SR)
    out = np.zeros(n)
    for k in range(9):
        i = int(rng.random() * 0.25 * SR)
        m = int(0.03 * SR)
        out[i:i + m] += filt(rng.standard_normal(m), 2500, 12000) * env(m, 0.0005, 0.006) * (1 - k / 10)
    t = tt(0.5)
    out += 0.5 * np.sin(2 * np.pi * 2200 * t) * env(n, 0.001, 0.08) * np.sin(2 * np.pi * 31 * t)
    return out


def zas():
    t = tt(0.3)
    sweep = np.sin(2 * np.pi * (1800 * t - 2500 * t * t)) * env(len(t), 0.002, 0.08)
    return 0.6 * whoosh(0.3, False) + 0.7 * sweep


def heartbeat():
    t = tt(0.5)
    def thump(d0):
        x = np.sin(2 * np.pi * 55 * t) * env(len(t), 0.004, 0.07)
        return np.roll(x, int(d0 * SR))
    return 1.1 * (thump(0) + 0.7 * thump(0.2))


def ding(f=1320, d=0.6):
    t = tt(d)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.01 * t)) * env(len(t), 0.002, 0.25)


def boing():
    t = tt(0.5)
    f = 180 + 120 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 5)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.003, 0.2)


def zap():
    t = tt(0.6)
    buzz = np.sign(np.sin(2 * np.pi * 120 * t)) * 0.3 + filt(rng.standard_normal(len(t)), 1000, 6000) * 0.5
    return buzz * env(len(t), 0.01, 0.25)


def tape_rewind(d):
    t = tt(d)
    f = 300 + 1600 * t / d
    whir = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + filt(rng.standard_normal(len(t)), 800, 5000) * 0.5
    return whir * np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.05)


def slurp():
    t = tt(0.45)
    f = 600 + 900 * t
    return filt(rng.standard_normal(len(t)), 500, 3000) * env(len(t), 0.02, 0.2) * (0.6 + 0.4 * np.sin(2 * np.pi * 18 * t))


def squeeze(up=False):
    t = tt(0.45)
    f = (900 - 600 * t / 0.45) if not up else (300 + 600 * t / 0.45)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.02, 0.3) * 0.6


def thud():
    t = tt(0.25)
    return (np.sin(2 * np.pi * (90 * t)) * env(len(t), 0.002, 0.06) + 0.3 * filt(rng.standard_normal(len(t)), 100, 900) * env(len(t), 0.001, 0.03))


def tick():
    t = tt(0.05)
    return filt(rng.standard_normal(len(t)), 2000, 8000) * env(len(t), 0.0005, 0.008)


def birds(d):
    out = np.zeros(int(d * SR))
    for k in range(int(d * 2)):
        i = int(rng.random() * (d - 0.3) * SR)
        t = tt(0.12)
        f = 3000 + 1500 * np.sin(2 * np.pi * 25 * t)
        out[i:i + len(t)] += np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.01, 0.05) * 0.25
    return out


def fizz():
    t = tt(0.8)
    return filt(rng.standard_normal(len(t)), 3000, 10000) * env(len(t), 0.05, 0.4) * 0.4


# ---------- música: marimba alegre a 112 BPM ----------
def music():
    bpm = 112
    beat = 60 / bpm
    out = np.zeros(N)
    prog = [(60, 64, 67), (57, 60, 64), (65, 69, 72), (67, 71, 74)]  # C Am F G
    mel = [72, 76, 79, 76, 74, 72, 74, 76, 77, 76, 74, 72, 71, 72, 74, 79]

    def note(m, d, g=0.25):
        f = 440 * 2 ** ((m - 69) / 12)
        t = tt(d)
        return g * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 30)) * env(len(t), 0.002, 0.18)

    nb = int(DUR / beat) + 1
    for b in range(nb):
        t0 = b * beat
        i = int(t0 * SR)
        ch = prog[(b // 4) % 4]
        bass = note(ch[0] - 24, beat * 0.9, 0.35)
        x = bass
        if b % 2 == 1:
            for m in ch:
                x = x[:len(x)] + 0
                y = note(m - 12, beat * 0.5, 0.10)
                j = i + int(beat * 0.5 * SR)
                if j + len(y) < N:
                    out[j:j + len(y)] += y
        if i + len(x) < N:
            out[i:i + len(x)] += x
        for h in (0, 0.5):
            mm = mel[(b * 2 + int(h * 2)) % len(mel)]
            y = note(mm, beat * 0.45, 0.13)
            j = i + int(h * beat * SR)
            if j + len(y) < N:
                out[j:j + len(y)] += y
        # shaker
        for q in range(4):
            j = i + int(q * beat / 4 * SR)
            y = filt(rng.standard_normal(int(0.04 * SR)), 5000, 12000) * env(int(0.04 * SR), 0.001, 0.01) * 0.05
            if j + len(y) < N:
                out[j:j + len(y)] += y
    return out


def add(buf, x, at, g=1.0):
    i = int(at * SR)
    j = min(N, i + len(x))
    if 0 <= i < N:
        buf[i:j] += g * x[: j - i]


v = voice()
m = music()
# la música se corta en el ¡zas! y vuelve en "Día de calor"; baja en el nombre científico
gate = np.ones(N)
t_all = np.arange(N) / SR
zas_t = W("zas")
gate[(t_all > zas_t - 0.02) & (t_all < T(7))] = 0.0
ramp = (t_all >= T(7)) & (t_all < T(7) + 0.3)
gate[ramp] = (t_all[ramp] - T(7)) / 0.3
gate[(t_all > T(23)) & (t_all < T(24))] *= 0.5
m *= gate
# ducking con la envolvente de la voz
envv = np.abs(v)
win = int(0.08 * SR)
envv = np.convolve(envv, np.ones(win) / win, mode="same")
duck = 1.0 - 0.6 * np.clip(envv / 0.15, 0, 1)
m *= duck
fx = np.zeros(N)
# eventos
add(fx, chomp(), 0.25, 0.8)
add(fx, ice_crack(), 1.2, 0.35)
add(fx, zas(), zas_t - 0.03, 1.0)
add(fx, ice_crack(), zas_t, 0.9)
for k in range(3):
    add(fx, heartbeat(), T(3, 0.1 + k * 0.42), 0.8)
add(fx, whoosh(0.4, True), T(4) - 0.15, 0.7)
add(fx, ding(2600, 0.3), T(4, 0.93), 0.35)   # copo que rebota
add(fx, pop(), T(5, 0.05), 0.6)
add(fx, tape_rewind(T(7) - T(6)), T(6), 0.8)
add(fx, birds(T(8) - T(7)), T(7), 0.6)
add(fx, ding(1320), T(8, 0.8), 0.45)
add(fx, pop(), T(8) + (FR[8][1] - FR[8][0] - 16) / 30, 0.8)
cyc = (FR[9][1] - FR[9][0]) / 2 / 30
for c in range(2):
    add(fx, chomp(), T(9) + c * cyc + cyc * 0.45, 0.9)
add(fx, whoosh(0.3, False), T(10) - 0.12, 0.6)
add(fx, fizz(), T(10, 1.6), 0.6)
add(fx, pop(), T(10, 0.2), 0.4)
add(fx, squeeze(False), T(11, 0.5), 0.6)
add(fx, pop(), T(11, 0.2), 0.4)
add(fx, heartbeat(), T(12, 0.2), 0.9)
add(fx, heartbeat(), T(12, 0.8), 0.7)
add(fx, zap(), T(13, 0.3), 0.6)
add(fx, pop(), T(13, 0.2), 0.4)
add(fx, whoosh(0.35, True), T(14) - 0.1, 0.5)
add(fx, zap(), T(15, 0.4), 0.4)
add(fx, boing(), W("confunde"), 0.6)
add(fx, heartbeat(), T(16, 0.1), 0.7)
add(fx, whoosh(0.35, True), T(17) - 0.1, 0.5)
add(fx, pop(), T(17, 0.2), 0.4)
add(fx, slurp(), T(18, 0.6), 0.7)
add(fx, pop(), T(18, 0.2), 0.4)
add(fx, squeeze(True), T(19, 0.6), 0.6)
add(fx, squeeze(False), T(20, 0.3), 0.6)
add(fx, ding(990, 0.5), T(20, 1.2), 0.4)
add(fx, thud(), T(21, 0.05), 0.9)
add(fx, pop(), T(21, 0.2), 0.4)
add(fx, whoosh(0.4, True), T(22) - 0.1, 0.4)
# letras que caen: un golpe por letra
t_g, t_e = W("gangli"), W("esfeno")
for k in range(16):
    add(fx, thud(), t_g + (k * 1.2 + 6) / 30, 0.35)
for k in range(14):
    add(fx, thud(), t_e + (k * 1.2 + 6) / 30, 0.35)
add(fx, pop(), T(25, 0.2), 0.4)
add(fx, fizz(), T(25, 0.9), 0.5)
add(fx, slurp(), T(26, 0.5), 0.6)
for k in range(8):
    add(fx, tick(), T(27, 0.3 + k * 0.45), 0.5)
add(fx, ding(1760), T(27, 2.4), 0.4)
add(fx, pop(), T(27, 0.2), 0.4)
add(fx, chomp(), T(30, 0.3), 0.9)

mix = v * 1.0 + m * 0.16 + fx * 0.45
mix = np.tanh(mix * 1.1) / 1.1
mix = mix / (np.abs(mix).max() + 1e-9) * 0.9
tmp = os.path.join(OUT, "ep01_pre.wav")
wavfile.write(tmp, SR, (mix * 32767).astype(np.int16))
dst = os.path.join(OUT, "ep01_mix.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", dst], check=True)
# diferencia voz/música (dB) para el QA
vr = np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2))
mr = np.sqrt(np.mean((m * 0.16)[(m != 0)] ** 2) + 1e-12)
print("ok audio", dst, "voz/música dB:", round(20 * np.log10(vr / mr), 1))
