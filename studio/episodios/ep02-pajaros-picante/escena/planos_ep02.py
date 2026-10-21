"""Los 40 planos del Ep. 2 (storyboard v3.1, puerta 3 APROBADO; estilos de la puerta 4 APROBADO).

Cada función pXX(sc, a, b) arma su escena y devuelve {"actualizar": f -> info, "meta": {...}}.
PIEZAS (al final) dice qué renderiza cada pieza: planos principales (cuadros del video) y auxiliares (lupas y
recuadros que el post compone encima).
"""
import math, os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.abspath(os.path.join(HERE, "../../.."))
for p in (HERE, os.path.join(STUDIO, "plantilla")):
    if p not in sys.path:
        sys.path.insert(0, p)
import bpy
from mathutils import Vector, Euler, Matrix, Quaternion
import props as P
import props_ep02 as E
import personajes as PJ
import desierto as D
import vfx as V
import ep02 as E2
import anim_pj as AP

R = math.radians
FR = E2.FR
lin, suave, sale, entra, tramo = E2.lin, E2.suave, E2.sale, E2.entra, E2.tramo


# =====================================================================================================
# C0: el set del cuadro 0 (planos 1, 2, 14, 17, 40)
# =====================================================================================================
def _c0(sc):
    import set_c0
    S = set_c0.armar(sc)
    S["llama"] = AP.Llama(root=bpy.data.objects["Llamarada"])
    rt = S["rt"]
    # las lágrimas siguen a la cabeza del ratón
    for ob in list(bpy.data.objects):
        if "_lagr_" in ob.name:
            PJ.colgar(ob, rt["cabeza"])
    S["rt_cab0"] = rt["cabeza"].rotation_euler.copy()
    S["pj_cab0"] = S["pj"]["cabeza"].rotation_euler.copy()
    S["mand0"] = S["pj"]["mandibula"].rotation_euler.x
    return S


def _c0_vida(S, fase):
    """Lo que se mueve siempre en C0: la llama, el ratón que tiembla un poco y el pájaro que respira (sin cambiar la pose)."""
    S["llama"].poner(fase)
    rt = S["rt"]
    c = S["rt_cab0"]
    rt["cabeza"].rotation_euler = Euler((c.x + R(1.2) * E2.ruido(fase, 3, 2.4), c.y, c.z + R(1.0) * E2.ruido(fase, 4, 2.0)))


