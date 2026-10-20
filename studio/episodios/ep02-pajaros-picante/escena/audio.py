"""Audio del Ep. 2: voz + música sintetizada (guitarrita del desierto con ducking) + efectos por plano
→ OUT/ep02_mix.wav (−14 LUFS, TP ≤ −1,5 dBTP). Efectos de la columna SFX del storyboard v3.1. Todo sintetizado: sin
música ni sonidos con derechos."""
import json, os, subprocess, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ep02 as E2

OUT = os.environ.get("OUT", os.path.join(HERE, "out"))
REPO = os.environ.get("REPO", os.path.abspath(os.path.join(HERE, "../../../..")))
SR = 48000
DUR = (E2.FIN - 1) / 30
N = int(DUR * SR)
rng = np.random.default_rng(12)


def T(k, off=0.0):
    return E2.T[k][0] + off


def W(prefix, after=0.0):
    return E2.t_palabra(prefix, after)


def voz():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(REPO, "out/tts/ep02-pajaros-picante.mp3"), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
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


def env(n, a=0.004, d=0.1):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def tt(d):
    return np.arange(int(d * SR)) / SR


def ruido(n):
    return rng.standard_normal(n)


def tono(f, d, a=0.003, dec=0.2):
    t = tt(d)
    f = np.broadcast_to(np.asarray(f, dtype=float), t.shape) if np.ndim(f) else np.full(t.shape, float(f))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), a, dec)


# ---------------- efectos ----------------
def viento(d):
    n = int(d * SR)
    x = filt(ruido(n), 150, 900)
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.35 * np.arange(n) / SR + 1.3)
    return x * lfo * np.minimum(1, np.arange(n) / (0.3 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.3 * SR)) * 0.35


def chisporroteo(d, densidad=40):
    n = int(d * SR)
    out = filt(ruido(n), 200, 1500) * 0.12
    for _ in range(int(d * densidad)):
        i = int(rng.random() * (n - 800))
        m = int(rng.uniform(0.002, 0.006) * SR)
        out[i:i + m] += filt(ruido(m), 1500, 9000) * env(m, 0.0003, 0.0015) * rng.uniform(0.3, 1.0)
    return out


def glup():
    t = tt(0.32)
    f = 420 - 300 * t / 0.32
    burbuja = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.004, 0.09)
    return 0.9 * burbuja + 0.25 * filt(ruido(len(t)), 200, 1200) * env(len(t), 0.002, 0.03)


def mordisco():
    t = tt(0.22)
    crunch = filt(ruido(len(t)), 1200, 6000) * env(len(t), 0.001, 0.04)
    return 0.7 * crunch + 0.5 * np.sin(2 * np.pi * 240 * t) * env(len(t), 0.002, 0.04)


def llamarada():
    n = int(0.9 * SR)
    x = ruido(n)
    out = np.zeros(n)
    seg = 1200
    for k in range(0, n, seg):
        c = 300 + 1800 * np.exp(-k / n * 3)
        out[k:k + seg] = filt(x[k:k + seg], c * 0.5, min(c * 2.2, 20000))
    return out * env(n, 0.01, 0.35) * 1.4


def latigazo():
    t = tt(0.12)
    return filt(ruido(len(t)), 2500, 14000) * env(len(t), 0.0005, 0.02) * 1.3


def golpe_grave():
    t = tt(0.45)
    return np.sin(2 * np.pi * (70 - 30 * t) * t) * env(len(t), 0.003, 0.18) * 1.3


def pop():
    t = tt(0.12)
    return np.sin(2 * np.pi * (500 * t + 4000 * t * t)) * env(len(t), 0.002, 0.03)


def suspiro():
    n = int(0.8 * SR)
    t = np.arange(n) / SR
    x = filt(ruido(n), 300, 2500)
    return x * np.sin(np.pi * t / 0.8) ** 2 * 0.55


def whoosh(d=0.35, up=True):
    n = int(d * SR)
    x = ruido(n)
    out = np.zeros(n)
    seg = 1200
    for k in range(0, n, seg):
        c = 400 + 2600 * (k / n if up else 1 - k / n)
        out[k:k + seg] = filt(x[k:k + seg], c * 0.7, min(c * 1.6, 20000))
    return out * np.sin(np.pi * np.arange(n) / n) ** 2


def ding(f=1320, d=0.6):
    t = tt(d)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.01 * t)) * env(len(t), 0.002, 0.25)


def timbre(d=1.0, f=1800, apagado=False):
    t = tt(d)
    golpes = (np.sin(2 * np.pi * 22 * t) > 0).astype(float)
    x = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.4 * t)) * (0.5 + 0.5 * golpes)
    e = np.minimum(1, t / 0.01) * np.exp(-t / (0.08 if apagado else 0.6))
    return x * e * (0.35 if apagado else 0.5)


