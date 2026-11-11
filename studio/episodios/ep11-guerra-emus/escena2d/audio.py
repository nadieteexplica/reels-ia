"""Audio del Ep. 11: voz (voz.wav, ya recortada por prep.py) + música de comedia sintetizada (bajo tuba "um-pa" + marimba, Do mayor,
132 bpm) con ducking + un efecto por evento visual → <salida>/mix.wav a −14 LUFS."""
import os, subprocess, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else AQUI
sys.argv = sys.argv[:1]
sys.path.insert(0, AQUI)
import video as V

SR = 48000
DUR = V.DUR
N = int(DUR * SR)
rng = np.random.default_rng(7)


def filt(x, lo=None, hi=None, o=2):
    if lo and hi:
        return sosfilt(butter(o, [lo, hi], btype="band", fs=SR, output="sos"), x)
    if lo:
        return sosfilt(butter(o, lo, btype="high", fs=SR, output="sos"), x)
    return sosfilt(butter(o, hi, btype="low", fs=SR, output="sos"), x)


def tt(d):
    return np.arange(int(d * SR)) / SR


def add(buf, x, at, g=1.0):
    i = int(at * SR)
    if i < 0:
        x = x[-i:]; i = 0
    j = min(len(buf), i + len(x))
    if i < len(buf):
        buf[i:j] += g * x[: j - i]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def marimba(m, d=0.5):
    t = tt(d); f = hz(m)
    return (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.16) + 0.35 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t / 0.04)) * np.minimum(1, t / 0.002)


def tuba(m, d=0.3):
    t = tt(d); f = hz(m)
    x = sum(np.sin(2 * np.pi * f * k * t) / k ** 1.3 for k in range(1, 7))
    return filt(x, None, 900) * np.minimum(1, t / 0.015) * np.minimum(1, (d - t) / 0.05) * 0.5


def chas(d=0.08, g=1.0):
    n = int(d * SR)
    return filt(rng.standard_normal(n), 4000, 11000) * np.exp(-np.arange(n) / SR / 0.02) * g


def pop_(f0=500, f1=1100, d=0.09):
    t = tt(d)
    return np.sin(2 * np.pi * np.cumsum(np.linspace(f0, f1, len(t))) / SR) * np.exp(-t / 0.03)


def boing(d=0.5):
    t = tt(d)
    f = 180 + 260 * np.exp(-t / 0.08) + 40 * np.sin(2 * np.pi * 11 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.18)


def golpe(d=0.35, f=70):
    t = tt(d)
    x = np.sin(2 * np.pi * np.cumsum(np.linspace(f * 2.2, f * 0.7, len(t))) / SR) * np.exp(-t / 0.09)
    n = int(0.05 * SR)
    x[:n] += filt(rng.standard_normal(n), 200, 3000) * np.exp(-np.arange(n) / SR / 0.012) * 0.8
    return x


def clac():
    n = int(0.12 * SR)
    x = filt(rng.standard_normal(n), 1500, 7000) * np.exp(-np.arange(n) / SR / 0.012)
    t = tt(0.12)
    return x + 0.6 * np.sin(2 * np.pi * 2300 * t) * np.exp(-t / 0.02)


def rafaga(d, cps=11):
    x = np.zeros(int(d * SR))
    for i in range(int(d * cps)):
        add(x, golpe(0.08, 160) * 0.7, i / cps); add(x, clac() * 0.25, i / cps)
    return x


def whoosh(d=0.45):
    n = int(d * SR); t = tt(d)
    x = rng.standard_normal(n)
    y = filt(x, 300, 2500) * np.sin(np.pi * t / d) ** 2
    return y * 0.5


def motor(d):
    t = tt(d)
    f = 52 + 10 * np.sin(2 * np.pi * 0.9 * t)
    x = np.tanh(sum(np.sin(2 * np.pi * np.cumsum(f) / SR * k) / k for k in range(1, 9)) * 1.3)
    return filt(x, 50, 1200) * (0.7 + 0.3 * np.sign(np.sin(2 * np.pi * 26 * t))) * np.minimum(1, t / 0.2) * np.minimum(1, (d - t) / 0.25) * 0.35


def galope(d, pps=9):
    x = np.zeros(int(d * SR))
    for i in range(int(d * pps)):
        add(x, golpe(0.07, 120) * (0.5 + 0.2 * (i % 2)), i / pps)
    return x * 0.6


def ding(m=84, d=1.2):
    t = tt(d); f = hz(m)
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 2.01 * f * t) + 0.25 * np.sin(2 * np.pi * 3.02 * f * t)) * np.exp(-t / 0.35) * 0.4


def graznido(d=0.3):
    t = tt(d)
    f = 520 - 200 * t / d + 60 * np.sin(2 * np.pi * 30 * t)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.4 + np.sin(2 * np.pi * np.cumsum(f * 2) / SR) * 0.3
    return filt(x, 300, 3500) * np.sin(np.pi * t / d) * 0.6