def _agarre(S):
    """Pivote del ají en el pico (en el punto que muerde) para girarlo y tragarlo."""
    pj, aji = S["pj"], S["aji"]
    bpy.context.view_layer.update()
    pico = pj["pico"]
    gz = -S["AJI_LARGO"] * S["AJI_T"] * (1 - 0.18 * S["AJI_T"])
    grip_w = aji.matrix_world @ Vector((0, 0, gz))
    piv = P.empty("AgarreAji", loc=grip_w, coll=S["CP"])
    piv.rotation_mode = "QUATERNION"
    PJ.colgar(piv, pico)
    PJ.colgar(aji, piv)
    M = pico.matrix_world.to_3x3().normalized()
    arriba = (M @ Vector((0, 0, 1))).normalized()
    afuera = (M @ Vector((0, -1, 0))).normalized()
    mejor = None
    for g in (-90, 90):
        piv.rotation_quaternion = Quaternion(arriba, R(g))
        bpy.context.view_layer.update()
        punta = (aji.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
        if mejor is None or punta.dot(afuera) > mejor[1]:
            mejor = (g, punta.dot(afuera))
    piv.rotation_quaternion = Quaternion()
    S.update(agarre=piv, agarre_giro=mejor[0], agarre_eje=arriba, agarre_in=-afuera, agarre_loc0=piv.location.copy(),
             aji_loc0=aji.location.copy(), aji_rot0=aji.rotation_euler.copy(), aji_gz=gz)
    return piv


def _agarre_poner(S, giro=0.0, largo=1.0, adentro=0.0):
    """giro 0..1 (0 = cruzado como en C0, 1 = en el eje del pico) · largo: fracción del largo que queda (se acorta
    alrededor del punto que muerde: el trozo tragado no asoma por la nuca) · adentro: metros que entra hacia la boca."""
    piv, aji = S["agarre"], S["aji"]
    piv.rotation_quaternion = Quaternion(S["agarre_eje"], R(S["agarre_giro"]) * giro)
    piv.location = S["agarre_loc0"] + S["agarre_in"] * adentro
    aji.scale = (1, 1, largo)
    Rm = S["aji_rot0"].to_matrix()
    aji.location = S["aji_loc0"] - Rm @ Vector((0, 0, S["aji_gz"] * (largo - 1)))


def p01(sc, a, b):
    S = _c0(sc)
    cam = S["cam"]
    c0, foco = cam.location.copy(), S["foco"]

    pj = S["pj"]
    cab0 = S["pj_cab0"]
    f_parp = a + int((b - a) * 0.55)

    def act(f):
        x = lin(f, a, b - 1)
        cam.location = c0.lerp(foco, 0.11 * suave(x))   # parte exacto en C0 y hace push-in (puerta 6 r1: más marcado)
        _c0_vida(S, f)
        # puerta 6 r1: el pájaro estaba quieto 1,7 s → mastica el ají (mandíbula y cabeza) y parpadea; en el cuadro 1 es C0
        k = suave(lin(x, 0.0, 0.25))
        mast = math.sin(max(0.0, x - 0.05) * 2 * math.pi * 2.2) * k
        pj["mandibula"].rotation_euler.x = S["mand0"] + R(5) * max(0.0, mast)
        pj["cabeza"].rotation_euler = Euler((cab0.x + R(2.5) * mast, cab0.y + R(4) * k, cab0.z + R(5) * k))
        AP.parpados(pj["parpados"], AP.parpadeo(f, f_parp, -30, dur=6))
    return {"actualizar": act, "meta": {"c0": [list(c0), list(foco)]}}


def p40(sc, a, b):
    """Mismo set del cuadro 0; la cámara parte más abierta y el último cuadro es exactamente C0 (loop con el plano 1)."""
    S = _c0(sc)
    cam = S["cam"]
    c0, foco = cam.location.copy(), S["foco"]
    lejos = c0 + (c0 - foco) * 0.22

    pj = S["pj"]
    cab0 = S["pj_cab0"]
    f_parp = a + int((b - a) * 0.40)

    def act(f):
        fase = f - (b - 1) + 1                 # en el último cuadro la fase es 1 = la del primer cuadro del video
        cam.location = lejos.lerp(c0, sale(lin(f, a, b - 1)))
        _c0_vida(S, fase)
        # puerta 6 r1: el pájaro no estaba quieto 1,7 s; ladea la cabeza, parpadea una vez y vuelve exacto a C0
        x = lin(f, a, b - 1)
        k = math.sin(math.pi * x) ** 2
        pj["cabeza"].rotation_euler = Euler((cab0.x + R(-4) * k, cab0.y + R(5) * k, cab0.z + R(7) * k))
        AP.parpados(pj["parpados"], AP.parpadeo(f, f_parp, -30, dur=6))
    return {"actualizar": act}


def _cam_pajaro(S, cam, desde, lens):
    """Cámara para primeros planos del pájaro: `desde` en coordenadas relativas a la cabeza (mundo)."""
    bpy.context.view_layer.update()
    cab = S["pj"]["cabeza"].matrix_world.translation.copy()
    return cab, cab + Vector(desde)


def p02(sc, a, b):
    """y ni lo siente: el ají gira en el pico hasta su eje, entra un trozo de un trago y baja el bulto por el cuello."""
    S = _c0(sc)
    pj = S["pj"]
    _agarre(S)
    bulto = AP.Bulto(pj, S["CP"])
    cam = E2.camara(sc, "Cam02", lens=50, fstop=6.0)
    bpy.context.view_layer.update()
    cab = pj["cabeza"].matrix_world @ Vector((0, -0.016, 0.030))      # centro de la cabeza
    pico_dir = (pj["pico"].matrix_world.to_3x3() @ Vector((0, -1, 0))).normalized()
    centro = cab + pico_dir * 0.050                                    # entre la cabeza y la punta del pico
    pos = centro + Vector((-0.26, -0.36, 0.02))                        # 3/4 desde la izquierda (puerta 6 r1: un poco más atrás)
    n = b - a

    def act(f):
        x = (f - a) / n
        giro = suave(lin(x, 0.05, 0.38))
        tr = AP.trago(lin(x, 0.36, 0.86))
        tg = suave(lin(x, 0.46, 0.62))
        _agarre_poner(S, giro, 1 - 0.20 * tg, 0.012 * tg)
        c = S["pj_cab0"]
        pj["cabeza"].rotation_euler = Euler((c.x - R(14) * tr + R(3) * (giro - suave(lin(x, 0.3, 0.45))), c.y, c.z - R(6) * giro))
        pj["mandibula"].rotation_euler.x = S["mand0"] + R(7) * tr
        bulto.poner(lin(x, 0.55, 0.95))
        # tilt suave hacia abajo siguiendo el bulto
        k = suave(lin(x, 0.5, 1.0))
        E2.mirar(cam, pos, centro + Vector((0, 0, float(os.environ.get("P2_Z", -0.042)) - 0.015 * k)), foco=cab + pico_dir * 0.02)   # puerta 6 r1: el pico bajaba a los subtítulos
        _c0_vida(S, f)
    return {"actualizar": act}


ACORTADO = (0.80, 0.012)          # largo y entrada del ají después del primer trago (planos 2→14, 17)


def _pajaro_acortado(S):
    _agarre(S)
    _agarre_poner(S, 1.0, *ACORTADO)


def p14(sc, a, b):
    """Los pájaros tienen la misma alarma: el pájaro de perfil con el ají ya acortado (el recuadro va en el post)."""
    S = _c0(sc)
    _pajaro_acortado(S)
    cam = E2.camara(sc, "Cam14", lens=50, fstop=4.5)
    bpy.context.view_layer.update()
    pj = S["pj"]
    cab = pj["cabeza"].matrix_world @ Vector((0, -0.016, 0.030))
    pico_dir = (pj["pico"].matrix_world.to_3x3() @ Vector((0, -1, 0))).normalized()
    lado = pico_dir.cross(Vector((0, 0, 1))).normalized()               # perfil: la cámara mira de costado al pico
    # puerta 6 r1: el pico quedaba cortado por el borde y el 14–16 eran 5 s del mismo cuadro quieto → un solo push-in
    # largo de 14 a 16 (piezas "14", "15" y "16"), el pájaro parpadea, mueve la cabeza y traga saliva
    pos = cab + pico_dir * float(os.environ.get("P14_ADEL", 0.06)) - lado * float(os.environ.get("P14_D", 0.50)) + Vector((0, 0, 0.02))
    tgt = cab + pico_dir * float(os.environ.get("P14_ADEL", 0.06)) + Vector((0, 0, float(os.environ.get("P14_Z", -0.055))))
    A, B = FR(14)[0], FR(16)[1]
    parps = [A + int((B - A) * q) for q in (0.18, 0.55, 0.86)]
    cab0 = S["pj_cab0"]

    def act(f):
        x = lin(f, A, B - 1)
        E2.empujar(cam, f, A, B - 1, pos, tgt, cuanto=0.12, foco=cab)
        _c0_vida(S, f)
        ang = 0.0
        for q in parps:
            ang = AP.parpadeo(f, q, -30, dur=6)
            if ang != -30:
                break
        AP.parpados(pj["parpados"], ang)
        # cabeza: mira un poco hacia el recuadro y vuelve, con un respiro
        mira = math.sin(math.pi * lin(x, 0.10, 0.50)) * 0.8 + math.sin(math.pi * lin(x, 0.62, 0.95)) * 0.6
        pj["cabeza"].rotation_euler = Euler((cab0.x - R(5) * mira + R(1.2) * math.sin(f * 0.21), cab0.y, cab0.z + R(4) * mira))
        bpy.context.view_layer.update()
        return {"pico": E2.pantalla(sc, cam, S["pj"]["pico"].matrix_world @ Vector((0, -0.03, -0.004)))}
    return {"actualizar": act}


def p17(sc, a, b):
    """no el picante: una sola acción, el pájaro se traga otro trozo del mismo ají (glup)."""
    S = _c0(sc)
    pj = S["pj"]
    _pajaro_acortado(S)
    bulto = AP.Bulto(pj, S["CP"])
    cam = E2.camara(sc, "Cam17", lens=50, fstop=5.0)
    bpy.context.view_layer.update()
    cab = pj["cabeza"].matrix_world @ Vector((0, -0.016, 0.030))
    pico_dir = (pj["pico"].matrix_world.to_3x3() @ Vector((0, -1, 0))).normalized()
    pos = cab + pico_dir * 0.03 + Vector((-0.20, -0.32, 0.03))
    tgt = cab + pico_dir * 0.03 + Vector((0, 0, -0.035))
    n = b - a

    def act(f):
        x = (f - a) / n
        tr = AP.trago(lin(x, 0.0, 0.62))
        tg = suave(lin(x, 0.15, 0.32))
        _agarre_poner(S, 1.0, ACORTADO[0] - 0.15 * tg, ACORTADO[1] + 0.008 * tg)
        c = S["pj_cab0"]
        pj["cabeza"].rotation_euler = Euler((c.x - R(14) * tr, c.y, c.z - R(6)))
        pj["mandibula"].rotation_euler.x = S["mand0"] + R(7) * tr
        bulto.poner(lin(x, 0.28, 0.85))
        E2.empujar(cam, f, a, b - 1, pos, tgt, cuanto=0.06, foco=cab)
        _c0_vida(S, f)
    return {"actualizar": act}


# =====================================================================================================
# desierto sin el C0 (ratón en la roca principal y el resto de los planos del desierto)
# =====================================================================================================
def _desierto(sc, roca_atras=True, piedritas=True):
    C = P.collection("Desierto")
    S = D.armar(C)
    TOP = S["top"]
    D.cielo(sc, sol_elev=16, sol_azim=-55, fuerza=3.0)
    E2.area(sc, "Relleno", (0.9, -1.3, 0.8), 10, 1.2, (0.75, 0.88, 1.0), (0.05, 0.0, TOP + 0.1))
    E2.area(sc, "Contorno", (0.5, 1.1, 0.75), 60, 0.6, (1.0, 0.70, 0.40), (0.05, 0.0, TOP + 0.12))
    D.roca("DunaIzq", (-1.6, 2.6, 0), (3.2, 1.6, 0.45), C, seed=44)
    if roca_atras:
        D.roca("RocaAtras", (0.12, 0.30, 0), (0.50, 0.30, 0.36), C, seed=3)
    bpy.context.view_layer.update()
    rp = bpy.data.objects["RocaPrincipal"]
    dg = bpy.context.evaluated_depsgraph_get()
    ev = rp.evaluated_get(dg)
    Mi = rp.matrix_world.inverted()

    def suelo(x, y):
        hit, loc, *_ = ev.ray_cast(Mi @ Vector((x, y, 2.0)), (Mi.to_3x3() @ Vector((0, 0, -1))).normalized())
        return (rp.matrix_world @ loc).z if hit else TOP
    if piedritas:
        rr = random.Random(3)
        pied = P.mat("Piedrita", (0.55, 0.30, 0.16), rough=0.8)
        for k in range(40):
            pz = P.prim("ico", f"Piedrita{k}", C, pied, r=rr.uniform(0.002, 0.007), sub=2)
            pz.scale = (1, rr.uniform(0.7, 1.3), rr.uniform(0.5, 0.8))
            x, y = rr.uniform(-0.30, 0.30), rr.uniform(-0.55, 0.05)
            if abs(x - 0.10) < 0.09 and -0.20 < y < 0.12:
                continue
            pz.location = (x, y, suelo(x, y) + pz.scale.z * 0.0045 * 0.75 - 0.0005)
    return dict(C=C, TOP=TOP, suelo=suelo, CP=P.collection("Personajes"))


MX, MY = 0.10, 0.05          # ratón en la roca principal (tabla de utilería)


class Raton:
    """El ratón del cactus en la roca principal, con cara que se pone roja, llama, lágrimas y bocanada."""

    def __init__(self, sc, S, x=MX, y=MY, rot=-50, escala=1.15, nombre="Raton", llama=True, lagrimas=True):
        self.sc, self.S = sc, S
        rt = PJ.raton(S["CP"], nombre=nombre)
        self.rt = rt
        rt["root"].scale = (escala, escala, escala)
        rt["root"].location = (x, y, S["suelo"](x, y))
        rt["root"].rotation_euler.z = R(rot)
        self.rot0 = R(rot)
        for k, ob in enumerate(rt["orejas"]):
            ob.rotation_euler = (R(10), 0, R(10 * (1 if k else -1)))
        for k, br in enumerate(rt["brazos"]):
            br.rotation_euler = (R(-5), 0, 0)
        self.roja = AP.cara_roja_animable(rt)
        bpy.context.view_layer.update()
        self.cab0 = rt["cabeza"].rotation_euler.copy()
        self.llama = None
        if llama:
            o, d = self.boca_dir()
            self.llama = AP.Llama(nombre + "Llama", o, d, S["CP"], escala=1.5)
            self.llama_piv = P.empty(nombre + "LlamaPiv", loc=o, coll=S["CP"])
            PJ.colgar(self.llama_piv, rt["cabeza"])
            PJ.colgar(self.llama.root, self.llama_piv)
            self.llama.base_rot = self.llama.root.rotation_euler.copy()
            self.llama.poner(0, 0)
        self.lagr = []
        if lagrimas:
            for o in rt["ojos"]:
                ow = o.matrix_world.translation
                abajo = (rt["cabeza"].matrix_world.to_3x3() @ Vector((0, -0.3, -1))).normalized()
                for ob in V.lagrimas(o.name + "_lagr", ow + abajo * 0.010, abajo, S["CP"], largo=0.028, seed=1):
                    PJ.colgar(ob, rt["cabeza"])
                    self.lagr.append(ob)
        self.ojo_esc = [o.scale.copy() for o in rt["ojos"]]
        self.pose()

    def boca_dir(self):
        bpy.context.view_layer.update()
        rt = self.rt
        boca_w = rt["boca"].matrix_world.translation.copy()
        M = rt["cabeza"].matrix_world.to_3x3().normalized()
        frente = (M @ Vector((0, -1, 0.0))).normalized()
        frente = (frente + Vector((0, 0, 0.04))).normalized()
        abajo = (M @ Vector((0, 0, -1))).normalized()
        return boca_w + frente * 0.026 * 1.15 + abajo * 0.006, frente

    def pose(self, cab=(0, 0, 0), cuerpo=0.0, giro=0.0, boca=0.0, ojos=-100, ojos_esc=1.0, roja=0.0, llama=0.0, f=0,
             lagrimas=False, brazo=None, doblar=0.0, lado=0.0):
        """cab: grados (x, y, z) que se suman a la cabeza · cuerpo: inclinación hacia adelante (grados) · giro: grados en z
        · boca 0..1 · ojos: ángulo de los párpados · roja 0..1 · llama 0..1 · brazo: (x, z) grados del brazo derecho."""
        rt = self.rt
        rt["root"].rotation_euler = Euler((R(cuerpo), 0, self.rot0 + R(giro)))
        rt["cabeza"].rotation_euler = Euler((self.cab0.x + R(cab[0]), self.cab0.y + R(cab[1]), self.cab0.z + R(cab[2])))
        rt["boca"].scale = (1 + 0.6 * boca, 1 + 0.4 * boca, 1 + 2.2 * boca)
        AP.parpados(rt["parpados"], ojos)
        for o, s0 in zip(rt["ojos"], self.ojo_esc):
            o.scale = s0 * ojos_esc
        self.roja(roja)
        if self.llama:
            self.llama.poner(f, llama, doblar, lado)
        if not hasattr(self, "lagr0"):
            self.lagr0 = [ob.location.copy() for ob in self.lagr]
        for k, (ob, l0) in enumerate(zip(self.lagr, self.lagr0)):     # puerta 6 r1: resbalan y caen (antes fijas)
            ph = ((f + 13 * k) % 26) / 26.0
            ob.location = l0 + Vector((0, 0, -0.010 * ph * ph))
            ob.hide_render = (not lagrimas) or ph > 0.92
        for k, br in enumerate(rt["brazos"]):
            if k == 1 and brazo is not None:
                br.rotation_euler = (R(brazo[0]), 0, R(brazo[1]))
            else:
                br.rotation_euler = (R(-5), 0, 0)

    def punto(self, nombre="boca"):
        bpy.context.view_layer.update()
        return self.rt[nombre].matrix_world.translation.copy()


def _aji_roca(S, nombre, donde, largo=0.10, grosor=0.0155, rot=-70, mordido=False, seed=11, piedra=0.0):
    """Ají acostado sobre la roca principal en `donde` (x, y); si piedra > 0, sobre una piedrita de esa altura."""
    x, y = donde
    z0 = S["suelo"](x, y)
    if piedra:
        pm = P.mat("PiedraLisa", (0.50, 0.27, 0.15), rough=0.8)
        pi = P.prim("ico", nombre + "_piedra", S["C"], pm, r=1.0, sub=3)
        pi.scale = (largo * 0.55, 0.040, piedra + 0.012)
        pi.location = (x, y, z0 - 0.012)
        pi.modifiers.new("Sub", "SUBSURF").levels = 1
        z0 += piedra
    a = E.aji(nombre, largo=largo, grosor=grosor, coll=S["CP"], seed=seed, curva=0.25)
    a.rotation_euler = (R(90), 0, R(rot))
    bpy.context.view_layer.update()
    # el centro del ají queda en (x, y), apoyado (radio máximo ~0,77·grosor)
    c = a.matrix_world @ Vector((0, 0, -largo * 0.5))
    a.location = Vector((x, y, z0 + grosor * 0.77 + 0.001)) + (a.location - c)
    a.location.z = z0 + grosor * 0.77 - (0.003 if piedra else -0.001)
    if mordido:
        E.mordisco_media_luna(a, S["CP"], t=0.55, lado=(0.62, 0.78, 0), r=grosor * 1.0, semillas=5, pulpa=False, en_corte=True)
    return a


def _cam_medio(sc, rt_obj, desde, lens=40, fstop=5.6, alto=0.0):
    cam = E2.camara(sc, "Cam", lens=lens, fstop=fstop)
    return cam


def p03(sc, a, b):
    """Este ratón lo prueba: ratón tranquilo, agacha el hocico y le da un mordisco al ají apoyado frente a él."""
    S = _desierto(sc)
    rat = Raton(sc, S, llama=False, lagrimas=False)
    # pose del mordisco, para ubicar el ají justo bajo la boca
    rat.pose(cab=(30, 0, 0), cuerpo=24, boca=0.7)
    boca = rat.punto("boca")
    rat.pose()
    entero = _aji_roca(S, "AjiEntero", (boca.x, boca.y - 0.004), piedra=max(0.0, boca.z - S["suelo"](boca.x, boca.y) - 0.024), rot=-80)
    bpy.context.view_layer.update()
    # mismo ají, ya mordido (aparece en el cuadro del mordisco, tapado por la cabeza)
    mord = entero.copy()
    mord.data = entero.data.copy()
    mord.name = "AjiMordidoRoca"
    S["CP"].objects.link(mord)
    for ch in entero.children:
        c2 = ch.copy()
        c2.parent = mord
        S["CP"].objects.link(c2)
    for m in list(mord.modifiers):
        if m.name.startswith("Bocado"):
            mord.modifiers.remove(m)
    E.mordisco_media_luna(mord, S["CP"], t=0.55, lado=(0.62, 0.78, 0), r=0.0155, semillas=5, pulpa=False, en_corte=True)
    cam = E2.camara(sc, "Cam03", lens=40, fstop=5.6)
    cab = (rat.punto("cabeza") + boca) / 2 + Vector((0, 0, float(os.environ.get("P3_Z", -0.045))))   # puerta 6 r1: el ají quedaba bajo los subtítulos
    pos = cab + Vector((0.08, -0.64, 0.02))
    n = b - a
    f_mord = a + int(n * 0.58)

    def act(f):
        x = (f - a) / n
        baja = suave(lin(x, 0.25, 0.52)) * (1 - suave(lin(x, 0.68, 0.92)))
        mastica = math.sin(max(0, f - f_mord) * 0.9) * (0.25 if f > f_mord else 0)
        rat.pose(cab=(30 * baja, 0, 0), cuerpo=24 * baja, boca=0.7 * suave(lin(x, 0.40, 0.55)) * (1 - suave(lin(x, 0.58, 0.64))) + abs(mastica) * 0.2,
                 ojos=AP.parpadeo(f, a + 8, -100), f=f)
        E2.oculto(entero, f >= f_mord)
        E2.oculto(mord, f < f_mord)
        E2.empujar(cam, f, a, b - 1, pos, cab, cuanto=0.06, foco=cab)
    return {"actualizar": act, "meta": {"mordisco": f_mord}}


def _raton_con_aji(sc, S, rat):
    """El ají ya mordido frente al ratón (en la misma posición que dejó el plano 3)."""
    rat.pose(cab=(30, 0, 0), cuerpo=24, boca=0.7)
    boca = rat.punto("boca")
    rat.pose()
    aji = _aji_roca(S, "AjiMordidoRoca", (boca.x, boca.y - 0.004), piedra=max(0.0, boca.z - S["suelo"](boca.x, boca.y) - 0.024), rot=-80, mordido=True)
    return aji


def p04(sc, a, b):
    """y echa fuego: la llama crece en 6 cuadros, los ojos se abren enormes y la cara se pone roja; shake corto."""
    S = _desierto(sc)
    rat = Raton(sc, S)
    aji = _raton_con_aji(sc, S, rat)
    cam = E2.camara(sc, "Cam04", lens=45, fstop=4.0)
    cab = rat.punto("cabeza") + Vector((0, 0, 0.0))
    pos = cab + Vector((0.13, -0.66, 0.02))
    tgt = cab + Vector((-0.045, -0.02, 0.0))      # puerta 6 r1: la cabeza se cortaba a la derecha · revisión del borrador: la llama salía cortada (sólo el centro blanco)
    f_fuego = a + 3
    doblar = float(os.environ.get("P4_DOBLAR", 30))

    def act(f):
        t = (f - f_fuego) / E2.FPS
        llama = rebote_llama(f - f_fuego)
        rat.pose(cab=(-12 * sale(lin(f, f_fuego, f_fuego + 5)), 0, 0), boca=suave(lin(f, f_fuego - 2, f_fuego + 2)),
                 ojos=-100 - 15 * suave(lin(f, f_fuego, f_fuego + 4)), ojos_esc=1 + 0.25 * E2.rebote(lin(f, f_fuego, f_fuego + 6)),
                 roja=suave(lin(f, f_fuego + 4, f_fuego + 16)), llama=llama * 0.8, doblar=doblar, f=f)
        sh = math.exp(-max(0, t) * 7) * (1 if t > 0 else 0)
        off = Vector((0.004 * math.sin(f * 2.7), 0, 0.004 * math.sin(f * 3.9))) * sh
        E2.mirar(cam, pos + off, tgt + off, foco=cab)
    return {"actualizar": act}


def rebote_llama(df):
    """Tamaño de la llama que nace: crece en 6 cuadros con un rebotito."""
    if df <= 0:
        return 0.0
    return min(1.12, E2.rebote(df / 6.0, 2.2)) if df < 6 else 1.0 + 0.05 * math.exp(-(df - 6) / 4)


def p05(sc, a, b):
    """Para el ají, tú y este ratón son lo mismo: ají mordido en primer plano; el foco se corre al ratón, que mira a
    cámara y apunta al que mira con la patita (sin tocar nada); llama más chica; aparece TÚ = RATÓN."""
    S = _desierto(sc)
    rat = Raton(sc, S)
    aji = _raton_con_aji(sc, S, rat)
    cam = E2.camara(sc, "Cam05", lens=35, fstop=2.8)
    bpy.context.view_layer.update()
    aj = aji.matrix_world @ Vector((0, 0, -0.05))
    cab = rat.punto("cabeza")
    adelante = Vector((aj.x - cab.x, aj.y - cab.y, 0)).normalized()
    pos = aj + adelante * 0.50 + Vector((0.06, 0, 0.07))
    tgt = cab.lerp(aj, 0.30) + Vector((0, 0, 0.045))
    n = b - a

    def act(f):
        x = (f - a) / n
        foco = aj.lerp(cab, suave(lin(x, 0.05, 0.32)))
        E2.empujar(cam, f, a, b - 1, pos, tgt, cuanto=0.18, foco=foco)
        mira = AP.mirar_a(rat.rt["cabeza"], cam.location, 0.7)
        k = suave(lin(x, 0.15, 0.40))
        # puerta 6 r1: 2,8 s en la misma pose → en "son lo mismo" se inclina hacia la cámara y asiente dos veces
        inc = math.sin(math.pi * lin(x, 0.48, 0.92))
        asiente = math.sin(lin(x, 0.55, 0.85) * 2 * math.pi * 2) * inc
        rat.pose(cab=(math.degrees(mira.x) * k + 10 * asiente, 0, math.degrees(mira.z) * k), cuerpo=9 * inc, ojos=AP.parpadeo(f, a + int(n * 0.7), -110), ojos_esc=1.15,
                 roja=1.0, llama=(0.26 - 0.12 * suave(lin(x, 0.40, 0.55))) + 0.03 * E2.ruido(f, 9, 2.0), doblar=25, lado=float(os.environ.get("LLAMA_LADO", -95)) * k, f=f, lagrimas=True,
                 brazo=(-62 * suave(lin(x, 0.35, 0.55)), 14 * suave(lin(x, 0.35, 0.55))))
        bpy.context.view_layer.update()
        orejas = [E2.pantalla(sc, cam, o.matrix_world @ Vector((0, 0, 0.04))) for o in rat.rt["orejas"]]
        return {"orejas_y": min(p[1] for p in orejas)}
    return {"actualizar": act}


def p06(sc, a, b):
    """mamíferos: la llama se vuelve una bocanada de humo con un suspiro; la cara sigue roja y con lágrimas."""
    S = _desierto(sc)
    rat = Raton(sc, S)
    aji = _raton_con_aji(sc, S, rat)
    o, d = rat.boca_dir()
    humo = AP.Bocanada("Humo06", o, d, S["CP"], n=7, tam=0.016)
    cam = E2.camara(sc, "Cam06", lens=40, fstop=4.0)
    cab = rat.punto("cabeza")
    pos = cab + Vector((0.06, -0.55, 0.0))
    tgt = cab + Vector((0, 0, -0.035))
    n = b - a

    def act(f):
        E2.empujar(cam, f, a, b - 1, pos, tgt, cuanto=0.05, foco=cab)
        x = (f - a) / n
        mira = AP.mirar_a(rat.rt["cabeza"], cam.location, 0.7)
        suspiro = math.sin(math.pi * lin(x, 0.15, 0.75))
        rat.pose(cab=(math.degrees(mira.x) - 6 * suspiro, 0, math.degrees(mira.z)), boca=0.5 * suspiro, ojos=-100 + 40 * suspiro,
                 roja=1.0, llama=0.45 * (1 - suave(lin(x, 0.10, 0.30))), doblar=70, f=f, lagrimas=True)
        humo.poner(lin(x, 0.15, 1.05))
    return {"actualizar": act}


def _textura_texto(nombre, lineas, tam=(512, 256), fondo=(255, 255, 255), color=(20, 24, 30), fuente_px=110, borde=None):
    """Imagen con texto (etiquetas de cajitas, carteles): devuelve una imagen de Blender."""
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGB", tam, fondo)
    d = ImageDraw.Draw(im)
    fpath = os.path.join(STUDIO, "plantilla", "fonts", "Inter-Black.otf")
    fz = fuente_px
    while True:
        fnt = ImageFont.truetype(fpath, fz)
        if all(fnt.getlength(t) <= tam[0] * 0.9 for t in lineas) or fz < 20:
            break
        fz -= 4
    h = fz * 1.15 * len(lineas)
    for k, t in enumerate(lineas):
        d.text((tam[0] / 2, tam[1] / 2 - h / 2 + fz * 1.15 * (k + 0.5)), t, font=fnt, fill=color, anchor="mm")
    if borde:
        d.rectangle((6, 6, tam[0] - 7, tam[1] - 7), outline=borde, width=10)
    path = os.path.join(bpy.app.tempdir or "/tmp", f"{nombre}.png")
    im.save(path)
    return bpy.data.images.load(path)


def _mat_imagen(nombre, img, rough=0.5, emit=0.0):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = img
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    if emit:
        nt.links.new(t.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emit
    return m


def _plano_imagen(nombre, img, ancho, alto, coll, emit=0.0):
    """Rectángulo con una imagen (cara de una cajita, cartel)."""
    import bmesh
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new()
    vs = [bm.verts.new((x * ancho / 2, 0, z * alto / 2)) for x, z in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    f = bm.faces.new(vs)
    for lp, (u, v) in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        lp[uv].uv = (u, v)
    ob = P.mesh_obj(nombre, bm, coll, smooth=False, m=_mat_imagen(nombre + "_m", img, emit=emit))
    return ob


def cajita_leche(nombre, texto, coll, color=(0.20, 0.55, 0.95), ancho=0.062, alto=0.11):
    """Cajita de leche (tetra con techo a dos aguas) con la etiqueta grande al frente (-Y). Origen = base."""
    root = P.empty(nombre, coll=coll)
    cuerpo_m = P.mat(nombre + "_cuerpo", (0.96, 0.96, 0.95), rough=0.4)
    banda = P.mat(nombre + "_banda", color, rough=0.4)
    c = P.prim("cube", nombre + "_caja", coll, cuerpo_m)
    c.scale = (ancho, ancho, alto)
    c.location = (0, 0, alto / 2)
    P.bevel(c, 0.002, 2)
    c.parent = root
    techo = P.prim("cyl", nombre + "_techo", coll, banda, r=ancho * 0.72, r2=0.0005, h=ancho * 0.45, seg=4)
    techo.rotation_euler = (0, 0, R(45))
    techo.scale = (1, 0.98, 1)
    techo.location = (0, 0, alto + ancho * 0.22)
    techo.parent = root
    img = _textura_texto(nombre + "_etq", [texto], (640, 360), fondo=(255, 255, 255), color=(16, 40, 90), fuente_px=150)
    et = _plano_imagen(nombre + "_etiqueta", img, ancho * 0.94, alto * 0.50, coll)
    et.location = (0, -ancho / 2 - 0.0008, alto * 0.48)
    et.parent = root
    b2 = P.prim("cube", nombre + "_franja", coll, banda)
    b2.scale = (ancho * 1.002, ancho * 1.002, alto * 0.16)
    b2.location = (0, 0, alto * 0.12)
    b2.parent = root
    return root


def baliza(nombre, coll, r=0.016):
    """Baliza de alarma (gorro): base gris y cúpula roja con dos haces que giran. Origen = base."""
    root = P.empty(nombre, coll=coll)
    base = P.prim("cyl", nombre + "_base", coll, P.mat("BalizaBase", (0.10, 0.10, 0.11), rough=0.4, metal=0.5), r=r * 1.1, r2=r * 1.05, h=r * 0.45, seg=40)
    base.location = (0, 0, r * 0.22)
    base.parent = root
    vidrio = P.mat("BalizaVidrio", (1.0, 0.06, 0.04), rough=0.15, emit=1.2)
    cup = P.prim("sphere", nombre + "_cupula", coll, vidrio, r=r, u=40, v=20)
    cup.scale = (1, 1, 1.25)
    cup.location = (0, 0, r * 0.45)
    cup.parent = root
    giro = P.empty(nombre + "_giro", loc=(0, 0, r * 0.9), coll=coll, parent=root)
    for k in (0, 1):
        L = bpy.data.lights.new(f"{nombre}_haz{k}", "SPOT")
        L.energy, L.color, L.spot_size, L.spot_blend = 1.5, (1.0, 0.1, 0.05), R(40), 0.5
        L.shadow_soft_size = 0.002
        ob = bpy.data.objects.new(f"{nombre}_haz{k}", L)
        coll.objects.link(ob)
        ob.parent = giro
        ob.rotation_euler = (R(90), 0, R(180 * k))
    return root, giro, vidrio


def p12(sc, a, b):
    """Tu cerebro cree que te quemas: el ratón sudando con una baliza de alarma apoyada en la cabeza, girando."""
    S = _desierto(sc)
    rat = Raton(sc, S, llama=False, lagrimas=False)
    bpy.context.view_layer.update()
    rt = rat.rt
    cab = rt["cabeza_malla"]
    # punto más alto de la cabeza (rayo hacia abajo): ahí se apoya la baliza
    dg = bpy.context.evaluated_depsgraph_get()
    c = rat.punto("cabeza")
    cc = cab.matrix_world @ (sum((Vector(v) for v in cab.bound_box), Vector()) / 8)    # centro de la cabeza
    Mi = cab.matrix_world.inverted()
    hit, loc, *_ = cab.evaluated_get(dg).ray_cast(Mi @ (cc + Vector((0, 0, 0.3))), (Mi.to_3x3() @ Vector((0, 0, -1))).normalized())
    top = cab.matrix_world @ loc
    bal, giro, vid = baliza("Baliza", S["CP"])
    bal.location = top - Vector((0, 0, 0.002))
    bal.scale = (2.0, 2.0, 2.0)
    PJ.colgar(bal, rt["cabeza"])
    gotas = []
    gm = P.mat("Sudor", (0.75, 0.90, 1.0), rough=0.05, transmission=0.9)
    for k, (dx, dz) in enumerate(((0.030, 0.012), (-0.028, 0.020), (0.022, -0.004))):
        g = P.prim("sphere", f"Sudor{k}", S["CP"], gm, r=0.0035)
        g.scale = (1, 1, 1.5)
        g.location = c + Vector((dx * 1.15, -0.03, dz * 1.15))
        PJ.colgar(g, rt["cabeza"])
        gotas.append((g, g.location.copy(), k))
    # puerta 6 r1: el ratón se veía translúcido (SSS + los haces rojos de la baliza pegados a las orejas)
    for m_ in bpy.data.materials:
        if m_.use_nodes and m_.name.startswith(("Raton", "raton", "Rosado", "Oreja_")) and "Principled BSDF" in m_.node_tree.nodes:
            m_.node_tree.nodes["Principled BSDF"].inputs["Subsurface Weight"].default_value = 0.0
    for ob in bpy.data.objects:
        if ob.type == "LIGHT" and ob.name.startswith("Baliza_haz"):
            ob.data.energy = 0.5
    cam = E2.camara(sc, "Cam12", lens=42, fstop=4.0)
    pos = c + Vector((0.04, -0.86, 0.10))      # puerta 6 r1: cara más arriba (los ojos en y≈600, el mentón sobre los subtítulos)
    tgt = c + Vector((0, 0, -0.065))

    z0 = rt["root"].location.z

    def act(f):
        x = lin(f, a, b - 1)
        E2.empujar(cam, f, a, b - 1, pos, tgt, cuanto=0.06, foco=c)
        mira = AP.mirar_a(rt["cabeza"], cam.location, 0.7)
        # puerta 6 r1: estaba tieso → con "¡FUEGO!" se agacha (anticipación), salta del susto con ojos enormes y boca
        # abierta, y queda temblando
        agacha = math.sin(math.pi * lin(x, 0.06, 0.16))
        salto = math.sin(math.pi * lin(x, 0.16, 0.34))
        susto = suave(lin(x, 0.14, 0.24))
        tiembla = susto * math.sin((f - a) * 2.3)
        rat.pose(cab=(math.degrees(mira.x) + 1.5 * E2.ruido(f, 5, 3) - 8 * salto, 0, math.degrees(mira.z) + 2.5 * tiembla), cuerpo=6 * agacha - 4 * salto,
                 boca=0.85 * susto, ojos=-108 - 8 * susto, ojos_esc=1.12 + 0.25 * susto + 0.15 * E2.rebote(lin(x, 0.16, 0.30)), roja=1.0, f=f)
        rt["root"].location.z = z0 - 0.006 * agacha + 0.030 * salto
        giro.rotation_euler = (0, 0, (f - a) * 0.55)
        vid.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.5 + 3.0 * max(0, math.sin((f - a) * 0.55 * 2)) ** 2
        for g, l0, k in gotas:
            ph = ((f - a + k * 13) % 36) / 36
            g.location = l0 + Vector((0, 0, -0.012 * ph))
        bpy.context.view_layer.update()
        return {"baliza_y": E2.pantalla(sc, cam, bal.matrix_world @ Vector((0, 0, 0.04)))[1]}
    return {"actualizar": act}


def termometro(nombre, coll, r=0.028):
    """Termómetro de cocina de esfera: pincho de metal y esfera con zonas (azul, verde 'normal', rojo) y aguja.
    Origen = punta del pincho; la esfera mira a -Y. Devuelve (raíz, aguja)."""
    from PIL import Image, ImageDraw
    root = P.empty(nombre, coll=coll)
    metal = P.mat("TermoMetal", (0.80, 0.80, 0.82), rough=0.25, metal=1.0)
    L = 0.09
    pin = P.prim("cyl", nombre + "_pincho", coll, metal, r=0.0018, r2=0.0012, h=L, seg=16)
    pin.location = (0, 0, L / 2)
    pin.parent = root
    caja = P.prim("cyl", nombre + "_caja", coll, metal, r=r, r2=r, h=0.012, seg=48)
    caja.rotation_euler = (R(90), 0, 0)
    caja.location = (0, 0.004, L + r * 0.9)
    caja.parent = root
    W = 512
    im = Image.new("RGB", (W, W), (245, 244, 238))
    d = ImageDraw.Draw(im)
    c = W / 2
    for a0, a1, col in ((135, 200, (70, 140, 230)), (200, 300, (70, 190, 110)), (300, 405, (235, 60, 40))):
        d.arc((40, 40, W - 40, W - 40), a0, a1, fill=col, width=60)
    for k in range(11):
        ang = math.radians(135 + 27 * k)
        d.line((c + 150 * math.cos(ang), c + 150 * math.sin(ang), c + 175 * math.cos(ang), c + 175 * math.sin(ang)), fill=(30, 30, 30), width=6)
    d.ellipse((c - 18, c - 18, c + 18, c + 18), fill=(30, 30, 30))
    path = os.path.join(bpy.app.tempdir or "/tmp", nombre + "_esfera.png")
    im.save(path)
    cara = _plano_imagen(nombre + "_cara", bpy.data.images.load(path), r * 1.38, r * 1.38, coll)
    cara.location = (0, -0.0025, L + r * 0.9)
    cara.parent = root
    vidrio = P.mat("TermoVidrio", (1, 1, 1), rough=0.02, transmission=1.0)
    vid = P.prim("cyl", nombre + "_vidrio", coll, vidrio, r=r * 0.96, r2=r * 0.96, h=0.002, seg=48)
    vid.rotation_euler = (R(90), 0, 0)
    vid.location = (0, -0.0045, L + r * 0.9)
    vid.parent = root
    ag_piv = P.empty(nombre + "_agujaPiv", loc=(0, -0.0035, L + r * 0.9), coll=coll, parent=root)
    ag = P.prim("cube", nombre + "_aguja", coll, P.mat("TermoAguja", (0.85, 0.05, 0.03), rough=0.4))
    ag.scale = (0.0016, 0.0008, r * 0.75)
    ag.location = (0, 0, r * 0.37)
    ag.parent = ag_piv
    return root, ag_piv


def p13(sc, a, b):
    """aunque nada esté caliente: termómetro clavado en el ají; la aguja da un tic chico y vuelve a 'normal'."""
    S = _desierto(sc)
    x, y = 0.06, -0.10
    aji = _aji_roca(S, "AjiTermo", (x, y), largo=0.11, grosor=0.017, rot=-75, mordido=True)
    bpy.context.view_layer.update()
    pinch = aji.matrix_world @ Vector((0.0, 0, -0.035))
    term, aguja = termometro("Termometro", S["CP"])
    term.location = pinch + Vector((0, 0, -0.012))
    term.rotation_euler = (R(-12), R(8), 0)
    cam = E2.camara(sc, "Cam13", lens=50, fstop=4.0)
    bpy.context.view_layer.update()
    esf = term.matrix_world @ Vector((0, 0, 0.09 + 0.025))
    pos = esf + Vector((-0.03, -0.64, -0.02))       # puerta 6 r1: el ají quedaba bajo la interfaz de la app
    tgt = esf + Vector((0, 0, -0.115))
    n = b - a

    def act(f):
        x_ = (f - a) / n
        tic = math.exp(-max(0, x_ - 0.35) * 18) * math.sin(max(0, x_ - 0.35) * 60) if x_ > 0.35 else 0
        aguja.rotation_euler = (0, R(-(10 + 14 * tic)), 0)          # en la zona verde ("normal")
        E2.empujar(cam, f, a, b - 1, pos, tgt, cuanto=0.05, foco=esf)
        bpy.context.view_layer.update()
        return {"termo_y": E2.pantalla(sc, cam, esf + Vector((0, 0, 0.035)))[1]}
    return {"actualizar": act}


def p33(sc, a, b):
    """¿Y tú?: de vuelta al desierto, el ratón volvió a probar (segundo ají mordido a su lado): cara roja, lágrimas y llama."""
    S = _desierto(sc)
    rat = Raton(sc, S)
    _aji_roca(S, "AjiMordido2", (0.02, 0.00), rot=-30, mordido=True, seed=12)
    cam = E2.camara(sc, "Cam33", lens=42, fstop=4.0)
    cab = rat.punto("cabeza")
    pos = cab + Vector((0.16, -0.62, 0.0))          # puerta 6 r1: cortaba las orejas
    tgt = cab + Vector((-0.02, 0, -0.025))

    def act(f):
        E2.empujar(cam, f, a, b - 1, pos, tgt, cuanto=0.07, foco=cab)
        mira = AP.mirar_a(rat.rt["cabeza"], cam.location, 0.7)
        rat.pose(cab=(math.degrees(mira.x), 0, math.degrees(mira.z)), boca=1.0, ojos=-112, ojos_esc=1.2, roja=1.0, llama=0.45, doblar=25, lado=float(os.environ.get("LLAMA_LADO", -95)), f=f, lagrimas=True)
    return {"actualizar": act}


def p34(sc, a, b):
    """Toma leche, aunque sea descremada: con la llama doblada hacia arriba, el ratón agacha el hocico sobre el vaso,
    bebe, la leche baja y la llama se achica; al levantar la cabeza sale un hilo de humo y queda la cara de alivio."""
    S = _desierto(sc)
    rat = Raton(sc, S)
    rat.pose(cab=(32, 0, 0), cuerpo=26, boca=0.4)
    boca = rat.punto("boca")
    rat.pose()
    z0 = S["suelo"](boca.x, boca.y)
    alto = max(0.05, min(0.085, boca.z - z0 - 0.002))
    vaso = E.vaso_leche("VasoLeche", S["CP"], alto=alto, r=0.036, nivel=0.85)
    vaso.location = (boca.x, boca.y - 0.010, z0 - 0.001)
    leche = bpy.data.objects["VasoLeche_leche"]
    caja = cajita_leche("CajaDescremada", "DESCREMADA", S["CP"])
    cx, cy = boca.x - 0.098, boca.y + 0.060          # puerta 6 r1: más lejos de la llama (se quemaba a blanco)
    caja.location = (cx, cy, S["suelo"](cx, cy) - 0.001)
    caja.rotation_euler.z = R(10)
    o, d = rat.boca_dir()
    humo = AP.Bocanada("Humo34", o, d, S["CP"], n=9, tam=0.007)
    if rat.llama:
        rat.llama.luz_e *= 0.5
    orejas0 = [o_.rotation_euler.copy() for o_ in rat.rt["orejas"]]
    cam = E2.camara(sc, "Cam34", lens=32, fstop=5.6)
    cab = rat.punto("cabeza")
    tgt = cab.lerp(boca, 0.5) + Vector((-0.02, 0, -0.03))
    pos = tgt + Vector((0.10, -0.62, 0.03))
    n = b - a

    def act(f):
        x = (f - a) / n
        # puerta 6 r1: al levantar la cabeza todo cambiaba de golpe (ojos, lágrimas); ahora sube en ~0,5 s con anticipación,
        # los ojos se entornan y se abren con fundido y lo rojo baja a café junto con el humo
        baja = suave(lin(x, 0.08, 0.28)) * (1 - suave(lin(x, 0.76, 0.96)))
        antic = math.sin(math.pi * lin(x, 0.70, 0.78))
        bebe = lin(x, 0.28, 0.76)
        nivel = 0.85 - 0.50 * suave(bebe)
        leche.scale = (1, 1, nivel / 0.85)
        hund = 0.5 * (0.85 - nivel)               # el hocico sigue el nivel de la leche (un poco más adentro)
        alivio = suave(lin(x, 0.84, 0.98))
        entorna = suave(lin(x, 0.26, 0.34)) * (1 - suave(lin(x, 0.74, 0.84)))
        ojos = -100 + 40 * entorna + 70 * alivio
        rat.pose(cab=(32 * baja + 18 * hund * baja + 4 * antic, 0, 14 * baja), cuerpo=26 * baja + 10 * hund * baja, boca=0.4 * baja,
                 ojos=ojos, roja=1.0 - 0.6 * alivio,
                 llama=max(0.0, 0.9 - 0.95 * suave(bebe)), doblar=55 * baja, f=f, lagrimas=x < 0.86)
        for k_, (o_, r0_) in enumerate(zip(rat.rt["orejas"], orejas0)):       # que la oreja no quede de canto al tomar
            o_.rotation_euler = Euler((r0_.x - R(25) * baja, r0_.y, r0_.z + (R(40) if k_ == 0 else R(-15)) * baja))
        humo.poner(lin(x, 0.84, 1.05))
        E2.empujar(cam, f, a, b - 1, pos, tgt, cuanto=0.05, foco=tgt)
    return {"actualizar": act}


# =====================================================================================================
# el chiltepín de Arizona (planos 18–22, 25–27)
# =====================================================================================================
MATA = Vector((-1.25, -1.70, 0.0))      # mata de chiltepín en la arena, delante de la roca principal


def _chiltepin(S, alto=0.36, frutos=26):
    root, fr = D.mata("Chiltepin", tuple(MATA), S["C"], alto=alto, seed=8, frutos=frutos, fruto_r=0.0065)
    return root, fr


def videocamara(nombre, coll, loc, mira):
    """Cámara de video en trípode (la de los científicos) con su luz roja de grabación. Devuelve (raíz, luz)."""
    root = P.empty(nombre, loc=loc, coll=coll)
    negro = P.mat("CamNegro", (0.03, 0.03, 0.035), rough=0.35)
    gris = P.mat("CamGris", (0.25, 0.25, 0.27), rough=0.4, metal=0.6)
    H = 0.42
    for k in range(3):
        ang = R(90 + 120 * k)
        P.tube(f"{nombre}_pata{k}", [(0, 0, H), (0.10 * math.cos(ang) * 0.5, 0.10 * math.sin(ang) * 0.5, H * 0.5), (0.13 * math.cos(ang), 0.13 * math.sin(ang), 0.0)], 0.006, coll, gris).parent = root
    cuerpo = P.prim("cube", nombre + "_cuerpo", coll, negro)
    cuerpo.scale = (0.07, 0.13, 0.08)
    cuerpo.location = (0, 0, H + 0.045)
    P.bevel(cuerpo, 0.008, 3)
    cuerpo.parent = root
    lente = P.prim("cyl", nombre + "_lente", coll, negro, r=0.028, r2=0.032, h=0.06, seg=40)
    lente.rotation_euler = (R(90), 0, 0)
    lente.location = (0, -0.09, H + 0.045)
    lente.parent = root
    vidrio = P.prim("cyl", nombre + "_vidrio", coll, P.mat("CamVidrio", (0.05, 0.08, 0.12), rough=0.02, coat=1.0), r=0.024, r2=0.024, h=0.004, seg=40)
    vidrio.rotation_euler = (R(90), 0, 0)
    vidrio.location = (0, -0.121, H + 0.045)
    vidrio.parent = root
    led_m = P.mat("CamLed", (1.0, 0.04, 0.03), rough=0.2, emit=0.0)
    led = P.prim("sphere", nombre + "_led", coll, led_m, r=0.006)
    led.location = (0.022, -0.06, H + 0.088)
    led.parent = root
    d = Vector(mira) - Vector(loc)
    root.rotation_euler.z = math.atan2(d.x, -d.y)
    return root, led_m


def p18(sc, a, b):
    """¿Por qué? En Arizona: toma aérea del desierto de Sonora al atardecer; grúa que baja."""
    S = _desierto(sc)
    _chiltepin(S)
    cam = E2.camara(sc, "Cam18", lens=28)
    p0, p1 = Vector((-0.6, -5.5, 3.6)), Vector((-1.0, -3.6, 0.55))
    t0, t1 = Vector((0.2, 4.0, 0.0)), Vector((-0.4, 2.0, 0.45))

    def act(f):
        x = E2.suave2(lin(f, a, b - 1))
        E2.mirar(cam, p0.lerp(p1, x), t0.lerp(t1, x))
    return {"actualizar": act}


def p19(sc, a, b):
    """científicos filmaron un chiltepín: una cámara de video en trípode frente a la mata; se enciende la luz roja."""
    S = _desierto(sc)
    mata, fr = _chiltepin(S)
    vc, led = videocamara("Videocamara", S["CP"], MATA + Vector((0.20, -0.62, 0)), MATA + Vector((0, 0, 0.2)))
    cam = E2.camara(sc, "Cam19", lens=30, fstop=8)
    pos = MATA + Vector((1.05, -1.60, 0.50))
    tgt = MATA + Vector((0.12, -0.42, 0.28))
    f_rec = a + 18

    def act(f):
        e = led.node_tree.nodes["Principled BSDF"]
        e.inputs["Emission Color"].default_value = (1.0, 0.04, 0.03, 1)
        e.inputs["Emission Strength"].default_value = 0.0 if f < f_rec else 6.0 * suave(lin(f, f_rec, f_rec + 4))
        E2.empujar(cam, f, a, b - 1, pos, tgt, cuanto=0.08, foco=MATA + Vector((0, 0, 0.2)))
        bpy.context.view_layer.update()
        return {"mata": E2.pantalla(sc, cam, MATA + Vector((0, 0, 0.40)))}
    return {"actualizar": act}


def p20(sc, a, b):
    """un ají silvestre: frutitos rojos y redondos en la rama, se mecen; macro con foco que se corre."""
    S = _desierto(sc, piedritas=False)
    mata, fr = _chiltepin(S, frutos=40)
    bpy.context.view_layer.update()
    pts = sorted([f_.matrix_world.translation.copy() for f_ in fr], key=lambda p: -p.z)
    f1 = pts[0]
    f2 = min(pts[1:], key=lambda p: abs((p - f1).length - 0.045))
    cam = E2.camara(sc, "Cam20", lens=85, fstop=5.0)        # puerta 6 r1: con f/2 todo quedaba borroso
    mid = (f1 + f2) / 2
    pos = mid + Vector((0.05, -0.36, 0.02))
    ramas = [o for o in mata.children]
    base = {o.name: o.rotation_euler.copy() for o in ramas}

    def act(f):
        for k, o in enumerate(ramas):
            r0 = base[o.name]
            o.rotation_euler = Euler((r0.x + R(1.6) * E2.ruido(f, k, 1.2), r0.y + R(1.2) * E2.ruido(f, k + 40, 1.0), r0.z))
        x = suave(lin(f, a + 6, b - 8))
        cam.data.dof.focus_distance = (f1.lerp(f2, x) - pos).length
        E2.mirar(cam, pos, mid)
        cam.data.dof.focus_distance = (f1.lerp(f2, x) - pos).length
    return {"actualizar": act}


def _cam_rec(sc):
    """La vista de la cámara de vigilancia de los científicos (fija) para los planos 21 y 22.
    Puerta 6 r1: las cabezas de los roedores y el pájaro caían en la franja de subtítulos → la cámara mira más abajo y
    más cerca, y lo que pasa queda en la mitad de arriba del cuadro."""
    cam = E2.camara(sc, "CamREC", lens=float(os.environ.get("REC_LENS", 32)), fstop=11)
    E2.mirar(cam, MATA + Vector(tuple(float(v) for v in os.environ.get("REC_POS", "0.25,-0.95,0.40").split(","))),
             MATA + Vector(tuple(float(v) for v in os.environ.get("REC_TGT", "-0.02,0.05,-0.03").split(","))))
    return cam


def _rata(S):
    return PJ.raton(S["CP"], nombre="Rata", lomo=(0.30, 0.29, 0.28), guata=(0.72, 0.70, 0.68), oreja=0.018, hocico=1.25)


def _salto(f, f0, paso=7, alto=0.018):
    """Altura de un saltito de roedor (cuadros por salto = paso)."""
    if f < f0:
        return 0.0
    ph = ((f - f0) % paso) / paso
    return alto * math.sin(math.pi * ph)


def p21(sc, a, b):
    """Ratones y ratas ni lo tocaban: vista REC; el ratón y la rata se acercan, huelen la mata y se van."""
    S = _desierto(sc)
    _chiltepin(S)
    cam = _cam_rec(sc)
    rata = _rata(S)
    rata["root"].scale = (1.45, 1.45, 1.45)
    rat = PJ.raton(S["CP"], nombre="RatonREC")
    rat["root"].scale = (1.15, 1.15, 1.15)
    for r_ in (rata, rat):
        for k, br in enumerate(r_["brazos"]):
            br.rotation_euler = (R(-5), 0, 0)
    n = b - a
    # caminos: entran desde los lados, llegan junto a la mata, huelen, se dan vuelta y se van
    caminos = {
        "rat": (MATA + Vector((0.23, -0.16, 0)), MATA + Vector((0.13, -0.10, 0))),       # puerta 6 r1: en cuadro desde el inicio
        "rata": (MATA + Vector((-0.27, -0.22, 0)), MATA + Vector((-0.16, -0.14, 0))),
    }

    def mover(r_, cm, f, f0, f_llega, f_vuelta, f_sale):
        ini, fin = cm
        d = (fin - ini)
        ang_ida = math.atan2(d.x, -d.y)
        if f <= f_llega:
            x = suave(lin(f, f0, f_llega))
            p = ini.lerp(fin, x)
            z = _salto(f, f0) if x < 0.98 else 0
            ang = ang_ida
        elif f <= f_vuelta:
            p, z, ang = fin, 0, ang_ida
        else:
            x = suave(lin(f, f_vuelta + 6, f_sale))
            p = fin.lerp(ini, x)
            z = _salto(f, f_vuelta + 6) if 0.02 < x < 1 else 0
            ang = ang_ida + math.pi * suave(lin(f, f_vuelta, f_vuelta + 6))
        r_["root"].location = p + Vector((0, 0, z))
        r_["root"].rotation_euler.z = ang
        # huelen: la cabeza se estira hacia la mata y el hocico tiembla
        olfa = suave(lin(f, f_llega, f_llega + 5)) * (1 - suave(lin(f, f_vuelta - 4, f_vuelta)))
        r_["cabeza"].rotation_euler = (R(18 * olfa + 3 * olfa * math.sin(f * 1.7)), 0, 0)
        r_["root"].rotation_euler.x = R(10 * olfa)

    def act(f):
        mover(rat, caminos["rat"], f, a, a + int(n * 0.30), a + int(n * 0.58), b + 10)
        mover(rata, caminos["rata"], f, a + 4, a + int(n * 0.36), a + int(n * 0.62), b + 14)
    return {"actualizar": act}


def p22(sc, a, b):
    """Los pájaros se lo devoraban: vista REC; el cuitlacoche ya está posado y se traga dos frutitos enteros, uno tras
    otro, sin masticar (cada uno se suelta de su tallito en la punta del pico y entra de un trago)."""
    S = _desierto(sc)
    mata, fr = _chiltepin(S)
    cam = _cam_rec(sc)
    pj = PJ.pajaro(S["CP"], nombre="CuitREC")
    pj["root"].scale = (1.0, 1.0, 1.0)
    pj["root"].location = MATA + Vector((0.10, -0.16, 0))        # puerta 6 r1: más junto a la mata
    pj["root"].rotation_euler.z = R(-75)
    # puerta 6 r1: a contraluz se veía casi negro → relleno cálido desde el lado de la cámara
    E2.area(sc, "RellenoPajaroREC", tuple(MATA + Vector((0.30, -0.70, 0.45))), 10, 0.6, (1.0, 0.92, 0.82), tuple(pj["root"].location + Vector((0, 0, 0.10))))
    for pv in pj["parpados"]:
        for ch in pv.children:
            ch.rotation_euler.x = R(-30)
    bulto = AP.Bulto(pj, S["CP"])
    bpy.context.view_layer.update()
    # dos frutitos que cuelgan de una ramita delante del pico (en la pose de picar)
    cab0 = pj["cabeza"].rotation_euler.copy()
    pj["cabeza"].rotation_euler = Euler((R(18), 0, R(14)))
    bpy.context.view_layer.update()
    punta = pj["pico"].matrix_world @ Vector((0, -0.068, -0.012))
    pj["cabeza"].rotation_euler = cab0
    fm = E.mat_aji()
    tallo_m = P.mat("TalloChiltepin", (0.20, 0.17, 0.07), rough=0.7)
    frutos = []
    for k in range(2):
        p_ = punta + Vector((0.004 * k, -0.002, 0.004 * k))
        fo = P.prim("sphere", f"FrutoREC{k}", S["CP"], fm, r=0.0068, u=24, v=12)
        fo.scale = (1, 1, 1.2)
        fo.location = p_
        P.tube(f"TallitoREC{k}", [tuple(p_ + Vector((0, 0, 0.006))), tuple(p_ + Vector((-0.01, 0.01, 0.03))), tuple(p_ + Vector((-0.03, 0.03, 0.05)))], 0.0012, S["CP"], tallo_m)
        frutos.append((fo, p_))
    n = b - a
    tomas = [a + 3, a + int(n * 0.52)]

    def act(f):
        cab = Euler((cab0.x, cab0.y, cab0.z))
        bul = None
        for k, (fo, p0) in enumerate(frutos):
            t0 = tomas[k]
            x = (f - t0) / (n * 0.42)
            # pica (0–0,25) → traga con la cabeza hacia arriba (0,25–0,7) → vuelve (0,7–1)
            # puerta 6 r1: el fruto se esfumaba → lo arranca, lo sostiene en la punta ~7 cuadros y lo traga echando la cabeza atrás
            pica = suave(lin(x, 0.0, 0.18)) * (1 - suave(lin(x, 0.38, 0.50)))
            tr = AP.trago(lin(x, 0.40, 0.95))
            if 0 <= x <= 1:
                cab = Euler((cab0.x + R(18) * pica - R(16) * tr, 0, cab0.z + R(14) * pica))
            pj["cabeza"].rotation_euler = cab
            pj["mandibula"].rotation_euler.x = R(14) * pica + R(6) * tr
            bpy.context.view_layer.update()
            boca = pj["pico"].matrix_world @ Vector((0, -0.010, -0.004))
            pt = pj["pico"].matrix_world @ Vector((0, -0.066, -0.012))
            if x < 0.18:
                fo.location = p0
                fo.hide_render = False
            elif x < 0.52:
                fo.location = pt.lerp(boca, suave(lin(x, 0.40, 0.52)))      # en la punta del pico y después adentro
                fo.hide_render = False
            else:
                fo.hide_render = True                       # ya entró al pico (de un trago)
            if 0.50 <= x <= 1.0:
                bul = lin(x, 0.50, 1.0)
        bulto.poner(bul if bul is not None else 0)
    return {"actualizar": act}


def p25(sc, a, b):
    """y salen en su caca listas para brotar: cae una caquita blanca con semillas y, en cámara rápida, brota una mata chica con flores."""
    S = _desierto(sc, piedritas=False)
    base = MATA + Vector((0.55, -0.30, 0))
    caca_m = P.mat("Caca", (0.93, 0.92, 0.88), rough=0.6)
    caca = PJ.blob("Caca", [((0, 0, 0.006), (0.016, 0.013, 0.007), (0, 0, 0)), ((0.004, 0.002, 0.011), (0.009, 0.008, 0.006), (0, 0, 0))], S["CP"], voxel=0.0006, suave=6)
    caca.data.materials.append(caca_m)
    caca.location = base
    # puerta 6 r1 (fondo liso 41,4–42,5 s): suelo con piedritas y ramitas en foco alrededor de la caca
    rr = random.Random(25)
    pied = P.mat("Piedrita25", (0.55, 0.30, 0.16), rough=0.8)
    for k in range(150):
        dx, dy = rr.uniform(-0.18, 0.18), rr.uniform(-0.18, 0.14)
        if abs(dx) < 0.03 and abs(dy) < 0.03:
            continue
        pz = P.prim("ico", f"Piedrita25_{k}", S["CP"], pied, r=rr.uniform(0.0018, 0.0060), sub=2)
        pz.scale = (1, rr.uniform(0.7, 1.3), rr.uniform(0.5, 0.8))
        pz.location = base + Vector((dx, dy, pz.scale.z * 0.003))
    rama_m = P.mat("Ramita25", (0.36, 0.24, 0.13), rough=0.8)
    for k in range(7):
        x0 = base + Vector((rr.uniform(-0.14, 0.14), rr.uniform(-0.10, 0.10), 0.0015))
        if (x0 - base).length < 0.04:
            continue
        ang = rr.uniform(0, math.pi)
        L_ = rr.uniform(0.03, 0.06)
        x1 = x0 + Vector((math.cos(ang) * L_, math.sin(ang) * L_, 0.0))
        P.tube(f"Ramita25_{k}", [tuple(x0), tuple((x0 + x1) / 2 + Vector((0, 0, 0.002))), tuple(x1)], 0.0011, S["CP"], rama_m)
    sem = P.mat("SemillaAjiCaca", (0.92, 0.80, 0.45), rough=0.5)
    semillas = []
    for k, (dx, dy) in enumerate(((0.008, -0.010), (-0.006, -0.011), (0.0, -0.012))):
        g = P.prim("cyl", f"SemillaCaca{k}", S["CP"], sem, r=0.0024, r2=0.0024, h=0.0007, seg=20)
        g.location = (dx, dy, 0.008)
        g.rotation_euler = (R(80), 0, R(20 * k))
        g.parent = caca
        semillas.append(g)
    # brote: tallo (curva que crece), hojas y flores blancas
    verde = P.mat("Brote", (0.12, 0.40, 0.08), rough=0.5)
    tallo_pts = [base + Vector((0.002, -0.006, 0.006)), base + Vector((0.004, -0.008, 0.05)), base + Vector((-0.004, -0.006, 0.10)), base + Vector((0.002, -0.004, 0.15))]
    tallo = P.tube("BroteTallo", [tuple(p_) for p_ in tallo_pts], 0.0022, S["CP"], verde)

    def en_tallo(z):
        """Punto del tallo a la altura z (interpolación lineal entre sus puntos)."""
        for p_, q_ in zip(tallo_pts, tallo_pts[1:]):
            if p_.z <= base.z + z <= q_.z:
                return p_.lerp(q_, (base.z + z - p_.z) / max(1e-6, q_.z - p_.z))
        return tallo_pts[-1].copy()
    tallo.data.bevel_factor_mapping_end = "SPLINE"
    hojas, flores = [], []
    hm = P.mat("BroteHoja", (0.10, 0.36, 0.07), rough=0.45, sss=0.1)
    fl = P.mat("FlorChiltepin", (0.97, 0.96, 0.92), rough=0.5)
    for k in range(6):          # puerta 6 r1: las hojas flotaban separadas del tallo → nacen en el tallo (la base en el tallo)
        z = 0.035 + 0.02 * k
        sg = 1 if k % 2 else -1
        h = P.prim("sphere", f"BroteHoja{k}", S["CP"], hm, r=1.0, u=16, v=8)
        h.location = en_tallo(z) + Vector((sg * 0.0115, 0, 0.0066))      # centro a medio largo de la hoja, que sale en diagonal
        h.rotation_euler = (0, R(60 * sg), 0)
        hojas.append((h, k))
    centro = P.mat("FlorCentro", (0.95, 0.75, 0.15), rough=0.5)
    for k in range(4):
        zf = 0.112 + 0.012 * k
        pf = en_tallo(zf) + Vector((0.008 * math.cos(k * 1.7), -0.004, 0.006))
        ped = P.tube(f"Pedicelo{k}", [tuple(en_tallo(zf - 0.004)), tuple(pf)], 0.0008, S["CP"], verde)
        fo = P.empty(f"Flor{k}", loc=pf, coll=S["CP"])
        fo["ped"] = ped.name
        fo.rotation_euler = (R(78), 0, R(-10 + 8 * k))      # la flor mira a cámara (revisión: de canto se leían como platillos grises)
        for j in range(5):
            pe = P.prim("sphere", f"Flor{k}_p{j}", S["CP"], fl, r=0.0036, u=12, v=6)
            pe.scale = (1, 0.55, 0.25)
            pe.location = (0.0040 * math.cos(j * 1.2566), 0.0040 * math.sin(j * 1.2566), 0)
            pe.rotation_euler = (0, 0, j * 1.2566)
            pe.parent = fo
        cc = P.prim("sphere", f"Flor{k}_c", S["CP"], centro, r=0.0016, u=12, v=6)
        cc.location = (0, 0, 0.0006)
        cc.parent = fo
        flores.append((fo, k))
    cam = E2.camara(sc, "Cam25", lens=60, fstop=7.0)
    # revisión del borrador: arrancaba con el cuadro vacío (la caca caía fuera de cuadro); ahora la caca cae en cuadro y la
    # cámara sube con el brote hasta encuadrar la mata entera con flores
    pos = base + Vector((0.04, -0.26, 0.07))
    tgt = base + Vector((0, 0, -0.022))          # puerta 6 r1: la caca caía detrás del subtítulo
    sube = Vector((0, 0, 0.088))
    n = b - a

    def act(f):
        x = (f - a) / n
        cae = lin(x, 0.0, 0.10)
        aplasta = math.exp(-max(0, x - 0.10) * 40) if x > 0.10 else 0
        caca.location = base + Vector((0, 0, 0.016 * (1 - entra(cae))))      # cae poquito: ya está en cuadro en el primer cuadro
        caca.scale = (1 + 0.35 * aplasta, 1 + 0.35 * aplasta, 1 - 0.45 * aplasta)
        crece = E2.suave(lin(x, 0.17, 0.92))
        tallo.data.bevel_factor_end = max(0.001, crece)
        tallo.hide_render = crece < 0.01
        for h, k in hojas:
            s_ = 0.012 * sale(lin(crece, 0.12 + 0.11 * k, 0.30 + 0.11 * k))
            h.scale = (s_, s_ * 0.45, s_ * 0.08)
            h.hide_render = s_ < 1e-4
        for fo, k in flores:
            s_ = sale(lin(crece, 0.82 + 0.03 * k, 0.97 + 0.01 * k))
            fo.scale = (s_, s_, s_)
            for ch in fo.children:
                ch.hide_render = s_ < 0.01
            bpy.data.objects[fo["ped"]].hide_render = s_ < 0.01
        caca.scale = caca.scale * (1 - 0.35 * suave(lin(x, 0.4, 0.9)))   # se va deshaciendo mientras brota
        k_ = E2.suave(lin(x, 0.22, 0.95))
        foco = tgt + sube * k_ * 0.6
        atras = Vector((-0.02, -0.30, 0.0)) * k_          # se abre para ver la mata entera con la caca abajo
        E2.empujar(cam, f, a, b - 1, pos + sube * k_ + atras, tgt + sube * k_, cuanto=0.03, foco=foco)
    return {"actualizar": act}


def poste_cuerda(nombre, coll, p0, p1, alto=0.20):
    """Dos postes cromados con una cuerda roja entre ellos (la entrada del "guardia"). Devuelve la curva de la cuerda."""
    cromo = P.mat("Cromo", (0.85, 0.85, 0.88), rough=0.12, metal=1.0)
    for k, p in enumerate((p0, p1)):
        b = P.prim("cyl", f"{nombre}_base{k}", coll, cromo, r=0.04, r2=0.035, h=0.012, seg=32)
        b.location = Vector(p) + Vector((0, 0, 0.006))
        t = P.prim("cyl", f"{nombre}_poste{k}", coll, cromo, r=0.008, r2=0.008, h=alto, seg=24)
        t.location = Vector(p) + Vector((0, 0, alto / 2))
        bo = P.prim("sphere", f"{nombre}_bola{k}", coll, cromo, r=0.014)
        bo.location = Vector(p) + Vector((0, 0, alto + 0.01))
    terc = P.mat("Terciopelo", (0.55, 0.02, 0.05), rough=0.6, sheen=0.0) if False else P.mat("Terciopelo", (0.55, 0.02, 0.05), rough=0.6)
    a, b = Vector(p0) + Vector((0, 0, alto - 0.01)), Vector(p1) + Vector((0, 0, alto - 0.01))
    cu = P.tube(f"{nombre}_cuerda", [tuple(a), tuple(a.lerp(b, 0.33) + Vector((0, 0, -0.05))), tuple(a.lerp(b, 0.66) + Vector((0, 0, -0.05))), tuple(b)], 0.006, coll, terc)
    return cu, a, b


def _poner_cuerda(cu, a, b, comba):
    """comba = cuánto cuelga la cuerda (m); 0 = tensa."""
    pts = cu.data.splines[0].points
    for k, pt in enumerate(pts):
        t = k / (len(pts) - 1)
        p = a.lerp(b, t) + Vector((0, 0, -comba * math.sin(math.pi * t)))
        pt.co = (*p, 1)


def _entrada(S):
    """La entrada del guardia junto a la mata: dos postes con cuerda y el ají guardia."""
    p0 = MATA + Vector((0.30, -0.25, 0))
    p1 = MATA + Vector((0.30, 0.20, 0))
    cu, ca, cb = poste_cuerda("Entrada", S["CP"], p0, p1)
    g = PJ.aji_guardia(S["CP"])
    g["root"].location = MATA + Vector((0.20, -0.42, 0))
    g["root"].rotation_euler.z = R(10)
    return cu, ca, cb, g


def p26(sc, a, b):
    """Los científicos creen que el picante es un guardia: en "picante" el ají guardia aterriza de un salto en su puesto
    junto a la entrada; en "guardia" se enciende una luz de discoteca sobre él."""
    S = _desierto(sc)
    _chiltepin(S)
    cu, ca, cb, g = _entrada(S)
    _poner_cuerda(cu, ca, cb, 0.06)
    pos_g = g["root"].location.copy()
    t_pic = E2.F(E2.t_palabra("picante", E2.T[26][0]))
    t_gua = E2.F(E2.t_palabra("guardia", E2.T[26][0]))
    disco = bpy.data.lights.new("Disco", "SPOT")
    disco.spot_size, disco.spot_blend, disco.energy = R(28), 0.3, 0.0
    do = bpy.data.objects.new("Disco", disco)
    S["CP"].objects.link(do)
    do.location = pos_g + Vector((0, 0, 1.1))
    do.rotation_euler = (0, 0, 0)
    bola_m = P.mat("BolaDisco", (0.9, 0.9, 0.95), rough=0.05, metal=1.0)
    bola = P.prim("ico", "BolaDisco", S["CP"], bola_m, r=0.05, sub=2)
    bola.location = pos_g + Vector((0, 0, 0.62))
    P.tube("BolaDiscoCable", [tuple(bola.location + Vector((0, 0, 0.05))), tuple(bola.location + Vector((0, 0, 0.4))), tuple(bola.location + Vector((0, 0, 0.8)))], 0.0015, S["CP"], P.mat("Cable", (0.05, 0.05, 0.05)))
    # puerta 6 r1: la bola de discoteca cortada arriba se leía como un objeto suelto → fuera (queda la luz de discoteca)
    bola.hide_render = True
    bpy.data.objects["BolaDiscoCable"].hide_render = True
    lt0 = g["lentes"].location.copy()
    cab0g = g["cabeza"].rotation_euler.copy()
    cam = E2.camara(sc, "Cam26", lens=30, fstop=8)
    pos = pos_g + Vector((-0.20, -0.95, 0.06))
    tgt = pos_g + Vector((0.0, 0.10, 0.26))

    def act(f):
        # salto: cae desde arriba fuera de cuadro y aterriza en t_pic (aplasta y se estira)
        dt = (f - t_pic) / E2.FPS
        if dt < 0:
            h = 0.9 * min(1.0, (-dt / 0.35)) ** 2
        else:
            h = 0.0
        sq = math.exp(-max(0, dt) * 6) * math.cos(max(0, dt) * 20) if dt >= 0 else 0       # aplasta y estira más largo
        st = 0.12 * math.exp(-((dt + 0.06) / 0.05) ** 2) if dt < 0 else 0.0                  # se estira al caer
        g["root"].location = pos_g + Vector((0, 0, h))
        g["root"].scale = (1 + 0.26 * sq - st * 0.5, 1 + 0.26 * sq - st * 0.5, 1 - 0.32 * sq + st)
        # en "guardia" se acomoda los lentes (suben y bajan) y asiente serio
        dg = (f - t_gua) / E2.FPS
        ac = math.sin(math.pi * E2.clamp(dg / 0.35)) if 0 <= dg <= 0.35 else 0.0
        g["lentes"].location = lt0 + Vector((0, 0, 0.012 * ac))
        g["cabeza"].rotation_euler = Euler((cab0g.x + R(8) * ac, cab0g.y, cab0g.z))
        on = suave(lin(f, t_gua, t_gua + 3))
        disco.energy = 220 * on
        disco.color = (1.0, 0.35 + 0.3 * math.sin(f * 0.5), 0.9)
        bola.rotation_euler.z = f * 0.12
        bola_m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.0
        E2.empujar(cam, f, a, b - 1, pos, tgt, cuanto=0.18, foco=pos_g + Vector((0, 0, 0.2)))     # puerta 6 r1: push-in más marcado
    return {"actualizar": act}


def p27(sc, a, b):
    """Espanta a los que destruyen semillas: llega el ratón, la cuerda sube sola como barrera, el guardia niega con la
    cabeza sin descruzar los brazos y el ratón se da vuelta y se va (paneo)."""
    S = _desierto(sc)
    _chiltepin(S)
    cu, ca, cb, g = _entrada(S)
    rat = PJ.raton(S["CP"], nombre="Raton27")
    rat["root"].scale = (1.15, 1.15, 1.15)
    for br in rat["brazos"]:
        br.rotation_euler = (R(-5), 0, 0)
    ini = MATA + Vector((0.95, -0.55, 0))
    fin = MATA + Vector((0.50, -0.38, 0))
    cam = E2.camara(sc, "Cam27", lens=32, fstop=8)
    n = b - a
    pg = g["root"].location.copy()

    def act(f):
        x = (f - a) / n
        # el ratón llega (0–0,3), espera (–0,7), se da vuelta y se va (0,7–1)
        d = fin - ini
        ang = math.atan2(d.x, -d.y)
        if x < 0.30:
            p = ini.lerp(fin, suave(lin(x, 0, 0.30)))
            z = _salto(f, a)
        elif x < 0.70:
            p, z = fin, 0
        else:
            p = fin.lerp(ini, suave(lin(x, 0.76, 1.0)))
            z = _salto(f, a + int(n * 0.76)) if x > 0.76 else 0
            ang += math.pi * suave(lin(x, 0.70, 0.76))
        rat["root"].location = p + Vector((0, 0, z))
        rat["root"].rotation_euler.z = ang
        # la cuerda sube sola (de colgando a tensa) cuando llega el ratón
        _poner_cuerda(cu, ca, cb, 0.10 * (1 - sale(lin(x, 0.30, 0.42))))
        # el guardia niega con la cabeza (brazos cruzados siempre)
        neg = math.sin(lin(x, 0.42, 0.68) * math.pi * 4) * math.sin(math.pi * lin(x, 0.42, 0.68))
        inc = math.sin(math.pi * lin(x, 0.40, 0.74))          # se inclina hacia el ratón (patovica) mientras niega
        g["cabeza"].rotation_euler = (R(6) * inc, 0, R(18) * neg)
        g["root"].rotation_euler.x = R(-9) * inc
        # paneo de la llegada del ratón al guardia
        tgt = (fin.lerp(pg, 0.5 * suave(lin(x, 0.2, 0.6)))) + Vector((-0.17, 0, 0.16))      # puerta 6 r1: el guardia entero y la mata detrás
        E2.mirar(cam, MATA + Vector((0.22, -1.75, 0.27)), tgt, foco=fin + Vector((0, 0, 0.1)))
    return {"actualizar": act}


def p28a(sc, a, b):
    """Y lo más loco: barrido rápido (whip) que sale del desierto (la otra mitad entra al bosque: p28b)."""
    S = _desierto(sc)
    _chiltepin(S)
    cam = E2.camara(sc, "Cam28a", lens=32)
    p = MATA + Vector((0.40, -1.55, 0.25))

    def act(f):
        x = entra(lin(f, a, b))
        ang = R(-75) * x
        d = Vector((math.sin(ang) * 1.0 - 0.0, math.cos(ang) * 1.0, -0.05))
        E2.mirar(cam, p, p + d)
    return {"actualizar": act}


# =====================================================================================================
# leche, estudio y bebida con gas (35–37)
# =====================================================================================================
def ardorometro(nombre, coll, loc, alto=0.12):
    """Tubo de vidrio con la misma llama del video adentro, a escala. Devuelve (raíz, Llama)."""
    root = P.empty(nombre, loc=loc, coll=coll)
    vidrio = P.mat("VidrioArdor", (0.95, 0.97, 1.0), rough=0.03, transmission=1.0)
    vidrio.node_tree.nodes["Principled BSDF"].inputs["IOR"].default_value = 1.12     # puerta 6 r1: con 1,45 la llama se veía como un garabato
    tubo = P.prim("cyl", nombre + "_tubo", coll, vidrio, r=0.022, r2=0.022, h=alto, seg=40)
    tubo.location = (0, 0, alto / 2 + 0.008)
    sol = tubo.modifiers.new("Grosor", "SOLIDIFY")
    sol.thickness = 0.0015
    tubo.parent = root
    base = P.prim("cyl", nombre + "_base", coll, P.mat("BaseArdor", (0.12, 0.12, 0.13), rough=0.4, metal=0.5), r=0.028, r2=0.028, h=0.010, seg=40)
    base.location = (0, 0, 0.005)
    base.parent = root
    tapa = P.prim("cyl", nombre + "_tapa", coll, P.mat("BaseArdor", (0.12, 0.12, 0.13)), r=0.025, r2=0.025, h=0.006, seg=40)
    tapa.location = (0, 0, alto + 0.011)
    tapa.parent = root
    bpy.context.view_layer.update()
    ll = AP.Llama(nombre + "_llama", Vector(loc) + Vector((0, 0, 0.012)), Vector((0, 0, 1)), coll, escala=0.62)
    for ch in ll.root.children:
        if "_chispa" in ch.name:
            ch.hide_render = True
    return root, ll


def _mesa_leche(S, x0=-0.12, y0=-0.18):
    """Lugar en la roca principal para los vasos de los planos 35–37."""
    return Vector((x0, y0, S["suelo"](x0, y0)))


def p35(sc, a, b):
    """En un estudio con 72 personas: sobre la roca aparecen 72 vasitos en grilla, en ola; un contador sube a 72."""
    S = _desierto(sc, piedritas=False)
    c = _mesa_leche(S, 0.0, -0.30)
    m = P.mat("Vasito", (0.97, 0.97, 0.96), rough=0.35)
    lm = P.mat("LecheVasito", (0.95, 0.94, 0.90), rough=0.3)
    vasos = []
    filas, cols, paso = 8, 9, 0.046
    for i_ in range(filas):
        for j in range(cols):
            x = c.x + (j - (cols - 1) / 2) * paso
            y = c.y + (i_ - (filas - 1) / 2) * paso
            z = S["suelo"](x, y)
            v = P.prim("cyl", f"Vasito{i_}_{j}", S["CP"], m, r=0.016, r2=0.013, h=0.032, seg=24)
            v.rotation_euler = (R(180), 0, 0)
            v.location = (x, y, z + 0.016)
            l = P.prim("cyl", f"VasitoLeche{i_}_{j}", S["CP"], lm, r=0.0145, r2=0.0145, h=0.002, seg=24)
            l.location = (0, 0, -0.012)
            l.parent = v
            vasos.append((v, (filas - 1 - i_) + j, Vector((x, y, z + 0.016))))
    n = b - a
    cam = E2.camara(sc, "Cam35", lens=30, fstop=11)
    p0, p1 = c + Vector((-0.10, -0.75, 0.12)), c + Vector((-0.05, -0.55, 0.62))
    tgt = c + Vector((0, 0.02, 0.0))
    orden = sorted(vasos, key=lambda t: t[1])

    def act(f):
        x = (f - a) / n
        cuenta = 0
        for idx, (v, k, loc) in enumerate(orden):
            t0 = 0.05 + 0.60 * idx / len(orden)
            sx = E2.rebote(lin(x, t0, t0 + 0.07), 2.0)
            v.scale = (max(1e-3, sx),) * 3
            v.hide_render = sx < 0.02
            for ch in v.children:
                ch.hide_render = sx < 0.02
            if x >= t0 + 0.02:
                cuenta += 1
        E2.mirar(cam, p0.lerp(p1, E2.suave2(x)), tgt, foco=tgt)
        return {"cuenta": cuenta}
    return {"actualizar": act}


def p36(sc, a, b):
    """fue de lo que más bajó el ardor: dos vasos de leche con su cajita (ENTERA y DESCREMADA) y un ardorómetro junto a
    cada uno; las dos llamas bajan casi igual y quedan chicas (no llegan a cero)."""
    S = _desierto(sc, piedritas=False)
    c = _mesa_leche(S, -0.05, -0.32)
    cosas = []
    for k, (txt, col) in enumerate((("ENTERA", (0.15, 0.40, 0.90)), ("DESCREMADA", (0.25, 0.65, 1.0)))):
        x = c.x + (k - 0.5) * 0.19
        z = S["suelo"](x, c.y)
        v = E.vaso_leche(f"Vaso36_{k}", S["CP"], alto=0.085, r=0.032, nivel=0.8)
        v.location = (x, c.y, z - 0.001)
        cj = cajita_leche(f"Caja36_{k}", txt, S["CP"], color=col)
        cj.location = (x - 0.062, c.y + 0.040, S["suelo"](x - 0.062, c.y + 0.040) - 0.001)     # al lado del vaso: se lee la etiqueta
        ar, ll = ardorometro(f"Ardor36_{k}", S["CP"], (x + 0.062, c.y - 0.01, S["suelo"](x + 0.062, c.y - 0.01) - 0.001))
        cosas.append(ll)
    # revisión del borrador: con 30 mm la fila quedaba chica y abajo, tapada por los subtítulos; ahora llena el ancho y
    # queda arriba de la franja de subtítulos (la cámara mira al suelo delante de la fila)
    cam = E2.camara(sc, "Cam36", lens=float(os.environ.get("P36_LENS", 31)), fstop=8)
    pos = c + Vector(tuple(float(v) for v in os.environ.get("P36_POS", "0.0,-0.98,0.34").split(",")))
    tgt = c + Vector(tuple(float(v) for v in os.environ.get("P36_TGT", "0.0,0.0,-0.015").split(",")))
    n = b - a

    def act(f):
        x = (f - a) / n
        for k, ll in enumerate(cosas):
            baja = suave(lin(x, 0.12 + 0.03 * k, 0.72 + 0.03 * k))
            ll.poner(f + 17 * k, 1.0 - 0.72 * baja - 0.02 * k)
        E2.empujar(cam, f, a, b - 1, pos, tgt + Vector((0, 0, 0.04)) * suave(x), cuanto=0.30, foco=tgt)   # puerta 6 r1: push-in a los faroles
    return {"actualizar": act}


def p37(sc, a, b):
    """Las bebidas con gas funcionaron mal: junto a un vaso de bebida con burbujas, el ardorómetro casi no baja."""
    S = _desierto(sc, piedritas=False)
    c = _mesa_leche(S, -0.05, -0.32)
    z = c.z
    v = E.vaso_leche("Vaso37", S["CP"], alto=0.10, r=0.034, nivel=0.85)
    v.location = (c.x - 0.04, c.y, z - 0.001)
    beb = bpy.data.objects["Vaso37_leche"]
    bm = P.mat("BebidaGas", (0.28, 0.07, 0.02), rough=0.05, transmission=0.6)
    beb.data.materials[0] = bm
    rr = random.Random(2)
    burb = []
    # puerta 6 r1: las burbujas transparentes no se veían dentro de la bebida oscura → claras y un poco emisivas, más, y
    # pegadas al vidrio de adelante; espuma arriba
    bmat = P.mat("Burbuja37", (0.98, 0.94, 0.86), rough=0.15, emit=0.45)
    for k in range(48):
        bo = P.prim("sphere", f"Burbuja{k}", S["CP"], bmat, r=rr.uniform(0.0016, 0.0030), u=12, v=6)
        ang = rr.uniform(R(-150), R(-30))          # mitad de adelante del vaso (la cámara mira desde -Y)
        rad = rr.uniform(0.020, 0.030)
        burb.append((bo, Vector((c.x - 0.04 + rad * math.cos(ang), c.y + rad * math.sin(ang), z + 0.006)), rr.uniform(0, 1), rr.uniform(0.6, 1.2)))
    esp = P.prim("cyl", "Espuma37", S["CP"], P.mat("Espuma37", (0.86, 0.72, 0.52), rough=0.6), r=0.031, r2=0.031, h=0.006, seg=40)
    esp.location = (c.x - 0.04, c.y, z + 0.10 * 0.85 - 0.002)
    ar, ll = ardorometro("Ardor37", S["CP"], (c.x + 0.07, c.y - 0.01, S["suelo"](c.x + 0.07, c.y - 0.01) - 0.001))
    cam = E2.camara(sc, "Cam37", lens=40, fstop=7)
    pos = c + Vector((0.015, -0.60, 0.15))       # puerta 6 r1: el ardorómetro quedaba cortado a la derecha y el vaso tocaba el borde
    tgt = c + Vector((0.015, 0.02, 0.060))
    n = b - a

    def act(f):
        x = (f - a) / n
        for bo, p0, ph, vel in burb:
            t = ((f - a) / 40 * vel + ph) % 1
            bo.location = p0 + Vector((0.0015 * math.sin(t * 9 + ph * 6), 0, 0.072 * t))
            bo.hide_render = t > 0.97
        ll.poner(f, 1.0 - 0.14 * suave(lin(x, 0.15, 0.6)) + 0.04 * math.sin(lin(x, 0.6, 1.0) * math.pi))
        E2.empujar(cam, f, a, b - 1, pos, tgt, cuanto=0.05, foco=tgt)
    return {"actualizar": act}


# =====================================================================================================
# el que se cree inmune y el guardia (38, 39)
# =====================================================================================================
def p38(sc, a, b):
    """Mándaselo al que se cree inmune: un ratón con lentes y medalla se pavonea frente a una pila de ajíes sin tocarlos;
    detrás entra de un salto el ají guardia y aterriza con los brazos cruzados, mirándolo. Órbita."""
    S = _desierto(sc)
    c = Vector((0.05, -0.15, S["suelo"](0.05, -0.15)))
    rat = Raton(sc, S, x=c.x + 0.08, y=c.y + 0.02, rot=10, llama=False, lagrimas=False)
    rt = rat.rt
    bpy.context.view_layer.update()
    # lentes de sol puestos y medalla al pecho (rígidos)
    ojos = [o.matrix_world.translation for o in rt["ojos"]]
    centro_ojos = (ojos[0] + ojos[1]) / 2
    M = rt["cabeza"].matrix_world.to_3x3().normalized()
    frente = (M @ Vector((0, -1, 0))).normalized()
    lt = PJ.lentes("LentesInmune", centro_ojos + frente * 0.012, 0.050, S["CP"], mirando=frente)
    PJ.colgar(lt, rt["cabeza"])
    pecho = rt["root"].matrix_world @ Vector((0, -0.036, 0.092))
    md = PJ.medalla("MedallaInmune", pecho + frente * 0.004, 0.012, S["CP"])
    md.rotation_euler = (0, 0, rt["root"].rotation_euler.z)
    PJ.colgar(md, rt["root"])
    # pila de ajíes
    rr = random.Random(4)
    for k in range(13):
        aj = E.aji(f"Pila{k}", largo=rr.uniform(0.08, 0.11), grosor=0.015, coll=S["CP"], seed=20 + k, curva=0.25)
        ang = rr.uniform(0, 6.28)
        r_ = rr.uniform(0, 0.05) * (1 if k < 9 else 0.4)
        x, y = c.x - 0.11 + r_ * math.cos(ang), c.y - 0.02 + r_ * math.sin(ang)
        aj.rotation_euler = (R(90 + rr.uniform(-15, 15)), 0, rr.uniform(0, 6.28))
        aj.location = (x, y, S["suelo"](x, y) + 0.012 + (0.020 if k >= 9 else 0) + (0.012 if k >= 12 else 0))
    g = PJ.aji_guardia(S["CP"])
    pg = Vector((c.x - 0.02, c.y + 0.24, S["suelo"](c.x - 0.02, c.y + 0.24)))
    g["root"].location = pg
    g["root"].rotation_euler.z = R(160)
    t_lle = a + int((b - a) * 0.55)
    cam = E2.camara(sc, "Cam38", lens=32, fstop=6)
    centro = c + Vector((0.045, 0.06, 0.13))        # puerta 6 r1: el ratón arrancaba cortado a la derecha
    n = b - a

    def act(f):
        x = (f - a) / n
        dt = (f - t_lle) / E2.FPS
        # puerta 6 r1: el ratón se quedaba igual cuando caía el guardia → 0,15 s después del golpe salta del susto, se le
        # abren los ojos y gira la cabeza hacia el ají; deja de pavonearse
        su = suave(lin(dt, 0.15, 0.40))
        pav = math.sin((f - a) * 0.35) * (1 - su)
        bpy.context.view_layer.update()
        mira_g = AP.mirar_a(rt["cabeza"], g["root"].matrix_world @ Vector((0, 0, 0.12)), 0.8 * su, limite=70)
        rat.pose(cab=(-12 * (1 - su) + 3 * pav + math.degrees(mira_g.x) * su, 0, 10 * pav + math.degrees(mira_g.z) * su),
                 cuerpo=-8 * (1 - su), giro=8 * pav + 25 * su, ojos=-80 - 35 * su, ojos_esc=1 + 0.25 * E2.rebote(lin(dt, 0.15, 0.45)), f=f)
        salto = math.sin(math.pi * lin(dt, 0.15, 0.42)) if 0.15 <= dt <= 0.42 else 0.0
        rt["root"].location.z = c.z + 0.004 * abs(math.sin((f - a) * 0.35)) * (1 - su) + 0.035 * salto
        h = 0.8 * min(1.0, (-dt / 0.3)) ** 2 if dt < 0 else 0.0
        sq = math.exp(-max(0, dt) * 10) * math.cos(max(0, dt) * 26) if dt >= 0 else 0
        g["root"].location = pg + Vector((0, 0, h))
        resp = 0.012 * math.sin(max(0.0, dt) * 5.0) * suave(lin(dt, 0.3, 0.6))      # ya parado: respira y se inclina hacia él
        g["root"].scale = (1 + 0.18 * sq - resp * 0.5, 1 + 0.18 * sq - resp * 0.5, 1 - 0.25 * sq + resp)
        g["root"].rotation_euler.x = R(-7) * suave(lin(dt, 0.35, 0.8))
        ang = R(-25 + 45 * suave(x))         # puerta 6 r1: arrancaba con el ratón pegado al borde derecho
        p = centro + Vector((math.sin(ang) * 0.75, -math.cos(ang) * 0.75, 0.10))
        E2.mirar(cam, p, centro, foco=centro)
    return {"actualizar": act}


def p39(sc, a, b):
    """Para el ají...: los lentes del guardia se deslizan por su cara hasta toparse con el bultito de nariz y asoman los
    ojos serios por encima; brazos cruzados todo el plano."""
    S = _desierto(sc)
    c = Vector((0.0, -0.20, S["suelo"](0.0, -0.20)))
    g = PJ.aji_guardia(S["CP"])
    g["root"].location = c
    g["root"].rotation_euler.z = R(8)
    bpy.context.view_layer.update()
    alto = g["alto"]
    cara = g["root"].matrix_world @ Vector((0, -alto * 0.17, alto * 0.78))
    lent = g["lentes"]
    l0 = lent.location.copy()
    cam = E2.camara(sc, "Cam39", lens=55, fstop=4)
    pos = cara + Vector((-0.06, -0.62, 0.02))
    tgt = cara + Vector((0, 0, -0.02))
    n = b - a

    def act(f):
        x = (f - a) / n
        d = sale(lin(x, 0.25, 0.55))
        lent.location = l0 + Vector((0, -0.004 * d, -alto * float(os.environ.get("BAJA_LENTES", 0.075)) * d))
        lent.rotation_euler = (R(-10 * d), 0, 0)
        E2.empujar(cam, f, a, b - 1, pos, tgt, cuanto=0.08, foco=cara)
    return {"actualizar": act}


# =====================================================================================================
# interior: la lengua y la campanita (cámara S) — planos 7, 8, 9, 11 y los recuadros 14S, 15S, 16S, 31S
# =====================================================================================================
def _lengua(sc):
    import set_lengua as SL
    S = SL.armar(sc)
    # papilas con brillo propio por objeto (Object Info > Color): se encienden en fila en el plano 7
    for nm in ("SensorReposo", "PapilaGrande"):
        m = bpy.data.materials[nm]
        nt = m.node_tree
        b = nt.nodes["Principled BSDF"]
        oi = nt.nodes.new("ShaderNodeObjectInfo")
        sep = nt.nodes.new("ShaderNodeSeparateColor")
        nt.links.new(oi.outputs["Color"], sep.inputs[0])
        b.inputs["Emission Color"].default_value = (1.0, 0.97, 0.92, 1)
        nt.links.new(sep.outputs[0], b.inputs["Emission Strength"])
    for cp, x, y, r in S["papilas"]:
        cp.color = (0, 0, 0, 1)
    return SL, S


def p07(sc, a, b):
    """Tu lengua tiene sensores de calor: la cámara entra por la boca abierta del ratón; las cúpulas se encienden en fila
    (blanco neutro); el dolly termina en el eje de la cámara S."""
    SL, S = _lengua(sc)
    E2.oculto(S["camp"], True)
    labio_m = P.mat("Labio", (0.45, 0.06, 0.09), rough=0.5, sss=0.2)
    diente_m = P.mat("DienteGrande", (0.95, 0.92, 0.84), rough=0.3)
    ZC = S["ZC"]
    # marco de la boca: labios arriba y abajo y los dos incisivos del ratón (se pasan con el dolly)
    for k, z in enumerate((0.36, -0.06)):
        l = P.prim("sphere", f"Labio{k}", S["C"], labio_m, r=1.0)
        l.scale = (0.50, 0.06, 0.09)
        l.location = (0, -0.62, z + ZC)
    for sx in (-1, 1):
        d = P.prim("cube", f"Incisivo{sx}", S["C"], diente_m)
        d.scale = (0.022, 0.012, 0.05)
        d.location = (sx * 0.024, -0.60, 0.29 + ZC)
        P.bevel(d, 0.006, 3)
    p0 = Vector((0.0, -0.52, 0.15 + ZC))
    for ob in list(bpy.data.objects):            # los labios quedan atrás de la cámara (no tapan el primer cuadro)
        if ob.name.startswith(("Labio", "Incisivo")):
            ob.hide_render = True
    n = b - a
    pap = sorted(S["papilas"], key=lambda t: t[2])
    y0, y1 = pap[0][2], pap[-1][2]

    def act(f):
        x = (f - a) / n
        k = E2.suave2(lin(x, 0.0, 0.85))
        pos = p0.lerp(S["cam_pos"], k)
        E2.mirar(S["cam"], pos, S["cam_tgt"], foco=S["foco"])
        S["cam"].data.dof.focus_distance = (S["foco"] - pos).length
        frente = y0 + (y1 - y0) * lin(x, 0.30, 0.95)       # la ola de luz recorre la lengua de adelante hacia atrás
        for cp, px, py, r in pap:
            v = math.exp(-((py - frente) / 0.05) ** 2) * (1 if x > 0.25 else 0)
            cp.color = (0.9 * v, 0, 0, 1)
    return {"actualizar": act}


def p08(sc, a, b):
    """como alarmas de incendio: una cúpula se transforma en la campanita de alarma plateada (cámara S)."""
    SL, S = _lengua(sc)
    ZC = S["ZC"]
    cup = P.prim("sphere", "CupulaCampana", S["C"], bpy.data.materials["SensorReposo"], r=0.012)
    cup.scale = (1, 1, 0.65)
    cup.location = (0, 0.02, ZC)
    n = b - a

    def act(f):
        x = (f - a) / n
        g = E2.rebote(lin(x, 0.20, 0.42), 2.0)
        S["camp"].scale = (max(0.001, g),) * 3
        E2.oculto(S["camp"], g < 0.02)
        c = (1 - suave(lin(x, 0.16, 0.30))) * E2.rebote(lin(f, a, a + 4), 1.5)      # puerta 6 r1: entra con pop
        cup.scale = (max(0.001, c * (1 + 0.6 * suave(lin(x, 0.0, 0.18)))),) * 2 + (max(0.001, c * 0.65),)
        cup.hide_render = c < 0.02
        din = math.exp(-max(0, x - 0.45) * 7) if x > 0.45 else 0
        SL.poner(S, None, 0, 0, empuje=suave(x))
        S["camp"].rotation_euler = (0, R(6 * din * math.sin((f - a) * 2.4)), 0)
    return {"actualizar": act}


def _timbre(f, f0, dur=40):
    """Intensidad del timbre que arranca en f0: sube rápido y se sostiene vibrando."""
    if f < f0:
        return 0.0, 0.0
    t = (f - f0) / E2.FPS
    return min(1.0, t / 0.08), t


def p09(sc, a, b):
    """Suenan con lo que quema de verdad: una gota de sopa hirviendo cae junto a la campanita y suena naranja."""
    SL, S = _lengua(sc)
    n = b - a
    f_cae = a + int(n * 0.32)

    def act(f):
        x = (f - a) / n
        su, t = _timbre(f, f_cae + 1)
        # puerta 6 r1: la bola aparecía entera en el cuadro; ahora parte arriba, fuera de cuadro, y cae desde el primer cuadro
        SL.poner(S, "naranja", su, t, gota=lin(f, a, f_cae), empuje=lin(f, a, b), alto=0.30,
                 posada=max(0.0, (f - f_cae) / E2.FPS))
    return {"actualizar": act}


def p11(sc, a, b):
    """una molécula que las hace sonar: la capsaicina entra desde la izquierda, calza en la campanita y la hace sonar roja."""
    SL, S = _lengua(sc)
    n = b - a
    f_calza = a + int(n * 0.45)

    def act(f):
        su, t = _timbre(f, f_calza)
        m = sale(lin(f, a + 2, f_calza))
        SL.poner(S, "roja", su, t, mol=m, empuje=0.6 * lin(f, a, b))
    return {"actualizar": act}


def p14S(sc, a, b):
    """Recuadro del plano 14: la misma campanita plateada, ahora del pájaro (ding chiquito)."""
    SL, S = _lengua(sc)

    def act(f):
        x = lin(f, a, b)
        din = math.exp(-max(0, x - 0.3) * 6) if x > 0.3 else 0
        SL.poner(S, None, 0, 0, empuje=0.5 * x)
        S["camp"].rotation_euler = (0, R(4 * din * math.sin((f - a) * 2.4)), 0)
    return {"actualizar": act}


def p15S(sc, a, b):
    """pero la capsaicina no la activa: la molécula llega a la campanita del pájaro y rebota; queda quieta y celeste."""
    SL, S = _lengua(sc)
    n = b - a
    f_toca = a + int(n * 0.45)

    def act(f):
        if f <= f_toca:
            m = sale(lin(f, a + 2, f_toca)) * 0.92
        else:
            m = 0.92 - 0.55 * sale(lin(f, f_toca, f_toca + int(n * 0.35)))      # rebota y se aleja
        # puerta 6 r1: la molécula era chiquita y la campana se ponía celeste (se leía "frío"); ahora la molécula es grande,
        # choca y rebota, y la campana queda plateada y quieta (un temblorcito mudo al choque)
        S["mol"].scale = (2.6,) * 3
        SL.poner(S, None, 0, 0, celeste=0.0, mol=m, empuje=0.5 * lin(f, a, b))
        g = math.exp(-max(0, f - f_toca) / 4.0) if f >= f_toca else 0.0
        S["camp"].rotation_euler = (0, R(3 * g * math.sin((f - f_toca) * 1.9)), 0)
    return {"actualizar": act}


def p16S(sc, a, b):
    """Sienten el calor...: la misma gota de sopa del plano 9 cae junto a la campanita del pájaro: suena naranja."""
    SL, S = _lengua(sc)
    n = b - a
    f_cae = a + int(n * 0.35)

    for o in S["gota_obs"]:          # puerta 6 r1: la gotita no se leía en la lupa → la bola de calor, el doble de grande
        if not o.name.startswith("VaporSopa"):
            o.scale = (o.scale.x * 2.0, o.scale.y * 2.0, o.scale.z * 2.0)
            S["gota_base"][o.name] = S["gota_base"][o.name] + Vector((0, 0, 0.0085 * 1.25))
    S["marca"].scale = (2.0, 2.0, 0.24)

    def act(f):
        su, t = _timbre(f, f_cae + 1)
        SL.poner(S, "naranja", su, t, celeste=0.0, gota=lin(f, a, f_cae), empuje=0.5 * lin(f, a, b), alto=0.20,
                 posada=max(0.0, (f - f_cae) / E2.FPS))
    return {"actualizar": act}


def p31S(sc, a, b):
    """Un solo cambio en su alarma: la campanita de la tupaya parte plateada, salta una sola pieza (~0,6 s) y queda
    celeste; entra la misma molécula roja, calza y la campanita da apenas un parpadeo rojo chico."""
    SL, S = _lengua(sc)
    per = S["perilla"]
    p0 = per.location.copy()
    n = b - a
    f_salta, f_vuelve = a + 4, a + 4 + 18
    f_calza = a + int(n * 0.78)

    def act(f):
        # la pieza (la perilla) salta, gira y vuelve a su lugar, y la campanita pasa a celeste
        x = lin(f, f_salta, f_vuelve)
        per.location = p0 + Vector((0, 0, 0.035 * math.sin(math.pi * x)))
        per.rotation_euler = (R(360 * suave(x)), 0, 0)
        cel = suave(lin(f, f_salta + 6, f_vuelve))
        m = sale(lin(f, f_vuelve + 4, f_calza)) if f > f_vuelve + 4 else None
        su, t = _timbre(f, f_calza)
        parp = 0.25 * su * math.exp(-t * 2.5) if su else 0
        SL.poner(S, "roja" if parp > 0.01 else None, parp, t, celeste=cel, mol=m, empuje=0.5 * lin(f, a, b))
    return {"actualizar": act}


# =====================================================================================================
# 10: el ají en corte
# =====================================================================================================
def _cerrar(me):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if not e.is_manifold], sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()


def p10(sc, a, b):
    """El ají trae capsaicina: el ají se abre en corte; las venas blancas de adentro brillan con gotitas rojas."""
    sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.05, 0.02, 0.015, 1)
    sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    C = P.collection("Corte")
    L = 0.26
    mitades = []
    interior = P.mat("AjiInteriorCorte", (0.78, 0.13, 0.05), rough=0.42, emit=0.02)   # pulpa roja (revisión del borrador: salmón claro + bloom = pétalo blanco)
    corte = P.prim("cube", "CajaCorte", C, None)
    corte.hide_render = True
    corte.display_type = "WIRE"
    for k, sgn in enumerate((1, -1)):
        aj = E.aji(f"AjiCorte{k}", largo=L, grosor=0.05, coll=C, seed=5, curva=0.15)
        _cerrar(aj.data)
        if interior.name not in [m.name for m in aj.data.materials]:
            aj.data.materials.append(interior)
        cj = P.prim("cube", f"CajaCorte{k}", C, interior)
        cj.scale = (0.2, 0.2, 0.5)
        cj.location = (0, sgn * 0.1, -L / 2 + 0.06)        # puerta 6 r1: el corte parte también el cáliz (antes cada mitad tenía el suyo)
        cj.hide_render = True
        cj.display_type = "WIRE"
        cj.parent = aj
        bo = aj.modifiers.new("Corte", "BOOLEAN")
        bo.operation = "DIFFERENCE"
        bo.object = cj
        bo.material_mode = "TRANSFER"
        piv = P.empty(f"MitadPiv{k}", coll=C)
        aj.parent = piv
        mitades.append((piv, sgn, aj))
    # venas (placenta) blancas a lo largo de la mitad de arriba, con gotitas rojas de capsaicina
    vena_m = P.mat("Placenta", (0.98, 0.96, 0.90), rough=0.5, emit=0.25)
    gota_m = P.mat("GotaCapsaicina", (1.0, 0.05, 0.03), rough=0.1, emit=3.0)
    semilla_m = P.mat("SemillaAji", (0.93, 0.80, 0.50), rough=0.45, emit=0.0)
    rr = random.Random(3)
    venas = []
    for piv, sgn, aj in mitades:
        for j, dx in enumerate((-0.010, 0.010)):
            pts = [(dx, 0, -0.012), (dx * 1.4, 0, -L * 0.25), (dx * 0.8, 0, -L * 0.48)]
            t = P.tube(f"Vena{sgn}{j}", pts, 0.0035, C, vena_m)
            t.parent = aj
            venas.append(t)
            for g in range(7):
                z = -0.02 - rr.uniform(0, L * 0.42)
                go = P.prim("sphere", f"Gota{sgn}{j}{g}", C, gota_m, r=rr.uniform(0.0016, 0.0028), u=16, v=8)
                go.location = (dx * (1.0 + 0.4 * (-z / (L * 0.5))) + rr.uniform(-0.002, 0.002), sgn * 0.0015, z)
                go.parent = aj
                venas.append(go)
            # semillas: discos crema pegados a la vena (lo que hace que se lea "ají por dentro")
            for g in range(6):
                z = -0.03 - (g + rr.uniform(-0.2, 0.2)) * L * 0.07
                se = P.prim("sphere", f"Semilla{sgn}{j}{g}", C, semilla_m, r=rr.uniform(0.0046, 0.0056), u=20, v=10)
                se.scale = (1.0, 0.32, 0.82)
                se.location = (dx * (1.0 + 0.4 * (-z / (L * 0.5))) + (1 if dx > 0 else -1) * rr.uniform(0.0062, 0.0085), sgn * 0.0012, z)
                se.rotation_euler = (0, rr.uniform(-0.5, 0.5), 0)
                se.parent = aj
                venas.append(se)
    for piv, sgn, aj in mitades:
        aj.rotation_euler = (0, R(90), 0)          # acostado a lo largo de X (la punta hacia -X)
        aj.location = (L / 2, 0, 0)
    L1 = bpy.data.lights.new("KeyCorte", "AREA")
    L1.energy, L1.size, L1.color = 11, 0.4, (1.0, 0.93, 0.85)
    lo = bpy.data.objects.new("KeyCorte", L1)
    sc.collection.objects.link(lo)
    lo.location = (-0.2, -0.3, 0.45)
    lo.rotation_euler = (Vector((0, 0, 0)) - lo.location).to_track_quat("-Z", "Y").to_euler()
    E2.area(sc, "RimCorte", (0.3, 0.4, 0.2), 10, 0.3, (1.0, 0.5, 0.4), (0, 0, 0))
    F_CAPS = E2.F(E2.t_palabra("capsaicina", E2.T[10][0]))
    cam = E2.camara(sc, "Cam10", lens=34, fstop=5.6)
    pos, tgt = Vector((0.0, -0.16, 0.44)), Vector((0.0, 0.0, 0.0))
    n = b - a

    def act(f):
        x = (f - a) / n
        ab = E2.suave(lin(x, 0.08, 0.42))         # puerta 6 r1: se abría de golpe; ahora en ~0,55 s, sin rebote
        for piv, sgn, aj in mitades:
            piv.rotation_euler = (R(sgn * 70 * ab), 0, 0)       # se abre como un libro: las caras de corte miran arriba
            piv.location = (0, sgn * 0.035 * ab, 0)
        brillo = 0.2 + 2.8 * suave(lin(x, 0.40, 0.70))
        gota_m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = brillo
        # al decir "capsaicina" se encienden las venas (ahí está la capsaicina)
        vena_m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.25 + 1.1 * suave(lin(f, F_CAPS, F_CAPS + 8))
        x2 = suave(lin(f, a, b - 1))
        E2.mirar(cam, pos.lerp(tgt, 0.10 * x2), tgt, foco=tgt, giro=90)      # el ají queda vertical en el cuadro (entero)
    return {"actualizar": act}


# =====================================================================================================
# bosque de China (28b–32)
# =====================================================================================================
def _bosque(sc):
    import set_bosque
    S = set_bosque.armar(sc)
    tp = S["tp"]
    S["tp_loc0"] = tp["root"].location.copy()
    S["tp_rot0"] = tp["root"].rotation_euler.copy()
    S["pc_rot0"] = tp["cabeza"].rotation_euler.copy()
    S["ojos_rot0"] = [o.rotation_euler.copy() for o in tp["ojos"]]
    cola = bpy.data.objects.get("Tupaya_cola")
    S["cola"] = cola
    S["cola_rot0"] = cola.rotation_euler.copy() if cola else None
    return S


def _tupaya_en(S, x):
    """Tupaya parada sobre la rama en x (misma orientación del cuadro de estilo)."""
    tp = S["tp"]
    tp["root"].location = Vector((x, 0.0, S["sobre_rama"](x, 0.0) - 0.002))


def _patas_tupaya(S):
    """Pivotes en las caderas para un paso simple (diagonales en fase). Se arma una vez por escena."""
    if "patas" in S:
        return S["patas"]
    root = S["tp"]["root"]
    out = []
    for (x, y) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        ob = bpy.data.objects.get(f"Tupaya_pata{x}{y}")
        if ob is None:
            continue
        piv = P.empty(f"PivPata{x}{y}", loc=(x * 0.020, y * 0.035 - 0.005, 0.050), coll=S["tp"]["root"].users_collection[0], parent=root)
        PJ.colgar(ob, piv)
        out.append((piv, 1 if x * y > 0 else -1))
    S["patas"] = out
    return out


def _caminar(S, f, peso=1.0):
    for piv, sg in _patas_tupaya(S):
        piv.rotation_euler = (R(26) * peso * sg * math.sin(f * 0.55), 0, 0)


def _cola(S, f, amp=6):
    if S["cola"] is not None:
        r0 = S["cola_rot0"]
        S["cola"].rotation_euler = Euler((r0.x + R(amp) * E2.ruido(f, 21, 1.6), r0.y, r0.z + R(amp * 1.5) * E2.ruido(f, 22, 1.3)))


def p28b(sc, a, b):
    """...el whip termina en el bosque verde con niebla (la mitad del plano 28)."""
    S = _bosque(sc)
    cam = S["cam"]
    c0 = cam.location.copy()
    q0 = cam.rotation_euler.to_quaternion()
    E2.oculto(S["tp"]["root"], True)

    def act(f):
        x = sale(lin(f, a, b))
        ang = R(70) * (1 - x)
        cam.rotation_mode = "QUATERNION"
        cam.rotation_quaternion = Quaternion((0, 0, 1), ang) @ q0
    return {"actualizar": act}


def p29(sc, a, b):
    """hay un mamífero que casi no lo siente: cámara que acompaña de costado a la tupaya que camina por la rama entre la
    niebla; en "casi no lo siente" se detiene y mira a cámara (en el 30 llega al encuadre principal).
    Puerta 6 r1: salía café oscuro (fuera de las luces del set) → las luces de la tupaya la acompañan; cola entera en cuadro."""
    S = _bosque(sc)
    tp = S["tp"]
    cam = S["cam"]
    n = b - a
    x_ini, x_fin = float(os.environ.get("P29_X0", -0.84)), float(os.environ.get("P29_X1", -0.68))
    dist = float(os.environ.get("P29_D", 1.05))
    r0 = S["pc_rot0"]
    TX = S["TX"]
    luces = [(o, o.location.copy()) for o in bpy.data.objects if o.name in ("Relleno", "Contorno", "RellenoPatas", "KeyTupaya", "RayoSol")]

    def act(f):
        x = (f - a) / n
        camina = suave(min(1.0, x / 0.66)) if x < 0.66 else 1.0
        tx = x_ini + (x_fin - x_ini) * camina
        _tupaya_en(S, tx)
        paso = 1 - suave(lin(x, 0.56, 0.68))
        tp["root"].location.z += 0.006 * abs(math.sin((f - a) * 0.55)) * paso       # (la altura sale del respaldo 0,135 del rayo: en x < -0,6 el rayo no pega)
        mira = suave(lin(x, 0.66, 0.84))
        tp["cabeza"].rotation_euler = Euler((r0.x * (0.2 + 0.8 * mira), 0, r0.z * mira))
        _caminar(S, f - a, paso)
        _cola(S, f, 10)
        for o, l0 in luces:
            o.location = l0 + Vector((tx - TX, 0, 0))
        bpy.context.view_layer.update()
        h = tp["cabeza"].matrix_world.translation
        tgt = Vector((tx - 0.02, 0.0, h.z - 0.03))
        pos = tgt + Vector((-0.08 + 0.06 * x, -dist, 0.07))
        E2.mirar(cam, pos, tgt, foco=h)
    return {"actualizar": act}


def p30(sc, a, b):
    """La tupaya, de China: la tupaya asoma en la rama y mira a cámara (encuadre del cuadro de estilo)."""
    S = _bosque(sc)
    tp = S["tp"]
    cam = S["cam"]
    c0 = cam.location.copy()
    t0 = S["tgt"].copy()
    n = b - a
    x0 = S["TX"]

    def act(f):
        x = (f - a) / n
        llega = suave(lin(x, 0.0, 0.42))
        _tupaya_en(S, (x0 - 0.20) + 0.20 * llega)          # puerta 6 r1: entra antes (se decía "la tupaya" sobre la rama vacía)
        tp["root"].location.z += 0.008 * abs(math.sin((f - a) * 0.55)) * (1 - llega)
        _caminar(S, f - a + 84, 1 - llega)        # sigue el paso del 29 (84 cuadros)
        mira = suave(lin(x, 0.40, 0.62))
        r0 = S["pc_rot0"]
        olf = suave(lin(x, 0.62, 0.75)) * math.sin((f - a) * 1.5)        # ya parada: olfatea (no queda tiesa)
        tp["cabeza"].rotation_euler = Euler((r0.x * mira + R(3) * olf, 0, r0.z * mira + R(2) * olf))
        for o, r_ in zip(tp["ojos"], S["ojos_rot0"]):
            o.rotation_euler = r_
        _cola(S, f)
        cam.rotation_mode = "XYZ"
        cam.location = c0.lerp(t0, 0.06 * suave(x))
        bpy.context.view_layer.update()
        return {"cabeza_y": E2.pantalla(sc, cam, tp["cabeza"].matrix_world.translation + Vector((0, 0, 0.05)))[1]}
    return {"actualizar": act}


def p31(sc, a, b):
    """Fondo del recuadro del plano 31: la tupaya en la rama, animada (puerta 6 r1: estaba tiesa 2,8 s). Olfatea, ladea la
    cabeza, en "cambio" mira hacia el recuadro (arriba a la izquierda) y vuelve a cámara como si nada."""
    S = _bosque(sc)
    tp = S["tp"]
    r0 = S["pc_rot0"]
    n = b - a

    def act(f):
        x = (f - a) / n
        _cola(S, f, 8)
        arriba = math.sin(math.pi * lin(x, 0.30, 0.75))
        ladea = math.sin(math.pi * lin(x, 0.05, 0.35))
        olf = math.sin((f - a) * 1.5) * (1 - arriba)
        tp["cabeza"].rotation_euler = Euler((r0.x * (1 - arriba) - R(18) * arriba + R(3) * olf, R(10) * ladea, r0.z * (1 - arriba) + R(25) * arriba))
    return {"actualizar": act}


def p32(sc, a, b):
    """y come plantas picantes como si nada: la tupaya mordisquea una espiga que cuelga, sin patas; en cada mordisco la
    espiga se acorta y la boca se cierra justo en la punta; apenas una gotita de sudor. Órbita lenta."""
    S = _bosque(sc)
    tp = S["tp"]
    pc = tp["cabeza"]
    esp = S["S"]["espigas"]
    nar = bpy.data.objects["Tupaya_naricita"]
    bpy.context.view_layer.update()
    n_w = nar.matrix_world.translation

    def punta(e):
        return e.matrix_world @ Vector((-0.003, 0.002, -e.data.splines[0].points[-1].co[2] * -1 if False else e.data.splines[0].points[-1].co[2]))
    e = min(esp, key=lambda o: (punta(o) - n_w).length)
    e_largo0 = e.scale.z
    gm = P.mat("SudorTupaya", (0.75, 0.90, 1.0), rough=0.05, transmission=0.9)
    gota = P.prim("sphere", "SudorTupaya", S["C"], gm, r=0.003)
    gota.scale = (1, 1, 1.5)
    cab_c = tp["root"].matrix_world @ Vector((0.012, -0.075, 0.118))
    gota.location = cab_c
    PJ.colgar(gota, pc)
    gl0 = gota.location.copy()
    cam = S["cam"]
    c0 = cam.location.copy()
    centro = S["cab_w"].copy()
    rel = c0 - centro
    x0 = S["TX"]
    fwd = (tp["root"].matrix_world.to_3x3() @ Vector((0, -1, 0))).normalized()
    n = b - a
    mordiscos = [0.18, 0.45, 0.72]
    ojos_s0 = [o_.scale.copy() for o_ in tp["ojos"]]

    def act(f):
        x = (f - a) / n
        # largo de la espiga: baja un poco en cada mordisco (la forma queda fija)
        largo = e_largo0 * (1 - 0.22 * sum(1 for m in mordiscos if x >= m + 0.06))     # puerta 6 r1: cada mordida se lleva un trozo que se ve
        e.scale = (1, 1, largo)
        # cabeza: apunta a la punta; en cada mordisco avanza, cierra y vuelve
        cerca = max(math.sin(math.pi * lin(x, m - 0.06, m + 0.12)) for m in mordiscos)
        bpy.context.view_layer.update()
        tip = punta(e)
        for _ in range(2):
            mira = AP.mirar_a(pc, tip, 1.0, limite=75)
            pc.rotation_euler = mira
            bpy.context.view_layer.update()
            d = (tip - nar.matrix_world.translation)
            avance = max(-0.05, min(0.06, d.dot(fwd) - 0.004 - 0.020 * (1 - cerca)))
            _tupaya_en(S, tp["root"].location.x + avance * fwd.x)
            bpy.context.view_layer.update()
        _cola(S, f)
        # entre mordidas mastica contenta: la cabeza late y los ojos se entornan
        mastica = max(math.sin(math.pi * lin(x, m + 0.10, m + 0.26)) for m in mordiscos)
        pc.rotation_euler = Euler((pc.rotation_euler.x + R(4) * mastica * math.sin((f - a) * 2.2), pc.rotation_euler.y, pc.rotation_euler.z))
        for o_, s0_ in zip(tp["ojos"], ojos_s0):
            o_.scale = (s0_.x, s0_.y, s0_.z * (1 - 0.45 * mastica))
        gota.location = gl0 + Vector((0, 0, -0.006 * suave(lin(x, 0.80, 1.0))))
        gota.hide_render = x < 0.62
        ang = R(-14 + 28 * x)
        rr_ = Matrix.Rotation(ang, 3, "Z") @ rel
        cam.rotation_mode = "QUATERNION"
        E2.mirar(cam, centro + rr_, S["tgt"] + (centro + rr_ - c0) * 0.0, foco=centro)
    return {"actualizar": act}


# =====================================================================================================
# 23 y 24: los recuadros "y si…" (muelas) y la lupa del cuello del pájaro
# =====================================================================================================
def _fondo_muelas(sc):
    sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.06, 0.36, 0.48, 1)
    sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.7


