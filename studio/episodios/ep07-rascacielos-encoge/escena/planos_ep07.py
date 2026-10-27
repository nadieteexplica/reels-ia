"""Planos del Ep. 7 (proceso v2, estilo realista): 4 escenas, 12 planos (storyboard.md v1).

E1 ciudad  — la torre entera en la ciudad al atardecer, achicándose en cámara rápida (planos 1, 2, 8 y 12).
E2 techo   — Pete arriba del sombrero mientras todo baja; detrás, la torre vecina de vidrio "sube" (plano 3).
E3 corte   — el sombrero de cerca y por dentro, con el frente de la envoltura abierto (planos 4, 5, 6, 7, 9 y 10).
E4 calle   — Pete en la vereda mirando la torre (plano 11).

Cada pieza arma su escena y devuelve actualizar(f) (todo calculado por cuadro, sin keyframes) y su meta para el post.
"""
import math, os, sys
import bpy
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../plantilla")))
import ep07 as E
import torre as TR
from ep07 import F, FR, T, lin, suave, sale, tramo, ruido, clamp, mirar, orbita, pantalla, oculto

FPS = 30
POSE = os.environ.get("POSE", "")
ESCENA = {1: "E1", 2: "E1", 3: "E2", 4: "E3", 5: "E3", 6: "E3", 7: "E3", 8: "E1", 9: "E3", 10: "E3", 11: "E1", 12: "E3", 13: "E3",
          14: "E1", 15: "E1", 16: "E1"}
H = TR.H


def TW(prefijo, desde=0.0):
    return E.t_palabra(prefijo, desde)


def tf(f):
    return (f - 1) / FPS


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
        return {"arm": arm, "anim": anim, "pestanas": pestanas, "ojos": ojos, "gestos": {}}
    o = E.cilindro(sc, "Pete_prueba", 0.22, 1.79, (0, 0, 0), mat=E.mat_pintura("prueba", (0.7, 0.3, 0.1)))
    return {"arm": o, "anim": None, "pestanas": None, "ojos": [], "gestos": {}}


GESTOS = os.environ.get("GESTOS", "")      # carpeta de animaciones de Mixamo del repo privado (assets.txt: "gestos mixamo")


def gesto(P, nombre):
    """Carga una animación de Mixamo (Without Skin) para actuar en un plano (puerta 6 v3: "Pete no actúa, queda como
    estatua"). Si no está (prueba local), Pete sigue con Happy Idle."""
    ruta = os.path.join(GESTOS, nombre + ".fbx") if GESTOS else ""
    if not ruta or not os.path.isfile(ruta) or P["arm"].type != "ARMATURE":
        return None
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=ruta, automatic_bone_orientation=False)
    nuevos = [o for o in bpy.data.objects if o not in antes]
    arm = next((o for o in nuevos if o.type == "ARMATURE"), None)
    for o in nuevos:
        o.hide_render = True
    P["gestos"][nombre] = arm
    return arm


def _largo_anim(anim):
    ad = anim.animation_data
    if ad and ad.action:
        a, b = ad.action.frame_range
        return int(a), max(2, int(round(b - a)))
    return 1, 60


def pose_pete(sc, P, f, cabeza=(0.0, 0.0), cuadro_anim=None, actua=None):
    """Pose de Pete en el cuadro f: copia la de Happy Idle (en loop con todo el largo de la animación de Mixamo, que
    empalma) y gira la cabeza (pitch, yaw en grados). cuadro_anim = índice dentro de la animación (por defecto, f).
    actua = (nombre, cuadro de inicio, cuadros de adelanto): en vez del idle, un gesto de Mixamo una vez desde ese cuadro
    (se queda en su último cuadro)."""
    arm, anim = P["arm"], P["anim"]
    g = P.get("gestos", {}).get(actua[0]) if actua else None
    if g is not None:
        a0, n = _largo_anim(g)
        sc.frame_set(a0 + int(clamp(f - actua[1] + actua[2], 0, n)))
        anim = g
    elif anim is None or arm.type != "ARMATURE":
        return
    else:
        a0, n = _largo_anim(anim)
        sc.frame_set(a0 + ((cuadro_anim if cuadro_anim is not None else f) % n))
    fa = None
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
        sw = 8 * math.sin(i / 30 * 1.3)                  # vaivén de equilibrio más amplio (puerta 6: "pose casi fija")
        E.rotar_hueso_mundo(arm, "LeftArm", eje_y, -(20 + sw))
        E.rotar_hueso_mundo(arm, "RightArm", eje_y, 20 - 0.6 * sw)
        E.rotar_hueso_mundo(arm, "LeftLeg", eje_x, 12 + 7 * math.sin(i / 30 * 1.1))
        E.rotar_hueso_mundo(arm, "RightLeg", eje_x, 10 + 7 * math.sin(i / 30 * 1.1 + 2.0))
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



