"""Ep. 15 — Las cosquillas (el tipo, sus manos y las de otro, el cerebro, el volumen, el robot); incluye el arte de los Ep. 11–14.
Antes: Ep. 14 — La tarjeta sin batería (tarjeta, bobina, chip, máquina de pago); incluye el arte de los Ep. 11–13.
Antes: Ep. 13 — La pantalla táctil (el dedo, el celular, los electrones, el chip, la salchicha); incluye el arte de los Ep. 11 y 12.
Antes: Ep. 12 — El oso soldado. Personajes y objetos 2D de comedia (PIL, sobre studio/plantilla/kit2d.py); parte del arte del Ep. 11.
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
    "menta": (176, 232, 214), "menta2": (140, 214, 192), "coral": (255, 122, 100), "morado": (104, 84, 190), "morado2": (76, 60, 150),
    "cel": (52, 56, 76), "cel2": (36, 38, 54), "pant": (60, 110, 220), "pant2": (40, 78, 170), "vidrio": (190, 232, 250), "dedo": (248, 190, 150),
    "dedo2": (226, 160, 122), "una": (255, 226, 214), "elec": (255, 214, 60), "elec2": (240, 170, 30), "chip": (46, 50, 62), "lana": (220, 70, 80),
    "lana2": (180, 44, 60), "agua": (110, 190, 250), "agua2": (70, 150, 230), "salch": (232, 120, 96), "salch2": (200, 88, 70), "nieve2": (226, 240, 250),
    "tarj": (38, 150, 160), "tarj2": (28, 118, 130), "tarj3": (90, 196, 200), "oro": (246, 196, 80), "oro2": (214, 156, 50), "cobre": (214, 130, 70),
    "maq": (70, 74, 96), "maq2": (48, 50, 68), "maqp": (150, 226, 190), "crema": (255, 240, 214), "crema2": (250, 224, 186), "cielo4": (180, 214, 255),
    "cielo5": (150, 190, 246), "rosa": (255, 170, 190), "rosa2": (246, 140, 170), "cuero": (150, 92, 60), "cuero2": (120, 70, 46),
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


def barco(L, x, y, s=1.0, t=0.0, humo=True):
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
        for j in range(3 if humo else 0):
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


def batalla(L, horizonte=1220, t=0.0, fogonazos=False):
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
        if fogonazos and u < 0.12:
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


# ------------------------------------------------------------------ Ep. 13: pantalla táctil
def fondo_puntos(L, c1, c2, t=0.0, paso=120):
    """Fondo liso con lunares que se mueven lento."""
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=c1)
    off = (t * 24) % paso
    for j in range(-1, H // paso + 2):
        for i in range(-1, W // paso + 2):
            K.circulo(L, i * paso + (paso / 2 if j % 2 else 0) + off, j * paso + off, 16, c2)


def electron(L, x, y, r=34, t=0.0, cara="feliz", fase=0.0, brillo=1.0):
    """Electrón de caricatura: bolita amarilla con cara. cara: feliz | susto | dormido | nada."""
    yy = y + math.sin(t * 5 + fase) * r * 0.12
    if brillo > 0:
        K.circulo(L, x, yy, r * 1.5, (255, 236, 150, int(90 * brillo)))
    K.circulo(L, x, yy, r, C["elec"], TINTA, max(3, r * 0.14))
    if cara == "nada" or r < 14:
        return
    for sg in (-1, 1):
        ox = x + sg * r * 0.34
        if cara == "susto":
            K.circulo(L, ox, yy - r * 0.1, r * 0.24, C["blanco"], TINTA, 2)
            K.circulo(L, ox, yy - r * 0.1, r * 0.09, TINTA)
        elif cara == "dormido":
            K.linea(L, [(ox - r * 0.16, yy - r * 0.08), (ox + r * 0.16, yy - r * 0.08)], TINTA, r * 0.1)
        else:
            K.circulo(L, ox, yy - r * 0.12, r * 0.11, TINTA)
    if cara == "susto":
        K.elipse(L, x, yy + r * 0.4, r * 0.16, r * 0.2, TINTA)
    elif cara == "feliz":
        L.d.arc((L.S(x - r * 0.3), L.S(yy + r * 0.0), L.S(x + r * 0.3), L.S(yy + r * 0.5)), 20, 160, fill=TINTA, width=int(L.S(max(2, r * 0.1))))


def rayo(L, x, y, s=1.0, color=None, rot=0.0):
    pts = [(-20, -80), (30, -80), (6, -16), (40, -16), (-26, 84), (-6, 10), (-40, 10)]
    c, sn = math.cos(rot), math.sin(rot)
    K.poligono(L, [(x + (px * c - py * sn) * s, y + (px * sn + py * c) * s) for px, py in pts], color or C["elec"], TINTA, 5)


def celular(L, cx, cy, w=560, h=1100, cara="normal", t=0.0, rejilla=0.0, n=(5, 9), pantalla=None, temblor=0.0, apagada=False, marca=None,
            electrones=True, falta=None, loca=0.0, mira=(0, 0)):
    """Celular de frente. rejilla 0..1 = aparece la rejilla con un electrón en cada cruce. marca = (i, j) cruce resaltado.
    falta = {(i, j): u} electrones que se fueron (u 0..1). cara: normal | susto | feliz | dormido | enojo | nada | amor.
    Devuelve dict con la caja de la pantalla y la función punto(i, j)."""
    cx = cx + math.sin(t * 60) * 7 * temblor
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    K.caja_red(L, x0 + 12, y0 + 18, x1 + 12, y1 + 18, w * 0.14, (0, 0, 0, 70))
    K.caja_red(L, x0, y0, x1, y1, w * 0.14, C["cel"], TINTA, 9)
    m = w * 0.06
    px0, py0, px1, py1 = x0 + m, y0 + m * 1.6, x1 - m, y1 - m * 1.6
    col = pantalla or (C["cel2"] if apagada else C["pant"])
    if loca > 0:
        col = [(255, 122, 100), (255, 214, 60), (110, 220, 140), (150, 110, 240)][int(t * 3) % 4]
    K.caja_red(L, px0, py0, px1, py1, w * 0.08, col, TINTA, 6)
    K.caja_red(L, cx - w * 0.1, y0 + m * 0.55, cx + w * 0.1, y0 + m * 1.0, m * 0.2, C["cel2"])
    nx, ny = n
    def punto(i, j):
        return (px0 + (px1 - px0) * (i + 0.5) / nx, py0 + (py1 - py0) * (j + 0.5) / ny)
    if rejilla > 0:
        a = int(200 * clamp(rejilla))
        for i in range(nx):
            xx = punto(i, 0)[0]
            K.linea(L, [(xx, py0 + 14), (xx, py0 + 14 + (py1 - py0 - 28) * clamp(rejilla * 1.5))], (190, 232, 250, a), 7)
        for j in range(ny):
            yy = punto(0, j)[1]
            K.linea(L, [(px0 + 14, yy), (px0 + 14 + (px1 - px0 - 28) * clamp(rejilla * 1.5), yy)], (190, 232, 250, a), 7)
        if electrones:
            for j in range(ny):
                for i in range(nx):
                    u = clamp(rejilla * 2.2 - (i + j) * 0.08)
                    if u <= 0:
                        continue
                    f = (falta or {}).get((i, j), 0.0)
                    if f >= 1:
                        continue
                    ex, ey = punto(i, j)
                    electron(L, ex, ey, 26 * u * (1 - f), t, "nada" if u < 0.6 else ("susto" if marca and abs(marca[0] - i) + abs(marca[1] - j) <= 1 else "feliz"),
                             fase=i * 1.7 + j, brillo=0.5)
        if marca:
            mx, my = punto(*marca)
            r = 70 + 10 * math.sin(t * 12)
            K.circulo(L, mx, my, r, None, TINTA, 20)
            K.circulo(L, mx, my, r, None, C["coral"], 12)
    if cara != "nada":
        fx, fy = cx + mira[0], py0 + (py1 - py0) * 0.2 + mira[1]
        e = w * 0.13
        for sg in (-1, 1):
            ox = fx + sg * e * 1.4
            if cara == "dormido":
                L.d.arc((L.S(ox - e * 0.6), L.S(fy - e * 0.4), L.S(ox + e * 0.6), L.S(fy + e * 0.5)), 10, 170, fill=C["blanco"], width=int(L.S(9)))
            elif cara == "feliz":
                L.d.arc((L.S(ox - e * 0.6), L.S(fy - e * 0.3), L.S(ox + e * 0.6), L.S(fy + e * 0.7)), 190, 350, fill=C["blanco"], width=int(L.S(10)))
            elif cara == "amor":
                K.circulo(L, ox - e * 0.22, fy - e * 0.1, e * 0.3, C["coral"]); K.circulo(L, ox + e * 0.22, fy - e * 0.1, e * 0.3, C["coral"])
                K.poligono(L, [(ox - e * 0.5, fy), (ox + e * 0.5, fy), (ox, fy + e * 0.62)], C["coral"])
            else:
                rr = e * (0.62 if cara == "susto" else 0.5)
                K.circulo(L, ox, fy, rr, C["blanco"], TINTA, 5)
                K.circulo(L, ox + mira[0] * 0.08, fy + (e * 0.08 if cara == "normal" else 0), rr * (0.34 if cara == "susto" else 0.5), TINTA)
                if cara == "enojo":
                    K.linea(L, [(ox - sg * e * 0.7, fy - e * 0.9), (ox + sg * e * 0.5, fy - e * 0.45)], C["blanco"], 10)
        by = fy + e * 1.5
        if cara == "susto":
            K.elipse(L, fx, by, e * 0.4, e * 0.5 + e * 0.1 * math.sin(t * 20), C["cel2"], C["blanco"], 6)
        elif cara in ("feliz", "amor"):
            L.d.chord((L.S(fx - e * 0.8), L.S(by - e * 0.6), L.S(fx + e * 0.8), L.S(by + e * 0.6)), 0, 180, fill=C["blanco"], outline=TINTA, width=int(L.S(4)))
        elif cara == "dormido":
            K.circulo(L, fx, by, e * 0.18, C["blanco"])
        elif cara == "enojo":
            L.d.arc((L.S(fx - e * 0.6), L.S(by - e * 0.1), L.S(fx + e * 0.6), L.S(by + e * 0.8)), 200, 340, fill=C["blanco"], width=int(L.S(9)))
        else:
            K.linea(L, [(fx - e * 0.5, by), (fx + e * 0.5, by)], C["blanco"], 9)
    return {"caja": (px0, py0, px1, py1), "punto": punto, "cx": cx}


def dedo(L, px, py, ang=200, largo=640, s=1.0, tipo="dedo", cara="normal", antifaz=False, t=0.0, mira=1):
    """Dedo índice de caricatura con la PUNTA en (px, py); el dedo se extiende desde la punta en dirección `ang` (grados, 0 = derecha,
    90 = abajo). tipo: dedo | guante | salchicha. cara: normal | feliz | susto | malo | nada."""
    a = math.radians(ang)
    g = 150 * s
    ux, uy = math.cos(a), math.sin(a)
    cx0, cy0 = px + ux * g * 0.5, py + uy * g * 0.5       # centro de la yema
    bx, by = px + ux * largo * s, py + uy * largo * s
    col, col2 = {"dedo": (C["dedo"], C["dedo2"]), "guante": (C["lana"], C["lana2"]), "salchicha": (C["salch"], C["salch2"])}[tipo]
    K.linea(L, [(cx0, cy0), (bx, by)], TINTA, g + 18)
    K.circulo(L, cx0, cy0, g / 2 + 9, TINTA)
    K.linea(L, [(cx0, cy0), (bx, by)], col, g)
    K.circulo(L, cx0, cy0, g / 2, col)
    nx_, ny_ = -uy, ux                                      # normal
    if tipo == "dedo":
        ux_, uy_ = cx0 + ux * g * 0.05 - nx_ * g * 0.2 * mira, cy0 + uy * g * 0.05 - ny_ * g * 0.2 * mira
        K.elipse(L, ux_, uy_, g * 0.26, g * 0.26, C["una"], TINTA, 4)
        for d in (0.52, 0.6):                               # pliegues del nudillo
            qx, qy = px + ux * largo * s * d, py + uy * largo * s * d
            K.linea(L, [(qx - nx_ * g * 0.3, qy - ny_ * g * 0.3), (qx + nx_ * g * 0.3, qy + ny_ * g * 0.3)], col2, 8 * s)
    elif tipo == "guante":
        for d in range(8):                                  # tejido
            qx, qy = px + ux * (g * 0.3 + d * g * 0.5), py + uy * (g * 0.3 + d * g * 0.5)
            K.linea(L, [(qx - nx_ * g * 0.42, qy - ny_ * g * 0.42), (qx + ux * g * 0.2, qy + uy * g * 0.2), (qx + nx_ * g * 0.42, qy + ny_ * g * 0.42)], col2, 9 * s)
        qx, qy = px + ux * largo * s * 0.8, py + uy * largo * s * 0.8
        K.linea(L, [(qx - nx_ * g * 0.5, qy - ny_ * g * 0.5), (qx + nx_ * g * 0.5, qy + ny_ * g * 0.5)], C["blanco"], 40 * s)
    else:
        qx, qy = px + ux * g * 0.02, py + uy * g * 0.02      # nudo de la salchicha
        K.circulo(L, px - ux * g * 0.06, py - uy * g * 0.06, g * 0.13, col2, TINTA, 4)
        K.linea(L, [(cx0 + nx_ * g * 0.24 + ux * g * 0.2, cy0 + ny_ * g * 0.24 + uy * g * 0.2), (cx0 + nx_ * g * 0.24 + ux * g * 1.6, cy0 + ny_ * g * 0.24 + uy * g * 1.6)], (255, 190, 170), 14 * s)
    if cara != "nada":
        fx, fy = px + ux * g * 1.75, py + uy * g * 1.75
        e = g * 0.17
        for sg in (-1, 1):
            ox, oy = fx + nx_ * sg * e * 1.5, fy + ny_ * sg * e * 1.5
            if cara == "feliz":
                K.circulo(L, ox, oy, e * 0.62, TINTA)
                K.circulo(L, ox + ux * e * 0.5, oy + uy * e * 0.5, e * 0.62, col)
            else:
                K.circulo(L, ox, oy, e * (1.1 if cara == "susto" else 0.9), C["blanco"], TINTA, 4)
                K.circulo(L, ox - ux * e * 0.25, oy - uy * e * 0.25, e * 0.4, TINTA)
        if antifaz:
            K.linea(L, [(fx - nx_ * g * 0.5, fy - ny_ * g * 0.5), (fx + nx_ * g * 0.5, fy + ny_ * g * 0.5)], (30, 30, 36), e * 3.0)
            for sg in (-1, 1):
                ox, oy = fx + nx_ * sg * e * 1.5, fy + ny_ * sg * e * 1.5
                K.circulo(L, ox, oy, e * 0.85, C["blanco"])
                K.circulo(L, ox - ux * e * 0.25, oy - uy * e * 0.25, e * 0.4, TINTA)
        mx, my = fx - ux * g * 0.42, fy - uy * g * 0.42
        if cara == "susto":
            K.circulo(L, mx, my, e * 0.6, (110, 44, 40), TINTA, 3)
        elif cara in ("feliz", "malo"):
            K.linea(L, [(mx - nx_ * e * 1.1, my - ny_ * e * 1.1 + ux * 0), (mx - ux * e * 0.5, my - uy * e * 0.5), (mx + nx_ * e * 1.1, my + ny_ * e * 1.1)], TINTA, 7 * s)
        else:
            K.linea(L, [(mx - nx_ * e * 0.8, my - ny_ * e * 0.8), (mx + nx_ * e * 0.8, my + ny_ * e * 0.8)], TINTA, 7 * s)
    return (bx, by)


def chip(L, x, y, s=1.0, t=0.0, cara="normal", lupa=None):
    """El chip que revisa la rejilla: cuadrado negro con patitas, lentes y (opcional) una lupa hacia `lupa` (x, y)."""
    w = 300 * s
    for i in range(5):
        for sg in (-1, 1):
            px = x - w * 0.36 + i * w * 0.18
            K.caja_red(L, px - 12 * s, y + sg * w * 0.5 - 30 * s, px + 12 * s, y + sg * w * 0.5 + 30 * s, 5 * s, C["metal"], TINTA, 4)
            py = y - w * 0.36 + i * w * 0.18
            K.caja_red(L, x + sg * w * 0.5 - 30 * s, py - 12 * s, x + sg * w * 0.5 + 30 * s, py + 12 * s, 5 * s, C["metal"], TINTA, 4)
    K.caja_red(L, x - w / 2, y - w / 2 + math.sin(t * 4) * 0, x + w / 2, y + w / 2, 30 * s, C["chip"], TINTA, 8)
    K.circulo(L, x - w * 0.34, y - w * 0.34, 12 * s, C["metal"])
    for sg in (-1, 1):
        K.circulo(L, x + sg * 56 * s, y - 20 * s, 46 * s, C["blanco"], C["elec"], 9)
        K.circulo(L, x + sg * 56 * s + (10 * s if lupa else 0), y - 20 * s + (8 * s if lupa else 0), 16 * s, TINTA)
    K.linea(L, [(x - 10 * s, y - 20 * s), (x + 10 * s, y - 20 * s)], C["elec"], 9 * s)
    if cara == "feliz":
        L.d.chord((L.S(x - 44 * s), L.S(y + 40 * s), L.S(x + 44 * s), L.S(y + 100 * s)), 0, 180, fill=C["blanco"], outline=TINTA, width=int(L.S(3)))
    else:
        K.linea(L, [(x - 30 * s, y + 70 * s), (x + 30 * s, y + 70 * s)], C["blanco"], 8 * s)
    if lupa:
        lx, ly = lupa
        K.linea(L, [(x + w * 0.4, y + w * 0.3), (lx, ly)], TINTA, 26 * s)
        K.linea(L, [(x + w * 0.4, y + w * 0.3), (lx, ly)], C["madera"], 14 * s)
        K.circulo(L, lx, ly, 110 * s, (220, 244, 255, 110), TINTA, 12 * s)
        K.circulo(L, lx, ly, 96 * s, None, C["blanco"], 6 * s)


def gota(L, x, y, s=1.0, t=0.0, cara="feliz"):
    K.poligono(L, [(x, y - 150 * s), (x - 70 * s, y - 30 * s), (x + 70 * s, y - 30 * s)], C["agua"], TINTA, 7)
    K.circulo(L, x, y, 84 * s, C["agua"], TINTA, 7)
    K.poligono(L, [(x, y - 140 * s), (x - 62 * s, y - 34 * s), (x + 62 * s, y - 34 * s)], C["agua"])
    K.elipse(L, x - 30 * s, y - 30 * s, 16 * s, 26 * s, (220, 240, 255))
    for sg in (-1, 1):
        K.circulo(L, x + sg * 28 * s, y + 4 * s, 11 * s, TINTA)
    L.d.arc((L.S(x - 26 * s), L.S(y + 10 * s), L.S(x + 26 * s), L.S(y + 50 * s)), 20, 160, fill=TINTA, width=int(L.S(6 * s)))


def nevada(L, t, n=60, semilla=21):
    random.seed(semilla)
    for i in range(n):
        x = random.uniform(0, W)
        v = random.uniform(120, 300)
        y = (random.uniform(0, H) + t * v) % H
        K.circulo(L, x + math.sin(t * 2 + i) * 20, y, random.uniform(6, 14), C["blanco"])


def invierno(L, horizonte=1300, t=0.0):
    K.cielo_bandas(L, [(150, 190, 230), (180, 210, 240), (214, 232, 248)], 0, horizonte)
    for x, w, h in ((180, 240, 620), (440, 200, 820), (700, 260, 540), (960, 220, 720)):      # edificios
        K.caja_red(L, x - w / 2, horizonte - h, x + w / 2, horizonte + 10, 8, (120, 140, 180), TINTA, 6)
        for j in range(int(h // 110)):
            for i in range(2):
                K.caja_red(L, x - w * 0.3 + i * w * 0.36, horizonte - h + 40 + j * 110, x - w * 0.3 + i * w * 0.36 + w * 0.22, horizonte - h + 100 + j * 110, 4, (255, 230, 150))
        K.caja_red(L, x - w / 2 - 10, horizonte - h - 26, x + w / 2 + 10, horizonte - h + 8, 12, C["blanco"], TINTA, 5)
    L.d.rectangle((0, L.S(horizonte), L.S(W), L.S(H)), fill=C["nieve2"])
    L.d.line([L.pt(0, horizonte), L.pt(W, horizonte)], fill=TINTA, width=int(L.S(7)))


# ------------------------------------------------------------------ Ep. 14: tarjeta sin batería
def _bobina_pts(x0, y0, x1, y1, vueltas=4, paso=26, chip=None):
    """Polilínea de una bobina rectangular en espiral, desde afuera hacia adentro, que termina en el chip."""
    pts = []
    a, b, c, d = x0, y0, x1, y1
    pts.append((a, b))
    for i in range(vueltas):
        pts += [(c, b), (c, d), (a, d), (a, b + paso)]
        a += paso; b += paso; c -= paso; d -= paso
        pts.append((a, b))
    if chip:
        pts += [(a, chip[1]), chip]
    return pts


def _parte(pts, u):
    """Devuelve la polilínea recortada a la fracción u (0..1) de su largo."""
    if u >= 1:
        return pts
    largos = [math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(pts, pts[1:])]
    falta = sum(largos) * max(0.0, u)
    out = [pts[0]]
    for (p, q), l in zip(zip(pts, pts[1:]), largos):
        if falta >= l:
            out.append(q); falta -= l
        else:
            k = falta / l if l else 0
            out.append((p[0] + (q[0] - p[0]) * k, p[1] + (q[1] - p[1]) * k)); break
    return out


def chip_cara(L, x, y, r, t=0.0, cara="dormido", brillo=0.0):
    """El chip de la tarjeta: cuadrado dorado con cara. cara: dormido | despierto | feliz | nada."""
    if brillo > 0:
        K.circulo(L, x, y, r * 1.9, (255, 236, 150, int(120 * brillo)))
    K.caja_red(L, x - r, y - r * 0.82, x + r, y + r * 0.82, r * 0.26, C["oro"], TINTA, max(3, r * 0.1))
    for dx in (-0.5, 0.5):
        K.linea(L, [(x + dx * r, y - r * 0.82), (x + dx * r, y - r * 0.5)], C["oro2"], max(2, r * 0.07))
        K.linea(L, [(x + dx * r, y + r * 0.82), (x + dx * r, y + r * 0.5)], C["oro2"], max(2, r * 0.07))
    if cara == "nada" or r < 20:
        return
    for sg in (-1, 1):
        ox, oy = x + sg * r * 0.36, y - r * 0.12
        if cara == "dormido":
            L.d.arc((L.S(ox - r * 0.2), L.S(oy - r * 0.16), L.S(ox + r * 0.2), L.S(oy + r * 0.2)), 10, 170, fill=TINTA, width=int(L.S(max(3, r * 0.08))))
        elif cara == "feliz":
            L.d.arc((L.S(ox - r * 0.2), L.S(oy - r * 0.1), L.S(ox + r * 0.2), L.S(oy + r * 0.3)), 190, 350, fill=TINTA, width=int(L.S(max(3, r * 0.09))))
        else:
            K.circulo(L, ox, oy, r * 0.2, C["blanco"], TINTA, max(2, r * 0.05))
            K.circulo(L, ox, oy, r * 0.08, TINTA)
    if cara == "dormido":
        K.circulo(L, x, y + r * 0.34, r * 0.08, TINTA)
    elif cara == "feliz":
        L.d.chord((L.S(x - r * 0.26), L.S(y + r * 0.1), L.S(x + r * 0.26), L.S(y + r * 0.52)), 0, 180, fill=C["blanco"], outline=TINTA, width=int(L.S(max(2, r * 0.05))))
    else:
        K.elipse(L, x, y + r * 0.36, r * 0.12, r * 0.14, (110, 44, 40), TINTA, max(2, r * 0.04))


def tarjeta(L, cx, cy, w=640, cara="dormido", t=0.0, rayosx=0.0, bobina=1.0, carga=0.0, chip="dormido", temblor=0.0, color=None, simbolo=True):
    """Tarjeta de pago genérica (sin marca), horizontal, centro en (cx, cy). rayosx 0..1 = se ve por dentro (bobina y chip).
    bobina 0..1 = cuánto de la bobina está dibujado; carga 0..1 = cuánto de la bobina va encendido. cara de la tarjeta: dormido | despierto |
    feliz | susto | nada. Devuelve dict con la posición del chip."""
    cx = cx + math.sin(t * 60) * 6 * temblor
    h = w * 0.63
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    k = w / 640.0
    col = color or C["tarj"]
    K.caja_red(L, x0 + 10 * k, y0 + 16 * k, x1 + 10 * k, y1 + 16 * k, 44 * k, (0, 0, 0, 70))
    chipp = (x0 + 150 * k, cy + 6 * k)
    if rayosx <= 0:
        K.caja_red(L, x0, y0, x1, y1, 44 * k, col, TINTA, 8)
        K.poligono(L, [(x0 + w * 0.5, y0 + 6), (x1 - 50 * k, y0 + 6), (x0 + w * 0.26, y1 - 6), (x0 + 30 * k, y1 - 6)], C["tarj3"] if not color else col)
        K.caja_red(L, x0, y0, x1, y1, 44 * k, None, TINTA, 8)
        K.caja_red(L, chipp[0] - 54 * k, chipp[1] - 44 * k, chipp[0] + 54 * k, chipp[1] + 44 * k, 12 * k, C["oro"], TINTA, 5)
        K.linea(L, [(chipp[0] - 54 * k, chipp[1]), (chipp[0] + 54 * k, chipp[1])], C["oro2"], 5 * k)
        K.linea(L, [(chipp[0], chipp[1] - 44 * k), (chipp[0], chipp[1] + 44 * k)], C["oro2"], 5 * k)
        if simbolo:                                 # onditas genéricas de "acércala"
            for i in range(3):
                r = (26 + i * 22) * k
                L.d.arc((L.S(x1 - 120 * k - r), L.S(y0 + 86 * k - r), L.S(x1 - 120 * k + r), L.S(y0 + 86 * k + r)), -50, 50, fill=C["blanco"], width=int(L.S(8 * k)))
        for i in range(4):                          # "números" como rayitas
            K.caja_red(L, x0 + 60 * k + i * 136 * k, y1 - 92 * k, x0 + 60 * k + i * 136 * k + 96 * k, y1 - 70 * k, 8 * k, (255, 255, 255, 150))
    else:
        K.caja_red(L, x0, y0, x1, y1, 44 * k, (col[0], col[1], col[2], int(255 - 150 * clamp(rayosx))), TINTA, 8)
        K.caja_red(L, x0, y0, x1, y1, 44 * k, (20, 60, 80, int(190 * clamp(rayosx))), TINTA, 8)
        pts = _bobina_pts(x0 + 34 * k, y0 + 34 * k, x1 - 34 * k, y1 - 34 * k, 4, 24 * k, chip=chipp)
        p = _parte(pts, bobina)
        if len(p) > 1:
            K.linea(L, p, TINTA, 15 * k)
            K.linea(L, p, C["cobre"], 8 * k)
        if carga > 0:
            pc = _parte(pts, min(bobina, carga))
            if len(pc) > 1:
                K.linea(L, pc, (255, 240, 150, 150), 26 * k)
                K.linea(L, pc, C["elec"], 10 * k)
                K.circulo(L, pc[-1][0], pc[-1][1], 16 * k + 5 * k * math.sin(t * 30), C["blanco"], C["elec"], 5)
        chip_cara(L, chipp[0], chipp[1], 62 * k, t, chip, brillo=1.0 if chip in ("despierto", "feliz") else 0.0)
    if cara != "nada" and rayosx <= 0:
        fx, fy = cx + 120 * k, cy - 6 * k
        e = 34 * k
        for sg in (-1, 1):
            ox = fx + sg * e * 1.5
            if cara == "dormido":
                L.d.arc((L.S(ox - e * 0.7), L.S(fy - e * 0.5), L.S(ox + e * 0.7), L.S(fy + e * 0.6)), 10, 170, fill=C["blanco"], width=int(L.S(9 * k)))
            elif cara == "feliz":
                L.d.arc((L.S(ox - e * 0.7), L.S(fy - e * 0.3), L.S(ox + e * 0.7), L.S(fy + e * 0.9)), 190, 350, fill=C["blanco"], width=int(L.S(10 * k)))
            else:
                rr = e * (0.8 if cara == "susto" else 0.66)
                K.circulo(L, ox, fy, rr, C["blanco"], TINTA, 5)
                K.circulo(L, ox, fy, rr * (0.34 if cara == "susto" else 0.5), TINTA)
        by = fy + e * 1.6
        if cara == "dormido":
            K.circulo(L, fx, by, e * 0.22, C["blanco"])
        elif cara == "feliz":
            L.d.chord((L.S(fx - e), L.S(by - e * 0.7), L.S(fx + e), L.S(by + e * 0.7)), 0, 180, fill=C["blanco"], outline=TINTA, width=int(L.S(4)))
        elif cara == "susto":
            K.elipse(L, fx, by, e * 0.4, e * 0.5, C["tarj2"], C["blanco"], 6)
        else:
            K.linea(L, [(fx - e * 0.6, by), (fx + e * 0.6, by)], C["blanco"], 9 * k)
    return {"chip": chipp, "caja": (x0, y0, x1, y1), "k": k}


def zzz(L, x, y, t, s=1.0, n=3, dir_x=1):
    for i in range(n):
        u = (t * 0.6 + i / n) % 1.0
        tam = (50 + i * 26 + u * 20) * s
        if tam * 2 >= 2:
            K.texto(L, "z", x + dir_x * (i * 50 + u * 40) * s, y - (i * 70 + u * 70) * s, tam, C["blanco"], borde=5, color_borde=TINTA)


def maquina(L, cx, cy, s=1.0, t=0.0, cara="normal", pantalla=None, emite=0.0, temblor=0.0):
    """Máquina de pago genérica, de frente, centro en (cx, cy). emite 0..1 = intensidad de las ondas que salen por arriba.
    cara: normal | feliz | fuerte | nada. Devuelve el punto de donde salen las ondas."""
    cx = cx + math.sin(t * 60) * 5 * temblor
    w, h = 420 * s, 640 * s
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    K.caja_red(L, x0 + 10 * s, y0 + 16 * s, x1 + 10 * s, y1 + 16 * s, 50 * s, (0, 0, 0, 70))
    K.caja_red(L, x0, y0, x1, y1, 50 * s, C["maq"], TINTA, 8)
    K.caja_red(L, x0 + 36 * s, y0 + 40 * s, x1 - 36 * s, y0 + 300 * s, 24 * s, pantalla or C["maqp"], TINTA, 6)
    fx, fy = cx, y0 + 150 * s
    e = 34 * s
    if cara != "nada":
        for sg in (-1, 1):
            ox = fx + sg * e * 1.7
            if cara == "feliz":
                L.d.arc((L.S(ox - e * 0.7), L.S(fy - e * 0.3), L.S(ox + e * 0.7), L.S(fy + e * 0.9)), 190, 350, fill=TINTA, width=int(L.S(10 * s)))
            else:
                K.circulo(L, ox, fy, e * 0.5, TINTA)
                K.circulo(L, ox + e * 0.14, fy - e * 0.16, e * 0.16, C["blanco"])
                if cara == "fuerte":
                    K.linea(L, [(ox - sg * e * 0.9, fy - e * 1.1), (ox + sg * e * 0.6, fy - e * 0.7)], TINTA, 10 * s)
        if cara == "feliz":
            L.d.chord((L.S(fx - e), L.S(fy + e * 0.6), L.S(fx + e), L.S(fy + e * 2.0)), 0, 180, fill=C["blanco"], outline=TINTA, width=int(L.S(4)))
        else:
            L.d.arc((L.S(fx - e * 0.8), L.S(fy + e * 0.5), L.S(fx + e * 0.8), L.S(fy + e * 1.5)), 20, 160, fill=TINTA, width=int(L.S(8 * s)))
    for j in range(3):                              # teclado
        for i in range(3):
            K.caja_red(L, x0 + 60 * s + i * 106 * s, y0 + 350 * s + j * 86 * s, x0 + 60 * s + i * 106 * s + 86 * s, y0 + 350 * s + j * 86 * s + 62 * s, 12 * s,
                       C["maq2"] if not (i == 2 and j == 2) else C["verde"], TINTA, 4)
    sale = (cx, y0 - 6 * s)
    if emite > 0:
        ondas(L, sale[0], sale[1], t, s=s, u=emite)
    return sale


def ondas(L, x, y, t, s=1.0, u=1.0, n=4, ang=(200, 340), color=None, alcance=520):
    """Ondas de energía que salen de (x, y) hacia arriba (arcos que crecen y se apagan)."""
    for i in range(n):
        f = (t * 0.9 + i / n) % 1.0
        r = (60 + alcance * f) * s
        a = int(230 * (1 - f) * clamp(u))
        if a <= 8:
            continue
        col = color or C["elec"]
        L.d.arc((L.S(x - r), L.S(y - r), L.S(x + r), L.S(y + r)), ang[0], ang[1], fill=(TINTA[0], TINTA[1], TINTA[2], a), width=int(L.S(26 * s)))
        L.d.arc((L.S(x - r), L.S(y - r), L.S(x + r), L.S(y + r)), ang[0], ang[1], fill=(col[0], col[1], col[2], a), width=int(L.S(15 * s)))


def bateria(L, cx, cy, s=1.0, nivel=0.7, tachada=0.0):
    w, h = 300 * s, 150 * s
    K.caja_red(L, cx + w / 2, cy - 36 * s, cx + w / 2 + 28 * s, cy + 36 * s, 8 * s, TINTA)
    K.caja_red(L, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 24 * s, C["blanco"], TINTA, 8)
    K.caja_red(L, cx - w / 2 + 18 * s, cy - h / 2 + 18 * s, cx - w / 2 + 18 * s + (w - 36 * s) * nivel, cy + h / 2 - 18 * s, 12 * s, C["verde"])
    if tachada > 0:
        r = 150 * s * tachada
        for sg in (-1, 1):
            K.linea(L, [(cx - r, cy - sg * r * 0.7), (cx + r, cy + sg * r * 0.7)], TINTA, 52 * s * tachada)
        for sg in (-1, 1):
            K.linea(L, [(cx - r, cy - sg * r * 0.7), (cx + r, cy + sg * r * 0.7)], C["rojo"], 34 * s * tachada)


def pila(L, cx, cy, s=1.0, tachada=0.0):
    K.caja_red(L, cx - 60 * s, cy - 130 * s, cx + 60 * s, cy + 130 * s, 22 * s, C["oro"], TINTA, 8)
    K.caja_red(L, cx - 60 * s, cy - 130 * s, cx + 60 * s, cy - 40 * s, 22 * s, C["cel"], TINTA, 8)
    K.caja_red(L, cx - 24 * s, cy - 160 * s, cx + 24 * s, cy - 128 * s, 8 * s, C["metal"], TINTA, 6)
    K.texto(L, "+", cx, cy - 86 * s, 60 * s, C["blanco"])
    if tachada > 0:
        r = 130 * s * tachada
        for sg in (-1, 1):
            K.linea(L, [(cx - r, cy - sg * r), (cx + r, cy + sg * r)], TINTA, 52 * s * tachada)
        for sg in (-1, 1):
            K.linea(L, [(cx - r, cy - sg * r), (cx + r, cy + sg * r)], C["rojo"], 34 * s * tachada)


def mano(L, x, y, s=1.0, color=None, color2=None):
    """Mano de caricatura agarrando algo en (x, y) (el puño queda abajo)."""
    c1, c2 = color or C["dedo"], color2 or C["dedo2"]
    K.caja_red(L, x - 110 * s, y + 60 * s, x + 110 * s, y + 900 * s, 60 * s, c1, TINTA, 8)
    K.circulo(L, x, y, 150 * s, c1, TINTA, 8)
    K.elipse(L, x - 120 * s, y - 60 * s, 62 * s, 96 * s, c1, TINTA, 8)
    K.circulo(L, x, y, 142 * s, c1)
    for i in range(3):
        L.d.arc((L.S(x - 60 * s + i * 56 * s), L.S(y - 110 * s), L.S(x + 10 * s + i * 56 * s), L.S(y - 30 * s)), 200, 340, fill=c2, width=int(L.S(8 * s)))


def cronometro(L, cx, cy, r, u=0.0):
    K.caja_red(L, cx - r * 0.16, cy - r * 1.28, cx + r * 0.16, cy - r * 0.96, r * 0.06, C["metal"], TINTA, 6)
    K.circulo(L, cx, cy, r, C["blanco"], TINTA, 10)
    for i in range(12):
        a = i * math.pi / 6
        K.linea(L, [(cx + math.cos(a) * r * 0.8, cy + math.sin(a) * r * 0.8), (cx + math.cos(a) * r * 0.9, cy + math.sin(a) * r * 0.9)], TINTA, 7)
    a0 = -math.pi / 2
    a1 = a0 + u * 2 * math.pi
    if u > 0.01:
        L.d.pieslice((L.S(cx - r * 0.74), L.S(cy - r * 0.74), L.S(cx + r * 0.74), L.S(cy + r * 0.74)), -90, -90 + u * 360, fill=C["coral"])
    K.linea(L, [(cx, cy), (cx + math.cos(a1) * r * 0.72, cy + math.sin(a1) * r * 0.72)], TINTA, 12)
    K.circulo(L, cx, cy, r * 0.08, TINTA)


def boleta(L, cx, cy, s=1.0, texto="CÓDIGO", rot=0.0, u=1.0, tachada=0.0):
    """Papelito con el código de un solo uso."""
    w, h = 300 * s * u, 150 * s * u
    if w < 6:
        return
    K.caja_red(L, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 14 * s, C["papel"], TINTA, 6)
    K.texto(L, texto, cx, cy - 26 * s * u, 40 * s * u, TINTA)
    for i in range(5):
        K.caja_red(L, cx - 110 * s * u + i * 46 * s * u, cy + 16 * s * u, cx - 110 * s * u + i * 46 * s * u + 30 * s * u, cy + 46 * s * u, 4, [C["coral"], C["morado"], C["verde"], C["elec"], C["cel"]][i])
    if tachada > 0:
        K.linea(L, [(cx - w / 2 - 10, cy), (cx - w / 2 - 10 + (w + 20) * tachada, cy)], C["rojo"], 16 * s)


def billetera(L, cx, cy, s=1.0):
    K.caja_red(L, cx - 330 * s, cy - 200 * s, cx + 330 * s, cy + 220 * s, 40 * s, C["cuero2"], TINTA, 8)
    K.caja_red(L, cx - 330 * s, cy - 110 * s, cx + 330 * s, cy + 220 * s, 40 * s, C["cuero"], TINTA, 8)
    for i in range(12):
        K.linea(L, [(cx - 300 * s + i * 52 * s, cy - 84 * s), (cx - 280 * s + i * 52 * s, cy - 84 * s)], C["crema"], 6 * s)


# ================================================================== Ep. 15 — cosquillas
C.update({
    "polera": (70, 176, 226), "polera2": (46, 140, 192), "pelo": (88, 58, 42), "otro": (156, 92, 214), "otro2": (118, 64, 180),
    "seso": (255, 158, 178), "seso2": (226, 112, 140), "seso3": (255, 200, 212), "robot": (176, 188, 202), "robot2": (124, 136, 156),
    "durazno": (255, 218, 176), "durazno2": (250, 200, 154), "lengua": (240, 110, 120), "boca": (120, 36, 44), "lagrima": (150, 214, 255),
    "noche2": (52, 46, 104), "noche3": (40, 34, 84), "cristal": (176, 226, 255), "cristal2": (120, 190, 240),
})


def _ext(p, ang, d):
    return (p[0] + math.cos(ang) * d, p[1] + math.sin(ang) * d)


def brazo(L, p0, p1, color, grosor=64, doblez=0.22, lado=1):
    """Brazo de dos tramos del hombro p0 a la muñeca p1; el codo sale hacia `lado` (perpendicular)."""
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    d = math.hypot(dx, dy) + 1e-6
    codo = (mx - dy / d * d * doblez * lado, my + dx / d * d * doblez * lado)
    K.miembro(L, [p0, codo, p1], color, grosor)
    return codo


def mano_cosq(L, x, y, ang, s=1.0, t=0.0, mueve=1.0, piel=None, fase=0.0, abierta=1.0):
    """Mano que hace cosquillas: palma en (x, y), dedos hacia `ang` (radianes) moviéndose rápido."""
    pc = piel or C["piel"]
    for i in range(4):
        base_a = ang + (-0.55 + i * 0.37) * abierta
        b = _ext((x, y), base_a, 34 * s)
        w = math.sin(t * 30 + i * 1.7 + fase) * 0.42 * mueve
        f1 = _ext(b, base_a + w, 44 * s)
        f2 = _ext(f1, base_a + w * 1.8 + 0.25 * mueve * math.sin(t * 30 + i), 34 * s)
        K.linea(L, [b, f1, f2], TINTA, 30 * s)
        K.linea(L, [b, f1, f2], pc, 21 * s)
    pul = _ext((x, y), ang - 1.45, 40 * s)
    pul2 = _ext(pul, ang - 0.7 + math.sin(t * 24 + fase) * 0.2 * mueve, 38 * s)
    K.linea(L, [(x, y), pul, pul2], TINTA, 32 * s)
    K.linea(L, [(x, y), pul, pul2], pc, 23 * s)
    K.circulo(L, x, y, 46 * s, pc, TINTA, 6)


def manga(L, p, ang, s, color):
    """Puño de la manga en la muñeca (para que se lea de quién es la mano)."""
    a, b = _ext(p, ang + math.pi / 2, 40 * s), _ext(p, ang - math.pi / 2, 40 * s)
    c, d = _ext(b, ang + math.pi, 40 * s), _ext(a, ang + math.pi, 40 * s)
    K.poligono(L, [a, b, c, d], color, TINTA, 6)


def cara_tipo(L, cx, cy, r, cara="aburrido", t=0.0, mira=0.0):
    """Cabeza del protagonista (pelo café en mechón, orejas, cara según `cara`)."""
    for sg in (-1, 1):
        K.circulo(L, cx + sg * r * 0.97, cy + r * 0.08, r * 0.2, C["piel"], TINTA, 7)
        K.circulo(L, cx + sg * r * 0.97, cy + r * 0.08, r * 0.09, C["piel2"])
    K.circulo(L, cx, cy, r, C["piel"], TINTA, 8)
    # pelo: casquete + mechón
    L.d.chord((L.S(cx - r * 1.02), L.S(cy - r * 1.06), L.S(cx + r * 1.02), L.S(cy + r * 0.5)), 188, 352, fill=C["pelo"], outline=TINTA, width=int(L.S(7)))
    K.poligono(L, [(cx - r * 0.2, cy - r * 0.92), (cx - r * 0.05, cy - r * 1.36), (cx + r * 0.12, cy - r * 0.98), (cx + r * 0.32, cy - r * 1.28), (cx + r * 0.42, cy - r * 0.86)],
               C["pelo"], TINTA, 6)
    ex, ey, ox = r * 0.36, cy - r * 0.02, mira * r * 0.06
    if cara == "risa":
        for sg in (-1, 1):                                   # ojos cerrados de risa (∩)
            L.d.arc((L.S(cx + sg * ex - r * 0.17), L.S(ey - r * 0.16), L.S(cx + sg * ex + r * 0.17), L.S(ey + r * 0.14)), 190, 350, fill=TINTA, width=int(L.S(r * 0.07)))
            K.circulo(L, cx + sg * r * 0.6, cy + r * 0.3, r * 0.14, (255, 140, 140, 150))
        mb = cy + r * 0.38
        L.d.chord((L.S(cx - r * 0.42), L.S(mb - r * 0.22), L.S(cx + r * 0.42), L.S(mb + r * 0.5)), 0, 180, fill=C["boca"], outline=TINTA, width=int(L.S(7)))
        K.caja_red(L, cx - r * 0.34, mb + r * 0.12, cx + r * 0.34, mb + r * 0.2, r * 0.03, C["blanco"])
        K.elipse(L, cx, mb + r * 0.4, r * 0.2, r * 0.1, C["lengua"])
        for sg in (-1, 1):                                   # lágrimas que saltan
            for k in range(2):
                u = (t * 2.4 + k * 0.5 + (sg + 1) * 0.13) % 1.0
                lx = cx + sg * (r * 0.62 + u * r * 0.9)
                ly = ey - r * 0.05 - math.sin(u * math.pi) * r * 0.5 + u * r * 0.6
                K.elipse(L, lx, ly, r * 0.07 * (1 - u * 0.4), r * 0.1 * (1 - u * 0.4), C["lagrima"], TINTA, 4)
    elif cara == "aburrido":
        for sg in (-1, 1):
            K.elipse(L, cx + sg * ex, ey, r * 0.19, r * 0.16, C["blanco"], TINTA, 6)
            K.circulo(L, cx + sg * ex + ox, ey + r * 0.06, r * 0.075, TINTA)
            L.d.chord((L.S(cx + sg * ex - r * 0.2), L.S(ey - r * 0.17), L.S(cx + sg * ex + r * 0.2), L.S(ey + r * 0.17)), 180, 360, fill=C["piel"])
            K.linea(L, [(cx + sg * ex - r * 0.2, ey), (cx + sg * ex + r * 0.2, ey)], TINTA, r * 0.05)
            K.linea(L, [(cx + sg * ex - r * 0.16, ey - r * 0.3), (cx + sg * ex + r * 0.16, ey - r * 0.3)], TINTA, r * 0.06)
        K.linea(L, [(cx - r * 0.2, cy + r * 0.48), (cx + r * 0.22, cy + r * 0.46)], TINTA, r * 0.06)
    else:                                                    # normal / sorpresa / tenso / feliz
        grande = 1.25 if cara in ("sorpresa", "tenso") else 1.0
        for sg in (-1, 1):
            K.elipse(L, cx + sg * ex, ey, r * 0.17 * grande, r * 0.2 * grande, C["blanco"], TINTA, 6)
            K.circulo(L, cx + sg * ex + ox * (2 if cara == "tenso" else 1), ey + r * 0.02, r * (0.06 if cara == "sorpresa" else 0.08), TINTA)
            if cara == "tenso":
                K.linea(L, [(cx + sg * ex - sg * r * 0.16, ey - r * 0.42), (cx + sg * ex + sg * r * 0.16, ey - r * 0.32)], TINTA, r * 0.06)
        if cara == "sorpresa":
            K.elipse(L, cx, cy + r * 0.5, r * 0.13, r * 0.17, C["boca"], TINTA, 6)
        elif cara == "tenso":
            pts = [(cx - r * 0.3 + i * r * 0.1, cy + r * 0.5 + (r * 0.04 if i % 2 else -r * 0.04)) for i in range(7)]
            K.linea(L, pts, TINTA, r * 0.05)
            K.elipse(L, cx + r * 0.86, cy - r * 0.42 + (t * 60 % 30), r * 0.08, r * 0.12, C["lagrima"], TINTA, 4)
        else:
            L.d.arc((L.S(cx - r * 0.3), L.S(cy + r * 0.12), L.S(cx + r * 0.3), L.S(cy + r * 0.6)), 20, 160, fill=TINTA, width=int(L.S(r * 0.06)))


def tipo(L, cx, cy, r=190, t=0.0, cara="aburrido", temblor=0.0, mira=0.0, polera=None):
    """El protagonista de medio cuerpo: cabeza en (cx, cy) de radio r; el torso sigue hasta abajo del cuadro.
    Devuelve los puntos para colgarle brazos: hombros, axilas, costillas y guata."""
    dx = math.sin(t * 47) * 12 * temblor
    dy = abs(math.sin(t * 23)) * -14 * temblor
    cx2 = cx + dx
    pc, pc2 = polera or C["polera"], C["polera2"] if not polera else tuple(max(0, v - 30) for v in polera)
    top = cy + r * 0.86
    K.caja_red(L, cx2 - r * 0.24, cy + r * 0.6, cx2 + r * 0.24, top + r * 0.2, r * 0.08, C["piel2"], TINTA, 6)
    K.caja_red(L, cx2 - r * 1.45, top + r * 3.9, cx2 + r * 1.45, top + r * 9, r * 0.2, (70, 92, 150), TINTA, 8)            # jeans
    K.linea(L, [(cx2, top + r * 4.3), (cx2, top + r * 9)], (50, 68, 120), r * 0.05)
    K.poligono(L, [(cx2 - r * 1.25, top + r * 0.3), (cx2 - r * 0.9, top), (cx2 + r * 0.9, top), (cx2 + r * 1.25, top + r * 0.3), (cx2 + r * 1.45, top + r * 3.95), (cx2 - r * 1.45, top + r * 3.95)], pc, TINTA, 8)
    K.caja_red(L, cx2 - r * 1.45, top + r * 3.85, cx2 + r * 1.45, top + r * 4.1, r * 0.05, C["cuero2"], TINTA, 6)          # cinturón
    K.caja_red(L, cx2 - r * 0.16, top + r * 3.82, cx2 + r * 0.16, top + r * 4.13, r * 0.04, C["oro"], TINTA, 5)
    L.d.chord((L.S(cx2 - r * 0.4), L.S(top - r * 0.22), L.S(cx2 + r * 0.4), L.S(top + r * 0.3)), 0, 180, fill=C["piel2"], outline=TINTA, width=int(L.S(6)))
    for y0 in (1.55, 2.25):                                                                          # franjas de la polera
        a0, a1 = 1.25 + 0.25 * (y0 - 0.3) / 7.7, 1.25 + 0.25 * (y0 + 0.3 - 0.3) / 7.7
        K.poligono(L, [(cx2 - r * a0 + 4, top + r * y0), (cx2 + r * a0 - 4, top + r * y0), (cx2 + r * a1 - 4, top + r * (y0 + 0.3)), (cx2 - r * a1 + 4, top + r * (y0 + 0.3))], pc2)
    cara_tipo(L, cx + dx * 1.3, cy + dy, r, cara, t, mira)
    return {"hom_i": (cx2 - r * 1.12, top + r * 0.35), "hom_d": (cx2 + r * 1.12, top + r * 0.35),
            "axi_i": (cx2 - r * 1.2, top + r * 0.95), "axi_d": (cx2 + r * 1.2, top + r * 0.95),
            "cos_i": (cx2 - r * 1.25, top + r * 1.6), "cos_d": (cx2 + r * 1.25, top + r * 1.6), "guata": (cx2, top + r * 2.2)}


def jaja(L, cx, cy, t, t0, r=360, n=5, tam=86, color=None):
    """'JA' que saltan alrededor de (cx, cy) desde t0."""
    if t < t0:
        return
    e = t - t0
    for i in range(n):
        an = -math.pi / 2 + (i - (n - 1) / 2) * 0.62 + math.sin(t * 9 + i) * 0.05
        u = clamp((e - i * 0.12) / 0.3)
        if u <= 0:
            continue
        rr = r * (0.8 + 0.2 * u) + math.sin(t * 14 + i * 2) * 10
        K.texto(L, "JA", cx + math.cos(an) * rr, cy + math.sin(an) * rr, tam * pop(e - i * 0.12), color or C["amarillo"], borde=7, color_borde=TINTA)


def cerebro(L, cx, cy, r=260, t=0.0, cara="normal", brillo=0.0):
    """El cerebro con cara (lóbulos de nubecita, surcos y cerebelo atrás)."""
    bob = math.sin(t * 2.4) * 6
    cy = cy + bob
    if brillo > 0:
        for i in range(3):
            K.circulo(L, cx, cy, r * (1.35 + i * 0.16), (255, 240, 160, int(70 * brillo / (i + 1))))
    lobs = [(-0.78, 0.05, 0.42), (-0.5, -0.42, 0.45), (0.0, -0.58, 0.5), (0.5, -0.42, 0.45), (0.8, 0.02, 0.42), (0.5, 0.36, 0.44),
            (-0.5, 0.36, 0.44), (0.0, 0.3, 0.5), (0.0, -0.1, 0.55)]
    K.elipse(L, cx + r * 0.62, cy + r * 0.62, r * 0.34, r * 0.24, C["seso2"], TINTA, 7)                   # cerebelo
    for i in range(5):
        K.linea(L, [(cx + r * 0.4, cy + r * (0.52 + i * 0.05)), (cx + r * 0.86, cy + r * (0.55 + i * 0.05))], (190, 84, 110), 4)
    for x, y, rr in lobs:
        K.circulo(L, cx + x * r, cy + y * r * 0.9, rr * r + 7, TINTA)
    for x, y, rr in lobs:
        K.circulo(L, cx + x * r, cy + y * r * 0.9, rr * r, C["seso"])
    random.seed(15)
    for i in range(9):                                       # surcos
        x0 = cx + random.uniform(-0.85, 0.85) * r
        y0 = cy + random.uniform(-0.6, 0.45) * r
        a = random.uniform(0, math.pi)
        pts = [(x0 + math.cos(a) * k * r * 0.07 + math.sin(k * 1.6) * r * 0.04, y0 + math.sin(a) * k * r * 0.07) for k in range(5)]
        K.linea(L, pts, C["seso2"], r * 0.035)
    K.linea(L, [(cx, cy - r * 0.62), (cx + r * 0.04, cy - r * 0.3), (cx - r * 0.02, cy - r * 0.1)], C["seso2"], r * 0.04)
    # cara
    ey = cy + r * 0.05
    if cara in ("feliz", "confiado"):
        for sg in (-1, 1):
            L.d.arc((L.S(cx + sg * r * 0.3 - r * 0.13), L.S(ey - r * 0.12), L.S(cx + sg * r * 0.3 + r * 0.13), L.S(ey + r * 0.12)), 190, 350, fill=TINTA, width=int(L.S(r * 0.06)))
        L.d.chord((L.S(cx - r * 0.24), L.S(ey + r * 0.06), L.S(cx + r * 0.24), L.S(ey + r * 0.42)), 0, 180, fill=C["boca"], outline=TINTA, width=int(L.S(6)))
    else:
        g = 1.25 if cara in ("preocupado", "sorpresa") else 1.0
        for sg in (-1, 1):
            K.elipse(L, cx + sg * r * 0.3, ey, r * 0.15 * g, r * 0.17 * g, C["blanco"], TINTA, 6)
            K.circulo(L, cx + sg * r * 0.3 + math.sin(t * 3) * r * 0.02, ey + r * 0.02, r * 0.065, TINTA)
            if cara == "preocupado":
                K.linea(L, [(cx + sg * r * 0.42, ey - r * 0.22), (cx + sg * r * 0.16, ey - r * 0.33)], TINTA, r * 0.055)
        if cara == "preocupado":
            pts = [(cx - r * 0.2 + i * r * 0.067, ey + r * 0.32 + (r * 0.03 if i % 2 else -r * 0.03)) for i in range(7)]
            K.linea(L, pts, TINTA, r * 0.045)
            K.elipse(L, cx - r * 0.86, cy - r * 0.38 + (t * 50 % 28), r * 0.07, r * 0.1, C["lagrima"], TINTA, 4)
        elif cara == "sorpresa":
            K.elipse(L, cx, ey + r * 0.33, r * 0.1, r * 0.13, C["boca"], TINTA, 6)
        else:
            L.d.arc((L.S(cx - r * 0.2), L.S(ey + r * 0.1), L.S(cx + r * 0.2), L.S(ey + r * 0.38)), 20, 160, fill=TINTA, width=int(L.S(r * 0.05)))


def volumen(L, cx, cy, s=1.0, nivel=0.5, t=0.0):
    """Medidor de volumen: parlante + 8 barras que se prenden de verde a rojo."""
    w, h = 820 * s, 330 * s
    K.caja_red(L, cx - w / 2 + 8, cy - h / 2 + 12, cx + w / 2 + 8, cy + h / 2 + 12, 46 * s, (0, 0, 0, 70))
    K.caja_red(L, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 46 * s, (44, 46, 66), TINTA, 8)
    px = cx - w / 2 + 120 * s
    K.poligono(L, [(px - 50 * s, cy - 40 * s), (px - 10 * s, cy - 40 * s), (px + 40 * s, cy - 90 * s), (px + 40 * s, cy + 90 * s), (px - 10 * s, cy + 40 * s), (px - 50 * s, cy + 40 * s)],
               C["blanco"], TINTA, 6)
    cols = [(110, 200, 100), (140, 210, 90), (180, 220, 80), (226, 220, 70), (250, 200, 60), (250, 160, 60), (240, 110, 60), (230, 64, 56)]
    n = 8
    x0 = px + 100 * s
    paso = (cx + w / 2 - 50 * s - x0) / n
    for i in range(n):
        bh = (60 + i * 26) * s
        x = x0 + i * paso
        lit = nivel * n > i + 0.01
        K.caja_red(L, x, cy + 120 * s - bh, x + paso * 0.7, cy + 120 * s, 10 * s, cols[i] if lit else (90, 92, 110), TINTA, 5)
    if nivel > 0.97:
        for i in range(3):
            u = (t * 2 + i / 3) % 1.0
            K.linea(L, [(px + 60 * s + u * 30 * s, cy - (70 + i * 10) * s), (px + 90 * s + u * 30 * s, cy - (90 + i * 10) * s)], C["amarillo"], 9 * s)


def hoja(L, cx, cy, s=1.0, titulo="ORDEN", sub="MOVER MANO", u=1.0, sello=0.0, color=None):
    """Hoja con una orden (y el timbre COPIA si `sello` > 0)."""
    if u <= 0.02:
        return
    w, h = 340 * s * u, 420 * s * u
    K.caja_red(L, cx - w / 2 + 8, cy - h / 2 + 10, cx + w / 2 + 8, cy + h / 2 + 10, 18 * s, (0, 0, 0, 70))
    K.caja_red(L, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 18 * s, color or C["papel"], TINTA, 7)
    K.texto(L, titulo, cx, cy - h * 0.32, 52 * s * u, TINTA)
    K.texto(L, sub, cx, cy - h * 0.15, 32 * s * u, C["polera2"])
    for i in range(4):
        K.linea(L, [(cx - w * 0.36, cy + h * (0.04 + i * 0.1)), (cx + w * (0.36 - 0.12 * (i == 3)), cy + h * (0.04 + i * 0.1))], (180, 170, 150), 8 * s * u)
    if sello > 0:
        sz = 1.0 + 0.6 * (1 - sello)
        K.caja_red(L, cx - 130 * s * sz, cy + h * 0.2 - 46 * s * sz, cx + 130 * s * sz, cy + h * 0.2 + 46 * s * sz, 14 * s, None, C["rojo"], 9 * sz)
        K.texto(L, "COPIA", cx, cy + h * 0.2, 62 * s * sz, C["rojo"])


def icono(L, que, x, y, r):
    """Íconos de la predicción: dónde (diana), cuándo (reloj), fuerza (pesa)."""
    if que == "donde":
        for i, c in enumerate((C["rojo"], C["blanco"], C["rojo"], C["blanco"])):
            K.circulo(L, x, y, r * (1 - i * 0.24), c, TINTA, 6)
    elif que == "cuando":
        cronometro(L, x, y + r * 0.1, r * 0.85, 0.3)
    else:
        K.poligono(L, [(x - r * 0.62, y + r * 0.8), (x + r * 0.62, y + r * 0.8), (x + r * 0.42, y - r * 0.32), (x - r * 0.42, y - r * 0.32)], C["cel"], TINTA, 7)
        L.d.arc((L.S(x - r * 0.34), L.S(y - r * 0.85), L.S(x + r * 0.34), L.S(y - r * 0.1)), 180, 360, fill=TINTA, width=int(L.S(r * 0.18)))
        K.texto(L, "KG", x, y + r * 0.26, r * 0.5, C["blanco"])


def pluma(L, x, y, ang, s=1.0, t=0.0):
    """Pluma de cosquillas con la punta en (x, y), apuntando hacia `ang`."""
    cola = _ext((x, y), ang + math.pi, 300 * s)
    K.linea(L, [cola, (x, y)], TINTA, 12 * s)
    pts = []
    n = 14
    for i in range(n + 1):
        u = i / n
        p = (cola[0] + (x - cola[0]) * u, cola[1] + (y - cola[1]) * u)
        wv = math.sin(u * math.pi) ** 0.8 * 60 * s * (1 + 0.08 * math.sin(t * 20 + u * 9))
        pts.append(_ext(p, ang - math.pi / 2, wv))
    for i in range(n, -1, -1):
        u = i / n
        p = (cola[0] + (x - cola[0]) * u, cola[1] + (y - cola[1]) * u)
        wv = math.sin(u * math.pi) ** 0.8 * 52 * s * (1 + 0.08 * math.sin(t * 20 + u * 7))
        pts.append(_ext(p, ang + math.pi / 2, wv))
    K.poligono(L, pts, (255, 236, 120), TINTA, 6)
    K.linea(L, [_ext(cola, ang, 40 * s), (x, y)], (220, 170, 60), 7 * s)


def robot(L, cx, cy, s=1.0, t=0.0, cara="normal", punta=None, ang_pluma=None):
    """Robot de cosquillas: caja con pantalla-cara y un brazo de dos tramos que termina en una pluma en `punta`."""
    K.caja_red(L, cx - 190 * s, cy - 150 * s, cx + 190 * s, cy + 150 * s, 40 * s, C["robot"], TINTA, 8)
    K.caja_red(L, cx - 150 * s, cy - 110 * s, cx + 150 * s, cy + 70 * s, 26 * s, (40, 60, 80), TINTA, 6)
    K.linea(L, [(cx, cy - 150 * s), (cx, cy - 230 * s)], TINTA, 12 * s)
    K.circulo(L, cx, cy - 240 * s, 22 * s, C["rojo"] if int(t * 3) % 2 else C["coral"], TINTA, 5)
    ey = cy - 30 * s
    verde = (120, 240, 170)
    if cara == "feliz":
        for sg in (-1, 1):
            L.d.arc((L.S(cx + sg * 60 * s - 30 * s), L.S(ey - 30 * s), L.S(cx + sg * 60 * s + 30 * s), L.S(ey + 24 * s)), 190, 350, fill=verde, width=int(L.S(12 * s)))
        L.d.arc((L.S(cx - 50 * s), L.S(ey - 10 * s), L.S(cx + 50 * s), L.S(ey + 60 * s)), 20, 160, fill=verde, width=int(L.S(12 * s)))
    else:
        for sg in (-1, 1):
            K.caja_red(L, cx + sg * 60 * s - 18 * s, ey - 26 * s, cx + sg * 60 * s + 18 * s, ey + 26 * s, 8 * s, verde)
        K.linea(L, [(cx - 40 * s, ey + 48 * s), (cx + 40 * s, ey + 48 * s)], verde, 10 * s)
    for i in range(3):
        K.circulo(L, cx - 90 * s + i * 90 * s, cy + 110 * s, 16 * s, [C["rojo"], C["amarillo"], C["verde"]][i], TINTA, 4)
    if punta:
        hom = (cx + 190 * s, cy - 40 * s)
        codo = brazo(L, hom, punta, C["robot2"], 46 * s, 0.25, -1)
        K.circulo(L, hom[0], hom[1], 30 * s, C["robot"], TINTA, 6)
        K.circulo(L, codo[0], codo[1], 28 * s, C["robot"], TINTA, 6)
        a = ang_pluma if ang_pluma is not None else math.atan2(punta[1] - codo[1], punta[0] - codo[0])
        pluma(L, _ext(punta, a, 230 * s)[0], _ext(punta, a, 230 * s)[1], a, 0.8 * s, t)
        K.caja_red(L, punta[0] - 34 * s, punta[1] - 34 * s, punta[0] + 34 * s, punta[1] + 34 * s, 10 * s, C["robot"], TINTA, 6)


def palanca(L, cx, cy, s=1.0, inclina=0.0):
    """Palanca (joystick) que mueve el robot."""
    K.caja_red(L, cx - 130 * s, cy - 40 * s, cx + 130 * s, cy + 60 * s, 24 * s, C["cel"], TINTA, 7)
    top = (cx + inclina * 120 * s, cy - 210 * s)
    K.linea(L, [(cx, cy - 30 * s), top], TINTA, 34 * s)
    K.linea(L, [(cx, cy - 30 * s), top], C["metal"], 22 * s)
    K.circulo(L, top[0], top[1], 50 * s, C["rojo"], TINTA, 7)
    return top


def bola(L, cx, cy, r, t=0.0, brillo=1.0):
    """Bola de cristal (el cerebro que predice) con una mano chiquita adentro."""
    K.poligono(L, [(cx - r * 0.7, cy + r * 1.2), (cx + r * 0.7, cy + r * 1.2), (cx + r * 0.48, cy + r * 0.82), (cx - r * 0.48, cy + r * 0.82)], C["oro2"], TINTA, 7)
    K.circulo(L, cx, cy, r * 1.0, C["cristal"], TINTA, 8)
    K.circulo(L, cx, cy, r * 0.86, C["cristal2"])
    mano_cosq(L, cx - r * 0.05, cy + r * 0.1, -0.5, r / 260, t, 1.0)
    L.d.chord((L.S(cx - r * 0.7), L.S(cy - r * 0.8), L.S(cx + r * 0.2), L.S(cy - r * 0.1)), 180, 280, fill=(255, 255, 255, 150))
    for i in range(5):
        an = t * 1.6 + i * 1.256
        x, y = cx + math.cos(an) * r * 1.25, cy + math.sin(an) * r * 1.05
        K.texto(L, "✦", x, y, 40 + 16 * math.sin(t * 6 + i), C["amarillo"], borde=4, color_borde=TINTA)
