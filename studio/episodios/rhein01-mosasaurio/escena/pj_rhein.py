"""Personajes de Rhein 01, hechos para esta idea (dibujo animado 3D, propios, sin assets externos):
- Niño pescador (~1,25 m): impermeable amarillo, gorro de pescador azul, botas verdes, pecas, ojos grandes.
- Mosasaurio (~12 m): diseño propio a partir de reconstrucciones reales (cola en media luna, aletas de remo, mandíbulas
  largas con dientes cónicos), lomo azul petróleo y guata crema. Nada del de Jurassic World (sin cresta ni flecos).

Convenciones (las de personajes.py del Ep. 2): origen en el suelo entre los pies (niño) o en el centro del cuerpo
(mosasaurio); miran hacia -Y; ojos con nombre *_ojoL / *_ojoR (los usa el chequeo de cara tapada).
Cada parte que se anima cuelga de un vacío (pivote) con nombre fijo: así cada plano posa sin keyframes.
"""
import math, os, sys
import bmesh
import bpy
import numpy as np
from mathutils import Vector, Euler, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../plantilla")))
import props as P
from base_pj import blob, esfera, ojo, parpado, mat_simple, colgar, cuerno


def vacio(name, loc, coll, parent=None):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.05
    coll.objects.link(e)
    e.location = loc
    if parent:
        e.parent = parent
    return e


def colgar_en(obs, piv):
    for o in obs:
        colgar(o, piv)


def mat_goma(name, col, rough=0.32):
    m = mat_simple(name, col, rough=rough, coat=0.35)
    return m


# ======================================================================= NIÑO
PIEL = (0.93, 0.62, 0.47)


