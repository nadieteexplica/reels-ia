# -*- coding: utf-8 -*-
"""Ep. 17 — Dormir con tu pareja te da radiación (guion D v3). Laboratorio nocturno, kit_explica (vuelta 3).

Ritmo de la vuelta 3 (beat v5 aprobado): el cambio pasa DENTRO del plano; se corta sólo cuando cambia la idea;
sin barridos con texto; nada quieto > ~1 s. Subtítulos arriba; nada importante sobre y≈520 ni bajo 1580.

Uso:
  .venv/bin/python video.py salida.mp4                 render local con mezcla.wav (o la voz) — ESCALA=0.5 para borrador
  .venv/bin/python video.py --cuadros 0,1.5 carpeta/   cuadros sueltos
  .venv/bin/python video.py carpeta A B                (render-2d.yml) cuadros A..B (1-indexados) en PNG
"""
import json
import math
import os
import subprocess
import sys
import time
from multiprocessing import Pool

AQUI = os.path.dirname(os.path.abspath(__file__))
EP = os.path.dirname(AQUI)
RAIZ = os.path.abspath(os.path.join(EP, "..", "..", ".."))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(RAIZ, "studio", "plantilla"))
import kit_explica as K  # noqa: E402
import arte17 as A  # noqa: E402

WORDS = json.load(open(os.path.join(EP, "words.json")))
FPS = 30
DUR_VOZ = 41.3
DUR = round(DUR_VOZ + 0.6, 2)
FIN = int(round(DUR * FPS))
VOZ = os.path.join(RAIZ, "out/voz-libre/ep17-radiacion-pareja/ep17-radiacion-pareja.wav")
MEZCLA = os.path.join(EP, "mezcla.wav")
EST = A.EST
TINTA, ORO, VERDE = A.TINTA, A.ORO, A.VERDE
CLAVES = ["irradia", "central nuclear", "plátano", "potasio", "radiactiva", "también", "cuatro mil", "rayo gamma",
          "pareja", "Inofensivo", "un año de noches", "le gana", "plátano gigante", "tóxico", "tóxica"]
an, tr, ee, es, eo = K.anim, K.tramo, K.ease_entrada, K.ease_salida, K.ease_estado


def w(i):
    return WORDS[i]["s"]


# cortes (cambio de idea): balanza | cama+plátano | balanza (pila) | cama (plátano gigante) | balanza (loop)
C_CAMA, C_PILA, C_GIGANTE, C_LOOP = w(16), w(103), w(112), w(120)
CORTES = [0.0, C_CAMA, C_PILA, C_GIGANTE, C_LOOP, DUR]
_T = [0.0]


def empuje(t):
    """Respiración de cámara por escena (zoom que se frena a la mitad, paneo que se frena a 1/4 y 3/4): nunca quieto
    (qa.py marca congelado > 0,5 s) y empieza y termina en 1,0 (sin salto en cortes ni en el loop)."""
    for a, b in zip(CORTES, CORTES[1:]):
        if a <= t < b:
            break
    else:
        a, b = CORTES[-2], CORTES[-1]
    u = (t - a) / max(0.01, b - a)
    amp = min(0.035, 0.006 * (b - a))
    ciclos = max(1, round((b - a) / 6))           # un paneo cada ~6 s: nunca demasiado lento
    return 1.0 + amp * math.sin(math.pi * u), 14.0 * math.sin(2 * math.pi * ciclos * u)


class Lienzo(K.Lienzo):
    def camara(self, s=1.0, ancla=(0, 0), destino=None, temblor=(0, 0)):
        f, px = empuje(_T[0])
        b = destino if destino is not None else ancla
        c = (520, 1000)
        super().camara(s * f, ancla, ((b[0] - c[0]) * f + c[0] + px, (b[1] - c[1]) * f + c[1]), temblor)


def lienzo(sem):
    return Lienzo(EST, semilla=sem, fondo_img=K.fondo_estudio(EST))


def sub(L, t):
    K.subtitulos(L, WORDS, t, CLAVES)


def pild(L, s, cx, cy, t, t0, t1=None, tam=44):
    if t < t0:
        return
    p = ee(tr(t, t0, 0.3))
    a = min(1, p * 2) * (1 - es(tr(t, t1, 0.3)) if t1 is not None else 1)
    K.pildora_energia(L, s, cx, cy, tam, alpha=a, pop=0.8 + 0.2 * p)


