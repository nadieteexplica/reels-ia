"""Planos del Ep. 5 v3 (proceso v2, estilo realista): 4 escenas, 16 planos (storyboard.md v3).

E1 imán de la rana — el electroimán sobre su losa en medio del salar al atardecer; la rana (escaneo real, 2,2 cm) flota
                     dentro del tubo de vidrio en la boca. Planos 3, 4, 5, 8 y 11 (el hueco de 3 cm visto desde arriba).
E2 adentro         — moléculas de agua entre células del tejido; las líneas del imán suben y a la molécula le sale su
                     empujón. Plano 7.
E4 imán gigante    — Pete en el salar ("como tú"); se arma el imán para una persona en 3 pasos: el hueco sale del suelo,
                     caen las bobinas y la carcasa, cae la tapa, y los cables cruzan el salar hasta la central nuclear.
                     Planos 6, 9, 10, 12, 13, 14 y 15.
E5 Pete flota      — Pete flota sobre la boca del imán gigante (SIMULACIÓN). Planos 1 (cuadro 0), 2 y 16 (vuelve al 0).

Cada pieza arma su escena y devuelve actualizar(f) (todo calculado por cuadro, sin keyframes) y su meta para el post.
"""
import math, os, random, sys
import bpy
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../plantilla")))
import ep05 as E
from ep05 import F, FR, T, lin, suave, sale, tramo, ruido, clamp, mirar, orbita, pantalla, oculto

FPS = 30
POSE = os.environ.get("POSE", "")
ESCENA = {1: "E5", 2: "E5", 3: "E1", 4: "E1", 5: "E1", 6: "E4", 7: "E2", 8: "E1", 9: "E4", 10: "E4", 11: "E1",
          12: "E4", 13: "E4", 14: "E4", 15: "E4", 16: "E5"}


def TW(prefijo, desde=0.0):
    return E.t_palabra(prefijo, desde)


def tf(f):
    return (f - 1) / FPS


# ===================================== E1 · el imán de la rana ======================================
Z0 = 0.08
BOCA = Z0 + 1.25 + 0.025
RANA_Z = BOCA + 0.045
LARGO_RANA = 0.022
ROT0 = (math.radians(6), math.radians(-6), math.radians(78))     # 3/4 hacia cámara: se ve un ojo (puerta 4 r1)
ALTO_CAM = 0.075                                                  # cámara 7,5 cm sobre la rana: de fondo, el salar a contraluz (azul)
R_CERCA = 0.22                                                   # la rana ocupa ~la mitad del ancho (cuadro A v2)
CABEZA = Vector((-0.008, -0.004, 0.002))                         # foco en la cabeza (el ojo), no en el centro
R_TUBO = 0.0158                                                  # tubo de vidrio: 3,16 cm de ancho (el hueco de 3,2 cm de Geim)
TOPE_TUBO = BOCA - 0.01 + 0.11


def armar_E1(sc):
    E.cielo_atardecer(sc, elev=2.5, rot=35, fuerza=0.35, sol=3.5)     # como el cuadro A v2.1
    sc.view_settings.exposure = -0.2
    E.salar(sc)
    E.cerros(sc)
    E.plataforma(sc)
    piezas = E.iman_lab(sc, alto=1.25, r=0.42, r_hueco=0.017)
    for p in piezas:
        p.location.z += Z0
    rana = E.rana(sc, LARGO_RANA)
    rana.location = (0, 0, RANA_Z)
    rana.rotation_euler = ROT0
    rana["s0"] = rana.scale.x
    bpy.context.view_layer.update()
    E.gotitas(sc, rana, 10, (0.00012, 0.00025))      # antes del tubo: los rayos de las gotitas tienen que tocar la piel, no el vidrio
    tubo = E.tubo(sc, "Tubo_vidrio", R_TUBO, 0.0148, 0.11, (0, 0, BOCA - 0.01), verts=96, mat=E.mat_acrilico(), bisel=0.0004)
    tubo["no_tapa_ojos"] = 1
    E.ojos_rana(sc, rana, LARGO_RANA)
    reb = E.luz_area(sc, "Rebote", (-0.22, -0.32, BOCA + 0.12), (0, 0, RANA_Z), 3.5, (1.0, 0.88, 0.78), 0.3)
    if reb is not None:
        reb.visible_glossy = False            # su reflejo en el vidrio se veía como una mancha clara junto a la rana (plano 8 v2)
    cam = E.camara(sc, (0.021, -R_CERCA, RANA_Z + ALTO_CAM), (0, 0, RANA_Z), lente=100, fstop=8.0)
    return {"rana": rana, "tubo": tubo, "cam": cam}


def rana_flota(rana, f, extra_z=0.0, giro=0.0):
    """Flota quieta en el aire: sube y baja 0,6 mm, gira apenas (±8° como máximo: nunca toca el vidrio) y respira (el
    cuerpo se infla 0,7 % y vuelve, ~1 vez por segundo: en el v2 se veía quieta como un modelo)."""
    rana.location = (0.0005 * ruido(f, 3, 0.4), 0.0005 * ruido(f, 4, 0.4), RANA_Z + 0.0006 * math.sin(f / 30 * 2.1) + extra_z)
    rana.rotation_euler = (ROT0[0] + math.radians(2.5 * ruido(f, 5, 0.3)), ROT0[1] + math.radians(2.5 * ruido(f, 6, 0.3)),
                           ROT0[2] + math.radians(giro))
    resp = 0.5 - 0.5 * math.cos(2 * math.pi * (f - 1) / 30 * 1.1)
    s0 = rana.get("s0", rana.scale.x)
    rana.scale = (s0 * (1 + 0.004 * resp), s0 * (1 + 0.007 * resp), s0 * (1 + 0.007 * resp))


