"""Audio del Ep. 10 (kamikazes; sobre el del Ep. 9): voz + música sintetizada (Re menor lento, 64 bpm: pad oscuro, latido
grave y golpes en los cortes grandes) con ducking, y los efectos de la columna SFX del storyboard (obturador, lámpara,
viento, motores radiales, alarma de zafarrancho, cañones de 20 mm, explosiones, agua, estática de radio) →
OUT/ep10_mix.wav (−14 LUFS, TP ≤ −1,5 dBTP). Todo sintetizado."""
import glob, json, os, subprocess, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ep10 as E

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
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(REPO, os.environ.get("VOZ", "out/tts/ep10-kamikazes.mp3")), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
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


def tic(f=2600):
    return tono(f, 0.06, 0.0008, 0.015) * 0.45


def obturador():
    """Cámara de fotos antigua: clic metálico doble con un resorte."""
    out = np.zeros(int(0.25 * SR))
    for at, f, g in ((0.0, 3200, 0.8), (0.07, 2100, 0.6)):
        n = int(0.05 * SR)
        k = filt(ruido(n), 1500, 7000) * env(n, 0.0005, 0.008) * g + tono(f, 0.05, 0.0005, 0.01) * 0.3 * g
        i = int(at * SR)
        out[i:i + n] += k
    return out


def lampara(d):
    """Mecha de querosén: siseo suave con chisporroteos."""
    n = int(d * SR)
    x = filt(ruido(n), 1500, 6000) * 0.012
    for _ in range(int(d * 3)):
        i = rng.integers(0, max(1, n - 800))
        x[i:i + 800] += filt(ruido(800), 2000, 7000) * np.exp(-np.linspace(0, 8, 800)) * rng.uniform(0.02, 0.06)
    return x


def viento(d, g=1.0):
    n = int(d * SR)
    x = filt(ruido(n), 80, 900) * 0.06 + filt(ruido(n), 900, 4000) * 0.012
    mod = 0.75 + 0.25 * np.sin(2 * np.pi * 0.13 * tt(d)) + 0.15 * np.sin(2 * np.pi * 0.31 * tt(d) + 1.0)
    return x * mod * g


def mar(d, g=1.0):
    """Olas contra el casco: ruido grave que sube y baja."""
    n = int(d * SR)
    x = filt(ruido(n), 60, 700) * 0.08
    return x * (0.6 + 0.4 * np.sin(2 * np.pi * 0.18 * tt(d)) ** 2) * g


def motor(d, f0=26.0, f1=None, g=1.0, cerca=1.0):
    """Motor radial de 14 cilindros: pulso grave de explosiones (f0 = vueltas/s · 7) con armónicos y ruido de hélice.
    f1 cambia el tono a lo largo del sonido (picada / Doppler)."""
    t = tt(d)
    f = np.linspace(f0, f1 or f0, len(t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = sum(np.sin(ph * k) / k ** 0.8 for k in range(1, 18)) * 0.25
    x = np.tanh(x * 1.8) * 0.5
    x += filt(ruido(len(t)), 200, 2500 + 2500 * cerca) * 0.10 * (0.8 + 0.2 * np.sin(ph * 0.5))
    return filt(x, 30, 1800 + 4000 * cerca) * g


def alarma(veces=6):
    """Zafarrancho de combate de la US Navy: bong… bong… metálico, dos por segundo."""
    out = np.zeros(int((veces * 0.5 + 1.0) * SR))
    for i in range(veces):
        b = (tono(560, 0.9, 0.002, 0.35) + 0.6 * tono(560 * 2.4, 0.9, 0.002, 0.2) + 0.3 * tono(560 * 3.9, 0.9, 0.002, 0.1)) * 0.45
        add_local(out, b, i * 0.5)
    return out


def rafaga(d, cadencia=7.5):
    """Cañón de 20 mm: disparos secos a ~450 por minuto, con cola grave."""
    out = np.zeros(int((d + 0.6) * SR))
    k = 0
    while k / cadencia < d:
        n = int(0.35 * SR)
        s = filt(ruido(n), 150, 6000) * env(n, 0.0005, 0.03) * 0.9 + tono(np.linspace(110, 50, n), 0.35, 0.0005, 0.08) * 0.8
        add_local(out, s * rng.uniform(0.8, 1.0), k / cadencia + rng.uniform(0, 0.01))
        k += 1
    return out


def explosion(g=1.0, lejos=0.0):
    n = int(2.2 * SR)
    x = filt(ruido(n), 30, 2500 - 1800 * lejos) * env(n, 0.003 + 0.02 * lejos, 0.5)
    x += tono(np.linspace(60, 28, n), 2.2, 0.002, 0.6) * 1.2
    return np.tanh(x * 1.5) * g


def agua_golpe(g=1.0):
    n = int(1.6 * SR)
    return filt(ruido(n), 300, 5000) * env(n, 0.01, 0.4) * 0.6 * g


def estatica(d, g=1.0):
    """Radio de válvulas: estática con silbidos que van y vienen."""
    t = tt(d)
    x = filt(ruido(len(t)), 800, 6000) * 0.12 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.7 * t))
    x += np.sin(2 * np.pi * np.cumsum(1800 + 700 * np.sin(2 * np.pi * 0.4 * t)) / SR) * 0.015
    return x * np.minimum(1, t / 0.2) * g


