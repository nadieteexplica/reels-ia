"""Ep. 10d — "Lo castigaron por seguir vivo" (2D plano, 7-nov-2026). Voz de 54,9 s (out/tts/ep10d-kamikaze-vivo.mp3).
Un solo protagonista (Kenichiro Oonuki), 31 planos (~1,8 s cada uno), reglas 13–20 de docs/GUIONISTA.md.
Reutiliza el kit 2D (studio/plantilla/kit2d.py) y escenas de ep10-kamikazes/escena2d/video2d.py.
Uso: python3 video.py <salida> [cuadro_desde cuadro_hasta]
"""
import json, math, os, random, sys
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
EPI = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, os.path.abspath(os.path.join(AQUI, "../../ep10-kamikazes/escena2d")))
import video2d as V
import kit2d as K
from kit2d import P

W, H, FPS = 1080, 1920, 30
words = json.load(open(os.path.join(EPI, "words.json")))
V.ENV = json.load(open(os.path.join(AQUI, "envolvente.json")))
FIN_VOZ = words[-1]["e"]
DUR = FIN_VOZ + 0.9
FIN = int(round(DUR * FPS))
clamp, suave, sale, pop = V.clamp, V.suave, V.sale, V.pop


def tw(prefijo, desde=0.0):
    p = prefijo.lower()
    for w in words:
        if w["s"] >= desde - 0.01 and w["w"].lower().strip(".,;:…!?¡¿").startswith(p):
            return w["s"]
    raise KeyError(prefijo)


CORTES = [0.0,
          tw("Su") - 0.1, tw("estrellar") - 0.12, tw("contra") - 0.1,                       # 2 misión · 3 picada · 4 cubierta
          tw("Japón", 7.5) - 0.1, tw("y", 9.6) - 0.06,                                     # 5 mapa · 6 cercado
          tw("Cómo") - 0.12, tw("En", 13) - 0.1, tw("morir", 14.3) - 0.1,                   # 7 viejo · 8 Japón 40 · 9 pecado
          tw("Era", 16) - 0.1, tw("el", 17.2) - 0.06,                                      # 10 honor · 11 samurái
          tw("Pero", 18.3) - 0.1, tw("Y", 19.5) - 0.06,                                    # 12 miedo · 13 no era el único
          tw("Cuando") - 0.1, tw("Les", 23.4) - 0.1, tw("y", 25.0) - 0.06,                  # 14 foto · 15 noche · 16 hoja
          tw("Por", 27.7) - 0.08, tw("Si", 28.3) - 0.08, tw("Y", 30.3) - 0.06,              # 17 ¿por qué? · 18 cobarde · 19 familia
          tw("El", 32.0) - 0.1, tw("Sus", 33.9) - 0.1, tw("Les", 35.9) - 0.1,               # 20 falla · 21 despegan · 22 azaleas
          tw("y", 36.9) - 0.06, tw("Quería") - 0.1,                                        # 23 «me adelanto» · 24 «quería ir contigo»
          tw("Le", 40.1) - 0.1, tw("Aterrizó") - 0.1,                                      # 25 motor · 26 isla
          tw("Volvió", 44.8) - 0.1, tw("Y", 45.9) - 0.06, tw("Para", 48) - 0.1,                 # 27 vivo · 28 castigo · 29 vergüenza
          tw("Sí", 50.8) - 0.1, tw("Pero", 52.6) - 0.1, DUR]                               # 30 balanza · 31 cierre
T = {i + 1: (CORTES[i], CORTES[i + 1]) for i in range(len(CORTES) - 1)}
for k, (a, b) in T.items():
    assert b - a >= 0.5, (k, a, b)


def plano_de(t):
    for k, (a, b) in T.items():
        if a <= t < b:
            return k
    return max(T)


# golpes (sacuden el cuadro) y sellos
T_GOLPE1 = tw("castigaron") + 0.02
T_PEGA1, T_PEGA2 = tw("pegaron") + 0.02, tw("bambú") + 0.02
T_VIVO1, T_VIVO2 = tw("vivo"), tw("vivo", 45.0)
T_COBARDE, T_FAMILIA = tw("cobarde"), tw("familia")
SACUDIDAS = [T_GOLPE1, T_VIVO1, T_COBARDE, T_FAMILIA, T_VIVO2, T_PEGA1, T_PEGA2]

def dibujo(fn):
    def envuelto(t, a, b, **kw):
        L = K.Lienzo(ss=V.SS)
        fn(L, t, a, b, **kw)
        return L.salida()
    return envuelto

TINTA = P["tinta"]
VERDE_AV = (98, 112, 80)


# ------------------------------------------------------------------ personajes
def cabeza_piloto(L, x, cy, k, mira=1, ojos="normal", hachimaki=True, sudor=-1.0, casco=True):
    """Cabeza del piloto (casco de cuero, antiparras, cinta). ojos: normal | miedo | triste | cerrados. sudor: 0..1 (gota que baja)."""
    K.circulo(L, x, cy, 52 * k, P["piel"], TINTA, 5)
    if casco:
        L.d.chord((L.S(x - 56 * k), L.S(cy - 60 * k), L.S(x + 56 * k), L.S(cy + 50 * k)), 180, 360, fill=P["cuero"], outline=TINTA, width=int(L.S(5)))
        for s in (-1, 1):
            K.caja_red(L, x + s * 54 * k - 9 * k, cy - 6 * k, x + s * 54 * k + 9 * k, cy + 40 * k, 8 * k, P["cuero"], TINTA, 4)
        K.caja_red(L, x - 46 * k, cy - 48 * k, x + 46 * k, cy - 26 * k, 10 * k, P["gris"], TINTA, 4)
        for s in (-1, 1):
            K.circulo(L, x + s * 22 * k, cy - 37 * k, 15 * k, (170, 196, 206), TINTA, 4)
        if hachimaki:
            K.caja_red(L, x - 52 * k, cy - 62 * k, x + 52 * k, cy - 48 * k, 6 * k, P["blanco"], TINTA, 3)
            K.circulo(L, x, cy - 55 * k, 6 * k, P["rojo"])
    ex = mira * 8 * k
    if ojos == "miedo":
        for s in (-1, 1):
            K.circulo(L, x + s * 18 * k + ex, cy + 4 * k, 10 * k, P["blanco"], TINTA, 3)
            K.circulo(L, x + s * 18 * k + ex, cy + 5 * k, 3.6 * k, TINTA)
            K.linea(L, [(x + s * 30 * k + ex, cy - 9 * k), (x + s * 8 * k + ex, cy - 17 * k)], TINTA, 3.5 * k)
        K.elipse(L, x + ex, cy + 30 * k, 8 * k, 6 * k, (110, 44, 40), TINTA, 3)
    elif ojos == "triste":
        for s in (-1, 1):
            K.circulo(L, x + s * 17 * k + ex, cy + 5 * k, 5.5 * k, TINTA)
            K.linea(L, [(x + s * 28 * k + ex, cy - 4 * k), (x + s * 8 * k + ex, cy - 13 * k)], TINTA, 3.5 * k)
        L.d.arc((L.S(x - 12 * k + ex), L.S(cy + 24 * k), L.S(x + 12 * k + ex), L.S(cy + 36 * k)), 200, 340, fill=TINTA, width=int(L.S(3.5 * k)))
    elif ojos == "cerrados":
        for s in (-1, 1):
            L.d.arc((L.S(x + s * 17 * k + ex - 8 * k), L.S(cy), L.S(x + s * 17 * k + ex + 8 * k), L.S(cy + 10 * k)), 0, 180, fill=TINTA, width=int(L.S(3.5 * k)))
        K.linea(L, [(x - 10 * k + ex, cy + 28 * k), (x + 10 * k + ex, cy + 28 * k)], TINTA, 3.5 * k)
    else:
        for s in (-1, 1):
            K.circulo(L, x + s * 17 * k + ex, cy + 4 * k, 5.5 * k, TINTA)
        K.linea(L, [(x - 12 * k + ex, cy + 26 * k), (x + 12 * k + ex, cy + 26 * k)], TINTA, 3.5 * k)
    if sudor >= 0:
        sy = cy - 14 * k + 40 * k * sudor
        sx = x - mira * 40 * k
        K.poligono(L, [(sx, sy - 16 * k), (sx - 7 * k, sy), (sx + 7 * k, sy)], (150, 204, 232), TINTA, 2)
        K.circulo(L, sx, sy + 2 * k, 7.5 * k, (150, 204, 232), TINTA, 2)


