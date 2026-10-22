"""Audio del Ep. 4: voz + música sintetizada (marimba juguetona; se corta en seco en "No." y vuelve) con ducking,
agua de ducha de fondo en todo el video (el sonido que amarra) y los efectos de la columna SFX del storyboard
→ OUT/ep04_mix.wav (−14 LUFS, TP ≤ −1,5 dBTP). Todo sintetizado."""
import glob, json, os, subprocess, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ep04 as E

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
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(REPO, "out/tts/ep04-cortina-ducha.mp3"), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
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


def ducha(d):
    """Agua de ducha: ruido de banda ancha con un leve chapoteo (lo que amarra el video)."""
    n = int(d * SR)
    x = filt(ruido(n), 900, 9000) * 0.10 + filt(ruido(n), 150, 900) * 0.04
    mod = 1 + 0.15 * np.sin(2 * np.pi * 0.7 * tt(d)) + 0.1 * filt(ruido(n), None, 6) * 4
    return x * mod


def plastico(d=0.35):
    """La cortina que pega: golpe blando de plástico + crujido."""
    n = int(d * SR)
    x = filt(ruido(n), 300, 3500) * env(n, 0.002, 0.06) * 0.9
    x += tono(np.linspace(180, 90, n), d, 0.001, 0.07) * 0.5
    return x


def chillido():
    """Patito de goma: chillido que sube y baja."""
    d = 0.32
    f = 900 + 500 * np.sin(np.linspace(0, np.pi, int(d * SR)))
    x = tono(f, d, 0.01, 0.25)
    x = x + 0.4 * tono(f * 2, d, 0.01, 0.2)
    return np.tanh(x * 2.5) * 0.35 * np.sin(np.linspace(0, np.pi, len(x)))


def fantasma(d=1.3):
    """Theremin de película de terror (glissando con vibrato), en broma."""
    t = tt(d)
    f = 520 + 380 * np.sin(np.linspace(-0.4, 2.2, len(t))) + 18 * np.sin(2 * np.pi * 6 * t)
    return tono(f, d, 0.08, 9.0) * np.sin(np.linspace(0, np.pi, len(t))) ** 0.6 * 0.45


def golpecito(f=1200):
    return tono(f, 0.12, 0.001, 0.03) * 0.6


def zumbido_giro(d):
    """El remolino girando: zumbido grave con barridos (como una rueda)."""
    t = tt(d)
    x = filt(ruido(len(t)), 200, 1400) * (0.6 + 0.4 * np.sin(2 * np.pi * 2.2 * t)) * 0.25
    x += tono(110 + 10 * np.sin(2 * np.pi * 2.2 * t), d, 0.3, 50) * 0.18
    return x * np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.3)


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


# ---------------- música: marimba juguetona en Do mayor, 112 bpm ----------------
def marimba(f, d=0.5):
    return (tono(f, d, 0.001, 0.18) + 0.25 * tono(f * 4.0, d, 0.001, 0.05) + 0.12 * tono(f * 9.9, d, 0.001, 0.02)) * 0.5


def musica():
    out = np.zeros(N)
    bpm = 112
    negra = 60 / bpm
    prog = [(48, 64, 67, 72), (45, 64, 69, 72), (41, 65, 69, 72), (43, 62, 67, 71)]     # C Am F G
    patron = [0, 2, 1, 2, 3, 2, 1, 2]
    for b in range(int(DUR / (negra * 4)) + 2):
        ch = prog[b % 4]
        i0 = b * negra * 4
        add(out, tono(440 * 2 ** ((ch[0] - 69) / 12), 0.6, 0.005, 0.3) * 0.35, i0)              # bajo
        add(out, tono(440 * 2 ** ((ch[0] - 57) / 12), 0.4, 0.005, 0.2) * 0.2, i0 + negra * 2)
        for k, p in enumerate(patron):
            m = ch[1 + p % 3] + (12 if p == 3 else 0)
            add(out, marimba(440 * 2 ** ((m - 69) / 12)), i0 + k * negra / 2, 0.35 if k % 2 == 0 else 0.25)
    return filt(out, 60, 9000)


def add(buf, x, at, g=1.0):
    i = int(at * SR)
    j = min(N, i + len(x))
    if 0 <= i < N:
        buf[i:j] += g * x[: j - i]


