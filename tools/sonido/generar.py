"""Biblioteca propia de efectos (SFX) de El viejo del dato: todo sintetizado acá, así que es CC0 por construcción.

Uso:
    .venv/bin/python tools/sonido/generar.py              # arma tools/sonido/biblioteca/*.wav + catalog.json
    .venv/bin/python tools/sonido/generar.py --verificar  # además compara el loudness propio con ffmpeg ebur128
    .venv/bin/python tools/sonido/generar.py --solo pop,ding

Cada efecto es una función con semilla fija: regenerar da exactamente los mismos archivos.
Todos salen a 48 kHz, 16 bits, mono (o estéreo los de movimiento, tensión y ambiente), normalizados a −20 LUFS
integrados (medidos con tools/sonido/medir.py, BS.1770-4) con techo de −1,5 dBTP. Si un golpe muy corto no llega a
−20 LUFS sin pasar el techo, se le aplica un limitador suave de hasta 4 dB y lo que falte queda bajo −20:
el catálogo anota el loudness real de cada clip.
Al regenerar se respeta el campo "usado_en" que ya tenía el catálogo.
"""
import argparse
import os
import sys

import numpy as np
from scipy.ndimage import minimum_filter1d, uniform_filter1d
from scipy.io import wavfile
from scipy.signal import fftconvolve, lfilter

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import medir  # noqa: E402

SR = medir.SR
BIB = os.path.join(AQUI, "biblioteca")
OBJETIVO_LUFS = -20.0
TECHO_DBTP = -1.5
MAX_LIMITE_DB = 4.0
FUENTE = "sintetizado por tools/sonido/generar.py"
LICENCIA = "CC0 1.0 — propio"

# ------------------------------------------------------------------ herramientas de síntesis


def tiempo(d):
    return np.arange(int(round(d * SR))) / SR


def ruido(n, rng):
    return rng.standard_normal(n)


def ruido_rosa(n, rng):
    """Ruido rosa (−3 dB/oct) por forma espectral con FFT."""
    x = rng.standard_normal(n)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = f[1]
    X /= np.sqrt(f / 20.0)
    y = np.fft.irfft(X, n)
    return y / (np.std(y) + 1e-12)


def biquad(tipo, f, q=0.707):
    """Coeficientes RBJ (cookbook). tipo: lp, hp, bp, peak."""
    f = float(np.clip(f, 10, SR * 0.47))
    w0 = 2 * np.pi * f / SR
    c, s = np.cos(w0), np.sin(w0)
    al = s / (2 * q)
    if tipo == "lp":
        b = [(1 - c) / 2, 1 - c, (1 - c) / 2]
    elif tipo == "hp":
        b = [(1 + c) / 2, -(1 + c), (1 + c) / 2]
    elif tipo == "bp":
        b = [al, 0.0, -al]
    else:
        raise ValueError(tipo)
    a = [1 + al, -2 * c, 1 - al]
    return np.array(b) / a[0], np.array(a) / a[0]


def filtro(x, tipo, f, q=0.707, orden=1):
    for _ in range(orden):
        b, a = biquad(tipo, f, q)
        x = lfilter(b, a, x)
    return x


