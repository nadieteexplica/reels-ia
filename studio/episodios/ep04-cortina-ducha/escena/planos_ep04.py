"""Planos del Ep. 4 (proceso v2): 3 escenas, 21 planos (storyboard.md).

E1 ducha     — Don Héctor bajo la ducha; la cortina liviana se le viene encima, se da vuelta y la cortina se le pega
               en la cara (desde afuera: una cara de fantasma marcada en la cortina). Planos 1–5 y 16 (repite el golpe).
E2 corte     — la ducha por dentro, sin personaje: chorro caliente/frío, vapor, el remolino acostado que gira como
               rueda, su centro de baja presión y la cortina que se mete. Planos 6–15 y 19 (con la cortina pesada).
E3 pesada    — la cortina pesada baja, casi no se mueve, él se relaja... y se infla con una cara de fantasma desde
               afuera. Planos 17, 18, 20 y 21 (termina en el encuadre del cuadro 0: loop).

Cada pieza arma su escena y devuelve actualizar(f) (pose calculada, sin keyframes). La actuación de cada escena es una
sola función del tiempo de la escena; los planos sólo cambian la cámara (o, en el 16, el tramo de E1 que se repite).
"""
import math, os, sys
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../plantilla")))
import ep04 as E
import bano as B
import personaje as PJ
from ep04 import FR, F, lin, suave, sale, entra, rebote, resorte, tramo, ruido, clamp

FPS = 30


def T0(k):
    return E.T[k][0]


def TW(prefijo, desde=0.0):
    return E.t_palabra(prefijo, desde)


# ===================================== E1 · la ducha ======================================
def _set_ducha(sc, pesada=False):
    sc.view_settings.exposure = -1.0          # piel mojada, espuma y cortina claras: sin quemar ni lavar (chequeos)
    S = B.armar(sc, corte=False, cortina="pesada" if pesada else "liviana", pato_en=(0.45, 0.365, B.Z_BORDE))
    pj = PJ.cargar(sc, x=0.0, y=0.10, z=B.Z_PISO, rot_z=math.pi)
    A = B.sistema_agua(n_gotas=700, n_aire=1, n_vapor=30)
    return S, pj, A


def _luz_rasante(sc, S):
    """Afuera de la cortina: luz que pasa rasante por la tela para que se lea el relieve (la cara de fantasma)."""
    S["luces"]["relleno"].data.energy = 45
    S["luces"]["techo"].data.energy = 70
    L = bpy.data.lights.new("Rasante", "AREA")
    L.energy, L.size, L.color = 260, 0.35, (1.0, 0.92, 0.82)
    o = bpy.data.objects.new("Rasante", L)
    sc.collection.objects.link(o)
    o.location = (0.10, -0.62, 2.30)
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = (Vector((0.0, -0.2, 1.62)) - o.location).to_track_quat("-Z", "Y")


def _quitar(*obs):
    """Saca una pared del render y de la escena evaluada (los rayos del chequeo de ojos tampoco la ven)."""
    for o in obs:
        o.hide_render = True
        o.hide_viewport = True


def _objetivos(pj):
    return [pj["cuerpo"]] + [o for o in pj["extras"] if o.name in ("Espuma", "Bigote")]


# tiempos de E1 (s, tiempo de la escena = tiempo del video en los planos 1–5)
E1_TOQUE = TW("cortina") + 0.05     # la cortina le toca la espalda (≈1,71)
E1_GIRO = (2.60, 2.95)              # se da vuelta para mirarla
E1_PEGA = 3.30                      # se le pega en la cara
E1_SUELTA = TW("no") + 0.05        # "No.": la cortina se suelta