def p_orbita(sc, a, b, ang0, ang1):
    S = armar_E1(sc)
    cam, rana = S["cam"], S["rana"]
    c = Vector((0, 0, RANA_Z))

    def act(f):
        x = suave(lin(f, a, b - 1))
        ang = ang0 + (ang1 - ang0) * x
        rana_flota(rana, f, giro=4 * math.sin((f - 1) / 30 * 0.7))
        p = orbita(c, R_CERCA, ang, ALTO_CAM)
        mirar(cam, p, c + Vector((0, 0, -0.008)), foco=c + CABEZA)      # la rana queda en y ~650 (lejos de los subtítulos)
        return {"rana": pantalla(sc, cam, rana.location)}
    return {"actualizar": act}


def p3(sc, a, b):
    # "Ya pasó con esta rana: flota…": la rana real (el cuadro A del v2), órbita de 35°
    return p_orbita(sc, a, b, -15, 20)


def p4(sc, a, b):
    # "…sola dentro de un imán.": desde arriba por la boca del tubo (no hay nada sobre la rana) y la grúa se aleja hasta
    # el electroimán entero sobre su losa en el salar (los planos 2 y 3 del v2 en uno)
    S = armar_E1(sc)
    cam, rana = S["cam"], S["rana"]
    c = Vector((0, 0, RANA_Z))
    t0 = T[4][0]
    arriba0 = Vector((0.02, -0.08, RANA_Z + 0.24))
    arriba1 = Vector((0.03, -0.11, RANA_Z + 0.30))
    lejos = Vector((1.5, -3.4, 1.05))

    def act(f):
        t = tf(f)
        rana_flota(rana, f)
        x1 = suave(lin(t, t0, t0 + 0.55))
        x2 = sale(suave(lin(t, t0 + 0.45, T[4][1] - 0.05)))
        p = arriba0.lerp(arriba1, x1).lerp(lejos, x2)
        tgt = (c + Vector((0, -0.009, -0.004))).lerp(Vector((0, 0, 0.85)), x2)
        lente = 100 - 25 * x1 - 45 * x2
        mirar(cam, p, tgt, lente=lente, foco=Vector((0, 0, 0.9)) if x2 > 0.3 else c)
        return {"iman": pantalla(sc, cam, (0, 0, 0.9)), "rana": pantalla(sc, cam, (0, 0, RANA_Z))}
    return {"actualizar": act}


def p5(sc, a, b):
    # "Es más que nada agua,": push-in hasta el ojo y la piel mojada (el plano 4 del v2)
    S = armar_E1(sc)
    cam, rana = S["cam"], S["rana"]

    def act(f):
        x = lin(f, a, b - 1) ** 1.6
        rana_flota(rana, f)
        c = Vector((0, 0, RANA_Z + 0.003))
        p0 = orbita(Vector((0, 0, RANA_Z)), R_CERCA, -10, ALTO_CAM)
        # termina frente a la cabeza (el ojo al centro del cuadro, nunca bajo la interfaz: chequeo cara_bajo_ui del v2);
        # se frena ~2,5 mm antes del vidrio (radio 15,8 mm), por el lado de la cabeza y un poco desde arriba
        ojos = [bpy.data.objects.get(n) for n in ("Rana_ojoL", "Rana_ojoR")]
        bpy.context.view_layer.update()
        cab = sum((o.matrix_world.translation for o in ojos if o), Vector()) / max(1, sum(1 for o in ojos if o))
        p1_ = Vector((p0.x, p0.y, 0)).normalized() * 0.0183 + Vector((0, 0, cab.z + 0.006))
        p = p0.lerp(p1_, x)
        mirar(cam, p, (c + Vector((0, 0, -0.008))).lerp(cab, x), lente=100, foco=c.lerp(cab, x))
        cam.data.dof.aperture_fstop = 5.6 + 6 * x
        return {}
    return {"actualizar": act}


def p8(sc, a, b):
    # "Con uno bien fuerte, ese empujón le gana a la gravedad.": flechas al lado de la rana (post); sube 4 mm en "gana"
    S = armar_E1(sc)
    cam, rana = S["cam"], S["rana"]
    c = Vector((0, 0, RANA_Z))
    t_gana = TW("gana", 14.0)

    def act(f):
        x = suave(lin(f, a, b - 1))
        sube = 0.004 * suave(lin(tf(f), t_gana - 0.6, t_gana + 0.6))
        rana_flota(rana, f, extra_z=sube)
        r = 0.40 - 0.03 * x
        p = orbita(c, r, 12, ALTO_CAM * r / R_CERCA)             # mismo ángulo que el cuadro A: de fondo la sal a contraluz
        mirar(cam, p, c + Vector((0.009, 0, -0.016)), foco=c + CABEZA)
        return {"rana": pantalla(sc, cam, rana.location), "lado": pantalla(sc, cam, rana.location + Vector((0.016, 0.004, 0)))}
    return {"actualizar": act}


