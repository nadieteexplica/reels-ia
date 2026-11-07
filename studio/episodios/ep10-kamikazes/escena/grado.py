"""Gradación común del Ep. 5 (cuadros de estilo y post del video): un poco más de color y contraste, sin quemar.
El cielo físico + AgX sale correcto pero algo apagado; Zack D. Films (referencia de calidad) es saturado sin ser pastel."""
from PIL import Image, ImageEnhance


def grado(im, color=1.2, contraste=1.07, calido=1.02):
    im = ImageEnhance.Color(im).enhance(color)
    im = ImageEnhance.Contrast(im).enhance(contraste)
    if calido != 1.0:
        r, g, b = im.split()
        r = r.point(lambda v: min(255, int(v * calido)))
        b = b.point(lambda v: int(v / calido))
        im = Image.merge("RGB", (r, g, b))
    return im
