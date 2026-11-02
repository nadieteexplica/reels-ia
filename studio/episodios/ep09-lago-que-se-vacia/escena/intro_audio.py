"""Audio del plano 0 (el mapa): la voz nueva + el mismo lenguaje musical de audio.py (pad oscuro en Re menor, subida) y
efectos (whoosh del zoom, dos toques en "Chile" y "lago", whoosh de bajada al corte) → intro_mix.wav, −14 LUFS como el resto.
Uso: python3 intro_audio.py <voz.mp3> <asr_intro.json> <salida.wav> [duración s]"""
import ast, json, os, subprocess, sys, tempfile
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, "audio.py")).read()
voz_p, asr_p, dst = sys.argv[1:4]
DUR = float(sys.argv[4]) if len(sys.argv) > 4 else 3.0
VOZ0 = float(os.environ.get("VOZ0", 0.10))
SR = 48000
N = int(DUR * SR)
ns = {"np": np, "butter": butter, "sosfilt": sosfilt, "SR": SR, "N": N, "rng": np.random.default_rng(9), "BPM": 96}
ns["NEGRA"] = 60 / 96
for nodo in ast.parse(SRC).body:
    if isinstance(nodo, ast.FunctionDef) and nodo.name in ("filt", "tt", "env", "ruido", "tono", "whoosh", "ding", "hz", "sierra",
                                                             "pad_oscuro", "subida", "add"):
        exec(compile(ast.Module([nodo], []), "audio.py", "exec"), ns)
g = ns

tmp = tempfile.mktemp(suffix=".wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", voz_p, "-ac", "1", "-ar", str(SR), tmp], check=True)
_, v = wavfile.read(tmp)
v = v.astype(np.float64) / 32768.0
voz = np.zeros(N)
i0 = int(VOZ0 * SR)
voz[i0:i0 + len(v)] += v[: N - i0]

pal = json.load(open(asr_p))["palabras"]
t_chile = next(p["s"] for p in pal if p["w"].lower().startswith("chile")) + VOZ0
t_lago = next(p["s"] for p in pal if p["w"].lower().startswith("lago")) + VOZ0

mus = np.zeros(N)
g["add"](mus, g["pad_oscuro"]((50, 53, 57), DUR + 0.3, 900)[:N], 0.0, 0.5)          # Re menor, el mismo pad del video
g["add"](mus, g["subida"](DUR - 0.2)[: N], 0.2, 0.55)                                 # la subida que lleva al corte
fx = np.zeros(N)
g["add"](fx, g["whoosh"](1.0, True), 0.0, 0.5)                                        # la Tierra que gira y el zoom
g["add"](fx, g["whoosh"](0.9, True), t_chile - 0.35, 0.45)
g["add"](fx, g["ding"](1175, 0.5), t_chile, 0.35)
g["add"](fx, g["ding"](1318, 0.6), t_lago, 0.35)
g["add"](fx, g["whoosh"](0.5, False), DUR - 0.5, 0.6)                                  # bajada al corte (el barro)
mix = voz * 1.0 + mus * 0.45 + fx * 0.45
mix = np.tanh(mix * 1.1) / 1.1
wavfile.write(tmp, SR, (np.clip(mix, -1, 1) * 32767).astype(np.int16))
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "alimiter=limit=0.6:level=false,loudnorm=I=-14:TP=-2.5:LRA=11",
                "-ar", str(SR), "-ac", "1", dst], check=True)
print("ok intro_audio", dst, round(DUR, 2), "s")
