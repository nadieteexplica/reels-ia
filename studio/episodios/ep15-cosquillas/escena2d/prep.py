"""Prepara la voz del Ep. 15: recorta el silencio largo (> 0,5 s, regla 20), deja voz.wav (48 kHz mono),
words.json corrido y envolvente.json (60 Hz, para la boca del viejo). Uso: python3 prep.py"""
import json, os, subprocess
import numpy as np
from scipy.io import wavfile

AQUI = os.path.dirname(os.path.abspath(__file__))
EPI = os.path.abspath(os.path.join(AQUI, ".."))
RAIZ = os.path.abspath(os.path.join(EPI, "../../.."))
SR = 48000
subprocess.run(["python3", os.path.join(RAIZ, "tools/words.py"), os.path.join(RAIZ, "out/tts/ep15-cosquillas.json"), os.path.join(EPI, "words_voz.json")], check=True)
w = json.load(open(os.path.join(EPI, "words_voz.json")))
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(RAIZ, "out/tts/ep15-cosquillas.mp3"), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
v = np.frombuffer(raw, np.float32).copy()
CORTES = []                       # (desde, hasta) en s de la voz original
for a, b in zip(w, w[1:]):
    gap = b["s"] - a["e"]
    if gap > 0.5:
        quita = gap - 0.42
        c0 = a["e"] + 0.2
        CORTES.append((c0, c0 + quita))
out, pos = [], 0.0
for c0, c1 in CORTES:
    out.append(v[int(pos * SR):int(c0 * SR)]); pos = c1
out.append(v[int(pos * SR):])
v2 = np.concatenate(out)
for x in w:
    d = sum(c1 - c0 for c0, c1 in CORTES if x["s"] >= c1 - 1e-6)
    x["s"] = round(x["s"] - d, 3); x["e"] = round(x["e"] - d, 3)
# respiros (regla 23): silencio extra antes de los giros y de la frase final (la voz salió a ~3,9 pal/s)
RESPIROS = [("Para", 0.15), ("Pero", 0.0), ("La", 0.35), ("No", 0.0), ("No", 0.45)]   # (palabra, s) en orden; 0 = sólo marca
idx, k = [], 0
for i, x in enumerate(w):
    if k < len(RESPIROS) and x["w"].strip("¿¡.,") == RESPIROS[k][0] and i > 0 and w[i - 1]["w"][-1] in ".?!":
        if RESPIROS[k][0] in ("Pero", "No") and RESPIROS[k][1] == 0.0 and not (k == 1 and i > 40 or k == 3 and i > 60):
            continue
        idx.append((i, RESPIROS[k][1])); k += 1
partes, pos, extra = [], 0, 0.0
for i, seg in idx:
    if seg <= 0:
        continue
    corte = (w[i - 1]["e"] + w[i]["s"]) / 2
    partes.append(v2[int(pos * SR):int(corte * SR)]); partes.append(np.zeros(int(seg * SR), np.float32)); pos = corte
    for x in w[i:]:
        x["s"] = round(x["s"] + seg, 3); x["e"] = round(x["e"] + seg, 3)
    extra += seg
partes.append(v2[int(pos * SR):])
v2 = np.concatenate(partes)
print("respiros", [(w[i]["w"], s_) for i, s_ in idx if s_ > 0])
json.dump(w, open(os.path.join(EPI, "words.json"), "w"), ensure_ascii=False, indent=0)
wavfile.write(os.path.join(AQUI, "voz.wav"), SR, (np.clip(v2 / (np.abs(v2).max() + 1e-9) * 0.9, -1, 1) * 32767).astype(np.int16))
n = int(len(v2) / SR * 60)
env = [float(np.sqrt(np.mean(v2[int(i * SR / 60):int((i + 2) * SR / 60)] ** 2) + 1e-12)) for i in range(n)]
m = max(env)
json.dump([round(min(1.0, e / m * 1.8), 3) for e in env], open(os.path.join(AQUI, "envolvente.json"), "w"))
print("cortes", CORTES, "· voz", round(len(v2) / SR, 2), "s ·", round(len(w) / w[-1]["e"], 2), "pal/s")