# ===================================== la torre en cámara rápida ======================================
DUR = 0.45                 # s que tarda el sombrero en bajar un piso (cada "clonc")
H_CORTE = 22.0             # pisos bajo la envoltura en las escenas por dentro (E3)
H_INI = 33.2               # al cuadro 0 ya bajó 4 pisos (se ve el hueco de 14 m bajo el fantasma) y sigue bajando


def _cloncs():
    """(inicio, pisos, duración) de cada bajada del sombrero en las tomas de afuera (v2)."""
    c = [(-0.03, 6, 2.2)]                                                  # gancho: 6 pisos a la vista
    c += [(TW("piso", 4.3), 1, DUR), (TW("piso", 4.9), 1, DUR)]           # "piso por piso"
    a3, b3 = T[3]
    c += [(a3 + 0.1, 1, DUR), (a3 + 0.6, 1, DUR), (a3 + 1.1, 1, DUR)]      # Pete en el techo
    c += [(T[8][0] + 0.3, 1, 1.3)]                                         # desde la calle
    c += [(TW("bajan", 28.0), 1, 1.7)]                                     # la bajada del plano 10 (adentro)
    c += [(TW("otra", 29.9), 1, DUR), (TW("otra", 30.6), 1, DUR), (TW("Como", 31.2), 5, 1.6)]
    c += [(TW("Dos", 39.0) - 0.05, 1, DUR), (TW("diez", 39.9) - 0.05, 1, DUR)]
    c += [(TW("Siete", 40.6) + 0.1, 16, 3.3)]                              # siete meses: hasta el suelo (h → −1 = desaparece)
    return c


CLONCS = _cloncs()


def h_de(t):
    h = H_INI
    for t0, n, d in CLONCS:
        h -= n * suave((t - t0) / d)
    return h


def pisos_en(t):
    """Contador: pisos que quedan (cuenta cada bajada cuando termina, como en la realidad)."""
    h = H_INI
    for t0, n, d in CLONCS:
        x = clamp((t - t0) / d)
        h -= n * x if n > 1 else (1 if x >= 0.7 else 0)
    return max(0, int(math.floor(h + 1e-6)) + 3)


def fantasma(sc):
    """Contorno de la altura original (capa de explicación): una caja de alambre blanco fino + un relleno apenas visible."""
    me = bpy.data.meshes.new("Fantasma")
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= TR.LX + 0.6; v.co.y *= TR.LY + 0.6; v.co.z = v.co.z + 0.5
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("Fantasma", me); sc.collection.objects.link(o)
    w = o.modifiers.new("alambre", "WIREFRAME"); w.thickness = 0.7; w.use_replace = True
    o.data.materials.append(E.mat_emision("fantasma", (1.0, 1.0, 1.0), 3.0))
    for k in ("visible_shadow", "visible_diffuse", "visible_glossy", "visible_transmission"):
        setattr(o, k, False)
    o["bajos"] = [v.index for v in o.data.vertices if v.co.z < 0.5]
    return o


def fantasma_a(o, tope):
    """El contorno va desde el techo actual hasta la altura original."""
    for v in o.data.vertices:
        v.co.z = tope if v.index in o["bajos"] else NP_ALTO
    o.data.update()


NP_ALTO = TR.NP * H + 0.45


def armar_E1(sc, con_fantasma=True):
    TR.cielo(sc)
    C = TR.ciudad(sc)
    S = TR.torre(sc)
    cam = E.camara(sc, (0, -300, 50), (0, 0, 70), lente=35, fstop=16)
    cam.data.clip_end = 20000
    S["cam"] = cam
    S["fant"] = fantasma(sc) if con_fantasma else None
    return S


def estado_afuera(S, f):
    t = tf(f)
    h = h_de(t)
    TR.estado(S, h)
    if S.get("fant") is not None:
        fantasma_a(S["fant"], (h + 3) * H + 0.45)
    return h


CAM0 = (Vector((172, -360, 45)), Vector((0, 0, 58.0)))


