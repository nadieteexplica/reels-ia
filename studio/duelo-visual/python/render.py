# -*- coding: utf-8 -*-
"""Beat del clavo, v4 (23-nov-2026, ronda 2 contra virales), con kit_explica (laboratorio nocturno).

Planos (storyboard_v2.json). Cortes en la palabra; los marcados con ~ llevan barrido (whip pan, 2–3 cuadros).
  0     GANCHO  = último cuadro: clavo de 20 m, martillo gigante, persona con cota 1,8 M y titular "CLAVO DE 20 M"
  0,18  A  "Esto es un clavo"      clavo chico de héroe en tablón de testa, martillo listo, cinta 8 cm
  1,28  B  "Un martillazo"         plano cerrado del golpe (anticipación, estela, flash, ondas, chispas, temblor)
  1,97~ C  "y entra"               tablón en corte: la madera sube y se traga el clavo + golpe en "entra"
  2,75  D1 "Pero este"             corte por coincidencia al clavo de 20 m (cabeza en el mismo lugar)
  3,15~ D2 "clavo mide"            pantalla partida ×250: el clavo real en la mano | el gigante
  3,69~ E  "veinte metros"         alzado: cinta 20 M, número héroe, persona con cota, bus, edificio de 6 pisos
  4,35~ F  "y pesa 50 toneladas"   suelo en corte, golpe en "pesa", 10 elefantes que saltan uno a uno → 50 T
  6,21~ G  "¿Con qué le pegas?"    a ras de suelo mirando arriba: la persona con un martillo normal ✗; en "pegas"
                                    entra el martillo gigante
  7,29~ FINAL = el cuadro 0 (loop)

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

import numpy as np

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
SCRATCH = "/private/tmp/claude-501/-Users-tomas-Desktop-Proyecto/d4cb7467-771f-4533-993e-f4f18f1ccbe0/scratchpad/duelo"
SALIDA = os.path.join(SCRATCH, "python-v4.mp4")


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
         clavo2=t_palabra("clavo", 2), mide=t_palabra("mide"), veinte=t_palabra("veinte"), y2=t_palabra("y", 2),
         pesa=t_palabra("pesa"), cincuenta=t_palabra("cincuenta"), con=t_palabra("con"), que=t_palabra("qué"),
         pegas=t_palabra("pegas"))
cuadro_de = lambda t: round(t * FPS) / FPS
T_GOLPE = cuadro_de(T["martillazo"])
T_FINAL = DUR - 0.3                                   # los últimos ~0,3 s vuelven al cuadro 0
BARRIDOS = [T["y"], T["clavo2"], T["veinte"], T["con"], T_FINAL]
ZOOM_IN = 0.1                                        # A→B y E→F: crash zoom (sin salto de escala)

# ------------------------------------------------------------------ composición común (loop y cortes por
# coincidencia: la cabeza del clavo y el martillo caen siempre en el mismo lugar de la pantalla)
CX = 500
Y_SUP = 1360                 # superficie (tablón / suelo)
N1 = 780                     # clavo chico: 41 % del alto
Y_TAPA = Y_SUP - N1          # 580: la cabeza queda bajo los subtítulos (nunca chocan)
PR_A = K.proyector_oblicuo(CX, Y_SUP, 1.0, 0.30)
MART_POS, MART_ANG, H1 = (742, 695), 75.0, 440

LG, Z0G = 22.5, -2.5         # clavo gigante: 22,5 m, 2,5 m enterrados → la tapa a 20 m
S1 = K.Cam3D(Y=-60, Z=4, pitch=0, F=2340, cx=CX, cy=1204)        # plano ancho: tapa y=580, suelo y=1360
S3 = K.Cam3D(Y=-60, Z=4, pitch=0, F=2340, cx=780, cy=1264)       # alzado con el clavo a la derecha
S4 = K.Cam3D(Y=-14, Z=1.2, pitch=-8, F=1500, cx=880, cy=1311)    # a ras de suelo, el suelo en corte
SG = K.Cam3D(Y=-9.5, Z=0.7, pitch=23, F=980, cx=720, cy=900)     # mirando hacia arriba desde el pie
PERSONA = (1.5, -18.0)       # al pie del clavo, un poco adelante: ~100 px de alto en el plano ancho
BUS = (-12.4, 1.5)
BUS_E = (-14.6, 1.5)


def sub(L, t, **kw):
    K.subtitulos(L, WORDS, t, CLAVES, **kw)


def dolly(cam, t, t0, dur, avance=3.5):
    """Empuje lento de cámara (1,0 → ~1,08) en 3D: los edificios se mueven distinto que el clavo (parallax)."""
    k = K.anim(t, t0, dur, K.ease_estado)
    return K.Cam3D(Y=cam.Y + avance * k, Z=cam.Z, pitch=cam.pitch, F=cam.F, cx=cam.cx, cy=cam.cy, X=cam.X)


# ------------------------------------------------------------------ mundo gigante
def mundo_gigante(L, cam3, t, persona=True, cota=True, polvo_frente=True, bus=BUS):
    K.edificios3d(L, cam3)
    K.suelo3d(L, cam3)
    base, esc = cam3.pr(0, 0, 0), cam3.escala(0, 0, 0)
    R = 0.0275 * LG
    K.grietas_suelo(L, cam3, 0, 0, 1.0)
    K.brillo_suave(L, base[0] + esc * 0.5, base[1] + 2, esc * R * 4.5, max(5, esc * R * 0.9), (0, 0, 0), 0.75, 6)
    K.bus3d(L, cam3.pr, bus[0], bus[1])
    K.clavo3d(L, cam3.pr, 0, 0, LG, z0=Z0G, recorte=0.0, stops=K.CROMO_ATARDECER)
    tapa = cam3.pr(0, 0, LG + Z0G)
    K.brillo_suave(L, tapa[0] - esc * 0.4, tapa[1] + 4, esc * 1.6 * cam3.escala(0, 0, 20) / esc, 10, (255, 236, 210), 0.3, 8)
    for s in (-1, 1):                                   # tierra levantada en la base
        xb, h = base[0] + s * esc * R, esc * 0.35
        pts = [(xb - s * 3, base[1] + 3), (xb + s * esc * 0.15, base[1] - h), (xb + s * esc * 0.6, base[1] - h * 1.2),
               (xb + s * esc * 1.3, base[1] - h * 0.5), (xb + s * esc * 1.9, base[1] + 3)]
        K.poligono(L, pts, (84, 62, 48))
        K.linea(L, pts[1:4], (220, 150, 96) if s < 0 else (150, 170, 200), max(1.0, esc * 0.05), alpha=0.8)
    if persona:
        X, Y = PERSONA
        K.persona_espalda(L, cam3.pr, X, Y)
        if cota:
            pies, cab = cam3.pr(X, Y, 0), cam3.pr(X, Y, 1.72)
            xl = cam3.pr(X + 0.55, Y, 0)[0]
            K.cota_persona(L, xl + L.ct[0], pies[1], cab[1], "1,8 M", "der")
    if polvo_frente:                                    # primer plano: piedras fuera de foco
        with K.desenfoque(L, 4) as d:
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


# ------------------------------------------------------------------ cuadro 0 / final
def plano_final(t, sem):
    k = 1 - K.anim(t, T_FINAL, DUR - 1 / FPS - T_FINAL, K.ease_entrada)   # 1 → 0: al final es el cuadro 0 exacto
    cam3 = K.Cam3D(Y=S1.Y + 4.5 * k, Z=S1.Z, pitch=S1.pitch, F=S1.F, cx=S1.cx, cy=S1.cy)
    L = lienzo_cielo(cam3, sem)
    mundo_gigante(L, cam3, t)
    K.martillo(L, MART_POS[0] + 40 * k, MART_POS[1] - 60 * k, H1, MART_ANG - 14 * k)
    K.titular(L, "CLAVO DE 20 M", alpha=1 - k)
    L.fundido_abajo(1560, 1720)
    return L


# ------------------------------------------------------------------ A: el clavo chico
def plano_a(t, sem):
    L = K.Lienzo(EST, semilla=sem, fondo_img=K.fondo_estudio(EST))
    zi = K.anim(t, T["un"] - ZOOM_IN, ZOOM_IN, lambda p: p * p)
    L.camara(s=(1.0 + 0.08 * K.anim(t, T["esto"], 1.1, K.ease_estado)) * (1 + 1.6 * zi), ancla=(CX, Y_TAPA + 20))
    K.tabla_testa(L, 110, 890, Y_SUP + 23, 460, prof=46)
    K.sombra_contacto(L, CX + 10, Y_SUP + 2, 40, 7, 0.7)
    K.ao(L, CX - 30, CX + 40, Y_SUP + 3, 8, 0.4)
    K.clavo3d(L, PR_A, 0, 0, N1)
    ant = K.anim(t, T["un"] - 0.16, 0.16, K.ease_estado)        # anticipación justo antes de "Un"
    ang = MART_ANG + 1.2 * math.sin(t * 3.4) + 9 * ant
    K.martillo(L, MART_POS[0] + 18 * ant, MART_POS[1] - 26 * ant, H1, ang)
    marcas = [(i / 80, 15 if i % 10 == 0 else (10 if i % 5 == 0 else 6), None) for i in range(81)]
    K.regla(L, 330, Y_SUP, Y_TAPA, K.anim(t, T["clavo"], 0.6, K.ease_entrada), marcas, ancho=34, cam=True)
    L.camara()
    K.etiqueta(L, "CLAVO · 8 CM", (CX - 52, Y_TAPA + 18), (66, 505), t, T["clavo"], tam=48, dur=0.6, texto_desde=0.3,
               t1=T["un"] - ZOOM_IN)
    L.fundido_abajo(1560, 1720)
    sub(L, t)
    K.zoom_rapido(L, zi, (CX, Y_TAPA + 20))
    return L


# ------------------------------------------------------------------ B: el golpe
NB, HB = 1600, 1650
Y_TAPA_B = 1080
PR_B = K.proyector_oblicuo(480, Y_TAPA_B + NB, 1.0, 0.30)
P_TOQUE = next(i / 2000 for i in range(2001) if K.ease_aterriza(i / 2000) >= 1.0)
P_PICO, Y_PICO = K.pico_aterriza()
D_SWING = (T_GOLPE - T["un"]) / P_TOQUE


def y_martillo_b(t):
    p = K.tramo(t, T["un"], D_SWING)
    y = K.ease_aterriza(p)
    if p < P_TOQUE:
        return -330 * (1 - y)
    return -22 * (y - 1) / (Y_PICO - 1)          # rebote: lo que la curva pasa de 1


def plano_b(t, sem):
    L = K.Lienzo(EST, semilla=sem, fondo_img=K.fondo_estudio(EST, luz=(0.3, 0.32)))
    e = t - T_GOLPE
    tx, ty = K.temblor(e, 16, 8)
    llegada = 1 - K.anim(t, T["un"], 0.1, K.ease_entrada)          # sigue el crash zoom del plano A
    zoom = (1.0 + 0.05 * (1 - K.anim(t, T_GOLPE, 0.5, K.ease_entrada)) if e >= 0 else 1.05) * (1 - 0.18 * llegada)
    L.camara(s=zoom, ancla=(480, Y_TAPA_B), temblor=(tx, ty))
    K.clavo3d(L, PR_B, 0, 0, NB)
    cy0 = Y_TAPA_B - 0.287 * HB
    if -2.5 / FPS < e < 0:                       # estela de 2 cuadros
        ya, yb = cy0 + y_martillo_b(t - 1 / FPS) + 0.2 * HB, cy0 + y_martillo_b(t) + 0.287 * HB
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
    K.zoom_rapido(L, llegada * 0.9, (480, Y_TAPA_B))
    return L


# ------------------------------------------------------------------ C: el corte de la madera
T_ENTRA = cuadro_de(T["entra"])


def plano_c(t, sem):
    L = K.Lienzo(EST, semilla=sem, fondo_img=K.fondo_estudio(EST))
    p = K.anim(t, T_ENTRA, 0.42, K.ease_estado)
    ys = Y_SUP - (N1 - 0.03 * N1) * p
    e = t - T_ENTRA
    tx, ty = K.temblor(e, 9, 6)
    L.camara(s=1.0 + 0.06 * K.anim(t, T["y"], 0.8, K.ease_estado), ancla=(CX, Y_TAPA + 60), temblor=(tx, ty))
    K.madera_corte(L, -60, 1140, ys, 1800, CX, Y_SUP - ys, 0.0275 * N1)
    K.clavo3d(L, PR_A, 0, 0, N1)
    K.esquirlas(L, CX, ys, e, n=12)
    K.polvo(L, CX, ys, e - 0.04, n=12)
    L.camara()
    if 0 <= e < 1 / FPS:
        K.flash_blanco(L, 0.5)
    # un solo valor claro: 8 CM, y una barra que muestra cuánto ya entró
    a = K.anim(t, T["y"] + 0.05, 0.25)
    if a > 0:
        b = (60, 690, 400, 900)
        L.d.rounded_rectangle([L.P(b[0], b[1], False), L.P(b[2], b[3], False)], radius=L.S(26, False),
                              fill=(14, 16, 22, int(230 * a)))
        K.numero_heroe(L, "8", "CM", 88, 830, 120, t, T["y"] + 0.05)
        m, d = L.temporal()
        d.rounded_rectangle([L.P(88, 856, False), L.P(372, 878, False)], radius=L.S(11, False), outline=255, width=int(L.S(3, False)))
        if p > 0.01:
            d.rounded_rectangle([L.P(88, 856, False), L.P(88 + 284 * p, 878, False)], radius=L.S(11, False), fill=255)
        L.fundir(m, alpha=a, capa="energia")
    L.fundido_abajo(1560, 1720)
    sub(L, t)
    return L


# ------------------------------------------------------------------ D1: corte por coincidencia al gigante
def plano_d1(t, sem):
    cam3 = dolly(S1, t, T["pero"], 0.6, 2.5)
    L = lienzo_cielo(cam3, sem)
    mundo_gigante(L, cam3, t)
    L.fundido_abajo(1560, 1720)
    sub(L, t)
    return L


# ------------------------------------------------------------------ D2: pantalla partida ×250
def plano_d2(t, sem):
    cam3 = dolly(K.Cam3D(Y=-60, Z=4, pitch=0, F=2340, cx=790, cy=1204), t, T["clavo2"], 0.6, 3)
    L = lienzo_cielo(cam3, sem)
    mundo_gigante(L, cam3, t, cota=False)
    # mitad izquierda: el clavo real en la mano, en el estudio
    I = K.Lienzo(EST, semilla=sem, fondo_img=K.fondo_estudio(EST, luz=(0.2, 0.35)))
    zi = 1.0 + 0.05 * K.anim(t, T["clavo2"], 0.6, K.ease_estado)
    I.camara(s=zi, ancla=(270, 1000))
    largo, cx, yb = 560, 250, 1330
    pr = K.proyector_oblicuo(cx, yb, 1.0, 0.3)
    K.mano_pinza(I, cx - 12, yb - largo * 0.6, 1.25, cam=True, nail=lambda: K.clavo3d(I, pr, 0, 0, largo, ns=60))
    corte = int(540 * L.ss)
    L.im.paste(I.im.crop((0, 0, corte, L.im.size[1])), (0, 0))
    L.en.paste(I.en.crop((0, 0, corte, L.en.size[1])), (0, 0))
    m, d = L.temporal()
    K.linea(L, [(540, 560), (540, 1560)], ancho=6, capa=d, cam=False)
    L.fundir(m, alpha=1.0, capa="energia")
    K.texto(L, 70, 1440, "8 CM", 72, TINTA, "black", trazo=6)
    pop = K.anim(t, T["clavo2"] + 0.08, 0.25)
    K.pildora_energia(L, "×250", 540, 690, 84, alpha=min(1, pop * 2), pop=0.8 + 0.2 * pop)
    L.fundido_abajo(1560, 1720)
    sub(L, t)
    return L


# ------------------------------------------------------------------ E: alzado con la cinta de 20 m
def plano_e(t, sem):
    cam3 = dolly(S3, t, T["veinte"], 0.66, 3)
    L = lienzo_cielo(cam3, sem)
    zi = K.anim(t, T["y2"] - ZOOM_IN, ZOOM_IN, lambda p: p * p)
    base_e = cam3.pr(0, 0, 0)
    L.camara(s=1 + 1.4 * zi, ancla=base_e)
    mundo_gigante(L, cam3, t, persona=False, bus=BUS_E)
    X, Y = -1.6, PERSONA[1]
    K.persona_espalda(L, cam3.pr, X, Y)
    pies, cab = cam3.pr(X, Y, 0), cam3.pr(X, Y, 1.72)
    K.cota_persona(L, cam3.pr(X - 0.55, Y, 0)[0], pies[1], cab[1], "1,8 M", "izq")
    y_suelo, y_tapa = cam3.pr(0, 0, 0)[1], cam3.pr(0, 0, 20)[1]
    marcas = [(i / 20, 18 if i % 5 == 0 else 9, None) for i in range(21)]
    K.regla(L, cam3.pr(1.9, 0, 0)[0], y_suelo, y_tapa, K.anim(t, T["veinte"], 0.5, K.ease_entrada), marcas, ancho=36)
    K.numero_heroe(L, "20", "M", 60, 920, 320, t, T["veinte"])
    K.texto(L, 68, 990, "DE ALTO", 52, TINTA, "black", alpha=K.anim(t, T["veinte"] + 0.1, 0.25), trazo=5)
    L.camara()
    L.fundido_abajo(1560, 1720)
    sub(L, t, ocultar={"veinte", "metros"})
    K.zoom_rapido(L, zi, base_e)
    return L


# ------------------------------------------------------------------ F: el peso
T_PESA = cuadro_de(T["pesa"])
ELEF_T0, ELEF_PASO = T["y2"] + 0.02, (T["cincuenta"] - 0.05 - T["y2"] - 0.02) / 9   # el 10.º cae justo en "cincuenta"


def suelo_en_corte(L, cam3, t):
    pr = cam3.pr
    capas = [(0.0, -0.35, (70, 50, 38), (58, 42, 32)), (-0.35, -1.7, (118, 84, 58), (96, 68, 48)),
             (-1.7, -3.3, (142, 108, 76), (118, 88, 62)), (-3.3, -7.0, (88, 64, 48), (52, 38, 30))]
    xs = np.linspace(-30, 30, 90)
    for za, zb, c0, c1 in capas:
        q = [pr(-30, 0, za), pr(30, 0, za), pr(30, 0, zb), pr(-30, 0, zb)]
        K.relleno_gradiente(L, q, [(0, c0), (1, c1)], pr(0, 0, za), pr(0, 0, zb))
        K.linea(L, [pr(x, 0, za + 0.06 * math.sin(x * 0.9 + za * 3)) for x in xs], (48, 34, 26), 3, alpha=0.7, puntas=False)
    rng = np.random.default_rng(8)
    for _ in range(70):
        X, Z = rng.uniform(-9, 9), rng.uniform(-6, -0.2)
        p, s = pr(X, 0, Z), cam3.escala(X, 0, Z)
        r = rng.uniform(0.05, 0.22) * s
        col = [(150, 124, 96), (86, 66, 50), (176, 150, 120)][rng.integers(0, 3)]
        K.poligono(L, K.elipse_pts(p[0], p[1], r * 1.3, r, n=14, rot=rng.uniform(0, 180)), col, alpha=0.9)
        K.poligono(L, K.elipse_pts(p[0] - r * 0.3, p[1] - r * 0.3, r * 0.5, r * 0.25, n=10), (220, 196, 160), alpha=0.35)
    pg = K.anim(t, T_PESA, 0.6, K.ease_entrada)
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
    e = t - T_PESA
    tx, ty = K.temblor(e, 9, 6)
    llegada = 1 - K.anim(t, T["y2"], 0.1, K.ease_entrada)
    L.camara(s=(1.0 + 0.08 * K.anim(t, T["y2"], 1.8, K.ease_estado)) * (1 - 0.2 * llegada), ancla=(880, 1230), temblor=(tx, ty))
    K.edificios3d(L, S4, alpha=0.5)
    K.suelo3d(L, S4)
    suelo_en_corte(L, S4, t)
    K.clavo3d(L, S4.pr, 0, 0, LG, z0=Z0G, stops=K.CROMO_ATARDECER)
    base = S4.pr(0, 0, 0)
    K.nube_polvo(L, base[0], base[1], e, ancho=300, n=18, dur=1.4)
    K.esquirlas(L, base[0] - 60, base[1], e, n=14, color=(170, 130, 96), semilla=5, vel=1100)
    L.camara()
    if 0 <= e < 1 / FPS:
        K.flash_blanco(L, 0.55)
    # 10 elefantes que saltan uno a uno (pop 0 → 1,1 → 1) y el contador; el 10.º cae en "cincuenta"
    a_pl = K.anim(t, ELEF_T0 - 0.04, 0.2)
    if a_pl > 0:
        L.d.rounded_rectangle([L.P(36, 856, False), L.P(800, 1196, False)], radius=L.S(30, False), fill=(12, 14, 22, int(170 * a_pl)))
    k = K.pictogramas_pop(L, 58, 1040, 10, 108, t, ELEF_T0, paso=ELEF_PASO, gx=146, gy=134, forma=K.elefante_3d)
    if k:
        K.texto(L, 62, 912, f"×{k} ELEFANTES", 54, TINTA, "black", trazo=5)
    K.numero_heroe(L, "50", "T", 60, 830, 330, t, T["cincuenta"])
    L.fundido_abajo(1560, 1720)
    sub(L, t, x_centro=420, ancho_max=700, ocultar={"cincuenta", "toneladas"})
    K.zoom_rapido(L, llegada * 0.9, (880, 1230))
    return L


# ------------------------------------------------------------------ G: ¿con qué le pegas? (mirando hacia arriba)
def plano_g(t, sem):
    cam3 = K.Cam3D.mezcla(SG, K.Cam3D(Y=-8.3, Z=0.7, pitch=25, F=980, cx=720, cy=900), K.anim(t, T["con"], 1.1, K.ease_estado))
    L = lienzo_cielo(cam3, sem)
    K.edificios3d(L, cam3)
    K.suelo3d(L, cam3)
    K.grietas_suelo(L, cam3, 0, 0, 1.0)
    base = cam3.pr(0, 0, 0)
    K.brillo_suave(L, base[0] + 20, base[1] + 4, 200, 30, (0, 0, 0), 0.7, 6)
    K.bus3d(L, cam3.pr, BUS[0], BUS[1])
    K.clavo3d(L, cam3.pr, 0, 0, LG, z0=Z0G, recorte=0.0, stops=K.CROMO_ATARDECER)
    # la persona (de espaldas, grande) levanta un martillo normal: de verdad, a escala
    X, Y = -1.0, -6.8
    K.persona_espalda(L, cam3.pr, X, Y)
    hombro, mano = cam3.pr(X + 0.24, Y, 1.42), cam3.pr(X + 0.52, Y, 1.92)
    esc = cam3.escala(X, Y, 1.7)
    K.linea(L, [hombro, mano], (52, 58, 76), 0.11 * esc)
    K.linea(L, [hombro, mano], K.FRIO, 0.02 * esc, alpha=0.7)
    Hm = 0.3 * esc
    a = math.radians(100)
    K.martillo(L, mano[0] - math.cos(a) * 0.9 * Hm, mano[1] - math.sin(a) * 0.9 * Hm, Hm, 100)
    K.circulo(L, mano[0], mano[1], 0.045 * esc, (150, 112, 90))
    K.x_roja(L, mano[0] + 0.95 * Hm, mano[1] - 0.45 * Hm, 0.75 * Hm, K.tramo(t, T["que"], 0.25))
    # en "pegas" entra el martillo gigante desde arriba a la derecha (visto desde abajo, enorme)
    q = K.anim(t, T["pegas"], 0.5, K.ease_entrada)
    if q > 0:
        x0, y0, x1, y1 = 1350, -420, 840, 170
        hx, hy = x0 + (x1 - x0) * q, y0 + (y1 - y0) * q
        if q < 0.97:                                   # estela del arco
            m, d = L.temporal()
            for k in range(1, 5):
                qq = max(0.0, q - 0.07 * k)
                K.linea(L, [(x0 + (x1 - x0) * qq - 150, y0 + (y1 - y0) * qq + 210), (hx - 150, hy + 210)],
                        ancho=12 - 2 * k, capa=d, cam=True)
            L.fundir(m, alpha=0.8 * (1 - q), capa="energia")
        K.martillo(L, hx, hy, 780, 22 + 25 * (1 - q))
    L.fundido_abajo(1560, 1720)
    sub(L, t, x_centro=360, ancho_max=600)
    return L


def cuadro(t, semilla=0):
    if t < T["esto"]:
        L = plano_final(DUR - 1 / FPS, semilla)      # cuadro 0 = último cuadro (loop perfecto)
    elif t >= T_FINAL:
        L = plano_final(t, semilla)
    elif t < T["un"]:
        L = plano_a(t, semilla)
    elif t < T["y"]:
        L = plano_b(t, semilla)
    elif t < T["pero"]:
        L = plano_c(t, semilla)
    elif t < T["clavo2"]:
        L = plano_d1(t, semilla)
    elif t < T["veinte"]:
        L = plano_d2(t, semilla)
    elif t < T["y2"]:
        L = plano_e(t, semilla)
    elif t < T["con"]:
        L = plano_f(t, semilla)
    else:
        L = plano_g(t, semilla)
    for tc in BARRIDOS:                                # whip pan: 2 cuadros antes y 3 después del corte
        d = t - tc
        if -2.5 / FPS < d < 0:
            K.barrido(L, 0.45 + 0.45 * (1 + d * FPS / 2.5))
        elif 0 <= d < 2.5 / FPS:
            K.barrido(L, 0.9 * (1 - d * FPS / 2.5))
    return L.salida()


def _trabajo(i):
    return cuadro(i / FPS, i).tobytes()


def voz_normalizada():
    """La voz a −14 LUFS (pico −1,5 dBTP) con loudnorm en dos pasadas."""
    out = os.path.join(SCRATCH, "voz_-14lufs.wav")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", VOZ, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    j = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    filtro = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
              f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", VOZ, "-af", filtro, "-ar", "48000", out], check=True)
    return out


def render(salida):
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    t0 = time.time()
    voz = voz_normalizada()
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920",
           "-r", str(FPS), "-i", "-", "-i", voz, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium",
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
