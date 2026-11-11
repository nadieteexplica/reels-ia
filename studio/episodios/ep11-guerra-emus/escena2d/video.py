"""Ep. 11 — "El pájaro que le ganó una guerra a un ejército" (Guerra del Emú, 1932). 2D de comedia, todo por código (PIL).
Voz: escena2d/voz.wav + words.json (los deja prep.py). 15 planos; lo que cambia es el contenido, no la cámara (regla 24).
Uso: python3 video.py <carpeta_salida> [cuadro_desde cuadro_hasta]      (cuadros 1..FIN, 30 fps, 1080×1920)
"""
import json, math, os, random, sys
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
EPI = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)
import arte as A
import kit2d as K
from arte import C, TINTA, clamp, suave, sale, pop, rebote

W, H, FPS, SS = 1080, 1920, 30, 2
words = json.load(open(os.path.join(EPI, "words.json")))
ENV = json.load(open(os.path.join(AQUI, "envolvente.json")))
FIN_VOZ = words[-1]["e"]
DUR = FIN_VOZ + 1.0
FIN = int(round(DUR * FPS))


def tw(prefijo, desde=0.0):
    p = prefijo.lower()
    for w in words:
        if w["s"] >= desde - 0.01 and w["w"].lower().strip(".,;:…!?¡¿").startswith(p):
            return w["s"]
    raise KeyError(prefijo)


def boca(t):
    i = int(t * 60)
    return ENV[i] if 0 <= i < len(ENV) else 0.0


T_EJ = tw("ejército")
T_ES = tw("Es", 2.5)
T_NOV = tw("no", 4.0)
T_UNOS = tw("Unos")
T_GRANJ = tw("granjeros")
T_ASI = tw("Así")
T_TRES = tw("tres")
T_AMET = tw("ametralladoras")
T_FACIL = tw("Fácil")
T_PERO = tw("Pero")
T_CINC = tw("cincuenta")
T_LES = tw("Les", 15)
T_TRABO = tw("trabó")
T_SUB = tw("Subieron")
T_EN = tw("En", 19.5)
T_RAP = tw("rápidos")
T_SEGUN = tw("Según")
T_VIGIA = tw("vigía")
T_AVISA = tw("avisaba")
T_COM = tw("El", 25)
T_BALAS = tw("balas")
T_TANQ = tw("tanques")
T_IMAG = tw("Imagínate")
T_JEFE = tw("jefe")
T_POCO = tw("En", 30)
T_RETIRO = tw("retiró")
T_YLOS = tw("Y", 32.5)
T_YLA = tw("Y", 34)
T_UNA = tw("Una", 35.5)
T_CERCA = tw("cerca")
T_MARC = tw("Marcador")
T_CERO = tw("cero")
T_UNO = tw("uno", 38)

CORTES = [0.0, T_EJ - 0.08, T_ES - 0.1, T_UNOS - 0.08, T_ASI - 0.1, T_FACIL - 0.03, T_PERO - 0.06, T_LES - 0.1, T_SUB - 0.08, T_EN - 0.1,
          T_SEGUN - 0.08, T_COM - 0.12, T_IMAG - 0.12, T_POCO - 0.08, T_YLOS - 0.06, T_YLA - 0.06, T_MARC - 0.08, DUR]
T = {i + 1: (CORTES[i], CORTES[i + 1]) for i in range(len(CORTES) - 1)}
for _k, (_a, _b) in T.items():
    assert _b - _a >= 0.6, (_k, _a, _b)


def plano_de(t):
    for k, (a, b) in T.items():
        if a <= t < b:
            return k
    return max(T)


def dib(fn):
    def envuelto(t, a, b):
        L = K.Lienzo(ss=SS)
        fn(L, t, a, b)
        return L.salida()
    return envuelto


def txt(L, s, x, y, tam=64, *a, **kw):
    if tam * SS >= 2:
        K.texto(L, s, x, y, tam, *a, **kw)


def pild(L, s, cx, cy, t, t0, tam=56, fondo=None, tinta=None):
    if t >= t0:
        K.pildora(L, s, cx, cy, tam, fondo or C["blanco"], tinta or TINTA, pop(t - t0))