def nino(coll, nombre="Nino"):
    m_imp = mat_goma("Impermeable", (1.0, 0.70, 0.02), 0.34)
    m_piel = mat_simple("PielNino", PIEL, rough=0.55, sss=0.12)
    m_gorro = mat_simple("Gorro", (0.06, 0.16, 0.48), rough=0.7, sheen=0.4)
    m_pelo = mat_simple("PeloNino", (0.36, 0.14, 0.04), rough=0.6, sheen=0.3)
    m_jean = mat_simple("Jean", (0.10, 0.22, 0.52), rough=0.75, sheen=0.25)
    m_bota = mat_goma("Bota", (0.07, 0.42, 0.18), 0.3)
    m_boca = mat_simple("BocaNino", (0.38, 0.03, 0.05), rough=0.4)
    m_diente = mat_simple("DienteNino", (0.97, 0.95, 0.9), rough=0.3)
    m_ceja = mat_simple("CejaNino", (0.25, 0.09, 0.03), rough=0.7)
    m_peca = mat_simple("Peca", (0.68, 0.34, 0.20), rough=0.6)
    m_boton = mat_simple("Boton", (0.12, 0.12, 0.14), rough=0.3, coat=0.6)

    raiz = vacio(nombre, (0, 0, 0), coll)
    cadera = vacio(nombre + "_cadera", (0, 0, 0.40), coll, raiz)
    torso = vacio(nombre + "_torso", (0, 0, 0.42), coll, raiz)
    cabeza = vacio(nombre + "_cabeza", (0, 0, 0.80), coll, raiz)
    hombroL = vacio(nombre + "_hombroL", (0.165, 0.0, 0.72), coll, raiz)
    hombroR = vacio(nombre + "_hombroR", (-0.165, 0.0, 0.72), coll, raiz)
    piernaL = vacio(nombre + "_piernaL", (0.075, 0.0, 0.40), coll, raiz)
    piernaR = vacio(nombre + "_piernaR", (-0.075, 0.0, 0.40), coll, raiz)
    bpy.context.view_layer.update()

    # --- torso (impermeable)
    cuerpo = blob(nombre + "_impermeable", [
        ((0, 0, 0.64), (0.15, 0.125, 0.17), (0, 0, 0)),
        ((0, -0.005, 0.50), (0.19, 0.16, 0.12), (0, 0, 0)),
        ((0, -0.005, 0.43), (0.205, 0.17, 0.07), (0, 0, 0)),     # ruedo con vuelo
        ((0, 0.0, 0.76), (0.135, 0.11, 0.05), (0, 0, 0)),
        ((0, 0.06, 0.80), (0.12, 0.08, 0.055), (12, 0, 0)),      # capucha doblada atrás
    ], coll, voxel=0.006, suave=10)
    cuerpo.data.materials.append(m_imp)
    botones = [esfera(f"{nombre}_boton{i}", (0, -0.148 + 0.004 * i, 0.66 - 0.085 * i), 0.016, coll, m_boton, escala=(1, 0.5, 1))
               for i in range(3)]
    colgar_en([cuerpo] + botones, torso)

    # --- cabeza
    cab = esfera(nombre + "_cara", (0, 0, 1.02), 0.19, coll, m_piel, escala=(1.04, 0.98, 0.96))
    orejas = [esfera(f"{nombre}_oreja{s}", (sx * 0.192, 0.005, 1.0), 0.04, coll, m_piel, escala=(0.55, 0.8, 1))
              for s, sx in (("L", 1), ("R", -1))]
    nariz = esfera(nombre + "_nariz", (0, -0.192, 0.995), 0.027, coll, mat_simple("NarizNino", (0.95, 0.52, 0.40), 0.5, sss=0.15),
                   escala=(1.1, 0.9, 0.9))
    ojos = []
    for s, sx in (("L", 1), ("R", -1)):
        o = ojo(f"{nombre}_ojo{s}", (sx * 0.076, -0.142, 1.055), 0.060, (sx * 0.05, -2.0, 1.03), coll, (0.22, 0.42, 0.10), iris_frac=0.58, pupila_frac=0.45)
        p = parpado(f"{nombre}_parpado{s}", o, 0.060, coll, m_piel, abierto=0.0)
        p.rotation_euler = (math.radians(-112), 0, 0)
        ojos += [o, p]
    cejas = [cuerno(f"{nombre}_ceja{s}", (sx * 0.040, -0.172, 1.128), (sx, -0.25, 0.10), (0, 0, 1), 0.070, 0.012, 0.009,
                    coll=coll, m=m_ceja, curv=0.5) for s, sx in (("L", 1), ("R", -1))]
    boca = esfera(nombre + "_boca", (0, -0.168, 0.925), 0.062, coll, m_boca, escala=(1.0, 0.32, 0.34))
    dientes = blob(nombre + "_dientes", [((-0.017, -0.183, 0.944), (0.016, 0.010, 0.014), (0, 0, 0)),
                                         ((0.020, -0.183, 0.942), (0.015, 0.010, 0.013), (0, 0, 8))], coll, voxel=0.0025, suave=4)
    dientes.data.materials.append(m_diente)
    lengua = esfera(nombre + "_lengua", (0, -0.176, 0.908), 0.03, coll, mat_simple("LenguaNino", (0.85, 0.30, 0.32), 0.4, sss=0.2), escala=(1.2, 0.5, 0.45))
    m_mej = mat_simple("Mejilla", (0.98, 0.45, 0.40), rough=0.6, sss=0.1)
    mejillas = [esfera(f"{nombre}_mejilla{s}", (sx * 0.112, -0.150, 0.975), 0.03, coll, m_mej, escala=(1.0, 0.35, 0.75)) for s, sx in (("L", 1), ("R", -1))]
    pecas = []
    for s, sx in (("L", 1), ("R", -1)):
        for i, (dx, dz) in enumerate(((0.0, 0.0), (0.022, 0.012), (0.018, -0.016), (0.040, -0.002))):
            pecas.append(esfera(f"{nombre}_peca{s}{i}", (sx * (0.085 + dx), -0.163 + 0.012 * dx / 0.04, 0.985 + dz), 0.0065, coll, m_peca,
                                escala=(1, 0.4, 1)))
    # pelo que asoma bajo el gorro (mechones)
    pelo = blob(nombre + "_pelo", [
        ((0.0, -0.11, 1.135), (0.12, 0.06, 0.035), (-20, 0, 0)),
        ((0.13, -0.05, 1.10), (0.05, 0.08, 0.05), (0, 20, 0)),
        ((-0.13, -0.05, 1.10), (0.05, 0.08, 0.05), (0, -20, 0)),
        ((0.06, -0.135, 1.115), (0.045, 0.035, 0.03), (-10, 0, 25)),
        ((-0.05, -0.14, 1.11), (0.04, 0.035, 0.028), (-10, 0, -30)),
        ((0.0, 0.10, 1.07), (0.15, 0.08, 0.09), (0, 0, 0)),
    ], coll, voxel=0.006, suave=8)
    pelo.data.materials.append(m_pelo)
    # gorro de pescador: copa + ala inclinada hacia abajo
    copa = blob(nombre + "_gorro_copa", [((0, 0.01, 1.165), (0.178, 0.17, 0.085), (0, 0, 0)),
                                         ((0, 0.01, 1.20), (0.15, 0.145, 0.06), (0, 0, 0))], coll, voxel=0.006, suave=8)
    copa.data.materials.append(m_gorro)
    bm = bmesh.new()
    n = 64
    anillos = []
    for (r, z) in ((0.168, 1.155), (0.265, 1.115), (0.272, 1.105)):
        anillos.append([bm.verts.new(((r) * math.cos(2 * math.pi * k / n), 0.01 + r * math.sin(2 * math.pi * k / n), z)) for k in range(n)])
    for i in range(len(anillos) - 1):
        for k in range(n):
            bm.faces.new((anillos[i][k], anillos[i][(k + 1) % n], anillos[i + 1][(k + 1) % n], anillos[i + 1][k]))
    ala = P.mesh_obj(nombre + "_gorro_ala", bm, coll, m=m_gorro)
    sol = ala.modifiers.new("Grosor", "SOLIDIFY")
    sol.thickness = 0.012
    sub = ala.modifiers.new("Sub", "SUBSURF")
    sub.levels = sub.render_levels = 1
    gorro = vacio(nombre + "_gorro", (0, 0.02, 1.10), coll)
    bpy.context.view_layer.update()
    colgar_en([copa, ala], gorro)
    gorro.rotation_euler = (math.radians(-16), 0, 0)
    gorro.location.z += 0.02
    bpy.context.view_layer.update()
    mechon = cuerno(nombre + "_mechon", (0.02, -0.12, 1.14), (0.2, -0.6, 1), (1, 0, 0), 0.09, 0.022, 0.004, coll=coll, m=m_pelo, curv=1.2)
    colgar_en([cab, nariz, boca, dientes, lengua, pelo, mechon, copa, ala] + mejillas + orejas + cejas + pecas + [o for o in ojos if o.name.endswith(("ojoL", "ojoR"))], cabeza)

    # --- brazos (mangas + manos), cuelgan del hombro hacia abajo
    for s, sx, piv in (("L", 1, hombroL), ("R", -1, hombroR)):
        manga = cuerno(f"{nombre}_manga{s}", (sx * 0.165, 0, 0.73), (sx * 0.25, 0, -1), (sx * 0.4, -0.3, 0), 0.30, 0.058, 0.048,
                       coll=coll, m=m_imp, curv=0.15)
        mano = esfera(f"{nombre}_mano{s}", (sx * 0.245, -0.02, 0.42), 0.048, coll, m_piel, escala=(0.9, 0.8, 1.05))
        pulgar = esfera(f"{nombre}_pulgar{s}", (sx * 0.228, -0.058, 0.445), 0.019, coll, m_piel, escala=(1, 1, 1.3))
        colgar_en([manga, mano, pulgar], piv)
    # --- piernas (jean + bota)
    for s, sx, piv in (("L", 1, piernaL), ("R", -1, piernaR)):
        pierna = cuerno(f"{nombre}_pierna{s}", (sx * 0.075, 0, 0.42), (0, 0, -1), (0, -1, 0), 0.22, 0.065, 0.058, coll=coll, m=m_jean, curv=0.02)
        bota = blob(f"{nombre}_bota{s}", [((sx * 0.075, -0.01, 0.12), (0.068, 0.072, 0.11), (0, 0, 0)),
                                          ((sx * 0.075, -0.05, 0.04), (0.07, 0.11, 0.045), (0, 0, 0))], coll, voxel=0.006, suave=6)
        bota.data.materials.append(m_bota)
        colgar_en([pierna, bota], piv)
    return raiz


