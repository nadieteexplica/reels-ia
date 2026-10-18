"""Audio de las muestras: voz (0-5.1 s) + efectos de caricatura + musiquita de ukelele que se corta en el ¡zas!"""
import subprocess, pathlib, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000; DUR = 5.1; N = int(SR * DUR)
rng = np.random.default_rng(4)
t_all = np.arange(N) / SR

def voice():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(pathlib.Path(__file__).resolve().parents[2] / "out/tts/ep1-helado.mp3"), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    v = np.frombuffer(raw, np.float32)[:N].copy()
    v = np.pad(v, (0, N - len(v)))
    f = int(0.08 * SR); v[-f:] *= np.linspace(1, 0, f)
    return v / (np.abs(v).max() + 1e-9) * 0.9

def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)
def lp(x, f):
    return sosfilt(butter(2, f, btype="low", fs=SR, output="sos"), x)
def hp(x, f):
    return sosfilt(butter(2, f, btype="high", fs=SR, output="sos"), x)

def add(buf, x, at, g=1.0):
    i = int(at * SR); j = min(N, i + len(x))
    if i < N: buf[i:j] += g * x[: j - i]

def env(n, a=0.004, d=0.1):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)

def chomp():
    n = int(0.22 * SR); t = np.arange(n) / SR
    boop = np.sin(2 * np.pi * (260 * t - 330 * t * t)) * env(n, 0.003, 0.05)
    crunch = bp(rng.standard_normal(n), 1500, 5500) * env(n, 0.002, 0.03)
    return 0.8 * boop + 0.5 * crunch

def pop():
    n = int(0.12 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (500 * t + 4000 * t * t)) * env(n, 0.002, 0.03)

def whoosh(dur=0.35, up=True):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n); e = np.sin(np.pi * t / dur) ** 2
    lo = np.linspace(400, 3000, n) if up else np.linspace(3000, 400, n)
    out = np.zeros(n); seg = 2400
    for k in range(0, n, seg):
        c = lo[k]; out[k:k + seg] = bp(x[k:k + seg], c * 0.7, min(c * 1.6, 20000))
    return out * e

def freeze_hit():
    n = int(1.6 * SR); t = np.arange(n) / SR
    thump = np.sin(2 * np.pi * (90 * t - 25 * t * t)) * env(n, 0.002, 0.18)
    thump = np.tanh(2.5 * thump)
    shing = sum(np.sin(2 * np.pi * f * t + rng.random() * 6) * a for f, a in [(2093, .5), (3136, .4), (4186, .3), (5274, .25), (6645, .18), (7902, .12)])
    shing *= env(n, 0.003, 0.45)
    crackle = np.zeros(n)
    for _ in range(140):
        i = int(rng.random() ** 1.6 * 0.9 * SR); L = int(0.004 * SR)
        crackle[i:i + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (0.0008 * SR)) * (0.4 + rng.random())
    crackle = hp(crackle, 2500) * np.exp(-t / 0.6)
    return 0.9 * thump + 0.35 * shing + 0.6 * crackle

def slap():
    n = int(0.15 * SR)
    return lp(rng.standard_normal(n), 1800) * env(n, 0.001, 0.025) * 1.2

def chatter(dur):
    n = int(dur * SR); out = np.zeros(n); rate = 16
    for k in range(int(dur * rate)):
        i = int(k / rate * SR); L = int(0.012 * SR)
        if i + L < n: out[i:i + L] += hp(rng.standard_normal(L), 3000) * np.exp(-np.arange(L) / (0.002 * SR))
    return out * 0.6

def throb(at_list):
    n = int(0.3 * SR); t = np.arange(n) / SR
    b = np.sin(2 * np.pi * (70 * t)) * env(n, 0.01, 0.09)
    return b

def ks_pluck(freq, dur, bright=0.5):
    n = int(dur * SR); p = int(SR / freq)
    buf = rng.uniform(-1, 1, p) * 0.5; out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * (0.993 + 0.004 * bright)
    return out * np.exp(-np.arange(n) / SR / 0.6)

def music():
    out = np.zeros(N)
    bpm = 132; beat = 60 / bpm
    chords = [[261.6, 329.6, 392.0], [293.7, 349.2, 440.0], [329.6, 392.0, 493.9], [261.6, 329.6, 392.0]]
    strum_pat = [0, 0.5, 1, 1.5, 1.75, 2.5, 3, 3.5]
    cache = {}
    tb = 0.0; bar = 0
    while tb < 2.89:
        ch = chords[bar % 4]
        for sp in strum_pat:
            at = tb + sp * beat
            if at >= 2.89: break
            for k, f in enumerate(ch):
                key = (round(f, 1))
                if key not in cache: cache[key] = ks_pluck(f, 0.5)
                add(out, cache[key] * (0.5 if sp % 1 else 0.8), at + k * 0.008)
        tb += 4 * beat; bar += 1
    # corte seco en el zas
    i = int(2.89 * SR); out[i:] = 0
    fade = int(0.01 * SR); out[i - fade:i] *= np.linspace(1, 0, fade)
    # después: un brillo helado suave y temblón
    t = t_all; pad = np.zeros(N)
    for f in [1567.98, 2093.0, 2637.0]:
        pad += np.sin(2 * np.pi * f * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t))
    pad *= np.clip((t - 3.0) / 0.4, 0, 1) * 0.08
    return out + pad

v = voice()
sfx = np.zeros(N)
for b in [0.3, 0.88, 1.43]:
    add(sfx, whoosh(0.16), b - 0.02, 0.25)
    add(sfx, chomp(), b + 0.19, 0.9)
add(sfx, pop(), 2.62, 0.35)
add(sfx, whoosh(0.3, up=True), 2.62, 0.3)
add(sfx, freeze_hit(), 2.92, 1.0)
add(sfx, slap(), 3.6, 0.7)
add(sfx, chatter(1.55), 3.55, 0.25)
for k in range(5):
    add(sfx, throb(None), 3.66 + k / 3.1 + 0.08, 0.5 + (0.3 if 4.15 < 3.66 + k / 3.1 < 4.6 else 0))
m = music()
# ducking: música baja cuando habla la voz
env_v = np.convolve(np.abs(v), np.ones(int(0.05 * SR)) / (0.05 * SR), mode="same")
duck = 1 - 0.55 * np.clip(env_v / 0.08, 0, 1)
mix = v + 0.55 * sfx + 0.22 * m * duck
mix /= np.abs(mix).max() / 0.95
wavfile.write(str(pathlib.Path(__file__).resolve().parent / "audio.wav"), SR, (mix * 32767).astype(np.int16))
print("ok", len(mix) / SR)
