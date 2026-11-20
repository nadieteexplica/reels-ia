"""Audio del Ep. 16: música sintetizada de los 50–60 (progresión doo-wop Do–La m–Fa–Sol con vibráfono, bajo caminante y escobillas) + un efecto por evento + voz. Sale mix.wav a −14 LUFS."""
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



def vibra(m_, d=0.6):
    t = tt(d); f = hz(m_)
    x = (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t / 0.05)) * np.exp(-t / 0.45)
    return x * (0.8 + 0.2 * np.sin(2 * np.pi * 5.5 * t)) * np.minimum(1, t / 0.004)


def contrabajo(m_, d):
    t = tt(d); f = hz(m_)
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t)
    return filt(x, None, 700) * np.minimum(1, t / 0.008) * np.exp(-t / (d * 0.7)) * 0.6


def escobilla(d=0.18, g=1.0):
    n = int(d * SR)
    return filt(rng.standard_normal(n), 2500, 9000) * np.exp(-np.arange(n) / SR / 0.06) * g * 0.5


BPM = 112
NEG = 60 / BPM
ACORDES = [(48, (60, 64, 67)), (45, (57, 60, 64)), (41, (53, 57, 60)), (43, (55, 59, 62))]       # Do · La m · Fa · Sol (doo-wop)
CAMINA = {48: (48, 52, 55, 57), 45: (45, 48, 52, 50), 41: (41, 45, 48, 50), 43: (43, 47, 50, 47)}
m = np.zeros(N)
silencios = [(V.T_PERO - 0.05, V.T_SEGUIA + 0.25), (V.T_LE2 - 0.25, V.T_BANG2 + 0.2)]
comp = 0
t = 0.0
while t < DUR - 0.3:
    bajo, ac = ACORDES[comp % 4]
    for neg in range(4):
        tn = t + neg * NEG
        if any(a_ <= tn < b_ for a_, b_ in silencios) or tn > DUR - 0.4:
            continue
        add(m, contrabajo(CAMINA[bajo][neg], NEG * 0.95), tn, 0.9)
        add(m, escobilla(0.16, 0.6 if neg % 2 else 0.3), tn)
        if neg in (1, 3):
            add(m, escobilla(0.1, 0.3), tn + NEG * 0.66)
        if neg in (0, 2):
            for nn in ac:
                add(m, vibra(nn + 12, 0.7), tn + NEG * 0.5, 0.10)
        mel = (ac[2] + 12, ac[1] + 12, ac[0] + 12, ac[1] + 12)
        if comp % 2 == 1:
            add(m, vibra(mel[neg] + 12, 0.5), tn, 0.16)
    t += 4 * NEG
    comp += 1
m = filt(m, 40, 9000)
envv = np.convolve(np.abs(v), np.ones(int(0.1 * SR)) / int(0.1 * SR), mode="same")
m *= 1.0 - 0.5 * np.clip(envv / 0.12, 0, 1)
vr = np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2)); mr = np.sqrt(np.mean(m[np.abs(m) > 1e-4] ** 2) + 1e-12)
m *= (vr / 10 ** (20.0 / 20)) / mr


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
def estatica(d, g=1.0):
    n = int(d * SR); t_ = tt(d)
    x = filt(rng.standard_normal(n), 1200, 9000) * (0.8 + 0.2 * np.sin(2 * np.pi * 60 * t_))
    return x * np.minimum(1, t_ / 0.08) * np.minimum(1, (d - t_) / 0.12) * 0.3 * g


def arrullo(d=0.6):
    """Cucurrú de paloma: grave, con vibrato que sube y baja."""
    t_ = tt(d)
    f = 330 + 60 * np.sin(np.pi * t_ / d) + 18 * np.sin(2 * np.pi * 22 * t_)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(2 * np.pi * np.cumsum(f * 2) / SR)
    return filt(x, 200, 1500) * np.sin(np.pi * t_ / d) ** 2 * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 7 * t_))) * 0.5


def aleteo(d=0.8, fps=12):
    x = np.zeros(int(d * SR))
    for i in range(int(d * fps)):
        n = int(0.05 * SR)
        add(x, filt(rng.standard_normal(n), 300, 2500) * np.exp(-np.arange(n) / SR / 0.015) * 0.6, i / fps)
    return x


def escobazo(d=0.35):
    t_ = tt(d)
    return filt(rng.standard_normal(len(t_)), 1500, 7000) * np.sin(np.pi * t_ / d) ** 2 * 0.5


def brillito():
    x = np.zeros(int(0.9 * SR))
    for i, m_ in enumerate((88, 91, 95, 100)):
        add(x, ding(m_, 0.6), i * 0.07, 0.5)
    return x


fx = np.zeros(N)
T = V.T
# estática de la tele donde se ve la lluvia
for k in (1, 2, 3, 13, 14, 15):
    a_, b_ = T[k]
    add(fx, estatica(b_ - a_ + 0.05, 0.6 if k != 3 else 1.0), a_)
