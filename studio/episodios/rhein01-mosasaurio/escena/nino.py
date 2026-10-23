"""Rhein 01 — el niño pescador semi-realista (MakeHuman CC0 ~10 años, rig propio mixamorig:*, pj/nino.blend).

Impermeable amarillo, jeans, botas de goma verdes, gorro de pescador azul (procedural, pegado a la cabeza), pecas.
La actuación es procedural (huesos + 34 shape keys FACS), sin animaciones de Mixamo: el render no depende del repo
privado y cada pose se controla exacta (manos sin objetos agarrados: regla de LECCIONES #2).

  pj = cargar(sc, x, y, z, rot_z)
  pose(pj, f, expr={"susto": 1}, brazoL=(...), brazoR=(...), ...)
"""
import math, os
import bpy
import bmesh
import numpy as np
from mathutils import Vector, Euler, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
BLEND = os.path.join(HERE, "pj", "nino.blend")
P = "mixamorig:"


def _mat(nombre, color, rough=0.5, sss=0.0, coat=0.0, sheen=0.0):
    m = bpy.data.materials.get(nombre) or bpy.data.materials.new(nombre)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Subsurface Weight"].default_value = sss
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Sheen Weight"].default_value = sheen
    return m


def _pegar(ob, rig, hueso="Head"):
    mw = ob.matrix_world.copy()
    ob.parent = rig
    ob.parent_type = "BONE"
    ob.parent_bone = P + hueso
    bpy.context.view_layer.update()
    ob.matrix_world = mw


def _gorro(rig, cuerpo):
    """Gorro de pescador azul: copa redonda + ala ancha que cae un poco. Se calza sobre la cabeza del cuerpo."""
    bpy.context.view_layer.update()
    H = rig.matrix_world @ rig.pose.bones[P + "Head"].head
    co = np.array([cuerpo.matrix_world @ v.co for v in cuerpo.data.vertices])
    top = co[:, 2].max()
    cab = co[(co[:, 2] > top - 0.055)]
    cx, cy = float(np.median(cab[:, 0])), float(np.median(cab[:, 1]))
    r = float(np.percentile(np.hypot(cab[:, 0] - cx, cab[:, 1] - cy), 99)) + 0.016
    z0 = top - 0.050
    bm = bmesh.new()
    n = 72
    perfil = [(r * 1.0, z0 - 0.004), (r * 1.0, z0 + 0.025), (r * 0.95, z0 + 0.052), (r * 0.80, z0 + 0.072), (r * 0.45, z0 + 0.084), (0.0, z0 + 0.087)]
    ala = [(r * 1.0, z0 - 0.002), (r * 1.32, z0 - 0.020), (r * 1.46, z0 - 0.034)]
    rings = []
    for (rr, zz) in list(reversed(ala))[:-1] + perfil:
        rings.append([bm.verts.new((cx + rr * math.cos(2 * math.pi * k / n), cy + rr * 1.06 * math.sin(2 * math.pi * k / n), zz)) for k in range(n)])
    for i in range(len(rings) - 1):
        for k in range(n):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % n], rings[i + 1][(k + 1) % n], rings[i + 1][k]))
    me = bpy.data.meshes.new("Gorro")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new("Gorro", me)
    bpy.context.scene.collection.objects.link(ob)
    so = ob.modifiers.new("Grosor", "SOLIDIFY")
    so.thickness = 0.008
    sd = ob.modifiers.new("Sub", "SUBSURF")
    sd.levels = sd.render_levels = 2
    m = _mat("GorroTela", (0.035, 0.11, 0.38), rough=0.85, sheen=0.5)
    nt = m.node_tree
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 600
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.15
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], nt.nodes["Principled BSDF"].inputs["Normal"])
    me.materials.append(m)
    # costura del ala (una línea más oscura)
    ob.rotation_euler = (math.radians(-10), 0, 0)            # inclinado hacia atrás: no tapa los ojos
    ob.location = (0, 0.004, 0.0)
    _pegar(ob, rig, "Head")
    return ob