def cam_cuadro0(cam, x=0.0):
    """x = 0: la cámara del cuadro 0; x > 0 se acerca (dolly in hacia la torre)."""
    p, m = CAM0
    mirar(cam, p.lerp(m, 0.07 * x), m, lente=32)


def p1(sc, a, b):
    # CUADRO 0 · "Este rascacielos se achicó...": la torre entera bajando el sombrero, con el fantasma de su altura
    S = armar_E1(sc)

    def act(f):
        estado_afuera(S, f)
        cam_cuadro0(S["cam"], suave(lin(f, a, b - 1)))
        return {"pisos": pisos_en(tf(f)), "fant": pantalla(sc, S["cam"], (0, -TR.LY / 2, NP_ALTO))}
    return {"actualizar": act}


def p2(sc, a, b):
    # "piso por piso.": la parte de arriba de cerca, la cámara baja con el sombrero
    S = armar_E1(sc, con_fantasma=False)

    def act(f):
        h = estado_afuera(S, f)
        top = (h + 3) * H
        x = lin(f, a, b - 1)
        mirar(S["cam"], Vector((58 + 6 * x, -132, top - 4)), Vector((0, 0, top - 7)), lente=50)
        return {"pisos": pisos_en(tf(f))}
    return {"actualizar": act}


def p11(sc, a, b):
    # "Y otra vez. Y otra vez. Como su construcción, en reversa.": la torre entera de 3/4, órbita lenta
    S = armar_E1(sc)
    cen = Vector((0, 0, 0))

    def act(f):
        estado_afuera(S, f)
        x = suave(lin(f, a, b - 1))
        pos = Vector((60, -260, 130)).lerp(Vector((40, -250, 124)), x)
        mirar(S["cam"], pos, Vector((0, 0, 52 - 6 * x)), lente=35)
        return {"pisos": pisos_en(tf(f)), "fant": pantalla(sc, S["cam"], (0, -TR.LY / 2, NP_ALTO))}
    return {"actualizar": act}


def p14(sc, a, b):
    # "Dos pisos cada diez días.": general desde otro lado, dolly in corto
    S = armar_E1(sc)

    def act(f):
        estado_afuera(S, f)
        x = suave(lin(f, a, b - 1))
        mirar(S["cam"], Vector((-150 + 8 * x, -330, 60)), Vector((0, 0, 40)), lente=35)
        return {"pisos": pisos_en(tf(f)), "fant": pantalla(sc, S["cam"], (0, -TR.LY / 2, NP_ALTO))}
    return {"actualizar": act}


def p15(sc, a, b):
    # "Siete meses después, donde había un rascacielos de cuarenta pisos... no quedaba nada.": la torre baja hasta el suelo
    # y desaparece; queda el contorno fantasma entero. Cámara del cuadro 0, acercándose
    S = armar_E1(sc)

    def act(f):
        estado_afuera(S, f)
        cam_cuadro0(S["cam"], 0.6 * suave(lin(f, a, b - 1)))
        return {"pisos": pisos_en(tf(f)), "fant": pantalla(sc, S["cam"], (0, -TR.LY / 2, NP_ALTO)), "base": pantalla(sc, S["cam"], (0, -TR.LY / 2, 0))}
    return {"actualizar": act}


def p16(sc, a, b):
    # "Y nadie lo vio caer.": el lote vacío con el fantasma, dolly out hasta la cámara exacta del cuadro 0 (loop)
    S = armar_E1(sc)

    def act(f):
        estado_afuera(S, f)
        cam_cuadro0(S["cam"], 0.6 * (1 - sale(lin(f, a, b - 6))))
        return {"fant": pantalla(sc, S["cam"], (0, -TR.LY / 2, NP_ALTO))}
    return {"actualizar": act}


# ===================================== E2 · Pete en el techo ======================================
def armar_pete(sc, S, pos, giro):
    P = cargar_pete(sc)
    P["giro"] = giro
    arm = P["arm"]
    arm.location = pos
    if arm.type == "ARMATURE":
        P["rot0"] = arm.rotation_euler.copy()
        arm.rotation_euler.z = P["rot0"].z + math.radians(giro)
    else:
        P["rot0"] = arm.rotation_euler.copy()
    return P