def act_e1(S, pj, A, t, f, fastidio=False, afuera=False):
    """Actuación de E1 en el tiempo de escena t."""
    rig = pj["rig"]
    # giro del cuerpo (se da vuelta hacia la cortina)
    g = suave(lin(t, E1_GIRO[0] * FPS, E1_GIRO[1] * FPS)) if False else suave(clamp((t - E1_GIRO[0]) / (E1_GIRO[1] - E1_GIRO[0])))
    rig.rotation_euler = (0, 0, math.pi * (1 - g))
    # expresión
    tranquilo = 1 - clamp((t - E1_TOQUE + 0.05) / 0.12)
    choque = resorte(t - E1_TOQUE, frec=2.6, amort=5.0) if t > E1_TOQUE else 0.0
    expr = {"alivio": tranquilo, "susto": (1 - tranquilo)}
    if t > E1_SUELTA:
        r = clamp((t - E1_SUELTA) / 0.25)
        expr = {"susto": 1 - r, "duda": r}
    if fastidio and t > E1_TOQUE:
        expr = {"asco": 1 - tranquilo, "susto": 0.4}
    cab_x = -12 * tranquilo + 6 * (1 - tranquilo) + 2 * math.sin(t * 2.1)     # mira hacia el chorro (arriba) y luego se echa atrás
    cab_y = 4 * math.sin(t * 1.3) * tranquilo
    hombros = min(1.0, choque * 1.1)
    torso_x = -6 * clamp(choque) * (1 if t < E1_GIRO[0] else 0.3)
    parp = PJ.parpadeo(f) if tranquilo < 0.5 and t < E1_PEGA else 0.0
    # tarareo con la boca mientras está tranquilo (algo cambia en la cara)
    if tranquilo > 0.5:
        expr["sonrisa"] = 0.35 + 0.25 * max(0.0, math.sin(t * 9))
    pega_c = suave(clamp((t - E1_GIRO[1]) / 0.3)) * (1 - suave(clamp((t - E1_SUELTA) / 0.4)))
    PJ.pose(pj, f, expr=expr, cabeza=(cab_x + 10 * pega_c, cab_y, 3 * math.sin(t * 0.9)), cuello=(6 * pega_c, 0, 0),
            torso=(torso_x + 10 * pega_c, 0, 0), hombros=hombros, parpadeo=parp)
    # cortina: ya viene en camino en el cuadro 0, le toca la espalda, después se le pega en la cara y se suelta
    if t < E1_GIRO[0]:
        inf = 0.36 + 0.14 * sale(clamp(t / E1_TOQUE))
        centro, radio = (0.18, 1.42), (0.42, 0.48)
    elif t < E1_SUELTA:
        x = sale(clamp((t - E1_GIRO[0]) / (E1_PEGA - E1_GIRO[0])))
        inf = 0.48 + 0.20 * x
        centro, radio = (0.06 - 0.06 * x, 1.40 + 0.25 * x), (0.50, 0.50)
    else:
        x = suave(clamp((t - E1_SUELTA) / 0.5))
        inf = 0.68 - 0.40 * x
        centro, radio = (0.0, 1.65 - 0.3 * x), (0.50, 0.50)
    bpy.context.view_layer.update()
    if t < E1_GIRO[0]:      # le toca la espalda: la cortina se apoya en él (rayos), no lo atraviesa
        B.deformar_cortina(S["cortina"], f, inflar=inf, centro=centro, radio=radio, aleteo=1.0, objetivos=_objetivos(pj))
    else:                   # se le pega en la cara: la cara se marca en la cortina (relieve hacia afuera)
        pega = suave(clamp((t - E1_GIRO[1]) / (E1_PEGA - E1_GIRO[1]))) * (1 - suave(clamp((t - E1_SUELTA) / 0.45)))
        B.deformar_cortina(S["cortina"], f, inflar=inf, centro=centro, radio=radio, aleteo=1.0 - 0.6 * pega,
                           cara=(0.0, 1.70), empuje_cara=0.11 * pega, cara_dentro=True, tope_y=-0.07)
    # patito: se cae del borde con el golpe
    pato = S["pato"]
    tc = t - (E1_TOQUE + 0.18)
    if tc > 0:
        caida = min(1.0, tc / 0.32)
        z = B.Z_BORDE - (B.Z_BORDE - B.Z_PISO) * caida ** 2
        if tc > 0.32:
            z = B.Z_PISO + 0.06 * abs(math.sin((tc - 0.32) * 12)) * math.exp(-(tc - 0.32) * 6)
        pato.location = (0.45 - 0.05 * caida, 0.365 - 0.16 * caida, z)
        pato.rotation_euler = (math.radians(95 * min(1.0, tc / 0.3)), 0.0, math.radians(180 + 25 * caida))
    else:
        pato.location = (0.45, 0.365, B.Z_BORDE)
        pato.rotation_euler = (0, 0, math.radians(180 + 10 * math.sin(t * 3)))
    B.gotas(A, t, caliente=0.15, densidad=0.25 if afuera else 1.0)
    B.vapor(A, t, caliente=0.0 if afuera else 0.5)