def confeti(L, t, t0, n=44, semilla=4):
    if t < t0:
        return
    random.seed(semilla)
    cols = [C["rojo"], C["amarillo"], C["blanco"], C["verde"], C["cuello"]]
    for i in range(n):
        x = random.uniform(0, W)
        v = random.uniform(500, 1100)
        y = -60 + (t - t0) * v - random.uniform(0, 500)
        y = y % (H + 200) - 100
        a = t * random.uniform(3, 8) + i
        w = 26 * abs(math.cos(a)) + 6
        K.poligono(L, [(x - w, y - 12), (x + w, y - 12), (x + w, y + 12), (x - w, y + 12)], cols[i % 5], TINTA, 3)


# ------------------------------------------------------------------ planos
def heroe(L, t, marc_u=1.0, cero=1.0, uno=1.0, lentes=False, medalla=False, grazna=0.0):
    """Cuadro 0 y cierre: el emú con casco, grande, y el marcador arriba. Detrás, un soldado chico con bandera blanca."""
    A.outback(L, 1260, t)
    A.soldado(L, 880, 1560, alto=300, t=t, mira=-1, cara="susto", bandera=True, tiembla=1.0, sudor=True)
    A.emu(L, 400, 1800, alto=960, t=t, casco=not lentes, ojos="serio", lentes=lentes, medalla=medalla, boca=grazna)
    if marc_u > 0:
        late = 0.62 + 0.1 * math.sin(t * 9)               # "?" que late hasta que se revela cada número
        A.marcador(L, 540, 345 - (1 - sale(marc_u)) * 700, 0.82, izq="0" if cero else "?", der="1" if uno else "?",
                   u_izq=cero if cero else late, u_der=uno if uno else late)


@dib
def p1(L, t, a, b):
    heroe(L, t, grazna=math.sin(clamp((t - 0.5) / 0.35) * math.pi))


@dib
def p2(L, t, a, b):
    # "…al ejército de Australia": tres soldados con bandera blanca, el emú los mira desde arriba
    A.outback(L, 1260, t)
    pild(L, "AUSTRALIA, 1932", 540, 330, t, a + 0.1, 60, C["rojo"], C["blanco"])
    for i, x in enumerate((250, 540, 830)):
        A.soldado(L, x, 1790 - (i == 1) * 20, alto=520, t=t + i, mira=1 if i < 2 else -1, cara=("susto", "triste", "susto")[i], bandera=(i == 1), tiembla=0.8, sudor=(i != 1))


@dib
def p3(L, t, a, b):
    # "Es un emú: enorme, y no vuela."
    A.outback(L, 1260, t)
    vuela = t >= T_NOV
    salto = 0.0
    if vuela:
        u = (t - T_NOV) / 0.75
        salto = max(0.0, math.sin(clamp(u) * math.pi)) * 150
    aplasta = clamp((t - T_NOV - 0.75) / 0.1) if vuela else 0
    A.soldado(L, 940, 1700, alto=620, t=t, mira=-1, cara="susto" if t > tw("enorme") else "normal")
    A.emu(L, 380, 1700 - salto, alto=820, t=t, ojos="susto" if (vuela and salto > 5) else ("x" if aplasta and t < T_NOV + 1.5 else "normal"),
          alas=1.0 if vuela and salto > 5 else 0.0, squash=0.0)
    te = tw("enorme")
    if t >= te:                                         # regla de medir
        u = sale((t - te) / 0.25)
        x = 740
        y1, y0 = 1700, 1700 - 800 * u
        K.linea(L, [(x, y1), (x, y0)], TINTA, 16)
        K.linea(L, [(x, y1), (x, y0)], C["amarillo"], 8)
        for yy in (y0, y1):
            K.linea(L, [(x - 40, yy), (x + 40, yy)], TINTA, 14)
        if not vuela:
            pild(L, "1,8 m", 800, 800, t, te + 0.15, 64, C["amarillo"])
    pild(L, "EMÚ", 300, 420, t, T_ES + 0.25, 84, C["rojo"], C["blanco"])
    if vuela:
        pild(L, "NO VUELA", 660, 480, t, T_NOV + 0.1, 70)
        if aplasta:
            A.polvo(L, 520, 1720, (t - T_NOV - 0.75) * 0.5, 6, 1.0, dir_x=1)
            A.polvo(L, 300, 1720, (t - T_NOV - 0.75) * 0.5, 6, 1.0, dir_x=-1, semilla=3)