def seiza(L, x, y, alto=420, t=0.0, mira=1, inclina=0.0, temblor=0.0, ojos="cerrados", casco=True):
    """Piloto de rodillas (seiza), de frente. y = suelo. inclina 0..1 = agacha la cabeza."""
    k = alto / 420
    x = x + math.sin(t * 47) * temblor * 4 * k
    lean = mira * 34 * k * inclina
    hom = y - 236 * k + 22 * k * inclina
    K.poligono(L, [(x - 62 * k + lean, hom - 6 * k), (x + 62 * k + lean, hom - 6 * k), (x + 66 * k, y - 40 * k), (x - 66 * k, y - 40 * k)], P["caqui"], TINTA, 5)
    K.caja_red(L, x - 108 * k, y - 66 * k, x + 108 * k, y + 4 * k, 32 * k, P["oliva"], TINTA, 5)
    for s in (-1, 1):
        K.miembro(L, [(x + s * 58 * k + lean, hom + 12 * k), (x + s * 74 * k + lean * 0.5, hom + 100 * k), (x + s * 50 * k, y - 62 * k)], P["caqui"], 28 * k)
        K.circulo(L, x + s * 50 * k, y - 62 * k, 14 * k, P["piel"], TINTA, 4)
    cy = hom - 62 * k
    K.caja_red(L, x - 16 * k + lean, cy + 30 * k, x + 16 * k + lean, hom + 4 * k, 6 * k, P["piel2"], TINTA, 4)
    K.caja_red(L, x - 40 * k + lean, hom - 12 * k, x + 40 * k + lean, hom + 14 * k, 12 * k, P["blanco"], TINTA, 4)
    cabeza_piloto(L, x + lean * 1.3, cy + 10 * k * inclina, k, mira, ojos, casco=casco)


ROPA_OF = {"cabeza": "gorra", "torso": (112, 108, 74), "piernas": (86, 84, 58), "botas": (40, 36, 32), "gorra": (112, 108, 74)}


def mano_de(x, y, alto, ang, mira, t):
    """Dónde queda la mano derecha de K.persona (misma cuenta que el kit) y hacia dónde apunta el antebrazo."""
    k = alto / 420.0
    hom = y - 330 * k + math.sin(t * 2.2) * 3 * k
    hx = x + 58 * k
    a = math.radians(ang)
    L1 = 92 * k
    codo = (hx + mira * math.sin(a) * L1 * 0.95, hom + math.cos(a) * L1)
    mano = (codo[0] + mira * math.sin(a * 1.1) * L1 * 0.9, codo[1] + math.cos(a * 1.1) * L1 * 0.9)
    return mano, (mira * math.sin(a * 1.1), math.cos(a * 1.1)), k


def oficial(L, x, y, alto=900, ang=10, t=0.0, mira=-1, espada=True):
    """Oficial con gorra. ang = ángulo del brazo derecho (170 arriba, 60 golpe). Con espada de bambú (shinai)."""
    K.persona(L, x, y, alto=alto, ropa=ROPA_OF, pose={"brazo_der": ang, "brazo_izq": 10}, mira=mira, t=t)
    if espada:
        (mx, my), (dx, dy), k = mano_de(x, y, alto, ang, mira, t)
        lar = 0.5 * alto
        x0, y0 = mx - dx * 40 * k, my - dy * 40 * k
        x1, y1 = mx + dx * lar, my + dy * lar
        K.linea(L, [(x0, y0), (x1, y1)], TINTA, 17 * k)
        K.linea(L, [(x0, y0), (x1, y1)], (218, 194, 124), 10 * k)
        for f in (0.35, 0.7, 0.98):
            K.circulo(L, mx + dx * lar * f, my + dy * lar * f, 6 * k, (120, 92, 50))
        K.circulo(L, mx, my, 14 * k, P["piel"], TINTA, 4)


def civil(L, x, y, alto=800, t=0.0, mira=1, pelo=(70, 64, 60), torso=(92, 90, 96)):
    K.persona(L, x, y, alto=alto, ropa={"cabeza": "nada", "torso": torso, "piernas": (70, 68, 74), "botas": (50, 44, 40)}, mira=mira, t=t)
    k = alto / 420.0
    cy = y - 330 * k + math.sin(t * 2.2) * 3 * k - 62 * k
    L.d.chord((L.S(x - 54 * k), L.S(cy - 58 * k), L.S(x + 54 * k), L.S(cy + 20 * k)), 180, 360, fill=pelo, outline=TINTA, width=int(L.S(4)))


def golpe_u(t, t0, dur=0.11, queda=1.1, sube=0.5):
    """0 = espada arriba, 1 = abajo (pegó). Queda abajo `queda` s y sube en `sube` s."""
    if t < t0:
        return 0.0
    if t < t0 + dur:
        return sale((t - t0) / dur)
    return 1.0 - suave((t - t0 - queda) / sube)


# ------------------------------------------------------------------ fondos y objetos
def atardecer(L, y1=1150):
    K.cielo_bandas(L, [(120, 70, 84), (170, 96, 92), (214, 130, 100), (236, 170, 120), (246, 204, 150)], 0, y1)
    K.circulo(L, 300, y1 - 40, 120, (252, 226, 170))


def pista_tarde(L):
    atardecer(L)
    V.lomas(L, 1110, 200, (120, 92, 96), 0.4)
    V.lomas(L, 1160, 110, (96, 84, 76), 2.2)
    V.pista_suelo(L)


def sala(L, tono=(176, 156, 124)):
    L.d.rectangle((0, 0, L.S(W), L.S(1300)), fill=tono)
    for i in range(7):
        L.d.line([L.pt(80 + i * 160, 0), L.pt(80 + i * 160, 1300)], fill=tuple(int(c * 0.86) for c in tono), width=int(L.S(10)))
    L.d.rectangle((0, L.S(1300), L.S(W), L.S(H)), fill=(122, 96, 70))
    for i in range(8):
        L.d.line([L.pt(0, 1330 + i * 80), L.pt(W, 1330 + i * 80)], fill=(104, 82, 60), width=int(L.S(4)))
    L.d.line([L.pt(0, 1300), L.pt(W, 1300)], fill=TINTA, width=int(L.S(6)))


