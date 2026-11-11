"""Audio del Ep. 12: voz (voz.wav, ya recortada por prep.py) + música de comedia sintetizada (marcha de juguete: tuba, marimba y redoble, Fa mayor,
116 bpm) con ducking + un efecto por evento visual → <salida>/mix.wav a −14 LUFS."""
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

# ---------------------------------------------------------------- música (marcha de juguete)
def redoble(g=1.0):
    n = int(0.07 * SR)
    return filt(rng.standard_normal(n), 1200, 8000) * np.exp(-np.arange(n) / SR / 0.018) * g


BPM = 116
NEG = 60 / BPM
ACORDES = [(41, (60, 65, 69)), (38, (62, 65, 69)), (46, (58, 62, 65)), (48, (60, 64, 67))]    # Fa · Re m · Si b · Do
MEL = [[17, 17, 21, 24, 21, 17, 12, 17], [14, 17, 21, 17, 14, 12, 9, 14], [22, 22, 26, 29, 26, 22, 17, 22], [24, 28, 31, 28, 24, 22, 19, 16]]
m = np.zeros(N)
silencios = [(V.T_YEL - 0.1, V.T_LO - 0.05), (V.T_NO - 0.1, V.T_CARG - 0.05), (V.T_IMAG - 0.05, V.T[17][0]), (V.T_SE - 0.1, V.T_NOMBRE)]
comp = 0
t = 0.0
while t < DUR - 0.3:
    bajo, ac = ACORDES[comp % 4]
    for neg in range(4):
        tn = t + neg * NEG
        if any(a <= tn < b for a, b in silencios) or tn > DUR - 0.4:
            continue
        add(m, tuba(bajo if neg % 2 == 0 else bajo + 7, NEG * 0.8), tn, 0.9)
        add(m, redoble(0.22 if neg % 2 else 0.12), tn)
        add(m, redoble(0.1), tn + NEG * 0.5); add(m, redoble(0.08), tn + NEG * 0.75)
        if neg % 2 == 1:
            for n_ in ac:
                add(m, marimba(n_, 0.22), tn, 0.18)
        for sub in range(2):
            nota = MEL[comp % 4][neg * 2 + sub]
            if (comp // 2) % 2 == 1 or sub == 0:
                add(m, marimba(60 + nota, 0.4), tn + sub * NEG / 2, 0.45)
    t += 4 * NEG
    comp += 1
m = filt(m, 50, 9000)
envv = np.convolve(np.abs(v), np.ones(int(0.1 * SR)) / int(0.1 * SR), mode="same")
m *= 1.0 - 0.5 * np.clip(envv / 0.12, 0, 1)
vr = np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2)); mr = np.sqrt(np.mean(m[np.abs(m) > 1e-4] ** 2) + 1e-12)
m *= (vr / 10 ** (15.0 / 20)) / mr


def gruñido(d=0.5, f0=95):
    t = tt(d)
    f = f0 * (1 + 0.25 * np.sin(np.pi * t / d)) + 6 * np.sin(2 * np.pi * 27 * t)
    x = np.tanh(sum(np.sin(2 * np.pi * np.cumsum(f) / SR * k) / k for k in range(1, 10)) * 1.5)
    return filt(x, 80, 1400) * np.sin(np.pi * t / d) ** 0.7 * 0.6


def sirena(d=1.0):
    t = tt(d)
    x = sum(np.sin(2 * np.pi * f * t) for f in (174, 233)) * 0.5
    return filt(np.tanh(x * 2), 100, 1500) * np.minimum(1, t / 0.08) * np.minimum(1, (d - t) / 0.3) * 0.4


def fanfarria(notas=(65, 69, 72, 77), paso=0.12, largo=0.5):
    x = np.zeros(int((paso * len(notas) + largo + 0.2) * SR))
    for i, n_ in enumerate(notas):
        d = largo if i == len(notas) - 1 else paso * 1.1
        t = tt(d); f = hz(n_)
        y = sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 8))
        add(x, filt(y, 200, 4000) * np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.06) * 0.3, i * paso)
    return x


# ---------------------------------------------------------------- efectos (uno por evento)
fx = np.zeros(N)
T = V.T
add(fx, fanfarria((65, 69, 72), 0.1, 0.35), 0.0, 0.6); add(fx, gruñido(0.4), 0.45, 0.5)
add(fx, whoosh(0.3), T[2][0] - 0.1, 0.6)
for tt_ in (V.T_RANGO, V.T_NUM, V.T_LIB):
    add(fx, pop_(700, 1500, 0.1), tt_ - 0.05, 0.6)
add(fx, whoosh(0.3), T[3][0] - 0.1, 0.5); add(fx, pop_(), T[3][0] + 0.05, 0.5); add(fx, gruñido(0.35, 260), T[3][0] + 0.5, 0.35)
for i in range(4):
    add(fx, golpe(0.1, 110), T[4][0] + 0.05 + i * 0.14, 0.4)