def crack():
    t = tt(0.25)
    return filt(ruido(len(t)), 800, 7000) * env(len(t), 0.0005, 0.04) + 0.4 * np.sin(2 * np.pi * 180 * t) * env(len(t), 0.001, 0.05)


def clic():
    t = tt(0.06)
    return filt(ruido(len(t)), 2500, 9000) * env(len(t), 0.0003, 0.006) + 0.5 * np.sin(2 * np.pi * 2200 * t) * env(len(t), 0.0005, 0.01)


def sirena(d=1.2):
    t = tt(d)
    f = 700 + 350 * (0.5 - 0.5 * np.cos(2 * np.pi * t / 0.6))
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.25 + np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4
    return filt(x, 300, 4000) * np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.1)


def tic():
    t = tt(0.05)
    return filt(ruido(len(t)), 2000, 8000) * env(len(t), 0.0005, 0.008) * 1.2


def boing():
    t = tt(0.5)
    f = 180 + 120 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 5)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.003, 0.2)


def bip():
    return tono(2100, 0.12, 0.002, 0.08) * 0.6


def pasitos(d, paso=0.23):
    out = np.zeros(int(d * SR))
    for k in range(int(d / paso)):
        i = int(k * paso * SR)
        m = int(0.03 * SR)
        if i + m < len(out):
            out[i:i + m] += filt(ruido(m), 800, 4000) * env(m, 0.001, 0.008) * 0.6
    return out


def nop():
    return np.concatenate([tono(520, 0.12, 0.004, 0.08), tono(390, 0.18, 0.004, 0.1)]) * 0.6


def crujido():
    out = np.zeros(int(0.5 * SR))
    for k in range(6):
        i = int(rng.uniform(0, 0.3) * SR)
        m = int(0.04 * SR)
        out[i:i + m] += filt(ruido(m), 1500, 7000) * env(m, 0.001, 0.01)
    return out * 0.9


def plop():
    t = tt(0.2)
    return np.sin(2 * np.pi * np.cumsum(300 - 600 * t) / SR) * env(len(t), 0.002, 0.06)


def brote(d=1.6):
    t = tt(d)
    f = 400 + 900 * t / d
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, t / 0.1) * np.minimum(1, (d - t) / 0.2) * 0.25 + \
        filt(ruido(len(t)), 3000, 9000) * 0.05


def bajo_disco(d=1.2, bpm=120):
    out = np.zeros(int(d * SR))
    beat = 60 / bpm
    for k in range(int(d / beat * 2)):
        i = int(k * beat / 2 * SR)
        x = np.sin(2 * np.pi * (55 if k % 2 == 0 else 82) * tt(beat / 2)) * env(int(beat / 2 * SR), 0.003, 0.12)
        j = min(len(out), i + len(x))
        out[i:j] += x[: j - i]
    return out * 1.2


def bzz(d=0.45):
    t = tt(d)
    return np.sign(np.sin(2 * np.pi * 110 * t)) * 0.3 * np.minimum(1, t / 0.01) * np.minimum(1, (d - t) / 0.02)


def hojas(d):
    n = int(d * SR)
    out = np.zeros(n)
    for k in range(int(d * 6)):
        i = int(rng.random() * (n - 0.2 * SR))
        m = int(0.18 * SR)
        out[i:i + m] += filt(ruido(m), 2000, 8000) * np.sin(np.pi * np.arange(m) / m) * 0.25
    return out


def plin():
    return ding(2640, 0.35) * 0.7


def mordisquitos(d, cada=0.5):
    out = np.zeros(int(d * SR))
    for k in range(int(d / cada)):
        x = mordisco() * 0.5
        i = int(k * cada * SR)
        j = min(len(out), i + len(x))
        out[i:j] += x[: j - i]
    return out


def sorbo():
    t = tt(0.9)
    return filt(ruido(len(t)), 500, 3000) * env(len(t), 0.05, 0.4) * (0.6 + 0.4 * np.sin(2 * np.pi * 14 * t))


def psss():
    t = tt(0.7)
    return filt(ruido(len(t)), 4000, 12000) * env(len(t), 0.02, 0.3) * 0.6


def baja_tono(d=1.4):
    t = tt(d)
    return np.sin(2 * np.pi * np.cumsum(660 - 300 * t / d) / SR) * np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.2) * 0.3


