"""Audio del Ep. 5: voz + música sintetizada (pulso suave y luminoso, de asombro) con ducking, viento del salar de
fondo (lo que amarra el exterior), zumbido grave del imán en los planos de la rana y los efectos de la columna SFX del
storyboard → OUT/ep05_mix.wav (−14 LUFS, TP ≤ −1,5 dBTP). Todo sintetizado."""
import glob, json, os, subprocess, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ep05 as E

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
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(REPO, os.environ.get("VOZ", "out/tts/ep05-iman-rana-v3.mp3")), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
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


def viento(d):
    """Viento del salar: ruido grave que respira (amarra todo lo que pasa afuera)."""
    n = int(d * SR)
    x = filt(ruido(n), 80, 900) * 0.06 + filt(ruido(n), 900, 4000) * 0.012
    mod = 0.75 + 0.25 * np.sin(2 * np.pi * 0.13 * tt(d)) + 0.15 * np.sin(2 * np.pi * 0.31 * tt(d) + 1.0)
    return x * mod


def zumbido_iman(d, f0=55):
    """El electroimán prendido: zumbido grave limpio (con su armónico)."""
    t = tt(d)
    x = np.sin(2 * np.pi * f0 * t) * 0.18 + np.sin(2 * np.pi * f0 * 2 * t) * 0.07 + np.sin(2 * np.pi * f0 * 3 * t) * 0.03
    return x * np.minimum(1, t / 0.25) * np.minimum(1, (d - t) / 0.25)


def glup():
    d = 0.35
    f = np.linspace(260, 720, int(d * SR))
    return tono(f, d, 0.004, 0.08) * 0.55


def tic(f=2600):
    return tono(f, 0.06, 0.0008, 0.015) * 0.45


def clank(f=210):
    n = int(0.9 * SR)
    x = (tono(f, 0.9, 0.001, 0.35) + 0.6 * tono(f * 2.76, 0.9, 0.001, 0.2) + 0.35 * tono(f * 5.4, 0.9, 0.001, 0.1)) * 0.5
    x[: int(0.05 * SR)] += filt(ruido(int(0.05 * SR)), 300, 4000) * 0.5
    return x


def electrico(d):
    """Zumbido eléctrico que sube (los cables que se encienden)."""
    t = tt(d)
    f = 60 + 40 * t / d
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15 + filt(ruido(len(t)), 2000, 8000) * 0.02 * (t / d)
    return np.tanh(x * 3) * 0.3 * np.minimum(1, t / 0.2) * np.minimum(1, (d - t) / 0.3)


def whoom(d=1.2):
    t = tt(d)
    return tono(np.linspace(90, 160, len(t)), d, 0.3, 50) * 0.35 * np.sin(np.linspace(0, np.pi, len(t)))


def pfff():
    n = int(0.5 * SR)
    return filt(ruido(n), 600, 3000) * env(n, 0.02, 0.15) * 0.4


# ---------------- música: pads de asombro (Re mayor / Si menor), 84 bpm ----------------
def pad(f, d):
    t = tt(d)
    x = sum(np.sin(2 * np.pi * f * (1 + dt) * t) for dt in (-0.003, 0.0, 0.004)) / 3
    return x * np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.6)


def campanita(f, d=1.2):
    return (tono(f, d, 0.002, 0.6) + 0.3 * tono(f * 2.0, d, 0.002, 0.3)) * 0.35


def musica():
    out = np.zeros(N)
    bpm = 84
    compas = 60 / bpm * 4
    prog = [(50, 62, 66, 69), (47, 62, 66, 71), (43, 59, 62, 67), (45, 61, 64, 69)]      # D Bm G A
    arpe = [0, 1, 2, 1, 3, 2, 1, 2]
    for b in range(int(DUR / compas) + 2):
        ch = prog[b % 4]
        i0 = b * compas
        for m in ch[1:]:
            add(out, pad(440 * 2 ** ((m - 69) / 12), compas + 0.6) * 0.12, i0)
        add(out, pad(440 * 2 ** ((ch[0] - 69) / 12), compas + 0.6) * 0.18, i0)
        for k, p in enumerate(arpe):
            m = ch[1 + p % 3] + 12
            add(out, campanita(440 * 2 ** ((m - 69) / 12)), i0 + k * compas / 8, 0.22 if k % 2 == 0 else 0.15)
    return filt(out, 50, 8000)


def add(buf, x, at, g=1.0):
    i = int(at * SR)
    j = min(N, i + len(x))
    if 0 <= i < N:
        buf[i:j] += g * x[: j - i]


v = voz()
m = musica()
envv = np.convolve(np.abs(v), np.ones(int(0.08 * SR)) / int(0.08 * SR), mode="same")
m *= 1.0 - 0.55 * np.clip(envv / 0.15, 0, 1)

