"""Los 36 planos del Ep. 3 (storyboard v1, fichas de plano) en 9 escenas.

Cada función pXX(sc, a, b) arma su escena y devuelve {"actualizar": f -> info, "meta": {...}}. Las escenas comparten
el set de la obra (`calle.py`) y el edificio (`edificio.py`, patas con regla). PIEZAS (al final) dice qué renderiza
cada pieza. Sin personajes con ojos: el chequeo de caras se corre con --sin-personajes.
"""
import math, os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.abspath(os.path.join(HERE, "../../.."))
for p in (HERE, os.path.join(STUDIO, "plantilla")):
    if p not in sys.path:
        sys.path.insert(0, p)
import bpy
from mathutils import Vector, Euler, Matrix
import props as P
import ep03 as E
import edificio as ED
import calle as C
import corte as K

R = math.radians
FR = E.FR
lin, suave, sale, entra, tramo = E.lin, E.suave, E.sale, E.entra, E.tramo
V = 1.6                       # m por segundo de video (cámara rápida: un ciclo de pasos cada 1,5 s)
D_C0 = 1.8                    # distancia del cuadro 0: grupo A (amarillo) a medio paso
C0_POS, C0_TGT, C0_LENS, C0_SHIFT = (-36.0, -24.0, 0.5), (-6.0, 0.0, 4.5), 12.0, -0.07


def t_de(f):
    return (f - 1) / E.FPS


def _cam(sc, lens=24, shift=0.0):
    cam = E.camara(sc, lens=lens)
    cam.data.shift_y = shift
    return cam


def _obra(sc, edificio=True, sol=None):
    S = C.armar(sc)
    C.cielo(sc, **(sol or {}))
    S["ed"] = ED.Edificio(sc) if edificio else None
    return S


def _polvo(coll):
    m = P.mat("Polvo", (0.62, 0.50, 0.36), rough=1.0, alpha=0.55)
    m.blend_method = "BLEND" if hasattr(m, "blend_method") else None
    bolas = []
    for k in range(9):
        b = P.prim("ico", f"Polvo{k}", coll, m, sub=2, r=0.25)
        b.hide_render = True
        bolas.append(b)
    return bolas


def _poner_polvo(bolas, centro, edad, seed=0):
    r = random.Random(seed)
    for k, b in enumerate(bolas):
        if edad < 0 or edad > 0.9:
            b.hide_render = True
            continue
        a = r.uniform(0, 2 * math.pi)
        d = 0.3 + 1.6 * sale(edad / 0.9) * r.uniform(0.6, 1.0)
        b.hide_render = False
        b.location = (centro.x + d * math.cos(a), centro.y + d * math.sin(a), 0.15 + 0.5 * sale(edad / 0.9) * r.uniform(0.3, 1))
        s = (0.6 + 1.4 * sale(edad / 0.9)) * (1 - edad / 0.9) + 0.05
        b.scale = (s, s, s * 0.6)


