"""Ep. 10c — "La mente de un kamikaze" (2D plano, 7-nov-2026). Voz de 57,5 s (out/tts/ep10c-kamikaze-mente.mp3).
Reutiliza el kit 2D (studio/plantilla/kit2d.py) y las escenas del Ep. 10 en 2D (ep10-kamikazes/escena2d/video2d.py).
Uso: python3 video.py <salida> [desde hasta]
"""
import json, math, os, random, sys
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
EPI = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, os.path.abspath(os.path.join(AQUI, "../../ep10-kamikazes/escena2d")))
sys.argv = sys.argv[:1] + sys.argv[1:]
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


CORTES = [0.0, tw("Mañana") - 0.1, tw("su", 4.0) - 0.25, tw("Cómo") - 0.15, tw("En", 8.5) - 0.15, tw("honor") - 0.35,
          tw("Y", 14.9) - 0.15, tw("Entonces") - 0.15, tw("estrellar") - 0.15, tw("Les", 25.5) - 0.15, tw("pero", 26.6) - 0.15,
          tw("Antes", 29.5) - 0.15, tw("pintar", 30) - 0.2, tw("Él", 35.0) - 0.15, tw("Años", 38.5) - 0.15, tw("Solo", 44.3) - 0.15, tw("Pero", 48) - 0.15,
          tw("Uno", 50) - 0.15, DUR]
T = {i + 1: (CORTES[i], CORTES[i + 1]) for i in range(len(CORTES) - 1)}


def plano_de(t):
    for k, (a, b) in T.items():
        if a <= t < b:
            return k
    return max(T)


# ------------------------------------------------------------------ personajes nuevos
def mujer(L, x, y, alto=700, embarazada=True, mira=-1, t=0.0, inclina=0.0):
    """Mujer japonesa de los años 40 (monpe y blusa), plana. inclina > 0 = se inclina (reverencia)."""
    k = alto / 700
    hom = y - 560 * k
    cad = y - 300 * k
    tela, tela2 = (122, 104, 132), (92, 80, 104)
    # piernas (monpe: pantalón ancho de trabajo) y zapatos
    K.poligono(L, [(x - 70 * k, cad), (x + 70 * k, cad), (x + 60 * k, y - 10 * k), (x + 10 * k, y - 10 * k), (x, cad + 60 * k),
                   (x - 10 * k, y - 10 * k), (x - 60 * k, y - 10 * k)], tela2, P["tinta"], 5)
    for s in (-1, 1):
        K.caja_red(L, x + s * 35 * k - 30 * k, y - 22 * k, x + s * 35 * k + 30 * k, y + 2 * k, 8 * k, (60, 50, 44), P["tinta"], 4)
    # torso (blusa) con la guata
    K.caja_red(L, x - 78 * k, hom, x + 78 * k, cad + 20 * k, 40 * k, tela, P["tinta"], 5)
    if embarazada:
        K.elipse(L, x - mira * 60 * k, cad - 60 * k, 70 * k, 92 * k, tela, P["tinta"], 5)
    # brazos sobre la guata
    for s in (-1, 1):
        K.miembro(L, [(x + s * 70 * k, hom + 30 * k), (x + s * 84 * k, cad - 80 * k), (x - mira * 40 * k, cad - 60 * k + s * 20 * k)], tela, 30 * k)
    # cabeza con moño
    cy = hom - 76 * k
    K.caja_red(L, x - 18 * k, cy + 40 * k, x + 18 * k, hom + 6 * k, 6 * k, P["piel2"], P["tinta"], 4)
    K.circulo(L, x, cy, 62 * k, P["piel"], P["tinta"], 5)
    L.d.chord((L.S(x - 66 * k), L.S(cy - 70 * k), L.S(x + 66 * k), L.S(cy + 40 * k)), 180, 360, fill=(36, 30, 30), outline=P["tinta"], width=int(L.S(5)))
    K.circulo(L, x + mira * 52 * k, cy - 48 * k, 26 * k, (36, 30, 30), P["tinta"], 4)
    for s in (-1, 1):
        K.circulo(L, x + s * 20 * k + mira * 10 * k, cy + 6 * k, 6 * k, P["tinta"])
    L.d.line([L.pt(x - 10 * k + mira * 10 * k, cy + 30 * k), L.pt(x + 10 * k + mira * 10 * k, cy + 30 * k)], fill=P["tinta"], width=int(L.S(4)))


