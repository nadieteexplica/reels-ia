"""Arma el cuadro del plano 23: el ratón de perfil (render MODO=cara) + una lupa redonda grande con el primer plano de las
muelas (render MODO=lupa), unidas por dos líneas a una marca en la mejilla; encima, el recuadro punteado "y si…" y la ✕.

Uso: compone_muelas.py cara.png lupa.png salida.jpg MEJ_X MEJ_Y   (MEJ_* = posición de la mejilla en cara.png, en píxeles)
"""
import math, sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

cara_p, lupa_p, dst = sys.argv[1], sys.argv[2], sys.argv[3]
mx, my = float(sys.argv[4]), float(sys.argv[5])
im = Image.open(cara_p).convert("RGB")
W, H = im.size
k = W / 1080
lupa = Image.open(lupa_p).convert("RGB")
# lupa: círculo de 560 px (52 % del ancho) arriba a la derecha, sin tapar la cabeza (la cara mira a la izquierda)
D = int(float(__import__("os").environ.get("LUPA_D", 520)) * k)
cx, cy = int(float(__import__("os").environ.get("LUPA_CX", 760)) * k), int(float(__import__("os").environ.get("LUPA_CY", 600)) * k)
L = lupa.size[0]
recorte = int(L * float(__import__("os").environ.get("LUPA_ZOOM", 0.72)))
lz = lupa.crop(((L - recorte) // 2, (L - recorte) // 2, (L + recorte) // 2, (L + recorte) // 2)).resize((D, D), Image.LANCZOS)
mask = Image.new("L", (D, D), 0)
ImageDraw.Draw(mask).ellipse((0, 0, D - 1, D - 1), fill=255)
d = ImageDraw.Draw(im)
# líneas de la mejilla a la lupa (tangentes aproximadas), detrás de la lupa
r_m = int(26 * k)
ang = math.atan2(cy - my, cx - mx)
for s in (-1, 1):
    a = ang + s * math.pi / 2
    p0 = (mx + r_m * math.cos(a), my + r_m * math.sin(a))
    p1 = (cx + D / 2 * math.cos(a), cy + D / 2 * math.sin(a))
    d.line((p0, p1), fill=(255, 255, 255), width=max(3, int(5 * k)))
# sombra suave bajo la lupa
sh = Image.new("L", (W, H), 0)
ImageDraw.Draw(sh).ellipse((cx - D // 2 + 10, cy - D // 2 + 18, cx + D // 2 + 10, cy + D // 2 + 18), fill=140)
sh = sh.filter(ImageFilter.GaussianBlur(int(18 * k)))
im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, sh)
im.paste(lz, (cx - D // 2, cy - D // 2), mask)
d = ImageDraw.Draw(im)
gro = max(6, int(10 * k))
d.ellipse((cx - D // 2, cy - D // 2, cx + D // 2, cy + D // 2), outline=(250, 246, 236), width=gro)
d.ellipse((mx - r_m, my - r_m, mx + r_m, my + r_m), outline=(250, 246, 236), width=max(4, int(6 * k)))
im.save(dst, **({"quality": 94} if dst.lower().endswith((".jpg", ".jpeg")) else {}))
print("lupa", cx, cy, D, "mejilla", mx, my)