# P1: el Big Bang en la tele
add(fx, pop_(400, 900), 0.02, 0.5); add(fx, brillito(), V.T_BANG - 0.05, 0.6); add(fx, boing(0.4), V.T_BANG - 0.05, 0.4)
# P2: el viejo y la tele sin señal
add(fx, whoosh(0.35), T[2][0] - 0.06, 0.5); add(fx, pop_(), V.T_LLUVIA - 0.05, 0.35); add(fx, ding(84, 0.6), V.T_SENAL - 0.1, 0.5); add(fx, pop_(600, 1200), V.T_SENAL - 0.12, 0.4)
# P3: el puntito escondido
add(fx, whoosh(0.3), T[3][0] - 0.05, 0.5); add(fx, brillito(), T[3][0] + 0.25, 0.6); add(fx, pop_(700, 1500), V.T_ESC, 0.4)
# P4: la antena gigante
add(fx, whoosh(0.4), T[4][0] - 0.06, 0.5); add(fx, pop_(), T[4][0] + 0.15, 0.5); add(fx, pop_(650, 1300), V.T_COMO - 0.1, 0.5)
add(fx, sube(0.35, 150, 500), V.T_GIG - 0.12, 0.6); add(fx, golpe(0.4, 55), V.T_GIG + 0.2, 0.8)
# P5: el ruido que no se va
add(fx, whoosh(0.3), T[5][0] - 0.05, 0.4); add(fx, estatica(T[5][1] - V.T_RUIDO + 0.1, 0.7), V.T_RUIDO - 0.1)
add(fx, zap(0.2, 900, 300), V.T_NADA - 0.12, 0.7)
# P6: las palomas
add(fx, whoosh(0.35), T[6][0] - 0.06, 0.5); add(fx, arrullo(0.6), T[6][0] + 0.2, 0.7); add(fx, arrullo(0.5), V.T_PALOMAS + 0.15, 0.6)
add(fx, pop_(), V.T_PALOMAS - 0.12, 0.5)
# P7: se van volando y la escoba
add(fx, whoosh(0.3), T[7][0] - 0.05, 0.4); add(fx, aleteo(0.9), T[7][0], 0.7)
tk = V.T_LIMP
while tk < T[7][1] - 0.2:
    add(fx, escobazo(0.3), tk, 0.6); tk += 0.36
# P8: pero el ruido seguía
add(fx, estatica(T[8][1] - T[8][0], 0.75), T[8][0]); add(fx, golpe(0.35, 70), V.T_SEGUIA - 0.05, 0.9); add(fx, clac(), V.T_SEGUIA - 0.03, 0.6)
# P9: la luz más antigua (y el contador)
add(fx, whoosh(0.5), T[9][0] - 0.08, 0.6); add(fx, sube(0.9, 200, 1400), T[9][0], 0.45); add(fx, brillito(), V.T_LUZ - 0.1, 0.6)
tk = V.T_ANTIGUA - 0.1
while tk < V.T_ANTIGUA + 0.7:
    add(fx, clac(), tk, 0.25); tk += 0.07
add(fx, ding(89, 0.8), V.T_ANTIGUA + 0.72, 0.5)
# P10: llega de todo el cielo
add(fx, whoosh(0.4), T[10][0] - 0.06, 0.5); add(fx, sube(0.8, 300, 900), T[10][0] + 0.05, 0.35); add(fx, ding(84, 0.8), V.T_CIELO, 0.4)
# P11: por eso tu tele también la captaba
add(fx, whoosh(0.35), T[11][0] - 0.05, 0.5); add(fx, sube(0.6, 400, 1200), T[11][0] + 0.1, 0.35); add(fx, boing(0.45), V.T_CAPT2 - 0.1, 0.6); add(fx, brillito(), V.T_CAPT2, 0.4)
# P12: la grilla y el uno por ciento
add(fx, whoosh(0.3), T[12][0] - 0.05, 0.4)
for i in range(10):
    add(fx, blip(76 + i, 0.06), T[12][0] + i * 0.07, 0.35)
add(fx, ding(91, 0.9), V.T_UNO - 0.1, 0.6); add(fx, pop_(), V.T_UNO - 0.15, 0.5)
# P13: le pegabas a la tele
add(fx, whoosh(0.35), T[13][0] - 0.06, 0.5); add(fx, whoosh(0.25), V.T_PEGABAS - 0.25, 0.6); add(fx, golpe(0.4, 90), V.T_PEGABAS - 0.2, 1.0)
add(fx, clac(), V.T_PEGABAS - 0.19, 0.7); add(fx, boing(0.6), V.T_PEGABAS + 0.05, 0.7)
# P14: le pegabas al Big Bang (¡ay!)
add(fx, pop_(500, 1000), T[14][0] + 0.02, 0.4); add(fx, trombon_triste()[: int(0.75 * SR)], V.T_BANG2 - 0.1, 0.45); add(fx, pop_(800, 1600), V.T_BANG2 - 0.1, 0.5)
# P15: vuelta al cuadro 0
add(fx, whoosh(0.3), T[15][0] - 0.05, 0.4); add(fx, brillito(), T[15][0] + 0.05, 0.4)

fr = np.sqrt(np.mean(fx[np.abs(fx) > 1e-3] ** 2))
fx *= (vr / 10 ** (12.5 / 20)) / fr
mix = v * (0.25 / vr) + (m + fx) * (0.25 / vr)
mix = np.tanh(mix * 1.2) / 1.2
mix[-int(0.15 * SR):] *= np.linspace(1, 0, int(0.15 * SR))
os.makedirs(OUT, exist_ok=True)
tmp = os.path.join(OUT, "pre.wav")
wavfile.write(tmp, SR, (mix / (np.abs(mix).max() + 1e-9) * 0.9 * 32767).astype(np.int16))
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "alimiter=limit=0.7:level=false,loudnorm=I=-14:TP=-1.5:LRA=11",
                "-ar", "48000", os.path.join(OUT, "mix.wav")], check=True)
print("ok audio", os.path.join(OUT, "mix.wav"))
