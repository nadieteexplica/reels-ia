# -*- coding: utf-8 -*-
"""Arte del Ep. 17 (radiación de la pareja) en laboratorio nocturno, el estilo del beat v5 aprobado.

Objetos reales con volumen (degradado + sombra de contacto + borde frío), energía oro sólo en lo radiactivo.
Todo en coordenadas de pantalla 1080×1920 (la cámara del Lienzo las mueve).
"""
import math
import os
import sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(RAIZ, "studio", "plantilla"))
import kit_explica as K  # noqa: E402

EST = K.ESTILOS["laboratorio_nocturno"]
TINTA, GRIS, ORO = K.rgb(EST["tinta"]), K.rgb(EST["gris"]), K.rgb(EST["energia"])
VERDE = K.rgb("#5CD68A")

PLATANO = [(0.0, (150, 112, 34)), (0.18, (222, 182, 62)), (0.42, (248, 220, 104)), (0.62, (236, 200, 78)),
           (0.86, (186, 142, 44)), (1.0, (120, 86, 28))]
MADERA = [(0.0, (70, 46, 30)), (0.4, (118, 80, 50)), (0.7, (98, 64, 40)), (1.0, (58, 38, 26))]
COLCHA = [(0.0, (54, 66, 92)), (0.35, (78, 94, 126)), (0.7, (64, 78, 106)), (1.0, (40, 50, 72))]
SABANA = [(0.0, (170, 172, 176)), (0.5, (214, 214, 216)), (1.0, (160, 162, 168))]
PIEL = [(0.0, (150, 104, 78)), (0.45, (206, 152, 116)), (1.0, (140, 96, 72))]
CONCRETO = [(0.0, (92, 96, 104)), (0.3, (168, 172, 178)), (0.55, (200, 202, 206)), (0.8, (130, 134, 142)),
            (1.0, (84, 88, 96))]
ACERO = [(0.0, (72, 76, 86)), (0.3, (176, 182, 192)), (0.45, (226, 230, 236)), (0.7, (124, 130, 140)),
         (1.0, (78, 82, 92))]


def _rot(p, c, ang):
    ca, sa = math.cos(ang), math.sin(ang)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * ca - y * sa, c[1] + x * sa + y * ca)


