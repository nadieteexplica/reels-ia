"""Audio del Ep. 10d: voz + música sintetizada con empuje (Re menor a 84 bpm: pad, bajo en corcheas, bombo y hi-hat desde el
"pero", corte en seco en "Volvió vivo") + efectos (golpes de bambú, sellos, motores, papel, grillos) → <salida>/mix.wav a −14 LUFS."""
import os, subprocess, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else AQUI
sys.argv = sys.argv[:1]
sys.path.insert(0, AQUI)
import video as VV

SR = 48000
DUR = VV.DUR
N = int(DUR * SR)
rng = np.random.default_rng(10)
T, tw = VV.T, VV.tw


def filt(x, lo=None, hi=None):
    if lo and hi:
        return sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), x)
    if lo:
        return sosfilt(butter(2, lo, btype="high", fs=SR, output="sos"), x)
    return sosfilt(butter(2, hi, btype="low", fs=SR, output="sos"), x)


def tt(d):
    return np.arange(int(d * SR)) / SR


def env(n, a=0.004, d=0.1):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def tono(f, d, a=0.003, dec=0.2):
    t = tt(d)
    ph = 2 * np.pi * np.cumsum(np.broadcast_to(np.asarray(f, float), t.shape)) / SR if np.ndim(f) else 2 * np.pi * f * t
    return np.sin(ph) * env(len(t), a, dec)


def add(buf, x, at, g=1.0):
    i = int(at * SR)
    if i < 0:
        x = x[-i:]; i = 0
    j = min(len(buf), i + len(x))
    if i < len(buf):
        buf[i:j] += g * x[: j - i]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def sierra(f, d, k=8):
    t = tt(d)
    return sum(np.sin(2 * np.pi * f * n * t) / n for n in range(1, k + 1) if f * n < 12000) * 0.6


def pad(notas, d, corte=900):
    t = tt(d)
    x = np.zeros(len(t))
    for m in notas:
        for dt in (-0.004, 0.0, 0.005):
            x += sierra(hz(m) * (1 + dt), d)[: len(t)]
    x = filt(x / (3 * len(notas)), 40, corte)
    return x * np.minimum(1, t / 0.3) * np.minimum(1, np.maximum(0, d - t) / 0.3)


def golpe(g=1.0, cola=1.4):
    n = int(cola * SR)
    x = tono(np.linspace(72, 38, n), cola, 0.002, cola * 0.3) * 1.1
    m = int(0.25 * SR)
    x[:m] += filt(rng.standard_normal(m), 200, 5000) * env(m, 0.001, 0.05) * 0.6
    return x * g


def bambu(g=1.0):
    """Golpe seco de shinai: zumbido corto antes + chasquido."""
    n = int(0.5 * SR)
    out = np.zeros(n + int(0.15 * SR))
    w = int(0.15 * SR)
    sw = filt(rng.standard_normal(w), 600, 3000) * np.linspace(0, 1, w) ** 2 * 0.5
    add(out, sw, 0.0)
    c = filt(rng.standard_normal(n), 1500, 9000) * env(n, 0.0005, 0.03) * 1.4
    c += tono(np.linspace(260, 120, n), 0.5, 0.0005, 0.05) * 0.8
    add(out, c, 0.15)
    return out * g


def sello(g=1.0):
    n = int(0.6 * SR)
    x = tono(np.linspace(110, 50, n), 0.6, 0.001, 0.09) * 1.2 + filt(rng.standard_normal(n), 300, 3000) * env(n, 0.001, 0.03) * 0.8
    return x * g


def latido(g=1.0):
    out = np.zeros(int(0.8 * SR))
    for at, gg in ((0.0, 1.0), (0.24, 0.7)):
        add(out, tono(np.linspace(65, 40, int(0.3 * SR)), 0.3, 0.003, 0.08) * gg, at)
    return out * g


def viento(d, g=1.0):
    n = int(d * SR)
    x = filt(rng.standard_normal(n), 80, 900) * 0.06 + filt(rng.standard_normal(n), 900, 4000) * 0.012
    return x * (0.75 + 0.25 * np.sin(2 * np.pi * 0.13 * tt(d))) * g


