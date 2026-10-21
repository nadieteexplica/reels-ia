"""Audio del Ep. 3: voz + música sintetizada (solemne, de documental: el contraste con lo absurdo es el chiste) con ducking
+ efectos de la columna SFX del storyboard → OUT/ep03_mix.wav (−14 LUFS, TP ≤ −1,5 dBTP). Todo sintetizado.
El "psshh-tum" de cada paso sale de los pasos reales de la animación (meta de cada cuadro: fase del ciclo)."""
import glob, json, os, subprocess, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ep03 as E

OUT = os.environ.get("OUT", os.path.join(HERE, "out"))
REPO = os.environ.get("REPO", os.path.abspath(os.path.join(HERE, "../../../..")))
RENDER = os.environ.get("RENDER", "")
SR = 48000
DUR = (E.FIN - 1) / 30
N = int(DUR * SR)
rng = np.random.default_rng(3)


def T(k, off=0.0):
    return E.T[k][0] + off


def d_(k):
    return E.T[k][1] - E.T[k][0]


def W(prefix, after=0.0):
    return E.t_palabra(prefix, after)


def voz():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(REPO, "out/tts/ep03-edificio-que-camino.mp3"), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True).stdout
    v = np.frombuffer(raw, np.float32).copy()
    v = np.pad(v, (0, max(0, N - len(v))))[:N]
    return v / (np.abs(v).max() + 1e-9) * 0.9


def filt(x, lo=None, hi=None, order=2):
    if lo and hi:
        return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)
    if lo:
        return sosfilt(butter(order, lo, btype="high", fs=SR, output="sos"), x)
    return sosfilt(butter(order, hi, btype="low", fs=SR, output="sos"), x)


def tt(d):
    return np.arange(int(d * SR)) / SR


def env(n, a=0.004, d=0.1):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def ruido(n):
    return rng.standard_normal(n)


def tono(f, d, a=0.003, dec=0.2):
    t = tt(d)
    ph = 2 * np.pi * np.cumsum(np.broadcast_to(np.asarray(f, float), t.shape)) / SR if np.ndim(f) else 2 * np.pi * f * t
    return np.sin(ph) * env(len(t), a, dec)


# ---------------- efectos ----------------
def paso(g=1.0):
    """psshh (hidráulico) + tum (pie que pisa)."""
    n1 = int(0.28 * SR)
    ps = filt(ruido(n1), 2500, 9000) * env(n1, 0.01, 0.09) * 0.35
    tum = tono(np.linspace(85, 48, int(0.35 * SR)), 0.35, 0.002, 0.09) * 0.9 + filt(ruido(int(0.35 * SR)), None, 220) * env(int(0.35 * SR), 0.001, 0.05) * 0.5
    out = np.zeros(int(0.45 * SR))
    out[:n1] += ps
    i = int(0.09 * SR)
    out[i:i + len(tum)] += tum[: len(out) - i]
    return out * g


def golpe_grave():
    return tono(np.linspace(70, 38, int(0.7 * SR)), 0.7, 0.002, 0.22) * 1.0 + filt(ruido(int(0.7 * SR)), None, 160) * env(int(0.7 * SR), 0.001, 0.08) * 0.7


def whoosh(d=0.45, up=True):
    n = int(d * SR)
    x = ruido(n)
    f = np.linspace(400, 3500, n) if up else np.linspace(3500, 400, n)
    out = np.zeros(n)
    seg = 512
    for i in range(0, n, seg):
        j = min(n, i + seg)
        c = f[i]
        out[i:j] = filt(x[max(0, i - 2048):j], c * 0.6, c * 1.4)[-(j - i):]
    return out * np.sin(np.linspace(0, np.pi, n)) * 0.6


def ding(f=1320, d=0.7):
    return (tono(f, d, 0.002, 0.25) + 0.4 * tono(f * 2.01, d, 0.002, 0.12)) * 0.5