fx = np.zeros(N)
add(fx, viento(DUR), 0.0, 0.8)
def rumor(d):
    """El hueco que sale del suelo: rumor grave de máquina que sube."""
    t = tt(d)
    x = filt(ruido(len(t)), 40, 300) * 0.5 + np.sin(2 * np.pi * np.cumsum(45 + 25 * t / d) / SR) * 0.25
    return x * np.minimum(1, t / 0.15) * np.minimum(1, (d - t) / 0.1)


for k in (3, 4, 5, 8, 11):                                         # v3 · el imán de la rana prendido
    a, b = E.T[k]
    add(fx, zumbido_iman(b - a + 0.1), a, 0.7)
for k in (1, 2, 15, 16):                                           # el imán gigante prendido (más grave)
    a, b = E.T[k]
    add(fx, zumbido_iman(b - a + 0.1, 38), a, 0.6)
add(fx, whoom(1.4), 0.0, 0.8)                                      # cuadro 0: Pete flotando
add(fx, ding(1320, 0.6), W("flotar", 3.0), 0.4)
add(fx, whoosh(0.6, True), T(3) - 0.15, 0.6)                       # a la rana real
add(fx, ding(1568, 0.5), W("pasó", 4.0), 0.35)                     # ESTO SÍ PASÓ
add(fx, ding(1320, 0.6), W("sola", 6.0), 0.4)                      # SIN HILOS
add(fx, golpe_grave(), W("imán", 7.0), 0.5)                        # aparece el electroimán
add(fx, whoosh(0.8, True), T(5), 0.6)                              # push-in a la piel
add(fx, ding(1175, 0.5), W("nada", 8.0), 0.3)                      # AGUA
add(fx, ding(988, 0.5), W("como", 9.0), 0.3)                       # como tú
add(fx, glup(), T(7, 0.05), 0.8)                                   # adentro
add(fx, tic(3000), W("empuja", 10.0), 0.9)                         # nace el empujón
add(fx, ding(1568, 0.5), W("poquito", 12.0), 0.35)
add(fx, ding(1046, 0.5), W("fuerte", 14.0), 0.3)                   # ≈ 16 TESLAS
add(fx, whoom(1.4), W("gana", 14.0) - 0.5, 0.8)                    # le gana a la gravedad
add(fx, whoosh(0.9, False), T(9, 0.0), 0.5)                        # la parte hipotética
t_pri = W("primero", 19.0)
add(fx, ding(1175, 0.5), t_pri, 0.35)                              # PASO 1
add(fx, rumor(1.45), t_pri + 0.15, 0.7)                            # el hueco sale del suelo
add(fx, golpe_grave(), t_pri + 1.55, 0.6)
add(fx, tic(2600), W("tres", 22.0), 0.9)                           # la cota
add(fx, golpecito(700), W("mano", 23.0), 0.6)                      # no cabe
add(fx, ding(1175, 0.5), W("después", 25.0), 0.35)                 # PASO 2
bob, carc = E.bobinas_t()
for i, tl in enumerate(bob):                                       # las bobinas que caen
    add(fx, clank(190 + 18 * i), tl, 0.6)
add(fx, golpe_grave(), carc, 0.8)                                  # la carcasa
add(fx, clank(140), carc + 0.02, 0.5)
add(fx, clank(150), T(13, 0.4), 0.8)                               # la tapa
add(fx, ding(1046, 0.7), W("cuarenta", 28.0) + 0.05, 0.4)
add(fx, electrico(1.2), W("teslas", 28.0) - 0.2, 0.6)              # el cobre se enciende
add(fx, ding(1318, 0.6), W("doble", 30.0), 0.35)                   # las barras
add(fx, ding(1175, 0.5), W("final", 32.0), 0.35)                   # PASO 3
add(fx, electrico(E.T[14][1] - E.T[14][0]), T(14), 0.9)            # los cables a la central
add(fx, ding(1568, 0.6), W("entero", 34.0), 0.4)                   # ≈ 1 GIGAVATIO
add(fx, whoom(1.5), T(16, 0.0), 0.9)                               # Pete sube
mix = v * 1.0 + m * 0.45 + fx * 0.45          # música 1 dB más baja: quedaba a 14,9 dB bajo la voz (meta ≥ 15)
mix = np.tanh(mix * 1.1) / 1.1
mix = mix / (np.abs(mix).max() + 1e-9) * 0.9
os.makedirs(OUT, exist_ok=True)
tmp = os.path.join(OUT, "ep05_pre.wav")
wavfile.write(tmp, SR, (mix * 32767).astype(np.int16))
dst = os.path.join(OUT, "ep05_mix.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", dst], check=True)
vr = np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2))
mr = np.sqrt(np.mean((m * 0.45)[(m != 0)] ** 2) + 1e-12)
print("ok audio", dst, "voz/música dB:", round(20 * np.log10(vr / mr), 1))