def burbujas(d):
    out = np.zeros(int(d * SR))
    for k in range(int(d * 25)):
        i = int(rng.random() * (len(out) - 0.05 * SR))
        x = tono(rng.uniform(900, 2200), 0.04, 0.001, 0.01) * 0.25
        out[i:i + len(x)] += x
    return out


def fanfarria():
    def nota(m, d):
        f = 440 * 2 ** ((m - 69) / 12)
        t = tt(d)
        saw = 2 * ((f * t) % 1) - 1
        return filt(saw, 200, 3500) * env(len(t), 0.01, d * 0.8) * 0.35
    return np.concatenate([nota(67, 0.12), nota(72, 0.12), nota(76, 0.4)])


def mmhm():
    def hum(f0, f1, d):
        t = tt(d)
        f = np.linspace(f0, f1, len(t))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
        return filt(x, 100, 1500) * np.sin(np.pi * np.arange(len(t)) / len(t)) * 0.4
    return np.concatenate([hum(180, 150, 0.22), np.zeros(int(0.06 * SR)), hum(150, 200, 0.28)])


def pops_cadena(d, n=24):
    out = np.zeros(int(d * SR))
    for k in range(n):
        i = int(k / n * (d - 0.15) * SR)
        x = pop() * 0.35
        out[i:i + len(x)] += x
    return out


# ---------------- música: guitarrita del desierto (cuerda pulsada) a 104 BPM ----------------
def cuerda(f, d, g=0.25):
    n = int(d * SR)
    p = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, p)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.996
    return out * g


