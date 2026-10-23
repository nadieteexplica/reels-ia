"""Audio de Rhein 01: voz (dos tomas unidas en out/tts/rhein01-mosasaurio.mp3) + música sintetizada de aventura (marimba y
bajo; en la venta sube y se pone más brillante) con ducking, mar de fondo y los efectos de la columna SFX del storyboard
→ OUT/rhein01_mix.wav (−14 LUFS, TP ≤ −1,5 dBTP). Todo sintetizado (nada de música comercial)."""
import json, os, subprocess, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rhein01 as E

OUT = os.environ.get("OUT", os.path.join(HERE, "out"))
REPO = os.environ.get("REPO", os.path.abspath(os.path.join(HERE, "../../../..")))
SR = 48000
DUR = (E.FIN - 1) / 30
N = int(DUR * SR)
rng = np.random.default_rng(5)


def T(k, off=0.0):
    return E.T[k][0] + off


def W(prefix, after=0.0):
    return E.t_palabra(prefix, after)


def voz():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(REPO, "out/tts/rhein01-mosasaurio.mp3"), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
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


def golpecito(f=1200):
    return tono(f, 0.12, 0.001, 0.03) * 0.6


def wub():
    return tono(np.linspace(140, 45, int(0.8 * SR)), 0.8, 0.01, 0.3) * 0.9


def thud():
    g = golpe_grave() * 0.9
    n = int(0.5 * SR)
    g[:n] += filt(ruido(n), 80, 600) * env(n, 0.002, 0.12) * 0.4
    return g


def perilla():
    out = np.zeros(int(0.2 * SR))
    a, b = golpecito(2400), golpecito(1800)
    out[:len(a)] += a
    i = int(0.06 * SR)
    out[i:i + len(b)] += b[: len(out) - i]
    return out




def mar(d):
    n = int(d * SR)
    t = tt(d)
    x = filt(ruido(n), 200, 2500) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.18 * t) ** 2) * 0.10
    return x + filt(ruido(n), 40, 200) * 0.05


def chapuzon(g=1.0, d=0.9):
    n = int(d * SR)
    x = filt(ruido(n), 200, 6000) * env(n, 0.003, d * 0.35)
    x += tono(np.linspace(220, 60, n), d, 0.002, 0.15) * 0.6
    return x * g


def clac():
    n = int(0.12 * SR)
    return (filt(ruido(n), 1500, 7000) * env(n, 0.0005, 0.02) + tono(900, 0.12, 0.0005, 0.03) * 0.5) * 0.9


def trinquete(nclics=6, paso=0.05):
    out = np.zeros(int((nclics * paso + 0.2) * SR))
    for i in range(nclics):
        c = clac() * 0.6
        j = int(i * paso * SR)
        out[j:j + len(c)] += c[: len(out) - j]
    return out


def motor(d, f0=60, g=0.3):
    t = tt(d)
    x = np.sign(np.sin(2 * np.pi * f0 * t + 0.3 * np.sin(2 * np.pi * 7 * t))) * 0.3 + filt(ruido(len(t)), 80, 900) * 0.4
    return filt(x, None, 1800) * g * np.minimum(1, t / 0.2) * np.minimum(1, (d - t) / 0.2)


def bip(f=1400, d=0.09):
    return tono(f, d, 0.002, 0.05) * 0.6


def chirrido(d=0.6):
    t = tt(d)
    f = 2400 + 300 * np.sin(2 * np.pi * 13 * t)
    return np.tanh(tono(f, d, 0.01, 1.0) * 3) * 0.25 * np.sin(np.linspace(0, np.pi, len(t)))


def engranajes(d):
    t = tt(d)
    out = filt(ruido(len(t)), 300, 2500) * 0.08
    for i in range(int(d / 0.07)):
        c = clac() * 0.25
        j = int(i * 0.07 * SR)
        out[j:j + len(c)] += c[: len(out) - j]
    return out


def zumbido_metal(d):
    t = tt(d)
    return (tono(220 + 40 * t / d, d, 0.05, 50) * 0.2 + filt(ruido(len(t)), 2000, 8000) * 0.05) * np.sin(np.linspace(0, np.pi, len(t)))


def pop_(f=700):
    return tono(np.linspace(f, f * 0.5, int(0.08 * SR)), 0.08, 0.001, 0.03) * 0.7


def caja():
    return ding(2093, 0.5) + ding(2637, 0.5) * 0.6


def bocina():
    d = 0.5
    t = tt(d)
    x = np.sign(np.sin(2 * np.pi * 330 * t)) * 0.2 + np.sign(np.sin(2 * np.pi * 415 * t)) * 0.2
    return filt(x, None, 3000) * np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.05)


def silbido(d=0.75):
    t = tt(d)
    f = 1500 + 400 * np.sin(2 * np.pi * 2.5 * t) + 30 * np.sin(2 * np.pi * 7 * t)
    return tono(f, d, 0.05, 5.0) * 0.3 * np.sin(np.linspace(0, np.pi, len(t)))