def p3(sc, a, b):
    # "Sin una sola explosión.": Pete tranquilo en el techo; la vecina de vidrio "sube" detrás (el techo baja)
    S = armar_E1(sc, con_fantasma=False)
    P = armar_pete(sc, S, Vector((20.0, -1.0, 0)), -30)
    vista = Vector((0.36, 0.93, 0)).normalized()
    gesto(P, "Shrugging")
    t_ex = TW("explosión", 6.0)

    def act(f):
        h = estado_afuera(S, f)
        R = (h + 3) * H + 0.45
        P["arm"].location.z = R
        pose_pete(sc, P, f, cabeza=(-4, 0), actua=("Shrugging", F(t_ex) - 10, 0) if P["gestos"].get("Shrugging") else None)
        x = lin(f, a, b - 1)
        cam = Vector((20.0, -1.0, R + 1.5)) - vista * (3.6 - 0.25 * x)
        mirar(S["cam"], cam, cam + vista * 40 + Vector((0, 0, -40 * math.tan(math.radians(2.5)))), lente=40, foco=Vector((20.0, -1.0, R + 1.65)))
        S["cam"].data.dof.aperture_fstop = 5.6
        return {}
    return {"actualizar": act}


# ===================================== E4 · la calle ======================================
def p8(sc, a, b):
    # "desde la calle parece un piso más": al pie de la torre, mirando hacia arriba; la fachada dentada sube hasta el
    # sombrero contra el cielo y el sombrero baja despacio (Tomás, puerta 4 r1: enfocado en el edificio, no en la ciudad)
    S = armar_E1(sc, con_fantasma=False)

    def act(f):
        estado_afuera(S, f)
        x = suave(lin(f, a, b - 1))
        cam = Vector((24.0 - 1.0 * x, -42.0 + 1.0 * x, 1.6))
        d = (Vector((0, -10, 0)) - cam).length
        mirar(S["cam"], cam, Vector((0, -10, 1.6 + d * math.tan(math.radians(36 + 1.5 * x)))), lente=20)
        S["cam"].data.dof.aperture_fstop = 11
        return {}
    return {"actualizar": act}




def p6(sc, a, b):
    # "Solo armar eso toma dos meses.": el sombrero de cerca desde afuera, cerrado; un calendario de píldora cuenta los días
    S = armar_E3(sc)
    Z0 = S["Z0"]
    R = Z0 + 3 * H
    gancho(S, 2 * H - 4.0, con_bulto=False)
    corte_abierto(S, 0.0)
    for v in S["ventanas"]:
        oculto(v, True)

    def act(f):
        x = suave(lin(f, a, b - 1))
        mirar(S["cam"], Vector((-24 + 6 * x, -80 + 8 * x, R + 7)), Vector((2, 0, R - 5)), lente=40)
        return {}
    return {"actualizar": act}


def p7(sc, a, b):
    # "Después, lo cierran con paneles con ventanas a la misma altura que las del hotel": los 4 paños suben desde abajo del
    # sombrero y se cierran; las ventanas de la envoltura se alinean con las del hotel
    S = armar_E3(sc)
    Z0 = S["Z0"]
    R = Z0 + 3 * H
    gancho(S, 2 * H - 4.0, con_bulto=False)
    corte_abierto(S, 0.0)
    t_ci, t_ve = TW("cierran", 18.0), TW("ventanas", 19.3)
    env = S["env"]
    base = {k: v.location.z for k, v in env.items()}
    basev = {v.name: v.location.z for v in S["ventanas"]}

    def act(f):
        t = tf(f)
        x = suave(lin(f, a, b - 1))
        sube = suave((t - t_ci + 0.2) / 1.3)
        for k, v in env.items():
            v.location.z = base[k] - 2 * H * (1 - sube)
        for v in S["ventanas"]:
            v.location.z = basev[v.name] - 2 * H * (1 - sube)
            oculto(v, sube < 0.999)
        mirar(S["cam"], Vector((-30 + 4 * x, -70 + 6 * x, Z0 + 4.5)), Vector((0, 0, Z0 + 5.0)), lente=38)
        return {"ventana": pantalla(sc, S["cam"], (-10, -TR.LY / 2 - 1.1, Z0 + 2.2))}
    return {"actualizar": act}


