"""Audio del Ep. 5: voz + música sintetizada (v3.1: tensión en Re menor, 96 bpm, con golpes en cada paso) con ducking, viento del salar de
fondo (lo que amarra el exterior), zumbido grave del imán en los planos de la rana y los efectos de la columna SFX del
storyboard → OUT/ep07_mix.wav (−14 LUFS, TP ≤ −1,5 dBTP). Todo sintetizado."""
import glob, json, os, subprocess, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ep07 as E

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
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(REPO, os.environ.get("VOZ", "out/tts/ep07-rascacielos-encoge-v2.mp3")), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
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
    # v3.1: más corto y más bajo (con la música nueva, las campanitas sonaban a infantil)
    return (tono(f, d, 0.002, 0.12) + 0.3 * tono(f * 2.01, d, 0.002, 0.06)) * 0.3


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


# ---------------- música v3.1: tensión (Re menor, 96 bpm) ----------------
# Tomás (24-oct 08:14): la música de pads con campanitas "no llama la atención". Ahora: pulso de bajo en corcheas, pad
# oscuro, bombo que entra con la rana y va en negras desde "¿Y para ti?", tics en semicorcheas durante la construcción,
# subidas antes de cada corte grande, golpes en PASO 1/2/3 y un acorde mayor abierto en "Ahí sí… flotarías".
BPM = 96
NEGRA = 60 / BPM
COMPAS = 4 * NEGRA


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def sierra(f, d, k=10):
    """Diente de sierra aditivo (sin aliasing): k armónicos con 1/n."""
    t = tt(d)
    return sum(np.sin(2 * np.pi * f * n * t) / n for n in range(1, k + 1) if f * n < 12000) * 0.6


def pad_oscuro(notas, d, corte=900):
    t = tt(d)
    x = np.zeros(len(t))
    for m in notas:
        for dt in (-0.004, 0.0, 0.005):
            x += sierra(hz(m) * (1 + dt), d, 8)[: len(t)]
    x = filt(x / (3 * len(notas)), 40, corte)
    return x * np.minimum(1, t / 0.4) * np.minimum(1, np.maximum(0, d - t) / 0.4)


def nota_bajo(f, corte, d=None):
    d = d or NEGRA / 2
    n = int(d * SR)
    x = filt(sierra(f, d, 14)[:n], 30, corte)
    return x * env(n, 0.004, 0.16)


def bombo(g=1.0):
    d = 0.4
    x = tono(np.linspace(130, 42, int(d * SR)), d, 0.001, 0.12) * 1.0
    n = int(0.012 * SR)
    x[:n] += filt(ruido(n), 1500, 6000) * 0.4
    return x * g


def tic_hat(abierto=False):
    d = 0.18 if abierto else 0.05
    n = int(d * SR)
    return filt(ruido(n), 7000, None) * env(n, 0.001, 0.06 if abierto else 0.012) * 0.5


def subida(d):
    """Ruido que sube de tono y de volumen hasta el golpe."""
    n = int(d * SR)
    x = ruido(n)
    out = np.zeros(n)
    seg = 1024
    for a in range(0, n, seg):
        b = min(n, a + seg)
        c = 300 + 5200 * (a / n) ** 2
        out[a:b] = filt(x[max(0, a - 4096):b], c * 0.7, c * 1.3)[-(b - a):]
    return out * np.linspace(0, 1, n) ** 2 * 0.7


def golpe(g=1.0, cola=1.6):
    """Impacto de tráiler: bombo + boom de 45 Hz con cola + ráfaga de ruido."""
    n = int(cola * SR)
    x = tono(np.linspace(70, 38, n), cola, 0.002, cola * 0.35) * 1.1
    m = int(0.25 * SR)
    x[:m] += filt(ruido(m), 200, 5000) * env(m, 0.001, 0.05) * 0.8
    b = bombo(1.0)
    x[: len(b)] += b
    return x * g