def p11(sc, a, b):
    # "El de la rana mide tres centímetros: ni tu mano cabe.": de costado y de cerca, el tubo con la rana adentro (la cota
    # de 3 cm va de pared a pared, 9 mm por ENCIMA de la rana: puerta 3 r1); en "mano" la cámara se aleja y el post dibuja el
    # contorno de una mano adulta a escala real al lado del tubo (misma proyección)
    S = armar_E1(sc)
    cam, rana = S["cam"], S["rana"]
    c = Vector((0, 0, RANA_Z))
    t_tres = TW("tres", 22.0)
    t_mano = TW("mano", 23.0)

    def act(f):
        t = tf(f)
        rana_flota(rana, f, giro=4 * math.sin((f - 1) / 30 * 0.6))
        x1 = suave(lin(t, T[11][0], t_tres + 0.4))
        x2 = suave(lin(t, t_mano - 0.75, t_mano + 0.15))
        r = 0.32 - 0.05 * x1 + (1.4 - 0.27) * x2
        lente = 100 - 40 * x2
        ang = -6 + 6 * x1 + 4 * x2
        p = orbita(c, r, ang, 0.02 + 0.08 * x2)
        der = Vector((math.cos(math.radians(ang)), math.sin(math.radians(ang)), 0))
        # la rana en y ~620 (sobre los subtítulos) y, ya lejos, en x ~700 (a la izquierda va la mano)
        baja = 0.354 * r * 12 / lente
        izq = 0.296 * r * 6.75 / lente * x2
        mirar(cam, p, c - Vector((0, 0, baja)) - der * izq, lente=lente, foco=c + CABEZA)
        cam.data.dof.aperture_fstop = 8 + 8 * x2
        zc = RANA_Z + 0.009
        return {"izq": pantalla(sc, cam, -der * R_TUBO + Vector((0, 0, zc))), "der": pantalla(sc, cam, der * R_TUBO + Vector((0, 0, zc))),
                "mano_c": pantalla(sc, cam, c - der * 0.09 + Vector((0, 0, -0.012))),
                "mano_m": pantalla(sc, cam, c - der * 0.08 + Vector((0, 0, -0.012))),
                "rana": pantalla(sc, cam, rana.location)}
    return {"actualizar": act}


# ===================================== E2 · adentro de la rana ======================================
def armar_E2(sc):
    w_ = E.mundo(sc, "studio.hdr", 0.05)
    bg = w_.node_tree.nodes["Background"]
    mix = w_.node_tree.nodes.new("ShaderNodeMixRGB"); mix.blend_type = "MULTIPLY"; mix.inputs[0].default_value = 1.0
    mix.inputs[2].default_value = (0.5, 0.12, 0.1, 1)
    env = bg.inputs[0].links[0].from_node
    w_.node_tree.links.new(env.outputs[0], mix.inputs[1]); w_.node_tree.links.new(mix.outputs[0], bg.inputs[0])
    mats = (E.mat_molecula("oxigeno", (0.78, 0.07, 0.05)), E.mat_molecula("hidrogeno", (0.92, 0.93, 0.95), 0.12))
    random.seed(11)
    mols = []
    for i in range(80):
        p = Vector((random.uniform(-3.6, 3.6), random.uniform(-1.5, 9.0), random.uniform(-3.0, 7.0)))
        if p.y < 2.0 and abs(p.x) < 1.3 and 0.6 < p.z < 5.5:
            continue
        m = E.molecula_agua(sc, p, (random.uniform(0, 6.3), random.uniform(0, 6.3), random.uniform(0, 6.3)), 0.55, mats, f"H2O_{i}")
        m["giro"] = (random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))
        mols.append(m)
    heroe = E.molecula_agua(sc, (0.0, 0.0, 1.9), (math.radians(20), math.radians(-25), math.radians(35)), 1.0, mats, "H2O_heroe")
    E.tejido(sc)
    lineas = []
    for i, x in enumerate((-2.4, -1.3, -0.4, 0.5, 1.4, 2.5)):
        y = 1.5 + 0.6 * (i % 3)
        pts = [(x * 0.35, y, -4.0), (x * 0.5, y, -1.0), (x * 0.8, y, 2.0), (x * 1.3, y, 5.0), (x * 2.0, y, 8.0)]
        lineas.append(E.linea_campo(sc, f"campo{i}", pts, 0.012, (0.15, 0.75, 1.0), 1.6))
    fl_h = E.flecha(sc, "empujon_heroe", (0.0, 0.0, 2.45), 1.2, 0.05)
    E.luz_area(sc, "Llave", (-3.5, -4.0, 6.0), (0, 0, 1.9), 900, (1.0, 0.9, 0.82), 2.5)
    E.luz_area(sc, "Contra", (2.5, 4.0, 4.5), (0, 0, 1.9), 600, (0.5, 0.8, 1.0), 1.5)
    E.luz_punto(sc, "Brillo_abajo", (0, 1.5, -2.0), 300, (0.25, 0.8, 1.0), 1.0)
    cam = E.camara(sc, (1.3, -8.8, 2.7), (0, 0, 2.1), lente=50, fstop=2.2)
    return {"mols": mols, "heroe": heroe, "lineas": lineas, "fl_h": fl_h, "cam": cam}


def _giro_mols(S, f):
    for m in S["mols"]:
        g = m["giro"]
        m.rotation_euler = (m.rotation_euler.x + 0.004 * g[0], m.rotation_euler.y + 0.004 * g[1], m.rotation_euler.z + 0.004 * g[2])
    S["heroe"].rotation_euler.z = math.radians(35) + 0.25 * math.sin(f / 30 * 0.8)


