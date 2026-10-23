"""E2 mecánica de Rhein 01: las piezas de la caña de cerca y en corte (procedural, semi-realista).
- carrete(): tambor con el cable enrollado, dos engranajes grandes, disco de freno con pinza roja, rueda de trinquete con
  pestillo amarillo, y una carcasa que se vuelve transparente (nodo de mezcla 'Corte' en su material).
- cable_trenzado(): 6 hilos de acero que se trenzan en espiral alrededor del alma (fase y avance animables).
Todo se arma alrededor de un vacío raíz para ubicarlo junto a la torreta de la grúa.
"""
import math, os, sys
import bmesh
import bpy
from mathutils import Vector, Euler, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../plantilla")))
import props as P
from base_pj import mat_simple, colgar
import utileria as U


def engranaje(nombre, coll, m, r=0.2, dientes=24, ancho=0.05, alto_diente=0.03, hueco=0.05, rayos=5):
    """Engranaje recto: perfil con dientes trapezoidales extruido en Z, con agujero central y rayos."""
    bm = bmesh.new()
    pts = []
    for i in range(dientes):
        a0 = 2 * math.pi * i / dientes
        da = 2 * math.pi / dientes
        for (f, rr) in ((0.0, r), (0.15, r), (0.28, r + alto_diente), (0.52, r + alto_diente), (0.65, r), (1.0, r)):
            a = a0 + da * f
            pts.append((rr * math.cos(a), rr * math.sin(a)))
    vs_bot = [bm.verts.new((x, y, -ancho / 2)) for x, y in pts]
    vs_top = [bm.verts.new((x, y, ancho / 2)) for x, y in pts]
    n = len(pts)
    for i in range(n):
        bm.faces.new((vs_bot[i], vs_bot[(i + 1) % n], vs_top[(i + 1) % n], vs_top[i]))
    bm.faces.new(vs_top)
    bm.faces.new(list(reversed(vs_bot)))
    ob = P.mesh_obj(nombre, bm, coll, m=m, smooth=False)
    bv = ob.modifiers.new("Bisel", "BEVEL")
    bv.width, bv.segments = 0.003, 2
    # cubo central y rayos (piezas aparte, hijas)
    cubo = P.prim("cyl", nombre + "_cubo", coll, m, r=hueco * 1.6, r_top=hueco * 1.6, h=ancho * 1.6, seg=32)
    cubo.parent = ob
    return ob


