# -*- coding: utf-8 -*-
"""Beat del clavo, v3 (23-nov-2026, ronda contra virales), con kit_explica (laboratorio nocturno).

Planos (storyboard_v2.json): cada 0,7–1,6 s una composición nueva, cortes en la palabra.
  0     GANCHO  = el último cuadro (clavo gigante + martillo gigante): el loop empalma perfecto
  0,18  A  "Esto es un clavo"      clavo chico de héroe sobre tablón en testa, martillo listo, cinta métrica 8 cm
  1,28  B  "Un martillazo"         macro: la cara del martillo contra la cabeza (anticipación, estela, flash,
                                    ondas, chispas, temblor)
  1,97  C  "y entra"               tablón en corte: la madera sube y se traga el clavo, fibras que se doblan, 8 CM → 0
  2,75  D  "Pero este clavo mide"  corte por coincidencia (la cabeza en el mismo lugar) al clavo de 20 m;
                                    'dolly zoom' hasta ras de suelo; tarjeta ×250 con el clavo real en la mano
  3,69  E  "veinte metros"         alzado lateral: cinta que crece hasta 20 M, número héroe, bus y edificio
  4,59  F  "y pesa 50 toneladas"   a ras de suelo con el suelo en corte: grietas, polvo, 50 T héroe, 10 elefantes
  6,21  G  "¿Con qué le pegas?"    vuelve el plano ancho: martillo normal ✗, llega el martillo gigante

Uso:  .venv/bin/python studio/duelo-visual/python/render.py [salida.mp4]
      .venv/bin/python studio/duelo-visual/python/render.py --cuadros 0,1.5,3 carpeta/
"""
import json
import math
import os
import subprocess
import sys
import time
import wave
from multiprocessing import Pool

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(RAIZ, "studio", "plantilla"))
import kit_explica as K  # noqa: E402

SB = json.load(open(os.path.join(RAIZ, "studio/duelo-visual/storyboard.json")))
VOZ = os.path.join(RAIZ, SB["voz"])
WORDS = json.load(open(os.path.join(RAIZ, SB["words"])))
with wave.open(VOZ) as w_:
    DUR_VOZ = w_.getnframes() / w_.getframerate()
FPS = SB["formato"]["fps"]
DUR = DUR_VOZ + 0.5
NF = int(round(DUR * FPS))
EST = K.ESTILOS["laboratorio_nocturno"]
CLAVES = SB["palabras_clave_con_recuadro"]
TINTA, GRIS = K.rgb(EST["tinta"]), K.rgb(EST["gris"])
SALIDA = "/private/tmp/claude-501/-Users-tomas-Desktop-Proyecto/d4cb7467-771f-4533-993e-f4f18f1ccbe0/scratchpad/duelo/python-v3.mp4"


def t_palabra(txt, vez=1):
    k = 0
    for w in WORDS:
        if K._norm(w["w"]) == K._norm(txt):
            k += 1
            if k == vez:
                return w["s"]
    raise KeyError(txt)


T = dict(esto=t_palabra("esto"), clavo=t_palabra("clavo"), un=t_palabra("un", 2), martillazo=t_palabra("martillazo"),
         y=t_palabra("y"), entra=t_palabra("entra"), pero=t_palabra("pero"), este=t_palabra("este"),
         clavo2=t_palabra("clavo", 2), mide=t_palabra("mide"), veinte=t_palabra("veinte"), pesa=t_palabra("pesa"),
         cincuenta=t_palabra("cincuenta"), con=t_palabra("con"), que=t_palabra("qué"), pegas=t_palabra("pegas"))
T_GOLPE = round(T["martillazo"] * FPS) / FPS          # el cuadro del contacto

# ------------------------------------------------------------------ composición común (el loop y los cortes por
# coincidencia dependen de que la cabeza del clavo y el martillo caigan SIEMPRE en el mismo lugar de la pantalla)
CX = 500
Y_SUP = 1305                 # superficie (tablón / suelo) en la pantalla
N1 = 780                     # clavo chico: 41 % del alto
Y_TAPA = Y_SUP - N1          # 525: tapa de la cabeza
PR_A = K.proyector_oblicuo(CX, Y_SUP, 1.0, 0.30)
MART_POS, MART_ANG, H1 = (742, 640), 75.0, 440

