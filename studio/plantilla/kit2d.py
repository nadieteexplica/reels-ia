"""Kit 2D plano de El viejo del dato (7-nov-2026): todo se dibuja con código (PIL), sin 3D ni GPU.

Estilo: colores planos apagados de una paleta fija, contorno de tinta, papel con grano, un acento rojo. Piezas:
  Lienzo(w, h, ss)        → dibujo en sobremuestreo (ss) y salida a 1080×1920
  mapa(...)               → países de Natural Earth (dominio público) proyectados, con colores por país
  persona(...)            → silueta plana armada con formas y ropa de época intercambiable (poses por ángulos)
  viejo(...)              → el narrador (boina, lentes, bigote, tazón) con boca que se mueve con la voz
  avion_lateral(...)      → avión de hélice de perfil (silueta plana)
  flecha, pildora, texto, cielo_bandas, cerros, grano
"""
import json, math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(AQUI, "fonts")
FONT = os.path.join(FONTS, "Inter-Black.otf")
FONT_B = os.path.join(FONTS, "Inter-ExtraBold.otf")

P = {   # paleta fija (apagada) + acentos
    "papel": (236, 228, 212), "papel2": (226, 216, 196), "tinta": (38, 34, 32), "mar": (150, 178, 186), "mar2": (132, 162, 172),
    "tierra": (222, 208, 178), "tierra2": (204, 188, 156), "rojo": (196, 64, 52), "azul": (52, 86, 132), "azul2": (88, 124, 170),
    "ocre": (204, 150, 72), "verde": (110, 128, 84), "gris": (140, 136, 128), "blanco": (250, 246, 238), "piel": (226, 184, 148),
    "piel2": (196, 150, 112), "cuero": (112, 78, 52), "caqui": (150, 132, 92), "oliva": (96, 98, 66), "marino": (52, 60, 82),
    "cielo1": (240, 196, 150), "cielo2": (226, 160, 128), "cielo3": (172, 132, 140), "sol": (248, 226, 170),
}


class Lienzo:
    def __init__(self, w=1080, h=1920, ss=2, fondo=None):
        self.w, self.h, self.ss = w, h, ss
        self.im = Image.new("RGB", (w * ss, h * ss), fondo or P["papel"])
        self.d = ImageDraw.Draw(self.im, "RGBA")

    def S(self, v):
        return v * self.ss

    def pt(self, x, y):
        return (x * self.ss, y * self.ss)

    def salida(self):
        return self.im.resize((self.w, self.h), Image.LANCZOS)


# ------------------------------------------------------------------ formas básicas
def poligono(L, pts, relleno, borde=None, ancho=4):
    q = [L.pt(x, y) for x, y in pts]
    L.d.polygon(q, fill=relleno)
    if borde:
        L.d.line(q + [q[0]], fill=borde, width=int(L.S(ancho)), joint="curve")


def circulo(L, x, y, r, relleno, borde=None, ancho=4):
    L.d.ellipse((L.S(x - r), L.S(y - r), L.S(x + r), L.S(y + r)), fill=relleno,
                outline=borde, width=int(L.S(ancho)) if borde else 0)


def elipse(L, x, y, rx, ry, relleno, borde=None, ancho=4):
    L.d.ellipse((L.S(x - rx), L.S(y - ry), L.S(x + rx), L.S(y + ry)), fill=relleno,
                outline=borde, width=int(L.S(ancho)) if borde else 0)


def linea(L, pts, color, ancho=10):
    L.d.line([L.pt(x, y) for x, y in pts], fill=color, width=int(L.S(ancho)), joint="curve")
    for x, y in (pts[0], pts[-1]):     # puntas redondas
        r = ancho / 2
        L.d.ellipse((L.S(x - r), L.S(y - r), L.S(x + r), L.S(y + r)), fill=color)


def miembro(L, pts, color, ancho, tinta=True):
    """Brazo o pierna: trazo grueso con contorno de tinta."""
    if tinta:
        linea(L, pts, P["tinta"], ancho + 7)
    linea(L, pts, color, ancho)


def caja_red(L, x0, y0, x1, y1, r, relleno, borde=None, ancho=4):
    L.d.rounded_rectangle((L.S(x0), L.S(y0), L.S(x1), L.S(y1)), radius=L.S(r), fill=relleno,
                          outline=borde, width=int(L.S(ancho)) if borde else 0)