def pasos_tierra(n_pasos, cada=0.55):
    out = np.zeros(int((n_pasos * cada + 0.5) * SR))
    for i in range(n_pasos):
        m = int(0.18 * SR)
        s = filt(ruido(m), 200, 2500) * env(m, 0.004, 0.05) * 0.7 + tono(np.linspace(90, 55, m), 0.18, 0.002, 0.04) * 0.4
        add_local(out, s, i * cada)
    return out


def papel(d=0.6):
    n = int(d * SR)
    return filt(ruido(n), 1200, 8000) * (0.4 + 0.6 * np.abs(np.sin(np.linspace(0, 9, n)))) * env(n, 0.05, 0.3) * 0.25


def pincel(d=1.2):
    n = int(d * SR)
    return filt(ruido(n), 2500, 9000) * 0.06 * (0.5 + 0.5 * np.sin(2 * np.pi * 1.6 * tt(d)) ** 2)


def crujido_madera():
    n = int(0.6 * SR)
    x = np.zeros(n)
    for _ in range(6):
        i = rng.integers(0, n - 1500)
        x[i:i + 1500] += filt(ruido(1500), 300, 2200) * np.exp(-np.linspace(0, 7, 1500)) * rng.uniform(0.3, 0.8)
    return x * 0.5


def latido(g=1.0):
    """Lub-dub grave."""
    out = np.zeros(int(0.8 * SR))
    for at, gg in ((0.0, 1.0), (0.24, 0.7)):
        b = tono(np.linspace(65, 40, int(0.3 * SR)), 0.3, 0.003, 0.08) * gg
        add_local(out, b, at)
    return out * g


def add_local(buf, x, at, g=1.0):
    i = int(at * SR)
    j = min(len(buf), i + len(x))
    if 0 <= i < len(buf):
        buf[i:j] += g * x[: j - i]


# ---------------- música: Re menor lento (64 bpm) ----------------
BPM = 64
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


def agua_corre(d, g=1.0, hi=900):
    """Rugido de agua (ruido grave filtrado con pulsos lentos)."""
    n = int(d * SR)
    x = filt(ruido(n), 60, hi)
    lfo = 0.75 + 0.25 * np.sin(np.linspace(0, d * 2 * np.pi * 0.7, n))
    e = np.minimum(1, np.linspace(0, d / 0.25, n)) * np.minimum(1, np.linspace(d / 0.4, 0, n))
    return x * lfo * e * g


def crujido(d=0.9):
    """Hielo que cruje: chasquidos secos sobre un gemido grave."""
    n = int(d * SR)
    x = np.zeros(n)
    for _ in range(14):
        i = rng.integers(0, max(1, n - 2000))
        k = filt(ruido(1800), 900, 5000) * np.exp(-np.linspace(0, 9, 1800))
        x[i:i + 1800] += k * rng.uniform(0.3, 1.0)
    gem = np.sin(2 * np.pi * np.cumsum(np.linspace(70, 48, n)) / SR) * env(n, 0.05, d * 0.8)
    return x * 0.8 + gem * 0.5


