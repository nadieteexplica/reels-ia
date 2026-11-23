"""Aprieta una locución sin regenerarla: acorta los silencios largos y, si hace falta, la acelera un poco.

Qwen3-TTS deja pausas de hasta 1,4 s (15–19 s de silencio en 45 s de texto). Aquí cada silencio de más de
`--max-pausa` se deja en ese largo (misma regla que prep.py de los episodios: > 0,36 s → 0,3 s), y después,
si la voz queda más lenta que `--meta` palabras por segundo, se acelera con atempo hasta `--tope` (1,2× suena natural).

  python tools/voz_ajustar.py entrada.wav salida.wav --palabras 146 [--meta 3.1] [--max-pausa 0.3] [--tope 1.2]
"""
import argparse, subprocess

import numpy as np

SR = 48000


def leer(f):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def silencios(x, umbral_db=-38, minimo=0.12):
    """Tramos (inicio, fin) en muestras donde la energía (ventanas de 10 ms) queda bajo el umbral."""
    h = SR // 100
    n = len(x) // h
    rms = np.sqrt(np.mean(x[: n * h].reshape(n, h) ** 2, axis=1) + 1e-12)
    bajo = 20 * np.log10(rms / (np.abs(x).max() + 1e-9)) < umbral_db
    tramos, i = [], 0
    while i < n:
        if bajo[i]:
            j = i
            while j < n and bajo[j]:
                j += 1
            if (j - i) * h >= minimo * SR:
                tramos.append((i * h, j * h))
            i = j
        else:
            i += 1
    return tramos


def apretar(x, max_pausa):
    keep = int(max_pausa * SR)
    fade = int(0.006 * SR)
    partes, pos = [], 0
    for a, b in silencios(x):
        if b - a <= keep:
            continue
        # se deja la mitad del silencio permitido a cada lado del corte, con fundidos cortos
        c0, c1 = a + keep // 2, b - keep // 2
        seg = x[pos:c0].copy()
        seg[-fade:] *= np.linspace(1, 0, fade)
        partes.append(seg)
        pos = c1
        x[pos:pos + fade] *= np.linspace(0, 1, fade)
    partes.append(x[pos:])
    return np.concatenate(partes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("salida")
    ap.add_argument("--palabras", type=int, required=True)
    ap.add_argument("--meta", type=float, default=3.1, help="palabras por segundo buscadas (ElevenLabs en el Ep. 7: 3,13)")
    ap.add_argument("--max-pausa", type=float, default=0.3)
    ap.add_argument("--tope", type=float, default=1.2)
    a = ap.parse_args()

    x = leer(a.entrada)
    d0 = len(x) / SR
    y = apretar(x, a.max_pausa)
    d1 = len(y) / SR
    tempo = min(a.tope, max(1.0, d1 / (a.palabras / a.meta)))  # duración actual / duración que daría la meta
    filtros = f"atempo={tempo:.3f}," if tempo > 1.001 else ""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-af", filtros + "aresample=48000", a.salida], input=y.astype(np.float32).tobytes(), check=True)
    d2 = d1 / tempo
    print(f"{a.entrada}: {d0:.1f}s → pausas {d1:.1f}s → atempo {tempo:.2f} → {d2:.1f}s ({a.palabras / d2:.2f} pal/s)")


if __name__ == "__main__":
    main()