def timbre_escuela(d=1.0):
    t = tt(d)
    x = np.sign(np.sin(2 * np.pi * 22 * t)) * np.sin(2 * np.pi * 980 * t) * np.exp(-t * 1.5)
    return filt(x, 500, 3000) * 0.25


def tic():
    n = int(0.03 * SR)
    return filt(ruido(n), 3000, 9000) * env(n, 0.0005, 0.006) * 0.8


def ticks(d, cada):
    out = np.zeros(int(d * SR))
    k = 0.0
    while k < d - 0.03:
        i = int(k * SR)
        x = tic()
        out[i:i + len(x)] += x[: len(out) - i]
        k += cada
    return out


def cadena(d=0.8):
    out = np.zeros(int(d * SR))
    for k in range(int(d * 22)):
        i = int(k / 22 * SR + rng.uniform(0, 0.02) * SR)
        x = tono(rng.uniform(2200, 4200), 0.05, 0.001, 0.02) * 0.3
        out[i:i + len(x)] += x[: len(out) - i]
    return out


def frenazo():
    n = int(0.45 * SR)
    return filt(ruido(n), 1500, 4000) * env(n, 0.01, 0.12) * 0.5 + tono(np.linspace(300, 120, n), 0.45, 0.005, 0.15) * 0.3


def tierra(d):
    n = int(d * SR)
    x = filt(ruido(n), 150, 1800) * 0.25
    gr = np.zeros(n)
    for k in range(int(d * 30)):
        i = int(rng.uniform(0, d - 0.05) * SR)
        y = filt(ruido(int(0.04 * SR)), 800, 5000) * env(int(0.04 * SR), 0.001, 0.01) * 0.4
        gr[i:i + len(y)] += y[: n - i]
    return (x + gr) * np.sin(np.linspace(0, np.pi, n))


def clic():
    n = int(0.02 * SR)
    return (filt(ruido(n), 2000, 8000) * env(n, 0.0005, 0.004) + tono(1800, 0.02, 0.0005, 0.005)) * 0.6


def clics(d, n_):
    out = np.zeros(int(d * SR))
    for k in range(n_):
        i = int(d * (k / n_) ** 1.3 * SR)
        x = clic()
        out[i:i + len(x)] += x[: len(out) - i] * 0.5
    return out


def hidraulico(d, sube=0.0):
    t = tt(d)
    f = 120 + 160 * sube * t / d
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + filt(ruido(len(t)), 300, 2500) * 0.12
    return x * np.minimum(1, t / 0.08) * np.minimum(1, (d - t) / 0.15)


def sierra(d):
    t = tt(d)
    x = filt(ruido(len(t)), 2500, 7000) * (0.6 + 0.4 * np.sin(2 * np.pi * 14 * t)) * 0.35
    ch = np.zeros(len(t))
    for k in range(int(d * 40)):
        i = int(rng.uniform(0, d - 0.02) * SR)
        y = filt(ruido(int(0.01 * SR)), 5000, 12000) * 0.6
        ch[i:i + len(y)] += y[: len(t) - i]
    return (x + ch) * np.minimum(1, (d - t) / 0.1)


def crujido(d=0.6):
    n = int(d * SR)
    out = np.zeros(n)
    for k in range(18):
        i = int(rng.uniform(0, d - 0.03) * SR)
        y = filt(ruido(int(0.025 * SR)), 300, 1600) * env(int(0.025 * SR), 0.001, 0.008) * 0.8
        out[i:i + len(y)] += y[: n - i]
    return out


def buzzer():
    t = tt(0.4)
    return filt(np.sign(np.sin(2 * np.pi * 140 * t)), None, 1800) * 0.25 * np.minimum(1, (0.4 - t) / 0.05)


def trazo(d=0.6):
    n = int(d * SR)
    return filt(ruido(n), 1500, 6000) * 0.12 * np.sin(np.linspace(0, np.pi, n))


def huincha(d):
    return ticks(d, 0.045) * 0.6 + filt(ruido(int(d * SR)), 2000, 6000) * 0.05