def noche(L, t):
    K.cielo_bandas(L, [(18, 22, 40), (26, 32, 58), (36, 44, 74), (48, 56, 88)], 0, 1250)
    random.seed(7)
    for i in range(40):
        x, y = random.uniform(0, W), random.uniform(0, 900)
        r = random.uniform(2, 4.5) * (0.7 + 0.3 * math.sin(t * 3 + i))
        K.circulo(L, x, y, r, (236, 232, 210))
    K.circulo(L, 800, 330, 90, (240, 234, 204))
    K.circulo(L, 840, 300, 84, (26, 32, 58))
    V.lomas(L, 1180, 160, (22, 24, 34), 0.8)
    L.d.rectangle((0, L.S(1240), L.S(W), L.S(H)), fill=(30, 30, 36))


def azaleas(L, x, y, s=1.0, t=0.0, n=8):
    random.seed(21)
    flores = []
    for i in range(n):
        fx = x + random.uniform(-110, 110) * s + math.sin(t * 2.4 + i) * 5 * s
        fy = y - random.uniform(150, 280) * s
        K.linea(L, [(x, y), (fx, fy)], (78, 112, 56), 8 * s)
        K.elipse(L, (x + fx) / 2 + 16 * s, (y + fy) / 2, 22 * s, 9 * s, (96, 136, 70), TINTA, 2)
        flores.append((fx, fy, random.choice([(232, 108, 150), (240, 140, 172), (214, 84, 128)])))
    for fx, fy, c in flores:
        for j in range(5):
            a = j * 2 * math.pi / 5 + 0.3
            K.circulo(L, fx + math.cos(a) * 20 * s, fy + math.sin(a) * 20 * s, 18 * s, c, TINTA, 2)
        K.circulo(L, fx, fy, 8 * s, (250, 224, 140))
    K.caja_red(L, x - 34 * s, y - 20 * s, x + 34 * s, y + 70 * s, 12 * s, P["blanco"], TINTA, 3)


def casa(L, x, y, w=760, h=420):
    K.caja_red(L, x - w / 2, y - h, x + w / 2, y, 6, (206, 182, 140), TINTA, 5)
    for i in range(5):
        xx = x - w / 2 + 20 + i * (w - 40) / 4
        L.d.line([L.pt(xx, y - h), L.pt(xx, y)], fill=(110, 82, 56), width=int(L.S(12)))
    for j in range(2):     # shoji
        x0 = x - w / 2 + 60 + j * (w / 2)
        K.caja_red(L, x0, y - h + 70, x0 + w / 2 - 120, y - 120, 2, (240, 232, 210), TINTA, 3)
        for g in range(1, 4):
            L.d.line([L.pt(x0 + g * (w / 2 - 120) / 4, y - h + 70), L.pt(x0 + g * (w / 2 - 120) / 4, y - 120)], fill=(150, 120, 90), width=int(L.S(3)))
        for g in range(1, 3):
            L.d.line([L.pt(x0, y - h + 70 + g * (h - 190) / 3), L.pt(x0 + w / 2 - 120, y - h + 70 + g * (h - 190) / 3)], fill=(150, 120, 90), width=int(L.S(3)))
    K.poligono(L, [(x - w / 2 - 80, y - h), (x - w / 2 + 60, y - h - 170), (x + w / 2 - 60, y - h - 170), (x + w / 2 + 80, y - h)], (66, 64, 70), TINTA, 5)
    for i in range(9):
        L.d.line([L.pt(x - w / 2 - 60 + i * (w + 120) / 8, y - h), L.pt(x - w / 2 + 70 + i * (w - 130) / 8, y - h - 165)], fill=(90, 88, 96), width=int(L.S(5)))


def nube(L, x, y, s=1.0, c=(236, 238, 238)):
    for dx, dy, r in ((-90, 10, 60), (-30, -30, 80), (50, -10, 70), (110, 15, 50), (0, 25, 70)):
        K.circulo(L, x + dx * s, y + dy * s, r * s, c)


def humo_motor(L, x, y, t, t0, dir_x=-1, n=12, s=1.0):
    for i in range(n):
        u = ((t - t0) * 1.6 + i / n) % 1.0
        if t - t0 < i / n / 1.6:
            continue
        r = (14 + 46 * u) * s
        K.circulo(L, x + dir_x * 420 * u * s, y - 60 * u * s + math.sin(i * 7) * 20 * s, r, (40, 38, 36, int(220 * (1 - u))))


def balanza(L, cx, cy, ang, izq_u, der_u, t):
    a = math.radians(ang)
    K.poligono(L, [(cx - 170, 1760), (cx + 170, 1760), (cx + 30, 1660), (cx - 30, 1660)], (120, 96, 64), TINTA, 5)
    K.caja_red(L, cx - 18, cy, cx + 18, 1680, 8, (150, 120, 80), TINTA, 4)
    lx, ly = cx - 340 * math.cos(a), cy - 340 * math.sin(a)
    rx, ry = cx + 340 * math.cos(a), cy + 340 * math.sin(a)
    K.linea(L, [(lx, ly), (rx, ry)], TINTA, 30)
    K.linea(L, [(lx, ly), (rx, ry)], (186, 150, 96), 18)
    K.circulo(L, cx, cy, 30, P["ocre"], TINTA, 5)
    for (ex, ey), u, txt, col, tam in (((lx, ly), izq_u, "MORIR", (44, 40, 40), 70), ((rx, ry), der_u, "VOLVER VIVO", P["rojo"], 64)):
        py = ey + 300
        K.linea(L, [(ex, ey), (ex - 150, py)], TINTA, 5)
        K.linea(L, [(ex, ey), (ex + 150, py)], TINTA, 5)
        if u > 0:
            caida = -520 * (1 - sale(u))
            w = 300 if txt == "MORIR" else 400
            K.caja_red(L, ex - w / 2, py - 150 + caida, ex + w / 2, py - 6 + caida, 22, col, TINTA, 6)
            K.texto(L, txt, ex, py - 78 + caida, tam if txt == "MORIR" else 46, P["blanco"])
        L.d.chord((L.S(ex - 180), L.S(py - 40), L.S(ex + 180), L.S(py + 50)), 0, 180, fill=(150, 120, 80), outline=TINTA, width=int(L.S(5)))
        L.d.line([L.pt(ex - 180, py + 5), L.pt(ex + 180, py + 5)], fill=TINTA, width=int(L.S(5)))


# ------------------------------------------------------------------ sellos sobre el cuadro final
_FONTS = {}


def fuente(tam):
    if tam not in _FONTS:
        _FONTS[tam] = ImageFont.truetype(K.FONT, tam)
    return _FONTS[tam]