def _lineas(S, x):
    for l in S["lineas"]:
        l.data.bevel_factor_end = max(0.001, x)
        l.hide_render = x <= 0.002


def p7(sc, a, b):
    # "Y al agua, un imán la empuja... un poquito.": suben las líneas del imán y a la molécula le sale su empujón
    S = armar_E2(sc)
    cam = S["cam"]
    t_emp = TW("empuja", 10.0)
    t0 = T[7][0]

    def act(f):
        x = suave(lin(f, a, b - 1))
        _giro_mols(S, f)
        _lineas(S, sale(lin(tf(f), t0 + 0.2, t0 + 1.6)))
        s = sale(lin(tf(f), t_emp, t_emp + 0.35))
        for o in S["fl_h"]:
            o.hide_render = s <= 0.002
        c, p = S["fl_h"]
        c.scale = (1, 1, max(s, 0.001)); c.location = (0, 0, 2.45 + 0.42 * max(s, 0.001))
        p.scale = (max(s, 0.001),) * 3; p.location = (0, 0, 2.45 + 1.02 * max(s, 0.001))
        S["heroe"].location.z = 1.9 + 0.06 * sale(lin(tf(f), t_emp + 0.2, t_emp + 1.2))
        ang = -8 + 14 * x
        p_ = orbita(Vector((0, 0, 2.1)), 9.2, ang, 0.6)
        mirar(cam, p_, Vector((0, 0, 2.1)), foco=Vector((0, 0, 1.9)))
        return {"heroe": pantalla(sc, cam, (0, 0, 1.9))}
    return {"actualizar": act}


# ===================================== Pete ======================================
def cargar_pete(sc):
    if os.path.exists(os.path.join(E.ASSETS, E.PETE_FBX)):
        arm = E.pete(sc, None)
        anim = None
        if POSE and os.path.isfile(POSE):
            antes = set(bpy.data.objects)
            bpy.ops.import_scene.fbx(filepath=POSE, automatic_bone_orientation=False)
            nuevos = [o for o in bpy.data.objects if o not in antes]
            anim = next(o for o in nuevos if o.type == "ARMATURE")
            for o in nuevos:
                o.hide_render = True
        pestanas = next((o for o in sc.objects if o.type == "MESH" and "Eyelash" in o.name), None)
        ojos = [E.marca_ojo(sc, f"Pete_ojo{l}", None, (0, 0, 0), 0.012) for l in "LR"]
        return {"arm": arm, "anim": anim, "pestanas": pestanas, "ojos": ojos}
    o = E.cilindro(sc, "Pete_prueba", 0.22, 1.79, (0, 0, 0), mat=E.mat_pintura("prueba", (0.7, 0.3, 0.1)))
    return {"arm": o, "anim": None, "pestanas": None, "ojos": []}


def _largo_anim(anim):
    ad = anim.animation_data
    if ad and ad.action:
        a, b = ad.action.frame_range
        return int(a), max(2, int(round(b - a)))
    return 1, 60


def pose_pete(sc, P, f, cabeza=(0.0, 0.0), cuadro_anim=None):
    """Pose de Pete en el cuadro f: copia la de Happy Idle (en loop con todo el largo de la animación de Mixamo, que
    empalma) y gira la cabeza (pitch, yaw en grados). cuadro_anim = índice dentro de la animación (por defecto, f)."""
    arm, anim = P["arm"], P["anim"]
    if anim is None or arm.type != "ARMATURE":
        return
    a0, n = _largo_anim(anim)
    fa = a0 + ((cuadro_anim if cuadro_anim is not None else f) % n)
    sc.frame_set(fa)
    dst = {b.name.split(":")[-1]: b for b in arm.pose.bones}
    for b in anim.pose.bones:
        d = dst.get(b.name.split(":")[-1])
        if d is not None:
            d.rotation_mode = "QUATERNION"
            d.rotation_quaternion = b.rotation_quaternion.copy()
    bpy.context.view_layer.update()
    rz = Matrix.Rotation(math.radians(P.get("giro", 0.0)), 3, "Z")
    eje_x, eje_y = rz @ Vector((1, 0, 0)), rz @ Vector((0, 1, 0))     # izquierda y atrás de Pete (mira hacia -Y sin girar)
    if cabeza != (0.0, 0.0):
        E.rotar_hueso_mundo(arm, "Head", eje_x, cabeza[0])
        if cabeza[1]:
            E.rotar_hueso_mundo(arm, "Head", (0, 0, 1), cabeza[1])
    if P.get("flota"):
        # capa de flotar sobre el idle (puerta 3 v3): brazos abiertos con un vaivén lento de equilibrio, rodillas sueltas y
        # la punta de los pies hacia abajo (el idle de pie se leía "parado sobre un vidrio")
        i = cuadro_anim if cuadro_anim is not None else f
        sw = 4 * math.sin(i / 30 * 1.3)
        E.rotar_hueso_mundo(arm, "LeftArm", eje_y, -(18 + sw))
        E.rotar_hueso_mundo(arm, "RightArm", eje_y, 18 + sw)
        E.rotar_hueso_mundo(arm, "LeftLeg", eje_x, 12)
        E.rotar_hueso_mundo(arm, "RightLeg", eje_x, 8)
        E.rotar_hueso_mundo(arm, "LeftFoot", eje_x, 22)
        E.rotar_hueso_mundo(arm, "RightFoot", eje_x, 26)
    ojos_pete(sc, P)


