"""Planos del Ep. 5 (proceso v2, estilo realista): 5 escenas, 18 planos (storyboard.md v2).

E1 imán de la rana — el electroimán sobre su losa en medio del salar al atardecer; la rana (escaneo real, 2,2 cm) flota
                     dentro del tubo de vidrio en la boca. Planos 1–4, 8, 9 (la fresa) y 18 (loop al cuadro 0).
E2 adentro         — moléculas de agua entre células del tejido; las líneas del imán suben y a cada molécula le sale su
                     empujón. Planos 5–7.
E3 el refri        — Pete de pie junto a un refri en el salar: no flota. Planos 10–11.
E4 imán gigante    — se arma el imán para una persona; los cables cruzan el salar hasta la central nuclear. Planos 12–15.
E5 Pete flota      — Pete sube y flota sobre la boca del imán gigante (SIMULACIÓN). Planos 16–17.

Cada pieza arma su escena y devuelve actualizar(f) (todo calculado por cuadro, sin keyframes) y su meta para el post.
"""
import math, os, random, sys
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../plantilla")))
import ep05 as E
from ep05 import F, FR, T, lin, suave, sale, tramo, ruido, clamp, mirar, orbita, pantalla, oculto

FPS = 30
POSE = os.environ.get("POSE", "")
ESCENA = {1: "E1", 2: "E1", 3: "E1", 4: "E1", 5: "E2", 6: "E2", 7: "E2", 8: "E1", 9: "E1", 10: "E3", 11: "E3",
          12: "E4", 13: "E4", 14: "E4", 15: "E4", 16: "E5", 17: "E5", 18: "E1"}


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


def armar_E1(sc, fresa=False):
    E.cielo_atardecer(sc, elev=2.5, rot=10, fuerza=0.35, sol=3.5)
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
    bpy.context.view_layer.update()
    E.gotitas(sc, rana, 10, (0.00012, 0.00025))      # antes del tubo: los rayos de las gotitas tienen que tocar la piel, no el vidrio
    tubo = E.tubo(sc, "Tubo_vidrio", 0.0158, 0.0148, 0.11, (0, 0, BOCA - 0.01), verts=96, mat=E.mat_acrilico(), bisel=0.0004)
    tubo["no_tapa_ojos"] = 1
    E.ojos_rana(sc, rana, LARGO_RANA)
    fr = None
    if fresa:
        oculto(rana)
        fr = fresa_obj(sc)
        fr.location = (0, 0, RANA_Z)
    E.luz_area(sc, "Rebote", (-0.22, -0.32, BOCA + 0.12), (0, 0, RANA_Z), 3.5, (1.0, 0.88, 0.78), 0.3)
    cam = E.camara(sc, (0.021, -R_CERCA, RANA_Z + ALTO_CAM), (0, 0, RANA_Z), lente=100, fstop=8.0)
    return {"rana": rana, "tubo": tubo, "fresa": fr, "cam": cam}