def p23(sc, a, b):
    """Fondo del plano 23: el ratón entero en 3/4 (el post espeja, pone la lupa, el recuadro y la ✕).
    Puerta 6 r1: de perfil puro el ratón no se parecía al de la ficha (ojo de cuenta, hocico largo) y estaba congelado →
    3/4 para que se vean los ojos grandes y la guata, y mastica al ritmo de las muelas de la lupa, parpadea y mueve la cabeza."""
    _fondo_muelas(sc)
    os.environ.setdefault("CAMOFF", os.environ.get("P23_CAMOFF", "0.80,-0.66,0.07"))
    os.environ.setdefault("MIRADA", "0.6,-1.0,0.05")
    import set_muelas
    M = set_muelas.armar(sc, "cara")
    rt = M["rt"]
    cab0 = rt["cabeza"].rotation_euler.copy()
    n = b - a

    def act(f):
        x = (f - a) / n
        ciclo = (x * 3) % 1
        cierra = math.sin(math.pi * E2.clamp(ciclo / 0.6)) if ciclo < 0.6 else 0.0
        rt["cabeza"].rotation_euler = Euler((cab0.x + R(5) * cierra, cab0.y + R(3) * math.sin(x * 4.0), cab0.z + R(4) * math.sin(x * 2.5)))
        rt["boca"].scale = (1 + 0.5 * (1 - cierra), 1 + 0.3 * (1 - cierra), 1 + 1.6 * (1 - cierra) * (x < 0.97))
        AP.parpados(rt["parpados"], AP.parpadeo(f, a + int(n * 0.55), -100, dur=6))
        bpy.context.view_layer.update()
        return {"mejilla": E2.pantalla(sc, sc.camera, M["M"] @ Vector((0.0165, M["centro_loc"].y, M["centro_loc"].z)))}
    return {"actualizar": act}