def sello(im, s, cx, cy, t, t0, tam=170, color=(200, 36, 32), ang=-9):
    if t < t0:
        return
    e = (t - t0) / 0.13
    esc = 1.9 - 0.9 * sale(e)
    f = fuente(max(10, int(tam * esc)))
    bx = f.getbbox(s)
    tw_, th = bx[2] - bx[0], bx[3] - bx[1]
    pad = int(30 * esc)
    capa = Image.new("RGBA", (tw_ + 2 * pad, th + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    a = int(235 * clamp(e * 2))
    d.rounded_rectangle((4, 4, capa.width - 5, capa.height - 5), radius=int(18 * esc), outline=(*color, a), width=max(4, int(12 * esc)))
    d.text((pad - bx[0], pad - bx[1]), s, font=f, fill=(*color, a))
    capa = capa.rotate(ang, expand=True, resample=Image.BICUBIC)
    im.paste(capa, (int(cx - capa.width / 2), int(cy - capa.height / 2)), capa)


def recreacion(L):
    K.pildora(L, "RECREACIÓN", 880, 230, 30, fondo=(30, 32, 36), tinta=P["blanco"])


# ------------------------------------------------------------------ escenas
@dibujo
def _castigo(L, t, a, b, cerca=False, golpes=(T_GOLPE1,)):
    pista_tarde(L)
    V.barraca(L, 640, 1170, 260, 110)
    u = golpe_u(t, golpes[0]) if len(golpes) == 1 else max(golpe_u(t, g, queda=0.2, sube=0.35) for g in golpes)
    if cerca:
        seiza(L, 330, 1660, alto=1000, t=t, mira=1, inclina=0.5 + 0.5 * u, temblor=0.4 + u, ojos="cerrados")
        oficial(L, 820, 1980, alto=1400, ang=170 - 120 * u, t=t, mira=-1)
        fx, fy = 250, 1260
    else:
        seiza(L, 400, 1900, alto=820, t=t, mira=1, inclina=0.4 + 0.6 * u, temblor=0.3 + u, ojos="cerrados")
        oficial(L, 780, 1900, alto=1100, ang=170 - 120 * u, t=t, mira=-1)
        fx, fy = 300, 1430
    for g in golpes:
        if 0 <= t - g < 0.16:
            e = (t - g) / 0.16
            for j in range(9):
                an = j * 2 * math.pi / 9 + 0.3
                r0, r1 = 70 + 90 * e, 150 + 160 * e
                K.linea(L, [(fx + math.cos(an) * r0, fy + math.sin(an) * r0), (fx + math.cos(an) * r1, fy + math.sin(an) * r1)], (255, 244, 200), 14)
    recreacion(L)


def p1(t, a, b):
    im = _castigo(t, a, b)
    sello(im, "VIVO", 400, 640, t, T_VIVO1, tam=220)
    return im


@dibujo
def p2(L, t, a, b):
    pista_tarde(L)
    V.barraca(L, 760, 1180, 240, 100)
    K.avion_lateral(L, 620, 1250, largo=680, mira=-1, helice_t=0)
    K.caja_red(L, 540, 1286, 710, 1322, 16, (58, 58, 54), TINTA, 4)
    K.persona(L, 860, 1780, alto=900, ropa={"hachimaki": True}, mira=-1, t=t)
    K.pildora(L, "SU MISIÓN", 540, 330, 60, fondo=P["blanco"], escala=pop(t - a - 0.05))
    if t > tw("misión") + 0.3:
        K.flecha(L, 420, 1500, 580, 1340, P["rojo"], 14, u=sale((t - tw("misión") - 0.3) / 0.25))
        K.pildora(L, "BOMBA", 360, 1560, 44, fondo=P["rojo"], tinta=P["blanco"], escala=pop(t - tw("misión") - 0.3))
    recreacion(L)


@dibujo
def p3(L, t, a, b):
    u = clamp((t - a) / (b - a + 0.1))
    V.cielo_mar(L)
    V.flak(L, t, a + 0.1, n=8, semilla=5, zona=(60, 100, 1020, 900))
    V.mar(L, 1500, t=t)
    V.portaaviones(L, 540, 1520 + 160 * u ** 2, 700 + 600 * u ** 2)
    esc = 0.25 + 1.9 * u ** 1.7
    x = 650 - 100 * u; y = 300 + 560 * u
    V.humo_estela(L, [(x + (i + 1) * 30 * esc, y - (i + 1) * 60 * esc) for i in range(10)], 10 * esc, 40 * esc)
    V.avion_frente(L, x, y, escala=esc, inclina=0.1 * math.sin(t * 3))
    K.caja_red(L, x - 40 * esc, y + 60 * esc, x + 40 * esc, y + 100 * esc, 14 * esc, (58, 58, 54), TINTA, 4)


@dibujo
def p4(L, t, a, b):
    u = (t - a) / (b - a)
    V.cielo_mar(L)
    V.trazadoras(L, t, n=18, desde_y=1250)
    V.flak(L, t, a - 0.6, n=10, zona=(80, 120, 1000, 700))
    esc = 0.12 + 0.5 * u ** 1.5
    V.avion_frente(L, 600 - 80 * u, 380 + 180 * u, escala=esc, inclina=0.2 * math.sin(t * 4))
    V.mar(L, t=t)
    V.portaaviones(L, 540 - 60 * u, 1300, 1150)
    for i, x in enumerate((200, 290, 380, 470)):
        V.marinero(L, x - 60 * u, 1214, 160, arriba=sale((t - a - 0.15 * i) / 0.4) if i % 2 == 0 else 0, t=t + i)
    if (t * 4) % 1 < 0.5:
        K.circulo(L, 780 - 60 * u, 1060, 14, (255, 80, 60))
    if t > tw("Estados") - 0.05:
        K.pildora(L, "ESTADOS UNIDOS", 540, 330, 56, fondo=P["azul"], tinta=P["blanco"], escala=pop(t - tw("Estados") + 0.05))


@dibujo
def p5(L, t, a, b):
    u = suave((t - a) / (b - a))
    V.mapa_pacifico(L, t, (138 - 2 * u, 12 + 6 * u, 540, 960), 1650 + 450 * u, perdidas_u=(t - a) / 1.2, flechas_u=(t - a - 0.2) / 1.0)
    K.pildora(L, "JAPÓN PIERDE LA GUERRA", 540, 330, 52, fondo=P["blanco"], escala=pop(t - a - 0.05))


@dibujo
def p6(L, t, a, b):
    u = suave((t - a) / (b - a))
    f = V.mapa_japon(L, (137.5, 36.5, 540, 760), 2500 + 400 * u, colores={"JPN": P["rojo"]})
    for i, (x0, y0) in enumerate(((60, 300), (1020, 260), (1040, 1500), (80, 1560), (540, 1800))):
        ux = sale((t - a - 0.08 * i) / 0.6)
        tx, ty = 540 + (x0 - 540) * 0.32, 760 + (y0 - 760) * 0.32
        if ux > 0:
            K.flecha(L, x0, y0, tx, ty, (40, 70, 120), 24, u=ux)
    if t > tw("desesperado") - 0.05:
        K.pildora(L, "DESESPERADO", 540, 330, 66, fondo=P["rojo"], tinta=P["blanco"], escala=pop(t - tw("desesperado") + 0.05))


@dibujo
def p7(L, t, a, b):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=P["papel"])
    K.texto(L, "?", 760, 560 + 10 * math.sin(t * 4), 380, P["rojo"], borde=10)
    K.viejo(L, 480, 1850, alto=900, boca=V.boca(t), t=t, gesto="tazon", mira=1)


@dibujo
def p8(L, t, a, b):
    u = suave((t - a) / (b - a))
    V.mapa_japon(L, (136, 35.5, 540, 760), 2600 + 300 * u, colores={"JPN": P["rojo"]})
    K.pildora(L, "JAPÓN, AÑOS 40", 540, 330, 54, escala=pop(t - a - 0.05))


@dibujo
def p9(L, t, a, b):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=P["papel"])
    K.texto(L, "MORIR POR EL PAÍS", 540, 520, 76, TINTA)
    s = 1 + 0.04 * suave((t - a) / (b - a))
    K.texto(L, "PECADO", 540, 780, int(190 * s), TINTA)
    t0 = tw("pecado") - 0.05
    if t > t0:
        u = sale((t - t0) / 0.2)
        K.linea(L, [(140, 820), (140 + 800 * u, 740)], P["rojo"], 30)
    if t > t0 + 0.3:
        K.texto(L, "NO", 540, 1450, int(240 * pop(t - t0 - 0.3)), P["rojo"], borde=8)