def calle(sc):
    """Lo de la calle frente a la torre: paso de cebra, un poste con cables y una máquina expendedora."""
    blanco = TR.mat_simple("pintura_calle", (0.75, 0.74, 0.7), rugo=0.7, neb=False)
    for k in range(8):
        TR.caja(f"Cebra{k}", (0.5, 4.0, 0.02), (22 + k * 1.0, -49.0, 0.0), blanco)
    poste = TR.mat_simple("poste", (0.42, 0.41, 0.39), rugo=0.8, neb=False)
    TR.cilindro("Poste", 0.16, 11.0, (46.5, -41.5, 0), poste, verts=16)
    TR.caja("PosteBrazo", (2.2, 0.12, 0.12), (46.5, -41.5, 10.2), poste)
    cab = E.mat_cable("cable_calle", (0.03, 0.03, 0.03))
    for k, (dz, dx) in enumerate(((10.3, 0.9), (10.3, -0.9), (9.4, 0.6))):
        c = TR.cilindro(f"CableCalle{k}", 0.02, 90.0, (46.5 + dx, -41.5, dz), cab, verts=6)
        c.rotation_euler = (math.radians(90), 0, math.radians(8))
    maq = TR.caja("Expendedora", (1.0, 0.8, 1.85), (27.0, -40.8, 0.18), TR.mat_simple("expendedora", (0.75, 0.12, 0.1), rugo=0.4, neb=False))
    luz = TR.caja("ExpFrente", (0.86, 0.02, 1.2), (27.0, -41.21, 0.65), E.mat_emision("exp_luz", (0.95, 0.97, 1.0), 1.5))
    return maq


# ===================================== E3 · el sombrero por dentro ======================================
def armar_E3(sc):
    TR.cielo(sc)
    TR.ciudad(sc)
    S = TR.torre(sc, corte=True)
    TR.estado(S, H_CORTE)
    cam = E.camara(sc, (0, -300, 50), (0, 0, 70), lente=35, fstop=11)
    cam.data.clip_end = 20000
    S["cam"] = cam
    S["Z0"] = H_CORTE * H
    c = S["corte"]
    c["relleno"].energy = 1800.0          # poco relleno: que se vea el sol rasante que entra por el corte (negros reales)
    c["fondo"].energy = 700.0
    return S


def corte_abierto(S, x, borde=None):
    """x = 0: envoltura cerrada; x = 1: corte de esquina (frente sur y lado oeste transparentes: entra el sol rasante).
    El borde naranja sólo se enciende mientras se abre (puerta 4 r1: las líneas fijas se leían como láseres)."""
    TR.set_alfa(S["pm_s"], 1.0 - 0.94 * x)
    TR.set_alfa(S["pm_o"], 1.0 - 0.97 * x)
    for ven in S.get("ventanas", []):                 # las ventanas de la envoltura tapaban el corte (v2, 27-oct)
        oculto(ven, x > 0.02)
    v = (3.0 * x * (1 - x) * 4) if borde is None else borde
    TR.brillo(S["corte"]["borde"], v)
    for o in S["sombrero"].children:
        if o.name.startswith("Borde"):
            o.hide_render = v < 0.02          # apagado se veía como una línea negra cruzando el cuadro


def gatos_brillan(S, x):
    m = S["corte"]["gatas"][0].data.materials[0]
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Emission Color"].default_value = (1.0, 0.7, 0.05, 1)
    b.inputs["Emission Strength"].default_value = 1.6 * x


def gancho(S, z_local, x=0.0, y=0.0, con_bulto=True):
    """Gancho de la grúa a z_local (coordenadas del sombrero), con el cable desde el carro."""
    c = S["corte"]
    top = 2 * H - 2.8
    c["gancho"].location = (x, y, z_local)
    c["cable"].location = (x, y, z_local + 0.7)
    c["cable"].scale.z = max(0.05, top - (z_local + 0.7))
    c["bulto"].location = (x, y, z_local - 1.4)
    oculto(c["bulto"], not con_bulto)


def p4(sc, a, b):
    # "El truco: nunca le sacan el techo.": el sombrero de cerca desde afuera; el techo se marca naranja
    S = armar_E3(sc)
    Z0 = S["Z0"]
    R = Z0 + 3 * H
    t_nu = TW("nunca", 8.0)
    techo = S["sombrero"].children
    mat_b = E.mat_emision("techo_marca", (1.0, 0.45, 0.08), 0.0)
    marca = TR.caja("TechoMarca", (TR.LX + 1.4, TR.LY + 1.4, H + 1.75), (0, 0, 2 * H - 0.05), mat_b)
    marca.parent = S["sombrero"]; marca.visible_shadow = False
    marco = marca.modifiers.new("alambre", "WIREFRAME"); marco.thickness = 1.0; marco.use_replace = True       # 0,28 m no se veía a 80 m
    gancho(S, 2 * H - 4.0, con_bulto=False)
    corte_abierto(S, 0.0)

    def act(f):
        t = tf(f)
        x = suave(lin(f, a, b - 1))
        late = suave((t - t_nu) / 0.4) * (0.75 + 0.25 * math.sin((t - t_nu) * 9))
        TR.brillo(mat_b, 10.0 * late)
        mirar(S["cam"], Vector((-30 + 8 * x, -86 + 14 * x, R + 9 - 2 * x)), Vector((2, 0, R - 5)), lente=40)
        # el contorno del sombrero también se dibuja en el post (el alambre 3D no se veía en el render)
        esq = [pantalla(sc, S["cam"], (sx * (TR.LX / 2 + 0.7), sy * (TR.LY / 2 + 0.7), Z0 + z))
               for sx in (-1, 1) for sy in (-1, 1) for z in (2 * H - 0.3, 3 * H + 1.6)]
        return {"techo": esq, "late": round(late, 3)}
    return {"actualizar": act}


