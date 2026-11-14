"""Audio del Ep. 15: música sintetizada (electrónica de juguete con marimba) + un efecto por evento + voz. Sale mix.wav a −14 LUFS."""
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

# ---------------------------------------------------------------- música (electrónica de juguete)
def bombo(g=1.0):
    t = tt(0.22)
    return np.sin(2 * np.pi * np.cumsum(np.linspace(120, 46, len(t))) / SR) * np.exp(-t / 0.07) * g


def bajo_s(m_, d):
    t = tt(d); f = hz(m_)
    x = np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + np.sin(2 * np.pi * f * t)
    return filt(x, None, 500) * np.minimum(1, t / 0.01) * np.exp(-t / (d * 0.6)) * 0.5



BPM = 108
NEG = 60 / BPM
ACORDES = [(48, (60, 64, 67, 72)), (45, (57, 60, 64, 69)), (41, (53, 57, 60, 65)), (43, (55, 59, 62, 67))]    # Do · La m · Fa · Sol
m = np.zeros(N)
silencios = [(V.T[1][0], V.T_NO - 0.05), (V.T_NO2 - 0.1, V.T_PERO3), (V.T_NOBASTA - 0.5, V.T_NOBASTA)]
comp = 0
t = 0.0
while t < DUR - 0.3:
    bajo, ac = ACORDES[comp % 4]
    for neg in range(4):
        tn = t + neg * NEG
        if any(a <= tn < b for a, b in silencios) or tn > DUR - 0.4:
            continue
        if neg in (0, 2):
            add(m, bombo(0.6), tn); add(m, bajo_s(bajo, NEG * 0.8), tn, 0.8)
        else:
            add(m, chas(0.05, 0.2), tn); add(m, bajo_s(bajo + 7, NEG * 0.4), tn + NEG / 2, 0.45)
        for nn in ac[:3]:
            add(m, marimba(nn + 12, 0.25), tn + NEG / 2, 0.14)                   # contratiempo
        mel = (ac[0], ac[2], ac[1], ac[3], ac[2], ac[1], ac[2], ac[0])
        if comp % 2 == 0 or neg < 2:
            add(m, marimba(mel[(neg * 2) % 8] + 24, 0.3), tn, 0.26); add(m, marimba(mel[(neg * 2 + 1) % 8] + 24, 0.2), tn + NEG * 0.75, 0.18)
    t += 4 * NEG
    comp += 1
m = filt(m, 45, 9000)
envv = np.convolve(np.abs(v), np.ones(int(0.1 * SR)) / int(0.1 * SR), mode="same")
m *= 1.0 - 0.5 * np.clip(envv / 0.12, 0, 1)
vr = np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2)); mr = np.sqrt(np.mean(m[np.abs(m) > 1e-4] ** 2) + 1e-12)
m *= (vr / 10 ** (15.0 / 20)) / mr


def zap(d=0.16, f0=1800, f1=500):
    t = tt(d)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(np.linspace(f0, f1, len(t))) / SR)) * 0.5
    return filt(x, 400, 6000) * np.exp(-t / (d * 0.5)) * 0.6


def blip(m_=84, d=0.09):
    t = tt(d)
    return np.sin(2 * np.pi * hz(m_) * t) * np.exp(-t / 0.03) * 0.7


def gotazo():
    t = tt(0.25)
    return np.sin(2 * np.pi * np.cumsum(500 + 900 * np.exp(-t / 0.03)) / SR) * np.exp(-t / 0.06) * 0.8


def roncar(d=0.7):
    t = tt(d)
    x = filt(rng.standard_normal(len(t)), 80, 500) * (0.5 + 0.5 * np.sin(2 * np.pi * 28 * t))
    return x * np.sin(np.pi * t / d) ** 2 * 0.6


def viento(d):
    t = tt(d)
    x = filt(rng.standard_normal(len(t)), 300, 1400) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.4 * t))
    return x * np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.5) * 0.25