def granjero(L, x, y, alto, t, manos_arriba=0.0):
    k = alto / 420.0
    ropa = {"cabeza": "nada", "torso": (86, 130, 190), "piernas": (70, 84, 120), "botas": (84, 60, 44), "piel": C["piel"], "piel2": C["piel2"]}
    ang = 8 + 150 * manos_arriba
    K.persona(L, x, y, alto=alto, ropa=ropa, pose={"brazo_der": ang, "brazo_izq": ang}, mira=-1, t=t)
    cy = y - 330 * k + math.sin(t * 2.2) * 3 * k - 62 * k
    K.circulo(L, x, cy, 52 * k, C["piel"], TINTA, 5)
    for s in (-1, 1):
        K.circulo(L, x + s * 19 * k - 8 * k, cy + 2 * k, 15 * k, C["blanco"], TINTA, 3)
        K.circulo(L, x + s * 19 * k - 8 * k, cy + 3 * k, 4.5 * k, TINTA)
    K.elipse(L, x - 8 * k, cy + 32 * k, 14 * k, 12 * k, (110, 44, 40), TINTA, 3)
    K.elipse(L, x, cy - 36 * k, 96 * k, 22 * k, C["trigo"], TINTA, 5)
    L.d.chord((L.S(x - 48 * k), L.S(cy - 90 * k), L.S(x + 48 * k), L.S(cy - 6 * k)), 180, 360, fill=C["trigo"], outline=TINTA, width=int(L.S(5)))


@dib
def p4(L, t, a, b):
    # "Unos veinte mil se estaban comiendo el trigo de los granjeros."
    u = clamp((t - a) / (b - a))
    A.outback(L, 900, t, cerros=False)
    A.trigal(L, 960, 1840, t, comido=0.15 + 0.75 * u)
    random.seed(8)
    emus = []
    for i in range(16):                                   # manada al fondo
        emus.append((random.uniform(560, 940), random.uniform(-200, 1300), random.uniform(150, 230), i))
    for y_, x_, al, i in sorted(emus):
        xx = x_ - (t - a) * 120
        A.emu(L, xx, y_ + 420, alto=al, t=t, mira=-1, come=0.5 + 0.5 * math.sin(t * 7 + i), fase=i)
    A.emu(L, 760 - u * 120, 1760, alto=640, t=t, mira=-1, come=0.55 + 0.45 * math.sin(t * 9), ojos="feliz", boca=abs(math.sin(t * 12)))
    g = clamp((t - T_GRANJ + 0.1) / 0.2)
    if g > 0:
        granjero(L, 170, 1760 + (1 - sale(g)) * 600, 560, t, manos_arriba=1.0)
    n = int(20000 * sale((t - tw("veinte") + 0.1) / 0.5) / 500) * 500
    if t >= tw("veinte") - 0.1:
        K.pildora(L, f"{n:,} EMÚS".replace(",", "."), 540, 380, 84, C["rojo"], C["blanco"], pop(t - tw("veinte") + 0.1))


@dib
def p5(L, t, a, b):
    # "Así que el gobierno mandó tres soldados con ametralladoras."
    A.outback(L, 1260, t)
    for i, x in enumerate((230, 540, 850)):
        t0 = (a + 0.25 + i * 0.3) if t < T_TRES else 0
        ti = a + 0.2 + i * 0.32
        if t >= ti:
            cae = rebote(t - ti, 0.4)
            A.soldado(L, x, 1800 - (1 - cae) * 900, alto=540, t=t + i, mira=1, cara="feliz" if t > T_AMET else "normal", brazo_der=8 if t < T_AMET else 70)
            if t >= T_TRES - 0.05:
                K.pildora(L, str(i + 1), x, 880, 70, C["amarillo"], TINTA, pop(t - (T_TRES - 0.05) - i * 0.12))
    if t >= T_AMET:
        for i, x in enumerate((385, 695)):
            u = rebote(t - T_AMET - i * 0.15, 0.4)
            if u > 0:
                A.ametralladora(L, x - 60, 1820 - (1 - u) * 1300, 0.9, 1, t)
        pild(L, "2 AMETRALLADORAS", 540, 330, t, T_AMET + 0.25, 58, C["blanco"])
        pild(L, "10.000 BALAS", 540, 450, t, T_AMET + 0.55, 66, C["rojo"], C["blanco"])


@dib
def p6(L, t, a, b):
    # "Fácil, ¿no?" — el viejo del dato
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=C["amarillo"])
    random.seed(3)
    for i in range(14):
        an = i * math.pi / 7 + t * 0.4
        K.poligono(L, [(540, 900), (540 + math.cos(an) * 2200, 900 + math.sin(an) * 2200), (540 + math.cos(an + 0.22) * 2200, 900 + math.sin(an + 0.22) * 2200)], (255, 226, 110))
    K.viejo(L, 540, 1560, alto=1000, boca=boca(t), t=t, gesto="tazon", mira=1)
    u = pop(t - a - 0.05)
    if u > 0:
        txt(L, "¿FÁCIL?", 540, 360, 190 * u, C["rojo"], borde=10, color_borde=TINTA)