add(fx, ding(84, 0.8), V.T_ADOP, 0.6); add(fx, ding(88, 0.8), V.T_ADOP + 0.1, 0.5); add(fx, gruñido(0.3, 280), V.T_ADOP + 0.3, 0.35)
add(fx, whoosh(0.3), T[5][0] - 0.1, 0.6); add(fx, boing(0.4), T[5][0] + 0.1, 0.7); add(fx, gruñido(0.5), T[5][0] + 0.5, 0.5)
add(fx, pop_(), T[5][0] + 0.05, 0.4)
add(fx, clac(), T[6][0] + 0.3, 0.5); add(fx, ding(91, 0.5), T[6][0] + 0.32, 0.5); add(fx, gruñido(0.35, 120), V.T_CERV, 0.4)
add(fx, whoosh(0.3), T[7][0] - 0.1, 0.5); add(fx, sirena(0.9), T[7][0] + 0.15, 0.6)
for i in range(10):
    add(fx, golpe(0.07, 130), T[7][0] + 0.2 + i * 0.2, 0.35)
add(fx, pop_(), V.tw("mandaron") - 0.05, 0.5)
add(fx, trombon_triste()[: int(0.9 * SR)], T[8][0], 0.7); add(fx, pop_(400, 1000, 0.15), T[8][0] + 0.05, 0.6)
add(fx, whoosh(0.25), T[9][0] - 0.05, 0.5); add(fx, golpe(0.4, 60), V.tw("enlistaron") + 0.1, 1.1); add(fx, clac(), V.tw("enlistaron") + 0.1, 0.7)
add(fx, ding(84, 0.6), V.tw("enlistaron") + 0.3, 0.5)
add(fx, sirena(0.9), T[10][0] + 0.05, 0.6); add(fx, pop_(), T[10][0] + 0.05, 0.5); add(fx, gruñido(0.4, 130), T[10][0] + 0.5, 0.4)
add(fx, fanfarria((65, 69, 72, 77), 0.09, 0.4), T[11][0], 0.6); add(fx, golpe(0.3, 70), V.T_RASO_S, 0.7)
add(fx, whoosh(0.3), T[12][0] - 0.1, 0.5); add(fx, pop_(), T[12][0] + 0.05, 0.5); add(fx, pop_(650, 1300), V.T_ANTES, 0.4)
for i in range(4):
    add(fx, golpe(0.5, 45), T[12][0] + 0.4 + i * 0.75, 0.45)       # cañonazos lejanos
add(fx, gruñido(0.45), V.T_SEPUSO, 0.6); add(fx, pop_(), V.T_SEPUSO, 0.5)
add(fx, golpe(0.3, 80), T[13][0] + 0.08, 0.8); add(fx, clac(), T[13][0] + 0.08, 0.5)
add(fx, whoosh(0.3), T[14][0] - 0.05, 0.5)
for i in range(4):
    add(fx, golpe(0.18, 55), T[14][0] + 0.15 + i * 0.36, 0.8)      # pasos pesados
add(fx, pop_(), V.tw("municiones") - 0.05, 0.5)
add(fx, pop_(500, 900, 0.1), T[15][0] + 0.05, 0.4)
for i in range(5):
    add(fx, golpe(0.18, 55), T[15][0] + 0.3 + i * 0.58, 0.6)
add(fx, golpe(0.35, 60), V.T_CUAR - 0.05, 0.9); add(fx, pop_(600, 1500, 0.14), V.T_CUAR - 0.05, 0.6); add(fx, pop_(), V.T_DOS - 0.05, 0.5)
add(fx, ding(79, 0.8), T[16][0], 0.6)
add(fx, whoosh(0.3), T[17][0] - 0.1, 0.5); add(fx, pop_(), T[17][0] + 0.05, 0.4)
for i in range(3):
    add(fx, golpe(0.2, 55), V.T_COMP - 0.25 + i * 0.15, 0.7)
add(fx, boing(0.4), V.T_OSO2 - 0.1, 0.7); add(fx, gruñido(0.4, 130), V.T_OSO2 + 0.1, 0.5)
add(fx, whoosh(0.3), T[18][0] - 0.1, 0.5); add(fx, fanfarria((65, 69, 72, 77, 81), 0.08, 0.45), V.T_CABO - 0.3, 0.7); add(fx, ding(96, 0.6), V.T_CABO - 0.25, 0.5)
add(fx, whoosh(0.3), T[19][0] - 0.1, 0.5); add(fx, pop_(), T[19][0] + 0.05, 0.4); add(fx, whoosh(0.35), V.T_INSIG - 0.05, 0.8)
add(fx, ding(84, 1.2), V.T_INSIG + 0.1, 0.7); add(fx, ding(91, 1.0), V.T_INSIG + 0.22, 0.5); add(fx, pop_(), V.T_INSIG + 0.2, 0.4)
add(fx, whoosh(0.3), T[20][0] - 0.1, 0.5)
for i in range(6):
    add(fx, ding(100 + (i * 5) % 9, 0.2), T[20][0] + 0.3 + i * 0.37, 0.18)   # pajaritos
add(fx, pop_(), V.T_RETIRO, 0.5); add(fx, pop_(650, 1300), V.T_ZOO + 0.3, 0.4); add(fx, gruñido(0.4, 130), V.T_ZOO + 0.5, 0.35)
add(fx, whoosh(0.3), T[21][0] - 0.05, 0.5)
add(fx, fanfarria((65, 69, 72, 77), 0.1, 0.9), V.T_NOMBRE - 0.08, 0.8); add(fx, golpe(0.3, 70), V.T_NOMBRE - 0.08, 0.8); add(fx, ovacion(DUR - V.T_NOMBRE - 0.05), V.T_NOMBRE + 0.05, 0.8)

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