def _e1(sc, a, b, plano):
    S, pj, A = _set_ducha(sc)
    cam = E.camara(sc, lens=38)
    fondo, der = S["paredes"][0], S["paredes"][2]
    # las paredes que quedan entre la cámara y el personaje se sacan del render (hide_render: así tampoco tapan
    # los rayos del chequeo de ojos, que no respetan visible_camera)
    if plano in (1, 3):
        _quitar(fondo)                        # cámara "dentro" de la pared del fondo: mira la cara
    if plano in (2, 16):
        _quitar(der)                          # cámara en la punta de la tina: de perfil
    if plano in (4, 5):
        _luz_rasante(sc, S)
        sc.view_settings.exposure = -1.65     # afuera: la cortina clara llena el cuadro
    k0 = T0(plano)

    def act(f):
        t = (f - 1) / FPS
        tl = t
        if plano == 16:                       # el mismo golpe de E1, ahora "hacia ti"
            tl = min((t - T0(16)) + (E1_TOQUE - 0.9), E1_GIRO[0] - 0.05)     # no entra al giro de E1
        act_e1(S, pj, A, tl, f, fastidio=(plano == 16), afuera=plano in (4, 5))
        x = lin(f, a, b)
        if plano == 1:       # C0: la cara (tranquilo) y la cortina que se le viene por detrás
            E.empujar(cam, f, a, b, (0.66, 1.32, 1.86), (0.02, -0.04, 1.60), cuanto=0.08, lens=34)
        elif plano == 3:     # se da vuelta
            E.empujar(cam, f, a, b, (0.22, 1.25, 1.82), (0.0, 0.05, 1.64), cuanto=0.06, lens=38)
        elif plano in (2, 16):   # perfil desde la punta de la tina: la cortina le pega en la espalda, cae el patito
            E.empujar(cam, f, a, b, (1.95, -0.62, 1.78), (0.0, -0.12, 1.52), cuanto=0.07, lens=34)
        elif plano == 4:     # afuera: la cara de fantasma en la cortina
            E.empujar(cam, f, a, b, (0.10, -2.15, 1.60), (0.0, -0.35, 1.52), cuanto=0.10, lens=42)
        elif plano == 5:     # afuera, más cerca: la cara se suelta
            E.empujar(cam, f, a, b, (0.06, -1.45, 1.64), (0.0, -0.30, 1.58), cuanto=0.05, lens=46)
        bpy.context.view_layer.update()
        return {}
    return {"actualizar": act}


# ===================================== E2 · la ducha por dentro (corte) ======================================
CENTRO = (-0.20, 1.22)          # centro del remolino (x, z): su eje va de la pared a la cortina (y)


def _set_corte(sc, pesada=False):
    sc.view_settings.exposure = -1.55         # la tina blanca y los azulejos claros: sin lavar (chequeo de la puerta 4)
    S = B.armar(sc, corte=True, cortina="pesada" if pesada else "liviana")
    A = B.sistema_agua(n_gotas=900, n_aire=700, n_vapor=40)
    # brillo del centro (baja presión): esfera cian que aparece en el plano 13
    m = B.mat("CentroBaja", (0.25, 0.85, 1.0), rough=1.0, emis=4.0, alpha=0.0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(CENTRO[0], -0.03, CENTRO[1]), segments=32, ring_count=16)
    c = bpy.context.active_object
    c.name = "CentroBaja"
    c.scale = (1, 4.0, 1)                 # el ojo del remolino: un tubo de la pared a la cortina
    c.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return S, A, c