def grave_sub(d):
    t = tt(d)
    return (tono(45 + 8 * t / d, d, 0.3, 60) * 0.7 + filt(ruido(len(t)), 30, 180) * 0.2) * np.minimum(1, t / 0.5) * np.minimum(1, (d - t) / 0.3)


def eructo():
    d = 0.55
    t = tt(d)
    f = 70 + 20 * np.sin(2 * np.pi * 9 * t)
    return np.tanh(tono(f, d, 0.02, 0.6) * 4) * 0.5 * np.sin(np.linspace(0, np.pi, len(t)))


def huesos_(d=0.9):
    out = np.zeros(int(d * SR))
    for i in range(14):
        c = tono(rng.uniform(1800, 3200), 0.06, 0.0005, 0.015) * rng.uniform(0.3, 0.7)
        j = int(rng.uniform(0, d - 0.1) * SR)
        out[j:j + len(c)] += c[: len(out) - j]
    return out


def carga(d):
    t = tt(d)
    f = 200 * (6 ** (t / d))
    return (tono(f, d, 0.01, 50) * 0.3 + filt(ruido(len(t)), 1000, 8000) * 0.1 * t / d) * np.minimum(1, t / 0.1)


def explosion():
    d = 1.2
    n = int(d * SR)
    return filt(ruido(n), 40, 3000) * env(n, 0.003, 0.35) * 1.1 + tono(np.linspace(90, 30, n), d, 0.002, 0.4) * 0.8


def rugido():
    d = 0.6
    t = tt(d)
    return np.tanh((filt(ruido(len(t)), 80, 900) * 2 + tono(95, d, 0.02, 0.5)) * 2) * 0.35 * np.sin(np.linspace(0, np.pi, len(t)))


def marimba(f, d=0.5):
    return (tono(f, d, 0.001, 0.18) + 0.25 * tono(f * 4.0, d, 0.001, 0.05) + 0.12 * tono(f * 9.9, d, 0.001, 0.02)) * 0.5



def musica():
    out = np.zeros(N)
    bpm = 124
    negra = 60 / bpm
    prog = [(45, 64, 69, 72), (41, 65, 69, 72), (48, 64, 67, 72), (43, 62, 67, 71)]     # Am F C G (aventura)
    patron = [0, 2, 1, 2, 3, 2, 1, 2]
    t_venta = W("muy", 29.0) - 0.1
    for b in range(int(DUR / (negra * 4)) + 2):
        ch = prog[b % 4]
        i0 = b * negra * 4
        venta = i0 >= t_venta
        g = 1.25 if venta else 1.0
        add(out, tono(440 * 2 ** ((ch[0] - 69) / 12), 0.6, 0.005, 0.3) * 0.35 * g, i0)
        add(out, tono(440 * 2 ** ((ch[0] - 57) / 12), 0.4, 0.005, 0.2) * 0.2 * g, i0 + negra * 2)
        for k, p in enumerate(patron):
            m = ch[1 + p % 3] + (12 if p == 3 else 0) + (12 if venta and k % 4 == 0 else 0)
            add(out, marimba(440 * 2 ** ((m - 69) / 12)), i0 + k * negra / 2, (0.35 if k % 2 == 0 else 0.25) * g)
        for k in range(4):          # bombo y caja simples: más energía
            add(out, tono(np.linspace(120, 45, int(0.15 * SR)), 0.15, 0.001, 0.06) * (0.5 if k % 2 == 0 else 0.0) * g, i0 + k * negra)
            if k % 2 == 1:
                nn = int(0.12 * SR)
                add(out, filt(ruido(nn), 1500, 8000) * env(nn, 0.001, 0.04) * 0.25 * g, i0 + k * negra)
    return filt(out, 50, 10000)


def add(buf, x, at, g=1.0):
    i = int(at * SR)
    j = min(N, i + len(x))
    if 0 <= i < N:
        buf[i:j] += g * x[: j - i]



v = voz()
m = musica()
t_all = np.arange(N) / SR
gate = np.ones(N)
# corte en seco de la música en el clímax (sólo efectos) y vuelve fuerte con la venta
c0, c1 = W("agárrate") - 0.05, W("muy", 29.0) - 0.15
gate[(t_all > c0) & (t_all < c1)] = 0.0
m *= gate
envv = np.convolve(np.abs(v), np.ones(int(0.08 * SR)) / int(0.08 * SR), mode="same")
m *= 1.0 - 0.55 * np.clip(envv / 0.15, 0, 1)

fx = np.zeros(N)
add(fx, mar(DUR), 0.0, 0.5)
add(fx, zumbido_metal(1.4), 0.1, 0.5)                                   # 1 crujido del cable
for i in range(10):                                                     # 2 cada pollo que aparece en la montaña
    add(fx, pop_(600 + 40 * i), T(2) + 0.08 * i, 0.5)