def zumbido(d, f=110):
    t = tt(d)
    x = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2 * t) + 0.2 * np.sin(2 * np.pi * f * 3.01 * t)
    return x * (0.7 + 0.3 * np.sin(2 * np.pi * 5 * t)) * np.minimum(1, t / 0.25) * np.minimum(1, (d - t) / 0.25) * 0.3


def bip(d=0.22, m_=93):
    t = tt(d)
    return (np.sin(2 * np.pi * hz(m_) * t) + 0.3 * np.sin(2 * np.pi * hz(m_) * 2 * t)) * np.minimum(1, t / 0.005) * np.minimum(1, (d - t) / 0.02) * 0.6


def sube(d, f0=200, f1=1200):
    t = tt(d)
    return np.sin(2 * np.pi * np.cumsum(np.linspace(f0, f1, len(t))) / SR) * np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.05) * 0.4


# ---------------------------------------------------------------- efectos (uno por evento)
def grillo(d=0.9):
    x = np.zeros(int(d * SR))
    for k in range(3):
        for j in range(4):
            t0 = k * 0.3 + j * 0.035
            tt_ = tt(0.025)
            add(x, np.sin(2 * np.pi * 4400 * tt_) * np.sin(np.pi * tt_ / 0.025), t0)
    return x * 0.5


def brrr(d=1.0, cps=26):
    d = max(d, 0.06)
    """Dedos que hacen cosquillas: tableteo rápido y suave."""
    x = np.zeros(int(d * SR))
    for i in range(int(d * cps)):
        add(x, clac() * (0.25 + 0.15 * (i % 3 == 0)), i / cps)
    return filt(x, 900, 6000) * np.minimum(1, tt(d) / 0.05)[: len(x)] * 0.7


def risitas(d=1.2, f0=78):
    """'Ja ja ja' de juguete: marimbas que suben y bajan rápido."""
    x = np.zeros(int(d * SR))
    for i in range(int(d / 0.11)):
        add(x, marimba(f0 + (i % 4) * 2 + (3 if i % 2 else 0), 0.12), i * 0.11, 0.6)
    return x


