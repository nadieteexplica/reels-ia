"""Vara viral: pone NUESTRO beat al lado de cuadros de virales de referencia, con el mismo recorte y letras al
azar, para que un juez ciego diga qué nos falta para llegar a ese nivel (pedido de Tomás, 23-nov-2026).

  python3 studio/duelo-visual/vara_viral.py <nuestro.mp4> <salida> --ref touchscreen=<video>@0,1.5,3,... --ref buceo=<video>@...

Los videos de referencia son de otros creadores: este script SÓLO escribe en <salida> (que tiene que estar en el
scratchpad, fuera del repo). Nada de esto se commitea.

Recorte común a todos (quita la interfaz de Instagram de las grabaciones): arriba 12 %, abajo 21 %, derecha 13 %.
Se aplica igual a nuestro video para que el encuadre sea el mismo.
"""
import argparse, json, random, subprocess, sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[2]
FUENTE = RAIZ / "studio/plantilla/fonts/Inter-ExtraBold.otf"
ARRIBA, ABAJO, DERECHA = 0.12, 0.21, 0.13
ANCHO_T = 360


def cuadro(video, t, arriba=ARRIBA, abajo=ABAJO):
    out = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", "-f", "image2pipe",
                          "-vcodec", "png", "-"], capture_output=True, check=True).stdout
    from io import BytesIO
    im = Image.open(BytesIO(out)).convert("RGB")
    w, h = im.size
    im = im.crop((0, int(h * arriba), int(w * (1 - DERECHA)), int(h * (1 - abajo))))
    return im.resize((ANCHO_T, int(ANCHO_T * im.size[1] / im.size[0])))


def hoja(ims, cols=5):
    tw, th = ims[0].size
    filas = (len(ims) + cols - 1) // cols
    h = Image.new("RGB", (cols * tw + (cols - 1) * 6, filas * th + (filas - 1) * 6), (80, 80, 80))
    for i, im in enumerate(ims):
        h.paste(im, ((i % cols) * (tw + 6), (i // cols) * (th + 6)))
    return h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nuestro")
    ap.add_argument("salida")
    ap.add_argument("--nuestros-t", default="0,0.6,1.1,1.5,2.4,3.1,3.6,4.1,5.3,6.9")
    ap.add_argument("--ref", action="append", default=[])
    a = ap.parse_args()
    out = Path(a.salida)
    if str(RAIZ) in str(out.resolve()):
        sys.exit("la salida tiene que quedar FUERA del repo (los cuadros de los virales son de otros)")
    fuentes = [("nuestro", Path(a.nuestro), [float(x) for x in a.nuestros_t.split(",")])]
    for r in a.ref:
        nombre, resto = r.split("=", 1)
        video, ts = resto.rsplit("@", 1)
        fuentes.append((nombre, Path(video).expanduser(), [float(x) for x in ts.split(",")]))
    letras = [chr(65 + i) for i in range(len(fuentes))]
    random.shuffle(letras)
    clave = {}
    out.mkdir(parents=True, exist_ok=True)
    for letra, (nombre, video, ts) in zip(letras, fuentes):
        # nuestro video no trae interfaz: recorte casi igual de alto, corrido para no cortar nuestros subtítulos (y≈1380–1560)
        ab = (0.11, 0.18) if nombre == "nuestro" else (ARRIBA, ABAJO)
        hoja([cuadro(video, t, *ab) for t in ts]).save(out / f"{letra}.jpg", quality=86)
        clave[letra] = nombre
    (out.parent / f"{out.name}-clave.json").write_text(json.dumps(clave, indent=1))
    print("listo:", sorted(clave), "· clave en", out.parent / f"{out.name}-clave.json")


if __name__ == "__main__":
    main()