def p23L(sc, a, b):
    """Lupa del plano 23: las muelas del ratón; entran semillas enteras y salen hechas migas (las muelas se cierran)."""
    _fondo_muelas(sc)
    import set_muelas
    M = set_muelas.armar(sc, "lupa")
    sup = [o for o in bpy.data.objects if o.name.startswith(("Muela_sup", "Encia_sup"))]
    s0 = {o.name: o.location.copy() for o in sup}
    sem = [o for o in bpy.data.objects if o.name.startswith("Semilla") and "_cara" not in o.name]
    mig = [o for o in bpy.data.objects if o.name.startswith("Miga")]
    sem0 = {o.name: o.location.copy() for o in sem}
    n = b - a
    GAP = 0.0042

    def act(f):
        x = (f - a) / n
        # tres mordidas: la fila de arriba baja y aplasta; después de la segunda, las semillas ya son migas
        ciclo = (x * 3) % 1
        cierra = math.sin(math.pi * E2.clamp(ciclo / 0.6)) if ciclo < 0.6 else 0
        for o in sup:
            o.location = s0[o.name] + Vector((0, 0, -GAP * 0.92 * cierra))
        molidas = x > 0.4333          # se cambian justo cuando las muelas están cerradas (segunda mordida)
        for o in sem:
            o.hide_render = molidas
            for ch in o.children:
                ch.hide_render = molidas
            o.location = sem0[o.name] + Vector((0, 0.0012 * math.sin(f * 0.4), 0))
        for k, o in enumerate(mig):
            o.hide_render = not molidas and k > 3
    return {"actualizar": act}