fx = np.zeros(N)
T = V.T
# P1: se hace cosquillas: nada (grillos)
add(fx, brrr(T[1][1] - 0.1), 0.05, 0.45); add(fx, pop_(), V.T_NO - 0.05, 0.5); add(fx, grillo(0.9), V.T_NADA + 0.1, 0.5)
# P2: las manos de otro → risa
add(fx, whoosh(0.4), T[2][0] - 0.05, 0.5); add(fx, pop_(500, 1100), T[2][0] + 0.05, 0.4)
add(fx, whoosh(0.35), V.T_OTRO - 0.3, 0.6); add(fx, brrr(T[2][1] - V.T_OTRO), V.T_OTRO, 0.55)
add(fx, boing(0.5), V.T_RETUER - 0.05, 0.8); add(fx, risitas(T[2][1] - V.T_RETUER + 0.1), V.T_RETUER, 0.6)
# P3: los dos lo saben
add(fx, whoosh(0.3), T[3][0] - 0.08, 0.5); add(fx, pop_(), T[3][0] + 0.05, 0.4); add(fx, pop_(650, 1300), T[3][0] + 0.15, 0.4)
add(fx, ding(84, 0.6), V.T_DOS, 0.5); add(fx, ding(88, 0.6), V.T_DOS + 0.12, 0.45); add(fx, boing(0.4), V.T_SABES - 0.05, 0.6)
# P4–P5: la orden baja y se guarda la copia
add(fx, whoosh(0.3), T[4][0] - 0.08, 0.5); add(fx, pop_(), V.T_CEREBRO - 0.1, 0.4)
add(fx, sube(0.65, 1100, 300), V.T_ORDEN - 0.15, 0.5); add(fx, pop_(), V.T_ORDEN - 0.1, 0.5); add(fx, brrr(T[4][1] - V.T_ORDEN - 0.5), V.T_ORDEN + 0.5, 0.35)
add(fx, whoosh(0.25), T[5][0] - 0.05, 0.4); add(fx, pop_(700, 1400), T[5][0] + 0.05, 0.5); add(fx, golpe(0.3, 65), V.T_COPIA - 0.03, 0.8); add(fx, clac(), V.T_COPIA, 0.5)
# P6: calcula cuándo y dónde
add(fx, whoosh(0.3), T[6][0] - 0.08, 0.5); add(fx, sube(0.3, 400, 1200), T[6][0] + 0.15, 0.4)
add(fx, pop_(), V.T_CUANDO - 0.08, 0.5); add(fx, ding(86, 0.5), V.T_CUANDO + 0.1, 0.4)
add(fx, pop_(650, 1300), V.T_DONDE - 0.08, 0.5); add(fx, ding(89, 0.5), V.T_DONDE + 0.1, 0.4); add(fx, pop_(), V.T_TOCAR - 0.1, 0.4)
# P7: baja el volumen
add(fx, whoosh(0.3), T[7][0] - 0.08, 0.5); add(fx, pop_(), T[7][0] + 0.05, 0.4); add(fx, sube(0.6, 1200, 200), V.T_BAJA, 0.7)
# P8: la mano de otro, sin copia
add(fx, whoosh(0.4), T[8][0] - 0.05, 0.6); add(fx, brrr(T[8][1] - T[8][0]), T[8][0] + 0.1, 0.45)
add(fx, trombon_triste()[: int(0.7 * SR)], V.T_NOHAY + 0.05, 0.5); add(fx, zap(0.18, 1500, 500), V.T_NOHAY, 0.5)
# P9: volumen al máximo
add(fx, sube(0.3, 300, 1500), T[9][0], 0.7); add(fx, boing(0.5), T[9][0] + 0.3, 0.7); add(fx, risitas(T[9][1] - T[9][0] - 0.3), T[9][0] + 0.3, 0.6)
# P10–P13: el robot
add(fx, whoosh(0.4), T[10][0] - 0.08, 0.5); add(fx, bip(0.12, 91), T[10][0] + 0.1, 0.6); add(fx, bip(0.12, 96), T[10][0] + 0.25, 0.5)
add(fx, motor(T[13][1] - V.T_MUEVES), V.T_MUEVES, 0.4); add(fx, pop_(), V.T_MUEVES - 0.05, 0.4)
add(fx, pop_(), T[11][0] + 0.05, 0.5); add(fx, grillo(0.6), T[11][0] + 0.25, 0.5)
add(fx, whoosh(0.3), T[12][0] - 0.06, 0.4); tk = V.T_ATRASA - 0.1
while tk < V.T_SITE - 0.1:
    add(fx, clac(), tk, 0.3); tk += 0.2                                       # el cronómetro
add(fx, ding(84, 0.6), V.T_ATRASA + 0.4, 0.4)
add(fx, boing(0.5), V.T_SITE - 0.05, 0.8); add(fx, risitas(T[13][1] - V.T_SITE), V.T_SITE, 0.6); add(fx, brrr(T[13][1] - V.T_SITE), V.T_SITE, 0.35)
add(fx, pop_(600, 1300), T[13][0] + 0.02, 0.5); add(fx, ding(88, 0.5), V.T_SEPAS, 0.4)
# P14: saberlo no basta → predecirlas (y vuelta al cuadro 0)
add(fx, whoosh(0.4), T[14][0] - 0.08, 0.5); add(fx, pop_(), T[14][0] + 0.05, 0.4); add(fx, zap(0.2, 2400, 600), V.T_TU2 - 0.05, 0.6)
add(fx, ding(84, 1.0), V.T_PREDIC - 0.1, 0.6); add(fx, ding(91, 1.0), V.T_PREDIC + 0.05, 0.5); add(fx, sube(0.5, 400, 1600), V.T_PREDIC - 0.1, 0.4)
add(fx, whoosh(0.3), T[15][0] - 0.05, 0.4); add(fx, brrr(T[15][1] - T[15][0]), T[15][0], 0.4)

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
