# -*- coding: utf-8 -*-
"""Beat del clavo, v5 (23-nov-2026, ritmo), con kit_explica (laboratorio nocturno).

Nota del dueño sobre v4: "pasan las cosas muy rápido". v5: los cambios pasan DENTRO del plano, donde ya está el ojo.
  0–2,75     un plano: clavo de 8 cm con cinta; martillazo con rebote y brillo suave; en "entra" se hunde y la cinta
             se recoge con él (8 cm → 0 sin texto extra)
  2,75–6,21  corte por coincidencia al clavo de 20 m (la cabeza en el mismo lugar); desplazamiento lento; en el mismo
             lugar de la izquierda se reemplazan: tarjeta ×250 (el real en la mano) → 20 M → 10 elefantes → 50 T;
             en "toneladas" se raja el suelo
  6,21–fin   a ras de suelo: la persona con un martillo normal (✗) y en "pegas" llega el martillo gigante
Sin barridos, sin crash zoom, sin flashes blancos; el texto se lee quieto.

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
SALIDA = os.path.join(SCRATCH, "python-v5.mp4")
MEZCLA = os.path.join(SCRATCH, "beat-mix.wav")         # voz + efectos (tools/sonido/mezclar.py studio/duelo-visual/sfx-plan.json)


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


# ==================================================================================================================
# v5 (ritmo): los cambios pasan DENTRO del plano, donde ya está el ojo. Sólo 2 cortes (cuando cambia la idea), sin
# barridos ni crash zoom, sin flashes blancos de 1–2 cuadros (el golpe es un brillo suave de 4 cuadros), el texto se lee
# quieto, y nunca más de ~1,5 s sin un cambio.
# ==================================================================================================================
P_TOQUE = next(i / 2000 for i in range(2001) if K.ease_aterriza(i / 2000) >= 1.0)   # primer contacto de la curva
P_PICO, Y_PICO = K.pico_aterriza()
D_SWING = (T_GOLPE - T["un"]) / P_TOQUE              # el contacto cae justo en "martillazo"
T_ENTRA = cuadro_de(T["entra"])
ELEF_T0, ELEF_PASO = T["y2"] + 0.05, 0.12                 # 10 elefantes en ~1,1 s (se pueden contar)
REPOSO = (742.0, 695.0, 75.0)                         # martillo listo (cabeza x, y, ángulo)
ATRAS = (790.0, 610.0, 96.0)                          # anticipación
TOQUE = (CX, Y_TAPA - 0.287 * H1, 0.0)               # la cara sobre la cabeza del clavo
CTRL = (600.0, 330.0)                                 # el arco del golpe pasa por arriba


def pose_martillo(t):
    """Martillo del plano A: reposo → anticipación → golpe con rebote en 'martillazo' → vuelve al reposo en 'entra'."""
    ant = K.anim(t, T["un"] - 0.2, 0.2, K.ease_estado)
    if t < T["un"]:
        return tuple(r + (a - r) * ant for r, a in zip(REPOSO, ATRAS))
    p = K.tramo(t, T["un"], D_SWING)
    y = K.ease_aterriza(p)
    if p < P_TOQUE:
        u = y                                                     # arco cuadrático ATRÁS → TOQUE
        x = (1 - u) ** 2 * ATRAS[0] + 2 * (1 - u) * u * CTRL[0] + u * u * TOQUE[0]
        yy = (1 - u) ** 2 * ATRAS[1] + 2 * (1 - u) * u * CTRL[1] + u * u * TOQUE[1]
        return (x, yy, ATRAS[2] + (TOQUE[2] - ATRAS[2]) * u)
    reb = (y - 1) / (Y_PICO - 1)                                  # rebote: lo que la curva pasa de 1
    x, yy, ang = TOQUE[0] + 10 * reb, TOQUE[1] - 26 * reb, TOQUE[2] + 3 * reb
    v = K.anim(t, T_ENTRA + 0.1, 0.55, K.ease_estado)             # en "entra" vuelve al reposo
    return (x + (REPOSO[0] - x) * v, yy + (REPOSO[1] - yy) * v, ang + (REPOSO[2] - ang) * v)


def plano_clavo(t, sem):
    """0–2,75 s, un solo plano: el clavo, la cinta de 8 cm, el martillazo y el hundimiento pasan adentro."""
    L = K.Lienzo(EST, semilla=sem, fondo_img=K.fondo_estudio(EST))
    e = t - T_GOLPE
    tx, ty = K.temblor(e, 6, 6)
    L.camara(s=1.0 + 0.09 * K.anim(t, 0.0, T["pero"], K.ease_estado), ancla=(CX, 980), temblor=(tx, ty))
    K.tabla_testa(L, 110, 890, Y_SUP + 23, 460, prof=46)
    hunde = K.anim(t, T_ENTRA, 0.45, K.ease_estado) * (N1 - 0.03 * N1)
    K.sombra_contacto(L, CX + 10, Y_SUP + 2, 40 + 30 * hunde / N1, 7, 0.7)
    K.ao(L, CX - 30, CX + 40, Y_SUP + 3, 8, 0.4)
    K.clavo3d(L, PR_A, 0, 0, N1, z0=-hunde, recorte=0.0)
    # la cinta mide lo que queda afuera: 8 cm y se recoge con el clavo
    marcas = [(i / 80, 15 if i % 10 == 0 else (10 if i % 5 == 0 else 6), None) for i in range(81)]
    p_cinta = K.anim(t, T["clavo"], 0.6, K.ease_entrada) * (1 - hunde / N1)
    K.regla(L, 330, Y_SUP, Y_TAPA, p_cinta, marcas, ancho=34, cam=True)
    x, y, ang = pose_martillo(t)
    K.martillo(L, x, y, H1, ang)
    K.impacto(L, CX, Y_TAPA + 8, e, escala=0.62, ry=0.3, chispas=10)
    if 0 <= e < 4 / FPS:                                          # brillo suave de 4 cuadros (no un flash blanco)
        k = 1 - e * FPS / 4
        L.brillo = 1 + 1.8 * k
        K.brillo_suave(L, CX, Y_TAPA + 8, 150, 60, (255, 240, 210), 0.55 * k, 14)
    ee = t - T_ENTRA
    K.esquirlas(L, CX, Y_SUP, ee, n=12)
    K.polvo(L, CX, Y_SUP, ee - 0.04, n=12)
    L.camara()
    a8 = K.anim(t, T["clavo"] + 0.1, 0.3) * (1 - K.anim(t, T_ENTRA, 0.15))
    if a8 > 0:
        K.numero_heroe(L, "8", "CM", 56, Y_TAPA + 140, 126, t, T["clavo"] + 0.1, alpha=a8)
    L.fundido_abajo(1560, 1720)
    sub(L, t)
    return L


S3V = K.Cam3D(Y=-60, Z=4, pitch=0, F=2340, cx=780, cy=1264)


def cam_gigante(t):
    """Plano del gigante: corte por coincidencia en 'Pero' (la cabeza donde estaba la del clavo chico) y un
    desplazamiento LENTO (0,7 s) para dejarle lugar a la tarjeta y a los números; después, empuje lento."""
    k = K.anim(t, T["pero"] + 0.2, 0.7, K.ease_estado)
    c = K.Cam3D.mezcla(S1, S3V, k)
    return dolly(c, t, T["pero"] + 0.9, T["con"] - T["pero"] - 0.9, 3.0)


def tarjeta_real(L, t):
    """×250: el clavo real en la mano entra deslizándose a la izquierda (donde está el ojo) y sale en 'veinte'."""
    p_in = K.anim(t, T["pero"] + 0.2, 0.5, K.ease_entrada)
    p_out = K.anim(t, T["y2"] - 0.05, 0.35, K.ease_salida)
    if p_in <= 0 or p_out >= 1:
        return
    dx = -560 * (1 - p_in) - 560 * p_out
    b = (40 + dx, 1030, 470 + dx, 1470)
    L.d.rounded_rectangle([L.P(b[0] + 8, b[1] + 14, False), L.P(b[2] + 8, b[3] + 14, False)], radius=L.S(30, False), fill=(0, 0, 0, 110))
    L.d.rounded_rectangle([L.P(b[0], b[1], False), L.P(b[2], b[3], False)], radius=L.S(30, False), fill=(20, 19, 22, 245))
    m, d = L.temporal()
    d.rounded_rectangle([L.P(b[0], b[1], False), L.P(b[2], b[3], False)], radius=L.S(30, False), outline=255, width=int(L.S(4, False)))
    L.fundir(m, alpha=1.0, capa="energia")
    largo, cx, yb = 330, b[0] + 150, b[3] - 40
    pr = K.proyector_oblicuo(cx, yb, 1.0, 0.3)
    K.mano_pinza(L, cx - 9, yb - largo * 0.6, 0.85, cam=False, nail=lambda: K.clavo3d(L, pr, 0, 0, largo, ns=60, cam=False))
    K.texto(L, b[0] + 30, b[1] + 80, "8 CM", 64, TINTA, "black", trazo=6)
    pop = K.anim(t, T["pero"] + 0.45, 0.25)
    K.pildora_energia(L, "×250", b[2] - 20, b[1] + 6, 76, alpha=min(1, pop * 2) * (1 - p_out), pop=0.8 + 0.2 * pop)


def plano_gigante(t, sem):
    """2,75–6,21 s, un solo plano: ×250, 20 M, los elefantes y 50 T se reemplazan en el MISMO lugar de la izquierda."""
    cam3 = cam_gigante(t)
    L = lienzo_cielo(cam3, sem)
    e_t = t - T["cincuenta"] - 0.37                               # "toneladas": el peso se siente en la base
    tx, ty = K.temblor(e_t, 6, 6)
    L.camara(temblor=(tx, ty))
    mundo_gigante(L, cam3, t, persona=False, bus=BUS_E)
    base = cam3.pr(0, 0, 0)
    K.grietas_suelo(L, cam3, 0, 0, K.anim(t, T["cincuenta"] + 0.37, 0.6, K.ease_entrada), n=12, largo=10, semilla=9)
    K.nube_polvo(L, base[0], base[1], e_t, ancho=260, n=16, dur=1.2)
    K.esquirlas(L, base[0], base[1], e_t, n=12, color=(170, 130, 96), semilla=5, vel=900)
    X, Y = -1.6, PERSONA[1]
    K.persona_espalda(L, cam3.pr, X, Y)
    L.camara()
    tarjeta_real(L, t)
    # 20 M: cinta y número (salen en "y pesa")
    sale20 = K.anim(t, T["y2"], 0.35, K.ease_salida)
    if t >= T["veinte"] and sale20 < 1:
        y_suelo, y_tapa = cam3.pr(0, 0, 0)[1], cam3.pr(0, 0, 20)[1]
        marcas = [(i / 20, 18 if i % 5 == 0 else 9, None) for i in range(21)]
        K.regla(L, cam3.pr(1.9, 0, 0)[0], y_suelo, y_tapa, K.anim(t, T["veinte"], 0.5, K.ease_entrada), marcas,
                ancho=36, alpha=1 - sale20)
        K.numero_heroe(L, "20", "M", 60, 900, 320, t, T["veinte"], alpha=1 - sale20)
        K.texto(L, 68, 970, "DE ALTO", 52, TINTA, "black", alpha=K.anim(t, T["veinte"] + 0.1, 0.25) * (1 - sale20), trazo=5)
    # el peso: 10 elefantes que saltan en el mismo lugar, y 50 T donde estaba el 20 M
    sale50 = K.anim(t, T["con"] - 0.35, 0.35, K.ease_salida)
    if t >= T["y2"] and sale50 < 1:
        a_pl = K.anim(t, ELEF_T0 - 0.04, 0.2) * (1 - sale50)
        L.d.rounded_rectangle([L.P(36, 930, False), L.P(712, 1236, False)], radius=L.S(30, False), fill=(12, 14, 22, int(170 * a_pl)))
        if sale50 < 0.5:
            k = K.pictogramas_pop(L, 52, 1100, 10, 94, t, ELEF_T0, paso=ELEF_PASO, gx=132, gy=114, forma=K.elefante_3d)
            if k:
                K.texto(L, 60, 990, f"×{k} ELEFANTES", 60, TINTA, "black", trazo=6, alpha=1 - 2 * sale50)
        K.numero_heroe(L, "50", "T", 60, 900, 320, t, T["cincuenta"], alpha=1 - sale50)
    L.fundido_abajo(1560, 1720)
    ocultar = set()
    if t >= T["veinte"]:
        ocultar |= {"veinte", "metros"}
    if t >= T["cincuenta"]:
        ocultar |= {"cincuenta", "toneladas"}
    sub(L, t, ocultar=ocultar)
    return L


SQ = K.Cam3D(Y=-14, Z=0.7, pitch=30, F=760, cx=650, cy=1000)     # desde abajo, la cabeza del clavo a la vista
SQ2 = K.Cam3D(Y=-12.8, Z=0.7, pitch=30.5, F=760, cx=650, cy=1000)
HG = 640                                                           # martillo gigante (px)


def plano_pregunta(t, sem):
    """6,21 s → fin: la persona con un martillo normal (✗ en 'qué'); en 'pegas' el martillo gigante entra entero
    desde la derecha y golpea la cabeza (brillo suave, ondas, chispas, polvo). Cámara: sólo empuje lento."""
    cam3 = K.Cam3D.mezcla(SQ, SQ2, K.anim(t, T["con"], DUR - T["con"], K.ease_estado))
    L = lienzo_cielo(cam3, sem)
    t_golpe = cuadro_de(T["pegas"] + 0.05)
    e = t - t_golpe
    tx, ty = K.temblor(e, 8, 6)
    L.camara(temblor=(tx, ty))
    K.edificios3d(L, cam3)
    K.suelo3d(L, cam3)
    K.grietas_suelo(L, cam3, 0, 0, 1.0)
    base = cam3.pr(0, 0, 0)
    K.brillo_suave(L, base[0] + 20, base[1] + 4, 160, 24, (0, 0, 0), 0.7, 6)
    K.bus3d(L, cam3.pr, BUS[0], BUS[1])
    K.clavo3d(L, cam3.pr, 0, 0, LG, z0=Z0G, recorte=0.0, stops=K.CROMO_ATARDECER)
    tapa = cam3.pr(0, 0, LG + Z0G)
    X, Y = -1.7, -10.2
    K.persona_espalda(L, cam3.pr, X, Y)
    hombro, mano = cam3.pr(X + 0.24, Y, 1.42), cam3.pr(X + 0.52, Y, 1.92)
    esc = cam3.escala(X, Y, 1.7)
    K.linea(L, [hombro, mano], (52, 58, 76), 0.11 * esc)
    K.linea(L, [hombro, mano], K.FRIO, 0.02 * esc, alpha=0.7)
    Hm = 0.33 * esc
    a = math.radians(100)
    K.martillo(L, mano[0] - math.cos(a) * 0.9 * Hm, mano[1] - math.sin(a) * 0.9 * Hm, Hm, 100)
    K.circulo(L, mano[0], mano[1], 0.045 * esc, (150, 112, 90))
    K.x_roja(L, mano[0] + 0.9 * Hm, mano[1] - 0.5 * Hm, 0.8 * Hm, K.tramo(t, T["que"], 0.3))
    # el martillo gigante: entra entero por la derecha (0,35 s) y cae sobre la cabeza en "pegas"
    ang_t = 18.0
    ca, sa = math.cos(math.radians(ang_t)), math.sin(math.radians(ang_t))
    toque = (tapa[0] + sa * 0.287 * HG, tapa[1] - 6 - ca * 0.287 * HG)          # centro de la cabeza al tocar
    alto = (toque[0] + 190, toque[1] - 330, 55.0)
    entra = K.anim(t, T["que"], 0.3, K.ease_entrada)
    baja = K.tramo(t, t_golpe - 0.18, 0.18) ** 2                                 # cae acelerando
    if entra > 0:
        x0, y0 = 1250, -200
        hx = x0 + (alto[0] - x0) * entra + (toque[0] - alto[0]) * baja
        hy = y0 + (alto[1] - y0) * entra + (toque[1] - alto[1]) * baja
        ang = 120 + (alto[2] - 120) * entra + (ang_t - alto[2]) * baja
        K.martillo(L, hx, hy, HG, ang)
    K.impacto(L, tapa[0], tapa[1], e, escala=0.8, ry=0.32, chispas=12)
    K.nube_polvo(L, tapa[0], tapa[1] + 10, e, ancho=180, n=12, semilla=4, color=(170, 150, 130), dur=0.7, alpha=0.5)
    if 0 <= e < 4 / FPS:
        k = 1 - e * FPS / 4
        L.brillo = 1 + 1.8 * k
        K.brillo_suave(L, tapa[0], tapa[1], 160, 60, (255, 240, 210), 0.5 * k, 14)
    L.camara()
    L.fundido_abajo(1560, 1720)
    sub(L, t, x_centro=360, ancho_max=600)
    return L


def cuadro(t, semilla=0):
    if t < T["pero"]:
        L = plano_clavo(t, semilla)
    elif t < T["con"]:
        L = plano_gigante(t, semilla)
    else:
        L = plano_pregunta(t, semilla)
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
    voz = MEZCLA if os.path.exists(MEZCLA) else voz_normalizada()
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