# ------------------------------------------------------------------ plátano
def platano(L, cx, cy, largo=300, ang=0.0, brillo=0.0, pelado=0.0, alpha=1.0, cam=True, sombra=True):
    """Plátano real con volumen (media luna con degradado a lo ancho, puntas oscuras). brillo∈[0,1]: radiactivo
    (borde oro que brilla). pelado∈[0,1]: queda la cáscara abierta (para 'comerte un plátano')."""
    n = 28
    a = math.radians(ang)
    R = largo * 0.95                      # radio de la curva
    span = largo / R
    pts_c = []
    for i in range(n + 1):
        u = i / n
        th = -span / 2 + span * u
        x, y = R * math.sin(th), -R * math.cos(th) + R
        w = largo * 0.105 * math.sin(math.pi * min(1, max(0, u * 1.08 - 0.02))) ** 0.7
        pts_c.append((x, y, th, w))
    arriba = [(x - math.sin(th) * w * -1 * 0 + 0, y - w) for x, y, th, w in pts_c]
    abajo = [(x, y + w * 0.85) for x, y, th, w in pts_c]
    poly = [(cx + p[0], cy + p[1]) for p in arriba] + [(cx + p[0], cy + p[1]) for p in abajo[::-1]]
    poly = [_rot(p, (cx, cy), a) for p in poly]
    if sombra:
        K.sombra_contacto(L, cx, cy + largo * 0.16, largo * 0.42, largo * 0.05, 0.55 * alpha, cam=cam)
    p0 = _rot((cx, cy - largo * 0.12), (cx, cy), a)
    p1 = _rot((cx, cy + largo * 0.12), (cx, cy), a)
    if pelado < 1:
        K.relleno_gradiente(L, poly, PLATANO, p0, p1, alpha=alpha * (1 - pelado * 0.8), cam=cam)
        K.linea(L, poly + [poly[0]], (70, 50, 20), max(2, largo * 0.012), alpha=alpha * 0.8, cam=cam)
        # raya del lomo (arista) y puntas
        lomo = [_rot((cx + x, cy + y - w * 0.15), (cx, cy), a) for x, y, th, w in pts_c[3:-3]]
        K.linea(L, lomo, (255, 236, 150), max(2, largo * 0.008), alpha=alpha * 0.6, cam=cam)
        for e in (pts_c[0], pts_c[-1]):
            K.circulo(L, *_rot((cx + e[0], cy + e[1]), (cx, cy), a), largo * 0.022, (70, 52, 30), alpha=alpha, cam=cam)
    if pelado > 0:                         # cáscara abierta: tres tiras
        k = K.ease_salida(K.clamp(pelado))
        base = _rot((cx + pts_c[-1][0], cy + pts_c[-1][1]), (cx, cy), a)
        for s, d in ((-1, 0.9), (0, 0.0), (1, -0.9)):
            ang_t = a + math.radians(200 + 40 * s) * k * 0.5
            tira = []
            for i in range(12):
                u = i / 11
                tira.append((base[0] + math.cos(ang_t + d * u * k) * largo * 0.42 * u,
                             base[1] + math.sin(ang_t + d * u * k) * largo * 0.42 * u + largo * 0.1 * u * u))
            K.linea(L, tira, (206, 168, 60), largo * 0.07, alpha=alpha * k, cam=cam)
            K.linea(L, tira, (120, 86, 28), largo * 0.012, alpha=alpha * k, cam=cam)
    if brillo > 0:
        K.linea(L, poly + [poly[0]], capa="energia", ancho=max(3, largo * 0.016), alpha=brillo * alpha, cam=cam)
        r_ = min(largo * 0.5, 160)
        K.brillo_suave(L, cx, cy + largo * 0.05, r_, r_ * 0.45, ORO, 0.2 * brillo * alpha, 12, cam=cam)
    return poly