# =====================================================================================================
# E1 obra: la escuela camina derecho por +x (planos 1, 2, 3, 4, 12, 22, 31) · E9 loop (35, 36)
# =====================================================================================================
def _camina(sc, a, b, dist_de, cam_de, lens=24, shift=0.0, polvo_pata=None):
    S = _obra(sc)
    ed = S["ed"]
    cam = _cam(sc, lens, shift)
    pose = ED.recta(0, 0, 0)
    bolas = _polvo(S["coll"]) if polvo_pata is not None else None

    def act(f):
        t = t_de(f)
        d = dist_de(t)
        info = ed.poner(d, pose)
        pos, tgt = cam_de(t, d)
        E.mirar(cam, pos, tgt)
        if bolas:
            pt = ed.patas[polvo_pata]
            fase = (d / (2 * ED.PASO) + 0.5 * pt["g"]) % 1.0
            edad = (fase * 2 * ED.PASO) / V          # segundos desde que aterrizó
            _poner_polvo(bolas, pt["p"].matrix_world.translation.copy(), edad if fase < 0.5 else -1, seed=f // 40)
        return {"dist": round(d, 3), "fase": round(info["fase"], 3)}
    return {"actualizar": act}


def _c0_cam(t0, t1, push=0.06):
    def cam_de(t, d):
        x = suave(lin(t, t0, t1))
        p = Vector(C0_POS).lerp(Vector(C0_TGT), push * x)
        return p, C0_TGT
    return cam_de


def p01(sc, a, b):
    t0, t1 = E.T[1]
    return _camina(sc, a, b, lambda t: D_C0 + V * t, _c0_cam(t0, t1), lens=C0_LENS, shift=C0_SHIFT)


def p02(sc, a, b):
    t0, t1 = E.T[2]
    d0 = D_C0 + V * t0

    def cam_de(t, d):
        x = lin(t, t0, t1)
        return Vector((d - 34 + 6 * x, -78, 40 - 4 * x)), Vector((d + 2, 8, 6))
    return _camina(sc, a, b, lambda t: d0 + V * (t - t0), cam_de, lens=27, shift=-0.155)


def p03(sc, a, b):
    t0, t1 = E.T[3]

    def cam_de(t, d):
        return Vector((d - 9, -19, 0.55)), Vector((d - 5, 0, 0.75))
    return _camina(sc, a, b, lambda t: 10 + V * (t - t0), cam_de, lens=20, shift=-0.10)


def p04(sc, a, b):
    t0, t1 = E.T[4]
    t_land = E.t_palabra("patas", t0)          # el pie aterriza en "patas"
    d_land = 2 * ED.PASO * 6
    n = 22 * 0 + 9 * 6                         # una pata de la fila delantera, grupo A
    while True:
        x, y = -21 + 2 * (n // 6), -5 + 2 * (n % 6)
        if y == -5 and ((n // 6) + (n % 6)) % 2 == 0:
            break
        n += 6
    pt_x = -21 + 2 * (n // 6)

    def cam_de(t, d):
        pie = Vector((d_land + pt_x + ED.PASO / 2, -5, 0.15))
        sh = 0.04 * math.exp(-max(0, t - t_land) * 9) * math.sin(max(0, t - t_land) * 60) if t > t_land else 0
        return pie + Vector((-1.6, -4.6, 0.30 + sh)), pie + Vector((0.2, 0, 0.55 + sh))
    return _camina(sc, a, b, lambda t: d_land + V * 0.45 * (t - t_land), cam_de, lens=30, shift=-0.20)


def p12(sc, a, b):
    t0, t1 = E.T[12]

    def cam_de(t, d):
        return Vector((-46, -30, 2.2)), Vector((-8, 0, 4.0))
    return _camina(sc, a, b, lambda t: 1.2 + 1.4 * V * (t - t0), cam_de, lens=17, shift=-0.06)


def p22(sc, a, b):
    t0, t1 = E.T[22]

    def cam_de(t, d):
        return Vector((d - 2, -64, 4.0)), Vector((d + 1, 0, 6.5))
    return _camina(sc, a, b, lambda t: 20 + V * (t - t0), cam_de, lens=26, shift=-0.125)


def p31(sc, a, b):
    """Barrido hacia el cielo (la transición especial, hecha con la cámara y desenfoque de post)."""
    t0, t1 = E.T[31]

    def cam_de(t, d):
        x = entra(lin(t, t0, t1))
        return Vector((d - 30, -70, 30 + 24 * x)), Vector((d + 10 * x, 8, 6 + 55 * x))
    return _camina(sc, a, b, lambda t: 30 + V * (t - t0), cam_de, lens=26)


def p35(sc, a, b):
    t0, t1 = E.T[35]
    t_fin = E.T[36][1]

    def cam_de(t, d):
        x = suave(lin(t, t0, t1))
        return Vector((d - 40 + 4 * x, -88 + 10 * x, 46 - 18 * x)), Vector((d + 2, 8, 6))
    return _camina(sc, a, b, lambda t: D_C0 - V * (t_fin - t), cam_de, lens=27, shift=-0.14)


def p36(sc, a, b):
    t0, t1 = E.T[36]

    def cam_de(t, d):            # termina EXACTO en C0 (el plano 1 empieza ahí): loop
        x = suave(lin(t, t0, t1))
        ini = Vector(C0_POS) + Vector((-6, -10, 3.0))
        return ini.lerp(Vector(C0_POS), x), C0_TGT
    return _camina(sc, a, b, lambda t: D_C0 - V * (t1 - t), cam_de, lens=C0_LENS, shift=C0_SHIFT)


# =====================================================================================================
# E2 escuela antes de la mudanza (planos 5–11): quieta, sin patas; torres fantasma; bola de demolición
# =====================================================================================================
def _escuela(sc):
    S = _obra(sc, sol=dict(elev=24.0, azim=-62.0, fuerza=4.8))
    for ob in bpy.data.objects:     # antes de la obra: sin conos ni montones delante
        if ob.name.startswith(("Cono", "Monton", "Huella")):
            ob.hide_render = True
    S["ed"].quieto()
    return S


def _vidrio_fantasma():
    m = bpy.data.materials.get("Fantasma")
    if m:
        return m
    m = P.mat("Fantasma", (0.30, 0.62, 0.95), rough=0.08, emit=0.12, alpha=0.22)
    return m


def _torre_fantasma(name, x, y, w, d, h, coll):
    ob = ED._caja(name, -w / 2, w / 2, -d / 2, d / 2, 0, 1.0, coll, _vidrio_fantasma())
    ob.location = (x, y, 0)
    ob["h"] = h
    lineas = P.mat("FantasmaLineas", (0.55, 0.85, 1.0), emit=1.2, alpha=0.8)
    pisos = []
    for k in range(int(h // 4)):
        l = ED._caja(name + f"_l{k}", -w / 2 - 0.05, w / 2 + 0.05, -d / 2 - 0.05, d / 2 + 0.05, 0, 0.18, coll, lineas)
        l.location = (x, y, 4 * k + 3.8)
        pisos.append(l)
    return ob, pisos


def p05(sc, a, b):
    S = _escuela(sc)
    cam = _cam(sc, 30, -0.17)
    t0, t1 = E.T[5]

    def act(f):
        x = suave(lin(t_de(f), t0, t1))
        E.mirar(cam, Vector((-6, -62, 4)).lerp(Vector((-4, -50, 4.4)), x), (0, 0, 8.6))
    return {"actualizar": act}


def p06(sc, a, b):
    S = _escuela(sc)
    cam = _cam(sc, 55, 0.0)
    t0, t1 = E.T[6]
    placa = S["ed"].placa
    luz = E.area(sc, "Destello", (3, -12, 6), 0.0, 0.6, (1, 0.9, 0.7), (0, -8, 4))

    def act(f):
        t = t_de(f)
        x = suave(lin(t, t0, t1))
        bpy.context.view_layer.update()
        pz = sum((placa.matrix_world @ Vector(c) for c in placa.bound_box), Vector()) / 8
        E.mirar(cam, pz + Vector((1.2, -7.5, -0.6)).lerp(Vector((0.6, -5.6, -0.4)), x), pz)
        luz.data.energy = 900 * max(0.0, 1 - abs(t - (t0 + 0.8)) / 0.25)
    return {"actualizar": act}


def p07(sc, a, b):
    S = _escuela(sc)
    cam = _cam(sc, 30, -0.145)
    t0, t1 = E.T[7]

    def act(f):
        x = sale(lin(t_de(f), t0, t1))
        E.mirar(cam, Vector((-70, -120, 40 + 30 * x)), (0, 20, 2))
    return {"actualizar": act}


def p08(sc, a, b):
    S = _escuela(sc)
    cam = _cam(sc, 17, -0.02)
    t0, t1 = E.T[8]

    def act(f):
        x = suave(lin(t_de(f), t0, t1))
        E.mirar(cam, Vector((-15, -22, 0.6)).lerp(Vector((-12, -18, 0.6)), x), (-1, 0, 12))
        return {"contador": round(sale(lin(t_de(f), t0 + 0.15, t1 - 0.45)) * 7600)}
    return {"actualizar": act}


def _torres(S):
    coll = S["coll"]
    datos = [(-40, 6, 18, 20, 72), (40, 4, 18, 20, 84), (-14, 44, 24, 16, 96), (22, 46, 22, 16, 64), (0, -30, 28, 14, 56)]
    return [_torre_fantasma(f"Fantasma{i}", *d, coll) for i, d in enumerate(datos)]


def _crecer(torre, pisos, x):
    ob, h = torre, torre["h"]
    ob.scale.z = max(0.001, h * x)
    ob.hide_render = x <= 0.001
    for l in pisos:
        l.hide_render = l.location.z > h * x


def p09(sc, a, b):
    S = _escuela(sc)
    T = _torres(S)
    cam = _cam(sc, 22, -0.24)
    t0, t1 = E.T[9]

    def act(f):
        t = t_de(f)
        ang = R(-115 + 25 * lin(t, t0, t1))
        E.mirar(cam, (95 * math.cos(ang), 95 * math.sin(ang), 30), (0, 10, 18))
        for i, (ob, pisos) in enumerate(T[:4]):
            _crecer(ob, pisos, sale(lin(t, t0 + 0.25 * i, t0 + 0.25 * i + 1.3)))
        _crecer(*T[4], 0)
    return {"actualizar": act}


def p10(sc, a, b):
    S = _escuela(sc)
    T = _torres(S)
    cam = _cam(sc, 24, -0.25)
    t0, t1 = E.T[10]
    big, pisos = T[4]
    big.location = (0, 6, 0)
    for l in pisos:
        l.location.x, l.location.y = 0, 6

    def act(f):
        t = t_de(f)
        x = suave(lin(t, t0, t1))
        E.mirar(cam, Vector((-36, -64, 8)).lerp(Vector((-30, -56, 8)), x), (0, 0, 14))
        for ob, ps in T[:4]:
            _crecer(ob, ps, 1.0)
        _crecer(big, pisos, sale(lin(t, t0 + 0.1, t0 + 1.5)))
    return {"actualizar": act}


def p11(sc, a, b):
    S = _escuela(sc)
    cam = _cam(sc, 22, -0.27)
    t0, t1 = E.T[11]
    acero = P.mat("BolaAcero", (0.06, 0.06, 0.065), rough=0.35, metal=0.9)
    bola = P.prim("sphere", "Bola", S["coll"], acero, r=3.2)
    piv = Vector((-14, -14, 70))
    eslabones = [P.prim("torus", f"Cadena{k}", S["coll"], acero, R=0.35, r=0.09) for k in range(28)]

    def act(f):
        t = t_de(f)
        x = lin(t, t0, t0 + 0.75)
        ang = R(-34) * (1 - sale(x)) + R(1.6) * math.sin(max(0, t - t0 - 0.75) * 9) * math.exp(-max(0, t - t0 - 0.75) * 3)
        L = 62.0
        pos = piv + Vector((L * math.sin(ang), -0.0, -L * math.cos(ang))) + Vector((0, 0, 0))
        pos.y = -14 + (-2.2 - (-14)) * sale(x) * 0.0
        bola.location = (pos.x, -10.5, pos.z)
        for k, e in enumerate(eslabones):
            u = (k + 0.5) / len(eslabones)
            p_ = piv.lerp(Vector(bola.location) + Vector((0, 0, 2.4)), u)
            e.location = p_
            e.rotation_euler = (R(90) * (k % 2), 0, ang)
        E.mirar(cam, (-30, -38, 8), (-8, -6, 12))
    return {"actualizar": act}


# =====================================================================================================
# E3 corte (planos 13–17)
# =====================================================================================================
def _corte(sc):
    S = _obra(sc, edificio=True)
    k = K.Corte(sc, S["ed"])
    for ob in bpy.data.objects:
        if ob.name.startswith(("Fantasma",)):
            ob.hide_render = True
    return S, k


CORTE_POS, CORTE_TGT, CORTE_LENS, CORTE_SHIFT = (-22.0, -26.0, -1.0), (-20.0, 0.0, -1.2), 18.0, -0.135


def p13(sc, a, b):
    S, k = _corte(sc)
    cam = _cam(sc, CORTE_LENS, CORTE_SHIFT)
    t0, t1 = E.T[13]

    def act(f):
        t = t_de(f)
        x = suave(lin(t, t0, t1))
        k.poner(f, suave(lin(t, t0 + 0.1, t1 - 0.1)), 0, 0, 0)
        E.mirar(cam, Vector(CORTE_POS).lerp(Vector(CORTE_TGT), 0.04 * x), CORTE_TGT)
    return {"actualizar": act}


def p14(sc, a, b):
    S, k = _corte(sc)
    cam = _cam(sc, CORTE_LENS, CORTE_SHIFT)
    t0, t1 = E.T[14]
    t_198 = E.t_palabra("ciento", t0)

    def act(f):
        t = t_de(f)
        x = suave(lin(t, t0, t1))
        n = k.poner(f, 1, lin(t, t0 + 0.05, E.t_palabra("ocho", t0) + 0.15), 0, 0)
        E.mirar(cam, Vector(CORTE_POS).lerp(Vector(CORTE_TGT), 0.04 + 0.04 * x), CORTE_TGT)
        return {"contador": n}
    return {"actualizar": act}


def p15(sc, a, b):
    S, k = _corte(sc)
    cam = _cam(sc, 32)
    t0, t1 = E.T[15]
    luz = E.area(sc, "Barrido", (-10, -14, -1), 400.0, 1.5, (1, 0.95, 0.85), (-3, -4, -2))

    def act(f):
        t = t_de(f)
        x = suave(lin(t, t0, t1))
        k.poner(f, 1, 1, 0, 0)
        E.mirar(cam, Vector((-6.5, -14.5, -2.2)).lerp(Vector((-4.5, -14.2, -2.1)), x), (-4, -4, -1.6))
        luz.location = (-14 + 16 * x, -12, -1.0)
    return {"actualizar": act}


def p16(sc, a, b):
    S, k = _corte(sc)
    cam = _cam(sc, 30)
    t0, t1 = E.T[16]

    def act(f):
        t = t_de(f)
        x = suave(lin(t, t0, t1))
        k.poner(f, 1, 1, lin(t, t0 + 0.05, t1 - 0.05), 0)
        E.mirar(cam, Vector((-14, -17, -1.6)).lerp(Vector((-13, -15.8, -1.5)), x), (-15, -5, -1.2))
    return {"actualizar": act}


def p17(sc, a, b):
    S, k = _corte(sc)
    cam = _cam(sc, CORTE_LENS, CORTE_SHIFT)
    t0, t1 = E.T[17]

    def act(f):
        t = t_de(f)
        x = suave(lin(t, t0, t1))
        k.poner(f, 1, 1, 1, suave(lin(t, E.t_palabra("alzaron", t0) - 0.1, t1 - 0.1)))
        E.mirar(cam, Vector(CORTE_POS) + Vector((0, -2 * x, -0.8 * x)), Vector(CORTE_TGT) + Vector((0, 0, 0.6 * x)))
    return {"actualizar": act}


# =====================================================================================================
# E4 grupos (planos 18–21): las patas en cámara lenta, cada grupo se enciende
# =====================================================================================================
def _brillo(nombre, v):
    m = bpy.data.materials[nombre]
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Emission Color"].default_value = (*b.inputs["Base Color"].default_value[:3], 1)
    b.inputs["Emission Strength"].default_value = v


def _apagar(nombre, v):
    m = bpy.data.materials[nombre]
    b = m.node_tree.nodes["Principled BSDF"]
    col = ED.AMARILLO if nombre == "PataA" else ED.CELESTE
    b.inputs["Base Color"].default_value = (*(c * v + 0.25 * (1 - v) for c in col), 1)


def _grupos(sc, plano):
    S = _obra(sc)
    ed = S["ed"]
    cam = _cam(sc, 24, -0.10)
    pose = ED.recta(0, 0, 0)
    t0, t1 = E.T[plano]

    def act(f):
        t = t_de(f)
        if plano in (18, 19):
            d = ED.PASO
        elif plano == 20:
            d = ED.PASO + ED.PASO * suave(lin(t, t0 + 0.1, t1 - 0.1))
        else:
            d = 2 * ED.PASO + ED.PASO * suave(lin(t, t0 + 0.05, t1 - 0.05))
        ed.poner(d, pose, bob=0.0)
        if plano == 18:
            ga = 2.5 * max(0.0, 1 - abs(t - (t0 + 0.25)) / 0.45)
            gb = 2.5 * max(0.0, 1 - abs(t - (t0 + 1.05)) / 0.45)
            da = db = 1.0
        elif plano == 19:
            ga, gb, da, db = 0.0, 1.6, 0.35, 1.0
        elif plano == 20:
            ga, gb, da, db = 1.6, 0.0, 1.0, 0.35
        else:
            ga, gb, da, db = 0.0, 1.6, 0.35, 1.0
        _brillo("PataA", ga)
        _brillo("PataB", gb)
        _apagar("PataA", da)
        _apagar("PataB", db)
        x = suave(lin(t, t0, t1))
        E.mirar(cam, Vector((d - 4.0, -15.5, 0.45)).lerp(Vector((d - 3.4, -14.0, 0.45)), x), Vector((d + 1.0, -3, 0.95)))
        bpy.context.view_layer.update()
        pies = {}
        for g in (0, 1):
            pts = [E.pantalla(sc, cam, p["p"].matrix_world.translation + Vector((0, 0, 1.2))) for p in ed.patas if p["g"] == g and p["y"] == -5]
            pies[g] = [q for q in pts if 0 <= q[0] <= 1080 and 0 <= q[1] <= 1920]
        return {"pies_a": pies[0][:8], "pies_b": pies[1][:8]}
    return {"actualizar": act}


def p18(sc, a, b):
    return _grupos(sc, 18)


def p19(sc, a, b):
    return _grupos(sc, 19)


def p20(sc, a, b):
    return _grupos(sc, 20)


def p21(sc, a, b):
    return _grupos(sc, 21)


# =====================================================================================================
# E5 muletas (planos 23–24)
# =====================================================================================================
def _muleta(name, coll, alto=17.0):
    madera = P.mat("MaderaMuleta", (0.78, 0.52, 0.26), rough=0.45, coat=0.4)
    goma = P.mat("GomaMuleta", (0.08, 0.08, 0.08), rough=0.8)
    raiz = P.empty(name, coll=coll)
    sep = 3.0
    for s in (-1, 1):
        rail = P.prim("cyl", name + f"_r{s}", coll, madera, r=0.62, r2=0.62, h=alto * 0.62, seg=16)
        rail.parent = raiz
        rail.location = (s * sep * 0.5, 0, alto * 0.62)
        rail.rotation_euler = (0, -s * math.atan2(sep * 0.4, alto * 0.62), 0)
    pad = ED._caja(name + "_pad", -2.4, 2.4, -0.9, 0.9, alto * 0.92, alto, coll, goma, raiz, bisel=0.3)
    mano = P.prim("cyl", name + "_mano", coll, madera, r=0.38, r2=0.38, h=sep, seg=12)
    mano.parent = raiz
    mano.location = (0, 0, alto * 0.62)
    mano.rotation_euler = (0, R(90), 0)
    eje = P.prim("cyl", name + "_eje", coll, madera, r=0.55, r2=0.55, h=alto * 0.32, seg=16)
    eje.parent = raiz
    eje.location = (0, 0, alto * 0.16)
    punta = P.prim("cyl", name + "_punta", coll, goma, r=0.7, r2=0.62, h=1.0, seg=16)
    punta.parent = raiz
    punta.location = (0, 0, 0.4)
    return raiz


def _muletas_set(sc):
    S = _obra(sc)
    for ob in bpy.data.objects:
        if ob.name.startswith(("Cono", "Monton", "Huella")):
            ob.hide_render = True
    m1 = _muleta("MuletaIzq", S["coll"])
    m2 = _muleta("MuletaDer", S["coll"])
    return S, m1, m2


def _muletas(sc, plano):
    S, m1, m2 = _muletas_set(sc)
    ed = S["ed"]
    cam = _cam(sc, 22, -0.21)
    t0, t1 = E.T[plano]
    t23, t24 = E.T[23][0], E.T[24][0]

    def act(f):
        t = t_de(f)
        e1 = sale(lin(t, t23 + 0.15, t23 + 0.75))
        e2 = sale(lin(t, t23 + 0.85, t23 + 1.45))
        sube = suave(lin(t, t24 + 0.1, t24 + 1.0))
        paso = suave(lin(t, t24 + 1.0, t24 + 2.0))
        z = -ed.z_cuerpo + 2.4 * sube
        tamb = R(2.5) * math.sin(lin(t, t24 + 1.0, t24 + 2.0) * math.pi * 2) * (1 - paso * 0.5)
        x = 3.0 * paso
        ed.poner(0.0, ED.recta(x, 0, 0), alto=z, visibles=0, sin_pasos=True, marco=False)
        ed.raiz.rotation_euler = (tamb, 0, 0)
        for m_, e, s in ((m1, e1, -1), (m2, e2, 1)):
            m_.location = (s * 10.5 + x, -8.8 - 26 * (1 - e), 2.4 * sube)
            m_.rotation_euler = (R(-7.5) - R(25) * (1 - e), s * R(3), 0)
            for o in m_.children_recursive:
                o.hide_render = e <= 0.001
        xx = suave(lin(t, t0, t1))
        E.mirar(cam, Vector((-24 + 3 * xx, -54, 3.0)), (x, -6, 10.0))
    return {"actualizar": act}


def p23(sc, a, b):
    return _muletas(sc, 23)


def p24(sc, a, b):
    return _muletas(sc, 24)


# =====================================================================================================
# E6 mapa (planos 25–27): vista cenital, la curva y el giro de 21°
# =====================================================================================================
MAPA_INI = (-18.0, -38.0, R(90))          # el edificio camina hacia arriba de la pantalla (+y)


def _mapa(sc, plano):
    S = _obra(sc, sol=dict(elev=55.0, azim=-40.0, fuerza=4.4))
    ed = S["ed"]
    cam = E.camara(sc, lens=50)
    cam.data.type = "ORTHO"
    t0, t1 = E.T[plano]
    t25, t27 = E.T[25][0], E.T[27]
    pose = ED.curva(62.0, R(-21), *MAPA_INI)

    def act(f):
        t = t_de(f)
        if plano < 27:
            d = 0.0
        else:
            d = 62.0 * suave(lin(t, t27[0] + 0.1, t27[1] - 0.05))
        ed.poner(d, pose, bob=0.0)
        z = lin(t, t25, t27[1])
        cam.data.ortho_scale = 150 - 14 * z
        cam.location = (-2, -6, 180)
        cam.rotation_quaternion = Euler((0, 0, 0)).to_quaternion()
        bpy.context.view_layer.update()
        camino = [E.pantalla(sc, cam, (*pose(s)[:2], 0)) for s in [i * 62 / 24 for i in range(25)]]
        x0, y0, yaw0 = MAPA_INI
        rieles = [E.pantalla(sc, cam, (x0 + s * math.cos(yaw0) + o * math.cos(yaw0 + R(90)), y0 + s * math.sin(yaw0) + o * math.sin(yaw0 + R(90)), 0))
                  for o in (-6, 6) for s in (-10, 80)]
        c = E.pantalla(sc, cam, (*pose(d)[:2], 0))
        return {"camino": camino, "rieles": rieles, "centro": c, "giro": round(math.degrees(abs(pose(d)[2] - yaw0)), 2), "d": round(d, 2)}
    return {"actualizar": act}


def p25(sc, a, b):
    return _mapa(sc, 25)


def p26(sc, a, b):
    return _mapa(sc, 26)


def p27(sc, a, b):
    return _mapa(sc, 27)


# =====================================================================================================
# E7 timelapse (planos 28–30): 62 m y 18 días
# =====================================================================================================
TL_X0 = -31.0


def _huincha(coll):
    am = P.mat("Huincha", (1.0, 0.78, 0.10), rough=0.4)
    h = ED._caja("Huincha", 0, 1, -0.25, 0.25, 0.02, 0.06, coll, am)
    h.location = (TL_X0, -9.0, 0)
    marcas = []
    neg = P.mat("HuinchaMarca", (0.05, 0.05, 0.05), rough=0.5)
    for k in range(63):
        m = ED._caja(f"Marca{k}", -0.04, 0.04, -0.25, 0.05 + (0.15 if k % 10 == 0 else 0), 0.061, 0.07, coll, neg)
        m.location = (TL_X0 + k, -9.0, 0)
        marcas.append(m)
    return h, marcas


def _timelapse(sc, plano):
    S = _obra(sc)
    ed = S["ed"]
    sol, sky, bg = C.cielo(sc)
    h, marcas = _huincha(S["coll"])
    cam = _cam(sc, 22 if plano == 28 else 17, -0.115 if plano == 28 else -0.10)
    t0, t1 = E.T[plano]
    tA, tB = E.T[28][0], E.T[30][1]
    t29 = E.T[29]
    pose = ED.recta(0, 0, 0)

    def act(f):
        t = t_de(f)
        u = lin(t, tA + 0.1, tB - 0.3)
        d = TL_X0 + 62.0 * u
        largo = max(0.01, d - TL_X0)
        ed.poner(d, pose)
        h.scale.x = largo
        for k, m in enumerate(marcas):
            m.hide_render = k > largo
        # 18 días en el plano 29: el sol da vueltas y el cielo baja (sin parpadear a negro)
        dia = lin(t, t29[0] + 0.05, t29[1] - 0.05)
        ang = 2 * math.pi * 3 * dia
        el = 32 + 22 * math.sin(ang)
        az = -58 + 360 * 3 * dia
        d_ = Vector((math.sin(R(az)) * math.cos(R(el)), -math.cos(R(az)) * math.cos(R(el)), math.sin(R(el))))
        sol.rotation_euler = (-d_).to_track_quat("-Z", "Y").to_euler()
        luz = 0.55 + 0.45 * math.cos(ang) if 0 < dia < 1 else 1.0
        sol.data.energy = 4.6 * luz
        bg.inputs["Strength"].default_value = 0.22 * (0.45 + 0.55 * luz)
        if plano == 28:
            E.mirar(cam, (d - 6, -30, 1.4), (d + 3, 0, 2.6))
        else:
            E.mirar(cam, (-14, -58, 4.5), (0, 0, 7.5))
        return {"dist": round(largo, 2), "dia": int(min(18, 1 + 17 * dia)) if plano == 29 else (18 if plano == 30 else 0)}
    return {"actualizar": act}


def p28(sc, a, b):
    return _timelapse(sc, 28)


def p29(sc, a, b):
    return _timelapse(sc, 29)


def p30(sc, a, b):
    return _timelapse(sc, 30)


# =====================================================================================================
# E8 sala de conciertos de 2003 (planos 32–34): sobre rieles, sin patas; la autopista elevada
# =====================================================================================================
def _sala(coll):
    piedra = ED.mat_estuco("PiedraSala", (0.80, 0.70, 0.55))
    raiz = P.empty("Sala", coll=coll)
    ED._caja("SalaCuerpo", -15, 15, -10, 10, 0.8, 16, coll, piedra, raiz)
    ED._caja("SalaZocalo", -15.4, 15.4, -10.4, 10.4, 0.6, 2.2, coll, P.mat("Granito", (0.45, 0.43, 0.40), rough=0.6), raiz)
    ED._caja("SalaCornisa", -15.8, 15.8, -10.8, 10.8, 15.4, 16.4, coll, piedra, raiz)
    ED._caja("SalaAtico", -9, 9, -6, 6, 16.4, 20, coll, P.mat("CobreVerde", (0.30, 0.48, 0.42), rough=0.5, metal=0.3), raiz)
    for i in range(6):                       # pórtico de columnas
        x = -8.75 + 3.5 * i
        col = P.prim("cyl", f"SalaCol{i}", coll, piedra, r=0.65, r2=0.6, h=11.5, seg=20)
        col.parent = raiz
        col.location = (x, -11.6, 2.2 + 5.75)
    ED._caja("SalaFrontis", -10.4, 10.4, -12.6, -10.4, 13.7, 15.4, coll, piedra, raiz)
    import bmesh
    bm = bmesh.new()
    v = [bm.verts.new(p) for p in ((-10.6, -12.6, 15.4), (10.6, -12.6, 15.4), (0, -12.6, 19.2), (-10.6, -10.4, 15.4), (10.6, -10.4, 15.4), (0, -10.4, 19.2))]
    bm.faces.new((v[0], v[1], v[2]))
    bm.faces.new((v[3], v[5], v[4]))
    bm.faces.new((v[0], v[2], v[5], v[3]))
    bm.faces.new((v[1], v[4], v[5], v[2]))
    fr = P.mesh_obj("SalaFrontón", bm, coll, smooth=False, m=piedra)
    fr.parent = raiz
    vid = ED.mat_vidrio()
    for s in (-1, 1):
        for i in range(4):
            y = -7 + 4.5 * i
            ED._caja(f"SalaVent{s}{i}", s * 15.0 - 0.08, s * 15.0 + 0.08, y, y + 2.2, 5.0, 12.5, coll, vid, raiz)
    for i in range(5):
        ED._caja(f"SalaPuerta{i}", -7.4 + 3.5 * i, -6.0 + 3.5 * i, -10.1, -10.0, 2.2, 7.5, coll, vid, raiz)
    return raiz


def _autopista(coll, n=24):
    horm = P.mat("HormigonAutopista", (0.62, 0.61, 0.59), rough=0.8)
    tramos = []
    for k in range(n):
        y = -110 + 10 * k
        t = ED._caja(f"Tramo{k}", -7, 7, y, y + 9.9, 11, 12.4, coll, horm)
        p = ED._caja(f"Pilar{k}", -1.2, 1.2, y + 4, y + 6, 0, 11, coll, horm)
        tramos.append((t, p, y))
    autos = []
    for k in range(6):
        col = [(0.85, 0.15, 0.1), (0.95, 0.95, 0.95), (0.1, 0.3, 0.7), (0.15, 0.15, 0.15)][k % 4]
        a = ED._caja(f"AutoPista{k}", -1.0, 1.0, -2.2, 2.2, 12.4, 13.8, coll, P.mat(f"Auto{k % 4}", col, rough=0.3, metal=0.4), bisel=0.3)
        autos.append(a)
    return tramos, autos


def _sala_set(sc):
    S = _obra(sc, edificio=False, sol=dict(elev=36.0, azim=-50.0, fuerza=4.6))
    for ob in bpy.data.objects:     # otra calle: sin la obra
        if ob.name.startswith(("SueloObra", "Reja", "Grua", "Cono", "Oficina", "VigaPila", "Monton", "Huella")):
            ob.hide_render = True
    sala = _sala(S["coll"])
    acero = P.mat("Riel", (0.35, 0.33, 0.32), rough=0.4, metal=0.9)
    for s in (-7, 7):
        ED._caja(f"Riel{s}", -20, 90, -0.12 + s, 0.12 + s, -0.3, 0.25, S["coll"], acero)
    for k in range(40):
        ED._caja(f"Durmiente{k}", -20 + 2.8 * k, -19 + 2.8 * k, -9, 9, -0.3, 0.0, S["coll"], P.mat("Durmiente", (0.30, 0.22, 0.15), rough=0.9))
    tramos, autos = _autopista(S["coll"])
    return S, sala, tramos, autos


def _sala_plano(sc, plano):
    S, sala, tramos, autos = _sala_set(sc)
    cam = _cam(sc, 26 if plano != 33 else 24, -0.03)
    t0, t1 = E.T[plano]
    t33, t34 = E.T[33], E.T[34]

    def act(f):
        t = t_de(f)
        u = suave(lin(t, t33[0] + 0.1, t33[1] - 0.1))
        sala.location = (66.46 * u, 0, 0)
        arma = lin(t, t34[0] + 0.05, t34[1] - 0.1)
        for k, (tr, pi, y) in enumerate(tramos):
            vis = arma * len(tramos) > k
            tr.hide_render = not vis
            pi.hide_render = not vis
        for k, a_ in enumerate(autos):
            a_.hide_render = arma < 0.98 if plano == 34 else True
            a_.location = (-3.5 if k % 2 else 3.5, ((t - t34[0]) * 28 * (1 if k % 2 else -1) + 40 * k) % 230 - 110, 0)
        if plano == 32:
            x = sale(lin(t, t0, t1))
            E.mirar(cam, (-70, -110, 70 - 25 * x), (0, 0, 6))
        elif plano == 33:
            E.mirar(cam, (66.46 * u - 34, -62, 12), (66.46 * u + 2, 0, 8))
        else:
            x = suave(lin(t, t0, t1))
            E.mirar(cam, (-80, -95, 40 + 20 * x), (20, 0, 8))
        bpy.context.view_layer.update()
        return {"metros": round(66.46 * u, 1)}
    return {"actualizar": act}


def p32(sc, a, b):
    return _sala_plano(sc, 32)


def p33(sc, a, b):
    return _sala_plano(sc, 33)


def p34(sc, a, b):
    return _sala_plano(sc, 34)


# =====================================================================================================
def _pieza(k, fn, **kw):
    a, b = FR(k)
    return dict(a=a, b=b, fn=fn, plano=k, **kw)


FUNC = {1: p01, 2: p02, 3: p03, 4: p04, 5: p05, 6: p06, 7: p07, 8: p08, 9: p09, 10: p10, 11: p11, 12: p12,
        13: p13, 14: p14, 15: p15, 16: p16, 17: p17, 18: p18, 19: p19, 20: p20, 21: p21, 22: p22, 23: p23, 24: p24,
        25: p25, 26: p26, 27: p27, 28: p28, 29: p29, 30: p30, 31: p31, 32: p32, 33: p33, 34: p34, 35: p35, 36: p36}
ESCENA = {1: "E1", 2: "E1", 3: "E1", 4: "E1", 12: "E1", 22: "E1", 31: "E1", 5: "E2", 6: "E2", 7: "E2", 8: "E2", 9: "E2", 10: "E2",
          11: "E2", 13: "E3", 14: "E3", 15: "E3", 16: "E3", 17: "E3", 18: "E4", 19: "E4", 20: "E4", 21: "E4", 23: "E5", 24: "E5",
          25: "E6", 26: "E6", 27: "E6", 28: "E7", 29: "E7", 30: "E7", 32: "E8", 33: "E8", 34: "E8", 35: "E9", 36: "E9"}
PIEZAS = {str(k): _pieza(k, fn) for k, fn in FUNC.items() if k in E.T}