def rotulo(L, x, y, s, tam=50, color=TINTA, alpha=1.0, anchor="ls"):
    K.texto(L, x, y, s, tam, color, "black", anchor=anchor, alpha=alpha, trazo=6)


def _pant(L, p):
    x, y = L.P(p[0], p[1], True)
    return (x / L.ss, y / L.ss)


# ================================================================================================== balanza
BX, BY = 500, 740
INC0 = 0.16                                      # cuadro 0: inclinada hacia la cama


def inclinacion(t):
    if t < C_CAMA:
        return INC0 + 0.06 * eo(tr(t, w(6), 0.35))
    if t < C_GIGANTE:                            # P7: llega la pila y baja más
        return 0.05 + 0.20 * K.ease_aterriza(tr(t, w(106) - 0.1, 0.7))
    return INC0 + 0.04 * math.sin((t - C_LOOP) * 2.4) * (1 - tr(t, DUR - 0.6, 0.6))


def plano_balanza(t, sem):
    L = lienzo(sem)
    L.camara()
    loop = t >= C_LOOP
    pila_p = 0.0
    if C_PILA <= t < C_GIGANTE:
        pila_p = ee(tr(t, w(104), 0.6))
    inc = inclinacion(t)
    brillo = 0.55 + 0.45 * eo(tr(t, w(6), 0.3)) if t < C_CAMA else 0.8
    if loop:
        brillo = 0.55 + 0.45 * (1 - eo(tr(t, DUR - 0.8, 0.6)))
    if t < C_CAMA:                                  # clic: la cama destella en 'irradia'
        e = t - w(6)
        if 0 <= e < 0.25:
            brillo = 1.0
    platos = A.balanza(L, BX, BY, inc, t=t, brillo_cama=brillo, pila=pila_p)
    (lx, ly), (rx, ry) = [_pant(L, p) for p in platos]
    if t < C_CAMA:
        K.brillo_golpe(L, lx, ly - 70, t - w(6), 160, 70, 5)
    L.camara()
    # HUD 1 AÑO sobre cada platillo (izquierdo desde el cuadro 0; derecho en el 2.º 'año')
    if t < C_CAMA or loop:
        pild(L, "1 AÑO", lx, ly - 330, t, -1)
        pild(L, "1 AÑO", rx, ry - 330, t, w(10) if not loop else -1, DUR - 0.55 if loop else None)
        if loop:                                   # la cola vuelve al cuadro 0
            K.pildora_energia(L, "TU CAMA > CENTRAL NUCLEAR", 500, 590, 46, alpha=ee(tr(t, DUR - 0.75, 0.35)))
            K.brillo_golpe(L, lx, ly - 70, t - w(123), 160, 70, 5)
    else:
        pild(L, "1 AÑO", lx, ly - 330, t, -1)
        pild(L, "1 AÑO", rx, ry - 330, t, -1)
        if t >= w(105):
            rotulo(L, lx - 110, ly + 120, "365 NOCHES", 46, alpha=ee(tr(t, w(105), 0.3)))
    # cuadro 0: el gancho se lee sin sonido (sale en el corte)
    if t < C_CAMA:
        K.pildora_energia(L, "TU CAMA > CENTRAL NUCLEAR", 500, 590, 46, alpha=1 - es(tr(t, C_CAMA - 0.3, 0.3)))
    # en 'central nuclear' la torre se marca con una guía
    if t < C_CAMA:
        K.etiqueta(L, "CENTRAL", (rx, ry - 120), (640, 1420), t, w(14), C_CAMA - 0.2, tam=50, lado="der")
    sub(L, t)
    return L


# ================================================================================================== cama desde arriba
CX, CY, CW, CH = 380, 1080, 520, 760
VX, VY = 820, 820                                # velador


def brillo_personas(t):
    """TÚ = la persona de la derecha (junto al velador); PAREJA = la de la izquierda (la que se vuelve plátano)."""
    tu = 0.0
    if t >= w(34):
        tu = 0.45 * eo(tr(t, w(34), 0.5)) + 0.55 * eo(tr(t, w(45), 0.4))
    pareja = 0.0
    if t >= w(83):
        pareja = 0.5 * eo(tr(t, w(83), 0.5))
    return pareja, tu