def p24(sc, a, b):
    """Fondo del plano 24 (en espejo del 23): el pájaro entero de perfil sobre el mismo fondo turquesa (un cuadro)."""
    _fondo_muelas(sc)
    C = P.collection("Pajaro24")
    pj = PJ.pajaro(C, nombre="Cuit24")
    for pv in pj["parpados"]:
        for ch in pv.children:
            ch.rotation_euler.x = R(-30)
    pj["root"].rotation_euler.z = R(90)              # de perfil, mirando a la izquierda de la pantalla
    E2.area(sc, "Key", (0.6, -0.5, 0.6), 30, 0.5, (1, 0.96, 0.92), (0, 0, 0.12))
    # puerta 6 r1: salía gris carbón y la cola se cortaba; ahora relleno de frente, más lejos y corrido; traga en "traga"
    E2.area(sc, "Relleno24", (-0.2, -0.9, 0.3), 14, 0.8, (1, 0.94, 0.88), (0, 0, 0.11))
    cam = E2.camara(sc, "Cam24", lens=50)
    E2.mirar(cam, Vector((-0.045, -1.62, 0.125)), Vector((-0.045, 0, 0.125)))
    bulto = AP.Bulto(pj, C)
    cab0 = pj["cabeza"].rotation_euler.copy()
    t_tr = (E2.t_palabra("traga", E2.T[24][0]) - E2.T[24][0]) / (E2.T[24][1] - E2.T[24][0])
    n = b - a

    def act(f):
        x = (f - a) / n
        tr = AP.trago(lin(x, t_tr - 0.08, t_tr + 0.30))
        pj["cabeza"].rotation_euler = Euler((cab0.x - R(16) * tr, cab0.y, cab0.z))
        pj["mandibula"].rotation_euler.x = R(6) * tr
        bulto.poner(lin(x, t_tr + 0.05, t_tr + 0.50))
        AP.parpados(pj["parpados"], AP.parpadeo(f, a + int(n * 0.2), -30, dur=6))
        bpy.context.view_layer.update()
        cuello = pj["root"].matrix_world @ Vector((0, -0.045, 0.100))
        return {"cuello": E2.pantalla(sc, cam, cuello)}
    return {"actualizar": act}