def cielo_bandas(L, colores, y0=0, y1=None):
    """Cielo plano en bandas (sin degradado suave: es el look recortado)."""
    y1 = y1 if y1 is not None else L.h
    n = len(colores)
    for i, c in enumerate(colores):
        a = y0 + (y1 - y0) * i / n
        b = y0 + (y1 - y0) * (i + 1) / n + 1
        L.d.rectangle((0, L.S(a), L.S(L.w), L.S(b)), fill=c)


def cerros(L, base_y, alto, color, semilla=1, n=5, borde=True):
    random.seed(semilla)
    pts = [(-20, L.h + 10), (-20, base_y)]
    xs = sorted(random.uniform(0, L.w) for _ in range(n))
    for x in xs:
        pts.append((x - 120, base_y - alto * random.uniform(0.2, 0.5)))
        pts.append((x, base_y - alto * random.uniform(0.6, 1.0)))
        pts.append((x + 140, base_y - alto * random.uniform(0.2, 0.45)))
    pts += [(L.w + 20, base_y), (L.w + 20, L.h + 10)]
    poligono(L, pts, color, P["tinta"] if borde else None, 4)


def flecha(L, x0, y0, x1, y1, color, ancho=18, u=1.0, borde=True):
    if u <= 0.02:
        return
    x1 = x0 + (x1 - x0) * u
    y1 = y0 + (y1 - y0) * u
    a = math.atan2(y1 - y0, x1 - x0)
    cab = ancho * 2.4
    bx, by = x1 - cab * math.cos(a), y1 - cab * math.sin(a)
    if borde:
        linea(L, [(x0, y0), (bx, by)], P["tinta"], ancho + 8)
    linea(L, [(x0, y0), (bx, by)], color, ancho)
    pts = [(x1, y1), (bx + cab * 0.6 * math.cos(a + math.pi / 2), by + cab * 0.6 * math.sin(a + math.pi / 2)),
           (bx + cab * 0.6 * math.cos(a - math.pi / 2), by + cab * 0.6 * math.sin(a - math.pi / 2))]
    poligono(L, pts, color, P["tinta"] if borde else None, 4)


def texto(L, s, x, y, tam=64, color=None, fuente=FONT, ancla="mm", borde=0, color_borde=None):
    f = ImageFont.truetype(fuente, int(L.S(tam)))
    L.d.text(L.pt(x, y), s, font=f, fill=color or P["tinta"], anchor=ancla,
             stroke_width=int(L.S(borde)), stroke_fill=color_borde or P["tinta"])


def pildora(L, s, cx, cy, tam=52, fondo=None, tinta=None, escala=1.0):
    if escala <= 0.02:
        return
    f = ImageFont.truetype(FONT, int(L.S(tam * escala)))
    tw = f.getlength(s) / L.ss
    w, h = tw + 56 * escala, tam * 1.5 * escala
    caja_red(L, cx - w / 2 + 5, cy - h / 2 + 7, cx + w / 2 + 5, cy + h / 2 + 7, h / 2, (0, 0, 0, 70))
    caja_red(L, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, h / 2, fondo or P["blanco"], P["tinta"], 4)
    L.d.text(L.pt(cx, cy), s, font=f, fill=tinta or P["tinta"], anchor="mm")


def grano(im, fuerza=10, semilla=0):
    """Grano de papel fijo (la misma textura en todo el video: no titila)."""
    random.seed(semilla)
    g = Image.effect_noise(im.size, fuerza).convert("RGB")
    return Image.blend(im, Image.composite(im, g, Image.new("L", im.size, 230)), 0.35)


# ------------------------------------------------------------------ mapa
_GEO = {}


def cargar_paises(ruta):
    if ruta not in _GEO:
        _GEO[ruta] = json.load(open(ruta))["features"]
    return _GEO[ruta]


def proyectar(lon, lat, centro, escala):
    """Mercator simple: (lon, lat) → píxeles; centro = (lon, lat, x_px, y_px); escala = px por radián."""
    lo0, la0, x0, y0 = centro
    def m(la):
        la = max(-80, min(80, la))
        return math.log(math.tan(math.pi / 4 + math.radians(la) / 2))
    return x0 + (math.radians(lon - lo0)) * escala, y0 - (m(lat) - m(la0)) * escala