def musica():
    """Ep. 7: la misma música de tensión del Ep. 5 v3.1 (Re menor, 96 bpm), con la forma de este relato: pulso de bajo
    desde el cuadro 0, bombo desde "El truco", negras desde el PASO 1, tics en semicorcheas mientras desarman, golpes en
    PASO 1/2/3, subida antes de "lo más loco" y un acorde abierto en las luces."""
    out = np.zeros(N)
    t_tr, t_lo, t_lu = E.T[4][0], E.T[12][0], W("prenden", 37.3)
    pasos = [W("Primero", 9.5), W("adentro", 23.5), W("Cuando", 26.5)]
    prog = [(50, 53, 57), (46, 50, 53), (43, 46, 50), (45, 49, 52)]           # Dm Bb Gm A
    raiz = [38, 34, 31, 33]
    nb = int(DUR / COMPAS) + 2
    for b in range(nb):
        i0 = b * COMPAS
        if i0 >= DUR:
            break
        add(out, pad_oscuro(prog[b % 4], COMPAS + 0.5, 700 + 900 * min(1, i0 / t_lo)), i0, 0.5)
    k = 0
    while k * NEGRA / 2 < DUR:
        t = k * NEGRA / 2
        b = int(t / COMPAS) % 4
        corte = 350 + 1400 * min(1.0, t / t_lo)
        g = 0.75 if (k % 2 == 0) else 0.5
        add(out, nota_bajo(hz(raiz[b]), corte), t, g)
        k += 1
    k = 0
    while k * NEGRA < DUR - 0.3:
        t = k * NEGRA
        if t >= pasos[0] or (t >= t_tr and k % 2 == 0):
            add(out, bombo(0.9 if t >= pasos[0] else 0.6), t)
        k += 1
    k = 0
    while k * NEGRA / 4 < DUR - 0.3:
        t = k * NEGRA / 4
        if pasos[1] <= t < E.T[11][0] or t >= t_lo:
            add(out, tic_hat(), t, 0.33 if k % 2 else 0.16)
            if t >= t_lo and k % 4 == 2:
                add(out, tic_hat(True), t, 0.22)
        k += 1
    add(out, golpe(0.7, 1.2), 0.0)
    for tp in pasos:
        add(out, subida(0.45), tp - 0.45, 0.35)
        add(out, golpe(0.8), tp - 0.02)
    add(out, subida(1.8), t_lo - 1.8, 0.55)
    add(out, golpe(1.0, 2.0), t_lo - 0.02)
    add(out, pad_oscuro((50, 54, 57, 62), 2.6, 2400), t_lu, 0.55)            # las luces: Re mayor abierto
    t_si = W("Siete", 40.6)
    add(out, subida(1.4), t_si - 1.4, 0.5)                                     # subida al remate
    add(out, golpe(1.0, 2.2), t_si - 0.02)
    add(out, pad_oscuro((50, 54, 57, 62), DUR - E.T[16][0] + 0.3, 2600), E.T[16][0], 0.7)   # "nadie lo vio caer": acorde abierto, se apaga
    out = filt(out, 30, 9000)
    return out / (np.abs(out).max() + 1e-9)


def add(buf, x, at, g=1.0):
    i = int(at * SR)
    j = min(N, i + len(x))
    if 0 <= i < N:
        buf[i:j] += g * x[: j - i]


v = voz()
m = musica()
envv = np.convolve(np.abs(v), np.ones(int(0.08 * SR)) / int(0.08 * SR), mode="same")
m *= 1.0 - 0.55 * np.clip(envv / 0.15, 0, 1)
if os.environ.get("MUSICA_SOLA"):                 # para revisar la música sin la voz
    os.makedirs(OUT, exist_ok=True)
    wavfile.write(os.path.join(OUT, "musica_sola.wav"), SR, (m / (np.abs(m).max() + 1e-9) * 0.8 * 32767).astype(np.int16))
_vr = np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2))
_mr = np.sqrt(np.mean((m * 0.45)[m != 0] ** 2) + 1e-12)
m *= (_vr / 10 ** (15.0 / 20)) / _mr        # música a 15 dB bajo la voz (mínimo del manual)