def act_e2(S, A, c, t, f, pesada=False):
    """Actuación de E2 en el tiempo del video (5,40–24,39; el plano 19 la repite con la cortina pesada)."""
    caliente = 1.0 - suave(clamp((t - TW("pasa", 9.8)) / 0.6))           # al "pasa hasta con agua fría" se pone azul
    if pesada:
        caliente = 0.0
    B.gotas(A, t, caliente=caliente)
    B.vapor(A, t, caliente=caliente)
    # el remolino: se ve desde "arrastra" y se arma en "arma un remolino"
    t_arr, t_arma = TW("arrastra"), TW("arma")
    if pesada:
        vis, fuerza = 1.0, 1.0
    else:
        vis = 0.18 * suave(clamp((t - t_arr) / 0.8)) + 0.82 * suave(clamp((t - t_arma) / 1.2))
        fuerza = 0.35 * suave(clamp((t - t_arr) / 0.8)) + 0.65 * suave(clamp((t - t_arma) / 1.0))
    if t < t_arr - 0.05 and not pesada:
        vis = 0.0
    B.remolino(A, t, fuerza=max(fuerza, 0.05), centro=CENTRO, visible=vis, rmax=0.32)
    # brillo del centro (baja presión)
    t_c = TW("centro")
    a_c = 0.0 if pesada else suave(clamp((t - t_c) / 0.5)) * (1 - suave(clamp((t - TW("y", 22.0)) / 0.6)) * 0.6)
    m = c.data.materials[0]
    B._bsdf(m).inputs["Alpha"].default_value = 0.45 * a_c * (0.85 + 0.15 * math.sin(t * 6))
    c.hide_render = a_c < 0.01
    # cortina: se mete hacia el remolino (más con agua caliente; con la pesada casi nada)
    if pesada:
        inf = 0.035
    else:
        base = 0.17 + 0.06 * caliente
        empuje = 0.09 * suave(clamp((t - TW("empuja")) / 0.6))
        inf = base + empuje
    B.deformar_cortina(S["cortina"], f, inflar=inf, centro=CENTRO, radio=(0.36, 0.36), aleteo=0.6 if not pesada else 0.3)


def _alpha_cortina(S, valor):
    m = bpy.data.materials[S["cortina"]["ob"]["mat_alpha"]]
    B._bsdf(m).inputs["Alpha"].default_value = valor