def mapa(L, ruta, centro, escala, colores=None, borde=True, mar=None):
    """Dibuja todos los países; colores = {ISO_A3 o NAME: color}. Devuelve una función lon,lat → x,y."""
    L.d.rectangle((0, 0, L.S(L.w), L.S(L.h)), fill=mar or P["mar"])
    colores = colores or {}
    for f in cargar_paises(ruta):
        pr = f["properties"]
        c = colores.get(pr.get("ADM0_A3")) or colores.get(pr.get("NAME")) or P["tierra"]
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            anillo = poly[0]
            pts = [proyectar(lo, la, centro, escala) for lo, la in anillo]
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            if max(xs) < -50 or min(xs) > L.w + 50 or max(ys) < -50 or min(ys) > L.h + 50:
                continue
            poligono(L, pts, c, P["tinta"] if borde else None, 2.5)
    return lambda lo, la: proyectar(lo, la, centro, escala)


# ------------------------------------------------------------------ personajes
def persona(L, x, y, alto=420, ropa=None, pose=None, mira=1, t=0.0):
    """Silueta plana de pie con los pies en (x, y). ropa: colores y accesorios; pose: ángulos en grados.
    pose: brazo_izq, brazo_der (0 = colgando, 90 = adelante horizontal, 160 = arriba), saludo (True), paso (-1..1)."""
    ropa = dict({"torso": P["caqui"], "piernas": P["oliva"], "botas": P["cuero"], "piel": P["piel"], "cabeza": "casco_piloto"}, **(ropa or {}))
    pose = dict({"brazo_izq": 8, "brazo_der": 8, "paso": 0.0, "saludo": False}, **(pose or {}))
    k = alto / 420.0
    resp = math.sin(t * 2.2) * 3 * k
    cad_y = y - 190 * k
    hom_y = y - 330 * k + resp
    # piernas
    sep = 22 * k
    pa = pose["paso"]
    for lado, s in ((-1, -1), (1, 1)):
        px = x + lado * sep
        pie = (px + s * pa * 40 * k * mira, y - 6 * k)
        miembro(L, [(px, cad_y), ((px + pie[0]) / 2, (cad_y + y) / 2), pie], ropa["piernas"], 34 * k)
        caja_red(L, pie[0] - 26 * k + mira * 10 * k, y - 22 * k, pie[0] + 26 * k + mira * 10 * k, y + 4 * k, 9 * k, ropa["botas"], P["tinta"], 4)
    # torso
    caja_red(L, x - 62 * k, hom_y - 10 * k, x + 62 * k, cad_y + 16 * k, 30 * k, ropa["torso"], P["tinta"], 5)
    if ropa.get("chaleco"):
        caja_red(L, x - 56 * k, hom_y + 8 * k, x + 56 * k, cad_y - 20 * k, 22 * k, ropa["chaleco"], P["tinta"], 4)
    # brazos
    for lado, nombre in ((-1, "brazo_izq"), (1, "brazo_der")):
        hx = x + lado * 58 * k
        ang = math.radians(pose[nombre])
        if pose["saludo"] and nombre == "brazo_der":
            codo = (hx + 34 * k * mira, hom_y + 64 * k)
            mano = (x + 30 * k * mira, hom_y - 92 * k)
        else:
            L1 = 92 * k
            codo = (hx + mira * math.sin(ang) * L1 * 0.95, hom_y + math.cos(ang) * L1)
            mano = (codo[0] + mira * math.sin(ang * 1.1) * L1 * 0.9, codo[1] + math.cos(ang * 1.1) * L1 * 0.9)
        miembro(L, [(hx, hom_y + 12 * k), codo, mano], ropa["torso"], 28 * k)
        circulo(L, mano[0], mano[1], 14 * k, ropa["piel"], P["tinta"], 4)
    # cuello y cabeza
    cab_y = hom_y - 62 * k
    caja_red(L, x - 16 * k, cab_y + 30 * k, x + 16 * k, hom_y + 4 * k, 6 * k, ropa["piel2"] if "piel2" in ropa else P["piel2"], P["tinta"], 4)
    circulo(L, x, cab_y, 52 * k, ropa["piel"], P["tinta"], 5)
    cab = ropa["cabeza"]
    if cab == "casco_piloto":         # casco de cuero con antiparras y bufanda blanca
        L.d.chord((L.S(x - 56 * k), L.S(cab_y - 60 * k), L.S(x + 56 * k), L.S(cab_y + 50 * k)), 180, 360, fill=P["cuero"], outline=P["tinta"], width=int(L.S(5)))
        for s in (-1, 1):
            caja_red(L, x + s * 54 * k - 9 * k, cab_y - 6 * k, x + s * 54 * k + 9 * k, cab_y + 40 * k, 8 * k, P["cuero"], P["tinta"], 4)
        caja_red(L, x - 46 * k, cab_y - 48 * k, x + 46 * k, cab_y - 26 * k, 10 * k, P["gris"], P["tinta"], 4)
        for s in (-1, 1):
            circulo(L, x + s * 22 * k, cab_y - 37 * k, 15 * k, (170, 196, 206), P["tinta"], 4)
        caja_red(L, x - 40 * k, hom_y - 12 * k, x + 40 * k, hom_y + 14 * k, 12 * k, P["blanco"], P["tinta"], 4)
        if ropa.get("hachimaki"):
            caja_red(L, x - 52 * k, cab_y - 62 * k, x + 52 * k, cab_y - 48 * k, 6 * k, P["blanco"], P["tinta"], 3)
            circulo(L, x, cab_y - 55 * k, 6 * k, P["rojo"])
    elif cab == "gorra":              # gorra de oficial
        caja_red(L, x - 58 * k, cab_y - 58 * k, x + 58 * k, cab_y - 30 * k, 12 * k, ropa.get("gorra", P["oliva"]), P["tinta"], 4)
        caja_red(L, x - 30 * k * (1 - mira) - 6 * k, cab_y - 34 * k, x + 30 * k * (1 + mira) + 6 * k, cab_y - 22 * k, 5 * k, P["tinta"])
        circulo(L, x, cab_y - 46 * k, 7 * k, P["ocre"])
    elif cab == "casco_m1":           # casco redondo de la marina de EE.UU.
        L.d.chord((L.S(x - 66 * k), L.S(cab_y - 70 * k), L.S(x + 66 * k), L.S(cab_y + 30 * k)), 180, 360, fill=ropa.get("casco", P["gris"]), outline=P["tinta"], width=int(L.S(5)))
    # ojos (dos puntos) y boca simple
    for s in (-1, 1):
        circulo(L, x + s * 17 * k + mira * 8 * k, cab_y + 4 * k, 5.5 * k, P["tinta"])
    L.d.line([L.pt(x - 12 * k + mira * 8 * k, cab_y + 26 * k), L.pt(x + 12 * k + mira * 8 * k, cab_y + 26 * k)], fill=P["tinta"], width=int(L.S(4)))