add(fx, caja(), T(2) + 0.85, 0.6)
for i in range(8):                                                      # 3 los pollos vuelan a la cuerda
    add(fx, whoosh(0.25, True), T(3) + 0.15 * i, 0.25)
add(fx, grave_sub(1.2), T(4), 0.8)                                      # 4 la sombra enorme
add(fx, bocina(), T(5) + 0.2, 0.6)                                      # 5 bocina de micro
add(fx, ding(1568, 0.6), T(5) + 0.8, 0.4)                               #   regla 12 M
add(fx, motor(1.4, 50, 0.35), T(6), 1.0)                                # 6 motor de grúa
for i in range(3):
    add(fx, bip(1000, 0.18), T(6) + 0.3 + 0.4 * i, 0.5)                 #   bip de retroceso
for i in range(5):                                                      # 7 pernos que aprietan
    add(fx, trinquete(4, 0.04), T(7) + 0.1 + 0.25 * i, 0.6)
    add(fx, clac(), T(7) + 0.27 + 0.25 * i, 0.8)
add(fx, chapuzon(0.8, 0.6), T(8) + 0.05, 1.0)                           # 8 la popa se hunde
add(fx, zumbido_metal(1.0), T(9), 0.9)                                  # 9 el cable se trenza
add(fx, wub(), T(10) + 0.1, 0.6)                                        # 10 se tensa y sube
add(fx, engranajes(1.4), T(11), 0.9)                                    # 11 engranajes
add(fx, chirrido(0.7), T(12) + 0.15, 0.8)                               # 12 freno
add(fx, trinquete(6, 0.2), T(13), 0.9)                                  # 13 clic clic clic
add(fx, thud(), T(14) + 0.45, 0.9)                                      # 14 tirón y golpe
add(fx, clac(), T(15) + 0.2, 0.8)                                       # 15 pernos del asiento
for x in (0.15, 0.45, 0.75):                                            # 16 el arnés traba
    add(fx, clac(), T(16) + x + 0.1, 1.0)
add(fx, ding(1760, 0.6), T(17) + 0.2, 0.5)                              # 17 pulgar arriba
add(fx, ding(880, 0.3), T(18), 0.4)                                     # 18 radar se enciende
add(fx, bip(1400), T(18) + 0.5, 0.6)
add(fx, grave_sub(1.2), T(19), 0.9)                                     # 19 sube desde lo oscuro
add(fx, silbido(0.7), T(20), 0.7)                                       # 20 silba
t_b = T(21)
for i in range(16):                                                     # 21–23 bips cada vez más rápidos
    t_b += max(0.06, 0.32 * (0.82 ** i))
    if t_b < W("agárrate"):
        add(fx, bip(1500), t_b, 0.7)
add(fx, wub(), W("agárrate") + 0.1, 0.7)                                # 24 tensión
add(fx, chapuzon(1.4, 1.2), T(25) + 0.1, 1.2)                           # 25 sale del agua
add(fx, eructo(), T(25) + 0.75, 0.0)
add(fx, motor(1.0, 85, 0.35), T(26), 1.0)                               # 26 remolque
add(fx, whoosh(0.8, True), T(26), 0.6)
add(fx, huesos_(0.95), T(27), 1.0)                                      # 27 lluvia de huesos
add(fx, eructo(), T(27) + 0.35, 0.9)
add(fx, golpecito(900), T(28) + 0.3, 0.5)                               # 28 goteo
add(fx, carga(1.0), T(29), 0.9)                                         # 29 carga + explosión
add(fx, explosion(), T(29) + 1.0, 1.0)
for k in (30, 31, 34, 35):
    add(fx, whoosh(0.35, True), T(k), 0.35)
add(fx, ding(1568, 0.5), T(32), 0.4)
add(fx, rugido(), T(33), 0.6)
add(fx, bip(1500), T(35) + 0.6, 0.5)
add(fx, golpecito(500), T(37) + 0.3, 0.7)
add(fx, ding(1319, 0.9), T(38) + 0.05, 0.6)
add(fx, ding(1976, 0.9), T(38) + 0.2, 0.45)

mix = v * 1.0 + m * 0.42 + fx * 0.42
mix = np.tanh(mix * 1.1) / 1.1
mix = mix / (np.abs(mix).max() + 1e-9) * 0.9
os.makedirs(OUT, exist_ok=True)
tmp = os.path.join(OUT, "rhein01_pre.wav")
wavfile.write(tmp, SR, (mix * 32767).astype(np.int16))
dst = os.path.join(OUT, "rhein01_mix.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", dst], check=True)
vr = np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2))
mr = np.sqrt(np.mean((m * 0.42)[(m != 0)] ** 2) + 1e-12)
print("ok audio", dst, "voz/música dB:", round(20 * np.log10(vr / mr), 1))