def _e2(sc, a, b, plano):
    pesada = plano == 19
    S, A, c = _set_corte(sc, pesada=pesada)
    cam = E.camara(sc, lens=30)
    xc, zc = CENTRO
    # cámaras: 3/4 desde afuera por la punta abierta (caliente/frío, el empuje) y de frente a través de la cortina
    TRES4 = (Vector((2.0, -1.95, 1.70)), Vector((-0.15, -0.10, 1.05)))
    FRENTE = (Vector((xc + 0.05, -2.30, 0.98)), Vector((xc + 0.05, 0.0, 0.95)))
    FRENTE_C = (Vector((xc, -1.60, 1.00)), Vector((xc, 0.0, 0.98)))
    CHORRO = (Vector((0.10, -1.85, 1.30)), Vector((0.05, 0.10, 1.22)))
    EMPUJE = (Vector((1.45, -2.05, 1.20)), Vector((xc, -0.35, 1.02)))

    def act(f):
        t = (f - 1) / FPS
        tt = t if not pesada else (TW("remolino", 16.0) + (t - T0(19)))
        act_e2(S, A, c, tt, f, pesada=pesada)
        x = lin(f, a, b)
        alfa = 1.0
        if plano in (6, 8):
            E.empujar(cam, f, a, b, *TRES4, cuanto=0.07, lens=30)
        elif plano == 7:
            E.empujar(cam, f, a, b, Vector((1.75, 0.02, 1.62)), Vector((0.0, 0.14, 1.40)), cuanto=0.08, lens=32)
        elif plano == 9:     # "Mira la ducha por dentro": la cámara pasa al frente y la cortina se vuelve transparente
            u = suave(x)
            E.mirar(cam, TRES4[0].lerp(FRENTE[0], u), TRES4[1].lerp(FRENTE[1], u), lens=30)
            alfa = 1.0 - 0.90 * suave(clamp((x - 0.35) / 0.5))
        elif plano == 10:
            E.empujar(cam, f, a, b, *CHORRO, cuanto=0.08, lens=34)
            alfa = 0.10
        elif plano in (11, 12, 15):
            E.empujar(cam, f, a, b, *FRENTE, cuanto={11: 0.06, 12: 0.10, 15: 0.08}[plano], lens=30)
            alfa = 0.30 if plano == 15 else 0.10      # en el 15 se ven las franjas doblándose hacia el ojo
        elif plano in (13, 14):
            E.empujar(cam, f, a, b, *FRENTE_C, cuanto=0.10, lens=32)
            alfa = 0.10
        elif plano == 19:    # la cortina pesada se ve por delante: el remolino gira detrás y ella casi no se mueve
            E.empujar(cam, f, a, b, *FRENTE, cuanto=0.06, lens=30)
            alfa = 0.40
        _alpha_cortina(S, alfa)
        bpy.context.view_layer.update()
        rp = E.pantalla(sc, cam, (xc, -0.40, zc))
        info = {"centro": E.pantalla(sc, cam, (xc, -0.05, zc)),
                "chorro": E.pantalla(sc, cam, (0.05, 0.12, 1.45)),
                "cortina": E.pantalla(sc, cam, (xc, B.Y_CORT + 0.12, zc - 0.10)),
                "cortina_alta": E.pantalla(sc, cam, (xc, B.Y_CORT + 0.12, zc + 0.12)),
                "afuera": E.pantalla(sc, cam, (xc + 0.05, B.Y_CORT - 0.55, zc - 0.12)),
                "afuera_alta": E.pantalla(sc, cam, (xc + 0.05, B.Y_CORT - 0.55, zc + 0.14)),
                "radio_px": abs(E.pantalla(sc, cam, (xc, -0.05, zc + 0.32))[1] - E.pantalla(sc, cam, (xc, -0.05, zc))[1])}
        return info
    return {"actualizar": act}


# ===================================== E3 · la cortina pesada ======================================
E3_BAJA = (26.45, 27.35)        # la cortina pesada baja (se desenrolla) en "¿La solución?"
E3_INFLA = 32.15                # "igual se mueve": empieza a inflarse
E3_FANT = 33.95                 # "ahí sí es un fantasma": cara del fantasma y susto