v = voz()
m = musica()
t_all = np.arange(N) / SR
gate = np.ones(N)
# corte en seco de la música en "No." (vuelve con la explicación) y otra vez antes del remate final
for c0, c1 in ((W("no") - 0.05, T(6) + 0.2), (W("ahí", 33.0) - 0.15, W("ahí", 33.0) + 1.0)):
    gate[(t_all > c0) & (t_all < c1)] = 0.0
    r_ = (t_all >= c1) & (t_all < c1 + 0.4)
    gate[r_] = (t_all[r_] - c1) / 0.4
m *= gate
envv = np.convolve(np.abs(v), np.ones(int(0.08 * SR)) / int(0.08 * SR), mode="same")
m *= 1.0 - 0.55 * np.clip(envv / 0.15, 0, 1)

fx = np.zeros(N)
add(fx, ducha(DUR), 0.0, 0.55)                                   # agua de fondo todo el video
add(fx, whoosh(0.6, True), 0.15, 0.55)                           # la cortina que se viene
add(fx, plastico(), W("cortina") + 0.05, 1.0)                    # le pega en la espalda
add(fx, chillido(), W("cortina") + 0.28, 0.9)                    # se cae el patito
add(fx, golpecito(700), W("cortina") + 0.55, 0.7)
add(fx, whoosh(0.35, False), 2.62, 0.7)                          # se da vuelta
add(fx, plastico(0.3), 3.25, 0.9)                                # se le pega en la cara
add(fx, fantasma(1.35), W("un", 3.0), 1.0)                       # "¿Un fantasma?"
add(fx, golpecito(500), W("no") + 0.02, 0.8)                     # "No." (corte de música)
add(fx, whoosh(0.5, True), T(6, 0.05), 0.4)
add(fx, ding(1046, 0.6), W("aire", 6.0), 0.4)                    # píldora AIRE CALIENTE
add(fx, ding(1175, 0.6), W("agua", 7.5), 0.4)                    # píldora AGUA CALIENTE
add(fx, perilla(), W("pasa", 9.8), 0.9)                          # la llave a fría
add(fx, ding(1568, 0.6), W("agua", 10.5), 0.4)                   # píldora AGUA FRÍA
add(fx, whoosh(1.0, False), T(9, 0.1), 0.6)                      # la cámara baja al corte
add(fx, whoosh(0.8, False), W("arrastra"), 0.5)                  # el aire baja con el chorro
add(fx, zumbido_giro(W("en", 19.0) - W("arma") + 0.4), W("arma"), 1.0)   # el remolino gira
add(fx, wub(), W("presión") - 0.05, 0.9)                         # baja presión
add(fx, whoosh(0.7, True), W("afuera") - 0.2, 0.7)               # el aire de afuera empuja
add(fx, plastico(), T(16) + 0.55, 1.0)                           # "hacia ti": otro golpe
add(fx, whoosh(0.5, False), T(17, 0.1), 0.6)                     # baja la cortina pesada
add(fx, thud(), 27.35, 1.0)
add(fx, ding(1568, 0.8), W("pesada"), 0.5)                       # píldora CORTINA PESADA ✓
add(fx, zumbido_giro(d_(19) * 0.9), T(19), 0.6)
add(fx, fantasma(1.6), W("ahí", 33.0) - 0.1, 1.0)               # remate: "ahí sí es un fantasma"
add(fx, plastico(0.3), W("ahí", 33.0) + 0.2, 0.7)

mix = v * 1.0 + m * 0.50 + fx * 0.42
mix = np.tanh(mix * 1.1) / 1.1
mix = mix / (np.abs(mix).max() + 1e-9) * 0.9
os.makedirs(OUT, exist_ok=True)
tmp = os.path.join(OUT, "ep04_pre.wav")
wavfile.write(tmp, SR, (mix * 32767).astype(np.int16))
dst = os.path.join(OUT, "ep04_mix.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", dst], check=True)
vr = np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2))
mr = np.sqrt(np.mean((m * 0.50)[(m != 0)] ** 2) + 1e-12)
print("ok audio", dst, "voz/música dB:", round(20 * np.log10(vr / mr), 1))
