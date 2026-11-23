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


GRANO_VIVO = False  # grano distinto en cada cuadro = archivo enorme (79,6 MB por 7,6 s en el duelo): por defecto, quieto
_FONDOS = {}


def fondo(estilo, semilla=0, w=ANCHO, h=ALTO, luz=(0.46, 0.40), grano=None):
    """Fondo del estilo: color con luz central, viñeta suave, retícula HUD y grano. El grano es QUIETO por
    defecto (se ve igual de "papel fotográfico" y el video comprime ~10 veces mejor); GRANO_VIVO=True lo anima."""
    g = estilo["grano"] if grano is None else grano
    semilla = semilla if GRANO_VIVO else 0
    clave = (estilo["clave"], semilla, w, h, tuple(luz), g)
    if clave in _FONDOS:
        return _FONDOS[clave].copy()
    base = _fondo_base(estilo["clave"], w, h, tuple(luz))
    rng = np.random.default_rng(semilla)
    n = rng.standard_normal((h, w), dtype=np.float32) * g
    im = Image.fromarray(np.clip(base + n[..., None], 0, 255).astype(np.uint8), "RGB")
    if not GRANO_VIVO:
        _FONDOS[clave] = im.copy()
    return im


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

    def __init__(self, estilo, semilla=0, w=ANCHO, h=ALTO, ss=SS, luz=(0.46, 0.40), fondo_img=None):
        self.e, self.w, self.h, self.ss, self.semilla = estilo, w, h, ss, semilla
        # fondo_img: un fondo ya hecho a 1x (fondo_estudio o fondo_capas); si no, el fondo simple del estilo
        self.fondo1 = fondo_img if fondo_img is not None else fondo(estilo, semilla, w, h, luz)
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
        # grano fino sobre todo (quieto salvo GRANO_VIVO: el grano animado multiplica el peso del video)
        if GRANO_VIVO:
            rng = np.random.default_rng(self.semilla + 7919)
            arr = arr + rng.standard_normal(arr.shape[:2], dtype=np.float32)[..., None] * (self.e["grano"] * 0.45)
        else:
            arr = arr + _ruido(arr.shape[1], arr.shape[0], self.e["grano"] * 0.45, 7919)[..., None]
        out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
        for f in self.post:
            f(out)
        return out


def _c(color, capa, alpha=1.0):
    a = int(round(255 * clamp(alpha)))
    if capa == "base" or getattr(capa, "mode", "L") == "RGBA":     # base o una capa RGBA (desenfoque)
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


def texto(L, x, y, s, tam, color=(255, 255, 255), peso="black", anchor="ls", capa="base", alpha=1.0, cam=False,
          trazo=0):
    """Texto; trazo = contorno oscuro en px (≥4 para que se lea en el celular sobre cualquier fondo)."""
    X, Y = L.P(x, y, cam)
    f = fuente(L.S(tam, cam), peso)
    if alpha < 0.004:                    # ojo: PIL dibuja OPACO el texto con tinta de alfa 0
        return f.getlength(s) / L.S(1, cam)
    if trazo and capa == "base":
        L.d.text((X, Y), s, font=f, fill=_c(color, capa, alpha), anchor=anchor, stroke_width=int(round(L.S(trazo, cam))),
                 stroke_fill=(8, 9, 12, int(255 * alpha)))
        return f.getlength(s) / L.S(1, cam)
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
             peso="black", cam=False, alin="izq", rueda=False):
    # rueda=False (por defecto): salta de cifra en cifra; congelado nunca muestra medio digito
    # (duelo visual 23-nov: los jueces lo vieron como falla). rueda=True: odometro.
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
    v = round(float(valor), 5) if rueda else float(round(float(valor)))
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
            texto(L, x, base1, texto_, tam, tinta, "black", alpha=a, cam=cam, trazo=5)
        else:
            if caption:
                texto(L, x, base_c, caption, tc, gris, "black", alpha=a, cam=cam, trazo=4)
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


def _vis(w):
    """Como se ve la palabra en pantalla: MAYUSCULAS y sin puntuacion final (mas legible en el celular)."""
    return w.upper().rstrip(".,;:")


Y_MIN_SUB = 250          # nada de los subtítulos sobre esta línea: la barra de la app tapa los ~230 px de arriba


def preparar_subtitulos(words, claves, tam=112, ancho_max=860, x_centro=490, y_centro=None, y_arriba=300,
                        max_pal=3, pausa=0.32, achica_min=0.85, hueco_clave=0.3):
    """Arma los grupos de 1–3 palabras (sin partir una frase clave, cortando en puntuación y pausas)
    y fija la posición de cada palabra: el grupo no se mueve mientras se lee.
    Zona por defecto: ARRIBA (y_arriba = tope de las mayúsculas de la 1.ª línea, bajo la barra de la app),
    como los virales de referencia. y_centro (en vez de y_arriba) centra el bloque en esa y (modo antiguo)."""
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
    salida = []

    def largo(ln, f, esp, tam_g):
        # ancho de una línea: palabras + espacios; entre una palabra clave y una que no lo es va un hueco extra
        # (la píldora necesita aire: así nunca pisa a la palabra blanca de al lado)
        tot = sum(f.getlength(_vis(words[i]["w"])) for i in ln)
        for a, b in zip(ln, ln[1:]):
            tot += esp + (hueco_clave * tam_g if (span[a] is None) != (span[b] is None) else 0)
        return tot

    for gi, g in enumerate(grupos):
        # si no cabe, primero se achica (hasta achica_min) y sólo después se parte en dos líneas
        tam_g = tam
        f = fuente(tam_g, "black")
        esp = f.getlength(" ")
        total = largo(g, f, esp, tam_g)
        if total > ancho_max:
            tam_g = max(tam * achica_min, math.floor(tam * ancho_max / total * 0.99))
            f = fuente(tam_g, "black")
            esp = f.getlength(" ")
        total = largo(g, f, esp, tam_g)
        if total <= ancho_max or len(g) == 1:
            lineas = [g]
        else:                                        # dos líneas: el corte más parejo
            mejor = None
            for c in range(1, len(g)):
                m_ = max(largo(g[:c], f, esp, tam_g), largo(g[c:], f, esp, tam_g))
                if mejor is None or m_ < mejor[0]:
                    mejor = (m_, c)
            lineas = [g[:mejor[1]], g[mejor[1]:]]
        alto_l = tam_g * 1.06
        pos = {}
        for li, ln in enumerate(lineas):
            if y_centro is not None:
                base = y_centro + CAP * tam_g / 2 + (li - (len(lineas) - 1) / 2) * alto_l
            else:
                base = y_arriba + CAP * tam_g + li * alto_l
            x = x_centro - largo(ln, f, esp, tam_g) / 2
            for k_, i in enumerate(ln):
                wv = f.getlength(_vis(words[i]["w"]))
                pos[i] = (x, base, wv)
                if k_ + 1 < len(ln):
                    x += wv + esp + (hueco_clave * tam_g if (span[i] is None) != (span[ln[k_ + 1]] is None) else 0)
        # la 1.ª línea queda anclada arriba y el bloque crece hacia ABAJO; si algo (contorno, píldora) pasara sobre
        # Y_MIN_SUB, se baja el grupo entero
        tope = min(b for _, b, _ in pos.values()) - CAP * tam_g - max(0.17 * tam_g, 9) - 2
        if tope < Y_MIN_SUB:
            pos = {i: (x, b + Y_MIN_SUB - tope, w) for i, (x, b, w) in pos.items()}
        assert min(b for _, b, _ in pos.values()) - CAP * tam_g - max(0.17 * tam_g, 9) - 2 >= Y_MIN_SUB - 0.5
        miembros = {}
        for i in g:
            if span[i] is not None:
                miembros.setdefault(span[i], []).append(i)
        t_ini = 0.0 if gi == 0 else words[g[0]]["s"] - 0.03
        salida.append(dict(idx=g, pos=pos, miembros=miembros, t0=t_ini, tam=tam_g))
    for gi in range(len(salida)):
        salida[gi]["t1"] = salida[gi + 1]["t0"] if gi + 1 < len(salida) else 1e9
    return salida


def _caja_clave(g, dichas, pad_x, arriba, abajo):
    """Caja que abraza sólo las palabras clave ya dichas (crece palabra a palabra, también en 2 líneas)."""
    x0 = min(g["pos"][i][0] for i in dichas) - pad_x
    x1 = max(g["pos"][i][0] + g["pos"][i][2] for i in dichas) + pad_x
    filas = sorted({g["pos"][i][1] for i in dichas})
    return x0, filas[0] - CAP * g["tam"] - arriba, x1, filas[-1] + abajo


