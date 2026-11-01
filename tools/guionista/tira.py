"""Tira de los primeros 3 s de un video (6 cuadros en 0, 0,5, 1, 1,5, 2 y 3 s, 360 px de ancho cada uno) para el duelo
con cuadros reales (docs/GUIONISTA.md §4, paso 8) y para sumar un video publicado a las anclas.

  python3 tools/guionista/tira.py <video.mp4> <salida.jpg>

Siempre a 360 px de ancho, sea un animatic (540×960) o el render final: así ningún lado gana por resolución.
"""
import subprocess, sys, tempfile
from pathlib import Path
from PIL import Image

TIEMPOS = ("0", "0.5", "1", "1.5", "2", "3")


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    video, salida = sys.argv[1], Path(sys.argv[2])
    with tempfile.TemporaryDirectory() as tmp:
        cuadros = []
        for t in TIEMPOS:
            f = Path(tmp) / f"{t}.jpg"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", t, "-i", video, "-frames:v", "1",
                            "-vf", "scale=360:-2", str(f)], check=True)
            cuadros.append(Image.open(f).convert("RGB"))
        w, h = cuadros[0].size
        tira = Image.new("RGB", (w * len(cuadros), h))
        for i, c in enumerate(cuadros):
            tira.paste(c.resize((w, h)), (i * w, 0))
        salida.parent.mkdir(parents=True, exist_ok=True)
        tira.save(salida, quality=80)
    print(salida)


if __name__ == "__main__":
    main()