def trombon_triste():
    x = np.zeros(int(1.9 * SR))
    for i, m in enumerate((58, 57, 56, 55)):
        d = 0.36 if i < 3 else 0.8
        t = tt(d); f = hz(m) * (1 - 0.02 * t / d * (i == 3)) * (1 + 0.012 * np.sin(2 * np.pi * 6 * t) * (i == 3))
        n = sum(np.sin(2 * np.pi * np.cumsum(f) / SR * k) / k for k in range(1, 9))
        add(x, filt(n, 150, 2200) * np.minimum(1, t / 0.03) * np.minimum(1, (d - t) / 0.08) * 0.4, i * 0.38)
    return x


def ovacion(d=1.6):
    n = int(d * SR); t = tt(d)
    return filt(rng.standard_normal(n), 500, 5000) * np.minimum(1, t / 0.25) * np.minimum(1, (d - t) / 0.5) * 0.25


# ---------------------------------------------------------------- voz
sr, v = wavfile.read(os.path.join(AQUI, "voz.wav"))
v = v.astype(np.float64) / 32768
v = np.pad(v, (0, max(0, N - len(v))))[:N]

# ---------------------------------------------------------------- música (um-pa + marimba)
BPM = 132
NEG = 60 / BPM
ACORDES = [(48, (60, 64, 67)), (45, (57, 60, 64)), (41, (53, 57, 60)), (43, (55, 59, 62))]    # Do · La m · Fa · Sol
MEL = [[12, 16, 19, 16, 21, 19, 16, 12], [12, 16, 19, 24, 19, 16, 14, 12], [17, 21, 24, 21, 17, 21, 24, 28], [19, 23, 26, 23, 19, 17, 14, 11]]
m = np.zeros(N)
silencios = [(V.T_FACIL - 0.1, V.T_PERO), (V.T_TRABO, V.T_SUB - 0.05), (V.T_IMAG - 0.1, V.T_POCO), (V.T_UNA + 0.25, V.T_MARC)]
comp = 0
t = 0.0
while t < DUR - 0.3:
    bajo, ac = ACORDES[comp % 4]
    for neg in range(4):
        tn = t + neg * NEG
        if any(a <= tn < b for a, b in silencios) or tn > DUR - 0.4:
            continue
        if neg % 2 == 0:
            add(m, tuba(bajo if neg == 0 else bajo + 7, NEG * 0.9), tn, 1.0)
        else:
            for n_ in ac:
                add(m, marimba(n_, 0.25), tn, 0.22)
            add(m, chas(0.05, 0.12), tn)
        for sub in range(2):
            nota = MEL[comp % 4][neg * 2 + sub]
            if (comp // 4) % 2 == 1 or sub == 0:
                add(m, marimba(60 + nota, 0.45), tn + sub * NEG / 2, 0.5)
    t += 4 * NEG
    comp += 1
m = filt(m, 50, 9000)
envv = np.convolve(np.abs(v), np.ones(int(0.1 * SR)) / int(0.1 * SR), mode="same")
m *= 1.0 - 0.5 * np.clip(envv / 0.12, 0, 1)
vr = np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2)); mr = np.sqrt(np.mean(m[np.abs(m) > 1e-4] ** 2) + 1e-12)
m *= (vr / 10 ** (15.0 / 20)) / mr

# ---------------------------------------------------------------- efectos (uno por evento)
fx = np.zeros(N)
T = V.T
add(fx, ding(84), 0.02, 0.7); add(fx, graznido(), 0.55, 0.5)
add(fx, whoosh(0.3), T[2][0] - 0.1, 0.6); add(fx, pop_(), T[2][0] + 0.1, 0.5)
add(fx, pop_(600, 1300), V.T_ES + 0.25, 0.6); add(fx, pop_(), V.tw("enorme"), 0.5)
add(fx, boing(), V.T_NOV, 0.8); add(fx, golpe(0.3, 60), V.T_NOV + 0.75, 0.9)
add(fx, whoosh(0.3), T[4][0] - 0.1, 0.5)
for i in range(8):
    add(fx, chas(0.06, 0.5), T[4][0] + 0.3 + i * 0.33)
add(fx, pop_(500, 1400, 0.12), V.tw("veinte") - 0.1, 0.6); add(fx, graznido(), V.tw("trigo"), 0.4)
for i in range(3):
    add(fx, golpe(0.2, 90), T[5][0] + 0.2 + i * 0.32, 0.6); add(fx, pop_(700 + i * 150, 1200 + i * 150), V.T_TRES - 0.05 + i * 0.12, 0.5)
for i in range(2):
    add(fx, clac(), V.T_AMET + i * 0.15 + 0.25, 0.7)