def ojos_pete(sc, P, cam=None):
    """Ubica las marcas de los ojos en el centro de cada grupo de pestañas (malla deformada), un poco hacia la cámara."""
    if not P["pestanas"] or not P["ojos"]:
        return
    dg = bpy.context.evaluated_depsgraph_get()
    ev = P["pestanas"].evaluated_get(dg)
    me = ev.to_mesh()
    mw = ev.matrix_world
    pts = [mw @ v.co for v in me.vertices]
    ev.to_mesh_clear()
    if not pts:
        return
    cx = sum(p.x for p in pts) / len(pts)
    for o, lado in zip(P["ojos"], (1, -1)):
        g = [p for p in pts if (p.x - cx) * lado >= 0] or pts
        c = sum(g, Vector()) / len(g)
        cam = cam or sc.camera
        o.location = c + (cam.matrix_world.translation - c).normalized() * 0.012


def armar_salar_tarde(sc):
    E.cielo_atardecer(sc, elev=5, rot=60, fuerza=0.12, sol=4.0)
    sc.view_settings.exposure = -0.5
    E.salar(sc)
    E.cerros(sc)


# ===================================== E4 / E5 · el imán gigante ======================================
PLANTA = Vector((-1150, 2080, 0))
PETE_E4 = Vector((-3.4, -1.6, 0.0))
PETE_GIRO = -23            # Pete de 3/4 hacia la cámara alta del cuadro B v2
R_BOBINA = (2.4, 0.975)    # bobinas de cobre adentro de la carcasa (r 2,5 / hueco 0,95): quedan tapadas al llegar la carcasa


def armar_E4(sc, bobinas=False, hueco_acero=False):
    armar_salar_tarde(sc)
    E.central_nuclear(sc, pos=tuple(PLANTA))
    antes = set(bpy.data.objects)
    boca = E.iman_gigante(sc)
    piezas = [o for o in bpy.data.objects if o not in antes]
    G = {"boca": boca}
    G["plataforma"] = [o for o in piezas if o.name.startswith("G_plataforma")]
    G["hueco"] = [o for o in piezas if o.name.startswith("G_hueco")]
    G["cuerpo"] = [o for o in piezas if o.name.startswith(("G_cuerpo", "G_escarcha", "G_aro", "G_costilla"))]
    G["tapa"] = [o for o in piezas if o.name.startswith(("G_tapa", "G_cobre", "G_perno"))]
    G["cables"] = [o for o in piezas if o.name.startswith(("G_cable", "G_conector"))]
    for o in G["cuerpo"] + G["tapa"] + G["hueco"]:
        o["z0"] = o.location.z
    if hueco_acero:
        # PASO 1 (planos 10 y 12): el hueco se ve solo, de pie en la losa; de negro plano se leía como un hoyo recortado,
        # no como una pieza de metal: acero oscuro con mugre (por dentro, ya tapado, vuelve a ser la boca negra)
        m = E.mat_acero_industrial("hueco_acero", (0.075, 0.08, 0.085), sucio=0.35, rugo=(0.35, 0.7))
        for o in G["hueco"]:
            E.asignar(o, m)
    G["bobinas"] = []
    if bobinas:
        mb = E.mat_bobina()
        z0, alto = 0.45, 3.1
        for i in range(5):
            h = alto / 5
            o = E.tubo(sc, f"G_bobina{i}", R_BOBINA[0], R_BOBINA[1], h * 0.97, (0, 0, z0 + h * i), verts=192, mat=mb, bisel=0.02)
            o["z0"] = o.location.z
            G["bobinas"].append(o)
    P = cargar_pete(sc)
    E.luz_area(sc, "RellenoPete", (5.0, -13.2, 8.1), (0, 0, 4.4), 25, (1.0, 0.9, 0.82), 2.0, spread=30)   # como en el cuadro B v2
    cam = E.camara(sc, (7.0, -18.5, 3.4), (0, 0, 2.4), lente=35, fstop=8.0)
    return {"G": G, "P": P, "cam": cam}


def caer(o, t, tl, alto=9.0, dur=None):
    """La pieza o cae desde alto m sobre su lugar y llega en tl (acelera como algo pesado; rebota 2 cm al llegar)."""
    dur = dur or E.CAIDA
    if tl is None:
        o.hide_render = False
        o.location.z = o["z0"]
        return
    x = lin(t, tl - dur, tl)
    o.hide_render = t < tl - dur
    rebote = 0.02 * math.sin(math.pi * clamp((t - tl) / 0.18)) if t > tl else 0.0
    o.location.z = o["z0"] + alto * (1 - x * x) + rebote


def estado_iman(S, t, llegada):
    """llegada(o) → t en que esa pieza (carcasa, aros, tubos o tapa) termina de caer (None = ya está)."""
    for o in S["G"]["cuerpo"] + S["G"]["tapa"]:
        caer(o, t, llegada(o), alto=6.0, dur=0.35) if llegada(o) is not None else caer(o, t, None)


def sin_iman(S):
    """El salar vacío: sólo la losa (para los planos 6 y 9)."""
    for o in S["G"]["cuerpo"] + S["G"]["tapa"] + S["G"]["hueco"] + S["G"]["bobinas"]:
        o.hide_render = True
    cables(S, 0)