def carrete(coll, nombre="Carrete"):
    raiz = bpy.data.objects.new(nombre, None)
    coll.objects.link(raiz)
    m_ac = U.acero("AceroCarrete", (0.55, 0.56, 0.58))
    m_os = U.acero("AceroOscuro", (0.22, 0.22, 0.24))
    m_ro = U.pintura("PinzaRoja", (0.78, 0.05, 0.03), 0.1)
    m_am = U.pintura("PestilloAmarillo", (1.0, 0.72, 0.0), 0.1)
    m_cable = U.acero("CableAcero2", (0.40, 0.41, 0.43))
    eje = Vector((1, 0, 0))                      # el carrete gira alrededor de X
    rot = Euler((0, math.radians(90), 0))
    partes = {}
    # tambor con el cable enrollado (espiras)
    tambor = P.prim("cyl", nombre + "_tambor", coll, m_os, r=0.16, r_top=0.16, h=0.42, seg=48)
    tambor.rotation_euler = rot
    espiras = []
    for k in range(3):
        pts = []
        for i in range(0, 14 * 24 + 1):
            a = 2 * math.pi * i / 24
            x = -0.19 + 0.38 * i / (14 * 24)
            rr = 0.175 + 0.022 * k
            pts.append((x, rr * math.cos(a), rr * math.sin(a)))
        espiras.append(P.tube(f"{nombre}_espira{k}", pts, 0.011, coll, m=m_cable, res=2))
    # engranajes: uno grande en el tambor y uno chico (motor) que lo mueve
    g1 = engranaje(nombre + "_engranajeG", coll, m_ac, r=0.30, dientes=36, ancho=0.05, alto_diente=0.035)
    g1.rotation_euler = rot
    g1.location = (0.26, 0, 0)
    g2 = engranaje(nombre + "_engranajeC", coll, m_ac, r=0.13, dientes=16, ancho=0.05, alto_diente=0.035)
    g2.rotation_euler = rot
    g2.location = (0.26, 0.0, 0.30 + 0.13 + 0.032)
    motor = P.prim("cyl", nombre + "_motor", coll, U.pintura("MotorAzul", (0.05, 0.18, 0.45), 0.2), r=0.10, r_top=0.10, h=0.28, seg=32)
    motor.rotation_euler = rot
    motor.location = (0.45, 0.0, 0.30 + 0.13 + 0.032)
    # disco de freno y pinza
    disco = P.prim("cyl", nombre + "_disco", coll, m_ac, r=0.26, r_top=0.26, h=0.018, seg=64)
    disco.rotation_euler = rot
    disco.location = (-0.27, 0, 0)
    agujeros = []
    for k in range(12):
        a = 2 * math.pi * k / 12
        h = P.prim("cyl", f"{nombre}_aguj{k}", coll, m_os, r=0.012, r_top=0.012, h=0.022, seg=12)
        h.parent = disco                      # en el espacio del disco (girado 90° en Y): x local = -z del mundo
        h.location = (-0.19 * math.sin(a), 0.19 * math.cos(a), 0)
        agujeros.append(h)
    pinza = bpy.data.objects.new(nombre + "_pinza", None)
    coll.objects.link(pinza)
    pinza.location = (-0.27, 0.0, 0.215)
    pastillas = []
    for s in (-1, 1):
        pz = P.prim("cube", f"{nombre}_pinza{s}", coll, m_ro)
        pz.scale = (0.05, 0.16, 0.11)
        pz.location = (-0.27 + s * 0.045, 0.0, 0.215)
        P.bevel(pz, 0.012, 3)
        pastillas.append(pz)
    # rueda de trinquete y pestillo
    trinq = engranaje(nombre + "_trinquete", coll, m_os, r=0.20, dientes=18, ancho=0.04, alto_diente=0.05)
    trinq.rotation_euler = rot
    trinq.location = (-0.12, 0, 0)
    pest_piv = bpy.data.objects.new(nombre + "_pestillo", None)
    coll.objects.link(pest_piv)
    pest_piv.location = (-0.12, -0.10, 0.30)
    pest = P.prim("cube", nombre + "_pestilloBarra", coll, m_am)
    pest.scale = (0.035, 0.035, 0.14)
    pest.location = (-0.12, -0.075, 0.245)
    pest.rotation_euler = (math.radians(-35), 0, 0)
    P.bevel(pest, 0.008, 2)
    colgar(pest, pest_piv)
    # carcasa (con nodo 'Corte' para volverla transparente)
    m_car = bpy.data.materials.new("Carcasa")
    m_car.use_nodes = True
    nt = m_car.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.95, 0.62, 0.0, 1)
    b.inputs["Roughness"].default_value = 0.35
    b.inputs["Coat Weight"].default_value = 0.4
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.name = "Corte"
    mix.inputs["Fac"].default_value = 0.0
    nt.links.new(b.outputs["BSDF"], mix.inputs[1])
    nt.links.new(tr.outputs["BSDF"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], nt.nodes["Material Output"].inputs["Surface"])
    car = P.prim("cyl", nombre + "_carcasa", coll, m_car, r=0.40, r_top=0.40, h=0.80, seg=64)
    car.rotation_euler = rot
    car.location = (0, 0, 0.05)
    car.visible_shadow = False
    partes.update(tambor=tambor, espiras=espiras, g1=g1, g2=g2, motor=motor, disco=disco, pinza=pinza, pastillas=pastillas,
                  trinquete=trinq, pestillo=pest_piv, carcasa=car)
    for o in [tambor, g1, g2, motor, disco, pinza, trinq, pest_piv, car] + espiras + pastillas:
        if o.parent is None:
            o.parent = raiz
    return raiz, partes


def corte(alpha):
    """0 = carcasa entera, 1 = transparente (se ve el interior)."""
    bpy.data.materials["Carcasa"].node_tree.nodes["Corte"].inputs["Fac"].default_value = max(0.0, min(1.0, alpha))


def cable_trenzado(coll, nombre="Trenzado", largo=1.6, hilos=6, r_hilo=0.018, r_vuelta=0.032, vueltas=3.0):
    """Hilos de acero en hélice alrededor del alma, a lo largo de X. pose_trenzado(t) abre o cierra la trenza."""
    m = U.acero("HiloAcero", (0.68, 0.69, 0.71))
    alma = P.tube(nombre + "_alma", [(0, 0, 0), (largo, 0, 0)], r_hilo * 0.9, coll, m=m, res=4)
    obs = []
    for h in range(hilos):
        ob = P.tube(f"{nombre}_hilo{h}", [(largo * i / 40, 0, 0) for i in range(41)], r_hilo, coll, m=m, res=3)
        ob["fase"] = 2 * math.pi * h / hilos
        obs.append(ob)
    return alma, obs, dict(largo=largo, r=r_vuelta, vueltas=vueltas)


def pose_trenzado(obs, info, giro, cierre):
    """giro: radianes extra de la hélice; cierre 0..1: los hilos llegan desde afuera (abiertos) hasta su vuelta."""
    L, rv, nv = info["largo"], info["r"], info["vueltas"]
    for ob in obs:
        sp = ob.data.splines[0]
        n = len(sp.points)
        for i, p in enumerate(sp.points):
            u = i / (n - 1)
            x = L * u
            a = ob["fase"] + 2 * math.pi * nv * u + giro
            # frente de cierre: lo que está detrás del frente queda trenzado; delante, abierto
            abierto = max(0.0, min(1.0, (u - cierre) * 6.0))
            r = rv * (1 + 4.0 * abierto)
            p.co = (x, r * math.cos(a), r * math.sin(a), 1)