def subtitulos(L, words, t, claves, tam=112, estilo_clave="pildora", ocultar=(), **kw):
    """Subtítulos palabra por palabra, 1–3 palabras, Inter Black en MAYÚSCULAS, arriba (bajo la barra de la app).
    Blanco con contorno grueso y sombra suave. La palabra clave va en una PÍLDORA llena del color de energía con
    letra oscura (entra con un pop) — estilo_clave='recuadro' vuelve al recuadro con manillas del duelo.
    ocultar = palabras (normalizadas) que NO se muestran: cuando un número héroe ya dice "20 M", el subtítulo no lo
    repite al mismo tiempo (el resto del grupo queda en su lugar)."""
    clave_cache = (id(words), tuple(claves), tam, tuple(sorted(kw.items())))
    if clave_cache not in _CACHE_SUB:
        _CACHE_SUB[clave_cache] = preparar_subtitulos(words, claves, tam, **kw)
    grupos = _CACHE_SUB[clave_cache]
    g = next((g for g in grupos if g["t0"] <= t < g["t1"]), None)
    if g is None:
        return
    dicha = {}
    for i in g["idx"]:
        ts = 0.0 if (g["t0"] == 0.0 and i == g["idx"][0]) else words[i]["s"] - 0.04
        if t >= ts and _norm(words[i]["w"]) not in ocultar:
            dicha[i] = ease_entrada(tramo(t, ts, 0.16))
    en_clave = set()
    for i0, mm in g["miembros"].items():
        dichas = [i for i in mm if i in dicha]
        if not dichas:
            continue
        en_clave.update(mm)
        ts = 0.0 if (g["t0"] == 0.0 and i0 == g["idx"][0]) else words[i0]["s"] - 0.04
        a = ease_entrada(tramo(t, ts, 0.2))
        m, d = L.temporal()
        if estilo_clave == "pildora":
            # una píldora por línea, medida sobre la tinta real de las letras (misma línea base que el blanco)
            sc = 0.82 + 0.18 * a                                  # pop
            ft, tg = fuente(g["tam"], "black"), g["tam"]
            for b in sorted({g["pos"][i][1] for i in dichas}):
                fila = [i for i in dichas if g["pos"][i][1] == b]
                x0 = min(g["pos"][i][0] + ft.getbbox(_vis(words[i]["w"]), anchor="ls")[0] for i in fila) - 0.2 * tg
                x1 = max(g["pos"][i][0] + ft.getbbox(_vis(words[i]["w"]), anchor="ls")[2] for i in fila) + 0.2 * tg
                y0, y1 = b - CAP * tg - 0.17 * tg, b + 0.17 * tg
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                X0, Y0 = L.P(cx + (x0 - cx) * sc, cy + (y0 - cy) * sc, False)
                X1, Y1 = L.P(cx + (x1 - cx) * sc, cy + (y1 - cy) * sc, False)
                d.rounded_rectangle([X0, Y0, X1, Y1], radius=L.S(0.18 * tg, False), fill=255)
        else:
            x0, y0, x1, y1 = _caja_clave(g, dichas, 20, 16, 0.2 * g["tam"] + 6)
            sc = 1.10 - 0.10 * a
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            X0, Y0 = L.P(cx + (x0 - cx) * sc, cy + (y0 - cy) * sc, False)
            X1, Y1 = L.P(cx + (x1 - cx) * sc, cy + (y1 - cy) * sc, False)
            d.rectangle([X0, Y0, X1, Y1], fill=28)
            d.rectangle([X0, Y0, X1, Y1], outline=255, width=int(round(L.S(6, False))))
            h = L.S(7, False)
            for hx, hy in ((X0, Y0), (X1, Y0), (X0, Y1), (X1, Y1)):
                hx += L.S(3, False) if hx == X0 else -L.S(3, False)
                hy += L.S(3, False) if hy == Y0 else -L.S(3, False)
                d.rectangle([hx - h, hy - h, hx + h, hy + h], fill=255)
        L.fundir(m, alpha=a, capa="energia")
    f = fuente(g["tam"], "black")
    oscuro = rgb(L.e["fondo"])
    pildora = estilo_clave == "pildora"

    def dibujar(img, dicha=dicha, g=g, en_clave=en_clave):
        if not dicha:
            return
        ys = [g["pos"][i][1] for i in dicha]
        y0, y1 = int(min(ys) - g["tam"] - 40), int(max(ys) + 60)
        # sombra suave (sólo de las palabras blancas)
        m = Image.new("L", (img.size[0], y1 - y0), 0)
        dm = ImageDraw.Draw(m)
        for i, a in dicha.items():
            if pildora and i in en_clave:
                continue
            x, b, _ = g["pos"][i]
            dm.text((x, b - y0 + 8), _vis(words[i]["w"]), font=f, fill=int(255 * a), anchor="ls",
                    stroke_width=9, stroke_fill=int(255 * a))
        m = m.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.7))
        img.paste((0, 0, 0), (0, y0), m)
        d = ImageDraw.Draw(img, "RGBA")
        for i, a in dicha.items():
            x, b, _ = g["pos"][i]
            al = int(255 * a)
            if al < 1:                   # PIL dibuja opaco el texto con alfa 0
                continue
            if pildora and i in en_clave:
                d.text((x, b), _vis(words[i]["w"]), font=f, fill=oscuro + (al,), anchor="ls")
            else:
                d.text((x, b), _vis(words[i]["w"]), font=f, fill=(255, 255, 255, al), anchor="ls",
                       stroke_width=9, stroke_fill=(9, 10, 13, al))
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


# ==================================================================================================================
# v3 (23-nov-2026, ronda contra virales): luz y profundidad, 3D liviano, impacto, HUD (inset, regla, pictogramas,
# número héroe) y objetos nuevos. Todo sigue siendo función del tiempo y del lienzo L.
# ==================================================================================================================
CALIDO = (255, 222, 178)     # luz clave: cálida, arriba a la izquierda
FRIO = (150, 196, 255)       # luz de borde: fría, a la derecha
_RUIDOS = {}


def _ruido(w, h, g, semilla=0):
    """Grano quieto (se calcula una vez por proceso)."""
    k = (w, h, round(g, 3), semilla)
    if k not in _RUIDOS:
        _RUIDOS[k] = np.random.default_rng(semilla).standard_normal((h, w), dtype=np.float32) * g
    return _RUIDOS[k]


@lru_cache(maxsize=4)
def _vineta(w, h, fuerza=0.55):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rc = np.hypot((xx - w / 2) / (w * 0.5), (yy - h / 2) / (h * 0.5))
    v = np.clip((rc - 0.45) / 0.95, 0, 1)
    v = v * v * (3 - 2 * v)
    return (1 - fuerza * v)[..., None]