@dib
def p7(L, t, a, b):
    # "Pero el emú corre a casi cincuenta kilómetros por hora."
    A.outback(L, 1260, t, cerros=False)
    for i in range(3):                                    # cerros que pasan rápido
        x = (W + 500) - ((t - a) * 900 + i * 560) % (W + 1000)
        A.mesa(L, x, 1260, 340, 170)
        L.d.rectangle((L.S(x - 200), L.S(1262), L.S(x + 200), L.S(1275)), fill=C["tierra"])
    A.lineas_vel(L, -100, W + 100, 500, 1750, t - a, 12)
    A.polvo(L, 380, 1700, t, 9, 1.2)
    sx = 150 - (t - a) * 140                              # el soldado se queda atrás
    A.soldado(L, sx, 1640, alto=330, t=t, mira=1, cara="susto", paso=math.sin(t * 16), sudor=True, brazo_der=60, brazo_izq=40)
    A.emu(L, 600, 1700, alto=860, t=t, corre=1.6, ojos="serio", boca=0.2)
    if t >= T_CINC - 0.05:
        e = t - (T_CINC - 0.05)
        n = int(50 * sale(e / 0.4))
        K.pildora(L, f"CASI {n} km/h", 540, 400, 96, C["rojo"], C["blanco"], pop(e))


@dib
def p8(L, t, a, b):
    # "Les prepararon una emboscada, y una ametralladora se trabó."
    A.outback(L, 1180, t)
    trab = t >= T_TRABO
    # aguada con emús
    K.elipse(L, 800, 1560, 300, 90, (120, 190, 226), TINTA, 6)
    L.d.arc((L.S(640), L.S(1530), L.S(820), L.S(1580)), 180, 360, fill=C["blanco"], width=int(L.S(6)))
    for i, (x, y, al) in enumerate(((930, 1500, 380), (700, 1480, 330), (850, 1700, 470))):
        if trab:
            e = t - T_TRABO - 0.12 - i * 0.05
            dx = max(0, e) * 1500
            A.emu(L, x + dx, y, alto=al, t=t, mira=1, corre=1.8 if e > 0 else 0, ojos="susto", fase=i * 2)
        else:
            A.emu(L, x, y, alto=al, t=t, mira=-1, come=0.7 + 0.3 * math.sin(t * 6 + i), fase=i)
    # el arbusto con los soldados escondidos
    sube = sale((t - a) / 0.3)
    A.soldado(L, 200, 1990 + (1 - sube) * 200, alto=460, t=t, mira=1, cara="susto" if trab else "feliz", sombrero=True, sudor=trab)
    A.arbusto(L, 210, 1830, 1.5)
    A.ametralladora(L, 330, 1610, 0.95, 1, t, dispara=1.0 if (tw("y", 16.3) < t < T_TRABO - 0.3) else 0, trabada=trab, bipode=False)
    if not trab:
        pild(L, "EMBOSCADA", 300, 700, t, tw("emboscada") - 0.05, 64, C["verde2"], C["blanco"])
    else:
        e = t - T_TRABO
        A.estrella_golpe(L, 400, 700 - 40 * sale(e / 0.2), 270 * pop(e), C["rojo"], 11, None, rot=0.2)
        txt(L, "¡CLAC!", 400, 700 - 40 * sale(e / 0.2), 120 * pop(e), C["blanco"], borde=6)


@dib
def p9(L, t, a, b):
    # "Subieron otra a un camión."
    A.outback(L, 1260, t)
    u = sale((t - a) / 0.4)
    cx = -500 + 1000 * u
    pos, rot = A.camion(L, cx, 1700, 1.15, 1, t, salta=0.25)
    A.soldado(L, pos[0], pos[1], alto=400, t=t, mira=1, cara="feliz", brazo_der=80)
    tc = tw("camión")
    A.ametralladora(L, pos[0] + 190, pos[1] - 240, 0.8, 1, t, bipode=True)
    pild(L, "PLAN B", 540, 420, t, a + 0.15, 100, C["amarillo"])
    if t > tc + 0.2:
        A.estrella_golpe(L, 880, 760, 150 * pop(t - tc - 0.2), C["blanco"], 9)
        txt(L, "¡JA!", 880, 760, 80 * pop(t - tc - 0.2), C["rojo"])