def samurai(L, x, y, alto=1000, t=0.0):
    """Silueta de samurái con armadura y katana, de frente, sobre un sol rojo."""
    k = alto / 1000
    osc = (40, 34, 34)
    K.poligono(L, [(x - 210 * k, y - 560 * k), (x + 210 * k, y - 560 * k), (x + 250 * k, y - 250 * k), (x - 250 * k, y - 250 * k)], (120, 40, 36), P["tinta"], 6)
    for i in range(4):     # placas de la armadura
        yy = y - 520 * k + i * 70 * k
        L.d.line([L.pt(x - 220 * k, yy), L.pt(x + 220 * k, yy)], fill=P["tinta"], width=int(L.S(5)))
    K.poligono(L, [(x - 250 * k, y - 250 * k), (x + 250 * k, y - 250 * k), (x + 200 * k, y), (x - 200 * k, y)], osc, P["tinta"], 6)
    for s in (-1, 1):      # hombreras
        K.poligono(L, [(x + s * 200 * k, y - 600 * k), (x + s * 330 * k, y - 560 * k), (x + s * 320 * k, y - 400 * k), (x + s * 210 * k, y - 430 * k)], (120, 40, 36), P["tinta"], 6)
    cy = y - 700 * k
    K.circulo(L, x, cy, 110 * k, osc, P["tinta"], 6)
    L.d.chord((L.S(x - 170 * k), L.S(cy - 150 * k), L.S(x + 170 * k), L.S(cy + 60 * k)), 180, 360, fill=osc, outline=P["tinta"], width=int(L.S(6)))
    K.poligono(L, [(x - 150 * k, cy - 120 * k), (x - 230 * k, cy - 300 * k), (x - 120 * k, cy - 140 * k)], P["ocre"], P["tinta"], 5)
    K.poligono(L, [(x + 150 * k, cy - 120 * k), (x + 230 * k, cy - 300 * k), (x + 120 * k, cy - 140 * k)], P["ocre"], P["tinta"], 5)
    K.caja_red(L, x - 60 * k, cy - 10 * k, x + 60 * k, cy + 70 * k, 14 * k, (150, 50, 44), P["tinta"], 5)     # máscara
    K.linea(L, [(x + 260 * k, y - 120 * k), (x - 160 * k, y - 980 * k)], P["tinta"], 26 * k)                 # katana
    K.linea(L, [(x + 260 * k, y - 120 * k), (x - 160 * k, y - 980 * k)], (210, 214, 220), 14 * k)
    K.linea(L, [(x + 300 * k, y - 40 * k), (x + 250 * k, y - 140 * k)], (60, 40, 30), 30 * k)


# ------------------------------------------------------------------ escenas
dibujo = V.dibujo


def escena_pista(L, t, zoom=1.0, esposa=0.0, bomba=True, piloto_x=420, alto=880):
    V.cielo_amanecer(L, t=0.2)
    V.lomas(L, 1110, 220, (150, 128, 124), 0.3)
    V.lomas(L, 1160, 120, (118, 108, 92), 2.1)
    V.pista_suelo(L)
    V.barraca(L, 760, 1180, 240, 100)
    K.avion_lateral(L, 640, 1240, largo=640, mira=-1, helice_t=0)
    if bomba:
        K.caja_red(L, 560, 1272, 720, 1306, 16, (58, 58, 54), P["tinta"], 4)
    K.persona(L, piloto_x, 1760, alto=alto, ropa={"hachimaki": True}, mira=1, t=t)
    if esposa > 0:
        mujer(L, 860 + 300 * (1 - sale(esposa)), 1760, alto=720, mira=-1, t=t)


@dibujo
def p1(L, t, a, b):
    escena_pista(L, t)
    K.pildora(L, "TENIENTE HARUO ARAKI · 21 AÑOS", 540, 330, 46, escala=pop(t - a - 0.2))
    K.pildora(L, "RECREACIÓN", 900, 230, 30, fondo=(30, 32, 36), tinta=P["blanco"])