def tintineo():
    """Hielo contra vidrio."""
    a = tono(2350, 0.5, 0.001, 0.12) * 0.6
    a[: int(0.4 * SR)] += tono(3170, 0.4, 0.001, 0.08) * 0.4
    return a


def musica():
    """Ep. 10: Re menor lento (64 bpm). Pad oscuro desde el cuadro 0; latido grave en negras desde el mapa (plano 4);
    pulso de bajo que se aprieta en el ataque (11–16) y corta a silencio en el blanco del 16; vuelve en el mapa;
    se apaga en "Ese miedo" (24) y deja un acorde abierto y triste en el remate (26–27)."""
    out = np.zeros(N)
    t_ma, t_at, t_bl, t_vu, t_mi, t_fi = T(4), T(11), T(16, 1.45), T(17), T(24), T(26)
    prog = [(50, 53, 57), (46, 50, 53), (43, 46, 50), (45, 49, 52)]           # Dm Bb Gm A
    raiz = [38, 34, 31, 33]
    nb = int(DUR / COMPAS) + 2
    for b in range(nb):
        i0 = b * COMPAS
        if i0 >= DUR:
            break
        if t_bl <= i0 + COMPAS and i0 < t_vu:
            continue
        g = 0.5 if i0 < t_mi else 0.25
        add(out, pad_oscuro(prog[b % 4], COMPAS + 0.5, 600 + 700 * (t_at <= i0 < t_bl)), i0, g)
    k = 0
    while k * NEGRA / 2 < DUR:
        t = k * NEGRA / 2
        b = int(t / COMPAS) % 4
        if (t_at <= t < t_bl) or (t_vu <= t < t_mi):
            add(out, nota_bajo(hz(raiz[b]), 900 if t < t_bl else 600), t, 0.7 if k % 2 == 0 else 0.45)
        k += 1
    k = 0
    while k * NEGRA < DUR - 0.3:
        t = k * NEGRA
        if t_ma <= t < t_at or t_vu <= t < t_mi:
            add(out, bombo(0.45), t)
        elif t_at <= t < t_bl:
            add(out, bombo(0.8), t)
            add(out, bombo(0.5), t + NEGRA / 2)
        k += 1
    add(out, golpe(0.6, 1.4), T(4) - 0.02)                                     # la guerra
    add(out, golpe(0.5, 1.2), T(6) - 0.02)                                     # voluntarios
    add(out, subida(1.0), t_at - 1.0, 0.4)
    add(out, golpe(0.9, 1.6), t_at - 0.02)                                     # los estadounidenses
    add(out, golpe(0.8, 1.6), T(17) - 0.02)                                    # Okinawa
    add(out, golpe(0.7, 1.6), T(20) - 0.02)                                    # trece mil aviones
    add(out, pad_oscuro((50, 57, 62, 65), DUR - t_fi + 0.3, 1800), t_fi, 0.6)   # remate: acorde abierto (loop)
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


def Wk(prefix, k):
    """Primera palabra con ese prefijo desde el inicio del plano k (los tiempos cambian con la voz)."""
    return W(prefix, T(k) - 0.3)