def barrido(x, frecs, tipo="bp", q=1.0, bloque=128):
    """Filtro con frecuencia que cambia en el tiempo (frecs: arreglo del largo de x), por bloques con estado."""
    y = np.zeros_like(x)
    zi = np.zeros(2)
    for i in range(0, len(x), bloque):
        seg = x[i:i + bloque]
        b, a = biquad(tipo, frecs[min(i + bloque // 2, len(x) - 1)], q)
        y[i:i + bloque], zi = lfilter(b, a, seg, zi=zi)
    return y


def curva_log(f0, f1, n, forma=1.0):
    u = np.linspace(0, 1, n) ** forma
    return f0 * (f1 / f0) ** u


def seno_glide(frecs, fase0=0.0):
    return np.sin(fase0 + 2 * np.pi * np.cumsum(frecs) / SR)


def decae(t, tau, ataque=0.001):
    return (1 - np.exp(-t / max(ataque, 1e-5))) * np.exp(-t / tau)


def sierra(frecs, armonicos=8):
    fase = 2 * np.pi * np.cumsum(frecs) / SR
    y = np.zeros_like(fase)
    for k in range(1, armonicos + 1):
        y += np.sin(k * fase) / k
    return y * 0.6


def reverb(x, rt=0.3, mezcla=0.12, brillo=6000, predelay=0.008, semilla=1, estereo=False):
    """Sala corta por convolución con una respuesta de ruido que decae (RT60 = rt). Agrega la cola."""
    rng = np.random.default_rng(semilla)
    n = int(rt * SR)
    t = np.arange(n) / SR
    canales = 2 if estereo else 1

    def ir():
        h = rng.standard_normal(n) * np.exp(-6.9 * t / rt)
        h = filtro(h, "lp", brillo)
        h = np.concatenate([np.zeros(int(predelay * SR)), h])
        return h / np.sqrt(np.sum(h ** 2) + 1e-12)

    x2 = medir.como_2d(x).copy()
    f = min(int(0.01 * SR), len(x2) // 4)
    x2[-f:] *= np.linspace(1, 0, f)[:, None]          # el seco nunca termina de golpe (evita el click final)
    if x2.shape[1] == 1 and canales == 2:
        x2 = np.repeat(x2, 2, axis=1)
    out = []
    for ch in range(x2.shape[1]):
        h = ir()
        wet = fftconvolve(x2[:, ch], h)
        dry = np.concatenate([x2[:, ch], np.zeros(len(wet) - len(x2))])
        out.append(dry + mezcla * wet)
    y = np.stack(out, axis=1)
    return y[:, 0] if y.shape[1] == 1 else y


def paneo(x, pos):
    """Paneo de potencia constante; pos en [−1, 1] (escalar o arreglo)."""
    ang = (np.asarray(pos) + 1) * np.pi / 4
    return np.stack([x * np.cos(ang), x * np.sin(ang)], axis=1)


def poner(dst, src, t):
    i = int(round(t * SR))
    j = min(len(dst), i + len(src))
    if j > i:
        dst[i:j] += src[:j - i]
    return dst


def envolvente_pico(t, d, pico_rel, subida=2.0, bajada=1.5):
    tp = d * pico_rel
    e = np.where(t < tp, (t / tp) ** subida, np.clip(1 - (t - tp) / (d - tp), 0, 1) ** bajada)
    return e


# ------------------------------------------------------------------ catálogo de sonidos

SONIDOS = {}


def sonido(id_, categoria, tags, descripcion, semilla):
    def deco(fn):
        SONIDOS[id_] = dict(fn=fn, categoria=categoria, tags=tags, descripcion=descripcion, semilla=semilla)
        return fn
    return deco


def _whoosh(rng, d, f_ini, f_pico, f_fin, pico_rel, q, pan=(-0.6, 0.6), rt=0.4):
    t = tiempo(d)
    n = len(t)
    e = envolvente_pico(t, d, pico_rel)
    ip = int(n * pico_rel)
    fr = np.concatenate([curva_log(f_ini, f_pico, ip, 0.8), curva_log(f_pico, f_fin, n - ip, 1.2)])
    x = ruido_rosa(n, rng)
    cuerpo = barrido(x, fr, "bp", q)
    aire = filtro(ruido(n, rng), "hp", 3500) * 0.12
    soplo = filtro(ruido_rosa(n, rng), "lp", 220, orden=2) * 0.6
    y = (cuerpo + aire + soplo * e ** 0.5) * e
    st = paneo(y, np.linspace(pan[0], pan[1], n))
    return reverb(st, rt=rt, mezcla=0.15, brillo=5000, semilla=int(rng.integers(1e6)), estereo=True)


@sonido("whoosh-suave", "motion", ["whoosh", "transicion", "entra", "cambio de plano"],
        "soplido suave de 0,75 s, de izquierda a derecha", 101)
def whoosh_suave(rng):
    return _whoosh(rng, 0.75, 350, 1600, 600, 0.55, 1.0)


@sonido("whoosh-rapido", "motion", ["whoosh", "rapido", "corte", "zoom"],
        "pasada corta y brillante de 0,32 s", 102)
def whoosh_rapido(rng):
    return _whoosh(rng, 0.32, 600, 4500, 1500, 0.4, 1.4, pan=(-0.4, 0.5), rt=0.3)


@sonido("whoosh-reverso", "motion", ["whoosh", "reverso", "aspira", "antes de un golpe"],
        "aire que se aspira y corta seco al final (0,9 s); se alinea por el final", 103)
def whoosh_reverso(rng):
    d = 0.9
    t = tiempo(d)
    n = len(t)
    u = t / d
    x = barrido(ruido_rosa(n, rng), curva_log(300, 6000, n, 1.6), "bp", 0.9)
    x += filtro(ruido_rosa(n, rng), "lp", 300) * 0.5
    x += seno_glide(curva_log(110, 240, n)) * 0.12
    y = x * u ** 2.5
    y[-int(0.006 * SR):] *= np.linspace(1, 0, int(0.006 * SR))
    st = paneo(y, np.linspace(0.5, -0.1, n))
    # sala al revés: la reverb se aplica al clip invertido y se vuelve a invertir, así la cola queda ANTES
    st = reverb(st[::-1], rt=0.5, mezcla=0.2, semilla=7, estereo=True)[::-1]
    return st


@sonido("swoosh-sube", "motion", ["swoosh", "sube", "aparece", "crece"],
        "pasada que sube de tono (0,5 s), con un leve silbido tonal", 104)
def swoosh_sube(rng):
    d = 0.5
    t = tiempo(d)
    n = len(t)
    e = envolvente_pico(t, d, 0.7, 1.6, 1.2)
    x = barrido(ruido_rosa(n, rng), curva_log(500, 6000, n), "bp", 1.2)
    x += seno_glide(curva_log(320, 960, n)) * 0.25
    st = paneo(x * e, np.linspace(-0.2, 0.4, n))
    return reverb(st, rt=0.35, mezcla=0.15, semilla=11, estereo=True)


@sonido("swoosh-baja", "motion", ["swoosh", "baja", "sale", "cae"],
        "pasada que baja de tono (0,5 s)", 105)
def swoosh_baja(rng):
    d = 0.5
    t = tiempo(d)
    n = len(t)
    e = envolvente_pico(t, d, 0.3, 1.2, 1.8)
    x = barrido(ruido_rosa(n, rng), curva_log(6000, 500, n), "bp", 1.2)
    x += seno_glide(curva_log(960, 280, n)) * 0.25
    st = paneo(x * e, np.linspace(0.4, -0.2, n))
    return reverb(st, rt=0.35, mezcla=0.15, semilla=12, estereo=True)


@sonido("papel", "motion", ["papel", "desliza", "hoja", "carta", "entra un papel"],
        "hoja que se desliza sobre una mesa (0,6 s)", 106)
def papel(rng):
    d = 0.6
    t = tiempo(d)
    n = len(t)
    e = envolvente_pico(t, d, 0.4, 1.5, 1.3)
    base = filtro(filtro(ruido(n, rng), "hp", 1200, orden=2), "lp", 9000)
    grano = 0.55 + 0.45 * uniform_filter1d(rng.random(n), int(0.012 * SR))
    base = barrido(base * grano, curva_log(2200, 4200, n), "bp", 0.6) * 1.4 + base * 0.3
    crujidos = np.zeros(n)
    for i in np.flatnonzero(rng.random(n) < 120 / SR):
        crujidos = poner(crujidos, rng.choice([-1, 1]) * decae(tiempo(0.004), 0.0008, 0.0001), i / SR)
    crujidos = filtro(crujidos, "bp", 4000, 1.0)
    y = (base + crujidos * 3.0) * e
    return paneo(y, np.linspace(-0.25, 0.25, n))


def _pop(rng, f_ini, f_fin, tau_tono, tau, d=0.25):
    t = tiempo(d)
    f = f_fin + (f_ini - f_fin) * np.exp(-t / tau_tono)
    y = seno_glide(f) * decae(t, tau, 0.0008)
    clic = filtro(ruido(len(t), rng), "hp", 2000) * decae(t, 0.0015, 0.0001) * 0.3
    return reverb(y + clic, rt=0.25, mezcla=0.08, semilla=int(rng.integers(1e6)))


@sonido("pop", "emphasis", ["pop", "aparece", "burbuja", "reveal"], "pop redondo (tono que cae 950→300 Hz)", 201)
def pop(rng):
    return _pop(rng, 950, 300, 0.012, 0.035)


@sonido("pop-grave", "emphasis", ["pop", "grave", "aparece algo grande"], "pop grave y gordo", 202)
def pop_grave(rng):
    return _pop(rng, 600, 180, 0.015, 0.05, 0.3)


@sonido("pop-agudo", "emphasis", ["pop", "agudo", "chico", "pildora", "texto"], "pop chico y agudo", 203)
def pop_agudo(rng):
    return _pop(rng, 1600, 600, 0.008, 0.025, 0.2)


@sonido("reveal-brillo", "emphasis", ["reveal", "brillo", "magia", "aparece", "dato"],
        "pop agudo + arpegio de brillitos (0,9 s)", 204)
def reveal_brillo(rng):
    d = 0.9
    y = np.zeros(int(d * SR))
    poner(y, _pop(rng, 1600, 600, 0.008, 0.025, 0.2) * 0.8, 0)
    for k, f in enumerate([2093.0, 2637.0, 3136.0, 4186.0]):
        t = tiempo(0.6)
        p = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.003 * t)) * decae(t, 0.18, 0.002)
        poner(y, p * 0.35 * (0.85 ** k), 0.02 + 0.045 * k)
    return reverb(y, rt=0.6, mezcla=0.25, brillo=9000, semilla=21, estereo=False)


@sonido("click-ui", "ui", ["click", "boton", "interfaz", "toca"], "click limpio de interfaz", 301)
def click_ui(rng):
    t = tiempo(0.06)
    y = np.sin(2 * np.pi * 2800 * t) * decae(t, 0.004, 0.0002)
    y += 0.5 * np.sin(2 * np.pi * 5600 * t) * decae(t, 0.002, 0.0001)
    y += filtro(ruido(len(t), rng), "hp", 3000) * decae(t, 0.001, 0.00005) * 0.6
    return reverb(y, rt=0.12, mezcla=0.05, semilla=31)


@sonido("click-mecanico", "snap", ["click", "mecanico", "interruptor", "perilla", "clac"],
        "click-clac de interruptor (dos golpes de plástico)", 302)
def click_mecanico(rng):
    y = np.zeros(int(0.14 * SR))
    for t0, cuerpo, amp in [(0.0, 950, 1.0), (0.028, 780, 0.7)]:
        t = tiempo(0.08)
        g = filtro(ruido(len(t), rng), "bp", 2200, 2.0) * decae(t, 0.003, 0.0001)
        g += np.sin(2 * np.pi * cuerpo * t) * decae(t, 0.012, 0.0003) * 0.6
        g += np.sin(2 * np.pi * 180 * t) * decae(t, 0.015, 0.0005) * 0.5
        poner(y, g * amp, t0)
    return reverb(y, rt=0.15, mezcla=0.06, semilla=32)


@sonido("tick-contador", "ui", ["tick", "contador", "numero sube", "reloj"], "tick agudo y cortito para contadores", 303)
def tick_contador(rng):
    t = tiempo(0.03)
    y = np.sin(2 * np.pi * 4200 * t) * decae(t, 0.003, 0.0001)
    y += filtro(ruido(len(t), rng), "bp", 6000, 1.5) * decae(t, 0.0015, 0.00005) * 0.8
    return y


@sonido("tick-grave", "ui", ["tick", "madera", "contador", "segundero"], "tick de madera, más grave", 304)
def tick_grave(rng):
    t = tiempo(0.05)
    y = np.sin(2 * np.pi * 2100 * t) * decae(t, 0.005, 0.0001)
    y += np.sin(2 * np.pi * 900 * t) * decae(t, 0.008, 0.0002) * 0.7
    y += filtro(ruido(len(t), rng), "bp", 3000, 1.2) * decae(t, 0.002, 0.00005) * 0.5
    return y


def _campana(rng, f0, parciales, amps, taus, d):
    t = tiempo(d)
    y = np.zeros(len(t))
    for r, a, tau in zip(parciales, amps, taus):
        fase = rng.random() * 2 * np.pi
        y += a * np.sin(2 * np.pi * f0 * r * t + fase) * decae(t, tau, 0.0015)
    golpe = filtro(ruido(len(t), rng), "bp", f0 * 2, 1.0) * decae(t, 0.002, 0.0001) * 0.4
    return y + golpe


@sonido("ding", "emphasis", ["ding", "campana", "acierto", "dato", "listo"], "campanita brillante (Mi6) con cola larga", 401)
def ding(rng):
    y = _campana(rng, 1318.5, [1, 2.76, 5.40, 8.93], [1, 0.4, 0.2, 0.1], [0.9, 0.4, 0.2, 0.1], 3.0)
    return reverb(y, rt=0.5, mezcla=0.12, semilla=41)


@sonido("ding-grave", "emphasis", ["ding", "campana", "timbre", "grave"], "campana más grave (La5)", 402)
def ding_grave(rng):
    y = _campana(rng, 880.0, [1, 2.0, 2.76, 5.40], [1, 0.3, 0.35, 0.12], [1.1, 0.6, 0.45, 0.15], 3.5)
    return reverb(y, rt=0.6, mezcla=0.14, semilla=42)


@sonido("ping", "emphasis", ["ping", "radar", "señal", "espacio", "senal"], "ping puro y espacial (Do7) con eco de sala", 403)
def ping(rng):
    t = tiempo(1.8)
    y = (np.sin(2 * np.pi * 2093 * t) + 0.05 * np.sin(2 * np.pi * 4186 * t)) * decae(t, 0.3, 0.001)
    return reverb(y, rt=0.7, mezcla=0.25, brillo=7000, semilla=43)


@sonido("thud-suave", "emphasis", ["thud", "golpe", "suave", "cae", "aterriza"], "golpe sordo y blando", 501)
def thud_suave(rng):
    t = tiempo(0.8)
    f = 50 + 70 * np.exp(-t / 0.04)
    y = seno_glide(f) * decae(t, 0.12, 0.002)
    y += filtro(ruido(len(t), rng), "lp", 500, orden=2) * decae(t, 0.03, 0.0005) * 1.2
    return reverb(y, rt=0.2, mezcla=0.06, semilla=51)


@sonido("impacto-pesado", "emphasis", ["impacto", "golpe", "pesado", "boom", "hit"],
        "impacto grave con crujido y sala", 502)
def impacto_pesado(rng):
    t = tiempo(2.0)
    n = len(t)
    y = seno_glide(32 + 48 * np.exp(-t / 0.06)) * decae(t, 0.35, 0.002)
    y += filtro(ruido(n, rng), "lp", 900, orden=2) * decae(t, 0.09, 0.0005) * 1.8
    y += filtro(ruido(n, rng), "hp", 2000) * decae(t, 0.006, 0.0001) * 0.6
    y += np.sin(2 * np.pi * 220 * t) * decae(t, 0.06, 0.001) * 0.4
    y = np.tanh(y * 1.5) / 1.5
    return reverb(y, rt=0.9, mezcla=0.18, brillo=3000, semilla=52, estereo=True)


@sonido("thud-metal", "emphasis", ["metal", "clank", "golpe", "martillo", "fierro"],
        "golpe metálico (clank) con parciales inarmónicos", 503)
def thud_metal(rng):
    t = tiempo(2.0)
    n = len(t)
    y = np.zeros(n)
    for f, a, tau in zip([523, 1187, 1873, 2659, 3710, 5120], [1, 0.8, 0.6, 0.45, 0.3, 0.2],
                         [0.45, 0.3, 0.22, 0.15, 0.1, 0.06]):
        f *= 1 + rng.uniform(-0.01, 0.01)
        y += a * np.sin(2 * np.pi * f * t + rng.random() * 6.28) * decae(t, tau, 0.0005)
    y *= 0.5
    y += filtro(ruido(n, rng), "bp", 3500, 1.0) * decae(t, 0.004, 0.0001) * 1.2
    y += np.sin(2 * np.pi * 95 * t) * decae(t, 0.06, 0.001) * 0.8
    return reverb(y, rt=0.6, mezcla=0.15, semilla=53)


def _riser(rng, d):
    t = tiempo(d)
    n = len(t)
    u = t / d
    ruido_lr = [barrido(ruido_rosa(n, rng), curva_log(250, 7000, n, 1.3), "bp", 0.9) for _ in range(2)]
    tono = np.zeros(n)
    for det in (-0.006, 0.0, 0.006):
        tono += sierra(180 * (1 + det) * 2 ** (2 * u), 10)
    tono = barrido(tono, curva_log(600, 5000, n), "lp", 0.9) * 0.4
    vel = 3 + 15 * u ** 1.5
    trem = 1 - 0.35 * (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(vel) / SR))
    e = u ** 2 * trem
    st = np.stack([(ruido_lr[0] + tono * np.maximum(u, 0.02) ** -0.4) * e, (ruido_lr[1] + tono * np.maximum(u, 0.02) ** -0.4) * e], axis=1)
    st = reverb(st, rt=0.6, mezcla=0.12, semilla=61, estereo=True)[:n]
    st[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))[:, None]
    return st