# ------------------------------------------------------------------ cama vista desde arriba
def cama_arriba(L, cx, cy, ancho=620, alto=860, t=0.0, brillo_izq=0.0, brillo_der=0.0, izq_platano=0.0,
                respira=True, alpha=1.0, cam=True):
    """Cama doble desde arriba: marco de madera, colchón, 2 almohadas, colcha con dos bultos y dos cabezas.
    brillo_*: la persona se enciende en oro (radiactiva). izq_platano: la persona de la izquierda se vuelve un
    plátano gigante. Devuelve los centros de las dos personas (para los rayos)."""
    x0, y0, x1, y1 = cx - ancho / 2, cy - alto / 2, cx + ancho / 2, cy + alto / 2
    K.sombra_contacto(L, cx + 20, y1 + 10, ancho * 0.55, 28, 0.6 * alpha, cam=cam)
    marco = [(x0 - 22, y0 - 40), (x1 + 22, y0 - 40), (x1 + 22, y1 + 18), (x0 - 22, y1 + 18)]
    K.relleno_gradiente(L, marco, MADERA, (x0, y0), (x1, y0), alpha=alpha, cam=cam)
    cabecera = [(x0 - 30, y0 - 70), (x1 + 30, y0 - 70), (x1 + 30, y0 - 30), (x0 - 30, y0 - 30)]
    K.relleno_gradiente(L, cabecera, MADERA, (x0, y0 - 70), (x0, y0 - 30), alpha=alpha, cam=cam)
    colchon = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    K.relleno_gradiente(L, colchon, SABANA, (x0, y0), (x1, y0), alpha=alpha, cam=cam)
    # almohadas
    centros = []
    for s in (-1, 1):
        ax = cx + s * ancho * 0.24
        alm = K.elipse_pts(ax, y0 + 95, ancho * 0.2, 62, n=40)
        K.relleno_gradiente(L, alm, SABANA, (ax, y0 + 40), (ax, y0 + 150), alpha=alpha, cam=cam)
        K.linea(L, alm, (130, 132, 140), 2.5, alpha=alpha * 0.7, cam=cam)
        centros.append((ax, y0 + 300))
    # colcha con dos bultos (respiran)
    yc = y0 + 175
    resp = [math.sin(t * 1.6 + f) * 6 if respira else 0 for f in (0.0, 1.9)]
    borde = [(x0 - 6, yc)]
    for i in range(21):
        u = i / 20
        x = x0 + (x1 - x0) * u
        bump = sum(math.exp(-((x - (cx + s * ancho * 0.24)) / (ancho * 0.16)) ** 2) * (18 + r)
                   for s, r in zip((-1, 1), resp))
        borde.append((x, yc - bump))
    borde += [(x1 + 6, yc), (x1 + 6, y1 + 6), (x0 - 6, y1 + 6)]
    K.relleno_gradiente(L, borde, COLCHA, (x0, yc), (x1, yc), alpha=alpha, cam=cam)
    for s, r in zip((-1, 1), resp):           # volumen de los cuerpos bajo la colcha
        bx = cx + s * ancho * 0.24
        cuerpo = K.elipse_pts(bx, y0 + 470, ancho * 0.17 + r * 0.6, alto * 0.34, n=36)
        K.poligono(L, cuerpo, (96, 114, 150), alpha=alpha * 0.45, cam=cam)
        K.linea(L, K.elipse_pts(bx - 12, y0 + 450, ancho * 0.12, alto * 0.28, 200, 320, n=16), (140, 160, 196), 3,
                alpha=alpha * 0.5, cam=cam)
    K.linea(L, borde[1:22], (150, 168, 200), 3, alpha=alpha * 0.8, cam=cam)
    # cabezas sobre las almohadas
    for i, s in enumerate((-1, 1)):
        hx, hy = cx + s * ancho * 0.24, y0 + 105
        if i == 0 and izq_platano > 0:
            continue
        cab = K.elipse_pts(hx, hy, 56, 66, n=30)
        K.relleno_gradiente(L, cab, PIEL, (hx - 56, hy), (hx + 56, hy), alpha=alpha, cam=cam)
        pelo = K.elipse_pts(hx, hy - 18, 60, 52, 180, 360, n=20) + [(hx + 56, hy - 4), (hx - 56, hy - 4)]
        K.poligono(L, pelo, (40, 30, 26) if i == 0 else (88, 60, 40), alpha=alpha, cam=cam)
        for e in (-1, 1):                   # ojos cerrados
            K.linea(L, [(hx + e * 20 - 9, hy + 14), (hx + e * 20, hy + 19), (hx + e * 20 + 9, hy + 14)], (60, 40, 34),
                    3, alpha=alpha, cam=cam)
    # brillo radiactivo de cada persona
    for (b, s) in ((brillo_izq, -1), (brillo_der, 1)):
        if b <= 0:
            continue
        hx = cx + s * ancho * 0.24
        cont = K.elipse_pts(hx, y0 + 105, 62, 72, n=30)
        cuerpo = K.elipse_pts(hx, y0 + 470, ancho * 0.18, alto * 0.35, n=40)
        K.linea(L, cont, capa="energia", ancho=4, alpha=b * alpha, cam=cam)
        K.linea(L, cuerpo, capa="energia", ancho=4, alpha=b * alpha * 0.85, cam=cam)
        K.brillo_suave(L, hx, y0 + 380, ancho * 0.2, alto * 0.4, ORO, 0.16 * b * alpha, 14, cam=cam)
    if izq_platano > 0:                        # la pareja es un plátano gigante (abrazado)
        hx = cx - ancho * 0.24
        platano(L, hx, y0 + 330, alto * 0.75, ang=96, brillo=1.0, alpha=alpha * izq_platano, cam=cam, sombra=False)
    return centros