def act_e3(S, pj, A, t, f):
    rig = pj["rig"]
    rig.rotation_euler = (0, 0, math.pi)       # mira la ducha (la cámara C0)
    susto = suave(clamp((t - (E3_FANT + 0.25)) / 0.18))
    tranquilo = 1 - susto
    expr = {"alivio": tranquilo, "susto": susto}
    if tranquilo > 0.5:
        expr["sonrisa"] = 0.45 + 0.3 * max(0.0, math.sin(t * 8))
    sospecha = suave(clamp((t - (E3_INFLA + 0.9)) / 0.4)) * tranquilo
    if sospecha > 0:
        expr["duda"] = sospecha
        expr["alivio"] = tranquilo * (1 - sospecha)
    hombros = min(1.0, resorte(t - (E3_FANT + 0.25), frec=2.6, amort=5.0)) if t > E3_FANT + 0.25 else 0.0
    cab_x = -10 * tranquilo - 9 * susto + 1.5 * math.sin(t * 2.0)
    cab_y = 12 * sospecha * (1 - susto) + 3 * math.sin(t * 1.1) * tranquilo
    PJ.pose(pj, f, expr=expr, cabeza=(cab_x, cab_y, 2 * math.sin(t * 0.8)), torso=(-5 * susto, 0, 0), hombros=hombros,
            parpadeo=PJ.parpadeo(f, fase=11) if susto > 0.5 else 0.0)
    bpy.context.view_layer.update()
    # cortina pesada: baja (se desenrolla), queda casi quieta y después se infla con una cara desde afuera
    C = S["cortina"]
    bajar = sale(clamp((t - E3_BAJA[0]) / (E3_BAJA[1] - E3_BAJA[0])))
    infla = suave(clamp((t - E3_INFLA) / 1.6))
    cara = suave(clamp((t - (E3_FANT - 0.35)) / 0.45))
    B.deformar_cortina(C, f, inflar=0.03 + 0.20 * infla + 0.14 * cara, centro=(0.14, 1.48), radio=(0.4, 0.5), aleteo=0.4 + 0.6 * infla,
                       cara=(0.12, 1.62), empuje_cara=0.10 * cara, cara_dentro=False, tope_y=-0.05, cara_escala=1.6)
    if bajar < 1:
        me = C["ob"].data
        import numpy as np
        co = np.empty(len(me.vertices) * 3, np.float32)
        me.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)
        ztop = B.Z_RIEL - 0.03
        co[:, 2] = ztop - (ztop - co[:, 2]) * max(0.02, bajar)
        co[:, 1] += 0.05 * (1 - bajar) * np.sin(co[:, 0] * 12)
        me.vertices.foreach_set("co", co.ravel())
        me.update()
    B.gotas(A, t, caliente=0.15)
    B.vapor(A, t, caliente=0.4)


def _e3(sc, a, b, plano):
    S, pj, A = _set_ducha(sc, pesada=True)
    S["pato"].location = (0.45, 0.365, B.Z_BORDE)
    cam = E.camara(sc, lens=38)
    fondo = S["paredes"][0]
    if plano in (17, 18, 21):
        _luz_rasante(sc, S)
    if plano in (17, 18):
        sc.view_settings.exposure = -1.3
    if plano in (20, 21):
        _quitar(fondo)

    def act(f):
        t = (f - 1) / FPS
        act_e3(S, pj, A, t, f)
        if plano == 17:      # afuera, arriba: la cortina pesada baja desde el riel como telón y tapa la cabeza con espuma
            E.empujar(cam, f, a, b, (0.10, -1.85, 1.98), (0.0, -0.35, 1.84), cuanto=0.06, lens=40)
        elif plano == 18:
            E.empujar(cam, f, a, b, (0.35, -2.25, 1.55), (0.0, -0.35, 1.40), cuanto=0.08, lens=36)
        elif plano == 20:    # C0: él tranquilo, la cortina detrás
            E.empujar(cam, f, a, b, (0.66, 1.32, 1.86), (0.02, -0.04, 1.60), cuanto=0.05, lens=34)
        elif plano == 21:    # termina en el encuadre del cuadro 0 (loop)
            E.empujar(cam, f, a, b, (0.66, 1.32, 1.86), (0.02, -0.04, 1.60), cuanto=0.08, lens=34)
        bpy.context.view_layer.update()
        return {}
    return {"actualizar": act}


# =====================================================================================================
def _mk(fn, plano):
    return lambda sc, a, b: fn(sc, a, b, plano)


ESCENA = {**{k: "E1" for k in (1, 2, 3, 4, 5, 16)}, **{k: "E2" for k in (6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 19)},
          **{k: "E3" for k in (17, 18, 20, 21)}}
FUNC = {k: _mk({"E1": _e1, "E2": _e2, "E3": _e3}[e], k) for k, e in ESCENA.items()}


def _pieza(k, fn, **kw):
    a, b = FR(k)
    return dict(a=a, b=b, fn=fn, plano=k, **kw)


PIEZAS = {str(k): _pieza(k, fn) for k, fn in sorted(FUNC.items()) if k in E.T}
