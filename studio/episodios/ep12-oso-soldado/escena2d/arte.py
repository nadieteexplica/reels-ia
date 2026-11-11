"""Ep. 12 — El oso soldado. Personajes y objetos 2D de comedia (PIL, sobre studio/plantilla/kit2d.py); parte del arte del Ep. 11.
Paleta viva (outback: tierra naranja, cielo celeste, trigo dorado) con contorno de tinta grueso.
"""
import math, os, random, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(AQUI, "../../../plantilla")))
import kit2d as K
from kit2d import P

W, H = 1080, 1920
TINTA = (40, 30, 28)
C = {
    "cielo": (120, 200, 236), "cielo2": (164, 220, 240), "cielo3": (214, 238, 240), "tierra": (226, 128, 62), "tierra2": (204, 104, 50),
    "tierra3": (176, 84, 44), "trigo": (246, 198, 72), "trigo2": (226, 168, 48), "pluma": (124, 92, 66), "pluma2": (96, 70, 52),
    "pluma3": (156, 122, 90), "cuello": (112, 150, 190), "pico": (60, 54, 52), "pata": (110, 96, 84), "caqui": (188, 170, 110),
    "caqui2": (150, 134, 84), "piel": (240, 196, 160), "piel2": (212, 160, 122), "rojo": (232, 72, 60), "blanco": (255, 250, 240),
    "verde": (110, 160, 84), "verde2": (78, 124, 66), "metal": (92, 98, 108), "metal2": (60, 64, 74), "amarillo": (255, 210, 63),
    "camion": (96, 128, 100), "camion2": (70, 98, 78), "nube": (255, 255, 255), "noche": (38, 44, 78), "madera": (170, 120, 72),
    "oliva": (128, 138, 86), "oliva2": (98, 108, 66), "boina": (70, 62, 54), "oso": (150, 104, 64), "oso2": (118, 80, 50), "oso3": (206, 166, 118),
    "nariz": (50, 38, 34), "arena": (236, 196, 130), "arena2": (214, 170, 104), "monte": (150, 130, 150), "monte2": (112, 98, 128), "nieve": (250, 248, 244),
    "mar": (64, 150, 190), "mar2": (44, 120, 164), "casco_b": (110, 118, 128), "ocaso": (255, 170, 90), "ocaso2": (236, 110, 90), "ocaso3": (120, 70, 110),
    "campo": (92, 104, 70), "campo2": (70, 82, 56), "pasto": (126, 184, 96), "pasto2": (96, 156, 78), "bronce": (120, 150, 130), "bronce2": (88, 116, 100),
    "papel": (250, 240, 214), "sello": (200, 50, 50),
}


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def suave(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def sale(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def pop(edad, dur=0.28):
    if edad <= 0:
        return 0.0
    if edad >= dur:
        return 1.0
    x = edad / dur
    return 1 + 0.25 * math.sin(math.pi * x) * (1 - x) * 2 - (1 - x) ** 3


def rebote(edad, dur=0.5):
    """0→1 con rebote (para cosas que caen)."""
    if edad <= 0:
        return 0.0
    x = clamp(edad / dur)
    return 1 - abs(math.cos(x * math.pi * 2.5)) * (1 - x) ** 2


# ------------------------------------------------------------------ fondos
def outback(L, horizonte=1150, t=0.0, nubes=True, sol=True, cerros=True):
    K.cielo_bandas(L, [C["cielo"], C["cielo"], C["cielo2"], C["cielo3"]], 0, horizonte)
    if sol:
        K.circulo(L, 880, 300, 150, (255, 236, 150, 90))
        K.circulo(L, 880, 300, 105, (255, 232, 120), TINTA, 6)
    if nubes:
        for i, (x, y, s) in enumerate(((180, 250, 1.0), (640, 480, 0.75), (980, 640, 0.6))):
            nube(L, (x + t * 14 * (1 + i * 0.3)) % (W + 400) - 200, y, s)
    if cerros:
        mesa(L, 210, horizonte, 360, 190)
        mesa(L, 840, horizonte, 300, 130)
    L.d.rectangle((0, L.S(horizonte), L.S(W), L.S(H)), fill=C["tierra"])
    L.d.line([L.pt(0, horizonte), L.pt(W, horizonte)], fill=TINTA, width=int(L.S(7)))
    random.seed(5)
    for i in range(16):
        x, y = random.uniform(0, W), random.uniform(horizonte + 40, H)
        w = random.uniform(40, 120)
        K.linea(L, [(x, y), (x + w, y)], C["tierra2"], 8)


def mesa(L, x, y, w, h):
    K.poligono(L, [(x - w / 2, y), (x - w * 0.36, y - h), (x + w * 0.36, y - h), (x + w / 2, y)], C["tierra3"], TINTA, 6)
    K.linea(L, [(x - w * 0.3, y - h * 0.62), (x + w * 0.24, y - h * 0.62)], C["tierra2"], 9)


def nube(L, x, y, s=1.0):
    pts = ((-90, 10, 60), (-30, -30, 80), (50, -10, 70), (110, 15, 50), (0, 25, 70))
    for dx, dy, r in pts:
        K.circulo(L, x + dx * s, y + dy * s, r * s + 6, TINTA)
    for dx, dy, r in pts:
        K.circulo(L, x + dx * s, y + dy * s, r * s, C["nube"])


def trigal(L, y0, y1, t=0.0, filas=5, comido=0.0, semilla=3):
    """Campo de trigo entre y0 (fondo) e y1 (frente). comido 0..1 = espigas mordidas desde la derecha."""
    L.d.rectangle((0, L.S(y0), L.S(W), L.S(H)), fill=C["trigo2"])
    random.seed(semilla)
    for f in range(filas):
        u = f / max(1, filas - 1)
        y = y0 + (y1 - y0) * u
        alto = 90 + 110 * u
        paso = 46 + 26 * u
        x = -20 + random.uniform(0, 30)
        while x < W + 30:
            mord = (x / W) > (1 - comido * 1.15) + random.uniform(-0.08, 0.08)
            ond = math.sin(t * 2.4 + x * 0.013 + f) * (10 + 8 * u)
            if mord:
                K.linea(L, [(x, y), (x + ond * 0.3, y - alto * 0.3)], TINTA, 13 + 4 * u)
                K.linea(L, [(x, y), (x + ond * 0.3, y - alto * 0.3)], C["trigo2"], 7 + 4 * u)
            else:
                K.linea(L, [(x, y), (x + ond, y - alto)], TINTA, 13 + 4 * u)
                K.linea(L, [(x, y), (x + ond, y - alto)], C["trigo"], 7 + 4 * u)
                K.elipse(L, x + ond, y - alto - 22, 12 + 5 * u, 30 + 10 * u, C["trigo"], TINTA, 4)
            x += paso + random.uniform(-8, 8)


def arbusto(L, x, y, s=1.0, c=None):
    c = c or C["verde"]
    pts = ((-110, 0, 70), (-50, -50, 86), (40, -60, 90), (110, -6, 72), (0, 0, 90))
    for dx, dy, r in pts:
        K.circulo(L, x + dx * s, y + dy * s - 40 * s, r * s + 6, TINTA)
    for dx, dy, r in pts:
        K.circulo(L, x + dx * s, y + dy * s - 40 * s, r * s, c)
    L.d.rectangle((L.S(x - 172 * s), L.S(y - 30 * s), L.S(x + 172 * s), L.S(H + 10)), fill=c)


def polvo(L, x, y, t, n=7, s=1.0, dir_x=-1, semilla=1):
    random.seed(semilla)
    for i in range(n):
        u = (t * 1.8 + i / n) % 1.0
        r = (22 + 60 * u) * s
        px = x + dir_x * (40 + 330 * u) * s
        py = y - (20 + 70 * u * random.uniform(0.4, 1.2)) * s
        K.circulo(L, px, py, r, (250, 226, 190, int(210 * (1 - u))))


def lineas_vel(L, x0, x1, y0, y1, t, n=9, color=(255, 255, 255, 190), semilla=2):
    random.seed(semilla)
    for i in range(n):
        y = random.uniform(y0, y1)
        lar = random.uniform(120, 320)
        u = (t * random.uniform(1.6, 2.6) + random.random()) % 1.0
        x = x1 - (x1 - x0 + lar) * u
        K.linea(L, [(x, y), (x + lar, y)], color, 9)


# ------------------------------------------------------------------ el emú
def emu(L, x, y, alto=700, t=0.0, mira=1, corre=0.0, ojos="normal", casco=False, lentes=False, binoc=False, come=0.0,
        cuello_u=1.0, alas=0.0, boca=0.0, medalla=False, squash=0.0, lengua=False, fase=0.0):
    """Emú de caricatura con las patas en (x, y). corre = velocidad del ciclo de patas (0 quieto). come 0..1 = baja la cabeza.
    ojos: normal | serio | feliz | susto | x. alas 0..1 = aletea. squash 0..1 = aplastado (contra la reja)."""
    k = alto / 700.0
    s = mira
    ph = t * corre * 13 + fase
    bob = (abs(math.sin(ph)) * 26 * k if corre else math.sin(t * 2.6 + fase) * 6 * k)
    cy = y - 330 * k - bob                         # centro del cuerpo
    cx = x
    # patas (dos, con rodilla hacia atrás)
    for i, off in enumerate((0.0, math.pi)):
        a = math.sin(ph + off) if corre else 0.0
        lift = max(0.0, math.cos(ph + off)) if corre else 0.0
        hx = cx + (-18 + i * 36) * k
        pie = (hx + s * a * 150 * k, y - lift * 70 * k)
        rod = ((hx + pie[0]) / 2 - s * 46 * k, (cy + 90 * k + pie[1]) / 2)
        col = C["pata"] if i else tuple(int(c * 0.82) for c in C["pata"])
        K.linea(L, [(hx, cy + 90 * k), rod, pie], TINTA, 34 * k)
        K.linea(L, [(hx, cy + 90 * k), rod, pie], col, 20 * k)
        for da in (-0.5, 0.0, 0.5):                 # tres dedos
            K.linea(L, [pie, (pie[0] + s * math.cos(da) * 56 * k, pie[1] + math.sin(da) * 26 * k + 6 * k)], TINTA, 22 * k)
            K.linea(L, [pie, (pie[0] + s * math.cos(da) * 56 * k, pie[1] + math.sin(da) * 26 * k + 6 * k)], col, 11 * k)
    # cuerpo peludo (óvalo con flecos)
    rx, ry = 210 * k * (1 - 0.25 * squash), 150 * k * (1 + 0.2 * squash)
    random.seed(11)
    for i in range(13):                             # flecos de atrás y abajo
        a = math.radians(40 + i * 17)
        fx = cx - s * math.cos(a) * rx * 0.96
        fy = cy + math.sin(a) * ry * 0.96
        K.circulo(L, fx, fy, 44 * k, C["pluma2"], TINTA, 5)
    K.elipse(L, cx, cy, rx, ry, C["pluma"], TINTA, 7)
    for i in range(7):                              # plumas marcadas
        a = random.uniform(0, 6.28)
        px, py = cx + math.cos(a) * rx * 0.55, cy + math.sin(a) * ry * 0.5
        L.d.arc((L.S(px - 34 * k), L.S(py - 20 * k), L.S(px + 34 * k), L.S(py + 30 * k)), 20, 160, fill=C["pluma2"], width=int(L.S(7 * k)))
    # alita ridícula
    aw = math.sin(t * 34) * 38 * alas
    wy = cy + 6 * k - (70 * k + aw * k) * alas
    K.elipse(L, cx - s * 50 * k, wy, 118 * k, (58 + 10 * alas) * k, C["pluma3"], TINTA, 6)
    for i in range(3):
        L.d.arc((L.S(cx - s * 50 * k - (90 - i * 30) * k), L.S(wy - 30 * k), L.S(cx - s * 50 * k + (90 - i * 30) * k), L.S(wy + 40 * k)), 30, 150, fill=C["pluma2"], width=int(L.S(6 * k)))
    # cuello y cabeza
    base = (cx + s * 150 * k * (1 - 0.3 * squash), cy - 70 * k)
    largo = 330 * k * cuello_u
    baja = suave(come)
    ang = math.radians(-78 + 150 * baja) + math.sin(t * 2.6 + fase) * 0.04 * (1 - baja) + (math.sin(ph * 2) * 0.05 if corre else 0)
    cab = (base[0] + s * math.cos(ang) * largo, base[1] + math.sin(ang) * largo)
    mid = ((base[0] + cab[0]) / 2 + s * 40 * k * (1 - baja), (base[1] + cab[1]) / 2 + 30 * k * baja)
    K.linea(L, [base, mid, cab], TINTA, 78 * k)
    K.linea(L, [base, mid, cab], C["cuello"], 62 * k)
    K.circulo(L, base[0], base[1] + 6 * k, 58 * k, C["pluma"])      # collar de plumas
    hx_, hy_ = cab[0] + s * 16 * k, cab[1] - 10 * k
    rh = 72 * k
    # pico
    ab = 10 * k + 34 * k * clamp(boca)
    K.poligono(L, [(hx_ + s * 40 * k, hy_ - 14 * k), (hx_ + s * 150 * k, hy_ + 4 * k - ab * 0.2), (hx_ + s * 44 * k, hy_ + 22 * k)], C["pico"], TINTA, 6)
    K.poligono(L, [(hx_ + s * 36 * k, hy_ + 20 * k), (hx_ + s * 132 * k, hy_ + 14 * k + ab), (hx_ + s * 34 * k, hy_ + 44 * k)], (84, 76, 72), TINTA, 6)
    if lengua:
        K.elipse(L, hx_ + s * 120 * k, hy_ + 40 * k + math.sin(t * 30) * 8 * k, 44 * k, 16 * k, (240, 110, 130), TINTA, 4)
    K.circulo(L, hx_, hy_, rh, C["cuello"], TINTA, 7)
    for i in range(5):                              # mechón
        a = math.radians(-150 + i * 26) if s > 0 else math.radians(-30 - i * 26)
        K.linea(L, [(hx_ + math.cos(a) * rh * 0.8, hy_ + math.sin(a) * rh * 0.8), (hx_ + math.cos(a) * rh * 1.35, hy_ + math.sin(a) * rh * 1.35)], TINTA, 13 * k)
    # ojos
    ex, ey = hx_ + s * 24 * k, hy_ - 12 * k
    if lentes:
        K.caja_red(L, ex - 62 * k, ey - 26 * k, ex + 62 * k, ey + 26 * k, 14 * k, (20, 20, 24), TINTA, 5)
        K.linea(L, [(ex - 40 * k, ey - 10 * k), (ex - 14 * k, ey - 10 * k)], (255, 255, 255, 200), 7 * k)
    elif binoc:
        for dy in (-22, 22):
            K.caja_red(L, ex - 10 * k if s > 0 else ex - 120 * k, ey + dy * k - 24 * k, ex + 120 * k if s > 0 else ex + 10 * k, ey + dy * k + 24 * k, 12 * k, C["metal2"], TINTA, 5)
            K.circulo(L, ex + s * 122 * k, ey + dy * k, 28 * k, (170, 220, 240), TINTA, 5)
    else:
        for i, dx in enumerate((-22, 30)):
            r = (30 if i else 26) * k
            ox, oy = ex + dx * k, ey
            if ojos == "feliz":
                L.d.arc((L.S(ox - r), L.S(oy - r), L.S(ox + r), L.S(oy + r)), 200, 340, fill=TINTA, width=int(L.S(9 * k)))
                continue
            if ojos == "x":
                for sg in (-1, 1):
                    K.linea(L, [(ox - r * 0.7, oy - sg * r * 0.7), (ox + r * 0.7, oy + sg * r * 0.7)], TINTA, 9 * k)
                continue
            K.circulo(L, ox, oy, r * (1.25 if ojos == "susto" else 1.0), C["blanco"], TINTA, 5)
            pr = r * (0.3 if ojos == "susto" else 0.46)
            K.circulo(L, ox + s * r * 0.3, oy + (0 if ojos != "serio" else r * 0.15), pr, TINTA)
            if ojos == "serio":
                K.linea(L, [(ox - r * 1.2, oy - r * (1.25 if i == 0 else 0.7) if s > 0 else oy - r * (0.7 if i == 0 else 1.25)),
                            (ox + r * 1.2, oy - r * (0.7 if i == 0 else 1.25) if s > 0 else oy - r * (1.25 if i == 0 else 0.7))], TINTA, 11 * k)
    if casco:
        L.d.chord((L.S(hx_ - rh * 1.2), L.S(hy_ - rh * 1.55), L.S(hx_ + rh * 1.2), L.S(hy_ + rh * 0.35)), 180, 360, fill=C["verde2"], outline=TINTA, width=int(L.S(7)))
        K.caja_red(L, hx_ - rh * 1.4, hy_ - rh * 0.66, hx_ + rh * 1.4, hy_ - rh * 0.44, 8 * k, C["verde2"], TINTA, 6)
    if medalla:
        K.linea(L, [(base[0] - 30 * k, base[1] - 30 * k), (base[0] + s * 10 * k, base[1] + 80 * k), (base[0] + 50 * k, base[1] - 30 * k)], C["rojo"], 16 * k)
        K.circulo(L, base[0] + s * 10 * k, base[1] + 100 * k, 40 * k, C["amarillo"], TINTA, 6)
        K.texto(L, "1", base[0] + s * 10 * k, base[1] + 100 * k, 46 * k, TINTA)
    return (hx_, hy_)


def emu_chico(L, x, y, alto, t, mira=1, corre=1.0, fase=0.0, ojos="normal", come=0.0):
    return emu(L, x, y, alto=alto, t=t, mira=mira, corre=corre, fase=fase, ojos=ojos, come=come)


# ------------------------------------------------------------------ soldados
def soldado(L, x, y, alto=520, t=0.0, mira=1, cara="normal", brazo_der=8, brazo_izq=8, paso=0.0, sombrero=True, bandera=False,
            tiembla=0.0, oficial=False, sudor=False, gorro="boina", torso=None):
    """Soldado australiano de caricatura (sombrero con ala doblada). cara: normal | susto | feliz | triste | enojo."""
    x = x + math.sin(t * 50) * tiembla * 7
    k = alto / 420.0
    ropa = {"cabeza": "nada", "torso": torso or C["oliva"], "piernas": C["oliva2"], "botas": (84, 60, 44), "piel": C["piel"], "piel2": C["piel2"]}
    K.persona(L, x, y, alto=alto, ropa=ropa, pose={"brazo_der": brazo_der, "brazo_izq": brazo_izq, "paso": paso}, mira=mira, t=t)
    cy = y - 330 * k + math.sin(t * 2.2) * 3 * k - 62 * k
    # tapa la cara simple del kit y dibuja una expresiva
    K.circulo(L, x, cy, 52 * k, C["piel"], TINTA, 5)
    ex = mira * 8 * k
    if cara == "susto":
        for s in (-1, 1):
            K.circulo(L, x + s * 19 * k + ex, cy + 2 * k, 15 * k, C["blanco"], TINTA, 3)
            K.circulo(L, x + s * 19 * k + ex, cy + 3 * k, 4.5 * k, TINTA)
        K.elipse(L, x + ex, cy + 32 * k, 11 * k, 9 * k + 3 * k * math.sin(t * 20), (110, 44, 40), TINTA, 3)
    elif cara == "feliz":
        for s in (-1, 1):
            L.d.arc((L.S(x + s * 18 * k + ex - 9 * k), L.S(cy - 4 * k), L.S(x + s * 18 * k + ex + 9 * k), L.S(cy + 12 * k)), 180, 360, fill=TINTA, width=int(L.S(4.5 * k)))
        L.d.chord((L.S(x - 20 * k + ex), L.S(cy + 10 * k), L.S(x + 20 * k + ex), L.S(cy + 40 * k)), 0, 180, fill=C["blanco"], outline=TINTA, width=int(L.S(3.5 * k)))
    elif cara == "triste":
        for s in (-1, 1):
            K.circulo(L, x + s * 17 * k + ex, cy + 6 * k, 5.5 * k, TINTA)
            K.linea(L, [(x + s * 30 * k + ex, cy - 2 * k), (x + s * 8 * k + ex, cy - 13 * k)], TINTA, 4 * k)
        L.d.arc((L.S(x - 14 * k + ex), L.S(cy + 24 * k), L.S(x + 14 * k + ex), L.S(cy + 40 * k)), 200, 340, fill=TINTA, width=int(L.S(4 * k)))
    elif cara == "enojo":
        for s in (-1, 1):
            K.circulo(L, x + s * 17 * k + ex, cy + 6 * k, 6 * k, TINTA)
            K.linea(L, [(x + s * 30 * k + ex, cy - 14 * k), (x + s * 6 * k + ex, cy - 4 * k)], TINTA, 5 * k)
        K.elipse(L, x + ex, cy + 30 * k, 16 * k, 8 * k, (110, 44, 40), TINTA, 3)
    else:
        for s in (-1, 1):
            K.circulo(L, x + s * 17 * k + ex, cy + 4 * k, 6 * k, TINTA)
        K.linea(L, [(x - 12 * k + ex, cy + 26 * k), (x + 12 * k + ex, cy + 26 * k)], TINTA, 4 * k)
    if oficial:                                     # bigote de jefe
        K.poligono(L, [(x - 30 * k + ex, cy + 20 * k), (x + ex, cy + 10 * k), (x + 30 * k + ex, cy + 20 * k), (x + ex, cy + 24 * k)], (120, 84, 50), TINTA, 3)
    if sombrero and gorro == "boina":
        L.d.chord((L.S(x - 60 * k), L.S(cy - 84 * k), L.S(x + 60 * k), L.S(cy - 2 * k)), 180, 360, fill=C["boina"], outline=TINTA, width=int(L.S(5)))
        K.elipse(L, x - mira * 22 * k, cy - 62 * k, 52 * k, 22 * k, C["boina"], TINTA, 5)
        K.circulo(L, x + mira * 26 * k, cy - 54 * k, 9 * k, C["amarillo"], TINTA, 3)
    elif sombrero and gorro == "casco":
        L.d.chord((L.S(x - 62 * k), L.S(cy - 96 * k), L.S(x + 62 * k), L.S(cy + 6 * k)), 180, 360, fill=C["oliva2"], outline=TINTA, width=int(L.S(5)))
        K.caja_red(L, x - 74 * k, cy - 50 * k, x + 74 * k, cy - 36 * k, 6 * k, C["oliva2"], TINTA, 5)
    if sudor:
        for i, sx in enumerate((-66, 70)):
            u = (t * 1.4 + i * 0.5) % 1.0
            sy = cy - 30 * k + 60 * k * u
            K.poligono(L, [(x + sx * k, sy - 18 * k), (x + sx * k - 8 * k, sy), (x + sx * k + 8 * k, sy)], (150, 214, 240), TINTA, 2)
            K.circulo(L, x + sx * k, sy + 2 * k, 8.5 * k, (150, 214, 240), TINTA, 2)
    if bandera:
        hom = y - 330 * k
        mx, my = x + mira * 70 * k, hom - 60 * k
        K.linea(L, [(mx, my + 120 * k), (mx, my - 190 * k)], TINTA, 13 * k)
        K.linea(L, [(mx, my + 120 * k), (mx, my - 190 * k)], C["madera"], 7 * k)
        w = math.sin(t * 7) * 16 * k
        K.poligono(L, [(mx, my - 190 * k), (mx + mira * 150 * k, my - 176 * k + w), (mx + mira * 150 * k, my - 86 * k - w), (mx, my - 96 * k)], C["blanco"], TINTA, 5)
    return (x, cy)


def ametralladora(L, x, y, s=1.0, mira=1, t=0.0, dispara=0.0, trabada=False, bipode=True):
    """Ametralladora tipo Lewis de caricatura (cañón gordo y plato arriba), boca hacia `mira`. (x, y) = centro del cuerpo."""
    m = mira
    rec = -m * 10 * s * (math.sin(t * 60) if dispara else 0)
    x = x + rec
    if bipode:
        for dx in (60, 110):
            K.linea(L, [(x + m * 150 * s, y + 10 * s), (x + m * dx * s + m * 60 * s, y + 120 * s)], TINTA, 15 * s)
            K.linea(L, [(x + m * 150 * s, y + 10 * s), (x + m * dx * s + m * 60 * s, y + 120 * s)], C["metal"], 7 * s)
    K.poligono(L, [(x - m * 190 * s, y - 14 * s), (x - m * 80 * s, y - 20 * s), (x - m * 80 * s, y + 24 * s), (x - m * 150 * s, y + 30 * s), (x - m * 200 * s, y + 60 * s)], C["madera"], TINTA, 5)
    K.caja_red(L, x - 90 * s, y - 26 * s, x + 60 * s, y + 30 * s, 8 * s, C["metal2"], TINTA, 5)
    a, b = (x + m * 40 * s, x + m * 270 * s) if m > 0 else (x + m * 270 * s, x + m * 40 * s)
    K.caja_red(L, a, y - 34 * s, b, y + 30 * s, 26 * s, C["metal"], TINTA, 5)
    K.elipse(L, x - m * 10 * s, y - 40 * s, 80 * s, 20 * s, C["metal2"], TINTA, 5)
    K.elipse(L, x - m * 10 * s, y - 48 * s, 30 * s, 8 * s, C["metal"], TINTA, 3)
    boca_ = (x + m * 272 * s, y - 2 * s)
    if dispara:
        f = 0.6 + 0.4 * abs(math.sin(t * 70))
        pts = []
        for i in range(12):
            an = i * math.pi / 6
            r = (120 if i % 2 == 0 else 50) * s * f * dispara
            pts.append((boca_[0] + m * 60 * s + math.cos(an) * r, boca_[1] + math.sin(an) * r * 0.8))
        K.poligono(L, pts, C["amarillo"], TINTA, 5)
    if trabada:
        for i in range(5):
            u = (t * 0.9 + i / 5) % 1.0
            K.circulo(L, boca_[0] - m * 80 * s + math.sin(i * 3) * 30 * s, y - 60 * s - 200 * s * u, (22 + 40 * u) * s, (70, 66, 66, int(220 * (1 - u))))
    return boca_


def camion(L, x, y, s=1.0, mira=1, t=0.0, salta=1.0):
    """Camión de los años 30 con plataforma atrás; (x, y) = suelo bajo el centro."""
    m = mira
    by = y - abs(math.sin(t * 17)) * 26 * s * salta
    rot = math.sin(t * 17 + 1) * 0.03 * salta
    def R(px, py):
        dx, dy = px - x, py - by
        return (x + dx * math.cos(rot) - dy * math.sin(rot), by + dx * math.sin(rot) + dy * math.cos(rot))
    plat = [R(x - m * 330 * s, by - 150 * s), R(x + m * 60 * s, by - 150 * s), R(x + m * 60 * s, by - 96 * s), R(x - m * 330 * s, by - 96 * s)]
    K.poligono(L, plat, C["madera"], TINTA, 6)
    cab = [R(x + m * 60 * s, by - 330 * s), R(x + m * 220 * s, by - 330 * s), R(x + m * 240 * s, by - 200 * s), R(x + m * 330 * s, by - 190 * s),
           R(x + m * 340 * s, by - 96 * s), R(x + m * 60 * s, by - 96 * s)]
    K.poligono(L, cab, C["camion"], TINTA, 6)
    K.poligono(L, [R(x + m * 110 * s, by - 300 * s), R(x + m * 205 * s, by - 300 * s), R(x + m * 218 * s, by - 215 * s), R(x + m * 110 * s, by - 215 * s)], (190, 226, 240), TINTA, 5)
    fx, fy = R(x + m * 338 * s, by - 150 * s)
    K.circulo(L, fx, fy, 20 * s, C["amarillo"], TINTA, 4)
    for dx in (-230, 230):
        wx, wy = x + m * dx * s, y - 62 * s - abs(math.sin(t * 17 + dx)) * 12 * s * salta
        K.circulo(L, wx, wy, 66 * s, (44, 40, 40), TINTA, 6)
        K.circulo(L, wx, wy, 26 * s, C["metal"], TINTA, 4)
        a = t * 14 * m
        K.linea(L, [(wx - math.cos(a) * 22 * s, wy - math.sin(a) * 22 * s), (wx + math.cos(a) * 22 * s, wy + math.sin(a) * 22 * s)], TINTA, 6 * s)
    return R(x - m * 140 * s, by - 150 * s), rot      # dónde se para el artillero


def reja(L, x, y0, y1, n=7, caida=1.0):
    """Reja de madera y alambre que cruza el cuadro en vertical desde x (vista de lado). caida 0..1 = baja desde arriba."""
    off = -(1 - caida) * 1500
    for i in range(n):
        px = x + (i - n // 2) * 150
        K.caja_red(L, px - 20, y0 + off, px + 20, y1 + off, 8, C["madera"], TINTA, 6)
        K.poligono(L, [(px - 20, y0 + off), (px, y0 - 40 + off), (px + 20, y0 + off)], C["madera"], TINTA, 6)
    for j in range(6):
        yy = y0 + 60 + j * (y1 - y0 - 100) / 5 + off
        K.linea(L, [(x - n // 2 * 150 - 80, yy), (x + n // 2 * 150 + 80, yy)], TINTA, 9)
        K.linea(L, [(x - n // 2 * 150 - 80, yy), (x + n // 2 * 150 + 80, yy)], (190, 194, 200), 4)


def bala(L, x, y, s=1.0, ang=0.0):
    c, sn = math.cos(ang), math.sin(ang)
    def R(dx, dy):
        return (x + (dx * c - dy * sn) * s, y + (dx * sn + dy * c) * s)
    K.poligono(L, [R(-40, -14), R(14, -14), R(40, 0), R(14, 14), R(-40, 14)], (226, 180, 80), TINTA, 4)
    K.poligono(L, [R(-40, -14), R(-24, -14), R(-24, 14), R(-40, 14)], (180, 130, 60), TINTA, 3)


def estrella_golpe(L, x, y, r, color=None, n=10, texto=None, tam=70, rot=0.0):
    pts = []
    for i in range(n * 2):
        an = i * math.pi / n + rot
        rr = r if i % 2 == 0 else r * 0.62
        pts.append((x + math.cos(an) * rr, y + math.sin(an) * rr))
    K.poligono(L, pts, color or C["amarillo"], TINTA, 7)
    if texto:
        K.texto(L, texto, x, y, tam, TINTA)


def globo(L, x0, y0, x1, y1, punta, color=None):
    """Globo de diálogo (caja redondeada + punta hacia `punta`)."""
    cx = (x0 + x1) / 2
    K.poligono(L, [(cx - 50, y1 - 10), (cx + 50, y1 - 10), punta], color or C["blanco"], TINTA, 7)
    K.caja_red(L, x0, y0, x1, y1, 60, color or C["blanco"], TINTA, 7)
    K.poligono(L, [(cx - 43, y1 - 14), (cx + 43, y1 - 14), (punta[0] + (cx - punta[0]) * 0.12, punta[1] - (punta[1] - y1) * 0.12)], color or C["blanco"])


def marcador(L, cx, cy, s=1.0, izq="0", der="1", u_izq=1.0, u_der=1.0):
    """Marcador de estadio: EJÉRCITO | EMÚS."""
    w, h = 900 * s, 420 * s
    K.caja_red(L, cx - w / 2 + 10, cy - h / 2 + 14, cx + w / 2 + 10, cy + h / 2 + 14, 40 * s, (0, 0, 0, 80))
    K.caja_red(L, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 40 * s, (36, 40, 60), TINTA, 8)
    K.linea(L, [(cx, cy - h / 2 + 30 * s), (cx, cy + h / 2 - 30 * s)], (90, 96, 120), 8 * s)
    K.texto(L, "EJÉRCITO", cx - w / 4, cy - h / 2 + 76 * s, 60 * s, C["blanco"])
    K.texto(L, "EMÚS", cx + w / 4, cy - h / 2 + 76 * s, 60 * s, C["amarillo"])
    if u_izq > 0:
        K.texto(L, izq, cx - w / 4, cy + 50 * s, 250 * s * u_izq, C["blanco"])
    if u_der > 0:
        K.texto(L, der, cx + w / 4, cy + 50 * s, 250 * s * u_der, C["amarillo"])


# ------------------------------------------------------------------ Ep. 12: el oso
BRONCE = {"oso": (124, 156, 136), "oso2": (92, 122, 104), "oso3": (150, 180, 160), "nariz": (60, 84, 72), "gorra": (92, 122, 104), "tinta": (44, 62, 54), "ojo": (60, 84, 72)}


def _brazo(L, sx, sy, ang, largo, k, mira, col, tinta, grosor=62):
    a = math.radians(ang)
    codo = (sx + mira * math.sin(a) * largo * 0.55, sy + math.cos(a) * largo * 0.55)
    mano = (sx + mira * math.sin(a) * largo, sy + math.cos(a) * largo)
    K.linea(L, [(sx, sy), codo, mano], tinta, (grosor + 14) * k)
    K.linea(L, [(sx, sy), codo, mano], col, grosor * k)
    K.circulo(L, mano[0], mano[1], (grosor * 0.62) * k, col, tinta, 6)
    return mano


def oso(L, x, y, alto=900, t=0.0, mira=1, brazo_der=10, brazo_izq=10, gorra=True, ojos="normal", boca=0.0, camina=0.0, galones=False,
        tono=None, cabezon=1.0, saludo=0.0, fase=0.0, lengua=False):
    """Oso pardo de caricatura, de pie en dos patas, con los pies en (x, y). Brazos: 0 = abajo, 90 = al frente, 180 = arriba.
    saludo 0..1 = lleva la mano derecha a la frente. ojos: normal | feliz | susto | triste | serio. tono = paleta alternativa (estatua)."""
    P_ = dict(oso=C["oso"], oso2=C["oso2"], oso3=C["oso3"], nariz=C["nariz"], gorra=C["oliva2"], tinta=TINTA, ojo=TINTA)
    if tono:
        P_.update(tono)
    ti = P_["tinta"]
    k = alto / 900.0
    s = mira
    ph = t * camina * 9 + fase
    bob = abs(math.sin(ph)) * 22 * k if camina else math.sin(t * 2.4 + fase) * 5 * k
    bal = math.sin(ph) * 14 * k if camina else 0
    x = x + bal
    cy = y - 400 * k - bob                          # centro del cuerpo
    # patas traseras
    for i, sg in enumerate((-1, 1)):
        lift = max(0.0, math.sin(ph + (0 if sg < 0 else math.pi))) * 46 * k if camina else 0
        px = x + sg * 100 * k
        K.caja_red(L, px - 70 * k, cy + 150 * k, px + 70 * k, y - lift, 60 * k, P_["oso2"], ti, 7)
        K.elipse(L, px + s * 22 * k, y - 26 * k - lift, 92 * k, 40 * k, P_["oso2"], ti, 7)
    # brazo de atrás
    hom_y = cy - 150 * k
    _brazo(L, x - s * 150 * k, hom_y, brazo_izq, 300 * k, k, s, P_["oso2"], ti)
    # cuerpo (pera) y panza
    K.elipse(L, x, cy + 40 * k, 220 * k, 270 * k, P_["oso"], ti, 8)
    K.elipse(L, x, cy - 120 * k, 180 * k, 180 * k, P_["oso"], ti, 8)
    K.elipse(L, x, cy - 30 * k, 190 * k, 200 * k, P_["oso"])
    K.elipse(L, x + s * 20 * k, cy + 70 * k, 140 * k, 180 * k, P_["oso3"])
    # cabeza
    hx, hy = x + s * 16 * k, cy - 360 * k - 30 * k * (cabezon - 1)
    rh = 150 * k * cabezon
    for sg in (-1, 1):
        K.circulo(L, hx + sg * rh * 0.78, hy - rh * 0.72, rh * 0.36, P_["oso"], ti, 7)
        K.circulo(L, hx + sg * rh * 0.78, hy - rh * 0.72, rh * 0.18, P_["oso3"])
    K.circulo(L, hx, hy, rh, P_["oso"], ti, 8)
    mx, my = hx + s * rh * 0.22, hy + rh * 0.34
    K.elipse(L, mx, my, rh * 0.56, rh * 0.42, P_["oso3"], ti, 6)
    K.elipse(L, mx + s * rh * 0.08, my - rh * 0.2, rh * 0.2, rh * 0.14, P_["nariz"], ti, 4)
    ab = rh * 0.3 * clamp(boca)
    if ab > rh * 0.03:
        K.elipse(L, mx, my + rh * 0.14, rh * 0.2, ab * 0.6 + rh * 0.04, (120, 44, 44) if not tono else P_["nariz"], ti, 4)
        if lengua:
            K.elipse(L, mx, my + rh * 0.2 + ab * 0.3, rh * 0.12, rh * 0.1, (240, 120, 130), ti, 3)
    else:
        L.d.arc((L.S(mx - rh * 0.2), L.S(my - rh * 0.06), L.S(mx + rh * 0.2), L.S(my + rh * 0.24)), 20, 160, fill=ti, width=int(L.S(6 * k * cabezon)))
    for i, sg in enumerate((-1, 1)):
        ox, oy = hx + s * rh * 0.16 + sg * rh * 0.36, hy - rh * 0.14
        r = rh * 0.13
        if ojos == "feliz":
            L.d.arc((L.S(ox - r * 1.3), L.S(oy - r), L.S(ox + r * 1.3), L.S(oy + r * 1.4)), 190, 350, fill=ti, width=int(L.S(8 * k * cabezon)))
        elif ojos == "susto":
            K.circulo(L, ox, oy, r * 1.7, C["blanco"] if not tono else P_["oso3"], ti, 5)
            K.circulo(L, ox, oy, r * 0.6, P_["ojo"])
        else:
            K.circulo(L, ox, oy, r, P_["ojo"])
            if not tono:
                K.circulo(L, ox + r * 0.3, oy - r * 0.3, r * 0.32, C["blanco"])
            if ojos == "triste":
                K.linea(L, [(ox - sg * r * 1.6, oy - r * 2.4), (ox + sg * r * 1.2, oy - r * 1.6)], ti, 7 * k * cabezon)
            if ojos == "serio":
                K.linea(L, [(ox - sg * r * 1.6, oy - r * 1.5), (ox + sg * r * 1.2, oy - r * 2.3)], ti, 8 * k * cabezon)
    if gorra:                                       # gorra de cuartel
        K.poligono(L, [(hx - rh * 0.74, hy - rh * 0.74), (hx - rh * 0.5, hy - rh * 1.24), (hx + rh * 0.56, hy - rh * 1.3), (hx + rh * 0.8, hy - rh * 0.7)], P_["gorra"], ti, 7)
        K.linea(L, [(hx - rh * 0.6, hy - rh * 0.86), (hx + rh * 0.66, hy - rh * 0.84)], ti, 6 * k)
        K.circulo(L, hx + s * rh * 0.2, hy - rh * 1.02, rh * 0.1, C["amarillo"] if not tono else P_["oso3"], ti, 4)
    # brazo de adelante
    ang = brazo_der + (150 - brazo_der) * suave(saludo)
    sx_ = x + s * 150 * k
    if saludo > 0.02:
        a = math.radians(ang)
        codo = (sx_ + s * 150 * k, hom_y + 20 * k - 90 * k * suave(saludo))
        mano = (hx + s * rh * 0.86, hy - rh * 0.5)
        mano = (codo[0] + (mano[0] - codo[0]) * suave(saludo), codo[1] + (mano[1] - codo[1]) * suave(saludo) + (1 - suave(saludo)) * 200 * k)
        K.linea(L, [(sx_, hom_y), codo, mano], ti, 76 * k)
        K.linea(L, [(sx_, hom_y), codo, mano], P_["oso"], 62 * k)
        K.circulo(L, mano[0], mano[1], 40 * k, P_["oso"], ti, 6)
        mano_d = mano
    else:
        mano_d = _brazo(L, sx_, hom_y, brazo_der, 300 * k, k, s, P_["oso"], ti)
    if galones:                                     # dos galones de cabo
        gx, gy = sx_ + s * 6 * k, hom_y + 60 * k
        for j in range(2):
            K.linea(L, [(gx - 36 * k, gy + j * 30 * k), (gx, gy + 24 * k + j * 30 * k), (gx + 36 * k, gy + j * 30 * k)], ti, 22 * k)
            K.linea(L, [(gx - 36 * k, gy + j * 30 * k), (gx, gy + 24 * k + j * 30 * k), (gx + 36 * k, gy + j * 30 * k)], C["amarillo"], 11 * k)
    return {"cabeza": (hx, hy), "rh": rh, "mano": mano_d, "hombro": (sx_, hom_y), "cy": cy}


def caja_muni(L, cx, cy, s=1.0, rot=0.0):
    """Caja de madera de municiones (vista de frente), centro en (cx, cy)."""
    w, h = 300 * s, 190 * s
    def R(dx, dy):
        return (cx + dx * math.cos(rot) - dy * math.sin(rot), cy + dx * math.sin(rot) + dy * math.cos(rot))
    K.poligono(L, [R(-w / 2, -h / 2), R(w / 2, -h / 2), R(w / 2, h / 2), R(-w / 2, h / 2)], C["madera"], TINTA, 7)
    for dy in (-h * 0.18, h * 0.18):
        K.linea(L, [R(-w / 2 + 8 * s, dy), R(w / 2 - 8 * s, dy)], (140, 96, 56), 7 * s)
    for dx in (-w * 0.36, w * 0.36):
        K.poligono(L, [R(dx - 14 * s, -h / 2), R(dx + 14 * s, -h / 2), R(dx + 14 * s, h / 2), R(dx - 14 * s, h / 2)], (140, 96, 56), TINTA, 4)
    for i in range(3):                              # puntas de proyectil pintadas
        px = (-60 + i * 60) * s
        K.poligono(L, [R(px - 16 * s, 30 * s), R(px - 16 * s, -14 * s), R(px, -44 * s), R(px + 16 * s, -14 * s), R(px + 16 * s, 30 * s)], C["amarillo"], TINTA, 4)


def proyectil(L, cx, cy, s=1.0, rot=0.0, color=None):
    def R(dx, dy):
        return (cx + dx * math.cos(rot) - dy * math.sin(rot), cy + dx * math.sin(rot) + dy * math.cos(rot))
    K.poligono(L, [R(-50 * s, 120 * s), R(-50 * s, -60 * s), R(-30 * s, -120 * s), R(0, -150 * s), R(30 * s, -120 * s), R(50 * s, -60 * s), R(50 * s, 120 * s)], color or C["amarillo"], TINTA, 6)
    K.poligono(L, [R(-50 * s, 120 * s), R(-50 * s, 80 * s), R(50 * s, 80 * s), R(50 * s, 120 * s)], (200, 130, 60) if not color else color, TINTA, 5)


def montes(L, horizonte, t=0.0, nieve=True, c1=None, c2=None):
    random.seed(4)
    for capa, (col, alto_, n) in enumerate(((c2 or C["monte2"], 520, 4), (c1 or C["monte"], 380, 5))):
        for i in range(n):
            cx = (i + 0.5) * W / n + random.uniform(-70, 70)
            h = alto_ * random.uniform(0.7, 1.0)
            w = W / n * random.uniform(1.1, 1.5)
            K.poligono(L, [(cx - w / 2, horizonte), (cx - w * 0.08, horizonte - h), (cx + w * 0.1, horizonte - h * 0.92), (cx + w / 2, horizonte)], col, TINTA, 6)
            if nieve:
                K.poligono(L, [(cx - w * 0.16, horizonte - h * 0.78), (cx - w * 0.08, horizonte - h), (cx + w * 0.1, horizonte - h * 0.92), (cx + w * 0.18, horizonte - h * 0.74),
                               (cx + w * 0.06, horizonte - h * 0.8), (cx - w * 0.03, horizonte - h * 0.72)], C["nieve"], TINTA, 5)


def iran(L, horizonte=1200, t=0.0):
    K.cielo_bandas(L, [(255, 214, 150), (255, 226, 176), (255, 238, 204)], 0, horizonte)
    K.circulo(L, 930, 520, 90, (255, 244, 200), TINTA, 6)
    montes(L, horizonte, t)
    L.d.rectangle((0, L.S(horizonte), L.S(W), L.S(H)), fill=C["arena"])
    L.d.line([L.pt(0, horizonte), L.pt(W, horizonte)], fill=TINTA, width=int(L.S(7)))
    random.seed(9)
    for i in range(14):
        x, y = random.uniform(0, W), random.uniform(horizonte + 50, H)
        K.linea(L, [(x, y), (x + random.uniform(50, 130), y)], C["arena2"], 8)


def campamento(L, horizonte=1200, t=0.0):
    iran(L, horizonte, t)
    for x, s in ((220, 1.0), (880, 0.8)):           # carpas
        K.poligono(L, [(x - 210 * s, horizonte + 40), (x, horizonte - 240 * s), (x + 210 * s, horizonte + 40)], C["oliva"], TINTA, 7)
        K.poligono(L, [(x - 50 * s, horizonte + 40), (x, horizonte - 120 * s), (x + 50 * s, horizonte + 40)], C["oliva2"], TINTA, 5)


def barco(L, x, y, s=1.0, t=0.0):
    """Barco de transporte de costado; (x, y) = centro de la línea de flotación."""
    by = y + math.sin(t * 2) * 8 * s
    K.poligono(L, [(x - 520 * s, by - 190 * s), (x + 560 * s, by - 190 * s), (x + 450 * s, by + 40 * s), (x - 440 * s, by + 40 * s)], C["casco_b"], TINTA, 8)
    K.poligono(L, [(x - 445 * s, by - 20 * s), (x + 478 * s, by - 20 * s), (x + 450 * s, by + 40 * s), (x - 440 * s, by + 40 * s)], C["rojo"], TINTA, 6)
    K.caja_red(L, x - 300 * s, by - 330 * s, x + 260 * s, by - 190 * s, 14 * s, C["blanco"], TINTA, 7)
    for i in range(5):
        K.circulo(L, x - 220 * s + i * 105 * s, by - 262 * s, 26 * s, (150, 210, 236), TINTA, 5)
    for dx in (-110, 90):
        K.caja_red(L, x + dx * s - 50 * s, by - 500 * s, x + dx * s + 50 * s, by - 330 * s, 8 * s, C["amarillo"], TINTA, 7)
        K.caja_red(L, x + dx * s - 50 * s, by - 500 * s, x + dx * s + 50 * s, by - 456 * s, 8 * s, TINTA)
        for j in range(3):
            u = (t * 0.5 + j / 3) % 1.0
            K.circulo(L, x + dx * s - u * 200 * s, by - 540 * s - u * 240 * s, (30 + 60 * u) * s, (255, 255, 255, int(220 * (1 - u))))


def puerto(L, t=0.0, mar_y=1100):
    K.cielo_bandas(L, [C["cielo"], C["cielo2"], C["cielo3"]], 0, mar_y)
    nube(L, 240, 260, 0.9); nube(L, 860, 420, 0.7)
    L.d.rectangle((0, L.S(mar_y), L.S(W), L.S(H)), fill=C["mar"])
    for i in range(7):
        y = mar_y + 40 + i * 44
        for j in range(5):
            x = (j * 260 + i * 90 + t * 40) % (W + 200) - 100
            L.d.arc((L.S(x), L.S(y), L.S(x + 120), L.S(y + 40)), 200, 340, fill=C["mar2"], width=int(L.S(7)))


def muelle(L, y=1500):
    L.d.rectangle((0, L.S(y), L.S(W), L.S(H)), fill=(170, 150, 128))
    L.d.line([L.pt(0, y), L.pt(W, y)], fill=TINTA, width=int(L.S(8)))
    for i in range(8):
        L.d.line([L.pt(i * 160 + 40, y), L.pt(i * 160 + 40, H)], fill=(146, 128, 108), width=int(L.S(7)))


def batalla(L, horizonte=1220, t=0.0):
    K.cielo_bandas(L, [C["ocaso3"], C["ocaso2"], C["ocaso"], (255, 206, 130)], 0, horizonte)
    # cerro con el monasterio en ruinas
    K.poligono(L, [(380, horizonte), (640, horizonte - 520), (860, horizonte - 560), (1180, horizonte)], (96, 70, 92), TINTA, 7)
    K.caja_red(L, 650, horizonte - 660, 860, horizonte - 550, 6, (150, 128, 130), TINTA, 6)
    K.poligono(L, [(650, horizonte - 660), (690, horizonte - 720), (730, horizonte - 660)], (150, 128, 130), TINTA, 5)
    for i in range(3):
        K.caja_red(L, 676 + i * 60, horizonte - 630, 700 + i * 60, horizonte - 590, 4, (70, 50, 70))
    K.poligono(L, [(-100, horizonte), (120, horizonte - 300), (420, horizonte - 220), (640, horizonte)], (118, 86, 104), TINTA, 7)
    for i in range(3):                              # humo
        for j in range(4):
            u = (t * 0.25 + j / 4 + i * 0.3) % 1.0
            K.circulo(L, 300 + i * 300 + math.sin(u * 5 + i) * 40, horizonte - 250 - i * 90 - u * 420, 40 + 70 * u, (70, 58, 76, int(170 * (1 - u))))
    for i in range(3):                              # fogonazos lejanos
        u = (t * 1.3 + i * 0.37) % 1.0
        if u < 0.12:
            estrella_golpe(L, 180 + i * 330, horizonte - 120 - i * 60, 70 + 200 * u, (255, 236, 150), 8)
    L.d.rectangle((0, L.S(horizonte), L.S(W), L.S(H)), fill=C["campo"])
    L.d.line([L.pt(0, horizonte), L.pt(W, horizonte)], fill=TINTA, width=int(L.S(7)))
    random.seed(12)
    for i in range(14):
        x, y = random.uniform(0, W), random.uniform(horizonte + 50, H)
        K.linea(L, [(x, y), (x + random.uniform(50, 130), y)], C["campo2"], 8)


def pradera(L, horizonte=1200, t=0.0):
    K.cielo_bandas(L, [C["cielo"], C["cielo2"], C["cielo3"]], 0, horizonte)
    nube(L, (200 + t * 12) % 1300 - 100, 280, 1.0); nube(L, 820, 460, 0.7)
    for cx, w, h, col in ((200, 900, 260, C["pasto2"]), (860, 900, 200, C["pasto2"])):
        K.elipse(L, cx, horizonte + 30, w / 2, h, col, TINTA, 6)
    L.d.rectangle((0, L.S(horizonte), L.S(W), L.S(H)), fill=C["pasto"])
    L.d.line([L.pt(0, horizonte), L.pt(W, horizonte)], fill=TINTA, width=int(L.S(7)))
    random.seed(15)
    for i in range(18):
        x, y = random.uniform(0, W), random.uniform(horizonte + 40, H)
        K.linea(L, [(x, y), (x - 8, y - 30)], C["pasto2"], 8); K.linea(L, [(x + 14, y), (x + 20, y - 26)], C["pasto2"], 8)


def libreta(L, cx, cy, s=1.0, rot=0.0, foto=True, t=0.0):
    """Libreta militar abierta con la foto del oso."""
    w, h = 760 * s, 520 * s
    K.caja_red(L, cx - w / 2 + 10, cy - h / 2 + 14, cx + w / 2 + 10, cy + h / 2 + 14, 26 * s, (0, 0, 0, 70))
    K.caja_red(L, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 26 * s, C["papel"], TINTA, 8)
    K.caja_red(L, cx - w / 2, cy - h / 2, cx + w / 2, cy - h / 2 + 90 * s, 26 * s, C["oliva2"], TINTA, 8)
    K.texto(L, "LIBRETA MILITAR", cx, cy - h / 2 + 46 * s, 46 * s, C["papel"])
    fx0, fy0 = cx - w / 2 + 40 * s, cy - h / 2 + 130 * s
    K.caja_red(L, fx0, fy0, fx0 + 260 * s, fy0 + 330 * s, 10 * s, (200, 220, 230), TINTA, 6)
    if foto:
        oso(L, fx0 + 130 * s, fy0 + 384 * s, alto=300 * s, t=0, gorra=True, cabezon=1.5)
        K.caja_red(L, fx0 - 6 * s, fy0 + 333 * s, fx0 + 270 * s, fy0 + 386 * s, 0, C["papel"])
        K.caja_red(L, fx0, fy0, fx0 + 260 * s, fy0 + 330 * s, 10 * s, None, TINTA, 6)
    return (cx + 40 * s, cy - h / 2 + 130 * s)      # esquina donde van los renglones


def sello(L, cx, cy, texto, s=1.0, rot=-0.15, u=1.0, color=None):
    """Timbre de goma que cae (u 0..1)."""
    col = color or C["sello"]
    esc = 1 + (1 - clamp(u)) * 1.6
    w = (len(texto) * 46 + 80) * s * esc
    h = 120 * s * esc
    def R(dx, dy):
        return (cx + dx * math.cos(rot) - dy * math.sin(rot), cy + dx * math.sin(rot) + dy * math.cos(rot))
    K.poligono(L, [R(-w / 2, -h / 2), R(w / 2, -h / 2), R(w / 2, h / 2), R(-w / 2, h / 2)], C["papel"], col, 12 * s)
    K.texto(L, texto, cx, cy, 74 * s * esc, col)