def viejo(L, x, y, alto=520, boca=0.0, t=0.0, gesto="tazon", mira=-1):
    """El viejo del dato: boina roja, lentes redondos, bigote blanco, chaleco, tazón. boca 0..1 (con la voz)."""
    k = alto / 520.0
    bob = math.sin(t * 2.0) * 4 * k
    y = y + bob
    # cuerpo (chaleco sobre camisa)
    caja_red(L, x - 120 * k, y - 300 * k, x + 120 * k, y + 60 * k, 70 * k, (200, 186, 160), P["tinta"], 6)
    poligono(L, [(x - 112 * k, y - 250 * k), (x - 20 * k, y - 270 * k), (x - 4 * k, y + 60 * k), (x - 112 * k, y + 60 * k)], P["oliva"], P["tinta"], 5)
    poligono(L, [(x + 112 * k, y - 250 * k), (x + 20 * k, y - 270 * k), (x + 4 * k, y + 60 * k), (x + 112 * k, y + 60 * k)], P["oliva"], P["tinta"], 5)
    # brazo con el tazón (o apuntando)
    if gesto == "apunta":
        hx = x + mira * 110 * k
        miembro(L, [(hx, y - 230 * k), (hx + mira * 90 * k, y - 300 * k), (hx + mira * 170 * k, y - 370 * k)], (200, 186, 160), 42 * k)
        circulo(L, hx + mira * 170 * k, y - 370 * k, 22 * k, P["piel"], P["tinta"], 5)
        linea(L, [(hx + mira * 172 * k, y - 376 * k), (hx + mira * 210 * k, y - 412 * k)], P["tinta"], 16 * k)
        linea(L, [(hx + mira * 172 * k, y - 376 * k), (hx + mira * 206 * k, y - 410 * k)], P["piel"], 9 * k)
    else:
        hx = x + mira * 100 * k
        miembro(L, [(hx, y - 220 * k), (hx + mira * 40 * k, y - 120 * k), (hx - mira * 10 * k, y - 90 * k)], (200, 186, 160), 42 * k)
        caja_red(L, hx - mira * 10 * k - 34 * k, y - 150 * k, hx - mira * 10 * k + 34 * k, y - 70 * k, 12 * k, P["blanco"], P["tinta"], 5)
        circulo(L, hx - mira * 10 * k, y - 66 * k, 22 * k, P["piel"], P["tinta"], 5)
    # cabeza
    cy = y - 380 * k
    circulo(L, x, cy, 92 * k, P["piel"], P["tinta"], 6)
    # orejas
    for s in (-1, 1):
        circulo(L, x + s * 92 * k, cy + 10 * k, 20 * k, P["piel"], P["tinta"], 5)
    # boina roja (con el pitoncito)
    elipse(L, x - 6 * k, cy - 70 * k, 108 * k, 44 * k, P["rojo"], P["tinta"], 6)
    linea(L, [(x - 4 * k, cy - 112 * k), (x + 6 * k, cy - 128 * k)], P["tinta"], 10 * k)
    # lentes redondos
    for s in (-1, 1):
        circulo(L, x + s * 36 * k + mira * 6 * k, cy - 4 * k, 26 * k, (230, 240, 240, 200), P["tinta"], 5)
        circulo(L, x + s * 36 * k + mira * 10 * k, cy - 2 * k, 6 * k, P["tinta"])
    linea(L, [(x - 10 * k + mira * 6 * k, cy - 6 * k), (x + 10 * k + mira * 6 * k, cy - 6 * k)], P["tinta"], 5 * k)
    # nariz
    elipse(L, x + mira * 10 * k, cy + 26 * k, 16 * k, 14 * k, P["piel2"], P["tinta"], 4)
    # boca (se abre con la voz) bajo un bigote blanco grande
    ab = 4 + 24 * max(0.0, min(1.0, boca))
    elipse(L, x + mira * 8 * k, cy + 62 * k, 22 * k, ab * k, (110, 44, 40), P["tinta"], 4)
    poligono(L, [(x - 52 * k, cy + 48 * k), (x - 8 * k, cy + 34 * k), (x + mira * 8 * k, cy + 42 * k), (x + 8 * k, cy + 34 * k),
                 (x + 52 * k, cy + 48 * k), (x + 30 * k, cy + 56 * k), (x + mira * 8 * k, cy + 50 * k), (x - 30 * k, cy + 56 * k)],
             P["blanco"], P["tinta"], 4)