add(fx, obturador(), 0.02, 0.9)                                                # la foto
add(fx, lampara(T(3)), 0.0, 1.0)
add(fx, papel(0.5), T(2) + 0.1, 0.6)
add(fx, viento(T(4) - T(3) + 0.3), T(3), 0.9)
add(fx, motor(1.8, 22, 24, 0.35, 0.2), T(3) + 0.1, 1.0)                       # un motor que arranca a lo lejos
add(fx, viento(T(9) - T(5)), T(5), 0.7)
add(fx, motor(T(6) - T(5), 30, 44, 0.9, 0.6), T(5), 1.0)                       # el avión acelera y despega
add(fx, whoosh(0.6, False), T(5) + 1.2, 0.5)
add(fx, pasos_tierra(2, 0.5), T(6) + 0.5, 0.5)                                 # el oficial
add(fx, pasos_tierra(4, 0.08), T(7) + 0.3, 0.8)                                # la fila da el paso
add(fx, pasos_tierra(1), T(8) + 0.6, 1.0)                                      # el último
add(fx, lampara(T(11) - T(9)), T(9), 1.0)
add(fx, pincel(1.4), T(9) + 0.3, 1.0)
add(fx, crujido_madera(), T(10) + 0.4, 0.8)
add(fx, alarma(5), T(11) - 0.1, 0.55)                                          # zafarrancho
add(fx, mar(T(17) - T(11)), T(11), 0.8)
add(fx, viento(T(17) - T(11), 0.8), T(11), 0.8)
add(fx, motor(T(13) - T(12) + 0.1, 30, 46, 0.9, 0.5), T(12), 1.0)              # picada: el tono sube
add(fx, rafaga(T(14) - T(13) + 0.3), T(13), 0.75)
add(fx, rafaga(T(15) - T(14), 6.0), T(14), 0.35)
add(fx, explosion(0.6, 0.7), T(14) + 0.75, 1.0)
add(fx, agua_golpe(0.8), T(14) + 0.8, 1.0)
add(fx, explosion(0.4, 0.9), T(14) + 1.35, 1.0)
add(fx, motor(T(16) - T(15), 40, 48, 0.9, 0.8), T(15), 1.0)                    # sale del humo
add(fx, motor(T(16, 1.45) - T(16), 48, 62, 1.1, 1.0), T(16), 1.0)              # al máximo
add(fx, explosion(1.2, 0.3), T(16, 1.45), 1.0)                                 # golpe sordo (el blanco) y silencio
add(fx, mar(T(18) - T(17)), T(17) + 0.4, 0.8)
for i in range(3):
    add(fx, tono(np.linspace(500, 760, int(0.9 * SR)), 0.9, 0.2, 0.6) * 0.25, T(17) + 0.3 + 0.95 * i, 0.5)   # sirena lejana
for i in range(8):
    add(fx, tic(2400 + 120 * i), T(18) + 0.2 + 0.15 * i, 0.5)                  # las barras
add(fx, motor(T(21) - T(20), 24, 24, 0.35, 0.3), T(20), 1.0)                    # murmullo de motores
add(fx, motor(T(21) - T(20), 27, 27, 0.25, 0.3), T(20) + 0.2, 1.0)
add(fx, viento(T(22) - T(21)), T(21), 1.0)
add(fx, whoosh(0.8, True), T(21) + 0.3, 0.4)
add(fx, latido(0.9), T(22) + 0.2, 1.0)
add(fx, latido(0.9), T(22) + 1.1, 1.0)
add(fx, latido(1.1), T(23) + 0.1, 1.0)
add(fx, latido(1.1), T(23) + 0.9, 1.0)
add(fx, explosion(0.7, 1.0), T(25) + 0.1, 1.0)                                 # Hiroshima (apagado, lejos)
add(fx, explosion(0.7, 1.0), T(25) + 0.8, 1.0)                                 # Nagasaki
add(fx, estatica(T(27) - T(26) + 0.2), T(26), 0.9)
add(fx, lampara(T(27) - T(26)), T(26), 1.0)
add(fx, viento(DUR - T(27)), T(27), 0.8)
add(fx, motor(DUR - T(27), 34, 30, 0.7, 0.5) * np.linspace(1, 0.2, int((DUR - T(27)) * SR)), T(27), 1.0)   # se alejan
add(fx, obturador(), E.T[27][1] - 0.32, 0.9)                                    # loop: vuelve la foto
mix = v * 1.0 + m * 0.45 + fx * 0.45          # música 1 dB más baja: quedaba a 14,9 dB bajo la voz (meta ≥ 15)
mix = np.tanh(mix * 1.1) / 1.1
mix = mix / (np.abs(mix).max() + 1e-9) * 0.9
os.makedirs(OUT, exist_ok=True)
tmp = os.path.join(OUT, "ep10_pre.wav")
wavfile.write(tmp, SR, (mix * 32767).astype(np.int16))
dst = os.path.join(OUT, "ep10_mix.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "alimiter=limit=0.6:level=false,loudnorm=I=-14:TP=-2.5:LRA=11", "-ar", "48000", dst], check=True)
vr = np.sqrt(np.mean(v[np.abs(v) > 0.02] ** 2))
mr = np.sqrt(np.mean((m * 0.45)[(m != 0)] ** 2) + 1e-12)
print("ok audio", dst, "voz/música dB:", round(20 * np.log10(vr / mr), 1))