@dib
def p10(L, t, a, b):
    # "En ese terreno, los emús eran más rápidos."
    A.outback(L, 1260, t, cerros=False)
    e = t - a
    for i in range(3):
        x = (W + 500) - (e * 800 + i * 560) % (W + 1000)
        A.mesa(L, x, 1260, 340, 170)
        L.d.rectangle((L.S(x - 200), L.S(1262), L.S(x + 200), L.S(1275)), fill=C["tierra"])
    random.seed(2)
    for i in range(7):                                    # piedras y hoyos del terreno
        x = (W + 200) - (e * 1000 + i * 190) % (W + 400)
        y = 1640 + (i % 3) * 70
        K.elipse(L, x, y, 60, 26, C["tierra3"], TINTA, 5)
    cx = 190 - e * 150                                    # el camión se va quedando
    A.polvo(L, cx - 300, 1700, t, 8, 1.1)
    pos, rot = A.camion(L, cx, 1700, 0.95, 1, t, salta=1.6)
    A.soldado(L, pos[0], pos[1], alto=330, t=t, mira=1, cara="susto", tiembla=1.5, sudor=True, brazo_der=90, brazo_izq=120)
    A.ametralladora(L, pos[0] + 150, pos[1] - 200 + math.sin(t * 23) * 40, 0.66, 1, t, dispara=0.8)
    for i in range(4):                                    # balas que se van para cualquier lado
        u = (e * 1.7 + i / 4) % 1.0
        A.bala(L, cx + 330 + u * 500, 1350 - u * (300 + i * 170) * (1 if i % 2 else -0.3), 0.8, ang=-0.6 * (1 if i % 2 else -0.4))
    ex = 790 + e * 50
    A.emu(L, ex - 230, 1540, alto=380, t=t, corre=1.9, fase=2.0, ojos="feliz")
    A.emu(L, ex, 1740, alto=540, t=t, corre=1.7, mira=1, ojos="feliz", lengua=t > T_RAP - 0.5)
    pild(L, "TERRENO DISPAREJO", 540, 380, t, a + 0.15, 56)
    pild(L, "EMÚS > CAMIÓN", 540, 500, t, T_RAP - 0.1, 76, C["rojo"], C["blanco"])


@dib
def p11(L, t, a, b):
    # "Según los soldados, cada grupo tenía un vigía que avisaba."
    A.outback(L, 1300, t, cerros=False)
    K.poligono(L, [(520, 1300), (600, 880), (1010, 880), (1100, 1300)], C["tierra3"], TINTA, 7)   # la roca del vigía
    K.linea(L, [(640, 1020), (960, 1020)], C["tierra2"], 10)
    av = t >= T_AVISA
    A.emu(L, 800, 890, alto=600, t=t, mira=-1, binoc=not av, ojos="susto", boca=(abs(math.sin(t * 22)) if av else 0), cuello_u=1.15)
    pild(L, "VIGÍA", 820, 250, t, T_VIGIA - 0.05, 80, C["rojo"], C["blanco"])
    # soldados que se acercan agachados por la izquierda
    sx = -120 + sale((t - a) / 1.6) * 330
    A.soldado(L, sx, 1700, alto=300, t=t, mira=1, cara="normal" if not av else "triste")
    A.arbusto(L, sx - 20, 1600, 0.8)
    A.ametralladora(L, sx + 60, 1480, 0.5, 1, t, bipode=False)
    for i, (x, y, al) in enumerate(((330, 1800, 420), (560, 1720, 360), (760, 1830, 400))):
        if av:
            e = t - T_AVISA - 0.15 - i * 0.07
            A.emu(L, x + max(0, e) * 1300, y, alto=al, t=t, corre=1.9 if e > 0 else 0, ojos="susto", fase=i)
        else:
            A.emu(L, x, y, alto=al, t=t, mira=-1 if i % 2 else 1, come=0.8 + 0.2 * math.sin(t * 6 + i), fase=i)
    if av:
        e = t - T_AVISA
        A.estrella_golpe(L, 470, 520, 190 * pop(e), C["amarillo"], 10, rot=-0.2)
        txt(L, "¡OJO!", 470, 520, 96 * pop(e), C["rojo"], borde=5, color_borde=TINTA)


