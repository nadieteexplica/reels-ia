# -*- coding: utf-8 -*-
"""Kit "explica" de El viejo del dato (23-nov-2026): el look oscuro de explicador, todo dibujado con código.

Sólo PIL + numpy, sin GPU. Se dibuja en coordenadas de pantalla (1080×1920) sobre un lienzo al doble (ss=2)
y al final se achica: así los bordes salen suaves. El color de energía va en una capa aparte (una máscara),
y de esa capa sale el brillo (glow): sólo brilla lo que tiene energía.

Piezas:
  ESTILOS                                  → los 5 estilos de la skill estilo-visual (fondo, energía, tinta, notas)
  ease_entrada, ease_salida, ease_estado, ease_aterriza, bezier, tramo, anim
  Lienzo(estilo, semilla, luz)             → lienzo sobremuestreado + capa de energía + cámara (zoom y temblor)
  fondo(estilo, semilla)                   → fondo con luz central, viñeta, retícula HUD y grano
  glow(mascara)                            → brillo: copia borrosa de la capa de energía
  poligono, circulo, elipse_pts, linea, linea_punteada, relleno_gradiente, recortar_y, texto, fuente
  etiqueta(...)                            → etiqueta HUD: punto en el objeto → línea guía → subrayado → texto
  cota_vertical(...)                       → cota con topes y flechas que crece
  contador(...)                            → número que rueda como odómetro
  subtitulos(L, words, t, claves)          → 1–3 palabras a la vez; la clave en recuadro con manillas
  clavo, martillo, tabla, suelo, persona, destello, polvo  → objetos reales en vector semi-plano
"""
import math
import os
import re
from functools import lru_cache

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
FUENTES = os.path.join(AQUI, "fonts")
F_BLACK = os.path.join(FUENTES, "Inter-Black.otf")
F_XBOLD = os.path.join(FUENTES, "Inter-ExtraBold.otf")
ANCHO, ALTO, FPS, SS = 1080, 1920, 30, 2
CAP = 0.727          # alto de las mayúsculas de Inter, en "em"


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def mezcla(c0, c1, k):
    return tuple(int(round(a + (b - a) * k)) for a, b in zip(c0, c1))


# ------------------------------------------------------------------ estilos (los 5 de la skill)
ESTILOS = {
    "plano_tecnico": dict(
        clave="plano_tecnico", nombre="Plano técnico", fondo="#0E2A47", fondo_luz="#163A5F",
        energia="#F2E27D", tinta="#EAF2FA", gris="#7E97B3", peligro="#E5484D", grano=5, reticula=0.10,
        trazo=3, etiqueta="Inter ExtraBold 44, mayúsculas",
        entrada="se dibuja en orden de dibujante: contorno → piezas → cotas",
        sonido="raspado de lápiz sobre papel", notas="Líneas blancas finas; para máquinas y 'cómo se hace'."),
    "rayos_x": dict(
        clave="rayos_x", nombre="Rayos X", fondo="#05070A", fondo_luz="#0D1520",
        energia="#3FE0F0", tinta="#DCEBF2", gris="#6F8796", peligro="#E5484D", grano=7, reticula=0.0,
        trazo=3, etiqueta="Inter ExtraBold 46, mayúsculas",
        entrada="el objeto se revela con un barrido de escáner de arriba abajo",
        sonido="zumbido eléctrico corto", notas="Objeto translúcido, bordes claros, interior por densidad; 'qué hay adentro'."),
    "laboratorio_nocturno": dict(
        clave="laboratorio_nocturno", nombre="Laboratorio nocturno", fondo="#12141A", fondo_luz="#1C2029",
        energia="#F5B82E", tinta="#E9E6DF", gris="#8A8F99", peligro="#E5484D", grano=6, reticula=0.06,
        trazo=4, etiqueta="Inter ExtraBold 50, mayúsculas",
        entrada="objetos planos con sombra corta; entran con bezier(0.16,1,0.3,1)",
        sonido="clic metálico seco", notas="Fondo carbón, etiquetas HUD, energía oro; mecanismos cotidianos (estilo base)."),
    "pizarra": dict(
        clave="pizarra", nombre="Pizarra", fondo="#17302A", fondo_luz="#1F3D35",
        energia="#F59A3C", tinta="#ECEBE4", gris="#93A39C", peligro="#E5484D", grano=9, reticula=0.0,
        trazo=5, etiqueta="Inter ExtraBold 50, mayúsculas, como tiza",
        entrada="trazo de tiza que se escribe; el mito se borra de una pasada",
        sonido="tiza contra pizarra", notas="Mito + analogía: el mito se escribe y se borra, la verdad en el mismo lugar."),
    "escala": dict(
        clave="escala", nombre="Escala", fondo="#0B1328", fondo_luz="#14213F",
        energia="#5EEAB5", tinta="#E6ECF5", gris="#7D8AA6", peligro="#E5484D", grano=5, reticula=0.05,
        trazo=4, etiqueta="Inter ExtraBold 48, mayúsculas",
        entrada="zoom continuo entre escalas con contador ×1 → ×1.000.000 y regla que se estira",
        sonido="whoosh grave que sube", notas="Tamaños, distancias y números imposibles."),
}


# ------------------------------------------------------------------ curvas (claude-motion, con sus números)
def bezier(x1, y1, x2, y2):
    """Curva cúbica tipo CSS: devuelve f(p) con p∈[0,1] (tiempo) → avance (puede pasar de 1 si y>1)."""
    cx, cy = 3 * x1, 3 * y1
    bx, by = 3 * (x2 - x1) - cx, 3 * (y2 - y1) - cy
    ax, ay = 1 - cx - bx, 1 - cy - by

    def x_de(s):
        return ((ax * s + bx) * s + cx) * s

    def f(p):
        if p <= 0:
            return 0.0
        if p >= 1:
            return 1.0
        s = p
        for _ in range(8):                      # Newton
            err = x_de(s) - p
            if abs(err) < 1e-6:
                break
            der = (3 * ax * s + 2 * bx) * s + cx
            if abs(der) < 1e-6:
                break
            s -= err / der
        if not (0 <= s <= 1) or abs(x_de(s) - p) > 1e-4:   # respaldo: bisección
            a, b = 0.0, 1.0
            for _ in range(40):
                s = (a + b) / 2
                if x_de(s) < p:
                    a = s
                else:
                    b = s
        return ((ay * s + by) * s + cy) * s
    return f


ease_entrada = bezier(0.16, 1, 0.3, 1)      # entradas (~0,8 s)
ease_salida = bezier(0.6, 0, 0.9, 0.35)     # salidas (~0,4 s, la mitad que la entrada)
ease_estado = bezier(0.65, 0, 0.35, 1)      # de un estado a otro
ease_aterriza = bezier(0.55, 0, 0.2, 1.12)  # algo que aterriza con rebote (UNA vez por video)


def tramo(t, t0, dur):
    """Avance lineal 0→1 entre t0 y t0+dur."""
    if dur <= 0:
        return 1.0 if t >= t0 else 0.0
    return clamp((t - t0) / dur)