def p5(sc, a, b):
    # "Primero, lo vuelven un sombrero gigante, parado sobre gatos hidráulicos.": se abre el frente y se ven los gatos
    S = armar_E3(sc)
    Z0 = S["Z0"]
    t_pr, t_so, t_ga = TW("Primero", 9.5), TW("sombrero", 14.0), TW("gatos", 12.5)
    gancho(S, 2 * H - 4.0, con_bulto=False)
    vigas = [o for o in S["sombrero"].children if o.name.startswith("VigaR") or o.name.startswith("Temp")]
    m_viga = vigas[0].data.materials[0]
    bv = m_viga.node_tree.nodes["Principled BSDF"]
    bv.inputs["Emission Color"].default_value = (1.0, 0.45, 0.08, 1)
    g0 = S["corte"]["gatas"][0]

    def act(f):
        t = tf(f)
        x = suave(lin(f, a, b - 1))
        corte_abierto(S, suave((t - t_pr) / 0.8))
        t_co = TW("columnas", 10.5)
        bv.inputs["Emission Strength"].default_value = 1.2 * suave((t - t_co) / 0.4) * (1 - 0.6 * suave((t - t_ga) / 0.5))
        gatos_brillan(S, suave((t - t_ga) / 0.35))
        pos = Vector((-20, -64, Z0 + 5.5)).lerp(Vector((-15, -44, Z0 + 4.6)), x)     # afuera: se ve el techo, el corte y la fachada
        mirar(S["cam"], pos, Vector((-5, 0, Z0 + 3.2)), lente=32)
        mejor = None
        for g in S["corte"]["gatas"]:
            q = pantalla(sc, S["cam"], g.matrix_world.translation + Vector((0, 0, 1.0)))
            if 150 < q[0] < 930 and 600 < q[1] < 990:
                d = abs(q[0] - 540) + abs(q[1] - 850)
                if mejor is None or d < mejor[0]:
                    mejor = (d, q)
        return {"gata": mejor[1] if mejor else pantalla(sc, S["cam"], g0.matrix_world.translation + Vector((0, 0, 1.0)))}
    return {"actualizar": act}


def _marca_pieza(o, k):
    """La losa que la grúa está sacando se marca con un brillo blanco suave (capa de explicación)."""
    m = o.data.materials[0]
    if not m.name.startswith("losa_mov"):
        m = m.copy(); m.name = f"losa_mov_{o.name}"; o.data.materials[0] = m
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Emission Color"].default_value = (1.0, 0.95, 0.85, 1)
    b.inputs["Emission Strength"].default_value = 1.2 * k


def _losas(S, t, t0, paso=0.42, dur=0.9):
    """Las 8 piezas de la losa de arriba: cada una sube 0,4 m, se corre al pozo y baja por él (colgada del gancho)."""
    c = S["corte"]
    orden = [3, 5, 1, 7, 2, 4, 0, 6]
    activa = None
    for k, i in enumerate(orden):
        o = c["piezas"][i]
        base = Vector(o["base"])
        x = (t - (t0 + k * paso)) / dur
        if x <= 0:
            o.location = base; oculto(o, False); continue
        if x >= 1:
            oculto(o, True); continue
        oculto(o, False)
        sube = suave(x / 0.25) * 0.8
        corre = suave((x - 0.2) / 0.45)
        baja = suave((x - 0.6) / 0.4) * 9.0
        o.location = Vector((base.x * (1 - corre), base.y * (1 - corre), base.z + sube - baja))
        o.rotation_euler.x = math.radians(70) * suave((x - 0.55) / 0.3) * (1 if base.y > 0 else -1)
        activa = o
    return activa