def cables(S, x, brillo=0.0):
    for o in S["G"]["cables"]:
        if o.type == "CURVE":
            o.data.bevel_factor_end = max(0.001, x)
        o.hide_render = x <= 0.002
        for s in o.material_slots:
            m = s.material
            b = m.node_tree.nodes.get("Principled BSDF") if m else None
            if b:
                b.inputs["Emission Color"].default_value = (1.0, 0.5, 0.15, 1)
                b.inputs["Emission Strength"].default_value = brillo


def brillo_cobre(S, brillo):
    for o in S["G"]["tapa"]:
        if not o.name.startswith("G_cobre"):
            continue
        for s in o.material_slots:
            if s.material:
                bsdf = s.material.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs["Emission Color"].default_value = (1.0, 0.45, 0.15, 1)
                    bsdf.inputs["Emission Strength"].default_value = brillo


def girar_pete(P, grados, x=0.0, y=0.0):
    P["giro"] = grados
    if P["arm"].type == "ARMATURE":
        base = P["arm"].rotation_euler.copy()
        P["arm"].rotation_euler = (base.x + math.radians(x), base.y + math.radians(y), base.z + math.radians(grados))
    P["rot0"] = P["arm"].rotation_euler.copy()


def temblor(f, golpes, amp=0.035, dur=0.3):
    """Sacudón corto de la cámara en cada llegada (el peso de las piezas)."""
    t = tf(f)
    k = sum(max(0.0, 1 - (t - g) / dur) for g in golpes if 0 <= t - g < dur)
    return Vector((ruido(f, 21, 9.0), ruido(f, 22, 9.0), ruido(f, 23, 9.0))) * amp * min(1.0, k)


def p6(sc, a, b):
    # "como tú.": Pete de pie en el salar vacío, de 3/4 hacia la cámara, cámara al pecho (15° al lado del plano 9: la
    # central queda fuera del cuadro)
    S = armar_E4(sc)
    cam, P = S["cam"], S["P"]
    sin_iman(S)
    P["arm"].location = PETE_E4
    girar_pete(P, 25)
    d = Vector((0.309, -0.951, 0))
    cam.data.dof.aperture_fstop = 2.8

    def act(f):
        x = suave(lin(f, a, b - 1))
        pose_pete(sc, P, f)
        pos = PETE_E4 + d * (8.0 - 0.6 * x) + Vector((0, 0, 1.25))
        mirar(cam, pos, PETE_E4 + Vector((0, 0, 0.9)), lente=50, foco=PETE_E4 + Vector((0, 0, 1.5)))
        return {"pete": pantalla(sc, cam, PETE_E4 + Vector((0, 0, 1.0)))}
    return {"actualizar": act}


def p9(sc, a, b):
    # "¿Y para ti? Habría que construirlo.": Pete junto a la losa vacía mira hacia arriba (el plano 12 del v2)
    S = armar_E4(sc)
    cam, P = S["cam"], S["P"]
    sin_iman(S)
    P["arm"].location = PETE_E4
    girar_pete(P, 25)

    def act(f):
        x = suave(lin(f, a, b - 1))
        sube = suave(lin(tf(f), T[9][0] + 1.1, T[9][0] + 1.7))
        pose_pete(sc, P, f, cabeza=(-30 * sube, 0))
        mirar(cam, Vector((6.0, -17.5, 1.8)).lerp(Vector((5.0, -14.5, 1.75)), x), Vector((-2.0, -0.5, 1.5)), lente=35,
              foco=PETE_E4 + Vector((0, 0, 1.6)))
        return {}
    return {"actualizar": act}


def p10(sc, a, b):
    # "Primero: un hueco donde quepas.": PASO 1, el hueco (tubo de acero de 1,9 m de ancho y 3,1 m de alto) sale del
    # suelo en la losa, a la derecha de Pete (desde la dirección del plano 12: la luz que aprobó el v2)
    S = armar_E4(sc, hueco_acero=True)
    cam, P = S["cam"], S["P"]
    sin_iman(S)
    for o in S["G"]["hueco"]:
        o.hide_render = False
    P["arm"].location = PETE_E4
    girar_pete(P, 25)
    t_pri = TW("primero", 19.0)
    t_lle = t_pri + 1.55
    v = Vector((0.469, 0.883, 0))                  # dirección de la mirada (62°: el sol queda 32° fuera del cuadro)
    r = Vector((0.883, -0.469, 0))
    C0 = PETE_E4 - v * 6.0 + r * 1.0               # Pete a 6 m (a la izquierda), el hueco a 9 m (a la derecha)

    def act(f):
        t = tf(f)
        x = suave(lin(f, a, b - 1))
        s = sale(suave(lin(t, t_pri + 0.15, t_lle)))
        for o in S["G"]["hueco"]:
            o.location.z = o["z0"] - 3.25 * (1 - s)
        mira = suave(lin(t, t_pri + 0.3, t_pri + 1.1))
        pose_pete(sc, P, f, cabeza=(-14 * mira, 0))
        pos = C0 + r * (0.5 * x) + Vector((0, 0, 1.2)) + temblor(f, [t_lle], 0.02)
        tgt = C0 + v * 9.0 + Vector((0, 0, 0.73)) + r * (0.3 * x)
        mirar(cam, pos, tgt, lente=24, foco=PETE_E4 + Vector((0, 0, 1.4)))
        cam.data.dof.aperture_fstop = 8
        return {"pete": pantalla(sc, cam, PETE_E4 + Vector((0, 0, 1.0))), "hueco": pantalla(sc, cam, (0, 0, 3.6))}
    return {"actualizar": act}