fx = np.zeros(N)
import planos_ep07 as PL
add(fx, viento(DUR), 0.0, 0.6)
AFUERA = (1, 2, 3, 8, 11, 14, 15)
for t0, n, d in PL.CLONCS:
    if 0 <= t0 + d < DUR and any(E.T[k][0] <= t0 + d < E.T[k][1] for k in AFUERA) and n == 1:
        add(fx, clank(150), t0 + d - 0.02, 0.55)
add(fx, whoom(1.2), 0.0, 0.7)
add(fx, ding(1046, 0.7), W("alto", 1.0), 0.4)                      # EL MÁS ALTO
add(fx, viento(E.T[3][1] - E.T[3][0]), T(3), 0.9)
add(fx, whoosh(0.5, True), W("explosión", 6.0) - 0.3, 0.4)
add(fx, ding(880, 0.8), W("techo", 8.0), 0.45)
add(fx, pfff(), W("Primero", 9.5) + 0.1, 0.8)
add(fx, clank(190), W("columnas", 10.5), 0.6)                     # columnas de acero
add(fx, ding(1318, 0.6), W("gatos", 12.5), 0.4)                    # 15 GATOS
for i in range(6):
    add(fx, tic(2200), T(6) + 0.3 * i, 0.5)                        # el calendario corre
add(fx, ding(1175, 0.6), W("dos", 16.8), 0.4)                      # 2 MESES
add(fx, zumbido_iman(1.4, 70), W("cierran", 18.0) - 0.2, 0.7)     # los paneles suben
add(fx, clank(130), W("cierran", 18.0) + 1.1, 0.7)
add(fx, ding(1318, 0.6), W("ventanas", 19.3), 0.4)
add(fx, ding(1046, 0.6), W("parece", 22.5), 0.35)
t_es, t_ds = W("escondidos", 24.0), W("desarman", 25.0)
for i in range(8):
    add(fx, tic(1800), t_es + 0.25 + 0.08 * i, 0.35)
    add(fx, golpecito(320), T(9) + 0.5 + 0.45 * i + 0.1, 0.6)
    add(fx, thud(), T(9) + 0.5 + 0.45 * i + 0.9, 0.35)
t_ba, t_pi = W("bajan", 28.0), W("piso", 29.2)
add(fx, zumbido_iman(t_pi - t_ba + 0.2, 62), t_ba, 0.8)
add(fx, golpe_grave(), t_pi - 0.05, 0.8)
add(fx, clank(120), t_pi - 0.03, 0.7)
add(fx, whoosh(1.6, False), W("Como", 31.2), 0.6)
add(fx, ding(1046, 0.6), W("reversa", 32.4), 0.35)
add(fx, electrico(2.0), W("genera", 35.5), 0.8)
add(fx, ding(1568, 0.6), W("electricidad", 36.0), 0.35)
for i in range(6):
    add(fx, tic(2600), W("prenden", 37.3) + 0.2 * i, 0.7)
add(fx, ding(988, 0.5), W("Dos", 39.0), 0.35)
add(fx, whoosh(2.8, False), W("Siete", 40.6) + 0.1, 0.7)           # la torre baja entera
add(fx, ding(1175, 0.7), W("nada", 44.8), 0.4)
add(fx, whoom(1.6), T(16), 0.6)
mix = v * 1.0 + m * 0.45 + fx * 0.45          # música 1 dB más baja: quedaba a 14,9 dB bajo la voz (meta ≥ 15)
mix = np.tanh(mix * 1.1) / 1.1
mix = mix / (np.abs(mix).max() + 1e-9) * 0.9
os.makedirs(OUT, exist_ok=True)
tmp = os.path.join(OUT, "ep07_pre.wav")
wavfile.write(tmp, SR, (mix * 32767).astype(np.int16))
dst = os.path.join(OUT, "ep07_mix.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "alimiter=limit=0.6:level=false,loudnorm=I=-14:TP=-2.5:LRA=11", "-ar", "48000", dst], check=True)
vr = np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2))
mr = np.sqrt(np.mean((m * 0.45)[(m != 0)] ** 2) + 1e-12)
print("ok audio", dst, "voz/música dB:", round(20 * np.log10(vr / mr), 1))
