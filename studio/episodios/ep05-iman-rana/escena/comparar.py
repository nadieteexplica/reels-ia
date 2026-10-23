"""Hoja de comparación de realismo (pedido de Tomás, 22-oct): los cuadros de estilo del Ep. 5 al lado de un cuadro del Ep. 4
y de fotos reales del tema. Las fotos reales son de otros (Wikimedia Commons, licencias libres): la hoja es interna y va
sólo a Tomás y al auditor; no entra al video ni al repo (referencias/ está en .gitignore).
Uso: python3 comparar.py <estilo_A.jpg> <estilo_B.jpg> <cuadro_ep04.jpg> <salida.jpg> [ref_1.jpg ...]"""
import sys
from PIL import Image, ImageDraw, ImageFont

a, b, ep4, out, *refs = sys.argv[1:]
H = 960
try:
    F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
except OSError:
    F = ImageFont.load_default()


def tarjeta(ruta, titulo, alto=H):
    im = Image.open(ruta).convert("RGB")
    w = round(im.width * alto / im.height)
    im = im.resize((w, alto), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    tw = d.textlength(titulo, font=F)
    d.rectangle((0, 0, tw + 24, 46), fill=(0, 0, 0))
    d.text((12, 6), titulo, font=F, fill=(255, 210, 63))
    return im


fila1 = [tarjeta(a, "Ep. 5 · A"), tarjeta(b, "Ep. 5 · B"), tarjeta(ep4, "Ep. 4 (antes)")]
fila2 = [tarjeta(r, f"Foto real {i + 1}", H // 2) for i, r in enumerate(refs)]
ancho = max(sum(i.width for i in fila1), sum(i.width for i in fila2) if fila2 else 0)
hoja = Image.new("RGB", (ancho, H + (H // 2 if fila2 else 0)), (18, 18, 20))
x = 0
for im in fila1:
    hoja.paste(im, (x, 0)); x += im.width
x = 0
for im in fila2:
    hoja.paste(im, (x, H)); x += im.width
hoja.save(out, quality=88)
print(out, hoja.size)