def p12(sc, a, b):
    # "Después: bobinas y más bobinas,": PASO 2, 5 bobinas de cobre caen del cielo una tras otra alrededor del hueco y al
    # final la carcasa (con los aros y los tubos) baja encima como una funda; la cámara tiembla en cada golpe
    S = armar_E4(sc, bobinas=True, hueco_acero=True)
    cam, P = S["cam"], S["P"]
    cables(S, 0)
    for o in S["G"]["tapa"]:
        o.hide_render = True
    for o in S["G"]["hueco"]:
        o.hide_render = False
    llega_b, llega_c = E.bobinas_t()
    P["arm"].location = PETE_E4
    girar_pete(P, 25)

    def act(f):
        t = tf(f)
        for o, tl in zip(S["G"]["bobinas"], llega_b):
            caer(o, t, tl)
        for o in S["G"]["cuerpo"]:
            caer(o, t, llega_c, alto=9.0)
        pose_pete(sc, P, f, cabeza=(-25, 0))
        x = suave(lin(f, a, b - 1))
        # de espaldas a la central; cámara a la altura de los ojos: Pete adentro del cuadro y con la cara sobre la franja de
        # subtítulos (el plano 13 del v2)
        p = orbita(Vector((0, 0, 0)), 18.5, -40 + 10 * x, 1.75) + temblor(f, llega_b + [llega_c])
        mirar(cam, p, Vector((0, 0, 1.6)), lente=35, foco=Vector((0, 0, 2.0)))
        return {}
    return {"actualizar": act}


def p13(sc, a, b):
    # "hasta cuarenta teslas o más. Más del doble…": cae la tapa y el cobre se enciende en "teslas" (el plano 14 del v2)
    S = armar_E4(sc)
    cam, P = S["cam"], S["P"]
    cables(S, 0)
    t_tapa = T[13][0] + 0.4
    oculto(P["arm"])
    t_tes = TW("teslas", 28.0)

    def act(f):
        t = tf(f)
        estado_iman(S, t, lambda o: (t_tapa + 0.05 * (o.name.startswith("G_perno"))) if o in S["G"]["tapa"] else None)
        brillo_cobre(S, 0.6 * suave(lin(t, t_tes - 0.2, t_tes + 0.4)))
        x = suave(lin(f, a, b - 1))
        pos = Vector((4.2, -7.5, 6.2)).lerp(Vector((3.4, -6.4, 5.4)), x) + temblor(f, [t_tapa], 0.03)
        mirar(cam, pos, Vector((0, 0, 3.4)), lente=24, foco=Vector((0, 0, 3.5)))
        return {}
    return {"actualizar": act}


def p14(sc, a, b):
    # "Y al final, enchufarlo a un reactor nuclear entero...": PASO 3, desde atrás del imán los cables crecen y se
    # encienden y la cámara sigue su recorrido por el salar hasta la central en el horizonte (el plano 15 del v2)
    S = armar_E4(sc)
    cam, P = S["cam"], S["P"]
    oculto(P["arm"])
    estado_iman(S, 0, lambda o: None)
    brillo_cobre(S, 0.3)
    t_enc = TW("enchufarlo", 32.0)
    t_re = TW("reactor", 33.0)
    t0 = T[14][0]

    def act(f):
        t = tf(f)
        cables(S, sale(lin(t, t0 + 0.1, t0 + 1.3)), brillo=2.5 * suave(lin(t, t_enc - 0.1, t_enc + 0.5)) * (0.75 + 0.25 * math.sin(t * 9)))
        pan = suave(lin(t, t0 + 0.5, t_re + 0.25))
        pos = Vector((4.0, -2.0, 6.0)).lerp(Vector((3.0, 1.0, 4.6)), suave(lin(f, a, b - 1)))   # alta, sobre el imán
        d0 = (Vector((-3.0, 8.0, 0.0)) - pos).normalized()           # parte mirando la tapa y los cables que salen por atrás
        # al final la central queda a la derecha y sobre los subtítulos (x ~700, y ~780): a la izquierda va ≈ 1 GIGAVATIO
        d1 = Matrix.Rotation(math.radians(3.3), 3, "Z") @ (PLANTA + Vector((0, 0, -100)) - pos).normalized()
        tgt = pos + d0.slerp(d1, pan) * 10.0                     # gira la mirada (no el punto): paneo parejo
        mirar(cam, pos, tgt, lente=35, foco=PLANTA if pan > 0.5 else Vector((-1.0, 3.0, 1.0)))
        cam.data.dof.aperture_fstop = 11
        return {"central": pantalla(sc, cam, PLANTA + Vector((0, 0, 80)))}
    return {"actualizar": act}


def p15(sc, a, b):
    # "solo para ti.": Pete de pie al pie del imán terminado (cables encendidos), mirando hacia arriba; cámara baja
    S = armar_E4(sc)
    cam, P = S["cam"], S["P"]
    estado_iman(S, 0, lambda o: None)
    cables(S, 1.0, 1.6)
    brillo_cobre(S, 0.3)
    P["arm"].location = PETE_E4
    girar_pete(P, 25)
    u = Vector((math.cos(math.radians(236)), math.sin(math.radians(236)), 0))      # de Pete hacia la cámara (la del plano 12)
    cam.data.dof.aperture_fstop = 4.0

    def act(f):
        x = suave(lin(f, a, b - 1))
        pose_pete(sc, P, f, cabeza=(-22, 0))
        d = 5.3 - 0.5 * x
        pos = PETE_E4 + u * d + Vector((0, 0, 0.7))
        tgt = PETE_E4 + Vector((0, 0, 0.7 + d * math.tan(math.radians(3.6))))
        mirar(cam, pos, tgt, lente=35, foco=PETE_E4 + Vector((0, 0, 1.5)))
        return {"pete": pantalla(sc, cam, PETE_E4 + Vector((0, 0, 1.0)))}
    return {"actualizar": act}


