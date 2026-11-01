"""ficha.jpg del Ep. 5: los dos personajes tal como salen en los cuadros de estilo aprobados (puerta 4).
Uso: python3 ficha.py <estilo_A_HD.jpg> <estilo_B_HD.jpg> <salida.jpg>
La caja de cada personaje sale de su posición en pantalla (medida en el render), no de números a ojo."""
import sys
from PIL import Image, ImageDraw, ImageFont

a, b, out = sys.argv[1:4]
F = ImageFont.truetype("/home/claude/reels-ia/studio/plantilla/fonts/Inter-Black.otf", 34) if len(sys.argv) < 5 else None
A = Image.open(a).convert("RGB")
B = Image.open(b).convert("RGB")
rana = A.crop((140, 560, 940, 1160)).resize((800, 600))
pete_box = tuple(int(v) for v in (sys.argv[4].split(",") if len(sys.argv) > 4 else "380,560,700,1080".split(",")))
pete = B.crop(pete_box)
pete = pete.resize((round(600 * pete.width / pete.height), 600))
hoja = Image.new("RGB", (800 + pete.width + 40, 680), (20, 22, 26))
hoja.paste(rana, (0, 80))
hoja.paste(pete, (840, 80))
d = ImageDraw.Draw(hoja)
f = ImageFont.truetype("/home/claude/reels-ia/studio/plantilla/fonts/Inter-Black.otf", 34)
d.text((20, 20), "RANA (escaneo real, 2,2 cm)", font=f, fill=(255, 210, 63))
d.text((860, 20), "PETE (Mixamo)", font=f, fill=(255, 210, 63))
hoja.save(out, quality=90)
print(out, hoja.size)