def p24L(sc, a, b):
    """Lupa del plano 24: por dentro del cuello, las semillas bajan ENTERAS después del trago (contraste con las migas)."""
    sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.16, 0.04, 0.05, 1)
    sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    C = P.collection("Cuello")
    pared = P.mat("Garganta", (0.46, 0.11, 0.13), rough=0.38, coat=0.25)      # sin SSS: en un tubo de 1 cm la luz lo atravesaba y quedaba rosado pálido
    for sx in (-1, 1):          # las dos paredes del cuello (por dentro), húmedas, se leen como un tubo
        w_ = P.prim("cyl", f"Pared{sx}", C, pared, r=0.012, r2=0.012, h=0.3, seg=32)
        w_.location = (sx * 0.0225, 0.004, 0.0)
    sem = P.mat("SemillaEntera", (0.96, 0.86, 0.46), rough=0.5, coat=0.2)
    borde = P.mat("SemillaBordeE", (0.74, 0.56, 0.20), rough=0.55)
    semillas = []
    for k in range(5):
        g = P.prim("cyl", f"SemE{k}", C, borde, r=0.0055, r2=0.0055, h=0.0016, seg=32)
        cara = P.prim("cyl", f"SemE{k}_cara", C, sem, r=0.0045, r2=0.0045, h=0.0006, seg=32)
        cara.location = (0, 0, 0.0007)
        cara.parent = g
        g.rotation_euler = (R(70 + 9 * k), R(14 * k), 0)
        semillas.append((g, k))
    E2.area(sc, "LuzCuello", (0.03, -0.12, 0.06), 0.55, 0.1, (1.0, 0.92, 0.85), (0, 0, 0))
    E2.area(sc, "RimCuello", (-0.05, 0.06, 0.05), 0.5, 0.08, (1.0, 0.55, 0.50), (0, 0, 0))
    cam = E2.camara(sc, "Cam24L", lens=40)
    E2.mirar(cam, Vector((0, -0.075, 0.0)), Vector((0, 0, 0.0)))
    n = b - a

    def act(f):
        x = (f - a) / n
        for g, k in semillas:     # revisión del borrador: la lupa quedaba vacía al principio y al final; ahora pasan todo el plano
            z = 0.040 - 0.080 * lin(x, -0.18 + 0.21 * k, 0.30 + 0.21 * k)
            g.location = (0.005 * math.sin(k * 2.1) + 0.0015 * math.sin(f * 0.3 + k), 0.002, z)
            g.rotation_euler.z = f * 0.05 + k
    return {"actualizar": act}


