"""Ep. 16 — La tele de antes captaba el Big Bang. Arte nuevo (PIL sobre kit2d + arte.py del Ep. 15):
tele de los 60 con cara en la pantalla y lluvia, Big Bang chiquito con cara, living de los 60–70, sillón, antena de cuerno,
cielo de noche, científicos de los 60, palomas, caca, escoba, el cosmos, la Tierra con ondas, la luz que viaja, medalla, grilla de 100 puntos.
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw

import kit2d as K
from arte import C, TINTA, clamp, suave, sale, pop, estrella_golpe, nube

W, H = 1080, 1920
C16 = {
    "madera": (150, 92, 52), "madera2": (118, 70, 40), "madera3": (184, 122, 74), "bisel": (232, 220, 196), "bisel2": (204, 190, 166),
    "pant": (52, 56, 60), "perilla": (58, 52, 50), "oro": (246, 196, 80), "oro2": (214, 156, 50),
    "papel_m": (236, 170, 74), "papel_m2": (222, 148, 58), "papel_m3": (250, 206, 120), "piso": (168, 104, 62), "piso2": (146, 88, 52),
    "sillon": (120, 150, 104), "sillon2": (96, 124, 84), "lampara": (250, 224, 150),
    "noche": (24, 30, 64), "noche2": (40, 46, 96), "noche3": (66, 64, 128), "cerro": (40, 62, 70), "cerro2": (30, 48, 56),
    "metal": (196, 204, 212), "metal2": (150, 160, 172), "metal3": (110, 120, 134), "camisa": (250, 250, 246), "corbata": (52, 70, 120),
    "pantalon": (92, 92, 104), "pelo": (60, 44, 36), "pelo2": (110, 96, 86), "paloma": (150, 156, 170), "paloma2": (112, 118, 134),
    "cuello_v": (96, 170, 130), "cuello_m": (150, 110, 180), "cosmos": (14, 12, 40), "cosmos2": (34, 22, 74), "cosmos3": (70, 40, 120),
    "bang": (255, 246, 200), "bang2": (255, 170, 60), "bang3": (236, 74, 52), "luz": (255, 230, 120), "tierra_m": (70, 150, 220),
    "tierra_v": (110, 180, 100), "cinta": (200, 60, 60), "cinta2": (40, 80, 160), "carpeta": (252, 248, 236),
}


# ------------------------------------------------------------------ la lluvia (estática)
def _lluvia(L, x0, y0, x1, y1, t, radio=40, grano=7, oscuro=1.0, semilla=0):
    """Estática animada dentro de una caja redondeada (en coordenadas de 1080×1920)."""
    ss = L.ss
    w, h = int((x1 - x0) * ss), int((y1 - y0) * ss)
    if w < 4 or h < 4:
        return
    g = max(1, int(grano * ss))
    nw, nh = max(1, w // g), max(1, h // g)
    rng = np.random.default_rng(int(t * 30) * 7919 + semilla)
    a = rng.integers(20, 235, size=(nh, nw)).astype(np.float32)
    # bandas horizontales que bajan (como la tele de verdad)
    fil = np.arange(nh)[:, None]
    banda = 0.82 + 0.18 * np.sin(fil * 0.35 + t * 9.0)
    a = a * banda * oscuro
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "L").resize((w, h), Image.NEAREST).convert("RGB")
    # viñeta del tubo
    vig = Image.new("L", (w, h), 0)
    dv = ImageDraw.Draw(vig)
    for i in range(10):
        f = i / 10
        dv.rounded_rectangle((int(w * f * 0.12), int(h * f * 0.12), int(w * (1 - f * 0.12)), int(h * (1 - f * 0.12))), int(radio * ss), fill=int(255 * (0.35 + 0.65 * f)))
    im = Image.composite(im, Image.new("RGB", (w, h), (18, 18, 20)), vig)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), int(radio * ss), fill=255)
    L.im.paste(im, (int(x0 * ss), int(y0 * ss)), m)


def ojos_cara(L, cx, cy, s, cara="normal", t=0.0, mira=(0.0, 0.0)):
    """Ojos grandes y boca de dibujo animado (para la pantalla de la tele)."""
    parp = ((t + 1.7) % 3.7) < 0.12 and cara in ("normal", "orgullo", "feliz")
    for sg in (-1, 1):
        ex, ey = cx + sg * 105 * s, cy - 30 * s
        K.elipse(L, ex, ey, 62 * s, 70 * s, (0, 0, 0, 110))                                  # halo para despegarlo de la lluvia
        if cara == "mareado":
            K.elipse(L, ex, ey, 50 * s, 58 * s, C["blanco"], TINTA, 8 * s)
            for k in range(3):
                r = (12 + k * 13) * s
                L.d.arc((L.S(ex - r), L.S(ey - r), L.S(ex + r), L.S(ey + r)), 40 + k * 90 + t * 600, 320 + k * 90 + t * 600, fill=TINTA, width=int(L.S(6 * s)))
            continue
        if cara == "aburrido":
            K.elipse(L, ex, ey, 50 * s, 58 * s, C["blanco"], TINTA, 8 * s)
            K.circulo(L, ex + mira[0] * 14 * s, ey + 10 * s, 18 * s, TINTA)
            L.d.chord((L.S(ex - 54 * s), L.S(ey - 62 * s), L.S(ex + 54 * s), L.S(ey + 54 * s)), 180, 360, fill=C16["pant"], outline=TINTA, width=int(L.S(8 * s)))
            continue
        if parp:
            K.linea(L, [(ex - 44 * s, ey), (ex + 44 * s, ey)], TINTA, 10 * s)
            continue
        big = 1.18 if cara == "sorpresa" else 1.0
        K.elipse(L, ex, ey, 50 * s * big, 58 * s * big, C["blanco"], TINTA, 8 * s)
        pr = 22 * s if cara != "sorpresa" else 15 * s
        K.circulo(L, ex + mira[0] * 16 * s, ey + mira[1] * 16 * s + 6 * s, pr, TINTA)
        K.circulo(L, ex + mira[0] * 16 * s - pr * 0.35, ey + mira[1] * 16 * s - pr * 0.3, pr * 0.32, C["blanco"])
        if cara == "orgullo":
            K.linea(L, [(ex - 46 * s, ey - 84 * s), (ex + 40 * s, ey - 74 * s - sg * 8 * s)], TINTA, 10 * s)
    # boca
    my = cy + 92 * s
    if cara in ("normal", "feliz", "orgullo"):
        L.d.chord((L.S(cx - 70 * s), L.S(my - 50 * s), L.S(cx + 70 * s), L.S(my + 44 * s)), 0, 180, fill=(120, 40, 40), outline=TINTA, width=int(L.S(8 * s)))
        L.d.chord((L.S(cx - 34 * s), L.S(my + 6 * s), L.S(cx + 34 * s), L.S(my + 44 * s)), 0, 180, fill=(236, 110, 110))
    elif cara == "sorpresa":
        K.elipse(L, cx, my + 6 * s, 30 * s, 38 * s, (120, 40, 40), TINTA, 8 * s)
    elif cara == "aburrido":
        K.linea(L, [(cx - 46 * s, my), (cx + 46 * s, my + 6 * s)], TINTA, 10 * s)
    elif cara == "mareado":
        pts = [(cx - 60 * s + i * 12 * s, my + math.sin(i * 1.3 + t * 12) * 9 * s) for i in range(11)]
        K.linea(L, pts, TINTA, 10 * s)


def tele(L, cx, cy, w=760, t=0.0, cara="normal", lluvia=True, ojos=True, temblor=0.0, carpeta=False, antena=1.0,
         pantalla=None, salto=0.0, mira=(0.0, 0.0), semilla=0):
    """Tele de los 60: mueble de madera, pantalla de tubo con lluvia, perillas, patas y antena de conejo.
    (cx, cy) = centro del mueble. pantalla(L, x0, y0, x1, y1) dibuja otra cosa en la pantalla."""
    s = w / 760.0
    dx = math.sin(t * 61) * 10 * temblor * s
    dy = -abs(math.sin(t * 9)) * 30 * salto * s
    cx, cy = cx + dx, cy + dy
    hw, hh = 380 * s, 300 * s
    # patas (mid-century)
    for sg in (-1, 1):
        K.poligono(L, [(cx + sg * 250 * s, cy + hh - 10 * s), (cx + sg * 300 * s, cy + hh - 10 * s), (cx + sg * 340 * s, cy + hh + 150 * s),
                       (cx + sg * 318 * s, cy + hh + 154 * s)], C16["madera2"], TINTA, 7 * s)
    # antena de conejo
    if antena > 0:
        for sg, an in ((-1, -0.42), (1, 0.38)):
            a = an + math.sin(t * 1.6 + sg) * 0.03
            ln = 330 * s * antena
            px, py = cx + sg * 30 * s, cy - hh - 40 * s
            ex, ey = px + math.sin(a) * ln, py - math.cos(a) * ln
            K.linea(L, [(px, py), (ex, ey)], TINTA, 15 * s)
            K.linea(L, [(px, py), (ex, ey)], C16["metal"], 8 * s)
            K.circulo(L, ex, ey, 16 * s, C16["metal2"], TINTA, 6 * s)
        L.d.chord((L.S(cx - 80 * s), L.S(cy - hh - 80 * s), L.S(cx + 80 * s), L.S(cy - hh + 40 * s)), 180, 360, fill=C16["perilla"], outline=TINTA, width=int(L.S(7 * s)))
    # mueble
    K.caja_red(L, cx - hw + 10 * s, cy - hh + 16 * s, cx + hw + 10 * s, cy + hh + 16 * s, 60 * s, (0, 0, 0, 70))
    K.caja_red(L, cx - hw, cy - hh, cx + hw, cy + hh, 60 * s, C16["madera"], TINTA, 9 * s)
    for k in range(5):                                                                    # veta de la madera
        yy = cy - hh + 40 * s + k * 120 * s
        K.linea(L, [(cx - hw + 30 * s, yy), (cx - hw + 120 * s, yy + 8 * s)], C16["madera3"], 5 * s)
        K.linea(L, [(cx + hw - 140 * s, yy + 50 * s), (cx + hw - 40 * s, yy + 44 * s)], C16["madera2"], 5 * s)
    # bisel y pantalla
    bx0, by0, bx1, by1 = cx - hw + 46 * s, cy - hh + 40 * s, cx + hw - 46 * s, cy + hh - 110 * s
    K.caja_red(L, bx0, by0, bx1, by1, 70 * s, C16["bisel"], TINTA, 7 * s)
    px0, py0, px1, py1 = bx0 + 34 * s, by0 + 30 * s, bx1 - 34 * s, by1 - 30 * s
    K.caja_red(L, px0, py0, px1, py1, 60 * s, C16["pant"], TINTA, 7 * s)
    if pantalla:
        pantalla(L, px0, py0, px1, py1)
    elif lluvia:
        _lluvia(L, px0 + 4 * s, py0 + 4 * s, px1 - 4 * s, py1 - 4 * s, t, radio=56 * s, grano=7 * s, oscuro=0.8, semilla=semilla)
    # brillo del vidrio
    K.poligono(L, [(px0 + 40 * s, py0 + 30 * s), (px0 + 200 * s, py0 + 26 * s), (px0 + 60 * s, py0 + 130 * s)], (255, 255, 255, 60))
    if ojos and not pantalla:
        ojos_cara(L, (px0 + px1) / 2, (py0 + py1) / 2, s * 1.05, cara, t, mira)
    # perillas y parlante
    for k, xx in enumerate((cx + hw - 120 * s, cx + hw - 230 * s)):
        K.circulo(L, xx, cy + hh - 55 * s, 30 * s, C16["perilla"], TINTA, 6 * s)
        an = t * 0.7 + k
        K.linea(L, [(xx, cy + hh - 55 * s), (xx + math.cos(an) * 22 * s, cy + hh - 55 * s + math.sin(an) * 22 * s)], C16["bisel"], 5 * s)
    for k in range(5):
        K.linea(L, [(cx - hw + 70 * s + k * 34 * s, cy + hh - 78 * s), (cx - hw + 70 * s + k * 34 * s, cy + hh - 32 * s)], C16["madera2"], 10 * s)
    if carpeta:
        carpeta_tejida(L, cx + 140 * s, cy - hh, 120 * s)
    return (px0, py0, px1, py1)


def carpeta_tejida(L, cx, y, r):
    """La carpetita a crochet sobre la tele (con su figurita)."""
    for k in range(14):
        an = math.pi + k * math.pi / 13
        K.circulo(L, cx + math.cos(an) * r, y + math.sin(an) * r * 0.28 + 4, r * 0.16, C16["carpeta"], TINTA, 4)
    L.d.chord((L.S(cx - r), L.S(y - r * 0.3), L.S(cx + r), L.S(y + r * 0.3)), 180, 360, fill=C16["carpeta"], outline=TINTA, width=int(L.S(4)))
    # figurita (un perrito de loza)
    K.elipse(L, cx, y - 36, 34, 26, (240, 236, 226), TINTA, 4)
    K.circulo(L, cx + 30, y - 64, 20, (240, 236, 226), TINTA, 4)
    K.elipse(L, cx + 42, y - 82, 8, 14, (120, 80, 60), TINTA, 3)
    K.circulo(L, cx + 36, y - 66, 4, TINTA)


# ------------------------------------------------------------------ el Big Bang chiquito (símbolo que se repite)
def bang(L, x, y, r, t=0.0, cara="feliz", brillo=1.0, rot=None, chispas_n=10):
    """Explosión con cara: picos irregulares (no un sol), dos capas, chispas que salen."""
    if r < 3:
        return
    rot = t * 0.5 if rot is None else rot
    for k in range(4, 0, -1):
        K.circulo(L, x, y, r * (1 + k * 0.3 * brillo), (255, 200, 110, int(30 * brillo)))
    rnd = random.Random(31)
    largos = [rnd.uniform(1.2, 2.25) for _ in range(18)]
    for capa, (col, esc) in enumerate(((C16["bang3"], 1.0), (C16["bang2"], 0.78))):
        pts = []
        for i in range(36):
            an = i * math.pi / 18 + rot * (1 if capa == 0 else -0.6)
            if i % 2 == 0:
                rr = r * largos[i // 2] * esc * (1 + 0.07 * math.sin(t * 9 + i))
            else:
                rr = r * 0.92 * esc
            pts.append((x + math.cos(an) * rr, y + math.sin(an) * rr))
        K.poligono(L, pts, col, TINTA, max(3, 6 * r / 100))
    if chispas_n:
        for i in range(chispas_n):
            an = rnd.uniform(0, math.tau)
            f = (t * 0.9 + i / chispas_n) % 1.0
            d = r * (1.6 + 1.6 * f)
            sz = r * 0.09 * (1 - f) + 2
            K.circulo(L, x + math.cos(an) * d, y + math.sin(an) * d, sz, C16["bang"], TINTA, 3)
    K.circulo(L, x, y, r * 0.86, C16["bang"], TINTA, max(3, 6 * r / 100))
    k = r / 100
    if cara == "ay":
        for sg in (-1, 1):
            ex, ey = x + sg * 30 * k, y - 12 * k
            K.linea(L, [(ex - 12 * k, ey - 12 * k), (ex + 12 * k, ey + 12 * k)], TINTA, 7 * k)
            K.linea(L, [(ex - 12 * k, ey + 12 * k), (ex + 12 * k, ey - 12 * k)], TINTA, 7 * k)
        K.elipse(L, x, y + 32 * k, 15 * k, 19 * k, (140, 50, 40), TINTA, 5 * k)
        return
    parp = ((t + 1.4) % 2.9) < 0.1
    for sg in (-1, 1):
        ex, ey = x + sg * 30 * k, y - 12 * k
        if parp:
            K.linea(L, [(ex - 11 * k, ey), (ex + 11 * k, ey)], TINTA, 6 * k)
        else:
            K.elipse(L, ex, ey, 10 * k, 14 * k, TINTA)
            K.circulo(L, ex - 3 * k, ey - 5 * k, 4 * k, C["blanco"])
        K.elipse(L, x + sg * 50 * k, y + 16 * k, 12 * k, 7 * k, (255, 140, 110, 170))
    if cara == "sorpresa":
        K.elipse(L, x, y + 30 * k, 12 * k, 15 * k, (140, 50, 40), TINTA, 5 * k)
    else:
        L.d.chord((L.S(x - 24 * k), L.S(y + 4 * k), L.S(x + 24 * k), L.S(y + 42 * k)), 0, 180, fill=(140, 50, 40), outline=TINTA, width=int(L.S(5 * k)))


def palma(L, x, y, s=1.0, ang=0.0, piel=None, manga=None):
    """Mano abierta que pega (palma de frente). ang en radianes: hacia dónde apuntan los dedos."""
    piel = piel or C["piel"]
    ca, sa = math.cos(ang), math.sin(ang)
    def R(dx, dy):
        return (x + dx * ca - dy * sa, y + dx * sa + dy * ca)
    if manga:
        K.linea(L, [R(-260 * s, 0), R(-70 * s, 0)], TINTA, 96 * s)
        K.linea(L, [R(-260 * s, 0), R(-70 * s, 0)], manga, 82 * s)
    for k, (dy, ln) in enumerate(((-48, 92), (-16, 110), (16, 104), (46, 84))):
        p0, p1 = R(20 * s, dy * s), R((20 + ln) * s, dy * 1.15 * s)
        K.linea(L, [p0, p1], TINTA, 36 * s)
        K.linea(L, [p0, p1], piel, 25 * s)
    p0, p1 = R(-20 * s, -60 * s), R(30 * s, -120 * s)
    K.linea(L, [p0, p1], TINTA, 38 * s)
    K.linea(L, [p0, p1], piel, 27 * s)
    K.circulo(L, x, y, 72 * s, piel, TINTA, 6)


def confeti(L, t, t0, n=40, semilla=5, y_max=1000):
    if t < t0:
        return
    e = t - t0
    rnd = random.Random(semilla)
    cols = [C["amarillo"], C["coral"], C["menta"], (150, 190, 255), (255, 170, 200)]
    for i in range(n):
        x0 = rnd.uniform(60, W - 60)
        v = rnd.uniform(260, 520)
        y = -40 + v * e
        if y > y_max:
            continue
        x = x0 + math.sin(e * 3 + i) * 40
        an = e * 6 + i
        w, h = 22, 12
        K.poligono(L, [(x + math.cos(an) * w, y + math.sin(an) * h), (x - math.sin(an) * h, y + math.cos(an) * w),
                       (x - math.cos(an) * w, y - math.sin(an) * h), (x + math.sin(an) * h, y - math.cos(an) * w)], cols[i % len(cols)], TINTA, 2)


def chispas(L, x, y, r, t, n=6, color=None, semilla=1):
    """Estrellitas de 4 puntas dibujadas (nada de glifos Unicode: lección 163)."""
    random.seed(semilla)
    for i in range(n):
        an = random.uniform(0, math.tau)
        d = r * random.uniform(0.7, 1.3)
        f = (t * 1.3 + i / n) % 1.0
        sz = 18 * math.sin(math.pi * f) + 4
        px, py = x + math.cos(an) * d, y + math.sin(an) * d
        K.poligono(L, [(px, py - sz), (px + sz * 0.3, py - sz * 0.3), (px + sz, py), (px + sz * 0.3, py + sz * 0.3), (px, py + sz),
                       (px - sz * 0.3, py + sz * 0.3), (px - sz, py), (px - sz * 0.3, py - sz * 0.3)], color or C16["luz"], TINTA, 3)


# ------------------------------------------------------------------ el living de los 60–70
def living(L, t=0.0, piso_y=1180, lampara=True):
    L.d.rectangle((0, 0, L.S(W), L.S(piso_y)), fill=C16["papel_m"])
    for i in range(-1, 12):                                                               # papel mural: franjas y flores
        x = i * 110
        L.d.rectangle((L.S(x), 0, L.S(x + 40), L.S(piso_y)), fill=C16["papel_m2"])
    for j in range(9):
        for i in range(6):
            x = i * 220 + (110 if j % 2 else 0) - 30
            y = j * 150 + 60
            for k in range(6):
                an = k * math.pi / 3
                K.circulo(L, x + math.cos(an) * 20, y + math.sin(an) * 20, 13, C16["papel_m3"])
            K.circulo(L, x, y, 11, C16["madera3"])
    L.d.rectangle((0, L.S(piso_y), L.S(W), L.S(H)), fill=C16["piso"])
    for k in range(9):
        yy = piso_y + 40 + k * 90
        K.linea(L, [(0, yy), (W, yy)], C16["piso2"], 6)
    L.d.rectangle((0, L.S(piso_y - 30), L.S(W), L.S(piso_y)), fill=C16["madera2"])
    K.linea(L, [(0, piso_y - 30), (W, piso_y - 30)], TINTA, 6)
    if lampara:
        K.linea(L, [(95, 300), (95, piso_y - 20)], TINTA, 16)
        K.linea(L, [(95, 300), (95, piso_y - 20)], C16["oro2"], 8)
        K.poligono(L, [(30, 300), (160, 300), (130, 170), (60, 170)], C16["lampara"], TINTA, 6)
        K.circulo(L, 95, 330, 90, (255, 240, 180, 50))


def sillon_atras(L, x, y, s=1.0):
    K.caja_red(L, x - 230 * s, y - 520 * s, x + 230 * s, y + 40 * s, 110 * s, C16["sillon"], TINTA, 8)
    K.caja_red(L, x - 180 * s, y - 470 * s, x + 180 * s, y - 60 * s, 90 * s, C16["sillon2"])


def sillon_frente(L, x, y, s=1.0):
    for sg in (-1, 1):
        K.caja_red(L, x + sg * 200 * s - 70 * s, y - 220 * s, x + sg * 200 * s + 70 * s, y + 120 * s, 60 * s, C16["sillon"], TINTA, 8)
    K.caja_red(L, x - 210 * s, y - 40 * s, x + 210 * s, y + 140 * s, 50 * s, C16["sillon2"], TINTA, 8)


# ------------------------------------------------------------------ noche, cerro y antena de cuerno
def noche(L, t=0.0, horizonte=960, estrellas=70):
    K.cielo_bandas(L, [C16["noche"], C16["noche"], C16["noche2"], C16["noche3"]], 0, horizonte)
    random.seed(11)
    for i in range(estrellas):
        x, y = random.uniform(0, W), random.uniform(0, horizonte - 80)
        r = random.uniform(2, 5) * (0.7 + 0.3 * math.sin(t * 3 + i))
        K.circulo(L, x, y, r, (255, 250, 220))
    K.circulo(L, 860, 230, 70, (250, 244, 214), TINTA, 5)
    K.circulo(L, 880, 210, 70, C16["noche"])                                              # luna en cuarto
    K.poligono(L, [(0, horizonte + 30), (240, horizonte - 50), (560, horizonte - 10), (820, horizonte - 70), (W, horizonte - 20), (W, H), (0, H)], C16["cerro"], TINTA, 7)
    L.d.rectangle((0, L.S(horizonte + 120), L.S(W), L.S(H)), fill=C16["cerro2"])


def cuerno(L, x, y, s=1.0, t=0.0, boca=True):
    """Antena de cuerno (pirámide acostada) sobre su base giratoria. (x, y) = centro de la boca; el cuerno se angosta a la izquierda."""
    # base: armazón y riel
    K.caja_red(L, x - 520 * s, y + 230 * s, x + 220 * s, y + 280 * s, 20 * s, C16["metal3"], TINTA, 6)
    for k in range(6):
        xx = x - 480 * s + k * 130 * s
        K.linea(L, [(xx, y + 230 * s), (xx + 60 * s, y + 40 * s)], TINTA, 13 * s)
        K.linea(L, [(xx, y + 230 * s), (xx + 60 * s, y + 40 * s)], C16["metal2"], 7 * s)
    # cuerno: de la cabina (izq, chica) a la boca (der, grande)
    top = [(x - 560 * s, y - 40 * s), (x - 20 * s, y - 250 * s), (x + 60 * s, y - 210 * s), (x + 60 * s, y + 210 * s), (x - 20 * s, y + 230 * s), (x - 560 * s, y + 40 * s)]
    K.poligono(L, top, C16["metal"], TINTA, 8)
    K.poligono(L, [(x - 560 * s, y - 40 * s), (x - 20 * s, y - 250 * s), (x - 20 * s, y + 230 * s), (x - 560 * s, y + 40 * s)], C16["metal2"])
    for k in range(1, 7):                                                                 # costillas
        u = k / 7
        xx = x - 560 * s + 540 * s * u
        K.linea(L, [(xx, y - 40 * s - 210 * s * u), (xx, y + 40 * s + 190 * s * u)], C16["metal3"], 5 * s)
    K.linea(L, [(x - 560 * s, y - 40 * s), (x - 20 * s, y - 250 * s)], TINTA, 8 * s)
    K.linea(L, [(x - 560 * s, y + 40 * s), (x - 20 * s, y + 230 * s)], TINTA, 8 * s)
    # cabina al fondo
    K.caja_red(L, x - 660 * s, y - 70 * s, x - 540 * s, y + 70 * s, 12 * s, C16["metal3"], TINTA, 6)
    # boca (cuadro oscuro, en perspectiva)
    if boca:
        K.poligono(L, [(x - 20 * s, y - 250 * s), (x + 60 * s, y - 210 * s), (x + 60 * s, y + 210 * s), (x - 20 * s, y + 230 * s)], (20, 22, 30), TINTA, 7)


def ruido_txt(L, x, y, t, s=1.0, n=2, color=None, tam=66, ang=-0.15):
    """'KSSSHH' (la estática) que sale en ondas, sin encimarse y dentro del cuadro."""
    for i in range(n):
        f = (t * 0.7 + i / n) % 1.0
        a = int(255 * math.sin(math.pi * f))
        xx = min(x + math.cos(ang) * 150 * f * s, 700)
        yy = y + 120 * i + math.sin(ang) * 150 * f * s
        if a > 10:
            col = color or (255, 255, 255)
            K.texto(L, "KSSSHH", xx, yy, tam * s * (0.85 + 0.3 * f), (col[0], col[1], col[2], a), borde=6, color_borde=(30, 30, 40, a))


# ------------------------------------------------------------------ científicos de los 60
def cientifico(L, x, y, alto=520, t=0.0, cara="normal", mira=1, brazo=None, pelo="corto", lentes=True, audifonos=False, medalla=0.0):
    """De pie, pies en (x, y). brazo: None | 'apunta' | 'arriba' | 'escoba' | 'oreja'."""
    k = alto / 520.0
    bob = math.sin(t * 2.4 + x) * 3 * k
    hy = y - 360 * k + bob                                                                # hombros
    # piernas y zapatos
    for sg in (-1, 1):
        K.miembro(L, [(x + sg * 30 * k, y - 190 * k), (x + sg * 32 * k, y - 20 * k)], C16["pantalon"], 44 * k)
        K.caja_red(L, x + sg * 30 * k - 32 * k + mira * 10 * k, y - 26 * k, x + sg * 30 * k + 32 * k + mira * 10 * k, y + 4 * k, 10 * k, TINTA)
    # torso (camisa blanca y corbata)
    K.caja_red(L, x - 78 * k, hy - 14 * k, x + 78 * k, y - 170 * k, 40 * k, C16["camisa"], TINTA, 6)
    K.poligono(L, [(x - 12 * k, hy - 4 * k), (x + 12 * k, hy - 4 * k), (x + 18 * k, hy + 150 * k), (x, hy + 172 * k), (x - 18 * k, hy + 150 * k)], C16["corbata"], TINTA, 4)
    K.caja_red(L, x - 80 * k, y - 205 * k, x + 80 * k, y - 172 * k, 10 * k, TINTA)                 # cinturón
    # brazos
    for sg in (-1, 1):
        hx = x + sg * 74 * k
        if brazo == "apunta" and sg == mira:
            mano = (hx + mira * 190 * k, hy - 40 * k)
            K.miembro(L, [(hx, hy + 10 * k), (hx + mira * 95 * k, hy - 10 * k), mano], C16["camisa"], 38 * k)
        elif brazo == "arriba":
            mano = (hx + sg * 70 * k, hy - 170 * k)
            K.miembro(L, [(hx, hy + 10 * k), (hx + sg * 60 * k, hy - 70 * k), mano], C16["camisa"], 38 * k)
        elif brazo == "oreja":
            mano = (x + sg * 70 * k, hy - 110 * k)
            K.miembro(L, [(hx, hy + 10 * k), (hx + sg * 50 * k, hy + 60 * k), mano], C16["camisa"], 38 * k)
        elif brazo == "escoba":
            mano = (x + mira * (40 + sg * 30) * k + math.sin(t * 12) * 30 * k, hy + 120 * k + sg * 30 * k)
            K.miembro(L, [(hx, hy + 10 * k), (hx + sg * 10 * k, hy + 90 * k), mano], C16["camisa"], 38 * k)
        else:
            mano = (hx + sg * 14 * k, hy + 190 * k)
            K.miembro(L, [(hx, hy + 10 * k), (hx + sg * 16 * k, hy + 100 * k), mano], C16["camisa"], 38 * k)
        K.circulo(L, mano[0], mano[1], 20 * k, C["piel"], TINTA, 5)
    if brazo == "escoba":
        bx = x + mira * 60 * k + math.sin(t * 12) * 30 * k
        K.linea(L, [(bx, hy + 40 * k), (bx + mira * 120 * k, y + 0 * k)], TINTA, 16 * k)
        K.linea(L, [(bx, hy + 40 * k), (bx + mira * 120 * k, y + 0 * k)], C["madera"], 9 * k)
        K.poligono(L, [(bx + mira * 80 * k, y - 10 * k), (bx + mira * 170 * k, y - 10 * k), (bx + mira * 190 * k, y + 20 * k), (bx + mira * 60 * k, y + 20 * k)], C["trigo"], TINTA, 5)
    # cabeza
    cy = hy - 92 * k
    K.caja_red(L, x - 18 * k, cy + 40 * k, x + 18 * k, hy + 6 * k, 6 * k, C["piel2"], TINTA, 4)
    K.circulo(L, x, cy, 80 * k, C["piel"], TINTA, 6)
    for sg in (-1, 1):
        K.circulo(L, x + sg * 80 * k, cy + 8 * k, 16 * k, C["piel"], TINTA, 5)
    if pelo == "corto":
        L.d.chord((L.S(x - 84 * k), L.S(cy - 92 * k), L.S(x + 84 * k), L.S(cy + 30 * k)), 190, 350, fill=C16["pelo"], outline=TINTA, width=int(L.S(5)))
        K.caja_red(L, x - 70 * k, cy - 96 * k, x + 70 * k, cy - 54 * k, 18 * k, C16["pelo"], TINTA, 5)
    else:                                                                                  # pelado con los lados
        for sg in (-1, 1):
            K.elipse(L, x + sg * 70 * k, cy - 20 * k, 20 * k, 34 * k, C16["pelo2"], TINTA, 4)
    if audifonos:
        L.d.arc((L.S(x - 96 * k), L.S(cy - 110 * k), L.S(x + 96 * k), L.S(cy + 60 * k)), 190, 350, fill=TINTA, width=int(L.S(14 * k)))
        for sg in (-1, 1):
            K.caja_red(L, x + sg * 88 * k - 20 * k, cy - 20 * k, x + sg * 88 * k + 20 * k, cy + 40 * k, 12 * k, (60, 60, 70), TINTA, 5)
    # cara
    ox = mira * 10 * k
    for sg in (-1, 1):
        ex, ey = x + sg * 30 * k + ox, cy - 4 * k
        if cara == "molesto":
            K.linea(L, [(ex - 18 * k, ey - 26 * k + sg * 6 * k), (ex + 18 * k, ey - 26 * k - sg * 6 * k)], TINTA, 7 * k)
        if cara == "feliz":
            L.d.arc((L.S(ex - 12 * k), L.S(ey - 8 * k), L.S(ex + 12 * k), L.S(ey + 12 * k)), 200, 340, fill=TINTA, width=int(L.S(6 * k)))
        else:
            K.circulo(L, ex, ey, 8 * k if cara != "sorpresa" else 10 * k, TINTA)
        if lentes:
            K.circulo(L, ex, ey, 22 * k, (220, 236, 240, 90), TINTA, 5)
    if lentes:
        K.linea(L, [(x - 8 * k + ox, cy - 6 * k), (x + 8 * k + ox, cy - 6 * k)], TINTA, 5 * k)
    my = cy + 40 * k
    if cara == "feliz":
        L.d.chord((L.S(x - 30 * k + ox), L.S(my - 22 * k), L.S(x + 30 * k + ox), L.S(my + 22 * k)), 0, 180, fill=(140, 50, 40), outline=TINTA, width=int(L.S(5)))
    elif cara == "sorpresa":
        K.elipse(L, x + ox, my + 4 * k, 12 * k, 16 * k, (140, 50, 40), TINTA, 5)
    elif cara == "molesto":
        pts = [(x - 26 * k + ox + i * 8.6 * k, my + 4 * k + (6 * k if i % 2 else -2 * k)) for i in range(7)]
        K.linea(L, pts, TINTA, 6 * k)
    else:
        K.linea(L, [(x - 20 * k + ox, my), (x + 20 * k + ox, my + 2 * k)], TINTA, 6 * k)
    if medalla > 0:
        u = clamp(medalla)
        my2 = hy + 20 * k - (1 - u) * 400 * k
        K.linea(L, [(x - 50 * k, hy - 6 * k), (x, my2 + 70 * k)], C16["cinta2"], 14 * k)
        K.linea(L, [(x + 50 * k, hy - 6 * k), (x, my2 + 70 * k)], C16["cinta"], 14 * k)
        medalla_d(L, x, my2 + 110 * k, 48 * k, t)


def medalla_d(L, x, y, r, t=0.0):
    K.circulo(L, x, y, r * 1.12, C16["oro2"], TINTA, 6)
    K.circulo(L, x, y, r * 0.86, C16["oro"], TINTA, 4)
    pts = []
    for i in range(10):
        an = -math.pi / 2 + i * math.pi / 5
        rr = r * (0.56 if i % 2 == 0 else 0.24)
        pts.append((x + math.cos(an) * rr, y + math.sin(an) * rr))
    K.poligono(L, pts, C16["oro2"], TINTA, 3)
    an = t * 2.0
    K.linea(L, [(x - r * 0.5, y - r * 0.6), (x - r * 0.2, y - r * 0.75)], (255, 255, 255, 160), max(2, r * 0.12))


# ------------------------------------------------------------------ palomas
def paloma(L, x, y, s=1.0, t=0.0, mira=1, cara="normal", vuela=0.0):
    """Paloma gris con cuello tornasol. (x, y) = pies. vuela 0..1 = alas abiertas aleteando."""
    k = s
    bob = math.sin(t * 5 + x) * 4 * k * (1 - vuela)
    by = y - 70 * k + bob
    if vuela <= 0.05:
        for sg in (-1, 1):
            K.linea(L, [(x + sg * 14 * k, by + 30 * k), (x + sg * 16 * k, y)], (220, 120, 120), 6 * k)
    # cola
    K.poligono(L, [(x - mira * 40 * k, by), (x - mira * 110 * k, by - 10 * k), (x - mira * 110 * k, by + 24 * k)], C16["paloma2"], TINTA, 4)
    # cuerpo
    K.elipse(L, x, by, 62 * k, 44 * k, C16["paloma"], TINTA, 5)
    # ala
    if vuela > 0.05:
        f = math.sin(t * 26) * vuela
        for sg in (-1, 1):
            tip = (x - mira * 20 * k + sg * 30 * k, by - 40 * k - 90 * k * f * sg - 60 * k * vuela)
            K.poligono(L, [(x - 30 * k, by - 6 * k), (x + 26 * k, by - 6 * k), tip], C16["paloma2"], TINTA, 4)
    else:
        K.elipse(L, x - mira * 8 * k, by + 4 * k, 40 * k, 24 * k, C16["paloma2"], TINTA, 4)
    # cuello y cabeza
    hx, hy = x + mira * 44 * k, by - 44 * k
    K.elipse(L, x + mira * 34 * k, by - 18 * k, 24 * k, 26 * k, C16["cuello_v"])
    K.elipse(L, x + mira * 40 * k, by - 28 * k, 18 * k, 18 * k, C16["cuello_m"])
    K.circulo(L, hx, hy, 26 * k, C16["paloma"], TINTA, 5)
    K.poligono(L, [(hx + mira * 22 * k, hy - 4 * k), (hx + mira * 44 * k, hy + 4 * k), (hx + mira * 22 * k, hy + 10 * k)], (230, 170, 110), TINTA, 3)
    K.circulo(L, hx + mira * 8 * k, hy - 4 * k, 8 * k, (255, 140, 60), TINTA, 3)
    K.circulo(L, hx + mira * 9 * k, hy - 4 * k, 3.5 * k, TINTA)
    if cara == "inocente":
        K.linea(L, [(hx - 2 * k, hy - 18 * k), (hx + mira * 18 * k, hy - 22 * k)], TINTA, 4 * k)


def caca(L, x, y, r=26, u=1.0):
    if u <= 0.02:
        return
    r = r * u
    for dx, dy, rr in ((0, 0, 1.0), (-0.9, 0.3, 0.5), (0.8, 0.4, 0.45), (0.2, -0.7, 0.4)):
        K.circulo(L, x + dx * r, y + dy * r, rr * r + 3, (120, 120, 110))
    for dx, dy, rr in ((0, 0, 1.0), (-0.9, 0.3, 0.5), (0.8, 0.4, 0.45), (0.2, -0.7, 0.4)):
        K.circulo(L, x + dx * r, y + dy * r, rr * r, (246, 246, 238))
    K.circulo(L, x + r * 0.15, y - r * 0.1, r * 0.3, (90, 84, 70))


def nido(L, x, y, s=1.0):
    random.seed(4)
    K.elipse(L, x, y, 170 * s, 46 * s, C["madera"], TINTA, 6)
    for i in range(18):
        a = random.uniform(-160, 160)
        K.linea(L, [(x + a * s, y - random.uniform(-20, 20) * s), (x + (a + random.uniform(-70, 70)) * s, y + random.uniform(-26, 26) * s)], C["trigo2"], 6 * s)


# ------------------------------------------------------------------ el cosmos
def cosmos(L, t=0.0, semilla=3, galaxias=True):
    K.cielo_bandas(L, [C16["cosmos"], C16["cosmos"], C16["cosmos2"], C16["cosmos3"]], 0, H)
    random.seed(semilla)
    for i in range(140):
        x, y = random.uniform(0, W), random.uniform(0, H)
        r = random.uniform(1.5, 4.5) * (0.6 + 0.4 * math.sin(t * 2.5 + i))
        K.circulo(L, x, y, r, (255, 250, 230))
    if galaxias:
        for gx, gy, gr, c in ((180, 300, 70, (180, 140, 255)), (900, 1450, 90, (120, 200, 255)), (870, 520, 50, (255, 170, 200))):
            for k in range(4):
                K.elipse(L, gx, gy, gr * (1 - k * 0.2), gr * 0.38 * (1 - k * 0.2), (c[0], c[1], c[2], 50 + k * 30))


def tierra(L, x, y, r, t=0.0, antena=True):
    K.circulo(L, x, y, r * 1.18, (110, 180, 255, 50))
    K.circulo(L, x, y, r, C16["tierra_m"], TINTA, 7)
    random.seed(8)
    for dx, dy, rr in ((-0.35, -0.3, 0.38), (0.25, 0.1, 0.42), (-0.1, 0.5, 0.25), (0.5, -0.45, 0.2)):
        K.elipse(L, x + dx * r, y + dy * r, rr * r, rr * r * 0.7, C16["tierra_v"])
    L.d.ellipse((L.S(x - r), L.S(y - r), L.S(x + r), L.S(y + r)), outline=TINTA, width=int(L.S(7)))
    if antena:
        K.linea(L, [(x, y - r), (x, y - r - 40)], TINTA, 9)
        L.d.chord((L.S(x - 34), L.S(y - r - 70), L.S(x + 34), L.S(y - r - 10)), 180, 360, fill=C16["metal"], outline=TINTA, width=int(L.S(5)))


def onda(L, x0, y0, x1, y1, t, u=1.0, amp=26, lam=70, color=None, grosor=12, cabeza=True):
    """Onda de luz (sinusoide) de (x0,y0) a un punto u del camino a (x1,y1)."""
    if u <= 0.02:
        return
    dx, dy = x1 - x0, y1 - y0
    d = math.hypot(dx, dy)
    nx, ny = -dy / d, dx / d
    n = max(6, int(d * u / 8))
    pts = []
    for i in range(n + 1):
        s = d * u * i / n
        off = math.sin((s - t * 400) / lam * math.tau) * amp
        pts.append((x0 + dx / d * s + nx * off, y0 + dy / d * s + ny * off))
    K.linea(L, pts, TINTA, grosor + 8)
    K.linea(L, pts, color or C16["luz"], grosor)
    if cabeza:
        K.circulo(L, pts[-1][0], pts[-1][1], grosor * 1.4, color or C16["luz"], TINTA, 5)


def grilla100(L, x0, y0, x1, y1, t, u=1.0, especial=(6, 3), brillo=1.0):
    """10×10 puntitos grises (la lluvia ordenada) y uno dorado."""
    cw, ch = (x1 - x0) / 10, (y1 - y0) / 10
    n = int(100 * clamp(u))
    for idx in range(n):
        j, i = divmod(idx, 10)
        cx, cy = x0 + (i + 0.5) * cw, y0 + (j + 0.5) * ch
        if (i, j) == especial:
            continue
        g = 120 + int(80 * ((idx * 37) % 11) / 10)
        K.circulo(L, cx, cy, min(cw, ch) * 0.3, (g, g, g), (30, 30, 34), 3)
    if n > especial[1] * 10 + especial[0]:
        cx, cy = x0 + (especial[0] + 0.5) * cw, y0 + (especial[1] + 0.5) * ch
        rr = min(cw, ch)
        for k in range(3):
            K.circulo(L, cx, cy, rr * (0.75 + k * 0.28) * (1 + 0.1 * math.sin(t * 6)), (255, 200, 90, 60 - k * 15))
        bang(L, cx, cy, rr * 0.44 * (1 + 0.08 * math.sin(t * 7)), t, "feliz", brillo, chispas_n=0)


# ------------------------------------------------------------------ v3: la sopa del principio, los átomos y la luz que se estira
def sopa(L, t=0.0, niebla=1.0, enfria=0.0):
    """El universo recién nacido: sopa ardiente (naranja) que se enfría (rojo oscuro → azul noche) con neblina encima."""
    c0 = (255, 150, 60); c1 = (40, 30, 70)
    mezcla = lambda a, b, u: tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(3))
    top = mezcla((255, 190, 90), c1, enfria); bot = mezcla((220, 70, 40), (20, 16, 50), enfria)
    K.cielo_bandas(L, [top, mezcla(top, bot, 0.33), mezcla(top, bot, 0.66), bot], 0, H)
    rnd = random.Random(12)
    for i in range(26):                                                                    # burbujas de la sopa
        x = rnd.uniform(0, W); y0 = rnd.uniform(0, H); v = rnd.uniform(40, 120)
        y = (y0 - t * v) % (H + 200) - 100
        r = rnd.uniform(14, 40) * (1 - 0.6 * enfria)
        K.circulo(L, x, y, r, (255, 230, 170, int(70 * (1 - enfria))))
    if niebla > 0.02:
        for i in range(14):
            x = (rnd.uniform(0, W) + t * 30 * (1 if i % 2 else -1)) % (W + 400) - 200
            y = rnd.uniform(60, 1250)
            K.elipse(L, x, y, rnd.uniform(160, 300), rnd.uniform(60, 110), (255, 245, 230, int(90 * niebla)))


def particula(L, x, y, r, tipo="p", t=0.0, cara=True):
    """Protón (rojo, +) o electrón (celeste, −) con carita."""
    col = (232, 80, 70) if tipo == "p" else (90, 170, 255)
    K.circulo(L, x, y, r, col, TINTA, max(3, r * 0.14))
    k = r / 30
    if cara:
        for sg in (-1, 1):
            K.circulo(L, x + sg * 9 * k, y - 4 * k, 3.4 * k, TINTA)
        K.linea(L, [(x - 6 * k, y + 8 * k), (x + 6 * k, y + 8 * k)], TINTA, 2.6 * k)
    sx = x + r * 0.62; sy = y - r * 0.62
    K.linea(L, [(sx - 7 * k, sy), (sx + 7 * k, sy)], C["blanco"], 3.2 * k)
    if tipo == "p":
        K.linea(L, [(sx, sy - 7 * k), (sx, sy + 7 * k)], C["blanco"], 3.2 * k)


def particulas(L, t, n=22, enjambre=1.0, semilla=2, area=(40, 120, 1040, 940), atomos=0.0, rp=44, re_=26):
    """Protones y electrones sueltos zumbando; con atomos→1 cada electrón se va a orbitar su protón."""
    rnd = random.Random(semilla)
    x0, y0, x1, y1 = area
    for i in range(n):
        px = rnd.uniform(x0 + 60, x1 - 60); py = rnd.uniform(y0 + 60, y1 - 60)
        fx, fy = rnd.uniform(0.6, 1.4), rnd.uniform(0.6, 1.4)
        # protón: tiembla en su lugar
        pxx = px + math.sin(t * 7 * fx + i) * 26 * enjambre
        pyy = py + math.cos(t * 6 * fy + i) * 26 * enjambre
        # electrón: suelto, rápido; con átomos, en órbita
        ex_l = (rnd.uniform(x0, x1) + t * 260 * (fx - 1.0) * 3) % (x1 - x0) + x0
        ey_l = (rnd.uniform(y0, y1) + t * 200 * (fy - 1.0) * 3) % (y1 - y0) + y0
        an = t * 5 + i
        ex_o, ey_o = pxx + math.cos(an) * rp * 2.1, pyy + math.sin(an) * rp
        u = suave(atomos)
        ex, ey = ex_l + (ex_o - ex_l) * u, ey_l + (ey_o - ey_l) * u
        if u > 0.6:
            L.d.ellipse((L.S(pxx - rp * 2.1), L.S(pyy - rp), L.S(pxx + rp * 2.1), L.S(pyy + rp)), outline=(255, 255, 255, int(170 * (u - 0.6) / 0.4)), width=int(L.S(4)))
        particula(L, pxx, pyy, rp, "p", t)
        particula(L, ex, ey, re_, "e", t, cara=False)


def foton(L, x, y, r=46, t=0.0, cara="feliz", estela=None, color=None):
    """La luz: una bolita brillante con cara (y una estela de velocidad opcional, ángulo en radianes)."""
    col = color or C16["luz"]
    if estela is not None:
        for k in range(5):
            d = 40 + k * 46
            K.linea(L, [(x - math.cos(estela) * d, y - math.sin(estela) * d + (k - 2) * 14),
                        (x - math.cos(estela) * (d + 70), y - math.sin(estela) * (d + 70) + (k - 2) * 14)], (255, 255, 255, 200 - k * 30), 8)
    for k in range(3, 0, -1):
        K.circulo(L, x, y, r * (1 + k * 0.28), (col[0], col[1], col[2], 50))
    K.circulo(L, x, y, r, col, TINTA, 6)
    k = r / 46
    if cara == "mareado":
        for sg in (-1, 1):
            ex, ey = x + sg * 15 * k, y - 6 * k
            K.linea(L, [(ex - 7 * k, ey - 7 * k), (ex + 7 * k, ey + 7 * k)], TINTA, 4 * k)
            K.linea(L, [(ex - 7 * k, ey + 7 * k), (ex + 7 * k, ey - 7 * k)], TINTA, 4 * k)
        K.elipse(L, x, y + 16 * k, 8 * k, 10 * k, (140, 50, 40), TINTA, 3)
        return
    for sg in (-1, 1):
        K.elipse(L, x + sg * 15 * k, y - 6 * k, 6 * k, 9 * k, TINTA)
    if cara == "feliz":
        L.d.chord((L.S(x - 14 * k), L.S(y + 2 * k), L.S(x + 14 * k), L.S(y + 24 * k)), 0, 180, fill=(140, 50, 40), outline=TINTA, width=int(L.S(3)))
    else:
        K.elipse(L, x, y + 14 * k, 7 * k, 9 * k, (140, 50, 40), TINTA, 3)


def onda_estirada(L, x0, x1, y, t, lam=60, amp=40, color=None, grosor=14, cara=True, nombre=None):
    """Onda horizontal con longitud de onda lam (se estira al subir lam), con carita en la punta derecha."""
    n = max(40, int((x1 - x0) / 6))
    pts = [(x0 + (x1 - x0) * i / n, y + math.sin(((x1 - x0) * i / n - t * 220) / lam * math.tau) * amp) for i in range(n + 1)]
    K.linea(L, pts, TINTA, grosor + 9)
    K.linea(L, pts, color or C16["luz"], grosor)
    if cara:
        hx, hy = pts[-1]
        K.circulo(L, hx, hy, 34, color or C16["luz"], TINTA, 6)
        for sg in (-1, 1):
            K.elipse(L, hx + sg * 11, hy - 5, 4.5, 7, TINTA)
        L.d.chord((L.S(hx - 10), L.S(hy + 2), L.S(hx + 10), L.S(hy + 18)), 0, 180, fill=(140, 50, 40), outline=TINTA, width=int(L.S(3)))


def grilla_espacio(L, estira=0.0, color=(120, 110, 200, 90), cy=600):
    """Cuadrícula del espacio que se estira hacia los lados (estira 0..1)."""
    paso = 90 * (1 + 1.6 * estira)
    n = int(W / paso) + 3
    for i in range(-n, n + 1):
        x = W / 2 + i * paso
        K.linea(L, [(x, 0), (x, 1300)], color, 3)
    for j in range(0, 16):
        y = j * 90
        K.linea(L, [(0, y), (W, y)], color, 3)


def bombilla(L, x, y, s=1.0, u=1.0):
    if u <= 0.02:
        return
    s = s * u
    for k in range(3, 0, -1):
        K.circulo(L, x, y, 60 * s * (1 + k * 0.3), (255, 240, 150, 50))
    K.circulo(L, x, y, 60 * s, (255, 236, 130), TINTA, 6)
    K.caja_red(L, x - 28 * s, y + 50 * s, x + 28 * s, y + 92 * s, 8 * s, (170, 170, 180), TINTA, 5)
    K.linea(L, [(x - 18 * s, y + 10 * s), (x, y - 14 * s), (x + 18 * s, y + 10 * s)], (220, 150, 40), 6 * s)


def chupete(L, x, y, r):
    """Chupete para el Big Bang guagua."""
    k = r / 100
    K.elipse(L, x, y + 30 * k, 34 * k, 20 * k, (120, 200, 255), TINTA, 4)
    K.circulo(L, x, y + 30 * k, 12 * k, (255, 170, 190), TINTA, 3)
    L.d.arc((L.S(x - 20 * k), L.S(y + 34 * k), L.S(x + 20 * k), L.S(y + 74 * k)), 20, 160, fill=TINTA, width=int(L.S(5 * k)))


def termometro(L, x, y, h=360, nivel=1.0):
    K.caja_red(L, x - 30, y - h, x + 30, y, 30, C["blanco"], TINTA, 6)
    K.circulo(L, x, y + 20, 50, C["rojo"], TINTA, 6)
    hh = (h - 40) * clamp(nivel)
    K.caja_red(L, x - 16, y - hh, x + 16, y + 10, 16, C["rojo"])
    for k in range(5):
        K.linea(L, [(x + 30, y - 40 - k * 60), (x + 50, y - 40 - k * 60)], TINTA, 5)