def emu_tanque(L, x, y, s, t, mira=-1):
    A.emu(L, x, y - 70 * s, alto=560 * s, t=t, mira=mira, ojos="serio", casco=False)
    K.caja_red(L, x - 250 * s, y - 150 * s, x + 250 * s, y, 74 * s, C["metal2"], TINTA, 7)
    for i in range(4):
        wx = x - 174 * s + i * 116 * s
        K.circulo(L, wx, y - 75 * s, 46 * s, C["metal"], TINTA, 5)
        a = t * 5 + i
        K.linea(L, [(wx - math.cos(a) * 30 * s, y - 75 * s - math.sin(a) * 30 * s), (wx + math.cos(a) * 30 * s, y - 75 * s + math.sin(a) * 30 * s)], TINTA, 7 * s)


@dib
def p12(L, t, a, b):
    # "El comandante dijo que aguantaban las balas como tanques."
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=(250, 226, 170))
    L.d.rectangle((0, L.S(1560), L.S(W), L.S(H)), fill=C["tierra"])
    L.d.line([L.pt(0, 1560), L.pt(W, 1560)], fill=TINTA, width=int(L.S(7)))
    A.soldado(L, 230, 1900, alto=640, t=t, mira=1, cara="susto", oficial=True, sudor=True, brazo_der=60 + 20 * math.sin(t * 9), brazo_izq=30)
    pild(L, "EL COMANDANTE", 700, 1500, t, a + 0.15, 44, C["caqui2"], C["blanco"])
    u = pop(t - a - 0.1)
    if u > 0:
        A.globo(L, 300, 190, 1040, 950, (300, 1230))
        tq = t >= T_TANQ - 0.1
        if tq:
            emu_tanque(L, 700, 900, 0.9, t)
        else:
            A.emu(L, 720, 900, alto=520, t=t, mira=-1, ojos="serio")
        if t >= T_BALAS - 0.1:
            for i in range(5):                            # balas que rebotan
                uu = ((t - T_BALAS) * 2.2 + i / 5) % 1.0
                if uu < 0.5:
                    A.bala(L, 380 + uu * 2 * 190, 560 + i * 44, 0.6)
                else:
                    v = (uu - 0.5) * 2
                    A.bala(L, 570 - v * 170, 560 + i * 44 - v * 230 + v * v * 120, 0.6, ang=2.4 + v * 3)
                    if v < 0.25:
                        A.estrella_golpe(L, 585, 560 + i * 44, 44, C["amarillo"], 7)
            if tq:
                txt(L, "¡PING!", 470, 800, 70 * pop(t - T_TANQ + 0.1), C["rojo"], borde=5, color_borde=TINTA)


@dib
def p13(L, t, a, b):
    # "Imagínate explicarle eso a tu jefe."
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=(196, 214, 196))
    for i in range(8):
        L.d.line([L.pt(60 + i * 150, 0), L.pt(60 + i * 150, 1500)], fill=(180, 200, 182), width=int(L.S(12)))
    L.d.rectangle((0, L.S(1500), L.S(W), L.S(H)), fill=(150, 110, 80))
    L.d.line([L.pt(0, 1500), L.pt(W, 1500)], fill=TINTA, width=int(L.S(7)))
    # pizarra con el informe
    K.caja_red(L, 60, 330, 520, 880, 16, C["blanco"], TINTA, 8)
    txt(L, "INFORME", 290, 400, 54, TINTA)
    A.emu(L, 230, 800, alto=300, t=0, ojos="serio", casco=True)
    txt(L, "= TANQUE", 380, 820, 34, C["rojo"])
    # el jefe, grande y furioso, detrás del escritorio
    tj = T_JEFE
    crece = 1.0 + 0.12 * sale((t - tj) / 0.25)
    A.soldado(L, 790, 1820, alto=1000 * crece, t=t, mira=-1, cara="enojo", oficial=True, sombrero=False, tiembla=1.0 if t > tj else 0.2)
    K.caja_red(L, 520, 1300, 1140, 1960, 18, C["madera"], TINTA, 8)
    K.caja_red(L, 600, 1380, 1060, 1500, 10, (150, 104, 60), TINTA, 5)
    K.caja_red(L, 700, 1210, 900, 1300, 8, C["amarillo"], TINTA, 5)
    txt(L, "JEFE", 800, 1256, 50, TINTA)
    if t > tj:
        for i in range(3):                                # humo de rabia
            uu = ((t - tj) * 1.3 + i / 3) % 1.0
            K.circulo(L, 660 + i * 130, 560 - uu * 200, 30 + 40 * uu, (255, 255, 255, int(230 * (1 - uu))))
    A.soldado(L, 300, 1840, alto=600, t=t, mira=1, cara="susto", sudor=True, tiembla=1.2, brazo_izq=120)
    pild(L, "TÚ", 130, 960, t, tw("explicarle") - 0.05, 76, C["rojo"], C["blanco"])