@dibujo
def p10(L, t, a, b):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=(240, 226, 196))
    cx, cy = 540, 820
    rot = (t - a) * 0.25
    for i in range(16):
        a0 = rot + i * 2 * math.pi / 16
        a1 = a0 + math.pi / 16
        K.poligono(L, [(cx, cy), (cx + 1800 * math.cos(a0), cy + 1800 * math.sin(a0)), (cx + 1800 * math.cos(a1), cy + 1800 * math.sin(a1))], (210, 92, 78))
    K.circulo(L, cx, cy, 250 * (0.9 + 0.1 * sale((t - a) / 0.4)), P["rojo"], TINTA, 6)
    if t > tw("mayor") - 0.1:
        K.pildora(L, "EL MAYOR HONOR", 540, 1500, 72, fondo=P["blanco"], escala=pop(t - tw("mayor") + 0.1))


@dibujo
def p11(L, t, a, b):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=(232, 214, 186))
    K.circulo(L, 540, 760, 420, P["rojo"])
    SAM(L, 540, 1560 + 30 * (1 - sale((t - a) / 0.4)), alto=1000, t=t)
    K.pildora(L, "EL CÓDIGO SAMURÁI", 540, 330, 52, fondo=P["blanco"], escala=pop(t - a - 0.05))


@dibujo
def p12(L, t, a, b):
    K.cielo_bandas(L, [(70, 46, 58), (104, 64, 70), (140, 86, 82), (170, 108, 92)], 0, H)
    k = 6.4 + 0.5 * suave((t - a) / (b - a))
    x = 540 + math.sin(t * 50) * 3
    cy = 700
    K.caja_red(L, x - 120 * k, cy + 70 * k, x + 120 * k, cy + 260 * k, 50 * k, P["caqui"], TINTA, 6)
    K.caja_red(L, x - 16 * k, cy + 30 * k, x + 16 * k, cy + 70 * k, 6 * k, P["piel2"], TINTA, 4)
    K.caja_red(L, x - 44 * k, cy + 52 * k, x + 44 * k, cy + 80 * k, 12 * k, P["blanco"], TINTA, 5)
    cabeza_piloto(L, x, cy, k, mira=1, ojos="miedo", sudor=clamp((t - a - 0.3) / 0.9))
    K.pildora(L, "KENICHIRO OONUKI", 540, 330, 50, fondo=P["blanco"], escala=pop(t - a - 0.05))
    recreacion(L)


@dibujo
def p13(L, t, a, b):
    sala(L, (150, 132, 108))
    for i in range(5):
        x = 140 + i * 200
        mira = 1 if i % 2 == 0 else -1
        if t > a + 0.25 + 0.12 * i:
            mira = -mira
        K.persona(L, x, 1720, alto=880, ropa={"hachimaki": True}, mira=mira, t=t + i)
        k = 880 / 420
        cy = 1720 - 330 * k + math.sin((t + i) * 2.2) * 3 * k - 62 * k
        su = (t - a - 0.15 * i) / 0.8
        if su > 0:
            sx = x - mira * 40 * k
            sy = cy - 14 * k + 40 * k * clamp(su)
            K.poligono(L, [(sx, sy - 16 * k), (sx - 7 * k, sy), (sx + 7 * k, sy)], (150, 204, 232), TINTA, 2)
            K.circulo(L, sx, sy + 2 * k, 7.5 * k, (150, 204, 232), TINTA, 2)
    recreacion(L)


def p14(t, a, b):
    im, ven, _ = V.foto_plano("foto_201.jpg", t, a, b, 1.5, 1.75, (0.35, 0.45), (0.62, 0.45), rot=1.2)
    V.etiqueta_real(im, t, a + 0.05)
    V.pildora_t(im, "¿VOLUNTARIOS?", 540, 430, tw("voluntarios") - 0.05, t, tam=62, fondo=P["ocre"])
    V.pildora_t(im, "«ABSURDO»", 540, 1420, tw("absurdo") - 0.05, t, tam=70, fondo=P["rojo"], tinta=(255, 255, 255))
    return im


@dibujo
def p15(L, t, a, b):
    noche(L, t)
    V.barraca(L, 400, 1250, 520, 190)
    for i in range(3):
        K.caja_red(L, 430 + i * 160, 1250 - 160, 510 + i * 160, 1250 - 100, 3, (255, 210, 120), TINTA, 3)
    K.circulo(L, 610, 1120, 260, (255, 210, 120, 40))
    K.pildora(L, "UNA NOCHE PARA PENSAR", 540, 330, 54, fondo=P["blanco"], escala=pop(t - tw("noche") + 0.1))
    recreacion(L)


FRASE = "SÍ, CON TODO MI CORAZÓN"


@dibujo
def p16(L, t, a, b):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=(96, 80, 64))
    K.poligono(L, [(90, 300), (1000, 340), (980, 1780), (70, 1740)], (244, 236, 216), TINTA, 6)
    for i in range(12):
        y = 760 + i * 80
        L.d.line([L.pt(150, y), L.pt(930, y + 30)], fill=(200, 190, 170), width=int(L.S(3)))
    K.texto(L, "MISIÓN ESPECIAL", 540, 470, 66, TINTA)
    K.texto(L, "¿TE OFRECES?", 540, 580, 60, (120, 100, 80))
    # se escribe al ritmo de la voz
    t_s = [tw("Sí", 26), tw("con", 26), tw("todo", 26), tw("mi", 27), tw("corazón")]
    trozos = ["SÍ,", " CON", " TODO", " MI", " CORAZÓN"]
    txt = ""
    for ts, tr in zip(t_s, trozos):
        if t >= ts:
            txt += tr
    if txt:
        lineas = [txt[:3], txt[3:].strip()] if len(txt) > 3 else [txt]
        K.texto(L, lineas[0], 540, 760, 150, (30, 40, 90))
        if len(lineas) > 1 and lineas[1]:
            K.texto(L, lineas[1], 540, 920, 62, (30, 40, 90))
    if t > tw("corazón") + 0.35:
        K.pildora(L, "LO CONTRARIO DE LO QUE SENTÍAN", 540, 1500, 46, fondo=P["rojo"], tinta=P["blanco"], escala=pop(t - tw("corazón") - 0.35))
    recreacion(L)