def pose_nino(raiz, f=0, cabeza=(0, 0, 0), torso=(0, 0, 0), brazoL=(0, 0, 0), brazoR=(0, 0, 0), piernaL=(0, 0, 0), piernaR=(0, 0, 0),
              parpadeo=True, boca=0.0, cejas=0.0, mirar=None):
    """Pone la pose (grados XYZ por pivote). boca 0..1 abre la boca; cejas -1..1 (enojado..sorpresa)."""
    n = raiz.name
    O = bpy.data.objects
    for k, v in (("cabeza", cabeza), ("torso", torso), ("hombroL", brazoL), ("hombroR", brazoR), ("piernaL", piernaL), ("piernaR", piernaR)):
        O[f"{n}_{k}"].rotation_euler = Euler([math.radians(a) for a in v])
    # el torso arrastra hombros y cabeza: se componen a mano (pivotes hermanos, más fácil de posar)
    tq = O[f"{n}_torso"].rotation_euler.to_matrix()
    base_t = Vector((0, 0, 0.42))
    for k, p0 in (("cabeza", (0, 0, 0.80)), ("hombroL", (0.165, 0, 0.72)), ("hombroR", (-0.165, 0, 0.72))):
        O[f"{n}_{k}"].location = base_t + tq @ (Vector(p0) - base_t)
        O[f"{n}_{k}"].rotation_euler = (tq @ O[f"{n}_{k}"].rotation_euler.to_matrix()).to_euler()
    # parpadeo cada ~2,7 s
    ab = 1.0
    if parpadeo:
        fase = (f % 81)
        if fase < 5:
            ab = abs(fase - 2.5) / 2.5
    for s in "LR":
        O[f"{n}_parpado{s}"].rotation_euler = (math.radians(-112 + 197 * (1 - ab)), 0, 0)
        c = O[f"{n}_ceja{s}"]
        c.location.z = 0.012 * cejas
    b = O[f"{n}_boca"]
    b.scale = (1.0 - 0.15 * boca, 1.0, 1.0 + 1.3 * boca)
    O[f"{n}_lengua"].location.z = -0.012 * boca