def p9(sc, a, b):
    # "Después, escondidos bajo el sombrero, desarman el piso de abajo.": columnas cortadas y losas que bajan por el pozo
    S = armar_E3(sc)
    Z0 = S["Z0"]
    corte_abierto(S, 1.0, borde=0.0)
    t_de, t_es, t_ds = TW("adentro", 23.5), TW("escondidos", 24.0), TW("desarman", 25.0)
    c = S["corte"]
    P = armar_pete(sc, S, Vector((-8.5, -3.4, Z0)), 60)       # un obrero adentro: da la escala (puerta 4 r1)
    gesto(P, "Pointing")

    def act(f):
        t = tf(f)
        x = suave(lin(f, a, b - 1))
        pose_pete(sc, P, f, cabeza=(-6, 10), actua=("Pointing", F(t_ds) - 12, 0) if P["gestos"].get("Pointing") else None)
        for k, o in enumerate(c["cols_a"]):
            cut = suave((t - (t_es + 0.25 + 0.08 * k)) / 0.3)
            o.scale.z = max(0.001, 1 - cut)
            o.location.z = TR.H * cut
            oculto(o, cut >= 0.999)
        act_o = _losas(S, t, t_de + 0.5, paso=0.45, dur=1.5)
        if act_o is not None:
            gancho(S, act_o.location.z + 1.6, act_o.location.x, act_o.location.y, con_bulto=False)
        else:
            gancho(S, 2 * H - 4.0, con_bulto=False)
        mirar(S["cam"], Vector((-11, -38, Z0 + 4.2)).lerp(Vector((-9, -33, Z0 + 4.0)), x), Vector((-2, 1, Z0 + 2.9)), lente=30)
        info = {"pozo": pantalla(sc, S["cam"], (0, 0, Z0 + 0.3)), "pozo_abajo": pantalla(sc, S["cam"], (0, 0, Z0 - 6.0))}
        if act_o is not None:
            mw = act_o.matrix_world
            info["pieza"] = [pantalla(sc, S["cam"], mw @ Vector(v.co)) for v in act_o.data.vertices]
        return info
    return {"actualizar": act}


def _sin_piso_arriba(S):
    c = S["corte"]
    for o in c["cols_a"] + c["piezas"]:
        oculto(o, True)


def p10(sc, a, b):
    # "Y al final, los gatos bajan el sombrero... un piso.": los pistones se recogen y el sombrero baja 3,5 m
    S = armar_E3(sc)
    Z0 = S["Z0"]
    corte_abierto(S, 1.0, borde=0.0)
    _sin_piso_arriba(S)
    t_ga, t_ba, t_pi = TW("gatos", 27.5), TW("bajan", 28.0), TW("piso", 29.2)

    def act(f):
        t = tf(f)
        x = suave(lin(f, a, b - 1))
        gatos_brillan(S, suave((t - t_ga) / 0.3) * (1 - 0.5 * suave((t - t_pi) / 0.6)))
        baja = H * suave((t - t_ba) / (t_pi - t_ba - 0.02))
        TR.estado(S, H_CORTE, baja)
        gancho(S, 2 * H - 4.0, con_bulto=False)
        mirar(S["cam"], Vector((-38 + 3 * x, -33 + 3 * x, Z0 + 5.5)), Vector((-10, 0, Z0 + 3.2)), lente=32)
        return {}
    return {"actualizar": act}