def fresa_obj(sc, largo=0.024):
    """Fresa (modelo CC-BY 'Strawberry' de rodrigogelmi, Sketchfab) al tamaño de una fresa chica que cabe en el tubo."""
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=E.asset("dd6a424807614544835c8cc4529d6f0d.glb"))
    nuevos = [o for o in bpy.data.objects if o not in antes]
    mallas = [o for o in nuevos if o.type == "MESH"]
    pts = [o.matrix_world @ Vector(c) for o in mallas for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    centro = (lo + hi) / 2
    padre = bpy.data.objects.new("Fresa", None)
    sc.collection.objects.link(padre)
    for o in [o for o in nuevos if o.parent is None]:
        o.location -= centro
        o.parent = padre
    padre.scale = [largo / max(hi - lo)] * 3
    for m in {s.material for o in mallas for s in o.material_slots if s.material}:
        b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if b:
            b.inputs["Coat Weight"].default_value = 0.5
            b.inputs["Coat Roughness"].default_value = 0.1
    for o in mallas:
        E.liso(o, 180)
    return padre


def rana_flota(rana, f, extra_z=0.0, giro=0.0):
    """Flota quieta en el aire: sube y baja 0,6 mm y gira apenas (±8° como máximo: nunca toca el vidrio)."""
    rana.location = (0.0005 * ruido(f, 3, 0.4), 0.0005 * ruido(f, 4, 0.4), RANA_Z + 0.0006 * math.sin(f / 30 * 2.1) + extra_z)
    rana.rotation_euler = (ROT0[0] + math.radians(2.5 * ruido(f, 5, 0.3)), ROT0[1] + math.radians(2.5 * ruido(f, 6, 0.3)),
                           ROT0[2] + math.radians(giro))


def p_orbita(sc, a, b, ang0, ang1, pieza_inicio_cuadro0=False):
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


def p1(sc, a, b):
    return p_orbita(sc, a, b, -15, 20)


def p18(sc, a, b):
    # loop: termina exacto en la cámara del cuadro 0 (ángulo -15 del plano 1) y la rana en su pose del cuadro 0
    return p_orbita(sc, a, b, 30, -15)


def p2(sc, a, b):
    S = armar_E1(sc)
    cam, rana = S["cam"], S["rana"]
    c = Vector((0, 0, RANA_Z))

    def act(f):
        x = suave(lin(f, a, b - 1))
        rana_flota(rana, f)
        p0 = orbita(c, R_CERCA, 20, ALTO_CAM)
        p1_ = Vector((0.03, -0.11, RANA_Z + 0.30))
        mirar(cam, p0.lerp(p1_, x), c + Vector((0, 0, -0.008 * (1 - x))), lente=100 - 25 * x, foco=c + CABEZA * (1 - x))
        return {"rana": pantalla(sc, cam, rana.location)}
    return {"actualizar": act}


def p3(sc, a, b):
    S = armar_E1(sc)
    cam, rana = S["cam"], S["rana"]
    cam.data.dof.aperture_fstop = 8.0

    def act(f):
        x = suave(lin(f, a, b - 1))
        rana_flota(rana, f)
        p = Vector((0.03, -0.11, RANA_Z + 0.30)).lerp(Vector((1.5, -3.4, 1.05)), sale(x))
        tgt = Vector((0, 0, RANA_Z)).lerp(Vector((0, 0, 0.85)), sale(x))
        mirar(cam, p, tgt, lente=75 - 45 * sale(x), foco=Vector((0, 0, 0.9)) if x > 0.3 else tgt)
        return {"iman": pantalla(sc, cam, (0, 0, 0.9)), "rana": pantalla(sc, cam, (0, 0, RANA_Z))}
    return {"actualizar": act}


def p4(sc, a, b):
    S = armar_E1(sc)
    cam, rana = S["cam"], S["rana"]

    def act(f):
        x = lin(f, a, b - 1) ** 1.6
        rana_flota(rana, f)
        c = Vector((0, 0, RANA_Z + 0.003))
        p0 = orbita(Vector((0, 0, RANA_Z)), 0.36, -10, 0.006)
        p1_ = Vector((0.004, -0.0185, RANA_Z + 0.004))           # se frena 2 mm antes del vidrio (radio 15,8 mm)
        p = p0.lerp(p1_, x)
        mirar(cam, p, c, lente=100, foco=c)
        cam.data.dof.aperture_fstop = 5.6 + 6 * x
        return {}
    return {"actualizar": act}


def p8(sc, a, b):
    S = armar_E1(sc)
    cam, rana = S["cam"], S["rana"]
    c = Vector((0, 0, RANA_Z))
    t_gana = TW("gana", 14.0)

    def act(f):
        x = suave(lin(f, a, b - 1))
        sube = 0.004 * suave(lin(tf(f), t_gana - 0.6, t_gana + 0.6))
        rana_flota(rana, f, extra_z=sube)
        # la rana a la izquierda del centro: a la derecha va el par de flechas (post)
        p = orbita(c, 0.40 - 0.03 * x, -32, 0.006)
        mirar(cam, p, c + Vector((0.009, 0, -0.016)), foco=c)
        return {"rana": pantalla(sc, cam, rana.location), "lado": pantalla(sc, cam, rana.location + Vector((0.016, 0.004, 0)))}
    return {"actualizar": act}


def p9(sc, a, b):
    S = armar_E1(sc, fresa=True)
    cam, fr = S["cam"], S["fresa"]
    c = Vector((0, 0, RANA_Z))

    def act(f):
        x = suave(lin(f, a, b - 1))
        fr.location = (0, 0, RANA_Z + 0.0006 * math.sin(f / 30 * 2.1))
        fr.rotation_euler = (math.radians(8), math.radians(-5), math.radians(70 * x))
        p = orbita(c, 0.36, 5 - 20 * x, 0.004)
        mirar(cam, p, c + Vector((0, 0, -0.016)), foco=c)
        return {}
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
    flechas = []
    for m in mols:
        if m.location.y < 4.5 and abs(m.location.x) < 3.4:
            c, p = E.flecha(sc, f"emp_{m.name}", tuple(m.location + Vector((0, 0, 0.35))), 0.5, 0.025, fuerza=1.8)
            flechas.append((m, c, p, m.location.copy()))
    E.luz_area(sc, "Llave", (-3.5, -4.0, 6.0), (0, 0, 1.9), 900, (1.0, 0.9, 0.82), 2.5)
    E.luz_area(sc, "Contra", (2.5, 4.0, 4.5), (0, 0, 1.9), 600, (0.5, 0.8, 1.0), 1.5)
    E.luz_punto(sc, "Brillo_abajo", (0, 1.5, -2.0), 300, (0.25, 0.8, 1.0), 1.0)
    cam = E.camara(sc, (1.3, -8.8, 2.7), (0, 0, 2.1), lente=50, fstop=2.2)
    return {"mols": mols, "heroe": heroe, "lineas": lineas, "fl_h": fl_h, "flechas": flechas, "cam": cam}


def _giro_mols(S, f):
    for m in S["mols"]:
        g = m["giro"]
        m.rotation_euler = (m.rotation_euler.x + 0.004 * g[0], m.rotation_euler.y + 0.004 * g[1], m.rotation_euler.z + 0.004 * g[2])
    S["heroe"].rotation_euler.z = math.radians(35) + 0.25 * math.sin(f / 30 * 0.8)


def _escala(obs, s):
    for o in obs:
        o.scale = (max(s, 0.001),) * 3
        o.hide_render = s <= 0.002


def _lineas(S, x):
    for l in S["lineas"]:
        l.data.bevel_factor_end = max(0.001, x)
        l.hide_render = x <= 0.002


def _flechas_chicas(S, edad_fn):
    for (m, c, p, base) in S["flechas"]:
        s = edad_fn(m)
        for o in (c, p):
            o.hide_render = s <= 0.002
            o.scale = (1, 1, max(s, 0.001)) if o is c else (max(s, 0.001),) * 3
            o.location = base + Vector((0, 0, 0.35 + (0.175 if o is c else 0.425) * max(s, 0.001)))


def p5(sc, a, b):
    S = armar_E2(sc)
    cam = S["cam"]
    _lineas(S, 0); _escala(S["fl_h"], 0); _flechas_chicas(S, lambda m: 0)

    def act(f):
        x = suave(lin(f, a, b - 1))
        _giro_mols(S, f)
        mirar(cam, Vector((1.6, -11.5, 2.9)).lerp(Vector((1.3, -8.8, 2.7)), x), Vector((0, 0, 2.1)), foco=Vector((0, 0, 1.9)))
        return {}
    return {"actualizar": act}


def p6(sc, a, b):
    S = armar_E2(sc)
    cam = S["cam"]
    t_emp = TW("empuja", 8.0)
    _flechas_chicas(S, lambda m: 0)

    def act(f):
        x = suave(lin(f, a, b - 1))
        _giro_mols(S, f)
        _lineas(S, sale(lin(tf(f), T[6][0] + 0.2, T[6][0] + 1.6)))
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


def p7(sc, a, b):
    S = armar_E2(sc)
    cam = S["cam"]
    _lineas(S, 1.0)
    c, p = S["fl_h"]
    c.scale = (1, 1, 1); c.location = (0, 0, 2.87); p.location = (0, 0, 3.47)
    S["heroe"].location.z = 1.96
    t0, t1 = T[7][0] + 0.15, T[7][1] - 0.5
    dmax = max((m.location - Vector((0, 0, 1.9))).length for (m, *_r) in S["flechas"]) or 1.0

    def act(f):
        x = suave(lin(f, a, b - 1))
        _giro_mols(S, f)
        t = tf(f)
        _flechas_chicas(S, lambda m: sale(lin(t, t0 + (t1 - t0) * (m.location - Vector((0, 0, 1.9))).length / dmax,
                                              t0 + (t1 - t0) * (m.location - Vector((0, 0, 1.9))).length / dmax + 0.3)))
        mirar(cam, Vector((1.3, -9.4, 2.7)).lerp(Vector((1.8, -15.5, 3.2)), x), Vector((0, 1.0, 2.1)), lente=50 - 15 * x,
              foco=Vector((0, 1.0, 2.0)))
        cam.data.dof.aperture_fstop = 2.2 + 2.0 * x
        return {}
    return {"actualizar": act}


# ===================================== E3 · el refri en el salar ======================================
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


def pose_pete(sc, P, f, cabeza=(0.0, 0.0), cuadro_anim=None):
    """Pose de Pete en el cuadro f: copia la de Happy Idle (en loop) y gira la cabeza (pitch, yaw en grados)."""
    arm, anim = P["arm"], P["anim"]
    if anim is None or arm.type != "ARMATURE":
        return
    n = 60
    fa = 1 + ((cuadro_anim if cuadro_anim is not None else f) % n)
    sc.frame_set(fa)
    dst = {b.name.split(":")[-1]: b for b in arm.pose.bones}
    for b in anim.pose.bones:
        d = dst.get(b.name.split(":")[-1])
        if d is not None:
            d.rotation_mode = "QUATERNION"
            d.rotation_quaternion = b.rotation_quaternion.copy()
    bpy.context.view_layer.update()
    if cabeza != (0.0, 0.0):
        E.rotar_hueso_mundo(arm, "Head", (1, 0, 0), cabeza[0])
        if cabeza[1]:
            E.rotar_hueso_mundo(arm, "Head", (0, 0, 1), cabeza[1])
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


def refri_obj(sc, alto=1.75):
    """Refri (modelo CC-BY 'Refrigerator' de shedmon, Sketchfab) a tamaño real, con imanes de colores en la puerta."""
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=E.asset("64a8489527994fb498af1cca4a6fda9f.glb"))
    nuevos = [o for o in bpy.data.objects if o not in antes]
    mallas = [o for o in nuevos if o.type == "MESH"]
    pts = [o.matrix_world @ Vector(c) for o in mallas for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    padre = bpy.data.objects.new("Refri", None)
    sc.collection.objects.link(padre)
    base = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    for o in [o for o in nuevos if o.parent is None]:
        o.location -= base
        o.parent = padre
    k = alto / (hi.z - lo.z)
    kx = 0.78 / (hi.x - lo.x)                # un refri de 78 cm de ancho y 75 de fondo (el modelo es más ancho)
    ky = 0.75 / (hi.y - lo.y)
    padre.scale = (kx, ky, k)
    return padre, Vector((0.78, 0.75, alto))


def imanes_refri(sc, refri, dims):
    """Imanes de refri en la puerta (cara -Y): discos y cuadrados de colores, con brillo de plástico."""
    random.seed(4)
    cols = [(0.6, 0.03, 0.02), (0.02, 0.15, 0.55), (0.7, 0.45, 0.0), (0.03, 0.35, 0.08), (0.55, 0.05, 0.3)]
    out = []
    y = -dims.y / 2 - 0.004
    for i in range(7):
        x = random.uniform(-dims.x * 0.32, dims.x * 0.32)
        z = random.uniform(dims.z * 0.45, dims.z * 0.85)
        m = E.mat_pintura(f"iman_refri{i}", cols[i % len(cols)], rugo=(0.2, 0.35), sucio=0.05, capa=0.6)
        if i % 2:
            o = E.cilindro(sc, f"ImanRefri{i}", 0.028, 0.008, (x, y, z), verts=32, mat=m, bisel=0.002)
            o.rotation_euler = (math.radians(90), 0, 0)
        else:
            o = E.caja(sc, f"ImanRefri{i}", (0.05, 0.008, 0.035), (x, y, z), m, 0.003)
        out.append(o)
    return out


REFRI_POS = Vector((1.05, 0.15, 0.0))


def armar_E3(sc):
    armar_salar_tarde(sc)
    refri, dims = refri_obj(sc)
    refri.location = REFRI_POS
    bpy.context.view_layer.update()
    imanes = imanes_refri(sc, refri, dims)
    for o in imanes:
        o.location = REFRI_POS + Vector(o.location)
    P = cargar_pete(sc)
    P["arm"].location = (0, 0, 0)
    if P["arm"].type == "ARMATURE":
        base = P["arm"].rotation_euler.copy()
        P["arm"].rotation_euler = (base.x, base.y, base.z + math.radians(8))
    E.luz_area(sc, "RellenoPete", (2.5, -5, 2.6), (0.2, 0, 1.2), 40, (1.0, 0.86, 0.75), 2.0, spread=40)
    cam = E.camara(sc, (0.6, -4.6, 1.35), (0.35, 0, 1.05), lente=35, fstop=4.0)
    return {"P": P, "refri": refri, "dims": dims, "imanes": imanes, "cam": cam}


def p10(sc, a, b):
    S = armar_E3(sc)
    cam, P = S["cam"], S["P"]
    t_ref = TW("refri", 19.0)

    def act(f):
        x = suave(lin(f, a, b - 1))
        mira = suave(lin(tf(f), T[10][0] + 0.7, T[10][0] + 1.2))
        pose_pete(sc, P, f, cabeza=(-6 * mira, -28 * mira))
        abajo = suave(lin(tf(f), T[10][0] + 1.5, T[10][1] - 0.2))
        p = Vector((0.6, -4.6, 1.35)).lerp(Vector((0.5, -4.0, 0.75)), abajo)
        tgt = Vector((0.35, 0, 1.05)).lerp(Vector((0.3, 0, 0.35)), abajo)
        mirar(cam, p, tgt, foco=Vector((0.2, 0, 0.9)))
        return {"pies": pantalla(sc, cam, (0, 0, 0.05))}
    return {"actualizar": act}


def p11(sc, a, b):
    S = armar_E3(sc)
    cam = S["cam"]
    oculto(S["P"]["arm"])
    ims = S["imanes"]
    c = sum((Vector(o.location) for o in ims), Vector()) / len(ims)
    im = min(ims, key=lambda o: (Vector(o.location) - c).length)
    cam.data.dof.aperture_fstop = 4.0

    def act(f):
        x = suave(lin(f, a, b - 1))
        p = c + Vector((-1.25 + 0.2 * x, -1.6 + 0.35 * x, 0.25))
        mirar(cam, p, c + Vector((0.12, 0, -0.1)), lente=35, foco=Vector(im.location))
        return {"iman_refri": pantalla(sc, cam, im.location)}
    return {"actualizar": act}


# ===================================== E4 / E5 · el imán gigante ======================================
PLANTA = Vector((-1150, 2080, 0))
PETE_E4 = Vector((-3.4, -1.6, 0.0))
PETE_GIRO = -23            # Pete de 3/4 hacia la cámara alta del cuadro B v2


def armar_E4(sc):
    armar_salar_tarde(sc)
    E.central_nuclear(sc, pos=tuple(PLANTA))
    antes = set(bpy.data.objects)
    boca = E.iman_gigante(sc)
    piezas = [o for o in bpy.data.objects if o not in antes]
    G = {"boca": boca}
    G["plataforma"] = [o for o in piezas if o.name.startswith("G_plataforma")]
    G["cuerpo"] = [o for o in piezas if o.name.startswith(("G_cuerpo", "G_escarcha", "G_hueco", "G_aro", "G_costilla"))]
    G["tapa"] = [o for o in piezas if o.name.startswith(("G_tapa", "G_cobre", "G_perno"))]
    G["cables"] = [o for o in piezas if o.name.startswith(("G_cable", "G_conector"))]
    for o in G["cuerpo"] + G["tapa"]:
        o["z0"] = o.location.z
    P = cargar_pete(sc)
    E.luz_area(sc, "RellenoPete", (5.0, -13.2, 8.1), (0, 0, 4.4), 25, (1.0, 0.9, 0.82), 2.0, spread=30)   # como en el cuadro B v2
    cam = E.camara(sc, (7.0, -18.5, 3.4), (0, 0, 2.4), lente=35, fstop=8.0)
    return {"G": G, "P": P, "cam": cam}


def construir(S, t_cuerpo0=None, t_cuerpo1=None, t_tapa=None, cables=1.0, brillo_cables=0.0):
    """Estado del imán en el tiempo t: el cuerpo llega en tandas (de abajo hacia arriba, cayendo desde 6 m), la tapa cae
    después; los cables crecen desde el imán hacia la central."""
    G = S["G"]
    cuerpo = sorted(G["cuerpo"], key=lambda o: o["z0"])
    for o in cuerpo + G["tapa"]:
        o.hide_render = False
    return cuerpo


def estado_iman(S, t, llegada):
    """llegada(o) → t en que esa pieza termina de caer (None = ya está)."""
    for o in S["G"]["cuerpo"] + S["G"]["tapa"]:
        tl = llegada(o)
        if tl is None:
            o.hide_render = False
            o.location.z = o["z0"]
            continue
        x = lin(t, tl - 0.35, tl)
        o.hide_render = t < tl - 0.35
        o.location.z = o["z0"] + 6.0 * (1 - sale(x))


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


def p12(sc, a, b):
    S = armar_E4(sc)
    cam, P = S["cam"], S["P"]
    estado_iman(S, 0, lambda o: 999)
    cables(S, 0)
    P["arm"].location = PETE_E4
    if P["arm"].type == "ARMATURE":
        base = P["arm"].rotation_euler.copy()
        P["arm"].rotation_euler = (base.x, base.y, base.z + math.radians(25))

    def act(f):
        x = suave(lin(f, a, b - 1))
        sube = suave(lin(tf(f), T[12][0] + 1.1, T[12][0] + 1.7))
        pose_pete(sc, P, f, cabeza=(-30 * sube, 0))
        mirar(cam, Vector((6.0, -17.5, 1.8)).lerp(Vector((5.0, -14.5, 1.75)), x), Vector((-1.2, 0, 1.4)), lente=35, foco=PETE_E4 + Vector((0, 0, 1.6)))
        return {}
    return {"actualizar": act}


def p13(sc, a, b):
    S = armar_E4(sc)
    cam, P = S["cam"], S["P"]
    cables(S, 0)
    cuerpo = sorted(S["G"]["cuerpo"], key=lambda o: o["z0"])
    t0, t1 = T[13][0] + 0.2, T[13][1] - 0.25
    zs = sorted({round(o["z0"], 2) for o in cuerpo})
    lleg = {z: t0 + (t1 - t0) * i / max(1, len(zs) - 1) for i, z in enumerate(zs)}
    P["arm"].location = PETE_E4
    if P["arm"].type == "ARMATURE":
        base = P["arm"].rotation_euler.copy()
        P["arm"].rotation_euler = (base.x, base.y, base.z + math.radians(25))

    def act(f):
        t = tf(f)
        estado_iman(S, t, lambda o: lleg.get(round(o["z0"], 2), t1) if o in cuerpo else 999)
        pose_pete(sc, P, f, cabeza=(-25, 0))
        x = suave(lin(f, a, b - 1))
        p = orbita(Vector((0, 0, 0)), 18.5, -14 + 12 * x, 2.6)     # de espaldas a la central: el vapor no sale "del imán" (puerta 4 r1)
        mirar(cam, p, Vector((0, 0, 2.2)), lente=35, foco=Vector((0, 0, 2.0)))
        return {}
    return {"actualizar": act}


def p14(sc, a, b):
    S = armar_E4(sc)
    cam, P = S["cam"], S["P"]
    cables(S, 0)
    t_tapa = T[14][0] + 0.4
    oculto(P["arm"])
    cobre = [o for o in S["G"]["tapa"] if o.name.startswith("G_cobre")]
    t_tes = TW("teslas", 29.0)

    def act(f):
        t = tf(f)
        estado_iman(S, t, lambda o: (t_tapa + 0.05 * (o.name.startswith("G_perno"))) if o in S["G"]["tapa"] else None)
        brillo = 0.6 * suave(lin(t, t_tes - 0.2, t_tes + 0.4))
        for o in cobre:
            for s in o.material_slots:
                if not s.material:
                    continue
                bsdf = s.material.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs["Emission Color"].default_value = (1.0, 0.45, 0.15, 1)
                    bsdf.inputs["Emission Strength"].default_value = brillo
        x = suave(lin(f, a, b - 1))
        mirar(cam, Vector((4.2, -7.5, 6.2)).lerp(Vector((3.4, -6.4, 5.4)), x), Vector((0, 0, 3.4)), lente=24, foco=Vector((0, 0, 3.5)))
        return {}
    return {"actualizar": act}


def p15(sc, a, b):
    S = armar_E4(sc)
    cam, P = S["cam"], S["P"]
    oculto(P["arm"])
    estado_iman(S, 0, lambda o: None)
    t_gw = TW("gigavatio", 32.0)

    def act(f):
        t = tf(f)
        x = suave(lin(f, a, b - 1))
        cables(S, sale(lin(t, T[15][0], T[15][0] + 1.6)), brillo=2.5 * suave(lin(t, t_gw - 0.1, t_gw + 0.5)) * (0.75 + 0.25 * math.sin(t * 9)))
        # paneo: del imán hacia la central en el horizonte, siguiendo los cables
        d = (PLANTA - Vector((0, 0, 0))).normalized()
        tgt = Vector((0, 0, 1.8)).lerp(Vector((0, 0, 1.0)) + d * 60, sale(x))
        mirar(cam, Vector((5.5, -12.0, 2.2)).lerp(Vector((4.0, -8.5, 2.0)), x), tgt, lente=35, foco=tgt)
        cam.data.dof.aperture_fstop = 11
        return {"central": pantalla(sc, cam, PLANTA + Vector((0, 0, 80)))}
    return {"actualizar": act}


def p16(sc, a, b):
    # "Ahí sí flotarías": la cámara del cuadro B v2.1 (apenas sobre la tapa); Pete sale flotando del hueco y queda a
    # 1,2 m sobre la boca, recortado contra los cerros
    S = armar_E4(sc)
    cam, P = S["cam"], S["P"]
    estado_iman(S, 0, lambda o: None)
    cables(S, 1.0, 0.3)
    boca = S["G"]["boca"]
    if P["arm"].type == "ARMATURE":
        base = P["arm"].rotation_euler.copy()
        P["arm"].rotation_euler = (base.x + math.radians(4), base.y + math.radians(-3), base.z + math.radians(PETE_GIRO))
    az = math.radians(33)

    def act(f):
        x = suave(lin(f, a, b - 1))
        z = boca - 0.9 + 2.1 * sale(lin(f, a, b - 8))      # sale del hueco y queda a 1,2 m sobre la boca (cuadro B)
        P["arm"].location = (0.0, 0.0, z + 0.03 * math.sin(f / 30 * 2.0))
        pose_pete(sc, P, f, cabeza=(-8, 0), cuadro_anim=20)
        d = 13.5 - 1.5 * x
        pos = Vector((math.sin(az) * d, -math.cos(az) * d, 4.1))
        mirar(cam, pos, Vector((0, 0, 3.8)), lente=35, foco=Vector((0, 0, boca + 2.1)))
        cam.data.dof.aperture_fstop = 8
        return {}
    return {"actualizar": act}


def p17(sc, a, b):
    S = armar_E4(sc)
    cam, P = S["cam"], S["P"]
    estado_iman(S, 0, lambda o: None)
    cables(S, 1.0, 0.3)
    boca = S["G"]["boca"]
    if P["arm"].type == "ARMATURE":
        base = P["arm"].rotation_euler.copy()
        P["arm"].rotation_euler = (base.x + math.radians(4), base.y + math.radians(-3), base.z + math.radians(PETE_GIRO))

    def act(f):
        x = suave(lin(f, a, b - 1))
        P["arm"].location = (0.0, 0.0, boca + 1.2 + 0.03 * math.sin(f / 30 * 2.0))
        pose_pete(sc, P, f, cabeza=(-8, 0), cuadro_anim=20)
        mirar(cam, Vector((8.0, -20.0, 1.6)).lerp(Vector((10.5, -27.0, 1.7)), x), Vector((-2.0, 0, 3.2)), lente=24, foco=Vector((0, 0, 3.0)))
        cam.data.dof.aperture_fstop = 11
        return {}
    return {"actualizar": act}


# ===================================== piezas ======================================
FUN = {1: p1, 2: p2, 3: p3, 4: p4, 5: p5, 6: p6, 7: p7, 8: p8, 9: p9, 10: p10, 11: p11, 12: p12, 13: p13, 14: p14,
       15: p15, 16: p16, 17: p17, 18: p18}
PIEZAS = {}
for k in T:
    a, b = FR(k)
    n = b - a
    partes = 2 if n > 75 else 1
    if partes == 1:
        PIEZAS[str(k)] = {"a": a, "b": b, "fn": FUN[k], "base": str(k)}
    else:
        m = a + n // 2
        PIEZAS[f"{k}@1"] = {"a": a, "b": b, "fn": FUN[k], "base": str(k), "rango": (a, m)}
        PIEZAS[f"{k}@2"] = {"a": a, "b": b, "fn": FUN[k], "base": str(k), "rango": (m, b)}
