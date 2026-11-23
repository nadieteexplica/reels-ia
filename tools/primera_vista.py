"""Prueba de primera vista (lección 177): un juez ciego ve el video UNA vez, a velocidad real (cuadros cada 0,1 s,
en orden, una fila = 1 s), con la pista de audio descrita, y cuenta qué pasó segundo a segundo. Si no puede contar un
tramo, ese tramo va demasiado rápido.

  python3 tools/primera_vista.py <video> <words.json> <salida>     # salida fuera del repo si el video no es nuestro

Deja <salida>/fila-NN.jpg (10 cuadros por fila = 1 s; 4 filas por hoja) y audio.md. El juez lee las hojas en orden,
una sola vez (sin volver atrás) y responde por segundo: qué vio, qué entendió y dónde se perdió.
"""
import json, subprocess, sys
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "studio/duelo-visual"))
from vara_relativa import audio, describir_audio  # noqa: E402

FUENTE = RAIZ / "studio/plantilla/fonts/Inter-ExtraBold.otf"
ANCHO = 150


def cuadro(video, t):
    png = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1", "-f", "image2pipe",
                          "-vcodec", "png", "-"], capture_output=True, check=True).stdout
    im = Image.open(BytesIO(png)).convert("RGB")
    return im.resize((ANCHO, int(ANCHO * im.size[1] / im.size[0])))


def main():
    video, words, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)]))
    f = ImageFont.truetype(str(FUENTE), 16)
    n_seg = int(dur + 0.999)
    filas = []
    for s in range(n_seg):
        ims = []
        for k in range(10):
            t = min(s + k / 10, dur - 0.12)
            im = cuadro(video, t)
            d = ImageDraw.Draw(im)
            d.rectangle([0, 0, 44, 20], fill=(0, 0, 0))
            d.text((3, 1), f"{s + k / 10:.1f}", font=f, fill=(255, 230, 0))
            ims.append(im)
        tw, th = ims[0].size
        fila = Image.new("RGB", (10 * tw + 9 * 3, th), (60, 60, 60))
        for k, im in enumerate(ims):
            fila.paste(im, (k * (tw + 3), 0))
        filas.append(fila)
    for n in range(0, len(filas), 4):
        grupo = filas[n:n + 4]
        h = Image.new("RGB", (grupo[0].size[0], sum(g.size[1] + 6 for g in grupo)), (30, 30, 30))
        y = 0
        for g in grupo:
            h.paste(g, (0, y))
            y += g.size[1] + 6
        h.save(out / f"hoja-{n // 4 + 1}.jpg", quality=84)
    golpes, piso = audio(video, 0, dur)
    (out / "audio.md").write_text(describir_audio(json.load(open(words)), golpes, piso, 0, dur))
    print("listo:", out, f"({n_seg} s, {len(filas)} filas)")


if __name__ == "__main__":
    main()