@dibujo
def p17(L, t, a, b):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=P["papel"])
    K.texto(L, "¿POR QUÉ?", 540, 520 + 8 * math.sin(t * 6), 150, P["rojo"], borde=8)
    K.viejo(L, 560, 1880, alto=980, boca=V.boca(t), t=t, gesto="apunta", mira=-1)


def _cobarde_fondo(t, a, b):
    @dibujo
    def f(L, t, a, b):
        sala(L)
        K.persona(L, 330, 1720, alto=900, ropa={"hachimaki": True}, mira=1, t=t)
        oficial(L, 790, 1740, alto=960, ang=92, t=t, mira=-1, espada=False)
        recreacion(L)
    return f(t, a, b)


def p18(t, a, b):
    im = _cobarde_fondo(t, a, b)
    sello(im, "COBARDE", 540, 560, t, T_COBARDE, tam=150, ang=-8)
    return im


@dibujo
def _familia(L, t, a, b):
    K.cielo_bandas(L, [(196, 206, 210), (210, 216, 214), (222, 222, 212)], 0, 1350)
    L.d.rectangle((0, L.S(1350), L.S(W), L.S(H)), fill=(150, 134, 100))
    casa(L, 540, 1360, 860, 460)
    mujer(L, 380, 1820, alto=760, embarazada=False, mira=1, t=t)
    civil(L, 720, 1830, alto=860, t=t, mira=-1, pelo=(150, 146, 140))
    u = sale((t - a - 0.05) / 0.45)
    ex, ey = -200 + 740 * u, 520 + 60 * math.sin(u * math.pi)
    K.caja_red(L, ex - 110, ey - 70, ex + 110, ey + 70, 8, P["blanco"], TINTA, 5)
    K.poligono(L, [(ex - 110, ey - 70), (ex, ey + 10), (ex + 110, ey - 70)], (230, 224, 210), TINTA, 4)
    K.circulo(L, ex, ey + 10, 22, P["rojo"])
    recreacion(L)


def p19(t, a, b):
    im = _familia(t, a, b)
    sello(im, "VERGÜENZA", 540, 830, t, T_FAMILIA, tam=140, ang=7)
    return im


def mujer(L, x, y, alto=700, embarazada=True, mira=-1, t=0.0):
    k = alto / 700
    hom = y - 560 * k
    cad = y - 300 * k
    tela, tela2 = (122, 104, 132), (92, 80, 104)
    K.poligono(L, [(x - 70 * k, cad), (x + 70 * k, cad), (x + 60 * k, y - 10 * k), (x + 10 * k, y - 10 * k), (x, cad + 60 * k),
                   (x - 10 * k, y - 10 * k), (x - 60 * k, y - 10 * k)], tela2, TINTA, 5)
    for s in (-1, 1):
        K.caja_red(L, x + s * 35 * k - 30 * k, y - 22 * k, x + s * 35 * k + 30 * k, y + 2 * k, 8 * k, (60, 50, 44), TINTA, 4)
    K.caja_red(L, x - 78 * k, hom, x + 78 * k, cad + 20 * k, 40 * k, tela, TINTA, 5)
    for s in (-1, 1):
        K.miembro(L, [(x + s * 70 * k, hom + 30 * k), (x + s * 84 * k, cad - 80 * k), (x + s * 50 * k, cad - 40 * k)], tela, 30 * k)
    cy = hom - 76 * k
    K.caja_red(L, x - 18 * k, cy + 40 * k, x + 18 * k, hom + 6 * k, 6 * k, P["piel2"], TINTA, 4)
    K.circulo(L, x, cy, 62 * k, P["piel"], TINTA, 5)
    L.d.chord((L.S(x - 66 * k), L.S(cy - 70 * k), L.S(x + 66 * k), L.S(cy + 40 * k)), 180, 360, fill=(70, 66, 64), outline=TINTA, width=int(L.S(5)))
    K.circulo(L, x - mira * 52 * k, cy - 48 * k, 26 * k, (70, 66, 64), TINTA, 4)
    for s in (-1, 1):
        K.circulo(L, x + s * 20 * k + mira * 10 * k, cy + 6 * k, 6 * k, TINTA)
        K.linea(L, [(x + s * 30 * k + mira * 10 * k, cy - 6 * k), (x + s * 10 * k + mira * 10 * k, cy - 14 * k)], TINTA, 3.5 * k)
    L.d.arc((L.S(x - 12 * k + mira * 10 * k), L.S(cy + 26 * k), L.S(x + 12 * k + mira * 10 * k), L.S(cy + 40 * k)), 200, 340, fill=TINTA, width=int(L.S(3.5 * k)))


@dibujo
def p20(L, t, a, b):
    pista_tarde(L)
    x0 = 560
    K.avion_lateral(L, x0, 1250, largo=720, mira=-1, helice_t=0)
    nariz = x0 - 190 * 720 / 420
    humo_motor(L, nariz + 20, 1220, t, a, dir_x=0.25, n=14, s=1.4)
    K.persona(L, 900, 1780, alto=900, ropa={"hachimaki": True}, mira=-1, t=t)
    if t > tw("falló") - 0.05:
        K.pildora(L, "FALLA MECÁNICA", 540, 330, 56, fondo=P["ocre"], escala=pop(t - tw("falló") + 0.05))
    recreacion(L)


@dibujo
def p21(L, t, a, b):
    pista_tarde(L)
    for i in range(3):
        u = clamp((t - a - 0.3 * i + 0.5) / 2.4)
        x = 60 + 1100 * u
        y = 1130 - 30 * i - 600 * max(0.0, u - 0.2) ** 1.4
        K.avion_lateral(L, x, y, largo=540 - 90 * i, mira=1, helice_t=t)
    K.persona(L, 230, 1830, alto=980, ropa={"hachimaki": True}, mira=1, t=t)
    recreacion(L)


@dibujo
def p22(L, t, a, b):
    atardecer(L, H)
    s = 2.3 + 0.2 * suave((t - a) / (b - a))
    azaleas(L, 540, 1500, s=s, t=t)
    for sx in (-1, 1):
        K.circulo(L, 540 + sx * 70, 1560, 46, P["piel"], TINTA, 5)
    if t > tw("azaleas") - 0.05:
        K.pildora(L, "AZALEAS", 540, 330, 60, fondo=P["blanco"], escala=pop(t - tw("azaleas") + 0.05))
    recreacion(L)


@dibujo
def p23(L, t, a, b):
    atardecer(L, H)
    sh = math.sin(t * 60) * 3
    k = 4.2
    cx, cy = 560 + sh, 720
    K.caja_red(L, cx - 130 * k, cy + 60 * k, cx + 130 * k, cy + 300 * k, 40 * k, P["caqui"], TINTA, 6)
    K.caja_red(L, cx - 44 * k, cy + 52 * k, cx + 44 * k, cy + 80 * k, 12 * k, P["blanco"], TINTA, 5)
    cabeza_piloto(L, cx, cy, k, mira=-1, ojos="triste")
    K.poligono(L, [(-60, 1100 + sh), (1140, 1040 + sh), (1140, H), (-60, H)], VERDE_AV, TINTA, 8)
    K.circulo(L, 240, 1500 + sh, 150, P["rojo"], P["blanco"], 8)
    L.d.arc((L.S(cx - 420), L.S(cy - 440), L.S(cx + 420), L.S(cy + 760)), 180, 360, fill=TINTA, width=int(L.S(16)))
    K.linea(L, [(cx - 420, 1100 + sh), (cx - 420, cy + 160)], TINTA, 16)
    K.linea(L, [(cx + 420, 1060 + sh), (cx + 420, cy + 160)], TINTA, 16)
    if t > tw("Me", 37.5) - 0.05:
        K.pildora(L, "«ME ADELANTO»", 540, 1600, 66, fondo=P["blanco"], escala=pop(t - tw("Me", 37.5) + 0.05))
    recreacion(L)