def p12(sc, a, b):
    # "Y lo más loco: la grúa que baja los escombros genera electricidad.": el bulto baja por el pozo; el aro se enciende
    S = armar_E3(sc)
    Z0 = S["Z0"]
    corte_abierto(S, 1.0, borde=0.0)
    _sin_piso_arriba(S)
    c = S["corte"]
    t_lo, t_gr, t_ge = TW("loco", 33.5), TW("grúa", 34.2), TW("genera", 35.5)
    pulsos = []
    for k in range(3):                      # la electricidad que sale del generador y corre por el cable
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.32, location=(0, 0, 0))
        pu = bpy.context.object; pu.name = f"Pulso{k}"
        pu.data.materials.append(E.mat_emision(f"pulso{k}", (1.0, 0.72, 0.18), 12.0)); pu.parent = S["sombrero"]
        pu.visible_shadow = False
        pulsos.append(pu)

    def act(f):
        t = tf(f)
        x = suave(lin(f, a, b - 1))
        z = 3.9 - 4.6 * suave((t - T[12][0]) / 4.2)       # baja desde el primer cuadro del plano hasta entrar al pozo
        gancho(S, z, 0.0, 0.0, con_bulto=True)
        g = suave((t - t_ge) / 0.4)
        TR.brillo(c["aro"].data.materials[0], 5.0 * g * (0.8 + 0.2 * math.sin(t * 22)))      # dorado, sin quemarse a blanco
        TR.brillo(c["elec"], 3.0 * suave((t - t_ge - 0.3) / 0.5))
        for k, pu in enumerate(pulsos):
            u = ((t - t_ge - 0.2) / 0.9 - k * 0.33)
            on = 0.0 <= u <= 1.0
            oculto(pu, not on)
            if on:
                pu.location = (-2.35 - 17.0 * u, -0.85, 2 * H - 1.9)
        mira = Vector((-1.0, 0, Z0 + 3.6)).lerp(Vector((-0.8, 0, Z0 + 2.4)), suave((t - T[12][0]) / 4.2))
        mirar(S["cam"], Vector((-7.0, -32.0, Z0 + 4.6)).lerp(Vector((-6.0, -27.0, Z0 + 4.4)), x), mira, lente=32, foco=Vector((-1.5, 0, Z0 + 3.6)))
        zc = Z0 + 2 * H - 1.9
        camino = [(-2.35, 0.0, Z0 + 2 * H - 2.75), (-2.35, -0.85, zc), (-20.0, -0.85, zc), (-20.0, 3.6, Z0 + 2 * H - 1.8)]
        camino2 = [(-2.35, -0.85, zc), (20.0, -0.85, zc), (20.0, 3.6, Z0 + 2 * H - 1.8)]
        bw = c["bulto"].matrix_world.translation + Vector((0, 0, 0.7))
        return {"cable": [pantalla(sc, S["cam"], q) for q in camino], "cable2": [pantalla(sc, S["cam"], q) for q in camino2],
                "bulto": pantalla(sc, S["cam"], bw), "carro": pantalla(sc, S["cam"], (0, 0, Z0 + 2 * H - 2.4))}
    return {"actualizar": act}


def p13(sc, a, b):
    # "Con eso prenden las luces de la obra.": la electricidad llega a las lámparas y se prenden de a una
    S = armar_E3(sc)
    Z0 = S["Z0"]
    corte_abierto(S, 1.0, borde=0.0)
    _sin_piso_arriba(S)
    c = S["corte"]
    TR.brillo(c["aro"].data.materials[0], 7.0)
    TR.brillo(c["elec"], 5.0)
    gancho(S, 2 * H - 4.0, con_bulto=False)
    t_pr = TW("prenden", 37.3)

    def act(f):
        t = tf(f)
        x = suave(lin(f, a, b - 1))
        for k, (lm, lt) in enumerate(zip(c["lamparas"], c["luces"])):
            on = suave((t - (t_pr + 0.2 * k)) / 0.08)
            TR.brillo(lm.data.materials[0], 6.0 * on)
            lt.energy = 1600.0 * on
        c["relleno"].energy = 900.0
        c["fondo"].energy = 150.0
        mirar(S["cam"], Vector((-6, -40, Z0 + 3.6)).lerp(Vector((-3, -36, Z0 + 3.7)), x), Vector((0, 3, Z0 + 4.0)), lente=30)
        return {"lamparas": [pantalla(sc, S["cam"], lm.matrix_world.translation) for lm in c["lamparas"]],
                "piso": [pantalla(sc, S["cam"], lm.matrix_world.translation - Vector((0, 0, 4.6))) for lm in c["lamparas"]]}
    return {"actualizar": act}


# ===================================== piezas ======================================
FUN = {1: p1, 2: p2, 3: p3, 4: p4, 5: p5, 6: p6, 7: p7, 8: p8, 9: p9, 10: p10, 11: p11, 12: p12, 13: p13, 14: p14, 15: p15, 16: p16}
PIEZAS = {}
for k in T:
    a, b = FR(k)
    n = b - a
    partes = 2 if n > int(os.environ.get("PARTIR", 45)) else 1
    if partes == 1:
        PIEZAS[str(k)] = {"a": a, "b": b, "fn": FUN[k], "base": str(k)}
    else:
        m = a + n // 2
        PIEZAS[f"{k}@1"] = {"a": a, "b": b, "fn": FUN[k], "base": str(k), "rango": (a, m)}
        PIEZAS[f"{k}@2"] = {"a": a, "b": b, "fn": FUN[k], "base": str(k), "rango": (m, b)}