def plano_cama(t, sem):
    L = lienzo(sem)
    gigante = t >= C_GIGANTE
    # P4: empuje lento al cuerpo de la izquierda mientras se explica por dentro; P5 vuelve
    k = eo(tr(t, w(46), 0.9)) * (1 - eo(tr(t, w(70), 0.9)))
    cuerpo = (CX + CW * 0.24, CY - CH / 2 + 420)          # TÚ (derecha)
    L.camara(s=1.0 + 0.32 * k, ancla=cuerpo, destino=(cuerpo[0] + 120 * k, cuerpo[1] - 60 * k))
    izq, der = brillo_personas(t)
    if gigante:
        izq, der = 0.35, 1.0
    platano_g = ee(tr(t, w(118), 0.45)) if gigante else 0.0
    A.cama_arriba(L, CX, CY, CW, CH, t=t, brillo_izq=izq * (1 - platano_g), brillo_der=der, izq_platano=platano_g)
    # el velador y el plátano (cae en 'plátano'; se pela en 'comerte')
    if not gigante:
        A.velador(L, VX, VY)
        cae = ee(tr(t, w(23) - 0.15, 0.4))
        if t >= w(23) - 0.15:
            brillo_pl = eo(tr(t, w(31), 0.3))
            pel = eo(tr(t, w(93), 0.6))
            A.platano(L, VX, VY - 10 - 360 * (1 - cae), 190, ang=-18, brillo=brillo_pl * (1 - pel), pelado=pel,
                      alpha=min(1, cae * 2.5))
    # chispas: átomos que se desintegran dentro del cuerpo (desde 'desintegran')
    if w(55) <= t < C_PILA and not gigante:
        rng_t = int((t - w(55)) * 12)
        for j in range(7):
            sem_ = (rng_t * 7 + j) * 2654435761 % 1000
            u, v = (sem_ % 97) / 97, (sem_ // 97 % 89) / 89
            x = cuerpo[0] - 80 + 160 * u
            y = cuerpo[1] - 230 + 460 * v
            K.circulo(L, x, y, 6, capa="energia", alpha=0.9)
    # P4–P5: rayo gamma que sale del cuerpo y, en P5, cruza a la pareja
    if w(62) <= t < w(84) + 0.3:
        a_ = 1 - es(tr(t, w(84), 0.3))
        p_sale = ee(tr(t, w(62), 0.9))
        A.rayo(L, (cuerpo[0] - 10, cuerpo[1] - 40), (cuerpo[0] + 260, cuerpo[1] - 160), p_sale, 6, alpha=a_)
        punta_rayo = _pant(L, (cuerpo[0] + 150, cuerpo[1] - 110))
        if t >= w(78):
            otro = (CX - CW * 0.24, CY - CH / 2 + 380)
            for j, dy in enumerate((-90, 0, 90)):
                A.rayo(L, (cuerpo[0] - 40, cuerpo[1] + dy - 60), (otro[0] + 30, otro[1] + dy), ee(tr(t, w(78) + 0.12 * j, 0.6)),
                       5, alpha=a_)
    L.camara()
    # etiquetas (sin cámara)
    if not gigante:
        pl = (VX, VY - 10)
        if w(24) <= t < w(32) + 0.4:
            K.etiqueta(L, "POTASIO", (pl[0] - 40, pl[1] - 30), (560, 560), t, w(24), w(32), tam=50, lado="der")
        # la lupa: una pizca es radiactiva (1 de cada ~8.500)
        a_l = 0.0
        if w(26) <= t < w(32) + 0.3:
            a_l = ee(tr(t, w(26), 0.35)) * (1 - es(tr(t, w(32), 0.3)))
            A.lupa(L, 720, 1250, 140, t, w(31), alpha=a_l)
            if t >= w(31):
                rotulo(L, 720, 1490, "1 DE CADA ~8.500", 46, alpha=ee(tr(t, w(31), 0.3)) * a_l, anchor="ms")
        # P3: POTASIO también en tu cuerpo
        if w(37) <= t < w(46):
            pc = (CX + CW * 0.24, CY - CH / 2 + 300)
            K.etiqueta(L, "POTASIO", pc, (560, 640), t, w(37), w(46) - 0.3, tam=50, lado="der")
        # P4: unos 4 mil por segundo (número completo en 'cuatro mil')
        if w(48) <= t < w(59) + 0.4:
            a_n = 1 - es(tr(t, w(59), 0.35))
            K.numero_heroe(L, "~4.000", "", 480, 1360, 130, t, w(49), alpha=a_n)
            rotulo(L, 486, 1440, "POR SEGUNDO", 52, alpha=ee(tr(t, w(49) + 0.1, 0.3)) * a_n)
        if w(62) <= t < w(70):
            K.etiqueta(L, "RAYO GAMMA", punta_rayo, (560, 1180), t, w(62) + 0.2, w(70) - 0.3, tam=50, lado="der")
        # P6: cuánto — reloj de 8 h y 1 NOCHE ≈ 1 PLÁTANO; P6b inofensivo
        if w(84) <= t < w(97) + 0.3:
            a_h = ee(tr(t, w(84), 0.3)) * (1 - es(tr(t, w(97), 0.3)))
            horas = min(8, max(0, (t - w(84)) / 2.4 * 8))
            K.contador(L, horas, 700, 1080, 110, digitos=1, unidad=" H", capa="energia", alpha=a_h)
            rotulo(L, 704, 1140, "DURMIENDO", 44, alpha=a_h)
        if w(95) <= t < w(97) + 0.3:
            pild(L, "1 NOCHE ≈ 1 PLÁTANO", 480, 600, t, w(95), w(97), tam=46)
        if w(96) <= t < C_PILA:
            a_c = 1 - es(tr(t, w(97) + 0.5, 0.3))
            A.check(L, 210, 1530, 110, tr(t, w(96), 0.3), alpha=a_c)
            rotulo(L, 280, 1556, "INOFENSIVO", 60, alpha=ee(tr(t, w(96), 0.3)) * a_c)
        # P7a: un año de noches — las cáscaras se apilan junto a la cama + contador de noches
        if w(98) <= t < C_PILA:
            n = int(min(365, max(1, (t - w(98)) / (w(102) + 0.3 - w(98)) * 365)))
            K.contador(L, n, 700, 1080, 110, digitos=3, capa="energia")
            rotulo(L, 704, 1140, "NOCHES", 44)
            k_p = tr(t, w(98), C_PILA - w(98))
            for j in range(int(3 + 16 * k_p)):
                A.platano(L, 700 + (j * 37) % 200, 1440 - (j // 6) * 26, 110, ang=(j * 53) % 160 - 80, pelado=1.0,
                          sombra=False)
    sub(L, t)
    return L


# ================================================================================================== montaje
def cuadro(t, semilla=0):
    _T[0] = t
    if t < C_CAMA or C_PILA <= t < C_GIGANTE or t >= C_LOOP:
        L = plano_balanza(t, semilla)
    else:
        L = plano_cama(t, semilla)
    return L.salida()


ESCALA = float(os.environ.get("ESCALA", "1.0"))


def _trabajo(i):
    im = cuadro(i / FPS, i)
    if ESCALA != 1.0:
        im = im.resize((int(1080 * ESCALA), int(1920 * ESCALA)))
    return im.tobytes()


def render(salida):
    t0 = time.time()
    wv, hv = int(1080 * ESCALA), int(1920 * ESCALA)
    audio = MEZCLA if os.path.exists(MEZCLA) else VOZ
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{wv}x{hv}",
           "-r", str(FPS), "-i", "-", "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium",
           "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart",
           "-t", f"{DUR:.2f}", salida]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(int(os.environ.get("PROCESOS", "7"))) as pool:
        for k, b in enumerate(pool.imap(_trabajo, range(FIN), chunksize=3)):
            ff.stdin.write(b)
    ff.stdin.close()
    ff.wait()
    print(f"listo: {salida}  {FIN} cuadros, render {time.time() - t0:.0f}s")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--cuadros":
        os.makedirs(sys.argv[3], exist_ok=True)
        for s in sys.argv[2].split(","):
            tt = float(s)
            cuadro(tt, int(tt * FPS)).save(os.path.join(sys.argv[3], f"t{tt:05.2f}.png"))
    elif len(sys.argv) == 4 and sys.argv[2].isdigit():
        out, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
        os.makedirs(out, exist_ok=True)
        for i in range(a, b + 1):
            cuadro((i - 1) / FPS, i - 1).save(os.path.join(out, f"{i:05d}.png"))
    else:
        render(sys.argv[1])
