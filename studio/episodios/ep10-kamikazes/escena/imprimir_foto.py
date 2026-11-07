"""Convierte una foto de archivo (dominio público) en una copia impresa vieja para la mesa: borde de papel crema,
tono apenas sepia, viñeta, grano y rayitas. Mismo aspecto que tex/foto_impresa.jpg (la foto del cuadro 0).
Uso: python3 imprimir_foto.py <original> <salida> [ancho_px]"""
import sys
import numpy as np
from PIL import Image, ImageFilter, ImageOps

src, dst = sys.argv[1], sys.argv[2]
ancho = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
rng = np.random.default_rng(7)
im = ImageOps.exif_transpose(Image.open(src)).convert("L")
im = im.resize((ancho, int(im.height * ancho / im.width)), Image.LANCZOS)
im = ImageOps.autocontrast(im, cutoff=0.5)
a = np.asarray(im).astype(np.float32) / 255
h, w = a.shape
yy, xx = np.mgrid[0:h, 0:w]
vin = 1 - 0.28 * np.clip(np.sqrt(((xx - w / 2) / (w * 0.6)) ** 2 + ((yy - h / 2) / (h * 0.6)) ** 2) - 0.55, 0, 1)
a = a * vin + rng.normal(0, 0.025, a.shape)
for _ in range(14):                           # rayitas finas y claras del papel gastado
    x0, y0 = rng.integers(0, w), rng.integers(0, h)
    L = rng.integers(h // 12, h // 4)
    ang = rng.uniform(-0.3, 0.3)
    for t in range(L):
        x, y = int(x0 + t * np.sin(ang)), int(y0 + t * np.cos(ang))
        if 0 <= x < w and 0 <= y < h:
            a[y, x] = min(1.0, a[y, x] + 0.18)
a = np.clip(a, 0, 1)
sep = np.stack([a * 1.0, a * 0.93, a * 0.80], axis=-1) * 0.97 + 0.03
foto = Image.fromarray((sep * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
b = int(ancho * 0.055)
papel = np.ones((h + 2 * b, w + 2 * b, 3), np.float32) * np.array([0.89, 0.85, 0.77])
papel += rng.normal(0, 0.012, papel.shape)
out = Image.fromarray((np.clip(papel, 0, 1) * 255).astype(np.uint8))
out.paste(foto, (b, b))
out.save(dst, quality=92)
print("ok", dst, out.size)