@dib
def p14(L, t, a, b):
    # "En poco más de un mes, el ejército se retiró."
    A.outback(L, 1260, t)
    e = t - a
    # calendario
    K.caja_red(L, 90, 250, 430, 620, 26, C["blanco"], TINTA, 8)
    K.caja_red(L, 90, 250, 430, 350, 26, C["rojo"], TINTA, 8)
    txt(L, "DÍA", 260, 302, 52, C["blanco"])
    dia = min(38, int(1 + 37 * sale(e / 1.0)))
    txt(L, str(dia), 260, 490, 170, TINTA)
    for i, x0 in enumerate((280, 450, 620)):
        x = x0 - max(0, t - tw("el", 31.5)) * 330
        A.soldado(L, x, 1700, alto=470, t=t + i, mira=-1, cara="triste", paso=math.sin(t * 9 + i), bandera=(i == 0))
    A.emu(L, 990, 1860, alto=500, t=t, mira=-1, ojos="feliz", alas=1.0 if t > T_RETIRO else 0)
    pild(L, "CAYERON MENOS DE 1.000", 640, 700, t, T_POCO + 0.45, 56)
    pild(L, "DE 20.000 EMÚS", 640, 810, t, T_POCO + 0.7, 68, C["rojo"], C["blanco"])


@dib
def p15(L, t, a, b):
    # "Y los emús siguieron comiendo trigo."
    u = clamp((t - a) / (b - a))
    A.outback(L, 900, t, cerros=False)
    A.trigal(L, 960, 1840, t, comido=0.3 + 0.7 * u, semilla=6)
    A.emu(L, 260, 1500, alto=460, t=t, mira=1, come=0.55 + 0.45 * math.sin(t * 10), ojos="feliz", fase=1)
    A.emu(L, 820, 1560, alto=520, t=t, mira=-1, come=0.55 + 0.45 * math.sin(t * 9 + 2), ojos="feliz", fase=2)
    A.emu(L, 520, 1800, alto=720, t=t, mira=1, come=0.5 + 0.5 * math.sin(t * 11 + 1), ojos="feliz", boca=abs(math.sin(t * 12)))
    for i in range(3):
        e = (t - a) * 2.4 - i * 0.5
        if e > 0:
            txt(L, "ÑAM", 250 + i * 290, 620 - (i % 2) * 150, 90 * pop(e % 1.6, 0.2), C["blanco"], borde=7, color_borde=TINTA)


@dib
def p16(L, t, a, b):
    # "¿Y la única defensa que quedó? Una cerca."
    A.outback(L, 1260, t)
    cae = clamp((t - T_UNA) / 0.3)
    en_cerca = t >= T_UNA + 0.3
    if not en_cerca:
        ex = 330 - (T_UNA + 0.3 - t) * 230
        A.emu(L, ex, 1720, alto=760, t=t, corre=1.5, ojos="feliz")
        if cae <= 0:
            txt(L, "?", 760, 560, 520 * pop(t - a - 0.03), C["rojo"], borde=12, color_borde=TINTA)
    else:
        e = t - T_UNA - 0.3
        A.emu(L, 330 - min(e, 0.15) * 200, 1720, alto=760, t=t, ojos="x", squash=clamp(1 - e / 0.5) * 0.9 + 0.1)
        for i in range(3):                                # estrellitas del golpe
            an = t * 5 + i * 2.1
            A.estrella_golpe(L, 520 + math.cos(an) * 120, 760 + math.sin(an) * 50, 34, C["amarillo"], 5)
    if cae > 0:
        A.reja(L, 760, 620, 1740, n=5, caida=sale(cae))
    if en_cerca:
        e = t - T_UNA - 0.3
        if e < 0.5:
            A.estrella_golpe(L, 400, 740, 230 * pop(e), C["rojo"], 11)
            txt(L, "¡PAF!", 400, 740, 104 * pop(e), C["blanco"], borde=5)
        pild(L, "UNA CERCA", 540, 380, t, T_CERCA - 0.05, 100, C["amarillo"])


@dib
def p17(L, t, a, b):
    # "Marcador final: ejército, cero. Emús, uno." → vuelve al cuadro 0 (loop)
    gana = t >= T_UNO
    heroe(L, t, marc_u=clamp((t - a) / 0.3), cero=pop(t - T_CERO) if t >= T_CERO else 0, uno=pop(t - T_UNO) if gana else 0)
    if gana:
        confeti(L, t, T_UNO)


