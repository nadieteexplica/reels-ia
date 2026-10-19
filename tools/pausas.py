"""Ajusta pausas de una locución sin regenerarla (0 créditos): inserta o recorta silencio y corre los tiempos de words.json.

  python3 tools/pausas.py out/tts/<ep>.mp3 studio/episodios/<ep>/words.json "4.50:+0.20" "32.24:-0.30" ...

Cada ajuste es "segundo:±delta" en el tiempo ORIGINAL. El corte se hace en el punto de menor energía de los 0,25 s
alrededor (dentro del silencio, si lo hay), con fundidos de 6 ms para que no suene un clic. Un recorte sólo saca silencio
real (si no lo hay, falla). El original queda como <ep>_original.mp3 / words_original.json (sólo la primera vez).
"""
import json, os, shutil, subprocess, sys
import numpy as np

SR = 48000


def leer(mp3):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp3, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def escribir(x, mp3):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "libmp3lame", "-b:a", "192k", mp3],
                   input=x.astype(np.float32).tobytes(), check=True)


def punto_quieto(x, t, ventana=0.25):
    """Índice de menor energía (RMS en 10 ms) dentro de t±ventana/2."""
    a, b = int((t - ventana / 2) * SR), int((t + ventana / 2) * SR)
    a, b = max(0, a), min(len(x), b)
    w = int(0.010 * SR)
    seg = x[a:b] ** 2
    if len(seg) <= w:
        return int(t * SR)
    rms = np.sqrt(np.convolve(seg, np.ones(w) / w, mode="valid"))
    return a + int(np.argmin(rms)) + w // 2


def main():
    mp3, wj, ajustes = sys.argv[1], sys.argv[2], sys.argv[3:]
    base, ext = os.path.splitext(mp3)
    orig_mp3 = base + "_original" + ext
    orig_w = os.path.join(os.path.dirname(wj), "words_original.json")
    if not os.path.exists(orig_mp3):
        shutil.copy(mp3, orig_mp3)
        shutil.copy(wj, orig_w)
    x = leer(orig_mp3)
    words = json.load(open(orig_w))
    eds = sorted((float(a.split(":")[0]), float(a.split(":")[1])) for a in ajustes)
    f = int(0.006 * SR)
    trozos, prev, cortes = [], 0, []
    for t, d in eds:
        i = punto_quieto(x, t)
        if d > 0:
            trozos.append(x[prev:i].copy())
            if len(trozos[-1]) > f:
                trozos[-1][-f:] *= np.linspace(1, 0, f)
            trozos.append(np.zeros(int(d * SR), dtype=np.float32))
            prev = i
            cortes.append((i / SR, d))
        else:
            n = int(-d * SR)
            a, b = i - n // 2, i + n - n // 2
            if np.sqrt(np.mean(x[a:b] ** 2)) > 0.01:
                sys.exit(f"en {t:.2f} s no hay silencio suficiente para recortar {-d:.2f} s")
            trozos.append(x[prev:a].copy())
            prev = b
            cortes.append((i / SR, d))
        print(f"{t:6.2f} s → corte en {i / SR:6.3f} s, {d:+.2f} s")
    resto = x[prev:].copy()
    if eds and eds[-1][1] > 0 and len(resto) > f:
        resto[:f] *= np.linspace(0, 1, f)
    trozos.append(resto)
    y = np.concatenate(trozos)
    escribir(y, mp3)

    def corre(tt):
        return tt + sum(d for c, d in cortes if c <= tt + 1e-4)
    for w in words:
        w["s"], w["e"] = round(corre(w["s"]), 3), round(corre(w["e"]), 3)
    json.dump(words, open(wj, "w"), ensure_ascii=False, indent=0)
    print(f"listo: {len(x) / SR:.2f} s → {len(y) / SR:.2f} s; última palabra termina en {words[-1]['e']:.2f} s")


if __name__ == "__main__":
    main()