def velador(L, x, y, alpha=1.0, cam=True):
    """Velador (mesa de noche) desde arriba, con una lámpara chica. (x, y) = centro de la tapa."""
    tapa = [(x - 110, y - 95), (x + 110, y - 95), (x + 110, y + 95), (x - 110, y + 95)]
    K.sombra_contacto(L, x + 14, y + 104, 120, 16, 0.55 * alpha, cam=cam)
    K.relleno_gradiente(L, tapa, MADERA, (x - 110, y), (x + 110, y), alpha=alpha, cam=cam)
    K.linea(L, tapa + [tapa[0]], (40, 26, 18), 3, alpha=alpha, cam=cam)


# ------------------------------------------------------------------ balanza de platillos
def torre_enfriamiento(L, cx, yb, alto=280, alpha=1.0, cam=True, vapor_t=0.0):
    """Torre de enfriamiento de central (hiperboloide) con vapor. (cx, yb) = centro de la base."""
    w0, wc, wt = alto * 0.48, alto * 0.30, alto * 0.36
    izq, der = [], []
    for i in range(21):
        u = i / 20
        y = yb - alto * u
        w = (w0 * (1 - u) ** 2 + wc * 2 * u * (1 - u) * 0.9 + wt * u * u) if u < 1 else wt
        w = w0 + (wc - w0) * min(1, u / 0.72) if u < 0.72 else wc + (wt - wc) * (u - 0.72) / 0.28
        izq.append((cx - w, y))
        der.append((cx + w, y))
    cuerpo = izq + der[::-1]
    K.relleno_gradiente(L, cuerpo, CONCRETO, (cx - w0, yb), (cx + w0, yb), alpha=alpha, cam=cam)
    K.poligono(L, K.elipse_pts(cx, yb - alto, wt, wt * 0.18, n=30), (60, 62, 68), alpha=alpha, cam=cam)
    for k in range(6):
        u = k / 5
        K.linea(L, [(cx - w0 * 0.9 + u * w0 * 1.8, yb), (cx - wc * 0.8 + u * wc * 1.6, yb - alto * 0.72)], (100, 104, 112),
                1.5, alpha=alpha * 0.35, cam=cam)
    for j in range(5):                       # vapor
        f = (vapor_t * 0.35 + j / 5) % 1
        r = wt * (0.55 + 0.6 * f)
        K.circulo(L, cx + math.sin(j * 1.7) * wt * 0.4 * f, yb - alto - wt * 0.3 - f * alto * 0.55, r, (200, 204, 212),
                  alpha=alpha * 0.35 * (1 - f), cam=cam)


def cama_chica(L, cx, yb, ancho=240, alpha=1.0, cam=True, brillo=0.0):
    """Cama doble en 3/4 (para el platillo): base, colchón, almohadas, colcha y dos cabezas."""
    h = ancho * 0.42
    base = [(cx - ancho / 2, yb), (cx + ancho / 2, yb), (cx + ancho / 2, yb - h * 0.45), (cx - ancho / 2, yb - h * 0.45)]
    K.relleno_gradiente(L, base, MADERA, (cx, yb - h * 0.45), (cx, yb), alpha=alpha, cam=cam)
    tapa = [(cx - ancho / 2, yb - h * 0.45), (cx + ancho / 2, yb - h * 0.45), (cx + ancho * 0.42, yb - h),
            (cx - ancho * 0.42, yb - h)]
    K.relleno_gradiente(L, tapa, COLCHA, (cx - ancho / 2, yb), (cx + ancho / 2, yb), alpha=alpha, cam=cam)
    cab = [(cx - ancho * 0.46, yb - h * 0.45), (cx - ancho * 0.46, yb - h * 1.55), (cx - ancho * 0.40, yb - h * 1.6),
           (cx - ancho * 0.40, yb - h)]
    K.relleno_gradiente(L, cab, MADERA, (cx - ancho * 0.5, yb), (cx - ancho * 0.4, yb), alpha=alpha, cam=cam)
    for s in (0.18, 0.44):
        x = cx - ancho * 0.42 + ancho * s * 0.5
        K.poligono(L, K.elipse_pts(x + 12, yb - h * 0.98, ancho * 0.09, h * 0.12, n=16), (220, 220, 222), alpha=alpha,
                   cam=cam)
        cabeza = K.elipse_pts(x + 18, yb - h * 1.08, ancho * 0.055, h * 0.13, n=16)
        K.relleno_gradiente(L, cabeza, PIEL, (x, yb), (x + 40, yb), alpha=alpha, cam=cam)
        if brillo > 0:
            K.linea(L, cabeza, capa="energia", ancho=3, alpha=brillo * alpha, cam=cam)