FUN = {i: globals()[f"p{i}"] for i in range(1, 18)}
assert len(FUN) == len(T)

# ------------------------------------------------------------------ subtítulos (palabra por palabra, 1–3 palabras)
FONT = K.FONT
AMARILLO = (255, 210, 63)
CLAVE = {"EMÚ": (255, 150, 60), "EMÚS": (255, 150, 60), "CERO": (255, 96, 84), "UNO": (120, 230, 120), "CERCA": (120, 230, 120)}
BOX = (120, 960, 1000, 1250)


def limpiar(w):
    for ch in ",.:;!¡\"…«»":
        w = w.replace(ch, "")
    return w.upper()


TOK = [limpiar(x["w"]) for x in words]
grupos, g = [], []
for i, x in enumerate(words):
    g.append(i)
    fin = x["w"][-1] in ".,:;?!"
    sig_pausa = i + 1 < len(words) and words[i + 1]["s"] - x["e"] > 0.25
    largo = sum(len(TOK[j]) for j in g) + len(g) - 1
    prox = len(TOK[i + 1]) if i + 1 < len(words) else 0
    if fin or sig_pausa or len(g) == 3 or largo + 1 + prox > 16:
        grupos.append(g); g = []
if g:
    grupos.append(g)
# no dejar una palabra corta sola al final de frase si cabe con el grupo anterior
i = 1
while i < len(grupos):
    a_, b_ = grupos[i - 1], grupos[i]
    if len(b_) == 1 and len(a_) <= 2 and words[a_[-1]]["w"][-1] not in ".,:;?!" and sum(len(TOK[j]) for j in a_ + b_) + len(a_) <= 17 \
            and words[b_[0]]["s"] - words[a_[-1]]["e"] < 0.25:
        grupos[i - 1] = a_ + b_; del grupos[i]
    else:
        i += 1


def ancho_toks(f, toks):
    return sum(f.getlength(x) for x in toks) + f.getlength(" ") * 1.15 * (len(toks) - 1)


def subtitulos(im, t):
    g = None
    for gi, gg in enumerate(grupos):
        s, e = words[gg[0]]["s"], words[gg[-1]]["e"]
        nxt = grupos[gi + 1] if gi + 1 < len(grupos) else None
        e_show = min(e + 0.25, words[nxt[0]]["s"]) if nxt else e + 0.5
        if s - 0.03 <= t < e_show:
            g = gg
            break
    if g is None:
        return
    toks = [TOK[j] for j in g]
    maxw = BOX[2] - BOX[0] - 40
    for size in range(92, 59, -4):
        f = ImageFont.truetype(FONT, size)
        if ancho_toks(f, toks) <= maxw:
            break
    d = ImageDraw.Draw(im, "RGBA")
    y = (BOX[1] + BOX[3]) / 2 - f.size * 0.56
    x = W / 2 - ancho_toks(f, toks) / 2
    for j, tok in zip(g, toks):
        activo = words[j]["s"] - 0.02 <= t < max(words[j]["e"], words[j]["s"] + 0.12)
        col = CLAVE.get(tok.strip("¿?"), AMARILLO if activo else (255, 255, 255))
        d.text((x + 4, y + 7), tok, font=f, fill=(0, 0, 0, 120), stroke_width=7, stroke_fill=(0, 0, 0, 120))
        d.text((x, y), tok, font=f, fill=col, stroke_width=7, stroke_fill=(20, 16, 16))
        x += f.getlength(tok) + f.getlength(" ") * 1.15


_GRANO = {}


def cuadro(f):
    t = (f - 1) / FPS
    k = plano_de(t)
    a, b = T[k]
    im = FUN[k](t, a, b)
    if not _GRANO:
        _GRANO["g"] = Image.effect_noise((W, H), 14).convert("RGB")
    im = Image.blend(im, Image.composite(im, _GRANO["g"], Image.new("L", (W, H), 236)), 0.18)
    subtitulos(im, t)
    return im


if __name__ == "__main__":
    dst = sys.argv[1]
    os.makedirs(dst, exist_ok=True)
    a = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    b = int(sys.argv[3]) if len(sys.argv) > 3 else FIN
    paso = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    for f in range(a, b + 1, paso):
        cuadro(f).save(os.path.join(dst, f"{f:05d}.png"), compress_level=1)
    print("ok", a, b)