def musica():
    bpm = 104
    beat = 60 / bpm
    out = np.zeros(N)
    prog = [(57, 60, 64), (53, 57, 60), (55, 59, 62), (52, 56, 59)]     # Am F G E: aire de western de dibujo animado
    cache = {}

    def nota(m, d, g):
        key = (m, round(d, 3))
        if key not in cache:
            cache[key] = cuerda(440 * 2 ** ((m - 69) / 12), d, 1.0)
        return cache[key] * g

    nb = int(DUR / beat) + 1
    for b in range(nb):
        i = int(b * beat * SR)
        ch = prog[(b // 4) % 4]
        x = nota(ch[0] - 12, beat * 1.4, 0.32)
        if i + len(x) < N:
            out[i:i + len(x)] += x
        for h, m in ((0.5, ch[1]), (0.75, ch[2])):
            y = nota(m, beat * 0.8, 0.14)
            j = i + int(h * beat * SR)
            if j + len(y) < N:
                out[j:j + len(y)] += y
        if b % 2 == 1:   # castañuela suave
            m_ = int(0.03 * SR)
            y = filt(ruido(m_), 2500, 8000) * env(m_, 0.001, 0.006) * 0.06
            j = i + int(0.5 * beat * SR)
            if j + m_ < N:
                out[j:j + m_] += y
    return out


def add(buf, x, at, g=1.0):
    i = int(at * SR)
    j = min(N, i + len(x))
    if 0 <= i < N:
        buf[i:j] += g * x[: j - i]


v = voz()
m = musica()
t_all = np.arange(N) / SR
gate = np.ones(N)
# la música se corta en la llamarada (plano 4) y vuelve con la lengua (plano 7)
gate[(t_all > T(4) - 0.02) & (t_all < T(7))] = 0.0
ramp = (t_all >= T(7)) & (t_all < T(7) + 0.4)
gate[ramp] = (t_all[ramp] - T(7)) / 0.4
m *= gate
envv = np.convolve(np.abs(v), np.ones(int(0.08 * SR)) / int(0.08 * SR), mode="same")
m *= 1.0 - 0.6 * np.clip(envv / 0.15, 0, 1)

fx = np.zeros(N)
FR = E2.FR
d_ = lambda k: E2.T[k][1] - E2.T[k][0]
add(fx, viento(d_(1) + 0.3), T(1), 0.6)
add(fx, chisporroteo(d_(1)), T(1), 0.5)
add(fx, glup(), T(2, 0.75), 0.9)
f_m3 = (json.load(open(os.path.join(os.environ.get("RENDER", ""), "meta", "3.json"))).get("mordisco") if os.environ.get("RENDER") and
        os.path.exists(os.path.join(os.environ["RENDER"], "meta", "3.json")) else None)
add(fx, mordisco(), ((f_m3 - 1) / 30) if f_m3 else T(3, d_(3) * 0.58), 1.0)
add(fx, llamarada(), T(4, 0.08), 0.9)
add(fx, latigazo(), T(4, 0.06), 0.7)
add(fx, chisporroteo(d_(4) + d_(5)), T(4, 0.2), 0.35)
add(fx, golpe_grave(), T(5, 0.05), 0.8)
add(fx, pop(), T(5, 0.2), 0.5)
add(fx, suspiro(), T(6, 0.1), 0.8)
add(fx, whoosh(0.45, True), T(7) - 0.1, 0.7)
add(fx, ding(1320), T(8, d_(8) * 0.42), 0.5)
add(fx, timbre(1.2), T(9, d_(9) * 0.34), 0.7)
add(fx, crack(), T(10, 0.15), 0.8)
add(fx, clic(), T(11, d_(11) * 0.45), 0.8)
add(fx, timbre(1.0), T(11, d_(11) * 0.46), 0.7)
add(fx, sirena(1.2), T(12, 0.05), 0.55)
add(fx, pop(), T(12, 0.2), 0.4)
add(fx, tic(), T(13, d_(13) * 0.36), 1.0)
add(fx, pop(), T(13, 0.2), 0.4)
add(fx, ding(1320), T(14, 0.35), 0.45)
add(fx, pop(), T(14, 0.25), 0.4)
add(fx, boing(), T(15, d_(15) * 0.45), 0.8)
add(fx, timbre(1.0), T(16, d_(16) * 0.36), 0.7)
add(fx, glup(), T(17, 0.12), 0.9)
add(fx, viento(d_(18) + 0.4), T(18), 0.8)
add(fx, pop(), W("arizona", T(18)), 0.4)
add(fx, bip(), T(19, 18 / 30), 0.8)
add(fx, pop(), W("chiltepín", T(19)), 0.4)
add(fx, pasitos(d_(21) * 0.4), T(21), 0.6)
add(fx, nop(), T(21, d_(21) * 0.55), 0.7)
add(fx, pasitos(d_(21) * 0.4), T(21, d_(21) * 0.62), 0.5)
for k in range(2):
    add(fx, glup(), T(22, 0.25 + k * d_(22) * 0.5), 0.8)
add(fx, glup(), T(22, d_(22) * 0.9), 0.5)
add(fx, crujido(), T(23, 0.5), 0.8)
add(fx, crujido(), T(23, 1.4), 0.6)
add(fx, glup(), T(24, 0.3), 0.9)
add(fx, plop(), T(25, d_(25) * 0.10), 0.9)
add(fx, brote(1.6), T(25, d_(25) * 0.25), 0.7)
add(fx, golpe_grave(), W("picante", T(26)), 0.9)
add(fx, bajo_disco(E2.T[26][1] - W("guardia", T(26))), W("guardia", T(26)), 0.6)
add(fx, bzz(), T(27, d_(27) * 0.32), 0.6)
add(fx, whoosh(0.5, True), T(28) - 0.05, 0.9)
add(fx, hojas(d_(29)), T(29), 0.7)
add(fx, pop(), T(30, 0.2), 0.4)
add(fx, plin(), T(31, 0.15), 0.7)
add(fx, timbre(0.4, apagado=True), T(31, d_(31) * 0.78), 0.6)
add(fx, mordisquitos(d_(32) - 0.3, d_(32) * 0.27), T(32, d_(32) * 0.18), 0.7)
add(fx, chisporroteo(d_(33)), T(33), 0.6)
add(fx, sorbo(), T(34, d_(34) * 0.30), 0.8)
add(fx, psss(), T(34, d_(34) * 0.85), 0.7)
add(fx, pops_cadena(d_(35) * 0.6), T(35, d_(35) * 0.05), 0.6)
add(fx, baja_tono(d_(36) * 0.6), T(36, d_(36) * 0.12), 0.7)
add(fx, burbujas(d_(37)), T(37), 0.6)
add(fx, bzz(0.35), T(37, 0.25), 0.5)
add(fx, fanfarria(), T(38, 0.1), 0.8)
add(fx, golpe_grave(), T(38, d_(38) * 0.55), 0.8)
add(fx, mmhm(), T(39, 0.2), 0.9)
add(fx, viento(d_(40)), T(40), 0.5)
add(fx, chisporroteo(d_(40)), T(40), 0.5)

mix = v * 1.0 + m * 0.44 + fx * 0.45
mix = np.tanh(mix * 1.1) / 1.1
mix = mix / (np.abs(mix).max() + 1e-9) * 0.9
os.makedirs(OUT, exist_ok=True)
tmp = os.path.join(OUT, "ep02_pre.wav")
wavfile.write(tmp, SR, (mix * 32767).astype(np.int16))
dst = os.path.join(OUT, "ep02_mix.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", dst], check=True)
vr = np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2))
mr = np.sqrt(np.mean((m * 0.44)[(m != 0)] ** 2) + 1e-12)
print("ok audio", dst, "voz/música dB:", round(20 * np.log10(vr / mr), 1))