def cargar(sc, x=0.0, y=0.0, z=0.0, rot_z=0.0, sin_pelo=False):
    with bpy.data.libraries.load(BLEND, link=False) as (src, dst):
        dst.objects = [n for n in src.objects]
    for ob in dst.objects:
        if ob is not None:
            sc.collection.objects.link(ob)
    rig = bpy.data.objects["Rig"]
    cuerpo = bpy.data.objects["Cuerpo"]
    piel = bpy.data.materials.get("Piel")
    if piel:
        b = piel.node_tree.nodes["Principled BSDF"]
        b.inputs["Subsurface Weight"].default_value = 0.15
        b.inputs["Roughness"].default_value = 0.48
    imp = bpy.data.materials.get("Impermeable")
    if imp:
        b = imp.node_tree.nodes["Principled BSDF"]
        b.inputs["Roughness"].default_value = 0.28
        b.inputs["Coat Weight"].default_value = 0.7
        b.inputs["Coat Roughness"].default_value = 0.1
    gorro = _gorro(rig, cuerpo)
    if sin_pelo and "Pelo" in bpy.data.objects:
        bpy.data.objects["Pelo"].hide_render = True
    rig.location = (x, y, z)
    rig.rotation_euler = (0, 0, rot_z)
    pb = rig.pose.bones
    for b_ in pb:
        b_.rotation_mode = "XYZ"
    pj = {"rig": rig, "cuerpo": cuerpo, "pb": pb, "keys": cuerpo.data.shape_keys.key_blocks, "gorro": gorro}
    pose(pj, 1)
    return pj


EXPR = {
    "neutro": {},
    "susto": {"eye-left-opened-up": 1.0, "eye-right-opened-up": 1.0, "eyebrows-left-up": 1.0, "eyebrows-right-up": 1.0,
              "eyebrows-left-inner-up": 0.8, "eyebrows-right-inner-up": 0.8, "mouth-open": 1.0, "mouth-retraction": 0.4,
              "nose-left-dilatation": 0.5, "nose-right-dilatation": 0.5},
    "sonrisa": {"mouth-corner-puller": 1.0, "eyebrows-left-up": 0.3, "eyebrows-right-up": 0.3, "mouth-open": 0.2},
    "picaro": {"mouth-corner-puller": 0.8, "eyebrows-left-up": 0.8, "eyebrows-right-down": 0.4, "eye-right-slit": 0.35},
    "orgullo": {"mouth-corner-puller": 1.0, "eye-left-slit": 0.25, "eye-right-slit": 0.25, "eyebrows-left-up": 0.5,
                "eyebrows-right-up": 0.5},
    "concentrado": {"eyebrows-left-down": 0.6, "eyebrows-right-down": 0.6, "mouth-pursing": 0.5, "eye-left-slit": 0.3,
                    "eye-right-slit": 0.3},
    "grito": {"eye-left-opened-up": 1.0, "eye-right-opened-up": 1.0, "eyebrows-left-up": 1.0, "eyebrows-right-up": 1.0,
              "mouth-open": 1.0, "mouth-corner-puller": 0.5},
    "asco": {"mouth-upward-retraction": 0.7, "nose-left-elevation": 0.8, "nose-right-elevation": 0.8, "eye-left-slit": 0.6,
             "eye-right-slit": 0.6, "eyebrows-left-down": 0.6, "eyebrows-right-down": 0.6},
}