add(fx, pop_(), V.T_AMET + 0.55, 0.5)
add(fx, ding(79, 0.8), V.T_FACIL - 0.05, 0.6)
add(fx, whoosh(0.5), V.T_PERO - 0.1, 0.8); add(fx, galope(T[7][1] - T[7][0] - 0.1), T[7][0] + 0.1, 0.55); add(fx, pop_(600, 1500, 0.15), V.T_CINC, 0.6)
add(fx, pop_(), V.tw("emboscada") - 0.05, 0.4)
ta = V.tw("y", 16.3)
add(fx, rafaga(max(0.2, V.T_TRABO - 0.3 - ta)), ta, 0.6)
add(fx, clac(), V.T_TRABO, 1.0); add(fx, boing(0.35), V.T_TRABO + 0.05, 0.5); add(fx, galope(0.6, 12), V.T_TRABO + 0.15, 0.5); add(fx, graznido(), V.T_TRABO + 0.2, 0.5)
add(fx, motor(T[9][1] - T[9][0]), T[9][0], 0.7); add(fx, pop_(), T[9][0] + 0.15, 0.5)
add(fx, motor(T[10][1] - T[10][0]), T[10][0], 0.8); add(fx, galope(T[10][1] - T[10][0], 11), T[10][0], 0.4)
add(fx, rafaga(1.0, 9), T[10][0] + 0.2, 0.35); add(fx, graznido(0.4), V.T_RAP - 0.3, 0.6); add(fx, pop_(), V.T_RAP - 0.1, 0.5)
add(fx, whoosh(0.3), T[11][0] - 0.1, 0.5); add(fx, pop_(), V.T_VIGIA - 0.05, 0.5)
add(fx, graznido(0.25), V.T_AVISA, 0.9); add(fx, graznido(0.25), V.T_AVISA + 0.3, 0.9); add(fx, galope(0.7, 12), V.T_AVISA + 0.2, 0.5)
add(fx, pop_(400, 900, 0.12), T[12][0] + 0.1, 0.6)
for i in range(6):
    add(fx, ding(96 + (i % 3) * 2, 0.25), V.T_BALAS + i * 0.22, 0.35)
add(fx, golpe(0.3, 55), V.T_TANQ - 0.1, 0.8)
add(fx, whoosh(0.3), T[13][0] - 0.1, 0.5); add(fx, pop_(), V.tw("explicarle") - 0.05, 0.5); add(fx, golpe(0.4, 50), V.T_JEFE, 1.0)
add(fx, trombon_triste(), T[14][0] + 0.05, 0.7)
for i in range(6):
    add(fx, chas(0.05, 0.4), T[14][0] + i * 0.15)
add(fx, pop_(), V.T_POCO + 0.45, 0.4); add(fx, pop_(650, 1300), V.T_POCO + 0.7, 0.4)
for i in range(5):
    add(fx, chas(0.07, 0.6), T[15][0] + 0.1 + i * 0.3); add(fx, pop_(300, 500, 0.06), T[15][0] + 0.2 + i * 0.3, 0.4)
add(fx, pop_(400, 1000, 0.15), T[16][0] + 0.1, 0.6); add(fx, galope(V.T_UNA - T[16][0], 8), T[16][0], 0.35)
add(fx, whoosh(0.3), V.T_UNA, 0.7); add(fx, golpe(0.45, 55), V.T_UNA + 0.3, 1.1); add(fx, boing(0.6), V.T_UNA + 0.32, 0.7)
add(fx, whoosh(0.3), T[17][0] - 0.05, 0.5); add(fx, golpe(0.3, 70), V.T_CERO, 0.8); add(fx, ding(72, 0.5), V.T_CERO, 0.3)
add(fx, ding(84, 1.4), V.T_UNO, 0.9); add(fx, ding(88, 1.4), V.T_UNO + 0.12, 0.7); add(fx, ding(91, 1.4), V.T_UNO + 0.24, 0.7); add(fx, ovacion(DUR - V.T_UNO - 0.05), V.T_UNO + 0.05, 0.8)

fr = np.sqrt(np.mean(fx[np.abs(fx) > 1e-3] ** 2))
fx *= (vr / 10 ** (9.0 / 20)) / fr
mix = v * (0.25 / vr) + (m + fx) * (0.25 / vr)
mix = np.tanh(mix * 1.2) / 1.2
mix[-int(0.15 * SR):] *= np.linspace(1, 0, int(0.15 * SR))
os.makedirs(OUT, exist_ok=True)
tmp = os.path.join(OUT, "pre.wav")
wavfile.write(tmp, SR, (mix / (np.abs(mix).max() + 1e-9) * 0.9 * 32767).astype(np.int16))
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "alimiter=limit=0.7:level=false,loudnorm=I=-14:TP=-1.5:LRA=11",
                "-ar", "48000", os.path.join(OUT, "mix.wav")], check=True)
print("ok audio", os.path.join(OUT, "mix.wav"))