@dibujo
def p24(L, t, a, b):
    pista_tarde(L)
    u = clamp((t - a) / (b - a))
    K.avion_lateral(L, 640 + 500 * u, 1140 - 380 * u ** 1.6, largo=420 - 120 * u, mira=1, helice_t=t)
    K.persona(L, 300, 1820, alto=920, ropa={"hachimaki": True}, mira=1, t=t, pose={"brazo_der": 40, "brazo_izq": 30})
    azaleas(L, 380, 1410, s=0.6, t=t, n=5)
    if t > tw("Quería") - 0.05:
        K.pildora(L, "«QUERÍA IR CONTIGO»", 540, 330, 56, fondo=P["blanco"], escala=pop(t - tw("Quería") + 0.05))
    recreacion(L)


@dibujo
def p25(L, t, a, b):
    V.cielo_mar(L)
    V.mar(L, 1560, t=t)
    for i in range(4):
        nube(L, (1200 - (t - a) * 500 * (1 + 0.3 * i) + i * 420) % 1600 - 250, 300 + i * 260, 1.2 - 0.15 * i)
    tp = tw("pero", 41.0)
    caida = 220 * clamp((t - tp - 0.3) / 1.3) ** 2
    sh = math.sin(t * 40) * 6 if t > tp else math.sin(t * 3) * 6
    x, y = 520, 820 + caida + sh
    if t > tp:
        humo_motor(L, x + 190 * 600 / 420, y - 10, t, tp, dir_x=-1, n=14, s=1.2)
    K.avion_lateral(L, x, y, largo=600, mira=1, helice_t=t if t < tp + 0.4 else 0)
    if t > tw("volvió", 41.8) - 0.05:
        K.pildora(L, "OTRA VEZ", 540, 330, 66, fondo=P["rojo"], tinta=P["blanco"], escala=pop(t - tw("volvió", 41.8) + 0.05))
    recreacion(L)


@dibujo
def p26(L, t, a, b):
    V.cielo_mar(L)
    V.mar(L, 1300, t=t)
    K.elipse(L, 780, 1330, 280, 56, (222, 208, 178), TINTA, 5)
    K.elipse(L, 800, 1316, 210, 40, (110, 128, 84), TINTA, 4)
    K.linea(L, [(880, 1300), (900, 1120)], (110, 82, 56), 16)
    for ang in (-150, -110, -60, -20):
        r = math.radians(ang)
        K.linea(L, [(900, 1120), (900 + 110 * math.cos(r), 1120 + 60 * math.sin(r) + 40)], (78, 112, 56), 14)
    u = clamp((t - a) / 1.45)
    x, y = 120 + 580 * u, 420 + 830 * u ** 1.3
    V.humo_estela(L, [(x - (i + 1) * 34, y - (i + 1) * 30) for i in range(10)], 10, 34)
    K.avion_lateral(L, x, y, largo=300, mira=1)
    if u >= 1:
        for i in range(6):
            v = (t - a - 1.45) * 2
            K.circulo(L, 700 + i * 30 - 40, 1240 - 30 * v, 20 + 40 * v, (200, 186, 150, int(180 * clamp(1 - v))))
    K.pildora(L, "ATERRIZAJE DE EMERGENCIA", 540, 330, 46, fondo=P["blanco"], escala=pop(t - a - 0.1))
    recreacion(L)


@dibujo
def _vivo(L, t, a, b):
    pista_tarde(L)
    V.barraca(L, 600, 1170, 300, 120)
    K.persona(L, 300, 1760, alto=900, ropa={"hachimaki": True}, mira=1, t=t)
    oficial(L, 700, 1740, alto=900, ang=10, t=t, mira=-1, espada=False)
    oficial(L, 900, 1700, alto=860, ang=10, t=t + 1, mira=-1, espada=True)
    recreacion(L)


def p27(t, a, b):
    im = _vivo(t, a, b)
    sello(im, "VIVO", 330, 600, t, T_VIVO2, tam=220, ang=-10)
    return im


def p28(t, a, b):
    return _castigo(t, a, b, cerca=True, golpes=(T_PEGA1, T_PEGA2))


@dibujo
def p29(L, t, a, b):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=(54, 48, 50))
    K.caja_red(L, 40, 1040, 1040, 1080, 6, (110, 82, 56), TINTA, 4)
    for i in range(5):
        x = 140 + i * 200
        K.caja_red(L, x - 80, 640, x + 80, 1020, 10, (150, 118, 72), TINTA, 5)
        K.caja_red(L, x - 62, 662, x + 62, 1000, 6, (226, 220, 206))
        cabeza_piloto(L, x, 820, 1.1, mira=1, ojos="normal")
        K.caja_red(L, x - 70, 950, x + 70, 1000, 10, P["caqui"])
        K.poligono(L, [(x + 20, 640), (x + 80, 640), (x + 80, 700)], (20, 20, 22))
        K.poligono(L, [(x - 80, 640), (x - 20, 640), (x - 80, 700)], (20, 20, 22))
        for j in range(5):
            yy = 600 - j * 70
            K.circulo(L, x + 20 * math.sin(t * 2 + j + i), yy - (t * 40) % 70, 6, (200, 200, 200, 90))
    seiza(L, 540, 1820, alto=760, t=t, mira=1, inclina=1.0, temblor=0.15, ojos="cerrados")
    if t > tw("vergüenza") - 0.05:
        K.pildora(L, "«UNA VERGÜENZA»", 540, 330, 66, fondo=P["rojo"], tinta=P["blanco"], escala=pop(t - tw("vergüenza") + 0.05))
    recreacion(L)


@dibujo
def p30(L, t, a, b):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=P["papel"])
    tm = tw("muerte")
    u = clamp((t - tm + 0.25) / 0.3)
    ang = -12 * sale(clamp((t - tm) / 0.3))
    balanza(L, 540, 560, ang, u if t > tm - 0.25 else 0, 0, t)
    K.pildora(L, "¿MIEDO A MORIR? SÍ", 540, 250, 56, fondo=P["blanco"], escala=pop(t - a - 0.05))


@dibujo
def p31(L, t, a, b):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=P["papel"])
    tv = tw("volver", 53.5)
    u = clamp((t - tv + 0.3) / 0.3)
    g = sale(clamp((t - tv) / 0.35))
    ang = -12 + 34 * g + (2 * math.sin((t - tv) * 18) * math.exp(-(t - tv) * 3) if t > tv else 0)
    balanza(L, 540, 560, ang, 1.0, u if t > tv - 0.3 else 0, t)
    if t > tw("más", 53) - 0.05:
        K.pildora(L, "MÁS MIEDO A…", 540, 250, 62, fondo=P["rojo"], tinta=P["blanco"], escala=pop(t - tw("más", 53) + 0.05))