def balanza(L, cx, cy, inclin=0.12, t=0.0, alpha=1.0, cam=True, brillo_cama=0.0, pila=0.0, platano_en_cama=0.0,
            brazo=290):
    """Balanza de platillos: columna de acero, cruz que se inclina (inclin en radianes, + = baja la izquierda) y dos
    platillos colgando de cadenas. Izquierda: la cama (y la pila de cáscaras); derecha: la torre de una central.
    Devuelve las posiciones de los dos platillos."""
    piv = (cx, cy)
    K.sombra_contacto(L, cx, cy + 720, 300, 26, 0.55 * alpha, cam=cam)
    col = [(cx - 22, cy + 10), (cx + 22, cy + 10), (cx + 34, cy + 700), (cx - 34, cy + 700)]
    K.relleno_gradiente(L, col, ACERO, (cx - 34, cy), (cx + 34, cy), alpha=alpha, cam=cam)
    pie = K.elipse_pts(cx, cy + 710, 170, 34, n=36)
    K.relleno_gradiente(L, pie, ACERO, (cx - 170, cy + 710), (cx + 170, cy + 710), alpha=alpha, cam=cam)
    ex = [(piv[0] - brazo * math.cos(inclin), piv[1] + brazo * math.sin(inclin)),
          (piv[0] + brazo * math.cos(inclin), piv[1] - brazo * math.sin(inclin))]
    viga = [_rot(p, piv, -inclin) for p in [(cx - brazo - 10, cy - 12), (cx + brazo + 10, cy - 12), (cx + brazo + 10, cy + 12),
                                              (cx - brazo - 10, cy + 12)]]
    K.relleno_gradiente(L, viga, ACERO, (cx, cy - 12), (cx, cy + 12), alpha=alpha, cam=cam)
    K.circulo(L, cx, cy, 26, (60, 64, 72), alpha=alpha, cam=cam)
    K.circulo(L, cx, cy, 14, (200, 206, 214), alpha=alpha, cam=cam)
    platos = []
    for i, (px, py) in enumerate(ex):
        yp = py + 400
        for dx in (-120, 0, 120):
            K.linea(L, [(px, py), (px + dx, yp - 8)], (150, 156, 166), 2.5, alpha=alpha, cam=cam)
        plato = K.elipse_pts(px, yp, 150, 26, 0, 180, n=24) + [(px - 150, yp)]
        K.relleno_gradiente(L, plato, ACERO, (px - 150, yp), (px + 150, yp), alpha=alpha, cam=cam)
        K.poligono(L, K.elipse_pts(px, yp, 150, 22, n=30), (70, 74, 82), alpha=alpha, cam=cam)
        platos.append((px, yp))
    (lx, ly), (rx, ry) = platos
    if pila > 0:                              # pila de cáscaras sobre el platillo de la cama
        n = int(4 + 14 * pila)
        for k in range(n):
            ang = (k * 47) % 180 - 90
            platano(L, lx - 90 + (k * 53) % 180, ly - 14 - (k // 5) * 18, 90, ang=ang, pelado=1.0, alpha=alpha, cam=cam,
                    sombra=False)
    if brillo_cama > 0:
        K.brillo_suave(L, lx, ly - 70, 170, 90, ORO, 0.22 * brillo_cama * alpha, 14, cam=cam)
    cama_chica(L, lx, ly - 6, 280, alpha=alpha, cam=cam, brillo=brillo_cama)
    if platano_en_cama > 0:
        platano(L, lx + 10, ly - 80, 150, ang=-8, brillo=1.0, alpha=alpha * platano_en_cama, cam=cam, sombra=False)
    torre_enfriamiento(L, rx, ry - 6, 200, alpha=alpha, cam=cam, vapor_t=t)
    return platos


# ------------------------------------------------------------------ lupa, átomos, rayos
def lupa(L, cx, cy, r, t, t0, destaca=1, alpha=1.0):
    """Lupa redonda (sin cámara) con una grilla de átomos de potasio grises; 'destaca' titilan en oro."""
    if alpha <= 0.003:
        return
    K.circulo(L, cx + 10, cy + 14, r + 22, (0, 0, 0), alpha=0.35 * alpha, cam=False)
    K.circulo(L, cx, cy, r + 18, (50, 54, 62), alpha=alpha, cam=False)
    K.circulo(L, cx, cy, r, (28, 30, 38), alpha=alpha, cam=False)
    paso = r / 3.6
    k = 0
    for iy in range(-4, 5):
        for ix in range(-4, 5):
            x, y = cx + ix * paso + (iy % 2) * paso / 2, cy + iy * paso
            if math.hypot(x - cx, y - cy) > r - paso * 0.5:
                continue
            k += 1
            K.circulo(L, x, y, paso * 0.32, (120, 126, 138), alpha=alpha, cam=False)
            K.circulo(L, x - paso * 0.1, y - paso * 0.1, paso * 0.12, (180, 186, 196), alpha=alpha * 0.8, cam=False)
    if t >= t0:
        tit = 0.6 + 0.4 * math.sin((t - t0) * 9)
        K.circulo(L, cx + paso * 0.5, cy - paso, paso * 0.36, capa="energia", alpha=alpha * tit, cam=False)
    mango = [_rot(p, (cx, cy), math.radians(40)) for p in [(cx + r + 14, cy - 22), (cx + r + 200, cy - 26),
                                                           (cx + r + 200, cy + 26), (cx + r + 14, cy + 22)]]
    K.relleno_gradiente(L, mango, MADERA, mango[0], mango[2], alpha=alpha, cam=False)


def rayo(L, p0, p1, p, ancho=6, alpha=1.0, cam=True, ondas=5):
    """Rayo gamma: trazo ondulado en oro que avanza de p0 a p1 (p∈[0,1])."""
    if p <= 0 or alpha <= 0.003:
        return
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    lg = math.hypot(dx, dy) or 1
    nx, ny = -dy / lg, dx / lg
    pts = []
    n = 40
    for i in range(int(n * min(1, p)) + 1):
        u = i / n
        a = math.sin(u * ondas * 2 * math.pi) * 10
        pts.append((p0[0] + dx * u + nx * a, p0[1] + dy * u + ny * a))
    if len(pts) >= 2:
        K.linea(L, pts, capa="energia", ancho=ancho, alpha=alpha, cam=cam)
        K.circulo(L, pts[-1][0], pts[-1][1], ancho * 1.4, capa="energia", alpha=alpha, cam=cam)


def check(L, cx, cy, tam, p, alpha=1.0):
    if p <= 0:
        return
    pts = [(cx - tam * 0.45, cy), (cx - tam * 0.12, cy + tam * 0.32), (cx + tam * 0.5, cy - tam * 0.38)]
    from_ = K.clamp(p)
    for c, w in (((10, 14, 22), tam * 0.30), (VERDE, tam * 0.19)):
        n = max(2, int(2 + 30 * from_))
        tot = [pts[0]]
        seg = [(pts[0], pts[1]), (pts[1], pts[2])]
        lg = [math.dist(*s_) for s_ in seg]
        obj = sum(lg) * from_
        acc = 0
        for (a, b), l_ in zip(seg, lg):
            if acc + l_ >= obj:
                k = (obj - acc) / l_
                tot.append((a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k))
                break
            tot.append(b)
            acc += l_
        K.linea(L, tot, c, w, alpha=alpha, cam=False)