# clavo gigante: 22,5 m en total, 2,5 m enterrados → la tapa a 20 m
LG, Z0G = 22.5, -2.5
S1 = K.Cam3D(Y=-60, Z=4, pitch=0, F=2340, cx=CX, cy=1149)       # plano ancho: tapa en y=525, suelo en y=1305
S2 = K.Cam3D(Y=-9.5, Z=0.7, pitch=23, F=980, cx=CX, cy=900)    # a ras de suelo, mirando hacia arriba
S3 = K.Cam3D(Y=-60, Z=4, pitch=0, F=2340, cx=780, cy=1149)      # alzado con el clavo a la derecha
S4 = K.Cam3D(Y=-14, Z=1.2, pitch=-8, F=1500, cx=852, cy=1171)   # a ras de suelo, el suelo en corte
PERSONA = (-0.9, -6.5)
BUS = (-12.4, 1.5)


def sub(L, t):
    K.subtitulos(L, WORDS, t, CLAVES)


# ------------------------------------------------------------------ piezas del mundo gigante
def mundo_gigante(L, cam3, t, recorte_suelo=True, desenfoque=True):
    K.edificios3d(L, cam3)
    K.suelo3d(L, cam3)
    base = cam3.pr(0, 0, 0)
    esc = cam3.escala(0, 0, 0)
    R = 0.0275 * LG
    ry = abs(cam3.pr(0, -R * 3, 0)[1] - cam3.pr(0, R * 3, 0)[1]) / 2 + 2
    K.sombra_contacto(L, base[0] + esc * 0.6, base[1], esc * R * 4.2, max(4, ry * 1.2), 0.8)
    K.bus3d(L, cam3.pr, BUS[0], BUS[1])
    K.clavo3d(L, cam3.pr, 0, 0, LG, z0=Z0G, recorte=0.0 if recorte_suelo else None)
    # tierra levantada alrededor de la base
    for s in (-1, 1):
        xb = base[0] + s * esc * R
        h = esc * 0.35
        pts = [(xb - s * 3, base[1] + 3), (xb + s * esc * 0.15, base[1] - h), (xb + s * esc * 0.6, base[1] - h * 1.2),
               (xb + s * esc * 1.3, base[1] - h * 0.5), (xb + s * esc * 1.9, base[1] + 3)]
        K.poligono(L, pts, (84, 62, 48))
        K.linea(L, pts[1:4], (190, 140, 96), max(1.0, esc * 0.05), alpha=0.8)
    K.persona_espalda(L, cam3.pr, PERSONA[0], PERSONA[1])
    if desenfoque:                                  # primer plano: piedras fuera de foco
        with K.desenfoque(L, 4) as d:
            import numpy as np
            rng = np.random.default_rng(21)
            for _ in range(26):
                X, Y = rng.uniform(-18, 18), cam3.Y + rng.uniform(22, 34)
                p, s = cam3.pr(X, Y, 0), cam3.escala(X, Y, 0)
                r = rng.uniform(0.12, 0.35) * s
                if not (-40 < p[0] < 1120 and p[1] < 2000):
                    continue
                K.poligono(L, K.elipse_pts(p[0], p[1], r * 1.3, r * 0.55, n=14), (62, 48, 40), capa=d)
                K.poligono(L, K.elipse_pts(p[0] - r * 0.3, p[1] - r * 0.25, r * 0.6, r * 0.18, n=10), (170, 128, 92), capa=d, alpha=0.6)


def lienzo_cielo(cam3, semilla):
    return K.Lienzo(EST, semilla=semilla, fondo_img=K.fondo_capas(EST, cam3.horizonte()))


