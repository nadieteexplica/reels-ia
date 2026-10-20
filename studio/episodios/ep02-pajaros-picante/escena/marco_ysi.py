"""Recuadro 2D de "y si…": borde punteado redondeado y una ✕ (blanca sobre gris) o ✓ en una esquina superior.
Uso: marco_ysi.py in.png out.jpg [x|check] [der|izq] [mascara]
  der|izq: esquina de la marca (por defecto der). Va sobre el fondo, nunca encima del personaje.
  mascara: fuera del recuadro la imagen se oscurece y se desenfoca, para que se lea como un inserto y no como un error de encuadre."""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
src, dst = sys.argv[1], sys.argv[2]
marca = sys.argv[3] if len(sys.argv) > 3 else "x"
esquina = sys.argv[4] if len(sys.argv) > 4 else "der"
mascara = len(sys.argv) > 5 and sys.argv[5] == "mascara"
im = Image.open(src).convert("RGB")
W, H = im.size
m, r = int(W * 0.06), int(W * 0.08)
x0, y0, x1, y1 = m, int(H * 0.16), W - m, int(H * 0.80)
if mascara:
    fuera = ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(W // 60))).enhance(0.45)
    mk = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mk).rounded_rectangle((x0, y0, x1, y1), radius=r, fill=255)
    im = Image.composite(im, fuera, mk)
d = ImageDraw.Draw(im)
paso, largo = int(W * 0.035), int(W * 0.02)
grosor = max(3, W // 180)
for x in range(x0 + r, x1 - r, paso):
    d.line((x, y0, min(x + largo, x1 - r), y0), fill=(255, 255, 255), width=grosor)
    d.line((x, y1, min(x + largo, x1 - r), y1), fill=(255, 255, 255), width=grosor)
for y in range(y0 + r, y1 - r, paso):
    d.line((x0, y, x0, min(y + largo, y1 - r)), fill=(255, 255, 255), width=grosor)
    d.line((x1, y, x1, min(y + largo, y1 - r)), fill=(255, 255, 255), width=grosor)
for (cx, cy, a0) in ((x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90)):
    for a in range(a0, a0 + 90, 30):
        d.arc((cx - r, cy - r, cx + r, cy + r), a, a + 15, fill=(255, 255, 255), width=grosor)
R = int(W * 0.06)
cx = (x1 - R - int(W * 0.03)) if esquina == "der" else (x0 + R + int(W * 0.03))
cy = y0 + R + int(W * 0.03)
d.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(70, 70, 75) if marca == "x" else (40, 170, 80))
k = int(R * 0.45)
if marca == "x":
    d.line((cx - k, cy - k, cx + k, cy + k), fill=(255, 255, 255), width=grosor * 2)
    d.line((cx - k, cy + k, cx + k, cy - k), fill=(255, 255, 255), width=grosor * 2)
else:
    d.line((cx - k, cy, cx - k // 3, cy + k * 0.7, cx + k, cy - k * 0.6), fill=(255, 255, 255), width=grosor * 2)
im.save(dst, quality=93)