@dibujo
def p2(L, t, a, b):
    escena_pista(L, t)
    K.pildora(L, "MAYO DE 1945", 540, 330, 50, escala=pop(t - a - 0.1))
    K.pildora(L, "RECREACIÓN", 900, 230, 30, fondo=(30, 32, 36), tinta=P["blanco"])


@dibujo
def p3(L, t, a, b):
    escena_pista(L, t, esposa=(t - a) / 0.7, piloto_x=360)
    K.pildora(L, "SU ESPOSA, SHIGEKO", 760, 600, 44, escala=pop(t - tw("esposa")))
    K.pildora(L, "RECREACIÓN", 900, 230, 30, fondo=(30, 32, 36), tinta=P["blanco"])


@dibujo
def p4(L, t, a, b):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=P["papel"])
    K.texto(L, "?", 760, 560 + 10 * math.sin(t * 4), 380, P["rojo"], borde=10)
    K.viejo(L, 480, 1850, alto=900, boca=V.boca(t), t=t, gesto="tazon", mira=1)


@dibujo
def p5(L, t, a, b):
    u = suave((t - a) / (b - a))
    f = V.mapa_japon(L, (136, 35.5, 540, 760), 2600 + 300 * u, colores={"JPN": P["rojo"]})
    K.pildora(L, "JAPÓN, AÑOS 40", 540, 330, 50, escala=pop(t - a - 0.1))
    if t > tw("pecado") - 0.1:
        K.pildora(L, "MORIR POR EL PAÍS ≠ PECADO", 540, 470, 46, fondo=P["blanco"], escala=pop(t - tw("pecado") + 0.1))


@dibujo
def p6(L, t, a, b):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=(232, 214, 186))
    K.circulo(L, 540, 760, 420, P["rojo"])
    samurai(L, 540, 1560, alto=1000, t=t)
    K.pildora(L, "HONOR · BUSHIDŌ", 540, 330, 52, fondo=P["blanco"], escala=pop(t - a - 0.1))


@dibujo
def p7(L, t, a, b):
    u = suave((t - a) / (b - a))
    V.mapa_pacifico(L, t, (138 - 2 * u, 12 + 6 * u, 540, 960), 1650 + 450 * u, perdidas_u=(t - a) / 1.6, flechas_u=(t - a - 0.3) / 1.2)
    K.pildora(L, "1944", 540, 330, 64, escala=pop(t - a))


@dibujo
def p8(L, t, a, b):
    u = (t - a) / (b - a)
    escena_pista(L, t, piloto_x=300, alto=760)
    K.pildora(L, "LO MÁXIMO", 540, 330, 56, fondo=P["rojo"], tinta=P["blanco"], escala=pop(t - tw("máximo") + 0.1))


@dibujo
def p9(L, t, a, b):
    u = clamp((t - a) / (b - a + 0.1))
    V.cielo_mar(L)
    V.flak(L, t, a + 0.2, n=8, semilla=5, zona=(60, 100, 1020, 900))
    V.mar(L, 1500, t=t)
    V.portaaviones(L, 540, 1520 + 200 * u ** 2, 700 + 700 * u ** 2)
    esc = 0.2 + 2.0 * u ** 1.8
    x = 640 - 100 * u; y = 260 + 600 * u
    V.humo_estela(L, [(x + (i + 1) * 30 * esc, y - (i + 1) * 60 * esc) for i in range(10)], 10 * esc, 40 * esc)
    V.avion_frente(L, x, y, escala=esc, inclina=0.1 * math.sin(t * 3))
    K.caja_red(L, x - 40 * esc, y + 60 * esc, x + 40 * esc, y + 100 * esc, 14 * esc, (58, 58, 54), P["tinta"], 4)


def p10(t, a, b):
    im, ven, _ = V.foto_plano("foto_201.jpg", t, a, b, 1.55, 1.7, (0.35, 0.45), (0.62, 0.45), rot=1.2)
    V.etiqueta_real(im, t, a + 0.1)
    V.pildora_t(im, "«VOLUNTARIOS»", 540, 880, tw("voluntarios") - 0.05, t, tam=60, fondo=P["ocre"])
    return im