def avion_lateral(L, x, y, largo=420, mira=1, color=None, sol_rojo=True, helice_t=0.0, tinta=True):
    """Caza de hélice de perfil (silueta genérica de la época) centrado en (x, y), nariz hacia `mira`."""
    k = largo / 420.0
    c = color or (98, 112, 80)
    s = mira
    fus = [(x - 200 * k * s, y - 6 * k), (x - 150 * k * s, y - 22 * k), (x + 120 * k * s, y - 30 * k), (x + 190 * k * s, y - 18 * k),
           (x + 200 * k * s, y + 8 * k), (x + 120 * k * s, y + 26 * k), (x - 150 * k * s, y + 14 * k)]
    poligono(L, fus, c, P["tinta"] if tinta else None, 5)
    poligono(L, [(x - 170 * k * s, y - 14 * k), (x - 205 * k * s, y - 74 * k), (x - 180 * k * s, y - 76 * k), (x - 130 * k * s, y - 20 * k)], c, P["tinta"] if tinta else None, 5)
    poligono(L, [(x - 40 * k * s, y + 8 * k), (x + 70 * k * s, y + 8 * k), (x + 40 * k * s, y + 36 * k), (x - 70 * k * s, y + 36 * k)], c, P["tinta"] if tinta else None, 5)
    elipse(L, x + 40 * k * s, y - 34 * k, 50 * k, 18 * k, (170, 196, 206), P["tinta"] if tinta else None, 4)
    caja_red(L, x + 186 * k * s - 14 * k, y - 26 * k, x + 186 * k * s + 14 * k, y + 22 * k, 10 * k, P["tinta"])
    hl = 60 * k * abs(math.cos(helice_t * 40))
    linea(L, [(x + 204 * k * s, y - hl), (x + 204 * k * s, y + hl)], (70, 66, 60), 8 * k)
    if sol_rojo:
        circulo(L, x - 70 * k * s, y - 2 * k, 16 * k, P["rojo"], P["blanco"], 3)