# ------------------------------------------------------------------ A: el clavo chico
def plano_a(t, sem):
    L = K.Lienzo(EST, semilla=sem, fondo_img=K.fondo_estudio(EST))
    p_cam = K.anim(t, T["esto"], 1.1, K.ease_estado)
    L.camara(s=1.0 + 0.035 * p_cam, ancla=(CX, 900))
    K.tabla_testa(L, 110, 890, Y_SUP + 23, 460, prof=46)
    K.sombra_contacto(L, CX + 10, Y_SUP + 2, 40, 7, 0.7)
    K.ao(L, CX - 30, CX + 40, Y_SUP + 3, 8, 0.4)
    K.clavo3d(L, PR_A, 0, 0, N1)
    # el martillo respira y, en "Un", se echa atrás (anticipación)
    ant = K.anim(t, T["un"] - 0.16, 0.16, K.ease_estado)
    ang = MART_ANG + 1.2 * math.sin(t * 3.4) + 9 * ant
    K.martillo(L, MART_POS[0] + 18 * ant, MART_POS[1] - 26 * ant, H1, ang)
    L.camara()
    # cinta métrica 0–8 cm y etiqueta en "clavo"
    marcas = [(i / 80, 15 if i % 10 == 0 else (10 if i % 5 == 0 else 6), (str(i // 10) if i % 10 == 0 and i else None))
              for i in range(81)]
    K.regla(L, 330, Y_SUP, Y_TAPA, K.anim(t, T["clavo"], 0.6, K.ease_entrada), marcas, ancho=34)
    K.etiqueta(L, "CLAVO · 8 CM", (CX - 52, Y_TAPA + 18), (66, 452), t, T["clavo"], tam=46, dur=0.6, texto_desde=0.3)
    L.fundido_abajo(1560, 1720)
    sub(L, t)
    return L


# ------------------------------------------------------------------ B: macro del golpe
NB, HB = 1600, 1650
Y_TAPA_B = 1080
PR_B = K.proyector_oblicuo(480, Y_TAPA_B + NB, 1.0, 0.30)
P_TOQUE = next(i / 2000 for i in range(2001) if K.ease_aterriza(i / 2000) >= 1.0)
P_PICO, Y_PICO = K.pico_aterriza()
D_SWING = (T_GOLPE - T["un"]) / P_TOQUE


def y_martillo_b(t):
    """Desplazamiento vertical de la cabeza del martillo (0 = cara sobre la tapa)."""
    p = K.tramo(t, T["un"], D_SWING)
    y = K.ease_aterriza(p)
    if p < P_TOQUE:
        return -330 * (1 - y)
    return -22 * (y - 1) / (Y_PICO - 1)          # rebote: lo que la curva pasa de 1


def plano_b(t, sem):
    L = K.Lienzo(EST, semilla=sem, fondo_img=K.fondo_estudio(EST, luz=(0.3, 0.32)))
    e = t - T_GOLPE
    tx, ty = K.temblor(e, 16, 8)
    zoom = 1.0 + 0.05 * (1 - K.anim(t, T_GOLPE, 0.5, K.ease_entrada)) if e >= 0 else 1.05
    L.camara(s=zoom, ancla=(480, Y_TAPA_B), temblor=(tx, ty))
    K.clavo3d(L, PR_B, 0, 0, NB)
    cy0 = Y_TAPA_B - 0.287 * HB
    if -2.5 / FPS < e < 0:                           # estela (2 cuadros): copias entre el cuadro anterior y este
        y_ant = y_martillo_b(t - 1 / FPS)
        y_act = y_martillo_b(t)
        # estela: la cara "barrida" entre el cuadro anterior y este (se desvanece hacia arriba) + líneas de velocidad
        ya, yb = cy0 + y_ant + 0.2 * HB, cy0 + y_act + 0.287 * HB
        K.relleno_gradiente(L, [(480 - 0.055 * HB, ya), (480 + 0.055 * HB, ya), (480 + 0.055 * HB, yb), (480 - 0.055 * HB, yb)],
                            [(0, (200, 206, 216, 0)), (1, (200, 206, 216, 150))], (0, ya), (0, yb))
        for dx in (-0.075, -0.068, 0.068, 0.075):
            K.linea(L, [(480 + dx * HB, ya + 40), (480 + dx * HB, yb - 30)], (230, 234, 240), 2.5, alpha=0.5)
    K.martillo(L, 480, cy0 + y_martillo_b(t), HB, 0, sombra=False)
    K.impacto(L, 480, Y_TAPA_B, e, escala=1.0, ry=0.3, chispas=12)
    K.nube_polvo(L, 480, Y_TAPA_B + 10, e, ancho=150, n=10, semilla=12, color=(150, 140, 130), dur=0.6, alpha=0.5)
    if 0 <= e < 0.25:
        L.brillo = 1 + 1.6 * math.exp(-e * 12)
    L.camara()
    if 0 <= e < 1 / FPS:
        K.flash_blanco(L, 0.78)
    L.fundido_abajo(1560, 1720)
    sub(L, t)
    return L


# ------------------------------------------------------------------ C: el corte de la madera
def plano_c(t, sem):
    L = K.Lienzo(EST, semilla=sem, fondo_img=K.fondo_estudio(EST))
    p = K.anim(t, T["entra"], 0.42, K.ease_estado)
    hr = 0.03 * N1
    ys = Y_SUP - (N1 - hr) * p
    tx, ty = K.temblor(t - T["entra"] - 0.05, 5, 10)
    L.camara(temblor=(tx, ty))
    K.madera_corte(L, -30, 1110, ys, 1760, CX, Y_SUP - ys, 0.0275 * N1)
    K.clavo3d(L, PR_A, 0, 0, N1)
    K.polvo(L, CX, ys, t - T["entra"] - 0.04, n=12)
    L.camara()
    # placa con el número vivo: 8 CM → 0
    if t >= T["entra"]:
        a = K.anim(t, T["entra"], 0.25)
        b = (60, 660, 420, 870)
        L.d.rounded_rectangle([L.P(b[0], b[1], False), L.P(b[2], b[3], False)], radius=L.S(26, False),
                              fill=(14, 16, 22, int(225 * a)))
        K.texto(L, 92, 720, "8 CM → 0", 40, GRIS, "xbold", alpha=a)
        K.contador(L, 8 * (1 - p), 88, 836, 120, digitos=1, unidad=" CM", alpha=a)
    L.fundido_abajo(1560, 1720)
    sub(L, t)
    return L


# ------------------------------------------------------------------ D: corte al gigante + dolly zoom
def inset_clavo_real(L, b, a):
    x0, y0, x1, y1 = b
    cx = x0 + (x1 - x0) * 0.34
    yb = y1 - 76
    largo = (y1 - y0) - 160
    pr = K.proyector_oblicuo(cx, yb, 1.0, 0.3)
    K.mano_pinza(L, cx - 9, yb - largo * 0.6, 0.82, alpha=a, nail=lambda: K.clavo3d(L, pr, 0, 0, largo, cam=False, ns=40))
    K.texto(L, x0 + 26, y1 - 26, "8 CM", 34, TINTA, "black", alpha=a)


def plano_d(t, sem):
    k = K.anim(t, T["pero"] + 0.16, 0.62, K.ease_estado)
    cam3 = K.Cam3D.mezcla(S1, S2, k)
    L = lienzo_cielo(cam3, sem)
    mundo_gigante(L, cam3, t)
    K.inset(L, (600, 590, 926, 1010), t, T["este"], contenido=inset_clavo_real, insignia="×250", titulo="EL REAL")
    L.fundido_abajo(1560, 1720)
    sub(L, t)
    return L


# ------------------------------------------------------------------ E: alzado con la cinta de 20 m
def plano_e(t, sem):
    L = lienzo_cielo(S3, sem)
    L.camara(s=1.0 + 0.025 * K.anim(t, T["veinte"], 0.9, K.ease_estado), ancla=(600, 1305))
    mundo_gigante(L, S3, t)
    L.camara()
    y_suelo, y_tapa = S3.pr(0, 0, 0)[1], S3.pr(0, 0, 20)[1]
    marcas = [(i / 20, 18 if i % 5 == 0 else 9, (str(i) if i % 5 == 0 and i else None)) for i in range(21)]
    K.regla(L, 888, y_suelo, y_tapa, K.anim(t, T["veinte"], 0.5, K.ease_entrada), marcas, ancho=36, tam_txt=20)
    K.numero_heroe(L, "20", "M", 60, 880, 350, t, T["veinte"])
    K.texto(L, 68, 946, "DE ALTO · 250 VECES EL REAL", 34, TINTA, "xbold", alpha=K.anim(t, T["veinte"] + 0.1, 0.3))
    L.fundido_abajo(1560, 1720)
    sub(L, t)
    return L


# ------------------------------------------------------------------ F: el peso, a ras de suelo
def suelo_en_corte(L, cam3, t):
    import numpy as np
    pr = cam3.pr
    capas = [(0.0, -0.35, (70, 50, 38), (58, 42, 32)), (-0.35, -1.7, (118, 84, 58), (96, 68, 48)),
             (-1.7, -3.3, (142, 108, 76), (118, 88, 62)), (-3.3, -7.0, (88, 64, 48), (52, 38, 30))]
    for za, zb, c0, c1 in capas:
        q = [pr(-30, 0, za), pr(30, 0, za), pr(30, 0, zb), pr(-30, 0, zb)]
        K.relleno_gradiente(L, q, [(0, c0), (1, c1)], pr(0, 0, za), pr(0, 0, zb))
        xs = np.linspace(-30, 30, 90)
        K.linea(L, [pr(x, 0, za + 0.06 * math.sin(x * 0.9 + za * 3)) for x in xs], (48, 34, 26), 3, alpha=0.7, puntas=False)
    rng = np.random.default_rng(8)
    for _ in range(70):
        X, Z = rng.uniform(-9, 9), rng.uniform(-6, -0.2)
        p, s = pr(X, 0, Z), cam3.escala(X, 0, Z)
        r = rng.uniform(0.05, 0.22) * s
        col = [(150, 124, 96), (86, 66, 50), (176, 150, 120)][rng.integers(0, 3)]
        K.poligono(L, K.elipse_pts(p[0], p[1], r * 1.3, r, n=14, rot=rng.uniform(0, 180)), col, alpha=0.9)
        K.poligono(L, K.elipse_pts(p[0] - r * 0.3, p[1] - r * 0.3, r * 0.5, r * 0.25, n=10), (220, 196, 160), alpha=0.35)
    # grietas: en el corte (desde la punta) y en el suelo visto desde arriba (desde la base)
    pg = K.anim(t, T["pesa"], 0.6, K.ease_entrada)
    if pg > 0:
        rng = np.random.default_rng(4)
        for ang in (-160, -128, -100, -70, -40, -15, 200):
            a = math.radians(ang)
            pts, x, z = [], 0.0, Z0G + 0.4
            for k in range(7):
                x += math.cos(a) * 0.45 * pg + rng.uniform(-0.12, 0.12)
                z += math.sin(a) * 0.45 * pg * 0.7 + rng.uniform(-0.1, 0.1)
                pts.append(pr(x, 0, min(-0.05, z)))
            K.linea(L, [pr(0, 0, Z0G + 0.4)] + pts, (30, 20, 14), 3.2, alpha=0.85)
        for ang in (15, 40, 65, 95, 120, 150, 170):
            a = math.radians(ang)
            pts, x, y = [], 0.0, 0.0
            for k in range(8):
                x += math.cos(a) * 0.55 * pg + rng.uniform(-0.12, 0.12)
                y += math.sin(a) * 0.55 * pg
                pts.append(pr(x, max(0.05, y), 0))
            K.linea(L, [pr(0, 0.3, 0)] + pts, (22, 16, 12), 3, alpha=0.8)
    K.linea(L, [pr(-30, 0, 0), pr(30, 0, 0)], (196, 150, 104), 3)


def plano_f(t, sem):
    L = lienzo_cielo(S4, sem)
    tx, ty = K.temblor(t - T["pesa"], 7, 9)
    L.camara(s=1.0 + 0.04 * K.anim(t, T["pesa"], 1.6, K.ease_estado), ancla=(852, 1090), temblor=(tx, ty))
    K.edificios3d(L, S4, alpha=0.5)
    K.suelo3d(L, S4)
    suelo_en_corte(L, S4, t)
    K.clavo3d(L, S4.pr, 0, 0, LG, z0=Z0G)
    base = S4.pr(0, 0, 0)
    K.nube_polvo(L, base[0], base[1], t - T["pesa"], ancho=300, n=18, dur=1.4)
    L.camara()
    K.numero_heroe(L, "50", "T", 60, 820, 360, t, T["cincuenta"])
    a = K.anim(t, T["cincuenta"] + 0.1, 0.3)
    K.texto(L, 68, 880, "1 ELEFANTE ≈ 5 T", 36, TINTA, "xbold", alpha=a)
    K.pictogramas(L, 70, 970, 10, 70, t if t >= T["cincuenta"] else -1, T["cincuenta"] + 0.12, paso=0.075)
    L.fundido_abajo(1560, 1720)
    sub(L, t)
    return L


# ------------------------------------------------------------------ G: ¿con qué le pegas? (y el gancho)
def plano_g(t, sem, t_sub=None):
    L = lienzo_cielo(S1, sem)
    mundo_gigante(L, S1, t)
    # martillo normal (chico) con ✗
    p = K.anim(t, T["con"], 0.45, K.ease_entrada)
    if p > 0:
        x = -120 + (250 + 120) * p
        K.martillo(L, x, 900 - 40 * math.sin(p * math.pi), 170, 60 - 300 * (1 - p))
        K.x_roja(L, 340, 860, 84, K.tramo(t, T["que"], 0.25))
    # martillo gigante: entra arriba a la derecha en "pegas", queda como en el cuadro 0
    q = K.anim(t, T["pegas"], 0.55, K.ease_entrada)
    if q > 0:
        x = 1300 + (MART_POS[0] - 1300) * q
        y = -120 + (MART_POS[1] + 120) * q
        ang = 150 + (MART_ANG - 150) * q
        if q < 0.98:                                   # estela de energía del arco
            for k in range(6):
                qq = max(0.0, q - 0.05 * (k + 1))
                xx, yy = 1300 + (MART_POS[0] - 1300) * qq, -120 + (MART_POS[1] + 120) * qq
                K.circulo(L, xx - 120, yy + 40, 10 - k, capa="energia", alpha=(1 - k / 6) * (1 - q))
        K.martillo(L, x, y, H1, ang)
    K.etiqueta(L, "20 M · 50 T", (CX - 30, 760), (66, 640), t, T["con"], tam=46, dur=0.45, texto_desde=0.2)
    L.fundido_abajo(1560, 1720)
    sub(L, t if t_sub is None else t_sub)
    return L


def cuadro(t, semilla=0):
    if t < T["esto"]:
        L = plano_g(DUR - 1 / FPS, semilla, t_sub=t)      # gancho = último cuadro (loop perfecto)
    elif t < T["un"]:
        L = plano_a(t, semilla)
    elif t < T["y"]:
        L = plano_b(t, semilla)
    elif t < T["pero"]:
        L = plano_c(t, semilla)
    elif t < T["veinte"]:
        L = plano_d(t, semilla)
    elif t < T["pesa"]:
        L = plano_e(t, semilla)
    elif t < T["con"]:
        L = plano_f(t, semilla)
    else:
        L = plano_g(t, semilla)
    return L.salida()


def _trabajo(i):
    return cuadro(i / FPS, i).tobytes()


def render(salida):
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    t0 = time.time()
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920",
           "-r", str(FPS), "-i", "-", "-i", VOZ, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium",
           "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", salida]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(6) as pool:
        for k, b in enumerate(pool.imap(_trabajo, range(NF), chunksize=2)):
            ff.stdin.write(b)
            if k % 30 == 0:
                print(f"cuadro {k}/{NF}  {time.time() - t0:.1f}s", flush=True)
    ff.stdin.close()
    ff.wait()
    mb = os.path.getsize(salida) / 1e6
    print(f"listo: {salida}  {NF} cuadros, {DUR:.2f}s, render {time.time() - t0:.1f}s, {mb:.1f} MB")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--cuadros":
        os.makedirs(sys.argv[3], exist_ok=True)
        for s in sys.argv[2].split(","):
            tt = float(s)
            t1 = time.time()
            cuadro(tt, int(tt * FPS)).save(os.path.join(sys.argv[3], f"t{tt:05.2f}.png"))
            print(s, f"{time.time() - t1:.2f}s")
    else:
        render(sys.argv[1] if len(sys.argv) > 1 else SALIDA)