def p11(t, a, b):
    im, ven, _ = V.foto_plano("foto_choshi.jpg", t, a, b, 1.4, 1.75, (0.42, 0.45), (0.56, 0.42), rot=-1.0)
    V.etiqueta_real(im, t, a + 0.1)
    V.pildora_t(im, "ESCUADRONES ENTEROS", 540, 880, tw("escuadrones") - 0.05, t, tam=56, fondo=P["rojo"], tinta=P["blanco"])
    return im


def p12(t, a, b):
    im, ven, _ = V.foto_plano("foto_alumna.jpg", t, a, b, 1.45, 1.7, (0.45, 0.45), (0.55, 0.42), rot=1.0)
    V.etiqueta_real(im, t, a + 0.1)
    return im


@dibujo
def p13(L, t, a, b):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=(200, 186, 160))
    K.poligono(L, [(-40, 640), (1120, 600), (1120, 1000), (-40, 1040)], P["blanco"], P["tinta"], 6)
    u = clamp((t - a - 0.2) / (b - a - 0.4))
    K.circulo(L, 540, 820, 160, (236, 226, 214), (180, 150, 140), 3)
    K.circulo(L, 540, 820, 160 * math.sqrt(u), (176, 28, 28))
    random.seed(13)
    for i in range(10):     # gotas que caen
        v = (t * 1.6 + i * 0.13) % 1.0
        if u < 1:
            K.circulo(L, 470 + random.uniform(0, 140), 380 + 420 * v, 12, (176, 28, 28))
    K.pildora(L, "CON SU SANGRE", 540, 330, 56, fondo=P["blanco"], escala=pop(t - tw("sangre") + 0.1))


def p14(t, a, b):
    im, ven, _ = V.foto_plano("carta.jpg", t, a, b, 2.2, 2.0, (0.6, 0.5), (0.6, 0.5), rot=-2.0)
    V.pildora_t(im, "PERDÓN", 540, 560, tw("perdón") - 0.05, t, tam=72, fondo=P["ocre"])
    V.pildora_t(im, "RECREACIÓN", 880, 300, a, t, tam=34, fondo=(30, 32, 36), tinta=(255, 255, 255))
    return im


@dibujo
def p15(L, t, a, b):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=(62, 56, 60))
    K.circulo(L, 540, 720, 300, (92, 82, 86))
    mujer(L, 540, 1640, alto=1050, embarazada=False, mira=-1, t=t)
    K.pildora(L, "SHIGEKO, AÑOS DESPUÉS", 540, 330, 48, escala=pop(t - a - 0.1))
    if t > tw("vergüenza") - 0.05:
        K.pildora(L, "«UNA VERGÜENZA»", 540, 470, 56, fondo=P["rojo"], tinta=P["blanco"], escala=pop(t - tw("vergüenza") + 0.05))


@dibujo
def p16(L, t, a, b):
    u = suave((t - a) / (b - a))
    f = V.mapa_japon(L, (128.3, 25.6, 540, 820), 4600 + 500 * u)
    xo, yo = f(127.85, 26.45)
    K.circulo(L, xo, yo, 60 * (0.6 + 0.4 * abs(math.sin((t - a) * 3))), (196, 64, 52, 150))
    K.texto(L, "OKINAWA", xo + 40, yo - 40, 44, P["blanco"], ancla="lm", borde=6)
    t0 = tw("dos") - 0.1
    if t > t0:
        n = int(round(2000 * sale((t - t0) / 0.9) / 10)) * 10
        K.pildora(L, f"+{n:,}".replace(",", ".") + " KAMIKAZES", 540, 330, 64, fondo=P["ocre"], escala=pop(t - t0))


@dibujo
def p17(L, t, a, b):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=P["papel"])
    for i in range(5):
        x = 140 + i * 200
        distinto = i == 3
        ropa = {"hachimaki": True}
        if distinto:
            ropa["torso"] = (170, 150, 110)
        mira = -1 if (distinto and t > a + 0.5) else 1
        K.persona(L, x, 1400, alto=520, ropa=ropa, mira=mira, t=t + i)
    if t > a + 0.5:
        K.flecha(L, 740, 520, 740, 680, P["rojo"], 14, u=sale((t - a - 0.5) / 0.3))