def grillos(d):
    t = tt(d)
    return np.sin(2 * np.pi * 4300 * t) * (np.sin(2 * np.pi * 24 * t) > 0.3) * (np.sin(2 * np.pi * 1.4 * t) > 0) * 0.05


def rieles(d):
    t = tt(d)
    return (filt(ruido(len(t)), 60, 400) * 0.35 + ticks(d, 0.33) * 0.8) * np.minimum(1, t / 0.2)


def tramos(d, n_):
    out = np.zeros(int(d * SR))
    for k in range(n_):
        i = int(d * k / n_ * SR)
        x = golpe_grave()[: int(0.25 * SR)] * 0.35
        out[i:i + len(x)] += x[: len(out) - i]
    return out


def ciudad(d):
    return filt(ruido(int(d * SR)), 100, 900) * 0.07


# ---------------- música: cuerdas solemnes en re menor ----------------
def musica():
    out = np.zeros(N)
    bpm = 66
    compas = 4 * 60 / bpm
    prog = [(50, 57, 62, 65), (46, 53, 58, 62), (53, 57, 60, 65), (48, 55, 60, 64)]   # Dm Bb F C
    t_ = tt(compas * 1.05)
    for b in range(int(DUR / compas) + 1):
        ch = prog[b % 4]
        x = np.zeros(len(t_))
        for m in ch:
            f = 440 * 2 ** ((m - 69) / 12)
            for h, g in ((1, 1.0), (2, 0.45), (3, 0.25), (4, 0.12)):
                x += g * np.sin(2 * np.pi * f * h * t_ + rng.uniform(0, 6.28)) * (1 + 0.004 * np.sin(2 * np.pi * 5.2 * t_))
        x *= np.minimum(1, t_ / 0.6) * np.minimum(1, (t_[-1] - t_) / 0.5) * 0.045
        i = int(b * compas * SR)
        j = min(N, i + len(x))
        out[i:j] += x[: j - i]
        # timbal suave al empezar cada compás
        tb = tono(np.linspace(62, 52, int(0.9 * SR)), 0.9, 0.003, 0.35) * 0.12
        out[i:i + len(tb)] += tb[: max(0, min(len(tb), N - i))]
    return filt(out, 60, 6000)


def add(buf, x, at, g=1.0):
    i = int(at * SR)
    j = min(N, i + len(x))
    if 0 <= i < N:
        buf[i:j] += g * x[: j - i]


def pasos_de_meta():
    """Momentos en que un grupo de patas aterriza (la fase cruza 0 o 0,5) en los planos que caminan."""
    tiempos = []
    if not RENDER:
        return tiempos
    for p in glob.glob(os.path.join(RENDER, "meta", "*.json")):
        d = json.load(open(p))
        if str(d["pieza"]) not in {"1", "2", "3", "12", "22", "35", "36", "20", "21", "28"}:
            continue
        c = sorted((int(f), v["fase"]) for f, v in d.get("cuadros", {}).items() if "fase" in v)
        for (f0, a), (f1, b) in zip(c, c[1:]):
            if f1 - f0 > 2:
                continue
            if int(a / 0.5) != int(b / 0.5) or (b < a):          # cruzó 0,5 o dio la vuelta
                tiempos.append((f1 - 1) / 30)
    return sorted(tiempos)


v = voz()
m = musica()
t_all = np.arange(N) / SR
gate = np.ones(N)
for c0, c1 in ((T(4) + 0.30, T(5)), (T(29, d_(29) - 0.05), T(31))):     # cortes en seco: "tiene patas" y "18 días"
    gate[(t_all > c0) & (t_all < c1)] = 0.0
    r_ = (t_all >= c1) & (t_all < c1 + 0.4)
    gate[r_] = (t_all[r_] - c1) / 0.4
m *= gate
envv = np.convolve(np.abs(v), np.ones(int(0.08 * SR)) / int(0.08 * SR), mode="same")
m *= 1.0 - 0.55 * np.clip(envv / 0.15, 0, 1)

