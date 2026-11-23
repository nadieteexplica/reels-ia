# -*- coding: utf-8 -*-
"""Duelo visual (23-nov-2026), motor Python: el beat del clavo con kit_explica (estilo laboratorio nocturno).

Uso:  .venv/bin/python studio/duelo-visual/python/render.py [salida.mp4]
      .venv/bin/python studio/duelo-visual/python/render.py --cuadros 0,1.5,3 carpeta/   (sólo PNG de prueba)
Todo es función del tiempo t (segundos). Los cuadros se dibujan en paralelo y van directo a ffmpeg.
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
DUR = DUR_VOZ + 0.5                       # cola de 0,5 s
NF = int(round(DUR * FPS))
EST = K.ESTILOS["laboratorio_nocturno"]
CLAVES = SB["palabras_clave_con_recuadro"]
SALIDA = "/private/tmp/claude-501/-Users-tomas-Desktop-Proyecto/d4cb7467-771f-4533-993e-f4f18f1ccbe0/scratchpad/duelo/python.mp4"


def t_palabra(txt, vez=1):
    """Inicio de la palabra (la n-ésima vez que aparece) en words.json."""
    k = 0
    for w in WORDS:
        if K._norm(w["w"]) == K._norm(txt):
            k += 1
            if k == vez:
                return w["s"]
    raise KeyError(txt)


T = dict(clavo=t_palabra("clavo"), un=t_palabra("un", 2), martillazo=t_palabra("martillazo"),
         entra=t_palabra("entra"), pero=t_palabra("pero"), clavo2=t_palabra("clavo", 2),
         veinte=t_palabra("veinte"), cincuenta=t_palabra("cincuenta"), con=t_palabra("con"),
         pegas=t_palabra("pegas"))

# ------------------------------------------------------------------ plano 1–2: clavo chico sobre el tablón
CX = 500                     # eje del clavo (centro de la zona segura: 60..920)
N1 = 600                     # largo del clavo chico (≈31 % del alto)
G1 = K.geometria_clavo(N1)
Y_ENTRA = 1055               # punto de la cara de arriba del tablón donde apoya la punta
Y_CAB = Y_ENTRA - N1         # tope de la cabeza al inicio
Y_CAB_FIN = Y_ENTRA - G1["cabeza"]
H1 = 400                     # largo del mango del martillo
CARA = 0.287                 # la cara del martillo, en unidades de H, desde el centro de la cabeza
PIVOTE = (CX + 0.86 * H1, Y_CAB - CARA * H1)   # la muñeca: el martillo gira alrededor de este punto
ANG_ARRIBA = 27.0
P_PICO, Y_PICO = K.pico_aterriza()
P_TOQUE = next(i / 2000 for i in range(2001) if K.ease_aterriza(i / 2000) >= 1.0)   # primer contacto
D_GOLPE = 0.34
T_GOLPE0 = T["martillazo"] - P_TOQUE * D_GOLPE  # el contacto cae justo en "martillazo"
REBOTE = 3.5                                    # grados que rebota el martillo (lo que la curva pasa de 1)
D_HUNDE = 0.45

# ------------------------------------------------------------------ plano 3–4: clavo gigante
Y_SUELO = 1290
N2 = 1040
Y_CAB2 = 330
G2 = K.geometria_clavo(N2)
X_PERSONA = 655
ALTO_PERSONA = 88            # ≈ 1/11 del clavo visible
X_COTA = 368
H2 = 62                      # martillo chico (mismo dibujo)
MART2_FIN = (700, 408)


def _rot(px, py, ang, dx, dy):
    a = math.radians(ang)
    return (px + dx * math.cos(a) - dy * math.sin(a), py + dx * math.sin(a) + dy * math.cos(a))


def angulo_martillo(t):
    """Ángulo del martillo grande: respira arriba, anticipa, golpea con rebote y vuelve arriba en 'entra'."""
    if t < T_GOLPE0:
        ant = K.anim(t, T_GOLPE0 - 0.28, 0.28, K.ease_estado)       # anticipación: sube 4°
        return ANG_ARRIBA + 4 * ant
    if t < T["entra"]:
        a0 = ANG_ARRIBA + 4
        p = K.tramo(t, T_GOLPE0, D_GOLPE)
        y = K.ease_aterriza(p)
        if p < P_TOQUE:
            return a0 * (1 - y)                         # baja hasta tocar la cabeza
        return REBOTE * (y - 1) / (Y_PICO - 1)          # lo que la curva pasa de 1 = rebote hacia arriba
    return ANG_ARRIBA * K.anim(t, T["entra"] + 0.05, 0.55, K.ease_estado)


def respiro(t):
    """El martillo respira apenas (sube 6 px) antes del golpe; vuelve a 0 para el loop."""
    if t >= T_GOLPE0 - 0.28:
        return 0.0
    return -6 * math.sin(math.pi * min(1.0, t / (T_GOLPE0 - 0.28))) ** 2


def escena_chica(L, t):
    e_imp = t - T["martillazo"]
    tx = ty = 0.0
    if 0 <= e_imp < 0.22:                     # temblor corto del golpe
        amp = 6 * math.exp(-e_imp * 16)
        tx, ty = amp * math.sin(e_imp * 95), amp * 0.8 * math.cos(e_imp * 77)
    L.camara(temblor=(tx, ty))
    K.tabla(L, 110, 890, Y_ENTRA + 25, 420, prof=50)
    p_h = K.anim(t, T["entra"], D_HUNDE, K.ease_estado)
    y0 = Y_CAB + p_h * (Y_CAB_FIN - Y_CAB)
    # sombra de contacto (corta, hacia la derecha) y agujero
    K.poligono(L, K.elipse_pts(CX + 7, Y_ENTRA + 2, G1["sw"] * 0.95, 5), (40, 22, 10), alpha=0.55)
    if p_h > 0:
        K.poligono(L, K.elipse_pts(CX + 6, Y_ENTRA + 3, G1["D"] * 0.56 * p_h + G1["sw"] * 0.6, G1["ry"] * 0.9),
                   (40, 22, 10), alpha=0.5 * p_h)
    K.clavo(L, CX, y0, N1, recorte=Y_ENTRA)
    K.polvo(L, CX, Y_ENTRA, t - T["entra"] - 0.08)
    # martillo
    ang = angulo_martillo(t)
    hx, hy = _rot(PIVOTE[0], PIVOTE[1], ang, -0.86 * H1, 0)
    K.martillo(L, hx, hy + respiro(t), H1, ang)
    K.destello(L, CX, Y_CAB + 4, e_imp + 0.5 / FPS)    # medio cuadro de adelanto: el destello cae en el cuadro del golpe
    if 0 <= e_imp < 0.3:
        L.brillo = 1.0 + 1.4 * math.exp(-e_imp * 10)
    L.camara()
    # etiquetas (fijas en pantalla: no tiemblan mientras se leen)
    K.etiqueta(L, "CLAVO · 8 CM", (CX - G1["D"] / 2 + 7, y0 + G1["ry"] + 4), (66, 330), t, T["clavo"],
               t1=T["entra"] - 0.15, tam=50)
    K.etiqueta(L, None, (CX - G1["D"] / 2 - 22, Y_ENTRA + 8), (66, 842), t, T["entra"], tam=50,
               caption="QUEDA AFUERA", numero=dict(valor=8 * (1 - p_h), digitos=1, unidad=" CM"),
               dur=0.55, texto_desde=0.0)
    L.fundido_abajo(1335, 1440)


def escena_gigante(L, t):
    s = 1.0 + 1.05 * (1 - K.anim(t, T["pero"] + 0.08, 0.84, K.ease_estado))   # corte cerrado; la cámara se abre y revela la escala
    L.camara(s=s, ancla=(560, Y_SUELO))
    K.suelo(L, Y_SUELO)
    # grietas en la tierra alrededor de la punta
    for dx, dy, l, a in ((-1, 40, 60, 200), (1, 50, 70, -20), (-1, 75, 46, 160), (1, 82, 40, 25)):
        x0 = CX + dx * G2["sw"] * 0.4
        y0 = Y_SUELO + dy
        pts = [(x0, y0), (x0 + l * 0.5 * math.cos(math.radians(a)), y0 + l * 0.5 * math.sin(math.radians(a)) + 6),
               (x0 + l * math.cos(math.radians(a)), y0 + l * math.sin(math.radians(a)))]
        K.linea(L, pts, (40, 28, 20), 3, alpha=0.8)
    K.clavo(L, CX, Y_CAB2, N2)
    # tierra levantada en la base
    sw = G2["sw"]
    for lado in (-1, 1):
        xb = CX + lado * sw / 2
        K.poligono(L, [(xb - lado * 3, Y_SUELO + 2), (xb + lado * 4, Y_SUELO - 9), (xb + lado * 16, Y_SUELO - 12),
                       (xb + lado * 34, Y_SUELO - 4), (xb + lado * 48, Y_SUELO + 2)], (104, 76, 52))
        K.linea(L, [(xb + lado * 4, Y_SUELO - 9), (xb + lado * 16, Y_SUELO - 12), (xb + lado * 34, Y_SUELO - 4)],
                (156, 122, 88), 2.2)
    K.persona(L, X_PERSONA, Y_SUELO, ALTO_PERSONA)
    L.camara()
    a_out = 1 - K.ease_salida(K.tramo(t, T["con"], 0.4))
    # cota 0 → 20 M
    if t >= T["veinte"] and a_out > 0:
        p = K.anim(t, T["veinte"], 1.0, K.ease_entrada)
        K.cota_vertical(L, X_COTA, Y_SUELO, Y_CAB2, p, alpha=a_out)
        a_ext = K.anim(t, T["veinte"] + 0.55, 0.4) * a_out
        K.linea_punteada(L, (X_COTA + 30, Y_CAB2), (CX - G2["D"] / 2 - 8, Y_CAB2), K.rgb(EST["tinta"]), 3, alpha=0.6 * a_ext)
        K.linea_punteada(L, (X_COTA + 30, Y_SUELO), (CX - sw / 2 - 40, Y_SUELO), K.rgb(EST["tinta"]), 3,
                         alpha=0.6 * K.anim(t, T["veinte"], 0.3) * a_out)
        a_txt = K.anim(t, T["veinte"], 0.35) * a_out
        ym = (Y_SUELO + Y_CAB2) / 2
        K.texto(L, X_COTA - 34, ym - 76, "ALTO", 36, K.rgb(EST["gris"]), "xbold", anchor="rs", alpha=a_txt)
        K.contador(L, 20 * p, X_COTA - 34, ym + 30, 92, digitos=2, unidad=" M", alin="der", alpha=a_txt)
    # contador 0 → 50 T junto a la caña
    if a_out > 0:
        p50 = K.anim(t, T["cincuenta"] + 0.05, 1.0, K.ease_entrada)
        K.etiqueta(L, None, (CX + sw / 2 - 2, 905), (630, 770), t, T["cincuenta"], t1=T["con"], tam=50, lado="der",
                   caption="PESO", numero=dict(valor=50 * p50, digitos=2, unidad=" T"), dur=0.6, texto_desde=0.0)
    # el martillo de siempre entra desde la derecha, ridículamente chico
    if t >= T["con"]:
        p = K.anim(t, T["con"], 0.85, K.ease_entrada)
        x = 1230 + (MART2_FIN[0] - 1230) * p
        y = 250 + (MART2_FIN[1] - 250) * p + 3 * math.sin((t - T["con"]) * 4.2) * p
        ang = 40 + 230 * (1 - p) + 4 * math.sin((t - T["con"]) * 3.1) * p
        K.martillo(L, x, y, H2, ang, sombra=False)
        a_r = K.anim(t, T["con"] + 0.45, 0.5)
        if a_r > 0:
            cxr, cyr = _rot(x, y, ang, 0.42 * H2, 0)
            pts = K.elipse_pts(cxr, cyr, 54 + 14 * (1 - a_r), 54 + 14 * (1 - a_r), n=44)
            for i in range(0, 44, 2):
                K.linea(L, pts[i:i + 2], K.rgb(EST["tinta"]), 3, alpha=0.75 * a_r)
    # el signo de pregunta en "pegas"
    if t >= T["pegas"]:
        p = K.anim(t, T["pegas"], 0.55, K.ease_entrada)
        tam = 300 * (0.6 + 0.4 * p)
        K.texto(L, CX, Y_CAB2 - 34 - (1 - p) * 20, "?", tam, anchor="ms", capa="energia", alpha=min(1, p * 1.6))
    L.fundido_abajo(1385, 1500)


def cuadro(t, semilla):
    gig = t >= T["pero"]
    L = K.Lienzo(EST, semilla=semilla, luz=(0.46, 0.42) if gig else (0.46, 0.37))
    (escena_gigante if gig else escena_chica)(L, t)
    K.subtitulos(L, WORDS, t, CLAVES)
    return L.salida()


def _trabajo(i):
    return cuadro(i / FPS, i).tobytes()


def render(salida):
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    t0 = time.time()
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920",
           "-r", str(FPS), "-i", "-", "-i", VOZ, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium",
           "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", salida]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(6) as pool:
        for k, b in enumerate(pool.imap(_trabajo, range(NF), chunksize=2)):
            ff.stdin.write(b)
            if k % 30 == 0:
                print(f"cuadro {k}/{NF}  {time.time() - t0:.1f}s", flush=True)
    ff.stdin.close()
    ff.wait()
    print(f"listo: {salida}  {NF} cuadros, {DUR:.2f}s de video, render {time.time() - t0:.1f}s")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--cuadros":
        os.makedirs(sys.argv[3], exist_ok=True)
        for s in sys.argv[2].split(","):
            tt = float(s)
            cuadro(tt, int(tt * FPS)).save(os.path.join(sys.argv[3], f"t{tt:05.2f}.png"))
    else:
        render(sys.argv[1] if len(sys.argv) > 1 else SALIDA)