# poses de brazo (grados en Arm / ForeArm). En reposo del rig (pose T) los brazos van hacia los lados.
BRAZO = {          # medidos con el rig: Arm X+ baja el brazo, Z+ lo lleva adelante (izq.); ForeArm Z+ dobla el codo hacia adelante
    "abajo": ((80, 0, 4), (0, 0, 6)),
    "jarra": ((62, 0, -12), (95, 0, 10)),                 # mano en la cintura
    "apunta": ((8, 0, 84), (0, 0, 4)),                    # brazo estirado adelante
    "arriba": ((-72, 0, 6), (0, 0, 14)),                  # brazo arriba (celebra)
    "agarra": ((52, 0, 46), (0, 0, 62)),                  # manos al frente, a la altura del pecho (agarra la barra)
    "pulgar": ((74, 0, 28), (0, 0, 105)),                 # codo doblado, mano arriba (pulgar arriba)
    "senal": ((-20, 0, 40), (0, 0, 60)),                  # mano arriba adelante, haciendo señas a la grúa
}


def _set(pb, nombre, rot):
    b = pb.get(P + nombre)
    if b:
        b.rotation_euler = Euler([math.radians(v) for v in rot], "XYZ")


def _mezcla_rot(a, b, x):
    return tuple(a[i] + (b[i] - a[i]) * x for i in range(3))


def brazo(nombre, x=1.0, desde="abajo"):
    """Pose de brazo interpolada (x de 0 a 1 desde `desde`)."""
    a, b = BRAZO[desde], BRAZO[nombre]
    return (_mezcla_rot(a[0], b[0], x), _mezcla_rot(a[1], b[1], x))


def pose(pj, f, expr=None, cabeza=(0, 0, 0), cuello=(0, 0, 0), torso=(0, 0, 0), brazoL=None, brazoR=None,
         sentado=0.0, rodillas=0.0, parpadeo=0.0, respira=True, hombros=0.0):
    """brazoL/brazoR = ((arm xyz), (forearm xyz)) en grados; el lado R se espeja solo (Y y Z cambian de signo).
    sentado 0..1 dobla caderas 90° y rodillas 90°."""
    pb = pj["pb"]
    for side, s, br in (("Left", 1, brazoL), ("Right", -1, brazoR)):
        arm, fore = br if br else BRAZO["abajo"]
        _set(pb, side + "Arm", (arm[0], arm[1] * s, arm[2] * s))
        _set(pb, side + "ForeArm", (fore[0], fore[1] * s, fore[2] * s))
        _set(pb, side + "Shoulder", (-16 * hombros, 0, 0))
        _set(pb, side + "UpLeg", (90 * sentado + 10 * rodillas, 0, 0))
        _set(pb, side + "Leg", (-95 * sentado - 20 * rodillas, 0, 0))
        _set(pb, side + "Foot", (8 * sentado + 10 * rodillas, 0, 0))
    resp = math.sin(f / 30 * 2 * math.pi / 3.2) * (1.2 if respira else 0)
    _set(pb, "Spine", (torso[0] * 0.4, torso[1] * 0.4, torso[2] * 0.4))
    _set(pb, "Spine2", (torso[0] * 0.6 + resp, torso[1] * 0.6, torso[2] * 0.6))
    _set(pb, "Neck", cuello)
    _set(pb, "Head", cabeza)
    keys = pj["keys"]
    pesos = {}
    for nombre, w in (expr or {}).items():
        for k, v in EXPR[nombre].items():
            pesos[k] = pesos.get(k, 0.0) + v * w
    for kb in keys[1:]:
        kb.value = 0.0
    for k, v in pesos.items():
        if k in keys:
            keys[k].value = max(0.0, min(1.0, v))
    if parpadeo:
        for k in ("eye-left-closure", "eye-right-closure"):
            if k in keys:
                keys[k].value = max(keys[k].value, parpadeo)


def parpadeo(f, cada=88, fase=0):
    k = (f + fase) % cada
    return max(0.0, 1 - abs(k - 3) / 3) if k < 7 else 0.0


def ojos(pj):
    return [o for o in (bpy.data.objects.get("Ojo.L"), bpy.data.objects.get("Ojo.R")) if o]