fx = np.zeros(N)
for tp in pasos_de_meta():
    add(fx, paso(0.75), tp - 0.06)
add(fx, ciudad(d_(1) + d_(2) + d_(3)), 0.0, 1.0)
add(fx, golpe_grave(), W("patas", T(4)) + 0.05, 1.0)
add(fx, timbre_escuela(1.2), T(5, 0.1), 0.6)
add(fx, ding(1760, 0.9), T(6, 0.8), 0.6)
add(fx, ciudad(d_(7) + 0.4), T(7), 1.3)
add(fx, ticks(d_(8) - 0.5, 0.06), T(8, 0.15), 0.7)
add(fx, golpe_grave(), T(8, d_(8) - 0.42), 0.7)
add(fx, whoosh(1.2, True), T(9, 0.1), 0.6)
add(fx, whoosh(0.8, False), T(10, 0.2), 0.5)
add(fx, golpe_grave(), T(10, 1.4), 0.6)
add(fx, cadena(0.9), T(11), 0.7)
add(fx, frenazo(), T(11, 0.7), 0.8)
add(fx, tierra(d_(13)), T(13), 1.0)
add(fx, clics(d_(14) * 0.9, 40), T(14, 0.05), 1.0)
add(fx, hidraulico(d_(15), 0.2), T(15), 0.6)
add(fx, sierra(d_(16) - 0.1), T(16, 0.05), 0.8)
add(fx, hidraulico(d_(17), 1.0), T(17, 0.15), 0.8)
add(fx, ding(1320), T(18, 0.15), 0.6)
add(fx, ding(1568), T(18, 0.95), 0.6)
add(fx, golpe_grave(), T(19, 0.1), 0.6)
add(fx, hidraulico(d_(20) * 0.9, 0.5), T(20, 0.1), 0.7)
add(fx, hidraulico(d_(21) * 0.9, 0.5), T(21, 0.05), 0.6)
add(fx, crujido(0.7), T(23, 0.15), 0.9)
add(fx, crujido(0.7), T(23, 0.85), 0.9)
add(fx, crujido(1.0), T(24, 0.1), 1.0)
add(fx, paso(1.0), T(24, 1.0), 1.0)
add(fx, trazo(0.8), T(25, 0.05), 0.9)
add(fx, trazo(0.7), T(26, 0.05), 0.9)
add(fx, buzzer(), T(26, 0.75), 0.8)
add(fx, ticks(d_(27) - 0.2, 0.09), T(27, 0.1), 0.6)
add(fx, huincha(d_(28) - 0.1), T(28), 0.9)
add(fx, ticks(d_(29), 0.085), T(29), 0.9)
add(fx, ding(2093, 0.8), T(30, 0.9), 0.6)
add(fx, grillos(d_(30) - 0.9), T(30, 0.9), 1.0)
add(fx, whoosh(0.6, True), T(31, d_(31) * 0.45), 1.0)
add(fx, ciudad(d_(32)), T(32), 1.2)
add(fx, rieles(d_(33)), T(33), 0.9)
add(fx, tramos(d_(34) * 0.9, 12), T(34, 0.05), 0.8)

mix = v * 1.0 + m * 0.55 + fx * 0.42
mix = np.tanh(mix * 1.1) / 1.1
mix = mix / (np.abs(mix).max() + 1e-9) * 0.9
os.makedirs(OUT, exist_ok=True)
tmp = os.path.join(OUT, "ep03_pre.wav")
wavfile.write(tmp, SR, (mix * 32767).astype(np.int16))
dst = os.path.join(OUT, "ep03_mix.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", dst], check=True)
vr = np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2))
mr = np.sqrt(np.mean((m * 0.55)[(m != 0)] ** 2) + 1e-12)
print("ok audio", dst, "voz/música dB:", round(20 * np.log10(vr / mr), 1), "pasos:", len(pasos_de_meta()))