@sonido("riser-1s", "tension", ["riser", "tension", "sube", "suspenso", "antes del golpe"],
        "subida de tensión de 1 s que corta en el clímax; se alinea por el final", 601)
def riser_1s(rng):
    return _riser(rng, 1.0)


@sonido("riser-2s", "tension", ["riser", "tension", "sube", "suspenso", "largo"],
        "subida de tensión de 2 s; se alinea por el final", 602)
def riser_2s(rng):
    return _riser(rng, 2.0)


@sonido("snap", "snap", ["snap", "chasquido", "dedos", "corte", "aparece"], "chasquido de dedos", 701)
def snap(rng):
    t = tiempo(0.3)
    n = len(t)
    y = ruido(n, rng) * decae(t, 0.0007, 0.00005) * 0.8
    y += filtro(ruido(n, rng), "bp", 2600, 1.5) * decae(t, 0.02, 0.0002) * 2.0
    y += filtro(ruido(n, rng), "bp", 1200, 2.0) * decae(t, 0.008, 0.0002) * 1.2
    return reverb(y, rt=0.25, mezcla=0.15, semilla=71)


def _glitch(rng, d):
    n = int(d * SR)
    y = np.zeros(n)
    i = 0
    while i < n:
        largo = int(rng.uniform(0.025, 0.06) * SR)
        t = np.arange(largo) / SR
        tipo = rng.choice(["crush", "stutter", "hueco", "ruido"], p=[0.4, 0.3, 0.1, 0.2])
        if tipo == "crush":
            s = np.sin(2 * np.pi * rng.uniform(200, 3000) * t)
            paso = int(rng.integers(8, 20))
            s = np.repeat(s[::paso], paso)[:largo]
            bits = int(rng.integers(2, 4))
            s = np.round(s * 2 ** bits) / 2 ** bits
        elif tipo == "stutter":
            g = int(0.012 * SR)
            grano = filtro(ruido(g, rng), "bp", rng.uniform(800, 4000), 2.0) * np.hanning(g)
            s = np.tile(grano, largo // g + 1)[:largo] * 2
        elif tipo == "hueco":
            s = np.zeros(largo)
        else:
            s = filtro(ruido(largo, rng), "hp", 3000) * 0.6
        s = s[:max(0, min(largo, n - i))]
        f = min(48, len(s) // 2)
        if f:
            s[:f] *= np.linspace(0, 1, f)
            s[-f:] *= np.linspace(1, 0, f)
        y[i:i + len(s)] = s
        i += largo
    return y


@sonido("glitch", "ui", ["glitch", "error", "digital", "falla", "interferencia"], "falla digital cortada (0,45 s)", 801)
def glitch(rng):
    return _glitch(rng, 0.45)


@sonido("glitch-corto", "ui", ["glitch", "corte", "digital", "transicion"], "glitch de 0,2 s para cortes", 802)
def glitch_corto(rng):
    return _glitch(rng, 0.2)


def _tono(f, d, at=0.004, rel=0.012):
    t = tiempo(d)
    y = np.sin(2 * np.pi * f * t) + 0.15 * np.sin(2 * np.pi * 2 * f * t)
    e = np.minimum(1, t / at) * np.minimum(1, (d - t) / rel)
    return y * np.clip(e, 0, 1)


@sonido("beep", "ui", ["beep", "pitido", "aviso", "aparato"], "pitido simple de aparato (Si5, 0,16 s)", 901)
def beep(rng):
    return reverb(_tono(988, 0.16), rt=0.15, mezcla=0.05, semilla=91)


@sonido("beep-doble", "ui", ["beep", "doble", "confirmacion", "aparato"], "dos pitidos cortos (Re6)", 902)
def beep_doble(rng):
    y = np.zeros(int(0.26 * SR))
    poner(y, _tono(1175, 0.09), 0)
    poner(y, _tono(1175, 0.09), 0.15)
    return reverb(y, rt=0.15, mezcla=0.05, semilla=92)


@sonido("buzz-error", "ui", ["error", "buzz", "incorrecto", "falso", "mito"], "zumbido de error 'eh-eh'", 903)
def buzz_error(rng):
    y = np.zeros(int(0.45 * SR))
    for t0 in (0.0, 0.23):
        d = 0.16
        t = tiempo(d)
        s = sierra(np.full(len(t), 140.0), 20) + sierra(np.full(len(t), 147.0), 20)
        s = filtro(s, "lp", 2200, orden=2)
        s = np.tanh(s * 2) * np.clip(np.minimum(t / 0.005, (d - t) / 0.015), 0, 1)
        poner(y, s, t0)
    return y


@sonido("whomp", "emphasis", ["whomp", "bajo", "drop", "caida", "grave", "revelacion"],
        "caída de bajo (170→38 Hz) con barrido", 1001)
def whomp(rng):
    t = tiempo(1.8)
    n = len(t)
    f = 38 + 132 * np.exp(-t / 0.18)
    y = seno_glide(f)
    y += barrido(sierra(f, 12), curva_log(1200, 150, n), "lp", 1.2) * 0.35
    e = np.minimum(1, t / 0.008) * np.where(t < 0.12, 1.0, np.exp(-(t - 0.12) / 0.3))
    y = np.tanh(y * e * 1.4)
    return reverb(y, rt=0.5, mezcla=0.1, brillo=1500, semilla=101)


@sonido("obturador", "snap", ["camara", "foto", "obturador", "flash", "captura"], "obturador de cámara (clic-clac)", 1101)
def obturador(rng):
    y = np.zeros(int(0.2 * SR))
    for t0, cuerpo, amp in [(0.0, 1400, 1.0), (0.07, 1100, 0.8)]:
        t = tiempo(0.05)
        g = filtro(ruido(len(t), rng), "bp", 3000, 1.5) * decae(t, 0.002, 0.0001)
        g += np.sin(2 * np.pi * cuerpo * t) * decae(t, 0.006, 0.0002) * 0.6
        poner(y, g * amp, t0)
    t = tiempo(0.04)
    poner(y, filtro(ruido(len(t), rng), "bp", 5000, 1.0) * np.hanning(len(t)) * 0.25, 0.015)
    t = tiempo(0.05)
    poner(y, np.sin(2 * np.pi * 3200 * t) * decae(t, 0.02, 0.0005) * 0.15, 0.07)
    return reverb(y, rt=0.15, mezcla=0.06, semilla=111)


def _tecla(rng, cuerpo, amp_fondo):
    t = tiempo(0.06)
    y = filtro(ruido(len(t), rng), "bp", 3200, 1.5) * decae(t, 0.0025, 0.0001)
    y += np.sin(2 * np.pi * cuerpo * t) * decae(t, 0.01, 0.0003) * 0.5
    y += np.sin(2 * np.pi * 230 * t) * decae(t, 0.012, 0.001) * amp_fondo
    return y


@sonido("tecla", "snap", ["tecla", "teclado", "escribe", "tipeo", "texto"], "una tecla de teclado", 1201)
def tecla(rng):
    return reverb(_tecla(rng, 1800, 0.4), rt=0.12, mezcla=0.05, semilla=121)


@sonido("tecla-b", "snap", ["tecla", "teclado", "escribe", "variante"], "tecla, variante más aguda", 1202)
def tecla_b(rng):
    return reverb(_tecla(rng, 2100, 0.3), rt=0.12, mezcla=0.05, semilla=122)


@sonido("tecleo", "snap", ["teclado", "escribe", "tipeo", "texto que se escribe"],
        "7 teclas seguidas con ritmo humano (1,2 s)", 1203)
def tecleo(rng):
    y = np.zeros(int(1.2 * SR))
    t0 = 0.0
    for _ in range(7):
        poner(y, _tecla(rng, rng.uniform(1500, 2200), rng.uniform(0.25, 0.45)) * rng.uniform(0.7, 1.0), t0)
        t0 += rng.uniform(0.09, 0.19)
    return reverb(y, rt=0.12, mezcla=0.05, semilla=123)


@sonido("gota", "emphasis", ["gota", "agua", "plip", "liquido"], "gota de agua (plip que sube de tono)", 1301)
def gota(rng):
    t = tiempo(0.4)
    f = 700 + 1300 * (1 - np.exp(-t / 0.012))
    y = seno_glide(f) * decae(t, 0.045, 0.0005)
    t2 = tiempo(0.1)
    y2 = np.zeros(len(t))
    poner(y2, np.sin(2 * np.pi * 420 * t2) * decae(t2, 0.02, 0.002) * 0.25, 0.01)
    return reverb(y + y2, rt=0.35, mezcla=0.2, semilla=131)


@sonido("resorte", "emphasis", ["resorte", "boing", "rebota", "salta", "chiste"], "boing de resorte", 1401)
def resorte(rng):
    t = tiempo(1.6)
    f = 180 * (1 + 0.45 * np.exp(-t / 0.35) * np.sin(2 * np.pi * 11 * t))
    fase = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(fase) + 0.3 * np.sin(2 * fase) + 0.15 * np.sin(3 * fase)
    y = barrido(y, curva_log(4000, 900, len(t)), "lp", 1.5) * decae(t, 0.3, 0.003)
    return reverb(y, rt=0.25, mezcla=0.08, semilla=141)


@sonido("estatica-tv", "ambience", ["estatica", "tele", "nieve", "sin señal", "ruido", "kssshh"],
        "lluvia de tele sin señal (2 s, con zumbido de 50 Hz muy bajo)", 1501)
def estatica_tv(rng):
    d = 2.0
    t = tiempo(d)
    n = len(t)
    lr = []
    for _ in range(2):
        x = filtro(filtro(ruido(n, rng), "hp", 700, orden=2), "lp", 8000)
        mod = 0.8 + 0.2 * uniform_filter1d(rng.random(n), int(0.02 * SR))
        lr.append(x * mod)
    zumbido = (np.sin(2 * np.pi * 50 * t) + 0.5 * np.sin(2 * np.pi * 150 * t)) * 0.08
    st = np.stack(lr, axis=1) + zumbido[:, None]
    f = int(0.05 * SR)
    st[:f] *= np.linspace(0, 1, f)[:, None]
    st[-f:] *= np.linspace(1, 0, f)[:, None]
    return st


# ------------------------------------------------------------------ normalización y salida


def limitar(x, techo_lin, ventana_s=0.002):
    """Limitador con anticipación: ganancia mínima por ventana + suavizado (nunca pasa del techo en muestras)."""
    x2 = medir.como_2d(x)
    pico = np.abs(x2).max(axis=1)
    nec = np.minimum(1.0, techo_lin / np.maximum(pico, 1e-12))
    w = max(3, int(ventana_s * SR))
    g = minimum_filter1d(nec, 2 * w + 1)
    g = uniform_filter1d(g, w + 1)
    g = np.minimum(g, nec)
    y = x2 * g[:, None]
    return y[:, 0] if np.ndim(x) == 1 else y


def recortar_cola(x, umbral_db=-66):
    """Corta la cola bajo umbral_db y la apaga con un fade coseno de hasta 50 ms (sin click al final)."""
    x2 = medir.como_2d(x)
    env = np.abs(x2).max(axis=1)
    lim = env.max() * 10 ** (umbral_db / 20)
    idx = np.flatnonzero(env > lim)
    fin = min(len(env), (idx[-1] + int(0.01 * SR)) if len(idx) else len(env))
    y = x2[:fin].copy()
    f = min(int(0.05 * SR), len(y) // 4)
    y[-f:] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, f)))[:, None]
    f0 = min(24, len(y) // 4)
    y[:f0] *= np.linspace(0, 1, f0)[:, None]
    return y[:, 0] if np.ndim(x) == 1 else y


def normalizar(x):
    techo = 10 ** (TECHO_DBTP / 20)
    y = x / (np.abs(x).max() + 1e-12) * 0.5
    for _ in range(4):
        y = y * 10 ** ((OBJETIVO_LUFS - medir.lufs(y)) / 20)
        tp = medir.true_peak_db(y)
        if tp <= TECHO_DBTP:
            break
        exceso = tp - TECHO_DBTP
        if exceso <= MAX_LIMITE_DB:
            y = limitar(y, techo * 10 ** (-0.3 / 20))      # 0,3 dB de margen para el pico entre muestras
        else:
            y = limitar(y * 10 ** (-(exceso - MAX_LIMITE_DB) / 20), techo * 10 ** (-0.3 / 20))
    tp = medir.true_peak_db(y)
    if tp > TECHO_DBTP:
        y = y * 10 ** ((TECHO_DBTP - 0.05 - tp) / 20)
    return y


def escribir_wav(ruta, x):
    """WAV 16 bits con dither triangular de semilla fija (determinista)."""
    rng = np.random.default_rng(12345)
    d = (rng.random(x.shape) - rng.random(x.shape)) / 32768.0
    q = np.clip(np.round((x + d) * 32767), -32768, 32767).astype(np.int16)
    wavfile.write(ruta, SR, q)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--solo", help="ids separados por coma")
    ap.add_argument("--verificar", action="store_true", help="compara con ffmpeg ebur128 (clips de 0,4 s o más)")
    a = ap.parse_args()
    os.makedirs(BIB, exist_ok=True)
    ruta_cat = os.path.join(BIB, "catalog.json")
    previo = {}
    if os.path.exists(ruta_cat):
        previo = {c["id"]: c for c in medir.leer_json(ruta_cat).get("clips", [])}
    ids = list(SONIDOS) if not a.solo else [s.strip() for s in a.solo.split(",")]
    clips = dict(previo)
    total = 0
    for id_ in ids:
        s = SONIDOS[id_]
        x = s["fn"](np.random.default_rng(s["semilla"]))
        x = recortar_cola(np.asarray(x, dtype=np.float64))
        x = normalizar(x)
        ruta = os.path.join(BIB, f"{id_}.wav")
        escribir_wav(ruta, x)
        x_leido = wavfile.read(ruta)[1].astype(np.float64) / 32768.0
        l, tp = medir.lufs(x_leido), medir.true_peak_db(x_leido)
        tam = os.path.getsize(ruta)
        total += tam
        clips[id_] = {
            "id": id_, "archivo": f"{id_}.wav", "categoria": s["categoria"], "tags": s["tags"],
            "descripcion": s["descripcion"], "canales": 1 if x.ndim == 1 else 2,
            "duracion_s": round(len(x) / SR, 3), "peak_dbfs": round(tp, 2), "loudness_lufs": round(l, 2),
            "fuente": FUENTE, "licencia": LICENCIA, "usado_en": previo.get(id_, {}).get("usado_en", []),
        }
        extra = ""
        if a.verificar and len(x) >= 0.4 * SR:
            i_ff, _ = medir.ebur128_ffmpeg(ruta)
            extra = f"  ffmpeg ebur128 {i_ff:6.1f}  (dif {l - i_ff:+.2f})"
        print(f"{id_:16s} {s['categoria']:9s} {len(x) / SR:5.2f} s  {l:6.1f} LUFS  {tp:5.1f} dBTP  {tam / 1024:6.0f} KB{extra}")
    orden = [k for k in SONIDOS if k in clips] + sorted(k for k in clips if k not in SONIDOS)
    medir.escribir_json(ruta_cat, {
        "descripcion": "Biblioteca propia de SFX de El viejo del dato. Ver tools/sonido/generar.py.",
        "sr": SR, "objetivo_lufs": OBJETIVO_LUFS, "techo_dbtp": TECHO_DBTP,
        "medida": "loudness BS.1770-4 propio (tools/sonido/medir.py); clips < 0,4 s medidos como un solo bloque",
        "clips": [clips[k] for k in orden],
    })
    tam_total = sum(os.path.getsize(os.path.join(BIB, f)) for f in os.listdir(BIB))
    print(f"\n{len(ids)} clips generados · biblioteca completa {tam_total / 1e6:.2f} MB · {ruta_cat}")


if __name__ == "__main__":
    main()