# =====================================================================================================
# registro de piezas
# =====================================================================================================
def _pieza(k, fn, **kw):
    a, b = FR(k)
    return dict(a=a, b=b, fn=fn, plano=k, **kw)


_a28, _b28 = FR(28)
_m28 = (_a28 + _b28) // 2

PIEZAS = {
    "28a": dict(a=_a28, b=_m28, fn=p28a, plano=28),
    "28b": dict(a=_m28, b=_b28, fn=p28b, plano=28),
    "1": _pieza(1, p01),
    "2": _pieza(2, p02),
    "14": _pieza(14, p14),
    "15": _pieza(15, p14),          # fondo animado del 15 (puerta 6 r1)
    "16": _pieza(16, p14),          # fondo animado del 16
    "17": _pieza(17, p17),
    "40": _pieza(40, p40),
    "3": _pieza(3, p03),
    "4": _pieza(4, p04),
    "5": _pieza(5, p05),
    "6": _pieza(6, p06),
    "12": _pieza(12, p12),
    "13": _pieza(13, p13),
    "33": _pieza(33, p33),
    "34": _pieza(34, p34),
    "18": _pieza(18, p18),
    "19": _pieza(19, p19),
    "20": _pieza(20, p20),
    "21": _pieza(21, p21),
    "22": _pieza(22, p22),
    "25": _pieza(25, p25),
    "26": _pieza(26, p26),
    "27": _pieza(27, p27),
    "35": _pieza(35, p35),
    "36": _pieza(36, p36),
    "37": _pieza(37, p37),
    "38": _pieza(38, p38),
    "39": _pieza(39, p39),
    "7": _pieza(7, p07),
    "8": _pieza(8, p08),
    "9": _pieza(9, p09),
    "10": _pieza(10, p10),
    "11": _pieza(11, p11),
    "14S": _pieza(14, p14S, aux=True, cuadrado=True),
    "15S": _pieza(15, p15S, aux=True, cuadrado=True),
    "16S": _pieza(16, p16S, aux=True, cuadrado=True),
    "31S": _pieza(31, p31S, aux=True, cuadrado=True),
    "29": _pieza(29, p29),
    "30": _pieza(30, p30),
    "31": _pieza(31, p31),
    "32": _pieza(32, p32),
    "23": _pieza(23, p23),
    "23L": _pieza(23, p23L, aux=True, cuadrado=True, lado=1.2),
    "24": _pieza(24, p24),
    "24L": _pieza(24, p24L, aux=True, cuadrado=True, lado=1.0),
}


def _partir(pid, n):
    """Parte una pieza larga en n trabajos ("29@1"…): cada uno arma la escena entera con el rango completo del plano
    (la animación no cambia) y renderiza sólo su tramo de cuadros. El meta se junta en el post por "base"."""
    pz = PIEZAS.pop(pid)
    a, b = pz["a"], pz["b"]
    for i in range(n):
        PIEZAS[f"{pid}@{i + 1}"] = dict(pz, rango=(a + (b - a) * i // n, a + (b - a) * (i + 1) // n), base=pid)


for _pid, _n in (("29", 3), ("30", 2), ("25", 2), ("12", 2), ("36", 2)):
    _partir(_pid, _n)