def motor(d, f0, f1, g=1.0, tos=None):
    t = tt(d)
    f = np.linspace(f0, f1, len(t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.tanh(sum(np.sin(ph * k) / k ** 0.8 for k in range(1, 16)) * 0.45) * 0.5
    x += filt(rng.standard_normal(len(t)), 200, 4000) * 0.08
    x = filt(x, 30, 5000) * np.minimum(1, t / 0.15)
    if tos is not None:        # el motor tose y se apaga desde `tos` s
        m = np.ones(len(t))
        i0 = int(tos * SR)
        tm = t[i0:] - tos
        m[i0:] = (np.sin(2 * np.pi * 5 * tm) > -0.2) * np.exp(-tm / 0.9)
        x = x * sosfilt(butter(1, 30, fs=SR, output="sos"), m)
    return x * g


def flak(d, g=1.0):
    out = np.zeros(int((d + 1.0) * SR))
    for k in range(int(d * 5)):
        n = int(0.6 * SR)
        s = filt(rng.standard_normal(n), 60, 1500) * env(n, 0.002, 0.15) + tono(np.linspace(80, 40, n), 0.6, 0.002, 0.12) * 0.6
        add(out, s * rng.uniform(0.4, 1.0), k / 5 + rng.uniform(0, 0.1))
    return out * g


def papel(d=0.6):
    n = int(d * SR)
    return filt(rng.standard_normal(n), 1200, 8000) * (0.4 + 0.6 * np.abs(np.sin(np.linspace(0, 9, n)))) * env(n, 0.05, 0.3) * 0.25


def lapiz(d=0.35):
    n = int(d * SR)
    return filt(rng.standard_normal(n), 2000, 7000) * (0.5 + 0.5 * np.sin(np.linspace(0, 40, n)) ** 2) * np.hanning(n) * 0.3


def grillos(d):
    t = tt(d)
    x = np.sin(2 * np.pi * 4300 * t) * (np.sin(2 * np.pi * 28 * t) > 0.3) * ((t * 1.6) % 1 < 0.35)
    return filt(x, 3000, 6000) * 0.05


def campana(g=1.0):
    d = 2.5
    return (tono(660, d, 0.002, 0.9) + 0.5 * tono(1320 * 1.003, d, 0.002, 0.6) + 0.25 * tono(1980, d, 0.002, 0.4)) * g * 0.4


def whoosh(d=0.35, g=1.0):
    n = int(d * SR)
    return filt(rng.standard_normal(n), 400, 5000) * np.hanning(n) * 0.35 * g


# ---------------------------------------------------------------- voz
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.abspath(os.path.join(AQUI, "../../../../out/tts/ep10d-kamikaze-vivo.mp3")),
                      "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
v = np.frombuffer(raw, np.float32).copy()
v = np.pad(v, (0, max(0, N - len(v))))[:N]
v = v / (np.abs(v).max() + 1e-9) * 0.9

# ---------------------------------------------------------------- música
BPM = 84
NEG = 60 / BPM
COMP = 4 * NEG
prog = [(50, 53, 57), (46, 50, 53), (43, 46, 50), (45, 49, 52)]
raiz = [38, 34, 31, 33]
m = np.zeros(N)
t_pero = T[12][0]            # "Pero él tenía miedo": entra el ritmo
t_corte0, t_corte1 = T[27][0], T[28][0]     # "Volvió vivo": silencio
for b in range(int(DUR / COMP) + 1):
    add(m, pad(prog[b % 4], COMP + 0.4, 800), b * COMP, 0.5)
k = 0
while k * NEG / 2 < DUR:
    t = k * NEG / 2
    if T[2][0] <= t and not (t_corte0 <= t < t_corte1):
        n = int(NEG / 2 * SR)
        r = raiz[int(t / COMP) % 4]
        add(m, filt(sierra(hz(r), NEG / 2, 12)[:n], 30, 700) * env(n, 0.004, 0.14), t, 0.7 if k % 2 == 0 else 0.45)
        if t >= t_pero:
            if k % 2 == 0:
                add(m, tono(np.linspace(110, 42, int(0.25 * SR)), 0.25, 0.001, 0.07) * 1.3, t)      # bombo en negras
            hn = int(0.05 * SR)
            add(m, filt(rng.standard_normal(hn), 7000, 14000) * env(hn, 0.0005, 0.012), t + NEG / 4, 0.35)  # hi-hat a contratiempo
    k += 1
for t0 in (T[2][0], T[6][0], T[12][0], T[18][0], T[25][0], T[28][0], T[31][0]):
    add(m, golpe(0.7), t0 - 0.02)
# el silencio de "Volvió vivo": se apaga todo (también el pad)
i0, i1 = int(t_corte0 * SR), int(t_corte1 * SR)
fade = int(0.04 * SR)
gate = np.ones(N)
gate[i0:i1] = 0.0
gate[i0 - fade:i0] = np.linspace(1, 0, fade)
gate[i1:i1 + fade] = np.linspace(0, 1, fade)
m = filt(m, 30, 10000) * gate
m /= np.abs(m).max() + 1e-9
envv = np.convolve(np.abs(v), np.ones(int(0.08 * SR)) / int(0.08 * SR), mode="same")
m *= 1.0 - 0.5 * np.clip(envv / 0.15, 0, 1)
vr = np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2)); mr = np.sqrt(np.mean((m * 0.45)[m != 0] ** 2) + 1e-12)
m *= (vr / 10 ** (13.0 / 20)) / mr