def _acabar(arr_chico, estilo, w, h):
    """Sube un fondo calculado a 1/4 de resolución, le pone viñeta radial y grano quieto."""
    im = Image.fromarray(np.clip(arr_chico, 0, 255).astype(np.uint8), "RGB").resize((w, h), Image.BILINEAR)
    arr = np.asarray(im, np.float32) * _vineta(w, h) + _ruido(w, h, estilo["grano"])[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


_ESTUDIO = {}


def fondo_estudio(estilo, luz=(0.22, 0.2), w=ANCHO, h=ALTO):
    """Fondo de estudio oscuro: charco de luz cálida arriba a la izquierda, caída fría a la derecha."""
    clave = (estilo["clave"], tuple(luz), w, h)
    if clave not in _ESTUDIO:
        q = 4
        yy, xx = np.mgrid[0:h // q, 0:w // q].astype(np.float32) * q
        base = np.array(rgb(estilo["fondo"]), np.float32)
        r = np.hypot((xx - luz[0] * w) / h, (yy - luz[1] * h) / h)
        k = np.exp(-(r / 0.42) ** 2)[..., None]
        frio = np.clip((xx / w - 0.55) / 0.45, 0, 1)[..., None] * np.clip(1 - yy / h, 0.3, 1)[..., None]
        arr = base * (1 - 0.15 * frio) + np.array((44, 30, 18), np.float32) * k + np.array((0, 6, 16), np.float32) * frio
        _ESTUDIO[clave] = _acabar(arr, estilo, w, h)
    return _ESTUDIO[clave].copy()


_CIELOS = {}
CIELO = [(-4000, (14, 12, 18)), (-260, (28, 22, 30)), (-30, (150, 84, 50)), (0, (255, 164, 74)), (40, (250, 120, 66)),
         (140, (214, 84, 92)), (300, (128, 56, 112)), (560, (58, 40, 104)), (1050, (22, 24, 64)), (2600, (8, 10, 28))]


def fondo_capas(estilo, horizonte, sol_x=0.16, w=ANCHO, h=ALTO):
    """Cielo de atardecer en capas: cenit azul noche → bruma → resplandor cálido en el horizonte (el sol bajo a la
    izquierda es la misma luz clave). Las siluetas del medio y el suelo se dibujan encima (edificios3d, suelo3d)."""
    clave = (estilo["clave"], int(round(horizonte / 2)), sol_x, w, h)
    if clave in _CIELOS:
        return _CIELOS[clave].copy()
    q = 4
    yy, xx = np.mgrid[0:h // q, 0:w // q].astype(np.float32) * q
    d = horizonte - yy
    pos = np.array([c[0] for c in CIELO], np.float32)
    cols = np.array([c[1] for c in CIELO], np.float32)
    arr = np.stack([np.interp(d, pos, cols[:, k]) for k in range(3)], -1)
    r = np.hypot((xx - sol_x * w) / h, (yy - horizonte) / h * 1.6)
    arr += np.array((130, 70, 16), np.float32) * np.exp(-(r / 0.38) ** 2)[..., None]
    im = _acabar(arr, estilo, w, h)
    if len(_CIELOS) > 40:
        _CIELOS.clear()
    _CIELOS[clave] = im
    return im.copy()


# ------------------------------------------------------------------ cámaras
class Cam3D:
    """Cámara de agujero (pinhole) liviana: mundo en metros (X derecha, Y profundidad, Z arriba).
    pitch en grados (positivo = mira hacia arriba). pr(X, Y, Z) → (x, y) de pantalla."""

    def __init__(self, Y=-60.0, Z=4.0, pitch=0.0, F=2376.0, cx=500.0, cy=1162.0, X=0.0):
        self.X, self.Y, self.Z, self.pitch, self.F, self.cx, self.cy = X, Y, Z, pitch, F, cx, cy
        self.c, self.s = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))

    def _prof(self, X, Y, Z):
        ry, rz = Y - self.Y, Z - self.Z
        return ry * self.c + rz * self.s, -ry * self.s + rz * self.c

    def pr(self, X, Y, Z):
        prof, up = self._prof(X, Y, Z)
        prof = max(prof, 0.05)
        return (self.cx + self.F * (X - self.X) / prof, self.cy - self.F * up / prof)

    def escala(self, X, Y, Z):
        return self.F / max(self._prof(X, Y, Z)[0], 0.05)

    def horizonte(self):
        return self.cy + self.F * math.tan(math.radians(self.pitch))

    @staticmethod
    def mezcla(a, b, k):
        """Interpola dos cámaras (distancias y focal en escala logarítmica: el 'dolly zoom' se ve parejo)."""
        lg = lambda u, v: math.exp(math.log(u) + (math.log(v) - math.log(u)) * k)
        li = lambda u, v: u + (v - u) * k
        return Cam3D(Y=-lg(-a.Y, -b.Y), Z=lg(a.Z, b.Z), pitch=li(a.pitch, b.pitch), F=lg(a.F, b.F),
                     cx=li(a.cx, b.cx), cy=li(a.cy, b.cy), X=li(a.X, b.X))


def proyector_oblicuo(cx, y_suelo, escala=1.0, elev=0.30):
    """Proyector 'casi de frente, un poco desde arriba' para planos de estudio (unidades = px de pantalla)."""
    k = math.sin(elev)

    def pr(X, Y, Z):
        return (cx + X * escala, y_suelo - Z * escala - Y * escala * k)
    return pr


# ------------------------------------------------------------------ luz
def luz_clave(color, k=0.35):
    """Tiñe un color con la luz clave cálida."""
    return mezcla(color, CALIDO, k)


def borde_frio(L, pts, ancho=3, alpha=0.85, cam=True):
    """Luz de borde fría: línea fina azulada sobre el canto derecho de un objeto."""
    linea(L, pts, FRIO, ancho, alpha=alpha, cam=cam)


def sombra_contacto(L, cx, cy, rx, ry, alpha=0.6, capas=9, cam=True):
    """Sombra elíptica suave (capas concéntricas): el objeto se apoya, no flota."""
    for i in range(capas):
        k = 1 - i / capas
        poligono(L, elipse_pts(cx, cy, rx * (0.3 + 0.7 * k), ry * (0.3 + 0.7 * k), n=44), (0, 0, 0),
                 alpha=min(1, alpha * 1.6 / capas), cam=cam)


def ao(L, x0, x1, y, alto=30, alpha=0.55, cam=True):
    """Oclusión ambiental: banda oscura suave justo donde un objeto toca una superficie."""
    relleno_gradiente(L, [(x0, y - alto), (x1, y - alto), (x1, y + alto * 0.5), (x0, y + alto * 0.5)],
                      [(0, (0, 0, 0, 0)), (0.66, (0, 0, 0, int(255 * alpha))), (1, (0, 0, 0, 0))],
                      (0, y - alto), (0, y + alto * 0.5), cam=cam)


class desenfoque:
    """with desenfoque(L, radio) as d: ... dibuja en una capa aparte que se desenfoca (primer plano fuera de foco)."""

    def __init__(self, L, radio=6):
        self.L, self.radio = L, radio

    def __enter__(self):
        self.capa = Image.new("RGBA", self.L.im.size, (0, 0, 0, 0))
        return ImageDraw.Draw(self.capa, "RGBA")

    def __exit__(self, *a):
        bb = self.capa.getbbox()
        if not bb:
            return
        L, pad = self.L, int(self.radio * self.L.ss * 3)
        bb = (max(0, bb[0] - pad), max(0, bb[1] - pad), min(L.im.size[0], bb[2] + pad), min(L.im.size[1], bb[3] + pad))
        capa = self.capa.crop(bb).filter(ImageFilter.GaussianBlur(self.radio * L.ss))
        base = L.im.crop(bb).convert("RGBA")
        base.alpha_composite(capa)
        L.im.paste(base.convert("RGB"), bb[:2])


def temblor(edad, amp=12, cuadros=8, fps=FPS):
    """Temblor de cámara que se apaga en ~'cuadros' cuadros. Devuelve (dx, dy)."""
    if edad < 0 or edad > cuadros / fps:
        return (0.0, 0.0)
    k = (1 - edad * fps / cuadros) ** 2
    return (amp * k * math.sin(edad * 97), amp * 0.8 * k * math.cos(edad * 71))


def flash_blanco(L, alpha=0.8):
    """Un cuadro blanco encima de todo (el golpe)."""
    def f(img, a=alpha):
        img.paste(Image.blend(img, Image.new("RGB", img.size, (255, 250, 240)), a))
    L.post.insert(0, f)


# ------------------------------------------------------------------ impacto
def impacto(L, x, y, edad, escala=1.0, ry=0.34, chispas=11, semilla=3, cam=True):
    """Golpe metal contra metal: núcleo, 3 anillos de onda en el plano de la superficie, 8–12 chispas con gravedad.
    Todo en la capa de energía (brilla). edad = segundos desde el contacto."""
    if edad < 0 or edad > 0.7:
        return
    s = escala
    if edad < 0.1:
        circulo(L, x, y, (22 + 46 * ease_entrada(edad / 0.1)) * s, capa="energia", alpha=1 - edad / 0.1, cam=cam)
    for k in range(3):
        e = edad - k * 0.05
        if 0 <= e < 0.42:
            p = ease_entrada(e / 0.42)
            r = (50 + 330 * p) * s * (1 - 0.2 * k)
            w = max(1.6, (13 - 3.5 * k) * (1 - 0.7 * p)) * s
            m, d = L.temporal()
            poligono(L, elipse_pts(x, y, r, r * ry, n=80), capa=d, cam=cam)
            poligono(L, elipse_pts(x, y, max(0.1, r - w), max(0.1, r * ry - w * 0.6), n=80), capa=d, alpha=0, cam=cam)
            L.fundir(m, alpha=(1 - p) * 0.95, capa="energia")
    rng = np.random.default_rng(semilla)
    for _ in range(chispas):
        ang = math.radians(rng.uniform(-175, -5))
        v = rng.uniform(650, 1350) * s
        vida = rng.uniform(0.28, 0.55)
        if edad > vida:
            continue
        g = 2600 * s

        def pos(e):
            return (x + math.cos(ang) * v * e, y + math.sin(ang) * v * e * 0.7 + 0.5 * g * e * e)
        p1, p0 = pos(edad), pos(max(0.0, edad - 0.03))
        p0 = pos(max(0.0, edad - 0.05))
        linea(L, [p0, p1], ancho=max(2.0, (9 - 6 * edad / vida) * s), capa="energia", alpha=1 - (edad / vida) ** 2, cam=cam)


def nube_polvo(L, x, y, edad, ancho=200, n=14, semilla=5, color=(150, 128, 108), dur=1.1, alpha=0.55, cam=True):
    """Penacho de polvo que se abre y sube desde (x, y)."""
    if edad < 0 or edad > dur:
        return
    rng = np.random.default_rng(semilla)
    p = ease_entrada(edad / dur)
    for _ in range(n):
        dx, alto, r0 = rng.uniform(-1, 1), rng.uniform(0.2, 1.0), rng.uniform(0.25, 0.6)
        px = x + dx * ancho * (0.3 + 0.9 * p)
        py = y - alto * ancho * 0.55 * p - 6
        r = ancho * r0 * (0.35 + 0.8 * p)
        circulo(L, px, py, r, color, alpha=alpha * (1 - edad / dur) * 0.5, cam=cam)


# ------------------------------------------------------------------ HUD
def pildora_energia(L, s, cx, cy, tam=44, alpha=1.0, pop=1.0, cam=False):
    """Píldora llena del color de energía con la letra calada (se ve oscura): '×250'."""
    if alpha <= 0.003:
        return
    w = medir(s, tam, "black") + tam * 0.9
    h = tam * 1.25
    w, h = w * pop, h * pop
    m, d = L.temporal()
    X0, Y0 = L.P(cx - w / 2, cy - h / 2, cam)
    X1, Y1 = L.P(cx + w / 2, cy + h / 2, cam)
    d.rounded_rectangle([X0, Y0, X1, Y1], radius=(Y1 - Y0) / 2, fill=255)
    L.fundir(m, alpha=alpha, capa="energia")
    # la letra oscura va DESPUÉS del brillo (si se cala, el brillo la lava)
    X, Y = L.P(cx, cy + CAP * tam * pop / 2, cam)
    f1, oscuro = fuente(tam * pop * L.S(1, cam) / L.ss, "black"), rgb(L.e["fondo"])

    def letra(img, X=X / L.ss, Y=Y / L.ss, a=int(255 * alpha)):
        if a >= 1:
            ImageDraw.Draw(img, "RGBA").text((X, Y), s, font=f1, fill=oscuro + (a,), anchor="ms")
    L.post.insert(0, letra)


def numero_heroe(L, num, unidad, x, y, tam, t, t0, alin="izq", alpha=1.0, dur=0.32, cam=False):
    """Número protagonista (14–18 % del alto): cifra enorme en color de energía con brillo y la unidad al 50 %.
    Entra con un pop (escala 1,18 → 1). (x, y) = línea base. Devuelve el ancho."""
    if t < t0 or alpha <= 0.003:
        return 0
    p = ease_entrada(tramo(t, t0, dur))
    sc = 1.18 - 0.18 * p
    a = min(1.0, p * 2.2) * alpha
    if a < 0.004:                        # PIL dibuja opaco el texto con alfa 0
        return 0
    fn, fu = fuente(L.S(tam * sc, cam), "black"), fuente(L.S(tam * 0.5 * sc, cam), "black")
    wn, wu, esp = fn.getlength(num), fu.getlength(unidad), L.S(tam * 0.08 * sc, cam)
    total = wn + (esp + wu if unidad else 0)
    X, Y = L.P(x, y, cam)
    if alin == "der":
        X -= total
    elif alin == "centro":
        X -= total / 2
    # sombra corta para separarlo del fondo
    L.d.text((X + L.S(6, cam), Y + L.S(10, cam)), num, font=fn, fill=(0, 0, 0, int(120 * a)), anchor="ls")
    L.den.text((X, Y), num, font=fn, fill=int(255 * a), anchor="ls")
    if unidad:
        L.den.text((X + wn + esp, Y), unidad, font=fu, fill=int(255 * a), anchor="ls")
    return total / L.S(1, cam)


def inset(L, caja, t, t0, t1=None, contenido=None, insignia=None, titulo=None, cam=False):
    """Tarjeta redondeada (arriba a la derecha) con borde que brilla, para mostrar el dato con un objeto real.
    contenido(L, (x0, y0, x1, y1), alpha) dibuja adentro; insignia = texto de la píldora (p. ej. '×250')."""
    if t < t0:
        return
    p = ease_entrada(tramo(t, t0, 0.35))
    a = min(1.0, p * 1.8)
    if t1 is not None and t >= t1:
        a *= 1 - ease_salida(tramo(t, t1, 0.3))
    if a <= 0.003:
        return
    x0, y0, x1, y1 = caja
    sc = 0.9 + 0.1 * p
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    b = [cx + (x0 - cx) * sc, cy + (y0 - cy) * sc, cx + (x1 - cx) * sc, cy + (y1 - cy) * sc]
    rad = L.S(30, cam)
    P0, P1 = L.P(b[0], b[1], cam), L.P(b[2], b[3], cam)
    L.d.rounded_rectangle([P0[0] + L.S(8), P0[1] + L.S(14), P1[0] + L.S(8), P1[1] + L.S(14)], radius=rad,
                          fill=(0, 0, 0, int(110 * a)))
    L.d.rounded_rectangle([P0, P1], radius=rad, fill=(15, 17, 24, int(238 * a)))
    if contenido is not None and p > 0.3:
        contenido(L, tuple(b), a)
    m, d = L.temporal()
    d.rounded_rectangle([P0, P1], radius=rad, outline=255, width=int(round(L.S(4, cam))))
    L.fundir(m, alpha=a * 0.95, capa="energia")
    if titulo:
        texto(L, b[2] - 24, b[1] + 52, titulo, 30, rgb(L.e["gris"]), "xbold", anchor="rs", alpha=a, cam=cam)
    if insignia:
        pildora_energia(L, insignia, b[0] + 82, b[1] + 6, 46, alpha=a, pop=0.8 + 0.2 * ease_entrada(tramo(t, t0 + 0.15, 0.25)), cam=cam)


def regla(L, x, y0, y1, p, marcas, ancho=34, alpha=1.0, tam_txt=19, cam=False):
    """Cinta métrica que crece de y0 a y1 (p∈[0,1]) en el color de energía, con rayas y números calados.
    marcas = [(fracción, largo_raya, texto o None), ...]."""
    if p <= 0.002 or alpha <= 0.003:
        return
    yt = y0 + (y1 - y0) * p
    m, d = L.temporal()
    A, B = L.P(x - ancho / 2, min(yt, y0), cam), L.P(x + ancho / 2, max(yt, y0), cam)
    d.rounded_rectangle([A, B], radius=L.S(4, cam), fill=255)
    f = fuente(L.S(tam_txt, cam), "black")
    for fr, largo, txt in marcas:
        if fr > p + 1e-6:
            continue
        yy = y0 + (y1 - y0) * fr
        a, b = L.P(x - ancho / 2, yy, cam), L.P(x - ancho / 2 + largo, yy, cam)
        d.line([a, b], fill=0, width=max(1, int(round(L.S(2.2, cam)))))
        if txt:
            X, Y = L.P(x + ancho / 2 - 4, yy + tam_txt * CAP / 2 + (tam_txt * 0.9 if fr < 0.02 else 0), cam)
            d.text((X, Y), txt, font=f, fill=0, anchor="rs")
    # el gancho de la punta
    a, b = L.P(x - ancho / 2 - 6, yt - 5, cam), L.P(x + ancho / 2 + 6, yt + 5, cam)
    d.rectangle([a, b], fill=255)
    L.fundir(m, alpha=alpha, capa="energia")


def elefante(L, x, y, h, capa="base", color=(255, 255, 255), alpha=1.0, cam=False):
    """Pictograma de elefante de perfil (mirando a la derecha). (x, y) = abajo a la izquierda; h = alto."""
    m, d = L.temporal()
    E = lambda u, v: (x + u * h, y - v * h)
    poligono(L, elipse_pts(*E(0.52, 0.6), 0.46 * h, 0.31 * h, n=40), capa=d, cam=cam)
    for lx in (0.14, 0.32, 0.6, 0.78):
        poligono(L, [E(lx, 0.45), E(lx + 0.15, 0.45), E(lx + 0.14, 0.0), E(lx + 0.01, 0.0)], capa=d, cam=cam)
    poligono(L, elipse_pts(*E(1.0, 0.74), 0.22 * h, 0.21 * h, n=32), capa=d, cam=cam)
    linea(L, [E(1.14, 0.66), E(1.24, 0.42), E(1.22, 0.16), E(1.27, 0.08)], ancho=0.1 * h, capa=d, cam=cam)
    linea(L, [E(0.07, 0.68), E(0.0, 0.42)], ancho=0.035 * h, capa=d, cam=cam)
    linea(L, elipse_pts(*E(0.86, 0.72), 0.13 * h, 0.19 * h, 90, 270, 16), ancho=0.035 * h, capa=d, alpha=0, cam=cam)
    circulo(L, *E(1.07, 0.8), 0.025 * h, capa=d, alpha=0, cam=cam)
    linea(L, [E(1.12, 0.6), E(1.2, 0.56)], ancho=0.03 * h, capa=d, alpha=0, cam=cam)
    L.fundir(m, color, alpha, capa)


def pictogramas(L, x, y, n, h, t, t0, paso=0.08, cols=5, forma=elefante, cam=False):
    """Fila de pictogramas que se llenan uno a uno (los vacíos se ven tenues): el peso contado en elefantes."""
    gx, gy = h * 1.42, h * 1.18
    gris = rgb(L.e["gris"])
    for i in range(n):
        px, py = x + (i % cols) * gx, y + (i // cols) * gy
        te = t0 + i * paso
        if t < te:
            forma(L, px, py, h, "base", gris, 0.22, cam=cam)
        else:
            p = ease_entrada(tramo(t, te, 0.22))
            hh = h * (0.7 + 0.3 * p)
            forma(L, px + (h - hh) * 0.6, py, hh, "energia", alpha=min(1, p * 1.6), cam=cam)


def x_roja(L, cx, cy, tam, p, cam=False):
    """✗ de 'esto no sirve' (rojo: el único uso del color de peligro). Entra con un pop."""
    if p <= 0:
        return
    s = tam * (1.3 - 0.3 * ease_entrada(p)) / 2
    a = min(1, p * 2)
    roja = rgb(L.e["peligro"])
    for c, w in (((12, 10, 12), 0.34), (roja, 0.22)):
        linea(L, [(cx - s, cy - s), (cx + s, cy + s)], c, tam * w, alpha=a, cam=cam)
        linea(L, [(cx + s, cy - s), (cx - s, cy + s)], c, tam * w, alpha=a, cam=cam)


# ------------------------------------------------------------------ objetos 3D livianos
CROMO = [(-1.0, (30, 30, 34)), (-0.9, (92, 86, 80)), (-0.74, (186, 172, 156)), (-0.66, (255, 248, 236)),
         (-0.56, (255, 248, 236)), (-0.5, (156, 146, 136)), (-0.34, (208, 200, 190)), (-0.2, (122, 122, 128)),
         (0.02, (54, 58, 66)), (0.3, (34, 38, 46)), (0.52, (68, 78, 96)), (0.68, (140, 168, 206)),
         (0.74, (214, 232, 255)), (0.81, (214, 232, 255)), (0.88, (104, 124, 156)), (1.0, (24, 28, 38))]
_CR_U = np.array([c[0] for c in CROMO], np.float32)
_CR_C = np.array([c[1] for c in CROMO], np.float32)


# cromo "foto de producto" al atardecer: borde cálido del lado del sol, franja especular dura, brillo secundario
# suave, núcleo oscuro y relleno frío del cielo a la derecha
CROMO_ATARDECER = [(-1.0, (255, 150, 80)), (-0.93, (196, 104, 64)), (-0.84, (70, 52, 50)), (-0.7, (150, 132, 124)),
                   (-0.63, (255, 252, 244)), (-0.53, (255, 252, 244)), (-0.46, (126, 112, 112)), (-0.3, (176, 170, 176)),
                   (-0.12, (200, 196, 204)), (0.06, (84, 84, 96)), (0.3, (30, 32, 42)), (0.55, (56, 72, 104)),
                   (0.78, (132, 162, 208)), (0.9, (176, 204, 240)), (1.0, (44, 56, 84))]


def cromo(u, brillo=1.0, stops=None):
    """Color del acero cromado según la posición u∈[-1,1] a lo ancho del cilindro: 2–3 brillos duros (cálido a la
    izquierda, frío a la derecha) y un núcleo oscuro. stops=CROMO_ATARDECER para los planos de exterior."""
    if stops is not None:
        su = np.array([c[0] for c in stops], np.float32)
        sc = np.array([c[1] for c in stops], np.float32)
        return tuple(int(clamp(float(np.interp(u, su, sc[:, k])) * brillo, 0, 255)) for k in range(3))
    c = [float(np.interp(u, _CR_U, _CR_C[:, k])) * brillo for k in range(3)]
    return tuple(int(clamp(v, 0, 255)) for v in c)


def clavo3d(L, pr, X, Y, largo, z0=0.0, recorte=None, cam=True, estrias=True, semilla=7, ns=56, stops=None):
    """Clavo de acero cromado de verdad, para cualquier proyector pr(X, Y, Z) (oblicuo o cámara 3D):
    caña con bandas de cromo y estrías de acero cepillado, punta de diamante facetada, cabeza plana con bisel.
    La punta toca Z=z0 y la tapa queda en Z=z0+largo. recorte = Z mínima visible."""
    N = largo
    R, Rh, hr, pt = 0.0275 * N, 0.07 * N, 0.03 * N, 0.075 * N
    zt, zs1, zh0, zh1 = z0, z0 + pt, z0 + N - hr, z0 + N
    zc = -1e18 if recorte is None else recorte
    ancho_px = abs(pr(X + Rh, Y, z0 + N)[0] - pr(X - Rh, Y, z0 + N)[0])
    ns = int(clamp(ancho_px / 3, ns, 200))          # bandas finas en primeros planos (sin escalones)
    us = np.linspace(-1, 1, ns + 1)

    def cil(u, r, z):
        return pr(X + u * r, Y - math.sqrt(max(0.0, 1 - u * u)) * r, z)

    def bandas(r0, r1, za, zb, color_de):
        for i in range(ns):
            u0, u1 = us[i], us[i + 1]
            poligono(L, [cil(u0, r0, za), cil(u1, r0, za), cil(u1, r1, zb), cil(u0, r1, zb)], color_de((u0 + u1) / 2), cam=cam)

    arriba = pr(X, Y - Rh, zh1)[1] > pr(X, Y + Rh, zh1)[1]

    def cana():
        za = max(zs1, zc)
        if za < zh0:
            bandas(R, R, za, zh0, lambda u: cromo(u, 1.0, stops))
            if estrias:
                rng = np.random.default_rng(semilla)
                for _ in range(22):
                    u = rng.uniform(-0.92, 0.92)
                    w = max(0.6, abs(pr(X + R, Y, za)[0] - pr(X - R, Y, za)[0]) * 0.012)
                    claro = rng.uniform() < 0.5
                    linea(L, [cil(u, R, za), cil(u, R, zh0)], (255, 255, 255) if claro else (0, 0, 0), w,
                          alpha=rng.uniform(0.06, 0.16), cam=cam, puntas=False)
            # sombra de la cabeza sobre la caña
            zsom = max(za, zh0 - 0.07 * N)
            for k in range(12):
                z1 = zh0 - (zh0 - zsom) * k / 12
                poligono(L, [cil(-1, R, zsom), cil(1, R, zsom), cil(1, R, z1), cil(-1, R, z1)], (0, 0, 0), alpha=0.05, cam=cam)

    def punta():
        if zc >= zs1:
            return
        za = max(zt, zc)
        ra = R * (za - zt) / pt

        def cara(u):
            if u < -0.04:
                return mezcla((222, 210, 194), (150, 140, 132), (u + 1) * 0.6)
            if u < 0.04:
                return (255, 250, 240)
            if u > 0.82:
                return (150, 178, 214)
            return mezcla((88, 96, 110), (52, 58, 70), u)
        bandas(ra, R, za, zs1, cara)

    def cabeza():
        bandas(Rh, Rh, zh0, zh1, lambda u: cromo(u, 1.08, stops))
        if arriba:
            tapa = [pr(X + Rh * math.cos(a), Y + Rh * math.sin(a), zh1) for a in np.linspace(0, 2 * math.pi, 72)]
            relleno_gradiente(L, tapa, [(0, (246, 238, 226)), (0.35, (198, 196, 196)), (0.62, (110, 116, 128)),
                                        (1, (70, 78, 92))], pr(X - Rh, Y + Rh, zh1), pr(X + Rh, Y - Rh, zh1), cam=cam)
            bis = [pr(X + Rh * 0.86 * math.cos(a), Y + Rh * 0.86 * math.sin(a), zh1) for a in np.linspace(0.15, math.pi - 0.15, 36)]
            linea(L, bis, (255, 255, 255), max(1.0, abs(tapa[0][0] - tapa[36][0]) * 0.012), alpha=0.55, cam=cam)
            linea(L, tapa, (40, 42, 50), max(0.8, abs(tapa[0][0] - tapa[36][0]) * 0.008), alpha=0.7, cam=cam)
        else:
            base = [pr(X + Rh * math.cos(a), Y + Rh * math.sin(a), zh0) for a in np.linspace(0, 2 * math.pi, 72)]
            relleno_gradiente(L, base, [(0, (70, 64, 62)), (0.5, (36, 38, 46)), (1, (92, 116, 150))],
                              pr(X - Rh, Y, zh0), pr(X + Rh, Y, zh0), cam=cam)

    if arriba:
        cana(), punta(), cabeza()
    else:
        cabeza(), cana(), punta()
    return dict(R=R, Rh=Rh, hr=hr, punta=pt, z_tapa=zh1, z_base_cabeza=zh0)


def tabla_testa(L, x0, x1, yf, alto, prof=46, semilla=5, cam=True):
    """Tablón de madera: cara de arriba con veta larga y frente en TESTA (corte transversal: anillos de crecimiento
    y grietas radiales). yf = borde delantero de la cara de arriba."""
    rng = np.random.default_rng(semilla)
    ins = 26
    sup = [(x0, yf), (x1, yf), (x1 - ins, yf - prof), (x0 + ins, yf - prof)]
    relleno_gradiente(L, sup, [(0, (150, 102, 60)), (1, (226, 172, 108))], (0, yf - prof), (0, yf), cam=cam)
    for f_ in (0.2, 0.42, 0.62, 0.82):
        y = yf - prof * (1 - f_)
        xa, xb = x0 + ins * (1 - f_), x1 - ins * (1 - f_)
        linea(L, [(x, y + 1.4 * math.sin(x / 41 + f_ * 7)) for x in np.linspace(xa + 6, xb - 6, 40)], (150, 98, 54), 1.6, alpha=0.5, cam=cam)
    fr = [(x0, yf), (x1, yf), (x1, yf + alto), (x0, yf + alto)]
    relleno_gradiente(L, fr, [(0, (184, 124, 70)), (0.6, (150, 98, 54)), (1, (96, 62, 34))], (0, yf), (0, yf + alto), cam=cam)
    # anillos: la médula queda abajo, fuera del cuadro
    mx, my = x0 + (x1 - x0) * 0.42, yf + alto + 260
    for i in range(1, 46):
        r = 290 + i * 15 + rng.uniform(-3, 3)
        pts = [p for p in elipse_pts(mx, my, r * 1.05, r, 180, 360, 90) if yf + 2 < p[1] < yf + alto and x0 < p[0] < x1]
        if len(pts) > 2:
            linea(L, pts, (112, 70, 36) if i % 3 else (88, 54, 28), 1.4 + (i % 4 == 0) * 1.6, alpha=0.55, cam=cam, puntas=False)
    for ang, l in ((-62, 120), (-105, 90), (-140, 70)):
        a = math.radians(ang)
        r0 = math.hypot(mx - mx, (my - yf - alto)) + 10
        pa = (mx + math.cos(a) * r0, my + math.sin(a) * r0)
        pb = (mx + math.cos(a) * (r0 + l), my + math.sin(a) * (r0 + l))
        if yf < pa[1] < yf + alto and yf < pb[1]:
            linea(L, [pa, pb], (60, 36, 18), 3, alpha=0.7, cam=cam)
    linea(L, [(x0, yf), (x1, yf)], (250, 214, 160), 3, cam=cam)
    relleno_gradiente(L, [(x1 - 18, yf), (x1, yf), (x1, yf + alto), (x1 - 18, yf + alto)],
                      [(0, (150, 196, 255, 0)), (1, (150, 196, 255, 90))], (x1 - 18, 0), (x1, 0), cam=cam)


def madera_corte(L, x0, x1, ys, yb, cx, hundido, R, semilla=4, cam=True):
    """Tablón visto en CORTE de costado: fibras largas que el clavo arrastra hacia abajo (lo que ya entró) y
    comprime bajo la punta; astillas en la entrada. ys = superficie (borde del corte), hundido = px que entró."""
    rng = np.random.default_rng(semilla)
    pt = 24
    relleno_gradiente(L, [(x0, ys), (x1, ys), (x1, ys - pt), (x0, ys - pt)], [(0, (150, 102, 60)), (1, (226, 172, 108))],
                      (0, ys - pt), (0, ys), cam=cam)
    relleno_gradiente(L, [(x0, ys), (x1, ys), (x1, yb), (x0, yb)],
                      [(0, (222, 170, 108)), (0.35, (198, 142, 84)), (1, (140, 92, 50))], (0, ys), (0, yb), cam=cam)
    xs = np.linspace(x0, x1, 170)
    esp, i = 19, 0
    while True:
        dd = (i + 0.6) * esp + rng.uniform(-4, 4)
        i += 1
        base = ys + dd
        if base > yb + 20:
            break
        ond = rng.uniform(2, 6) * np.sin(xs / rng.uniform(180, 420) + rng.uniform(0, 6.3)) \
            + rng.uniform(0.5, 2) * np.sin(xs / rng.uniform(40, 90) + rng.uniform(0, 6.3))
        if hundido > 1 and dd < hundido:
            k = 22 * (1 - dd / hundido) ** 0.5 * min(1, hundido / 140)
            dy = k * np.exp(-((xs - cx) / (R * 2.8)) ** 2)
        elif hundido > 1:
            k = 14 * math.exp(-(dd - hundido) / 46) * min(1, hundido / 120)
            dy = k * np.exp(-((xs - cx) / (R * 2.2)) ** 2)
        else:
            dy = 0
        yl = base + ond + dy
        oscuro = i % 3 != 0
        linea(L, list(zip(xs, yl)), (138, 88, 46) if oscuro else (236, 190, 130), rng.uniform(1.4, 3.2),
              alpha=rng.uniform(0.35, 0.7) if oscuro else 0.4, cam=cam, puntas=False)
    for k in range(4):                      # bandas anchas de crecimiento
        yy = ys + 60 + k * 150
        relleno_gradiente(L, [(x0, yy), (x1, yy), (x1, yy + 60), (x0, yy + 60)],
                          [(0, (90, 50, 20, 0)), (0.5, (90, 50, 20, 34)), (1, (90, 50, 20, 0))], (0, yy), (0, yy + 60), cam=cam)
    if hundido > 1:
        for s in (-1, 1):                   # el hueco que abre la caña
            linea(L, [(cx + s * (R + 2), ys), (cx + s * (R + 2), ys + hundido)], (52, 30, 14), 4, alpha=0.6, cam=cam)
        a = min(1.0, hundido / 60)
        for j, (dx, h, inc) in enumerate(((8, 26, -0.5), (20, 16, -0.9), (34, 12, -0.4), (12, 20, 0.6), (27, 14, 0.9))):
            for s in (-1, 1):
                xb = cx + s * (R + dx)
                pts = [(xb - 5, ys), (xb + 5, ys), (xb + s * inc * h * 0.6, ys - h * a)]
                poligono(L, pts, (236, 192, 132) if j % 2 else (196, 140, 80), cam=cam)
    linea(L, [(x0, ys), (x1, ys)], (250, 214, 160), 3, cam=cam)


@lru_cache(maxsize=4)
def _ciudad(semilla):
    """Geometría fija de la ciudad (no depende de la cámara: nada titila cuando la cámara se mueve)."""
    rng = np.random.default_rng(semilla)
    capas = []
    for yb, a, k_bruma, alto_x in ((620.0, 0.55, 0.62, 1.5), (330.0, 0.7, 0.4, 1.15), (170.0, 0.85, 0.2, 0.9)):
        edif, X = [], -420.0
        while X < 420:
            w, alto = rng.uniform(12, 34), rng.uniform(10, 44) * alto_x
            ventanas = [(X + rng.uniform(1, w - 1), rng.uniform(2, alto - 2)) for _ in range(int(w * alto / 40))]
            ventanas = [v for v in ventanas if rng.uniform() < 0.5]
            edif.append((X, w, alto, ventanas))
            X += w + rng.uniform(1, 8)
        capas.append((yb, a, k_bruma, edif))
    return capas


def edificios3d(L, cam3, semilla=9, alpha=0.6, cam=True):
    """Ciudad en 3 capas (parallax real con la cámara 3D): la más lejana casi disuelta en la bruma cálida del
    horizonte, la del medio más oscura, y un edificio de 6 pisos (≈19 m) cerca, con ventanas encendidas."""
    bruma = (236, 150, 110)
    for yb, a, k_bruma, edif in _ciudad(semilla):
        col = mezcla((24, 26, 52), bruma, k_bruma)
        cv = mezcla((255, 200, 120), bruma, k_bruma * 0.6)
        for X, w, alto, ventanas in edif:
            pts = [cam3.pr(X, yb, 0), cam3.pr(X + w, yb, 0), cam3.pr(X + w, yb, alto), cam3.pr(X, yb, alto)]
            if pts[1][0] < -60 or pts[0][0] > 1140:
                continue
            poligono(L, pts, col, alpha=a * alpha / 0.6, cam=cam)
            sz = max(0.7, cam3.escala(X, yb, 0) * 0.7)
            for wx, wz in ventanas:
                q = cam3.pr(wx, yb, wz)
                poligono(L, [(q[0] - sz, q[1] - sz), (q[0] + sz, q[1] - sz), (q[0] + sz, q[1] + sz), (q[0] - sz, q[1] + sz)],
                         cv, alpha=(0.75 - k_bruma * 0.6) * alpha / 0.6, cam=cam)
    X0, X1, Yb, Hb = 7.0, 23.0, 90.0, 19.0
    cuerpo = [cam3.pr(X0, Yb, 0), cam3.pr(X1, Yb, 0), cam3.pr(X1, Yb, Hb), cam3.pr(X0, Yb, Hb)]
    relleno_gradiente(L, cuerpo, [(0, (92, 62, 70)), (0.5, (44, 40, 64)), (1, (28, 30, 52))], cam3.pr(X0, Yb, Hb), cam3.pr(X1, Yb, 0), alpha=alpha, cam=cam)
    for piso in range(6):
        for col in range(7):
            wx, wz = X0 + 1.2 + col * 2.1, 1.2 + piso * 3.0
            q = [cam3.pr(wx, Yb, wz), cam3.pr(wx + 1.2, Yb, wz), cam3.pr(wx + 1.2, Yb, wz + 1.6), cam3.pr(wx, Yb, wz + 1.6)]
            encendida = (piso * 7 + col * 3 + semilla) % 5 < 2
            poligono(L, q, (255, 204, 130) if encendida else (22, 24, 40), alpha=(0.85 if encendida else 0.6) * alpha / 0.6, cam=cam)
    linea(L, [cam3.pr(X0, Yb, Hb), cam3.pr(X0, Yb, 0)], (255, 170, 110), 2, alpha=0.5 * alpha / 0.6, cam=cam)
    borde_frio(L, [cam3.pr(X1, Yb, 0), cam3.pr(X1, Yb, Hb)], 2, alpha=0.4 * alpha / 0.6, cam=cam)


def suelo3d(L, cam3, semilla=2, cam=True, y_max=None):
    """Plano de suelo de tierra oscura que se pierde en la bruma del horizonte, con piedritas."""
    yc = cam3.Y
    pts = [cam3.pr(-3000, yc + 2.0, 0), cam3.pr(3000, yc + 2.0, 0), cam3.pr(3000, 3000, 0), cam3.pr(-3000, 3000, 0)]
    hz = cam3.horizonte()
    relleno_gradiente(L, pts, [(0, (150, 100, 72)), (0.05, (78, 58, 48)), (0.3, (46, 38, 34)), (1, (28, 24, 24))],
                      (0, hz), (0, hz + 700), cam=cam)
    rng = np.random.default_rng(semilla)
    for _ in range(140):
        X, Y = rng.uniform(-60, 60), rng.uniform(yc + 6, 220)
        r = rng.uniform(0.08, 0.35)
        p = cam3.pr(X, Y, 0)
        s = cam3.escala(X, Y, 0)
        if s * r < 0.7 or not (-50 < p[0] < 1130 and p[1] < 2000):
            continue
        poligono(L, elipse_pts(p[0], p[1] - s * r * 0.15, s * r, s * r * 0.35, n=14), (98, 78, 64), alpha=0.8, cam=cam)
        poligono(L, elipse_pts(p[0] - s * r * 0.2, p[1] - s * r * 0.28, s * r * 0.5, s * r * 0.14, n=10), (190, 150, 110), alpha=0.5, cam=cam)


def bus3d(L, pr, X0, Y0, largo=10.2, alto=4.4, cam=True):
    """Bus de dos pisos de perfil (mirando a la derecha) como cartel en 3D: rojo, ventanas con luz, ruedas,
    luz clave cálida arriba a la izquierda y borde frío a la derecha. (X0, Y0) = esquina trasera en el suelo."""
    M = lambda x, z: pr(X0 + x, Y0, z)
    P = lambda pts: [M(x, z) for x, z in pts]
    # sombra de contacto
    a, b = M(-0.3, 0), M(largo + 0.3, 0)
    sombra_contacto(L, (a[0] + b[0]) / 2, a[1], abs(b[0] - a[0]) * 0.56, max(3, abs(b[0] - a[0]) * 0.045), 0.75, cam=cam)
    cuerpo = [(0.15, 0.32), (largo - 0.1, 0.32), (largo, 0.7), (largo, alto - 0.45), (largo - 0.3, alto - 0.08), (largo - 0.8, alto),
              (0.6, alto), (0.15, alto - 0.3), (0.0, alto - 0.9), (0.0, 0.6)]
    relleno_gradiente(L, P(cuerpo), [(0, (236, 96, 74)), (0.45, (186, 40, 38)), (1, (112, 22, 26))], M(0, alto), M(0.8, 0.3), cam=cam)
    linea(L, P([(0.6, alto), (largo - 0.8, alto)]), (255, 200, 170), 2.2, alpha=0.8, cam=cam)
    for z0, z1 in ((2.85, 3.95), (1.05, 2.2)):        # ventanas de los dos pisos
        x = 0.45
        while x + 1.0 < largo - 1.4:
            q = P([(x, z0), (x + 1.0, z0), (x + 1.0, z1), (x, z1)])
            poligono(L, q, (22, 28, 40), cam=cam)
            if int(x * 7) % 3:
                poligono(L, q, (255, 196, 124), alpha=0.32, cam=cam)
            poligono(L, P([(x + 0.15, z1 - 0.1), (x + 0.45, z1 - 0.1), (x + 0.2, z0 + 0.15), (x + 0.05, z0 + 0.15)]), (255, 255, 255), alpha=0.12, cam=cam)
            x += 1.15
    poligono(L, P([(largo - 1.25, 2.85), (largo - 0.08, 2.85), (largo - 0.08, 3.95), (largo - 1.25, 3.95)]), (30, 40, 56), cam=cam)
    poligono(L, P([(largo - 1.25, 1.05), (largo - 0.08, 1.05), (largo - 0.08, 2.3), (largo - 1.25, 2.3)]), (30, 40, 56), cam=cam)
    poligono(L, P([(largo - 2.5, 0.45), (largo - 1.5, 0.45), (largo - 1.5, 2.3), (largo - 2.5, 2.3)]), (40, 46, 60), cam=cam)
    poligono(L, P([(0.0, 2.35), (largo, 2.35), (largo, 2.55), (0.0, 2.55)]), (236, 220, 186), cam=cam)
    poligono(L, P([(largo - 1.15, 4.0), (largo - 0.15, 4.0), (largo - 0.15, 4.28), (largo - 1.15, 4.28)]), (14, 14, 16), cam=cam)
    poligono(L, P([(largo - 1.05, 4.08), (largo - 0.3, 4.08), (largo - 0.3, 4.2), (largo - 1.05, 4.2)]), (255, 170, 60), alpha=0.9, cam=cam)
    poligono(L, P([(largo - 0.12, 0.8), (largo + 0.02, 0.8), (largo + 0.02, 1.0), (largo - 0.12, 1.0)]), (255, 236, 190), cam=cam)
    for xr in (1.9, largo - 3.1):
        c = M(xr, 0.55)
        r = abs(M(xr + 0.55, 0.55)[0] - c[0])
        poligono(L, elipse_pts(c[0], c[1], r * 1.18, r * 1.18, 180, 360, 24), (60, 16, 18), cam=cam)
        poligono(L, elipse_pts(c[0], c[1], r, r, n=30), (20, 20, 24), cam=cam)
        poligono(L, elipse_pts(c[0], c[1], r * 0.5, r * 0.5, n=20), (150, 150, 160), cam=cam)
        poligono(L, elipse_pts(c[0] - r * 0.12, c[1] - r * 0.12, r * 0.2, r * 0.2, n=12), (230, 230, 236), alpha=0.7, cam=cam)
    borde_frio(L, P([(largo, 0.7), (largo, alto - 0.45), (largo - 0.3, alto - 0.08)]), 2.2, cam=cam)


def persona_espalda(L, pr, X, Y, alto=1.75, mira_arriba=1.0, cam=True):
    """Persona de espaldas mirando hacia arriba (cartel en 3D): ropa oscura, luz de borde fría del cielo,
    toque cálido de la luz clave en el hombro izquierdo."""
    k = alto / 1.75
    M = lambda u, z: pr(X + u * k, Y, z * k)
    P = lambda pts: [M(u, z) for u, z in pts]
    a, b = M(-0.4, 0), M(0.4, 0)
    sombra_contacto(L, (a[0] + b[0]) / 2, a[1], abs(b[0] - a[0]) * 0.7, max(2, abs(b[0] - a[0]) * 0.12), 0.6, cam=cam)
    ancho = lambda u0, z0, u1, z1, w: [M(u0 - w, z0), M(u0 + w, z0), M(u1 + w, z1), M(u1 - w, z1)]
    jean, chaqueta, pelo = (34, 40, 56), (52, 58, 76), (26, 22, 24)
    for s in (-1, 1):
        poligono(L, ancho(0.1 * s, 0.95, 0.12 * s, 0.06, 0.075), jean, cam=cam)
        poligono(L, P([(0.12 * s - 0.09, 0.0), (0.12 * s + 0.09, 0.0), (0.12 * s + 0.08, 0.08), (0.12 * s - 0.08, 0.08)]), (18, 18, 22), cam=cam)
    torso = P([(-0.24, 1.44), (0.24, 1.44), (0.21, 0.88), (-0.21, 0.88)])
    relleno_gradiente(L, torso, [(0, (92, 88, 96)), (0.4, chaqueta), (1, (30, 34, 48))], M(-0.24, 1.44), M(0.24, 0.9), cam=cam)
    for s in (-1, 1):
        poligono(L, ancho(0.25 * s, 1.4, 0.29 * s, 0.86, 0.06), chaqueta if s < 0 else (40, 46, 62), cam=cam)
        circulo(L, *M(0.29 * s, 0.84), abs(M(0.05, 0)[0] - M(0, 0)[0]), (150, 112, 90), cam=cam)
    poligono(L, P([(-0.06, 1.42), (0.06, 1.42), (0.055, 1.52), (-0.055, 1.52)]), (120, 86, 70), cam=cam)
    hc = M(0, 1.62 - 0.02 * mira_arriba)
    rx = abs(M(0.105, 0)[0] - M(0, 0)[0])
    ry = abs(M(0, 0.12)[1] - M(0, 0)[1])
    poligono(L, elipse_pts(hc[0], hc[1], rx, ry, n=36), pelo, cam=cam)
    for s in (-1, 1):
        poligono(L, elipse_pts(hc[0] + s * rx * 0.98, hc[1] + ry * 0.12, rx * 0.16, ry * 0.24, n=12), (130, 92, 76), cam=cam)
    linea(L, elipse_pts(hc[0], hc[1], rx, ry, -80, 20, 16), FRIO, max(1.5, rx * 0.14), alpha=0.95, cam=cam)
    linea(L, elipse_pts(hc[0], hc[1], rx, ry, 160, 250, 12), (255, 170, 100), max(1.5, rx * 0.12), alpha=0.9, cam=cam)
    borde_frio(L, P([(0.24, 1.44), (0.21, 0.9)]), max(1.5, rx * 0.1), alpha=0.95, cam=cam)
    linea(L, P([(-0.24, 1.43), (-0.21, 0.9)]), (255, 170, 100), max(1.5, rx * 0.1), alpha=0.85, cam=cam)
    for s_ in (-1, 1):
        linea(L, P([(0.1 * s_ + 0.07 * s_, 0.92), (0.12 * s_ + 0.07 * s_, 0.08)]), FRIO if s_ > 0 else (255, 170, 100),
              max(1.2, rx * 0.08), alpha=0.8, cam=cam)
    linea(L, P([(-0.24, 1.43), (-0.06, 1.47)]), CALIDO, max(1.0, rx * 0.06), alpha=0.7, cam=cam)


def mano_pinza(L, x, y, s=1.0, alpha=1.0, cam=False, nail=None):
    """Mano que sostiene algo entre el pulgar y el índice (entra desde la derecha). (x, y) = punto de la pinza.
    nail(): función que dibuja el objeto sostenido entre el índice (atrás) y el pulgar (adelante)."""
    piel, sombra, luz = (226, 172, 132), (178, 120, 86), (248, 210, 172)
    Q = lambda u, v: (x + u * s, y + v * s)
    linea(L, [Q(126, -50), Q(70, -40), Q(14, -26)], sombra, 30 * s, alpha=alpha, cam=cam)
    linea(L, [Q(126, -52), Q(70, -42), Q(16, -29)], piel, 25 * s, alpha=alpha, cam=cam)
    linea(L, [Q(120, -60), Q(70, -50), Q(22, -37)], luz, 6 * s, alpha=0.8 * alpha, cam=cam)
    poligono(L, elipse_pts(*Q(20, -28), 8 * s, 6 * s, n=12, rot=-10), (250, 222, 204), alpha=0.8 * alpha, cam=cam)
    for u in (62, 82):
        linea(L, [Q(u, -52), Q(u + 3, -34)], sombra, 2.5 * s, alpha=0.5 * alpha, cam=cam)
    c = Q(146, 22)
    palma = elipse_pts(c[0], c[1], 64 * s, 80 * s, n=40, rot=-18)
    relleno_gradiente(L, palma, [(0, luz), (0.5, piel), (1, sombra)], Q(80, -60), Q(210, 110), alpha=alpha, cam=cam)
    for i, (a, b) in enumerate(((Q(134, 0), Q(92, 8)), (Q(138, 30), Q(98, 38)), (Q(134, 58), Q(102, 64)))):
        linea(L, [a, b], sombra, 23 * s, alpha=alpha, cam=cam)
        linea(L, [a, (b[0] + 2 * s, b[1] - 2 * s)], piel, 18 * s, alpha=alpha, cam=cam)
    if nail is not None:
        nail()
    linea(L, [Q(104, 70), Q(54, 40), Q(8, 6)], sombra, 31 * s, alpha=alpha, cam=cam)
    linea(L, [Q(104, 66), Q(54, 36), Q(10, 2)], luz, 25 * s, alpha=alpha, cam=cam)
    linea(L, [Q(96, 58), Q(52, 30), Q(14, -2)], (255, 236, 214), 6 * s, alpha=0.7 * alpha, cam=cam)
    linea(L, [Q(60, 46), Q(66, 38)], sombra, 3 * s, alpha=0.6 * alpha, cam=cam)
    poligono(L, elipse_pts(*Q(12, 0), 9 * s, 7 * s, n=14, rot=35), (250, 226, 210), alpha=0.8 * alpha, cam=cam)



# ==================================================================================================================
# v4 (23-nov-2026, ronda 2 contra virales): titular, pictogramas con pop, barrido, cota de persona, grietas, brillo
# ==================================================================================================================
def titular(L, s, y=300, tam=104, x_centro=490, alpha=1.0):
    """Titular de 2–4 palabras en píldora llena del color de energía con letra oscura (el gancho del cuadro 0)."""
    if alpha <= 0.003:
        return
    f = fuente(tam, "black")
    bb = f.getbbox(s, anchor="ls")
    w = bb[2] - bb[0]
    x = x_centro - w / 2 - bb[0]
    b = y + CAP * tam
    m, d = L.temporal()
    d.rounded_rectangle([L.P(x + bb[0] - 0.24 * tam, b - CAP * tam - 0.2 * tam, False),
                         L.P(x + bb[2] + 0.24 * tam, b + 0.2 * tam, False)], radius=L.S(0.2 * tam, False), fill=255)
    L.fundir(m, alpha=alpha, capa="energia")
    oscuro = rgb(L.e["fondo"])

    def letra(img, a=int(255 * alpha)):
        if a >= 1:
            ImageDraw.Draw(img, "RGBA").text((x, b), s, font=f, fill=oscuro + (a,), anchor="ls")
    L.post.append(letra)


def pictogramas_pop(L, x, y, n, h, t, t0, paso=2 / FPS, cols=5, forma=elefante, gx=None, gy=None, cam=False):
    """Pictogramas que aparecen uno a uno con pop (escala 0 → 1,1 → 1,0), brillantes en el color de energía.
    Devuelve cuántos ya aparecieron (para el contador)."""
    gx, gy = gx or h * 1.42, gy or h * 1.18
    k = 0
    for i in range(n):
        te = t0 + i * paso
        if t < te:
            continue
        k += 1
        p = tramo(t, te, 0.16)
        sc = 1.1 * ease_entrada(p / 0.6) if p < 0.6 else 1.1 - 0.1 * ease_estado((p - 0.6) / 0.4)
        hh = h * sc
        px, py = x + (i % cols) * gx, y + (i // cols) * gy
        if hh > 1:
            forma(L, px + (h - hh) * 0.64, py, hh, "energia", alpha=1.0, cam=cam)
    return k


def barrido(L, k, sentido=-1):
    """Transición 'whip pan': desenfoque de movimiento horizontal + corrimiento (k∈[0,1], 2–3 cuadros por corte).
    Se aplica al cuadro entero (llamar después de dibujar todo, subtítulos incluidos)."""
    if k <= 0.01:
        return

    def f(img, k=k):
        arr = np.asarray(img, np.float32)
        largo = int(20 + 110 * k)
        n = 9
        acc = np.zeros_like(arr)
        for i in range(n):
            acc += np.roll(arr, int(sentido * largo * i / (n - 1)), axis=1)
        acc /= n
        acc = np.roll(acc, int(sentido * 140 * k), axis=1)
        img.paste(Image.fromarray(np.clip(acc, 0, 255).astype(np.uint8), "RGB"))
    L.post.append(f)                     # al final: todo el cuadro se barre junto (píldora y letra no se separan)


def cota_persona(L, x_linea, y_pies, y_cabeza, texto_="1,8 M", lado="der", alpha=1.0):
    """Cota suelo → cabeza al lado de una persona, con la medida en letra grande (44 px, contorno)."""
    if alpha <= 0.003:
        return
    tinta = rgb(L.e["tinta"])
    m, d = L.temporal()
    linea(L, [(x_linea, y_pies), (x_linea, y_cabeza)], ancho=4, capa=d, cam=False)
    for yy in (y_pies, y_cabeza):
        linea(L, [(x_linea - 12, yy), (x_linea + 12, yy)], ancho=4, capa=d, cam=False)
    L.fundir(m, tinta, alpha)
    xm = x_linea + (18 if lado == "der" else -18)
    texto(L, xm, (y_pies + y_cabeza) / 2 + 16, texto_, 44, tinta, "black", anchor="ls" if lado == "der" else "rs",
          alpha=alpha, trazo=5)


def grietas_suelo(L, cam3, X=0.0, Y=0.0, p=1.0, n=9, largo=7.0, semilla=6, cam=True):
    """Grietas radiales y escombros en el suelo alrededor de la base de algo muy pesado (en el plano del suelo)."""
    if p <= 0:
        return
    rng = np.random.default_rng(semilla)
    for i in range(n):
        a = math.radians(rng.uniform(0, 360))
        pts, x, y = [cam3.pr(X + math.cos(a) * 0.7, Y + math.sin(a) * 0.7, 0)], X + math.cos(a) * 0.7, Y + math.sin(a) * 0.7
        for k in range(7):
            a += rng.uniform(-0.35, 0.35)
            paso = largo / 7 * p * rng.uniform(0.6, 1.3)
            x, y = x + math.cos(a) * paso, y + math.sin(a) * paso
            if y < cam3.Y + 3:
                break
            pts.append(cam3.pr(x, y, 0))
        if len(pts) > 1:
            linea(L, pts, (16, 12, 12), max(1.2, cam3.escala(X, Y, 0) * 0.06), alpha=0.85, cam=cam)
    for _ in range(16):
        a, r = rng.uniform(0, 6.283), rng.uniform(0.9, 3.2)
        x, y = X + math.cos(a) * r, Y + math.sin(a) * r
        if y < cam3.Y + 3:
            continue
        c, e = cam3.pr(x, y, 0), cam3.escala(x, y, 0)
        rr = e * rng.uniform(0.12, 0.3) * p
        poligono(L, [(c[0] - rr, c[1]), (c[0] - rr * 0.3, c[1] - rr * 0.8), (c[0] + rr, c[1] - rr * 0.3), (c[0] + rr * 0.7, c[1])],
                 (110, 82, 62), cam=cam)
        linea(L, [(c[0] - rr * 0.3, c[1] - rr * 0.8), (c[0] + rr, c[1] - rr * 0.3)], (220, 160, 110), max(1, rr * 0.2), alpha=0.7, cam=cam)


def brillo_suave(L, x, y, rx, ry, color=(255, 236, 210), alpha=0.35, radio=10, cam=True):
    """Mancha de luz (o de sombra, con color negro) desenfocada: bloom en la cabeza, sombra de contacto blanda."""
    with desenfoque(L, radio) as d:
        poligono(L, elipse_pts(x, y, rx, ry, n=48), color, capa=d, alpha=alpha, cam=cam)


def esquirlas(L, x, y, edad, n=10, color=(236, 196, 140), semilla=13, vel=900, dur=0.45, cam=True):
    """Astillas o escombros que salen disparados con desenfoque de movimiento (trazo del cuadro anterior a este)."""
    if edad < 0 or edad > dur:
        return
    rng = np.random.default_rng(semilla)
    for _ in range(n):
        a = math.radians(rng.uniform(-170, -10))
        v = vel * rng.uniform(0.5, 1.2)

        def pos(e):
            return (x + math.cos(a) * v * e, y + math.sin(a) * v * e + 1600 * e * e)
        p1, p0 = pos(edad), pos(max(0.0, edad - 1.4 / FPS))
        linea(L, [p0, p1], color, rng.uniform(3, 6), alpha=1 - edad / dur, cam=cam)



def zoom_rapido(L, k, centro, sentido=1):
    """Transición 'crash zoom': desenfoque radial (copias escaladas alrededor de 'centro') para unir dos planos de
    escala distinta sin salto. k∈[0,1]; sentido=1 acerca, -1 aleja. Se aplica al cuadro entero."""
    if k <= 0.01:
        return

    def f(img, k=k):
        w, h = img.size
        cx, cy = centro
        acc = np.zeros((h, w, 3), np.float32)
        n = 6
        for i in range(n):
            z = 1 + 0.16 * k * i / (n - 1)
            nw, nh = int(w * z), int(h * z)
            big = img.resize((nw, nh), Image.BILINEAR)
            x0, y0 = int(cx * z - cx), int(cy * z - cy)
            acc += np.asarray(big.crop((x0, y0, x0 + w, y0 + h)), np.float32)
        img.paste(Image.fromarray(np.clip(acc / n, 0, 255).astype(np.uint8), "RGB"))
    L.post.append(f)



def rellenar_mascara(L, m, stops, p0, p1, alpha=1.0):
    """Pinta a través de una máscara (de L.temporal) con un degradado lineal de p0 a p1 (coordenadas de pantalla)."""
    bb = m.getbbox()
    if not bb:
        return
    x0, y0, x1, y1 = bb
    a, b = L.P(*p0, False), L.P(*p1, False)
    dx, dy = b[0] - a[0], b[1] - a[1]
    n2 = dx * dx + dy * dy or 1.0
    gx = (np.arange(x0, x1, dtype=np.float32) + 0.5 - a[0]) * (dx / n2)
    gy = (np.arange(y0, y1, dtype=np.float32) + 0.5 - a[1]) * (dy / n2)
    tt = np.clip(gy[:, None] + gx[None, :], 0, 1)
    pos = np.array([q[0] for q in stops], np.float32)
    cols = np.array([q[1] for q in stops], np.float32)
    img = Image.fromarray(np.stack([np.interp(tt, pos, cols[:, k]) for k in range(3)], -1).astype(np.uint8), "RGB")
    mk = m.crop(bb)
    if alpha < 1:
        mk = mk.point(lambda v: int(v * alpha))
    L.im.paste(img, (x0, y0), mk)


def elefante_3d(L, x, y, h, capa=None, color=None, alpha=1.0, cam=False):
    """Elefante con volumen (no un ícono plano): piel gris con degradado de la luz clave, patas del fondo más oscuras,
    oreja con sombra, colmillo, brillo cálido en el lomo, borde frío y sombra de contacto. Misma firma que elefante()."""
    if h < 2 or alpha <= 0.003:
        return
    E = lambda u, v: (x + u * h, y - v * h)
    sombra_contacto(L, x + 0.62 * h, y + 0.01 * h, 0.62 * h, 0.07 * h, 0.6 * alpha, cam=cam)
    m, d = L.temporal()                                     # patas del fondo
    for lx in (0.32, 0.78):
        poligono(L, [E(lx, 0.45), E(lx + 0.15, 0.45), E(lx + 0.14, 0.0), E(lx + 0.01, 0.0)], capa=d, cam=cam)
    rellenar_mascara(L, m, [(0, (110, 104, 106)), (1, (52, 50, 58))], E(0, 0.5), E(0, 0), alpha)
    m, d = L.temporal()                                     # cuerpo, cabeza, trompa y patas de adelante
    poligono(L, elipse_pts(*E(0.52, 0.6), 0.46 * h, 0.31 * h, n=40), capa=d, cam=cam)
    for lx in (0.14, 0.6):
        poligono(L, [E(lx, 0.45), E(lx + 0.15, 0.45), E(lx + 0.14, 0.0), E(lx + 0.01, 0.0)], capa=d, cam=cam)
    poligono(L, elipse_pts(*E(1.0, 0.74), 0.22 * h, 0.21 * h, n=32), capa=d, cam=cam)
    linea(L, [E(1.14, 0.66), E(1.24, 0.42), E(1.22, 0.16), E(1.27, 0.08)], ancho=0.1 * h, capa=d, cam=cam)
    linea(L, [E(0.07, 0.68), E(0.0, 0.42)], ancho=0.035 * h, capa=d, cam=cam)
    rellenar_mascara(L, m, [(0, (214, 204, 196)), (0.35, (158, 152, 154)), (0.75, (104, 100, 108)), (1, (70, 68, 78))],
                     E(0.2, 0.95), E(0.6, 0.0), alpha)
    m, d = L.temporal()                                     # oreja
    poligono(L, elipse_pts(*E(0.86, 0.72), 0.14 * h, 0.2 * h, n=28), capa=d, cam=cam)
    rellenar_mascara(L, m, [(0, (150, 140, 142)), (1, (84, 80, 90))], E(0.74, 0.9), E(0.98, 0.52), alpha)
    linea(L, elipse_pts(*E(0.86, 0.72), 0.14 * h, 0.2 * h, 100, 260, 14), (56, 52, 60), 0.02 * h, alpha=0.8 * alpha, cam=cam)
    linea(L, elipse_pts(*E(0.5, 0.6), 0.44 * h, 0.29 * h, 205, 300, 18), (255, 214, 170), 0.035 * h, alpha=0.75 * alpha, cam=cam)
    linea(L, elipse_pts(*E(1.0, 0.74), 0.2 * h, 0.19 * h, -70, 30, 12), FRIO, 0.03 * h, alpha=0.7 * alpha, cam=cam)
    linea(L, [E(1.1, 0.6), E(1.2, 0.5), E(1.26, 0.52)], (246, 236, 214), 0.035 * h, alpha=alpha, cam=cam)
    for v in (0.5, 0.36, 0.24):
        linea(L, [E(1.18, v), E(1.26, v - 0.02)], (150, 144, 150), 0.012 * h, alpha=0.6 * alpha, cam=cam)
    circulo(L, *E(1.07, 0.8), 0.025 * h, (24, 22, 28), alpha=alpha, cam=cam)