# samurái: el mismo del Ep. 10c
sys.path.insert(0, os.path.abspath(os.path.join(AQUI, "../../ep10c-kamikaze-mente/escena2d")))


def SAM(L, x, y, alto=1000, t=0.0):
    k = alto / 1000
    osc = (40, 34, 34)
    K.poligono(L, [(x - 210 * k, y - 560 * k), (x + 210 * k, y - 560 * k), (x + 250 * k, y - 250 * k), (x - 250 * k, y - 250 * k)], (120, 40, 36), TINTA, 6)
    for i in range(4):
        yy = y - 520 * k + i * 70 * k
        L.d.line([L.pt(x - 220 * k, yy), L.pt(x + 220 * k, yy)], fill=TINTA, width=int(L.S(5)))
    K.poligono(L, [(x - 250 * k, y - 250 * k), (x + 250 * k, y - 250 * k), (x + 200 * k, y), (x - 200 * k, y)], osc, TINTA, 6)
    for s in (-1, 1):
        K.poligono(L, [(x + s * 200 * k, y - 600 * k), (x + s * 330 * k, y - 560 * k), (x + s * 320 * k, y - 400 * k), (x + s * 210 * k, y - 430 * k)], (120, 40, 36), TINTA, 6)
    cy = y - 700 * k
    K.circulo(L, x, cy, 110 * k, osc, TINTA, 6)
    L.d.chord((L.S(x - 170 * k), L.S(cy - 150 * k), L.S(x + 170 * k), L.S(cy + 60 * k)), 180, 360, fill=osc, outline=TINTA, width=int(L.S(6)))
    K.poligono(L, [(x - 150 * k, cy - 120 * k), (x - 230 * k, cy - 300 * k), (x - 120 * k, cy - 140 * k)], P["ocre"], TINTA, 5)
    K.poligono(L, [(x + 150 * k, cy - 120 * k), (x + 230 * k, cy - 300 * k), (x + 120 * k, cy - 140 * k)], P["ocre"], TINTA, 5)
    K.caja_red(L, x - 60 * k, cy - 10 * k, x + 60 * k, cy + 70 * k, 14 * k, (150, 50, 44), TINTA, 5)
    K.linea(L, [(x + 260 * k, y - 120 * k), (x - 160 * k, y - 980 * k)], TINTA, 26 * k)
    K.linea(L, [(x + 260 * k, y - 120 * k), (x - 160 * k, y - 980 * k)], (210, 214, 220), 14 * k)
    K.linea(L, [(x + 300 * k, y - 40 * k), (x + 250 * k, y - 140 * k)], (60, 40, 30), 30 * k)


FUN = {i: globals()[f"p{i}"] for i in range(1, 32)}
assert len(FUN) == len(T), (len(FUN), len(T))


# ------------------------------------------------------------------ subtítulos
def limpiar(w):
    for ch in ",.:;!¡?¿\"…«»":
        w = w.replace(ch, "")
    return w.upper()


TOK = [(limpiar(x["w"]), [i], x["w"][-1] in ".,:;?…") for i, x in enumerate(words)]
GRUPOS = """A ESTE PILOTO | KAMIKAZE | LO CASTIGARON | POR SEGUIR VIVO | SU MISIÓN | ESTRELLAR SU AVIÓN | CON UNA BOMBA | CONTRA UN BARCO |
DE ESTADOS UNIDOS | JAPÓN ESTABA | PERDIENDO LA GUERRA | Y ESTABA DESESPERADO | CÓMO ACEPTAS | MORIR ASÍ | EN EL JAPÓN | DE ESA ÉPOCA |
MORIR POR EL PAÍS | NO ERA PECADO | ERA EL MAYOR HONOR | EL DE LOS SAMURÁIS | PERO ÉL | TENÍA MIEDO | Y NO ERA | EL ÚNICO |
CUANDO PIDIERON | VOLUNTARIOS | A TODOS | LES PARECIÓ ABSURDO | LES DIERON | UNA NOCHE | PARA PENSARLO | Y TODOS ESCRIBIERON |
SÍ CON TODO | MI CORAZÓN | POR QUÉ | SI DECÍAS QUE NO | TE IBAN A LLAMAR | COBARDE | Y SE LO IBAN | A CONTAR | A TU FAMILIA |
EL DÍA DEL ATAQUE | SU AVIÓN FALLÓ | SUS COMPAÑEROS | DESPEGARON SIN ÉL | LES REGALÓ AZALEAS | Y UNO LE DIJO | ME ADELANTO |
QUERÍA IR CONTIGO | LE TOCÓ | SALIR A ÉL | PERO EL MOTOR | VOLVIÓ A FALLAR | ATERRIZÓ | DE EMERGENCIA | EN UNA ISLA | VOLVIÓ VIVO |
Y SUS JEFES | LE PEGARON | CON UNA ESPADA | DE BAMBÚ | PARA ELLOS | ERA UNA VERGÜENZA | PARA LOS MUERTOS | SÍ LE TENÍAN |
MIEDO A LA MUERTE | PERO LE TENÍAN | MÁS MIEDO | A VOLVER VIVOS"""
grupos, _j = [], 0
for g in [g.split() for g in GRUPOS.replace("\n", " ").split("|") if g.strip()]:
    idx = list(range(_j, _j + len(g)))
    assert [TOK[j][0] for j in idx] == g, (g, [TOK[j][0] for j in idx])
    grupos.append(idx); _j += len(g)
assert _j == len(TOK), (_j, len(TOK))
V.TOK, V.grupos, V.words = TOK, grupos, words
V.CLAVE.update({w: (240, 80, 64) for w in ("VIVO", "VIVOS", "MIEDO", "COBARDE", "VERGÜENZA", "CASTIGARON", "PEGARON")})


def sacudida(t):
    dx = dy = 0.0
    for g in SACUDIDAS:
        e = t - g
        if 0 <= e < 0.28:
            amp = 16 * (1 - e / 0.28)
            dx += amp * math.sin(e * 90); dy += amp * math.cos(e * 77)
    return int(dx), int(dy)


def cuadro(f):
    t = (f - 1) / FPS
    loop0 = DUR - 0.3
    k = plano_de(t) if t < loop0 else 1
    tt = t if t < loop0 else T[1][0] + (t - loop0)
    a, b = T[k]
    im = FUN[k](tt, a, b)
    dx, dy = sacudida(tt)
    if dx or dy:
        base = Image.new("RGB", (W, H), (20, 18, 18))
        base.paste(im.resize((W + 40, H + 70)), (dx - 20, dy - 35))
        im = base
    if not V._GRANO:
        V._GRANO["g"] = Image.effect_noise((W, H), 18).convert("RGB")
    im = Image.blend(im, Image.composite(im, V._GRANO["g"], Image.new("L", (W, H), 236)), 0.25)
    V.subtitulos(im, t)
    return im


if __name__ == "__main__":
    dst = sys.argv[1]
    os.makedirs(dst, exist_ok=True)
    a = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    b = int(sys.argv[3]) if len(sys.argv) > 3 else FIN
    for f in range(a, b + 1):
        cuadro(f).save(os.path.join(dst, f"{f:05d}.png"), compress_level=1)
    print("ok", a, b)