# ======================================================================= MOSASAURIO
def mat_mosa():
    m = bpy.data.materials.get("Mosasaurio")
    if m:
        return m
    m = bpy.data.materials.new("Mosasaurio")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.38
    b.inputs["Coat Weight"].default_value = 0.4
    b.inputs["Coat Roughness"].default_value = 0.15
    b.inputs["Subsurface Weight"].default_value = 0.05
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sepn = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Normal"], sepn.inputs[0])
    guata = nt.nodes.new("ShaderNodeMapRange")          # normal hacia abajo → guata clara (contrasombreado)
    guata.inputs["From Min"].default_value = 0.05
    guata.inputs["From Max"].default_value = -0.35
    nt.links.new(sepn.outputs["Z"], guata.inputs["Value"])
    base = nt.nodes.new("ShaderNodeMix")
    base.data_type = "RGBA"
    base.inputs["A"].default_value = (0.03, 0.16, 0.24, 1)     # lomo azul petróleo
    base.inputs["B"].default_value = (0.86, 0.80, 0.64, 1)     # guata crema
    nt.links.new(guata.outputs["Result"], base.inputs["Factor"])
    # franjas oscuras suaves en el lomo
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    wav = nt.nodes.new("ShaderNodeTexWave")
    wav.inputs["Scale"].default_value = 0.9
    wav.inputs["Distortion"].default_value = 2.5
    wav.bands_direction = "Y"
    nt.links.new(tc.outputs["Object"], wav.inputs["Vector"])
    fr = nt.nodes.new("ShaderNodeMapRange")
    fr.inputs["From Min"].default_value = 0.55
    fr.inputs["From Max"].default_value = 0.85
    nt.links.new(wav.outputs["Fac"], fr.inputs["Value"])
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    nt.links.new(guata.outputs["Result"], inv.inputs[1])
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    nt.links.new(fr.outputs["Result"], mul.inputs[0])
    nt.links.new(inv.outputs[0], mul.inputs[1])
    mul2 = nt.nodes.new("ShaderNodeMath")
    mul2.operation = "MULTIPLY"
    mul2.inputs[1].default_value = 0.55
    nt.links.new(mul.outputs[0], mul2.inputs[0])
    fra = nt.nodes.new("ShaderNodeMix")
    fra.data_type = "RGBA"
    fra.inputs["B"].default_value = (0.012, 0.07, 0.11, 1)
    nt.links.new(base.outputs["Result"], fra.inputs["A"])
    nt.links.new(mul2.outputs[0], fra.inputs["Factor"])
    nt.links.new(fra.outputs["Result"], b.inputs["Base Color"])
    # escamas: bump de voronoi
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 7.0
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.12
    bump.inputs["Distance"].default_value = 0.02
    nt.links.new(vor.outputs["Distance"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def _dientes(nombre, puntos, coll, m, hacia, largo=0.26, r=0.075):
    obs = []
    for i, p in enumerate(puntos):
        k = 0.75 + 0.25 * math.sin(i * 1.7)
        obs.append(cuerno(f"{nombre}{i}", p, hacia, (0, -1, 0), largo * k, r * k, 0.008, coll=coll, m=m, curv=0.35, n=10, seg=12))
    return obs


def mosasaurio(coll, nombre="Mosa"):
    m = mat_mosa()
    m_boca = mat_simple("BocaMosa", (0.55, 0.12, 0.14), rough=0.45, sss=0.2)
    m_diente = mat_simple("DienteMosa", (0.96, 0.92, 0.80), rough=0.25, coat=0.4)
    raiz = vacio(nombre, (0, 0, 0), coll)
    mandi = vacio(nombre + "_mandibula", (0, -3.55, -0.38), coll, raiz)      # bisagra de la mandíbula
    bpy.context.view_layer.update()
    cuerpo = blob(nombre + "_cuerpo", [
        ((0, -5.25, 0.05), (0.52, 1.25, 0.40), (4, 0, 0)),        # hocico (mandíbula superior)
        ((0, -4.15, 0.12), (0.80, 1.05, 0.62), (0, 0, 0)),        # cabeza
        ((0, -2.85, 0.05), (1.05, 1.20, 0.95), (0, 0, 0)),        # cuello
        ((0, -1.10, 0.0), (1.38, 2.10, 1.22), (0, 0, 0)),         # pecho
        ((0, 1.20, 0.0), (1.15, 2.10, 1.02), (0, 0, 0)),          # vientre
        ((0, 3.40, 0.0), (0.72, 1.90, 0.74), (0, 0, 0)),          # cola
        ((0, 5.20, 0.0), (0.38, 1.40, 0.46), (0, 0, 0)),          # punta de la cola
        ((0, -4.35, 0.62), (0.55, 0.55, 0.16), (0, 0, 0)),        # ceja ósea (frente)
    ], coll, voxel=0.06, suave=12)
    cuerpo.data.materials.append(m)
    # cola en media luna (lóbulo de abajo más grande, como en las reconstrucciones modernas)
    aleta_c = blob(nombre + "_aleta_cola", [
        ((0, 6.55, -0.85), (0.12, 0.62, 1.15), (-32, 0, 0)),
        ((0, 6.45, 0.65), (0.10, 0.48, 0.75), (28, 0, 0)),
        ((0, 6.05, 0.0), (0.22, 0.55, 0.40), (0, 0, 0)),
    ], coll, voxel=0.05, suave=10)
    aleta_c.data.materials.append(m)
    aletas = []
    for s, sx in (("L", 1), ("R", -1)):
        for j, (y, l) in enumerate(((-1.7, 1.55), (1.9, 1.15))):
            a = blob(f"{nombre}_aleta{s}{j}", [((sx * (1.2 + l * 0.55), y + 0.35, -0.55), (l * 0.62, 0.42, 0.09), (0, -sx * 22, sx * 18))],
                     coll, voxel=0.05, suave=10)
            a.data.materials.append(m)
            aletas.append(a)
    # boca: interior y mandíbula inferior
    interior = blob(nombre + "_interior", [((0, -4.6, -0.12), (0.46, 1.6, 0.22), (0, 0, 0))], coll, voxel=0.05, suave=6)
    interior.data.materials.append(m_boca)
    mand = blob(nombre + "_mandibula_inf", [
        ((0, -5.05, -0.34), (0.42, 1.30, 0.20), (-3, 0, 0)),
        ((0, -3.9, -0.40), (0.72, 0.95, 0.30), (0, 0, 0)),
    ], coll, voxel=0.05, suave=10)
    mand.data.materials.append(m)
    # dientes: fila de arriba (apuntan abajo) y de abajo (apuntan arriba)
    sup, inf = [], []
    for s, sx in (("L", 1), ("R", -1)):
        sup += _dientes(f"{nombre}_dsup{s}", [(sx * (0.40 - 0.055 * i), -6.15 + 0.30 * i, -0.18) for i in range(8)][::-1], coll, m_diente, (0, -0.15, -1))
        inf += _dientes(f"{nombre}_dinf{s}", [(sx * (0.36 - 0.05 * i), -5.95 + 0.30 * i, -0.22) for i in range(7)][::-1], coll, m_diente, (0, -0.15, 1),
                        largo=0.22, r=0.065)
    colgar_en([mand] + inf, mandi)
    # ojos grandes amarillos con ceja
    ojos = []
    for s, sx in (("L", 1), ("R", -1)):
        o = ojo(f"{nombre}_ojo{s}", (sx * 0.62, -4.45, 0.42), 0.24, (sx * 3.0, -6.0, 0.6), coll, (0.95, 0.62, 0.02), iris_frac=0.7, pupila_frac=0.35)
        pp = parpado(f"{nombre}_parpado{s}", o, 0.24, coll, m)
        pp.rotation_euler = (math.radians(-70), 0, 0)
        ojos.append(o)
    for o in [cuerpo, aleta_c, interior] + aletas + sup + ojos:
        colgar(o, raiz)
    return raiz


class Ondula:
    """Ondulación lateral del cuerpo del mosasaurio: deforma los vértices (cola mucho, cabeza nada) sin esqueleto."""

    def __init__(self, raiz):
        n = raiz.name
        self.obs = [o for o in bpy.data.objects if o.name.startswith(n + "_") and o.type == "MESH"
                    and not o.name.startswith((n + "_ojo", n + "_parpado", n + "_d", n + "_mandibula", n + "_interior"))]
        self.rest = {}
        for o in self.obs:
            co = np.empty(len(o.data.vertices) * 3, np.float32)
            o.data.vertices.foreach_get("co", co)
            self.rest[o.name] = co.reshape(-1, 3)
        bpy.context.view_layer.update()
        rinv = raiz.matrix_world.inverted()
        self.L = {}
        for o in self.obs:          # objeto → raíz: constante (las piezas van pegadas a la raíz)
            L = rinv @ o.matrix_world
            self.L[o.name] = (np.array(L), np.array(L.inverted()))
        self.raiz = raiz

    def aplicar(self, t, amp=0.55, frec=0.9, k=0.55):
        for o in self.obs:
            M, Mi = self.L[o.name]
            co = self.rest[o.name]
            h = np.c_[co, np.ones(len(co))] @ M.T
            y = h[:, 1]
            peso = np.clip((y + 2.5) / 9.0, 0, 1) ** 1.6
            h[:, 0] += amp * peso * np.sin(k * y - 2 * math.pi * frec * t)
            out = (h @ Mi.T)[:, :3].astype(np.float32)
            o.data.vertices.foreach_set("co", out.ravel())
            o.data.update()