def anim(t, t0, dur, curva=ease_entrada):
    return curva(tramo(t, t0, dur))


def pico_aterriza(n=2000):
    """Dónde está (p) y cuánto vale (y) el máximo del rebote de ease_aterriza: sirve para que el golpe
    caiga justo en la palabra."""
    mejor = (0.0, 0.0)
    for i in range(n + 1):
        p = i / n
        y = ease_aterriza(p)
        if y > mejor[1]:
            mejor = (p, y)
    return mejor


# ------------------------------------------------------------------ fuentes
@lru_cache(maxsize=64)
def fuente(px, peso="black"):
    return ImageFont.truetype(F_BLACK if peso == "black" else F_XBOLD, max(1, int(round(px))))


# ------------------------------------------------------------------ fondo
@lru_cache(maxsize=8)
def _fondo_base(clave, w, h, luz):
    e = ESTILOS[clave]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # luz suave detrás del foco
    r = np.hypot((xx - luz[0] * w) / h, (yy - luz[1] * h) / h)
    k = np.clip(r / 0.62, 0, 1)
    k = k * k * (3 - 2 * k)
    c0 = np.array(rgb(e["fondo_luz"]), np.float32)
    c1 = np.array(rgb(e["fondo"]), np.float32)
    img = c0 * (1 - k)[..., None] + c1 * k[..., None]
    # viñeta
    rc = np.hypot((xx - w / 2) / (w * 0.5), (yy - h / 2) / (h * 0.5))
    v = np.clip((rc - 0.55) / 0.85, 0, 1)
    v = v * v * (3 - 2 * v)
    img *= (1 - 0.5 * v)[..., None]
    # retícula de puntos (HUD), muy tenue
    if e.get("reticula", 0) > 0:
        tinta = np.array(rgb(e["tinta"]), np.float32)
        paso = 60
        for dy in (0, 1):
            for dx in (0, 1):
                sub = img[paso // 2 + dy::paso, 30 + dx::paso]
                sub += (tinta - sub) * e["reticula"]
    return img


def fondo(estilo, semilla=0, w=ANCHO, h=ALTO, luz=(0.46, 0.40), grano=None):
    """Fondo del estilo: color con luz central, viñeta suave, retícula HUD y grano (cambia con la semilla)."""
    base = _fondo_base(estilo["clave"], w, h, tuple(luz))
    g = estilo["grano"] if grano is None else grano
    rng = np.random.default_rng(semilla)
    n = rng.standard_normal((h, w), dtype=np.float32) * g
    return Image.fromarray(np.clip(base + n[..., None], 0, 255).astype(np.uint8), "RGB")


# ------------------------------------------------------------------ brillo
def glow(mascara, radios=(9, 30), pesos=(0.7, 0.75), fuerza=1.0):
    """Brillo de la capa de energía: copias borrosas (una cerrada y una abierta) de la máscara.
    Devuelve un arreglo HxW con la intensidad 0..1 (se suma en modo 'pantalla')."""
    w, h = mascara.size
    acc = np.zeros((h, w), np.float32)
    for r, p in zip(radios, pesos):
        f = 2 if r < 16 else 4
        chica = mascara.resize((w // f, h // f), Image.BOX)
        b = chica.filter(ImageFilter.GaussianBlur(r / f))
        acc += np.asarray(b.resize((w, h), Image.BILINEAR), np.float32) * (p / 255.0)
    return np.clip(acc * fuerza, 0, 1)


# ------------------------------------------------------------------ lienzo
class Lienzo:
    """Lienzo de un cuadro. Coordenadas de mundo = píxeles de pantalla 1080×1920 (la cámara las mueve).
    Capas: 'base' (RGB), 'energia' (máscara del color de energía, brilla) y 'post' (se dibuja ya achicado:
    subtítulos)."""

    def __init__(self, estilo, semilla=0, w=ANCHO, h=ALTO, ss=SS, luz=(0.46, 0.40)):
        self.e, self.w, self.h, self.ss, self.semilla = estilo, w, h, ss, semilla
        self.fondo1 = fondo(estilo, semilla, w, h, luz)
        self.im = self.fondo1.resize((w * ss, h * ss), Image.NEAREST)
        self.d = ImageDraw.Draw(self.im, "RGBA")
        self.en = Image.new("L", self.im.size, 0)
        self.den = ImageDraw.Draw(self.en)
        self.post = []
        self.brillo = 1.0
        self.camara()

    # cámara: zoom s alrededor de 'ancla' (que queda en 'destino' de la pantalla) + temblor
    def camara(self, s=1.0, ancla=(0, 0), destino=None, temblor=(0, 0)):
        self.cs, self.ca = s, ancla
        self.cb = destino if destino is not None else ancla
        self.ct = temblor

    def P(self, x, y, cam=True):
        if cam:
            x = (x - self.ca[0]) * self.cs + self.cb[0] + self.ct[0]
            y = (y - self.ca[1]) * self.cs + self.cb[1] + self.ct[1]
        return (x * self.ss, y * self.ss)

    def S(self, v, cam=True):
        return v * (self.cs if cam else 1.0) * self.ss

    def dib(self, capa):
        if capa == "base":
            return self.d
        if capa == "energia":
            return self.den
        return capa                      # un ImageDraw de una máscara temporal

    def temporal(self):
        m = Image.new("L", self.im.size, 0)
        return m, ImageDraw.Draw(m)

    def fundir(self, mascara, color=None, alpha=1.0, capa="base"):
        """Pega una máscara temporal con un color y una opacidad (sin dobles en los cruces de líneas)."""
        bb = mascara.getbbox()
        if not bb or alpha <= 0.003:
            return
        m = mascara.crop(bb)
        if alpha < 1:
            m = m.point(lambda v: int(v * alpha))
        if capa == "energia":
            self.en.paste(255, bb, m)
        else:
            self.im.paste(tuple(color[:3]), bb, m)

    def estampar(self, mascara, xy, color=None, capa="base", alpha=1.0):
        x, y = int(round(xy[0])), int(round(xy[1]))
        m = mascara if alpha >= 1 else mascara.point(lambda v: int(v * alpha))
        if capa == "energia":
            self.en.paste(255, (x, y), m)
        else:
            self.im.paste(tuple(color[:3]), (x, y), m)

    def fundido_abajo(self, y0, y1):
        """Funde todo lo que está bajo y0 hacia el fondo (en y1 ya es fondo puro): deja limpia la banda
        de subtítulos y la zona baja que tapa la interfaz."""
        ss = self.ss
        Y0, Y1 = int(y0 * ss), int(y1 * ss)
        alto = self.im.size[1] - Y0
        if alto <= 0:
            return
        g = np.clip((np.arange(alto, dtype=np.float32)) / max(1, Y1 - Y0), 0, 1)
        g = g * g * (3 - 2 * g)
        m = Image.fromarray((np.repeat(g[:, None], self.im.size[0], 1) * 255).astype(np.uint8), "L")
        fondo2 = self.fondo1.crop((0, y0, self.w, self.h)).resize((self.im.size[0], alto), Image.NEAREST)
        self.im.paste(fondo2, (0, Y0), m)

    def salida(self):
        img = self.im.reduce(self.ss)
        mk_img = self.en.reduce(self.ss)
        arr = np.asarray(img, dtype=np.float32)
        if mk_img.getbbox():
            en = np.array(rgb(self.e["energia"]), np.float32)
            g = glow(mk_img, fuerza=self.brillo)
            arr = 255 - (255 - arr) * (1 - g[..., None] * (en / 255.0))        # brillo en modo pantalla
            mk = np.asarray(mk_img, np.float32)[..., None] / 255.0
            arr = arr * (1 - mk) + en * mk
        rng = np.random.default_rng(self.semilla + 7919)                       # grano fino sobre todo
        arr = arr + rng.standard_normal(arr.shape[:2], dtype=np.float32)[..., None] * (self.e["grano"] * 0.45)
        out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
        for f in self.post:
            f(out)
        return out


def _c(color, capa, alpha=1.0):
    a = int(round(255 * clamp(alpha)))
    if capa == "base":
        return tuple(color[:3]) + (int(round(a * (color[3] / 255.0))) if len(color) > 3 else a,)
    return a


# ------------------------------------------------------------------ formas
def elipse_pts(cx, cy, rx, ry, a0=0, a1=360, n=56, rot=0):
    pts = []
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        x, y = rx * math.cos(a), ry * math.sin(a)
        pts.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return pts


def recortar_y(pts, y_max):
    """Recorta un polígono convexo a la parte con y ≤ y_max (lo que queda fuera de la madera o la tierra)."""
    if y_max is None:
        return pts
    out, n = [], len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        ia, ib = a[1] <= y_max, b[1] <= y_max
        if ia:
            out.append(a)
        if ia != ib:
            k = (y_max - a[1]) / (b[1] - a[1])
            out.append((a[0] + k * (b[0] - a[0]), y_max))
    return out


def poligono(L, pts, color=(255, 255, 255), capa="base", alpha=1.0, cam=True):
    q = [L.P(x, y, cam) for x, y in pts]
    if len(q) >= 3:
        L.dib(capa).polygon(q, fill=_c(color, capa, alpha))


def circulo(L, x, y, r, color=(255, 255, 255), capa="base", alpha=1.0, cam=True):
    X, Y = L.P(x, y, cam)
    R = L.S(r, cam)
    L.dib(capa).ellipse((X - R, Y - R, X + R, Y + R), fill=_c(color, capa, alpha))


def linea(L, pts, color=(255, 255, 255), ancho=4, capa="base", alpha=1.0, cam=True, puntas=True):
    q = [L.P(x, y, cam) for x, y in pts]
    w = max(1, int(round(L.S(ancho, cam))))
    d, c = L.dib(capa), _c(color, capa, alpha)
    d.line(q, fill=c, width=w, joint="curve")
    if puntas:
        r = w / 2
        for X, Y in (q[0], q[-1]):
            d.ellipse((X - r, Y - r, X + r, Y + r), fill=c)


def linea_punteada(L, p0, p1, color=(255, 255, 255), ancho=3, trazo=14, hueco=10, capa="base", alpha=1.0, cam=True):
    x0, y0 = p0
    x1, y1 = p1
    largo = math.hypot(x1 - x0, y1 - y0)
    if largo < 1:
        return
    ux, uy = (x1 - x0) / largo, (y1 - y0) / largo
    s = 0.0
    while s < largo:
        e = min(largo, s + trazo)
        linea(L, [(x0 + ux * s, y0 + uy * s), (x0 + ux * e, y0 + uy * e)], color, ancho, capa, alpha, cam)
        s += trazo + hueco


def relleno_gradiente(L, pts, stops, p0, p1, alpha=1.0, cam=True):
    """Rellena un polígono con un degradado lineal de p0 a p1 (stops: [(pos, (r,g,b[,a])), ...]).
    Es lo que da el brillo metálico y la madera."""
    q = [L.P(x, y, cam) for x, y in pts]
    if len(q) < 3:
        return
    W, H = L.im.size
    xs, ys = [p[0] for p in q], [p[1] for p in q]
    x0, x1 = max(0, int(math.floor(min(xs)))), min(W, int(math.ceil(max(xs))) + 1)
    y0, y1 = max(0, int(math.floor(min(ys)))), min(H, int(math.ceil(max(ys))) + 1)
    if x1 - x0 < 1 or y1 - y0 < 1:
        return
    a, b = L.P(*p0, cam), L.P(*p1, cam)
    dx, dy = b[0] - a[0], b[1] - a[1]
    n2 = dx * dx + dy * dy or 1.0
    gx = (np.arange(x0, x1, dtype=np.float32) + 0.5 - a[0]) * (dx / n2)
    gy = (np.arange(y0, y1, dtype=np.float32) + 0.5 - a[1]) * (dy / n2)
    tt = np.clip(gy[:, None] + gx[None, :], 0, 1)
    pos = np.array([s[0] for s in stops], np.float32)
    cols = np.array([s[1] for s in stops], np.float32)
    ch = [np.interp(tt, pos, cols[:, k]) for k in range(cols.shape[1])]
    img = Image.fromarray(np.stack(ch[:3], -1).astype(np.uint8), "RGB")
    mask = Image.new("L", (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(mask).polygon([(x - x0, y - y0) for x, y in q], fill=int(255 * clamp(alpha)))
    if cols.shape[1] == 4:
        mask = Image.fromarray((np.asarray(mask, np.float32) * (ch[3] / 255.0)).astype(np.uint8), "L")
    L.im.paste(img, (x0, y0), mask)


def texto(L, x, y, s, tam, color=(255, 255, 255), peso="black", anchor="ls", capa="base", alpha=1.0, cam=False):
    X, Y = L.P(x, y, cam)
    f = fuente(L.S(tam, cam), peso)
    L.dib(capa).text((X, Y), s, font=f, fill=_c(color, capa, alpha), anchor=anchor)
    return f.getlength(s) / L.S(1, cam)


def medir(s, tam, peso="black"):
    return fuente(tam * 4, peso).getlength(s) / 4.0


# ------------------------------------------------------------------ contador (odómetro)
@lru_cache(maxsize=16)
def _mascara_rodillo(w, h):
    y = np.arange(h, dtype=np.float32) / max(1, h - 1)
    g = np.clip(np.minimum(y, 1 - y) / 0.2, 0, 1)
    g = g * g * (3 - 2 * g)
    return Image.fromarray((np.repeat(g[:, None], w, 1) * 255).astype(np.uint8), "L")


def ancho_contador(tam, digitos=1, unidad="", peso="black"):
    f = fuente(tam * 4, peso)
    cw = max(f.getlength(d) for d in "0123456789")
    return (cw * digitos + (f.getlength(unidad) if unidad else 0)) / 4.0


def contador(L, valor, x, y, tam, digitos=1, unidad="", capa="energia", color=None, alpha=1.0,
             peso="black", cam=False, alin="izq"):
    """Número que rueda como odómetro (las cifras suben o bajan según cambie 'valor', con la curva que
    traiga 'valor'). (x, y) = línea base. Las cifras tienen ancho fijo: el número no baila mientras se lee."""
    if alpha <= 0.003:
        return 0
    color = color or rgb(L.e["energia"])
    px = L.S(tam, cam)
    f = fuente(px, peso)
    cw = max(f.getlength(d) for d in "0123456789")
    uw = f.getlength(unidad) if unidad else 0
    total = cw * digitos + uw
    X, Y = L.P(x, y, cam)
    if alin == "der":
        X -= total
    elif alin == "centro":
        X -= total / 2
    v = round(float(valor), 5)
    # ventana justa (alto de cifra + margen): la cifra que entra queda fuera hasta que rueda
    margen = px * 0.13
    alto = int(math.ceil(px * CAP + 2 * margen))
    ch = alto * 1.0
    base_c = margen + px * CAP
    ancho = int(math.ceil(cw)) + 4
    for i in range(digitos):
        pot = 10 ** (digitos - 1 - i)
        q = v / pot
        base = math.floor(q + 1e-9)
        frac = (q - base) if pot == 1 else clamp((v - base * pot) - (pot - 1))
        frac = ease_estado(clamp((frac - 0.45) / 0.55))   # la cifra se queda quieta y rueda al final: se lee
        s0 = "" if (pot > 1 and base == 0) else str(base % 10)
        s1 = "" if (pot > 1 and base + 1 == 0) else str((base + 1) % 10)
        celda = Image.new("L", (ancho, alto), 0)
        dc = ImageDraw.Draw(celda)
        off = frac * ch
        if s0:
            dc.text((ancho / 2, base_c - off), s0, font=f, fill=255, anchor="ms")
        if frac > 0.002 and s1:
            dc.text((ancho / 2, base_c - off + ch), s1, font=f, fill=255, anchor="ms")
        celda = ImageChops.multiply(celda, _mascara_rodillo(ancho, alto))
        L.estampar(celda, (X + i * cw + cw / 2 - ancho / 2, Y - base_c), color, capa, alpha)
    if unidad:
        L.dib(capa).text((X + cw * digitos, Y), unidad, font=f, fill=_c(color, capa, alpha), anchor="ls")
    return total / L.S(1, cam)


# ------------------------------------------------------------------ etiqueta HUD con línea guía
def etiqueta(L, texto_, punto, pos, t, t0, t1=None, tam=50, lado="izq", caption=None, numero=None,
             dur=0.8, texto_desde=0.45, cam=False):
    """Etiqueta en MAYÚSCULAS con línea guía de 4 px que termina en un punto sobre el objeto.
    pos = esquina izquierda-arriba del bloque de texto. lado='izq': el bloque queda a la izquierda del
    punto; 'der': a la derecha. numero = dict(valor, digitos, unidad): número vivo en color de energía.
    Entra en 'dur' s (punto → guía → subrayado → texto) y sale en 0,4 s desde t1. El texto no se mueve."""
    if t < t0:
        return
    a_out = 1.0
    if t1 is not None and t >= t1:
        a_out = 1 - ease_salida(tramo(t, t1, 0.4))
        if a_out <= 0.003:
            return
    e = L.e
    tinta, gris, fnd = rgb(e["tinta"]), rgb(e["gris"]), rgb(e["fondo"])
    u = (t - t0) / dur
    x, y = pos
    # medidas del bloque
    if numero is None:
        wb = medir(texto_, tam, "xbold")
        base1 = y + CAP * tam
        hb = CAP * tam
    else:
        tc, tn = tam * 0.72, tam * 1.75
        base_c = y + CAP * tc
        base_n = base_c + 18 + CAP * tn
        wb = max(medir(caption or "", tc, "xbold"), ancho_contador(tn, numero.get("digitos", 1), numero.get("unidad", "")))
        hb = base_n - y
    yu = y + hb + 18
    if lado == "izq":
        codo, lejos = (x + wb + 20, yu), (x, yu)
    else:
        codo, lejos = (x - 20, yu), (x + wb, yu)

    def fase(a, b):
        return ease_entrada(clamp((u - a) / (b - a)))
    p_pt, p_guia, p_sub, p_txt = fase(0, 0.3), fase(0.06, 0.5), fase(0.36, 0.78), fase(texto_desde, 1.0)
    # líneas en una máscara temporal (sin dobles en el codo)
    m, d = L.temporal()
    if p_guia > 0:
        q = (punto[0] + (codo[0] - punto[0]) * p_guia, punto[1] + (codo[1] - punto[1]) * p_guia)
        linea(L, [punto, q], ancho=e["trazo"], capa=d, cam=cam)
    if p_sub > 0:
        q = (codo[0] + (lejos[0] - codo[0]) * p_sub, yu)
        linea(L, [codo, q], ancho=e["trazo"], capa=d, cam=cam)
    L.fundir(m, tinta, a_out)
    # punto en el objeto: anillo oscuro + punto de tinta
    if p_pt > 0:
        circulo(L, punto[0], punto[1], 13 * p_pt, fnd, alpha=0.85 * a_out, cam=cam)
        circulo(L, punto[0], punto[1], 8.5 * p_pt, tinta, alpha=a_out, cam=cam)
    # texto
    if p_txt > 0:
        a = p_txt * a_out
        if numero is None:
            texto(L, x, base1, texto_, tam, tinta, "xbold", alpha=a, cam=cam)
        else:
            if caption:
                texto(L, x, base_c, caption, tc, gris, "xbold", alpha=a, cam=cam)
            contador(L, numero["valor"], x, base_n, tn, numero.get("digitos", 1), numero.get("unidad", ""),
                     capa="energia", alpha=a, cam=cam)


# ------------------------------------------------------------------ cota vertical
def cota_vertical(L, x, y_bajo, y_alto, p, tope=46, capa="energia", color=None, alpha=1.0, cam=False):
    """Cota de medida: línea con topes en los extremos y flechas, que crece desde y_bajo hasta y_alto."""
    if p <= 0.002 or alpha <= 0.003:
        return
    yp = y_bajo + (y_alto - y_bajo) * p
    m, d = L.temporal()
    w = L.e["trazo"] + 1
    linea(L, [(x, y_bajo), (x, yp)], ancho=w, capa=d, cam=cam)
    linea(L, [(x - tope / 2, y_bajo), (x + tope / 2, y_bajo)], ancho=w, capa=d, cam=cam)
    linea(L, [(x - tope / 2, yp), (x + tope / 2, yp)], ancho=w, capa=d, cam=cam)
    if abs(yp - y_bajo) > 60:
        s = 1 if y_alto < y_bajo else -1
        linea(L, [(x - 13, y_bajo - s * 20), (x, y_bajo - s * 4), (x + 13, y_bajo - s * 20)], ancho=w, capa=d, cam=cam)
        linea(L, [(x - 13, yp + s * 20), (x, yp + s * 4), (x + 13, yp + s * 20)], ancho=w, capa=d, cam=cam)
    L.fundir(m, color or rgb(L.e["energia"]), alpha, capa)


# ------------------------------------------------------------------ subtítulos
def _norm(w):
    return re.sub(r"[^\wáéíóúüñ]", "", w.lower())


_CACHE_SUB = {}


def preparar_subtitulos(words, claves, tam=84, ancho_max=850, x_centro=490, y_centro=1460,
                        max_pal=3, pausa=0.32):
    """Arma los grupos de 1–3 palabras (sin partir una frase clave, cortando en puntuación y pausas)
    y fija la posición de cada palabra: el grupo no se mueve mientras se lee."""
    n = len(words)
    toks = [_norm(w["w"]) for w in words]
    span = [None] * n                               # índice de inicio de la frase clave
    for k in claves:
        kt = [_norm(x) for x in k.split()]
        for i in range(n - len(kt) + 1):
            if toks[i:i + len(kt)] == kt and all(span[j] is None for j in range(i, i + len(kt))):
                for j in range(i, i + len(kt)):
                    span[j] = i
    # unidades (palabra suelta o frase clave) y segmentos (cortan en puntuación o pausa)
    segmentos, seg, i = [], [], 0
    while i < n:
        j = i
        while j + 1 < n and span[j + 1] is not None and span[j + 1] == span[i]:
            j += 1
        seg.append(list(range(i, j + 1)))
        fin = words[j]["w"][-1] in ".,;:?!…"
        if j + 1 < n and words[j + 1]["s"] - words[j]["e"] > pausa:
            fin = True
        if fin or j + 1 >= n:
            segmentos.append(seg)
            seg = []
        i = j + 1
    grupos = []
    for seg in segmentos:
        k = 0
        while k < len(seg):
            resto = sum(len(u) for u in seg[k:])
            meta = 2 if resto == 4 else max_pal
            g = list(seg[k])
            k += 1
            while k < len(seg) and len(g) + len(seg[k]) <= meta:
                g += seg[k]
                k += 1
            grupos.append(g)
    # posiciones
    salida = []
    for gi, g in enumerate(grupos):
        # si no cabe, primero se achica (hasta 84 %) y sólo después se parte en dos líneas
        tam_g = tam
        f = fuente(tam_g, "black")
        esp = f.getlength(" ")
        total = sum(f.getlength(words[i]["w"]) for i in g) + esp * (len(g) - 1)
        if total > ancho_max:
            tam_g = max(tam * 0.84, math.floor(tam * ancho_max / total * 0.99))
            f = fuente(tam_g, "black")
            esp = f.getlength(" ")
        anchos = [f.getlength(words[i]["w"]) for i in g]
        total = sum(anchos) + esp * (len(g) - 1)
        if total <= ancho_max or len(g) == 1:
            lineas = [g]
        else:                                        # dos líneas: el corte más parejo
            mejor = None
            for c in range(1, len(g)):
                a = sum(anchos[:c]) + esp * (c - 1)
                b = sum(anchos[c:]) + esp * (len(g) - c - 1)
                if mejor is None or max(a, b) < mejor[0]:
                    mejor = (max(a, b), c)
            lineas = [g[:mejor[1]], g[mejor[1]:]]
        alto_l = tam_g * 1.12
        pos = {}
        for li, ln in enumerate(lineas):
            base = y_centro + CAP * tam_g / 2 + (li - (len(lineas) - 1) / 2) * alto_l
            ws = [f.getlength(words[i]["w"]) for i in ln]
            x = x_centro - (sum(ws) + esp * (len(ln) - 1)) / 2
            for i, wv in zip(ln, ws):
                pos[i] = (x, base, wv)
                x += wv + esp
        cajas = {}
        for i in g:
            if span[i] is not None:
                x, b, wv = pos[i]
                top, bot = b - CAP * tam_g - 16, b + 0.2 * tam_g + 6
                caja = cajas.get(span[i])
                cajas[span[i]] = (x - 20, top, x + wv + 20, bot) if caja is None else (
                    min(caja[0], x - 20), min(caja[1], top), max(caja[2], x + wv + 20), max(caja[3], bot))
        t_ini = 0.0 if gi == 0 else words[g[0]]["s"] - 0.03
        salida.append(dict(idx=g, pos=pos, cajas=cajas, t0=t_ini, tam=tam_g))
    for gi in range(len(salida)):
        salida[gi]["t1"] = salida[gi + 1]["t0"] if gi + 1 < len(salida) else 1e9
    return salida


def subtitulos(L, words, t, claves, tam=84, **kw):
    """Subtítulos palabra por palabra: 1–3 palabras a la vez, Inter Black blanco con contorno oscuro;
    la palabra clave dentro de un recuadro del color de energía (6 px) con manillas cuadradas de 14 px."""
    clave_cache = (id(words), tuple(claves), tam, tuple(sorted(kw.items())))
    if clave_cache not in _CACHE_SUB:
        _CACHE_SUB[clave_cache] = preparar_subtitulos(words, claves, tam, **kw)
    grupos = _CACHE_SUB[clave_cache]
    g = next((g for g in grupos if g["t0"] <= t < g["t1"]), None)
    if g is None:
        return
    # recuadros (en la capa de energía: brillan)
    for i0, (x0, y0, x1, y1) in g["cajas"].items():
        ts = words[i0]["s"] - 0.03 if g["idx"][0] != i0 or g["t0"] > 0 else 0.0
        if t < ts:
            continue
        a = ease_entrada(tramo(t, ts, 0.22))
        sc = 1.10 - 0.10 * a
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        X0, Y0 = cx + (x0 - cx) * sc, cy + (y0 - cy) * sc
        X1, Y1 = cx + (x1 - cx) * sc, cy + (y1 - cy) * sc
        m, d = L.temporal()
        d.rectangle([L.P(X0, Y0, False), L.P(X1, Y1, False)], fill=28)
        w = L.S(6, False)
        d.rectangle([L.P(X0, Y0, False), L.P(X1, Y1, False)], outline=255, width=int(round(w)))
        h = 7
        for hx, hy in ((X0, Y0), (X1, Y0), (X0, Y1), (X1, Y1)):
            hx, hy = hx + (3 if hx == X0 else -3), hy + (3 if hy == Y0 else -3)
            d.rectangle([L.P(hx - h, hy - h, False), L.P(hx + h, hy + h, False)], fill=255)
        L.fundir(m, alpha=a, capa="energia")
    # palabras (se dibujan ya achicadas: el texto de FreeType sale nítido)
    f = fuente(g["tam"], "black")
    vis = []
    for i in g["idx"]:
        ts = 0.0 if (g["t0"] == 0.0 and i == g["idx"][0]) else words[i]["s"] - 0.04
        if t >= ts:
            vis.append((i, ease_entrada(tramo(t, ts, 0.16))))

    def dibujar(img, vis=vis, g=g):
        d = ImageDraw.Draw(img, "RGBA")
        for i, a in vis:
            x, b, _ = g["pos"][i]
            al = int(255 * a)
            d.text((x, b + 10 * (1 - a)), words[i]["w"], font=f, fill=(255, 255, 255, al), anchor="ls",
                   stroke_width=7, stroke_fill=(9, 10, 13, al))
    L.post.append(dibujar)


# ------------------------------------------------------------------ materiales
METAL = [(0.0, (66, 70, 80)), (0.10, (112, 118, 130)), (0.25, (206, 211, 220)), (0.33, (244, 246, 249)),
         (0.43, (190, 195, 205)), (0.66, (116, 122, 134)), (0.84, (78, 82, 92)), (0.94, (122, 128, 140)),
         (1.0, (84, 88, 98))]
METAL_TAPA = [(0.0, (150, 156, 167)), (0.30, (232, 235, 240)), (0.45, (210, 214, 222)), (0.75, (140, 146, 158)),
              (1.0, (104, 110, 122))]
MADERA_MANGO = [(0.0, (112, 68, 36)), (0.16, (186, 128, 72)), (0.36, (226, 176, 112)), (0.55, (204, 148, 88)),
                (0.82, (146, 94, 50)), (1.0, (100, 62, 32))]


def _xf(cx, cy, esc, ang):
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))

    def f(u, v):
        u, v = u * esc, v * esc
        return (cx + u * ca - v * sa, cy + u * sa + v * ca)
    return f


def _curva(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        s = i / n
        a, b, c, d = (1 - s) ** 3, 3 * (1 - s) ** 2 * s, 3 * (1 - s) * s * s, s ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


# ------------------------------------------------------------------ objetos
def clavo(L, cx, y0, largo, recorte=None, cam=True):
    """Clavo de acero real: cabeza plana circular (vista un poco desde arriba), caña lisa, punta de diamante,
    degradado metálico con brillo lineal. y0 = tope de la cabeza. recorte = y de la superficie donde entra
    (la caña y la punta bajo esa línea no se dibujan)."""
    N = largo
    D, ry, hr = 0.14 * N, 0.024 * N, 0.03 * N
    sw, punta = 0.055 * N, 0.075 * N
    ye, yr = y0 + ry, y0 + ry + hr
    ys1, yt = y0 + N - punta, y0 + N
    xl, xr = cx - sw / 2, cx + sw / 2
    # caña
    cana = recortar_y([(xl, yr - 1), (xr, yr - 1), (xr, ys1 + 0.5), (xl, ys1 + 0.5)], recorte)
    relleno_gradiente(L, cana, METAL, (xl, 0), (xr, 0), cam=cam)
    # sombra de la cabeza sobre la caña
    som = recortar_y([(xl, yr), (xr, yr), (xr, yr + 0.06 * N), (xl, yr + 0.06 * N)], recorte)
    relleno_gradiente(L, som, [(0, (10, 12, 16, 150)), (1, (10, 12, 16, 0))], (0, yr), (0, yr + 0.06 * N), cam=cam)
    # punta de diamante: dos caras (clara a la izquierda, oscura a la derecha) y la arista al medio
    yq = ys1 + punta * 0.16
    izq = recortar_y([(xl, ys1), (cx, ys1), (cx, yq), (cx, yt)], recorte)
    der = recortar_y([(cx, ys1), (xr, ys1), (cx, yt), (cx, yq)], recorte)
    relleno_gradiente(L, izq, [(0, (150, 156, 168)), (0.5, (222, 226, 233)), (1, (176, 182, 193))], (xl, ys1), (cx, yt), cam=cam)
    relleno_gradiente(L, der, [(0, (122, 128, 140)), (0.6, (84, 88, 98)), (1, (60, 64, 72))], (cx, ys1), (xr, yt), cam=cam)
    if recorte is None or recorte > ys1:
        arista = recortar_y([(cx - 0.8, yq), (cx + 0.8, yq), (cx + 0.3, yt - 1), (cx - 0.3, yt - 1)], recorte)
        poligono(L, arista, (240, 242, 246), alpha=0.7, cam=cam)
    # cabeza: canto (cilindro) y tapa (elipse)
    canto = [(cx - D / 2, ye)] + elipse_pts(cx, yr, D / 2, ry, 180, 0, 40) + [(cx + D / 2, ye)]
    relleno_gradiente(L, canto, METAL, (cx - D / 2, 0), (cx + D / 2, 0), cam=cam)
    poligono(L, elipse_pts(cx, ye, D / 2 + 0.6, ry + 0.6, n=64), (54, 58, 66), cam=cam)
    relleno_gradiente(L, elipse_pts(cx, ye, D / 2 - 0.8, ry - 0.8, n=64), METAL_TAPA,
                      (cx - D / 2, ye - ry), (cx + D / 2, ye + ry), cam=cam)
    # marcas finas del troquel en la tapa + reflejo
    poligono(L, elipse_pts(cx - D * 0.12, ye - ry * 0.18, D * 0.2, ry * 0.32, n=40), (255, 255, 255), alpha=0.28, cam=cam)
    linea(L, elipse_pts(cx, ye, D * 0.3, ry * 0.42, 200, 340, 20), (120, 126, 138), 1.2, alpha=0.6, cam=cam)


def geometria_clavo(largo):
    """Medidas útiles del clavo (para apuntar etiquetas y calcular el hundimiento)."""
    N = largo
    return dict(D=0.14 * N, ry=0.024 * N, hr=0.03 * N, sw=0.055 * N, punta=0.075 * N, cabeza=0.054 * N)


def martillo(L, cx, cy, H, ang=0.0, sombra=True, cam=True):
    """Martillo de carpintero real: cabeza de acero con cara redonda y oreja curva (uña), mango de madera
    con vetas. (cx, cy) = centro de la cabeza; H = largo del mango; ang en grados (0 = mango hacia la
    derecha, cara hacia abajo; positivo gira como las agujas del reloj)."""
    T = _xf(cx, cy, H, ang)
    # mango: perfil con cintura y empuñadura más gruesa
    us = np.linspace(0.05, 0.985, 30)
    hw = np.interp(us, [0.05, 0.15, 0.45, 0.70, 0.86, 0.95, 0.985], [0.030, 0.028, 0.025, 0.031, 0.037, 0.038, 0.034])
    arriba = [(u, -w) for u, w in zip(us, hw)]
    abajo = [(u, w) for u, w in zip(us, hw)][::-1]
    tapa = [(0.985 + 0.034 * math.cos(a), 0.034 * math.sin(a)) for a in np.linspace(-math.pi / 2, math.pi / 2, 12)]
    mango = arriba + tapa + abajo
    # cabeza: bloque del ojo, cuello y cara ensanchada
    cuerpo = [(-0.062, -0.085), (0.062, -0.085), (0.062, 0.058), (0.046, 0.090), (0.040, 0.120), (0.039, 0.185),
              (0.046, 0.212), (0.056, 0.236), (0.060, 0.256), (0.057, 0.272), (0.048, 0.287), (-0.048, 0.287),
              (-0.057, 0.272), (-0.060, 0.256), (-0.056, 0.236), (-0.046, 0.212), (-0.039, 0.185),
              (-0.040, 0.120), (-0.046, 0.090), (-0.062, 0.058)]
    # uña: curva que vuelve hacia el mango y se afina
    cen = _curva((0.0, -0.06), (0.0, -0.21), (0.07, -0.31), (0.225, -0.318), 26)
    ext, inn = [], []
    for i, (u, v) in enumerate(cen):
        a = cen[max(0, i - 1)]
        b = cen[min(len(cen) - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        nl = math.hypot(tx, ty) or 1
        nx, ny = -ty / nl, tx / nl
        s = i / (len(cen) - 1)
        w = 0.062 * (1 - s) ** 0.85 + 0.004
        ext.append((u - nx * w, v - ny * w))
        inn.append((u + nx * w, v + ny * w))
    una = ext + inn[::-1]
    P = lambda pts: [T(u, v) for u, v in pts]
    if sombra:
        dx, dy = 9, 13
        for forma in (mango, cuerpo, una):
            poligono(L, [(x + dx, y + dy) for x, y in P(forma)], (0, 0, 0), alpha=0.32, cam=cam)
    relleno_gradiente(L, P(mango), MADERA_MANGO, T(0.5, -0.038), T(0.5, 0.038), cam=cam)
    # vetas del mango
    for k, (v0, amp, fase, al) in enumerate(((-0.013, 0.004, 0.3, 0.55), (0.004, 0.005, 1.7, 0.45),
                                            (0.017, 0.003, 2.9, 0.5), (-0.004, 0.003, 4.0, 0.3))):
        pts = [T(u, v0 + amp * math.sin(u * 9 + fase) * (0.5 + u)) for u in np.linspace(0.1 + 0.05 * k, 0.95, 26)]
        linea(L, pts, (120, 74, 38), 0.0042 * H, alpha=al, cam=cam)
    poligono(L, [T(0.62, -0.006), T(0.75, -0.012), T(0.80, -0.004), T(0.70, 0.0)], (126, 78, 40), alpha=0.45, cam=cam)
    # brillo del mango
    linea(L, [T(u, -0.017 - 0.004 * u) for u in np.linspace(0.14, 0.9, 12)], (246, 214, 160), 0.0035 * H, alpha=0.5, cam=cam)
    # acero
    relleno_gradiente(L, P(una), [(0, (226, 230, 236)), (0.45, (150, 156, 168)), (1, (70, 74, 84))],
                      T(-0.03, -0.30), T(0.10, -0.15), cam=cam)
    relleno_gradiente(L, P(cuerpo), METAL, T(-0.062, 0), T(0.062, 0), cam=cam)
    # bisel de la cara y canto del bloque
    poligono(L, P([(-0.057, 0.272), (0.057, 0.272), (0.048, 0.287), (-0.048, 0.287)]), (236, 239, 244), alpha=0.85, cam=cam)
    linea(L, P([(-0.056, -0.07), (-0.056, 0.05)]), (246, 248, 250), 0.006 * H, alpha=0.55, cam=cam)
    linea(L, P([(-0.04, 0.125), (0.04, 0.125)]), (40, 44, 52), 0.004 * H, alpha=0.5, cam=cam)
    # bisel interior de la uña (sugiere la ranura)
    linea(L, P(inn[6:-2]), (52, 56, 64), 0.006 * H, alpha=0.7, cam=cam)


def tabla(L, x0, x1, yf, alto, prof=50, semilla=5, cam=True):
    """Tablón de madera en corte: cara de arriba (veta larga en perspectiva) y frente con vetas, nudo y
    bandas de crecimiento. yf = borde de adelante de la cara de arriba."""
    rng = np.random.default_rng(semilla)
    ins = 28
    sup = [(x0, yf), (x1, yf), (x1 - ins, yf - prof), (x0 + ins, yf - prof)]
    relleno_gradiente(L, sup, [(0, (178, 124, 72)), (1, (220, 166, 104))], (0, yf - prof), (0, yf), cam=cam)
    for f_ in (0.18, 0.37, 0.55, 0.74, 0.9):
        y = yf - prof * (1 - f_)
        xa, xb = x0 + ins * (1 - f_), x1 - ins * (1 - f_)
        pts = [(x, y + 1.6 * math.sin(x / 47 + f_ * 9)) for x in np.linspace(xa + 6, xb - 6, 40)]
        linea(L, pts, (160, 106, 58), 1.6 + f_, alpha=0.55, cam=cam)
    # frente
    fr = [(x0, yf), (x1, yf), (x1, yf + alto), (x0, yf + alto)]
    relleno_gradiente(L, fr, [(0, (196, 136, 78)), (0.5, (176, 118, 66)), (1, (140, 92, 50))], (0, yf), (0, yf + alto), cam=cam)
    nudos = [(x0 + (x1 - x0) * 0.72, yf + alto * 0.42, 26), (x0 + (x1 - x0) * 0.2, yf + alto * 0.74, 12)]
    n = 17
    xs = np.linspace(x0, x1, 90)
    for i in range(n):
        base = yf + alto * (i + 0.6) / (n + 0.4) + rng.uniform(-6, 6)
        a1, l1, f1 = rng.uniform(3, 9), rng.uniform(260, 520), rng.uniform(0, 6.3)
        a2, l2, f2 = rng.uniform(1, 3), rng.uniform(70, 140), rng.uniform(0, 6.3)
        ys = base + a1 * np.sin(xs / l1 * 6.283 + f1) + a2 * np.sin(xs / l2 * 6.283 + f2)
        for kx, ky, kr in nudos:
            dd = base - ky
            ys = ys + np.sign(dd if dd != 0 else 1) * kr * 1.9 * np.exp(-((xs - kx) / (kr * 2.6)) ** 2) * math.exp(-(dd / (kr * 3.2)) ** 2)
        ancho = rng.uniform(1.4, 3.6)
        oscuro = rng.uniform(0, 1) < 0.7
        col = (134, 84, 42) if oscuro else (222, 172, 112)
        linea(L, list(zip(xs, ys)), col, ancho, alpha=rng.uniform(0.35, 0.75) if oscuro else 0.35, cam=cam)
    for kx, ky, kr in nudos:
        poligono(L, elipse_pts(kx, ky, kr * 1.45, kr, n=40), (128, 78, 38), alpha=0.9, cam=cam)
        for k in (0.95, 0.62):
            linea(L, elipse_pts(kx, ky, kr * 1.45 * k, kr * k, n=40), (96, 58, 28), 2.2, alpha=0.8, cam=cam)
        poligono(L, elipse_pts(kx, ky, kr * 0.42, kr * 0.3, n=24), (78, 46, 22), cam=cam)
    # cantos: luz en el borde de arriba, sombra en los costados
    linea(L, [(x0, yf), (x1, yf)], (244, 204, 146), 3, cam=cam)
    linea(L, [(x0 + ins, yf - prof), (x1 - ins, yf - prof)], (150, 100, 56), 2, alpha=0.8, cam=cam)
    for xa, xb in ((x0, x0 + 14), (x1 - 14, x1)):
        relleno_gradiente(L, [(xa, yf), (xb, yf), (xb, yf + alto), (xa, yf + alto)],
                          [(0, (40, 24, 12, 110 if xa == x0 else 0)), (1, (40, 24, 12, 0 if xa == x0 else 110))],
                          (xa, 0), (xb, 0), cam=cam)


def suelo(L, y, x0=-300, x1=1400, prof=700, semilla=3, cam=True):
    """Suelo de tierra en corte: capa de humus, estratos ondulados y piedras."""
    rng = np.random.default_rng(semilla)
    relleno_gradiente(L, [(x0, y), (x1, y), (x1, y + prof), (x0, y + prof)],
                      [(0, (104, 74, 50)), (0.12, (96, 68, 46)), (0.5, (74, 52, 36)), (1, (44, 32, 24))],
                      (0, y), (0, y + prof), cam=cam)
    xs = np.linspace(x0, x1, 120)
    hum = [(x, y + 26 + 4 * math.sin(x / 60) + 3 * math.sin(x / 23)) for x in xs]
    poligono(L, [(x0, y)] + hum + [(x1, y)], (70, 50, 36), cam=cam)
    for k, (dy, a) in enumerate(((74, 7), (150, 10), (240, 12))):
        pts = [(x, y + dy + a * math.sin(x / (90 + 30 * k) + k) + 3 * math.sin(x / 31 + k * 2)) for x in xs]
        linea(L, pts, (58, 40, 28), 3, alpha=0.7, cam=cam)
        linea(L, [(px, py + 4) for px, py in pts], (128, 96, 68), 1.4, alpha=0.3, cam=cam)
    for _ in range(60):
        px, py = rng.uniform(x0, x1), y + rng.uniform(34, 320)
        r = rng.uniform(3, 13)
        col = [(132, 104, 78), (90, 68, 50), (150, 124, 96), (112, 90, 70)][rng.integers(0, 4)]
        rot = rng.uniform(0, 180)
        poligono(L, elipse_pts(px, py, r * 1.4, r, n=16, rot=rot), col, alpha=0.9, cam=cam)
        poligono(L, elipse_pts(px - r * 0.3, py - r * 0.35, r * 0.6, r * 0.3, n=10, rot=rot), (196, 170, 140), alpha=0.35, cam=cam)
    linea(L, [(x0, y), (x1, y)], (156, 122, 88), 3, cam=cam)


def persona(L, x, y, alto, color=None, cam=True):
    """Silueta humana gris (de pie, mirando hacia la izquierda y un poco arriba) para dar escala."""
    c = color or rgb(L.e["gris"])
    c2 = mezcla(c, (0, 0, 0), 0.22)
    h = alto
    Pp = lambda u, v: (x + u * h, y + v * h)
    poligono(L, elipse_pts(x - 0.02 * h, y, 0.2 * h, 0.03 * h, n=24), (0, 0, 0), alpha=0.35, cam=cam)
    # lado de atrás (más oscuro)
    linea(L, [Pp(0.045, -0.47), Pp(0.055, -0.25), Pp(0.06, -0.035)], c2, 0.078 * h, cam=cam)
    poligono(L, elipse_pts(x + 0.035 * h, y - 0.02 * h, 0.065 * h, 0.022 * h, n=16), c2, cam=cam)
    linea(L, [Pp(0.10, -0.765), Pp(0.125, -0.62), Pp(0.115, -0.49)], c2, 0.056 * h, cam=cam)
    # torso, cuello, cabeza (mirando arriba: la cabeza un poco hacia atrás)
    poligono(L, [Pp(-0.105, -0.80), Pp(0.11, -0.80), Pp(0.10, -0.52), Pp(-0.09, -0.52)], c, cam=cam)
    for u in (-0.075, 0.08):
        circulo(L, *Pp(u, -0.77), 0.042 * h, c, cam=cam)
    poligono(L, [Pp(-0.095, -0.56), Pp(0.10, -0.56), Pp(0.095, -0.45), Pp(-0.085, -0.45)], c2, cam=cam)
    poligono(L, [Pp(-0.03, -0.86), Pp(0.035, -0.86), Pp(0.032, -0.79), Pp(-0.028, -0.79)], c, cam=cam)
    poligono(L, elipse_pts(x + 0.012 * h, y - 0.905 * h, 0.064 * h, 0.071 * h, n=28, rot=-25), c, cam=cam)
    poligono(L, [Pp(-0.06, -0.93), Pp(-0.085, -0.95), Pp(-0.058, -0.965)], c, cam=cam)   # nariz
    # lado de adelante
    linea(L, [Pp(-0.045, -0.47), Pp(-0.052, -0.25), Pp(-0.058, -0.035)], c, 0.078 * h, cam=cam)
    poligono(L, elipse_pts(x - 0.085 * h, y - 0.02 * h, 0.07 * h, 0.022 * h, n=16), c, cam=cam)
    linea(L, [Pp(-0.095, -0.765), Pp(-0.125, -0.62), Pp(-0.112, -0.49)], c, 0.056 * h, cam=cam)


def destello(L, x, y, edad, angulos=(150, 180, 210), cam=True):
    """Golpe: destello del color de energía + líneas de impacto cortas (en la capa de energía)."""
    if edad < 0 or edad > 0.45:
        return
    p = clamp(edad / 0.32)
    if edad < 0.12:
        circulo(L, x, y, 14 + 16 * ease_entrada(edad / 0.12), capa="energia", alpha=0.85 * (1 - edad / 0.12), cam=cam)
    r = 34 + 72 * ease_entrada(p)
    m, d = L.temporal()
    poligono(L, elipse_pts(x, y, r, r * 0.42, n=48), capa=d, cam=cam)
    poligono(L, elipse_pts(x, y, max(0, r - 9 * (1 - p) - 2), max(0, r * 0.42 - 6 * (1 - p) - 1), n=48), capa=d, alpha=0, cam=cam)
    L.fundir(m, alpha=(1 - p) * 0.9, capa="energia")
    for a in angulos:
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        r_out = 58 + 92 * ease_entrada(clamp(edad / 0.2))
        r_in = 58 + 86 * ease_entrada(clamp((edad - 0.06) / 0.3))
        if r_out - r_in > 3:
            linea(L, [(x + ca * r_in, y + sa * r_in * 0.8), (x + ca * r_out, y + sa * r_out * 0.8)], ancho=8, capa="energia", cam=cam)


def polvo(L, x, y, edad, n=9, semilla=11, color=(226, 188, 136), cam=True):
    """Aserrín que salta cuando algo entra en la madera o la tierra."""
    if edad < 0 or edad > 0.7:
        return
    rng = np.random.default_rng(semilla)
    for _ in range(n):
        lado = rng.choice((-1, 1))
        vx, vy = lado * rng.uniform(60, 190), -rng.uniform(40, 140)
        r = rng.uniform(3, 7)
        p = ease_entrada(clamp(edad / 0.6))
        px, py = x + vx * p, y + vy * p + 260 * (edad ** 2)
        circulo(L, px, min(py, y + 6), r * (1 - 0.5 * p), color, alpha=(1 - clamp(edad / 0.7)) * 0.9, cam=cam)