# ---------------------------------------------------------------- efectos
fx = np.zeros(N)
add(fx, viento(T[2][0] + 0.5), 0.0, 0.8)
add(fx, bambu(1.0), VV.T_GOLPE1 - 0.15)
add(fx, sello(1.0), VV.T_VIVO1)
add(fx, motor(T[5][0] - T[3][0], 30, 50, 0.55), T[3][0])
add(fx, flak(T[5][0] - T[3][0], 0.4), T[3][0] + 0.2)
add(fx, whoosh(0.3), T[7][0] - 0.15, 0.8)
add(fx, whoosh(0.25), tw("pecado") - 0.1, 0.9)
add(fx, latido(0.9), T[12][0] + 0.05); add(fx, latido(0.8), T[13][0] + 0.1)
add(fx, papel(0.5), T[14][0] + 0.05, 0.6)
add(fx, grillos(T[16][0] - T[15][0] + 0.3), T[15][0])
add(fx, viento(T[16][0] - T[15][0], 0.5), T[15][0])
add(fx, papel(0.4), T[16][0], 0.6)
for w in ("Sí", "con", "todo", "mi", "corazón"):
    add(fx, lapiz(0.3), tw(w, 26), 0.8)
add(fx, whoosh(0.25), T[17][0] - 0.1, 0.7)
add(fx, sello(1.0), VV.T_COBARDE)
add(fx, whoosh(0.4), T[19][0] + 0.05, 0.8)
add(fx, sello(0.9), VV.T_FAMILIA)
add(fx, motor(T[21][0] - T[20][0], 24, 24, 0.35, tos=0.4), T[20][0])
add(fx, motor(T[22][0] - T[21][0] + 0.3, 30, 52, 0.5), T[21][0])
add(fx, motor(T[24][0] - T[23][0], 26, 28, 0.25), T[23][0])
add(fx, motor(T[25][0] - T[24][0] + 0.2, 30, 46, 0.35), T[24][0])
add(fx, motor(T[26][0] - T[25][0], 40, 40, 0.5, tos=tw("pero", 41.0) - T[25][0]), T[25][0])
add(fx, viento(T[27][0] - T[26][0], 0.9), T[26][0])
add(fx, golpe(0.6, 1.0), T[26][0] + 1.45)
add(fx, sello(1.2), VV.T_VIVO2)
add(fx, bambu(1.0), VV.T_PEGA1 - 0.15)
add(fx, bambu(0.9), VV.T_PEGA2 - 0.15)
add(fx, campana(1.0), T[29][0] + 0.05)
add(fx, sello(0.8), tw("muerte") + 0.05)
add(fx, sello(1.1), tw("volver", 53.5))
add(fx, golpe(0.6, 1.8), tw("volver", 53.5) + 0.02)

mix = v + m * 0.5 + fx * 0.5
mix = np.tanh(mix * 1.1) / 1.1
mix = mix / (np.abs(mix).max() + 1e-9) * 0.9
os.makedirs(OUT, exist_ok=True)
tmp = os.path.join(OUT, "pre.wav")
wavfile.write(tmp, SR, (mix * 32767).astype(np.int16))
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "alimiter=limit=0.6:level=false,loudnorm=I=-14:TP=-2.0:LRA=11",
                "-ar", "48000", os.path.join(OUT, "mix.wav")], check=True)
print("ok audio", os.path.join(OUT, "mix.wav"))