def p18(t, a, b):
    im, ven, _ = V.foto_plano("foto_uehara.jpg", t, a, b, 1.35, 1.75, (0.5, 0.45), (0.45, 0.4), rot=-1.0)
    V.etiqueta_real(im, t, a + 0.1)
    V.pildora_t(im, "RYŌJI UEHARA · ESTUDIANTE", 540, 430, a + 0.15, t, tam=46)
    V.pildora_t(im, "«UN LIBERAL»", 540, 880, tw("liberal") - 0.05, t, tam=60, fondo=P["azul"], tinta=P["blanco"])
    return im


FUN = {1: p1, 2: p2, 3: p3, 4: p4, 5: p5, 6: p6, 7: p7, 8: p8, 9: p9, 10: p10, 11: p11, 12: p12, 13: p13, 14: p14, 15: p15,
       16: p16, 17: p17, 18: p18}
assert len(FUN) == len(T), (len(FUN), len(T))


# ------------------------------------------------------------------ subtítulos (grupos automáticos)
def limpiar(w):
    for ch in ",.:;!¡?¿\"…":
        w = w.replace(ch, "")
    return w.replace("...", "").upper()


NUM = {("MIL", "NOVECIENTOS", "CUARENTA", "Y", "CUATRO"): "1944", ("VEINTIÚN",): "21", ("DOS", "MIL"): "2.000"}
TOK = []
i = 0
while i < len(words):
    hecho = False
    for seq, cifra in NUM.items():
        if tuple(limpiar(x["w"]) for x in words[i:i + len(seq)]) == seq:
            TOK.append((cifra, list(range(i, i + len(seq))), words[i + len(seq) - 1]["w"][-1] in ".,:;?…"))
            i += len(seq); hecho = True
            break
    if not hecho:
        TOK.append((limpiar(words[i]["w"]), [i], words[i]["w"][-1] in ".,:;?…"))
        i += 1
GRUPOS = """ESTE PILOTO | TIENE 21 AÑOS | MAÑANA SALE | EN UNA MISIÓN KAMIKAZE | Y SU ESPOSA | EMBARAZADA | ESTÁ ORGULLOSA DE ÉL |
CÓMO SE LLEGA | A PENSAR ASÍ | EN EL JAPÓN | DE ESA ÉPOCA | DAR LA VIDA | POR EL PAÍS | NO ERA UN PECADO | ERA UN HONOR |
EL DE LOS SAMURÁIS | Y EN 1944 | JAPÓN ESTÁ PERDIENDO | LA GUERRA | ENTONCES LES PIDE | A SUS PILOTOS | LO MÁXIMO |
ESTRELLAR SU AVIÓN | CON UNA BOMBA | CONTRA LOS BARCOS | DE ESTADOS UNIDOS | LES DICEN VOLUNTARIOS | PERO HAY JEFES | QUE OFRECEN |
ESCUADRONES ENTEROS | ANTES DE DESPEGAR | UNAS ALUMNAS | SE CORTAN LOS DEDOS | PARA PINTAR | CON SU SANGRE | EL SOL DE SU CINTA |
ÉL ESCRIBE | SU ÚLTIMA CARTA | Y LE PIDE PERDÓN | A SU ESPOSA | AÑOS DESPUÉS | ELLA LO EXPLICÓ ASÍ | HABRÍA SIDO | UNA VERGÜENZA |
QUE SIGUIERA VIVO | SOLO EN OKINAWA | MURIERON | MÁS DE 2.000 ASÍ | PERO NO TODOS | PENSABAN IGUAL | UNO DE ELLOS | ESTUDIANTE |
ESCRIBIÓ LA NOCHE ANTES | MAÑANA | UN LIBERAL | SE VA DE ESTE MUNDO"""
grupos, _j = [], 0
for g in [g.split() for g in GRUPOS.replace("\n", " ").split("|") if g.strip()]:
    idx = list(range(_j, _j + len(g)))
    assert [TOK[j][0] for j in idx] == g, (g, [TOK[j][0] for j in idx])
    grupos.append(idx); _j += len(g)
assert _j == len(TOK), (_j, len(TOK))
V.TOK, V.grupos, V.words = TOK, grupos, words


def cuadro(f):
    t = (f - 1) / FPS
    loop0 = DUR - 0.3
    k = plano_de(t) if t < loop0 else 1
    tt = t if t < loop0 else T[1][0] + (t - loop0)
    a, b = T[k]
    im = FUN[k](tt, a, b)
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