# --- E5 · Pete flota (planos 1, 2 y 16): el mismo Happy Idle en loop; el 16 termina en la pose y cámara del cuadro 0 ---
AZ_B = math.radians(33)


def _idx_e5(f):
    """Índice de la animación en E5: el último cuadro del video (plano 16) calza con el cuadro 1 (loop)."""
    if f >= FR(16)[0]:
        return f - (E.FIN - 1) + 1
    return f


def _pete_flota(sc, S, f, extra=0.0):
    P = S["P"]
    i = _idx_e5(f)
    P["arm"].location = (0.0, 0.0, S["G"]["boca"] + 1.2 + extra + 0.04 * math.sin(i / 30 * 2.0))
    if P["arm"].type == "ARMATURE":
        P["arm"].rotation_euler.z = P["rot0"].z + math.radians(4 * math.sin(i / 30 * 0.9))     # gira apenas, suelto en el aire
    pose_pete(sc, P, f, cabeza=(-8, 0), cuadro_anim=i)


def armar_E5(sc):
    S = armar_E4(sc)
    estado_iman(S, 0, lambda o: None)
    cables(S, 1.0, 0.3)
    girar_pete(S["P"], PETE_GIRO, 4, -3)
    S["P"]["flota"] = True
    return S


def cam_B(cam, d, boca, az=AZ_B):
    pos = Vector((math.sin(az) * d, -math.cos(az) * d, 4.1))
    mirar(cam, pos, Vector((0, 0, 3.8)), lente=35, foco=Vector((0, 0, boca + 2.1)))
    cam.data.dof.aperture_fstop = 8


def p1(sc, a, b):
    # CUADRO 0 · "Tu cuerpo repele los imanes.": Pete flotando a 1,2 m sobre la boca (la cámara del cuadro B v2.1),
    # dolly in lento desde la cámara exacta en que termina el plano 16
    S = armar_E5(sc)
    cam, boca = S["cam"], S["G"]["boca"]

    def act(f):
        x = suave(lin(f, a, b - 1))
        _pete_flota(sc, S, f)
        cam_B(cam, 12.0 - 1.2 * x, boca, AZ_B + math.radians(4) * x)
        return {}
    return {"actualizar": act}


def p2(sc, a, b):
    # "Con el imán correcto, podrías flotar.": todo el imán, los cables y la central; el cobre brilla en "imán" y Pete
    # sube 5 cm en "flotar" (el plano 17 del v2)
    S = armar_E5(sc)
    cam, boca = S["cam"], S["G"]["boca"]
    t_im = TW("imán", 2.0)
    t_fl = TW("flotar", 3.0)

    def act(f):
        t = tf(f)
        x = suave(lin(f, a, b - 1))
        brillo_cobre(S, 0.5 * math.sin(math.pi * clamp((t - t_im) / 0.8)))
        _pete_flota(sc, S, f, extra=0.05 * suave(lin(t, t_fl - 0.1, t_fl + 0.5)))
        mirar(cam, Vector((8.0, -20.0, 1.6)).lerp(Vector((10.5, -27.0, 1.7)), x), Vector((-2.0, 0, 3.2)), lente=24, foco=Vector((0, 0, 3.0)))
        cam.data.dof.aperture_fstop = 11
        return {}
    return {"actualizar": act}


def p16(sc, a, b):
    # "Ahí sí... flotarías.": Pete sale flotando del hueco y queda a 1,2 m sobre la boca; termina exacto en la cámara y la
    # pose del cuadro 0 (loop)
    S = armar_E5(sc)
    cam, boca = S["cam"], S["G"]["boca"]

    def act(f):
        x = suave(lin(f, a, b - 1))
        sube = sale(lin(f, a, b - 8))
        _pete_flota(sc, S, f, extra=-2.1 * (1 - sube))
        cam_B(cam, 13.5 - 1.5 * x, boca)
        return {}
    return {"actualizar": act}


# ===================================== piezas ======================================
FUN = {1: p1, 2: p2, 3: p3, 4: p4, 5: p5, 6: p6, 7: p7, 8: p8, 9: p9, 10: p10, 11: p11, 12: p12, 13: p13, 14: p14,
       15: p15, 16: p16}
PIEZAS = {}
for k in T:
    a, b = FR(k)
    n = b - a
    partes = 2 if n > int(os.environ.get("PARTIR", 45)) else 1      # el final parte desde 45 cuadros (máquinas más parejas)
    if partes == 1:
        PIEZAS[str(k)] = {"a": a, "b": b, "fn": FUN[k], "base": str(k)}
    else:
        m = a + n // 2
        PIEZAS[f"{k}@1"] = {"a": a, "b": b, "fn": FUN[k], "base": str(k), "rango": (a, m)}
        PIEZAS[f"{k}@2"] = {"a": a, "b": b, "fn": FUN[k], "base": str(k), "rango": (m, b)}
