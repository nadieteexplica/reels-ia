"""Personajes del Ep. 10: Mixamo "With Skin" del Release privado Personajes (nunca al repo público), vestidos de época.

- piloto (Ejército, 1945): mono de vuelo caqui, gorro de cuero con antiparras (Objaverse, CC-BY), bufanda blanca y cinta
  blanca con el sol rojo (hachimaki). Sin pelo a la vista (lo tapa el gorro).
- oficial: uniforme verde oliva y gorra con visera (procedural).
- marinero (Armada de EE.UU., 1945): camisa celeste de faena, pantalón azul, casco M1 gris (Objaverse, CC-BY).

Si el FBX no está (en la sesión local no hay personajes privados), se pone un maniquí de cápsulas del mismo alto para
probar encuadres (lección 105). Los huesos se buscan por sufijo (":Head", ":LeftUpLeg"…).
"""
import math, os, glob
import bpy
from mathutils import Vector, Quaternion, Matrix

import ep10 as E
import sets10 as S
from ep10 import asset, asignar, liso

GESTOS = os.environ.get("GESTOS", "")
ROPA = {
    "piloto": {"arriba": (0.30, 0.26, 0.17), "abajo": (0.30, 0.26, 0.17), "zapatos": (0.06, 0.04, 0.025)},
    "oficial": {"arriba": (0.17, 0.16, 0.09), "abajo": (0.17, 0.16, 0.09), "zapatos": (0.035, 0.025, 0.018)},
    "marinero": {"arriba": (0.36, 0.46, 0.6), "abajo": (0.05, 0.07, 0.13), "zapatos": (0.03, 0.025, 0.02)},
}
PIEL = ("body", "skin", "head", "face", "eye", "lash", "brow", "teeth", "tongue", "ear", "hand", "arm")
PELO = ("hair", "beard", "mustache", "moustache")
ZAP = ("shoe", "boot", "sneak", "feet", "foot", "sandal")
ABAJO = ("pant", "jean", "trouser", "bottom", "short", "leg", "skirt")
QUITAR = ("hat", "cap", "helmet", "glass", "vest", "bag", "headphone", "mask", "glove")


def hueso(arm, sufijo):
    for b in arm.pose.bones:
        if b.name.split(":")[-1] == sufijo:
            return b
    return None


def pos_hueso(arm, sufijo, cola=False):
    b = hueso(arm, sufijo)
    if b is None:
        return None
    bpy.context.view_layer.update()
    return arm.matrix_world @ (b.tail if cola else b.head)


def _teñir(mat, color, desat=0.85):
    """Mantiene el detalle de la textura (pliegues, costuras) pero la lleva al color de época."""
    if not mat or not mat.use_nodes:
        return
    nt = mat.node_tree
    b = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if b is None:
        return
    ent = b.inputs["Base Color"]
    hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.inputs["Saturation"].default_value = 1 - desat
    mul = nt.nodes.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs[0].default_value = 1.0
    mul.inputs[7].default_value = (*[min(1.0, c * 2.4) for c in color], 1)
    if ent.links:
        src = ent.links[0].from_socket
        nt.links.remove(ent.links[0])
        nt.links.new(src, hsv.inputs["Color"])
    else:
        hsv.inputs["Color"].default_value = (0.42, 0.42, 0.42, 1)
    nt.links.new(hsv.outputs[0], mul.inputs[6])
    nt.links.new(mul.outputs[2], ent)
    b.inputs["Roughness"].default_value = 0.85


def maniqui(sc, pos, rot_z=0.0, alto=1.72, color=(0.3, 0.26, 0.17)):
    """Maniquí de cápsulas para probar encuadres en local."""
    raiz = bpy.data.objects.new("Maniqui", None); sc.collection.objects.link(raiz)
    m = S.tela("maniqui", color)
    for nombre, (r, z0, z1) in {"cuerpo": (0.17, 0.85, 1.45), "piernas": (0.13, 0.0, 0.9), "cabeza": (0.11, 1.5, 1.72)}.items():
        o = E.cilindro(sc, "Man_" + nombre, r, z1 - z0, (0, 0, z0), verts=24, mat=m)
        o.parent = raiz
    raiz.location = pos; raiz.rotation_euler.z = rot_z
    raiz["maniqui"] = True
    return raiz


def persona(sc, archivo, rol, pos, rot_z=0.0, pose=None, frame=40, alto=None):
    """Importa el personaje, lo viste para su rol y le copia una pose de Mixamo. Devuelve el armature (o el maniquí)."""
    try:
        p = asset(archivo)
    except FileNotFoundError:
        return maniqui(sc, pos, rot_z, color=ROPA[rol]["arriba"])
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=p, automatic_bone_orientation=False)
    nuevos = [o for o in bpy.data.objects if o not in antes]
    arm = next(o for o in nuevos if o.type == "ARMATURE")
    arm.animation_data_clear()
    ropa = ROPA[rol]
    for o in nuevos:
        if o.type != "MESH":
            continue
        n = o.name.lower()
        if any(k in n for k in QUITAR):
            o.hide_render = True
            continue
        if any(k in n for k in PELO):
            o.hide_render = rol in ("piloto", "marinero", "oficial")
            continue
        liso(o, 180)
        for s in o.material_slots:
            m = s.material
            if not m:
                continue
            mn = m.name.lower()
            if any(k in n or k in mn for k in ZAP):
                _teñir(m, ropa["zapatos"])
            elif any(k in n or k in mn for k in ABAJO):
                _teñir(m, ropa["abajo"])
            elif any(k in n or k in mn for k in PIEL):
                b = next((x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED"), None)
                if b:
                    b.inputs["Specular IOR Level"].default_value = 0.3
                    b.inputs["Roughness"].default_value = 0.55
            else:
                _teñir(m, ropa["arriba"])
    print("personaje", archivo, rol, "mallas:", [o.name for o in nuevos if o.type == "MESH"])
    arm.location = pos
    arm.rotation_euler.z = rot_z
    if pose:
        f = buscar_gesto(pose)
        if f:
            E.copiar_pose(arm, f, frame)
    if rol == "piloto":
        gorro_piloto(sc, arm)
    elif rol == "marinero":
        casco_m1(sc, arm)
    elif rol == "oficial":
        gorra_oficial(sc, arm)
    return arm


def buscar_gesto(nombre):
    if not GESTOS:
        return None
    k = nombre.lower().replace(" ", "").replace("_", "").replace(".", "")
    for f in glob.glob(os.path.join(GESTOS, "**", "*.fbx"), recursive=True):
        b = os.path.basename(f).lower().replace(" ", "").replace("_", "").replace(".", "")
        if b.startswith(k):
            return f
    return None


def _a_hueso(obj, arm, sufijo):
    """Pega un objeto al hueso (sigue a la cabeza en cada pose)."""
    b = hueso(arm, sufijo)
    if b is None:
        return
    mw = obj.matrix_world.copy()
    obj.parent = arm
    obj.parent_type = "BONE"
    obj.parent_bone = b.name
    bpy.context.view_layer.update()
    obj.matrix_world = mw


def _ancho_cabeza(arm):
    a = pos_hueso(arm, "Head"); c = pos_hueso(arm, "HeadTop_End") or pos_hueso(arm, "Head", cola=True)
    return a, c


def gorro_piloto(sc, arm):
    a, c = _ancho_cabeza(arm)
    if a is None:
        return
    centro = a.lerp(c, 0.55)
    try:
        g = S.importar("casco", largo=0.27, eje="z", nombre_raiz="GorroPiloto")
        g.location = centro - Vector((0, 0, 0.13))
        g.rotation_euler.z = arm.rotation_euler.z
        _a_hueso(g, arm, "Head")
    except Exception as e:
        print("sin gorro:", e)
    # cinta blanca con el sol rojo, alrededor de la frente
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.103, depth=0.032, end_fill_type="NOTHING", location=centro + Vector((0, 0, -0.02)))
    cinta = bpy.context.object; cinta.name = "Hachimaki"
    cinta.rotation_euler.z = arm.rotation_euler.z + math.radians(90)
    asignar(cinta, bpy.data.materials.get("hachimaki") or S.textura("hachimaki", "hachimaki.jpg", rugo=0.9))
    _a_hueso(cinta, arm, "Head")
    # bufanda blanca de seda al cuello
    n = pos_hueso(arm, "Neck")
    if n is not None:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.075, minor_radius=0.028, location=n + Vector((0, 0, 0.02)))
        bf = bpy.context.object; bf.name = "Bufanda"
        asignar(bf, bpy.data.materials.get("seda") or S.tela("seda", (0.85, 0.84, 0.8), rugo=0.5, escala=400))
        _a_hueso(bf, arm, "Neck")


def casco_m1(sc, arm):
    a, c = _ancho_cabeza(arm)
    if a is None:
        return
    try:
        h = S.importar("m1", largo=0.30, eje="y", nombre_raiz="CascoM1")
        h.location = a.lerp(c, 0.5) - Vector((0, 0, 0.02))
        h.rotation_euler.z = arm.rotation_euler.z
        gris = E.mat_pintura("gris_armada", (0.22, 0.24, 0.25), rugo=(0.55, 0.85), sucio=0.4, capa=0.0)
        for o in S.mallas_de(h):
            asignar(o, gris)
        _a_hueso(h, arm, "Head")
    except Exception as e:
        print("sin casco:", e)


def gorra_oficial(sc, arm):
    a, c = _ancho_cabeza(arm)
    if a is None:
        return
    centro = a.lerp(c, 0.8)
    verde = E.mat_pintura("gorra", (0.15, 0.14, 0.08), rugo=(0.6, 0.9), sucio=0.3, capa=0.0)
    copa = E.cilindro(sc, "GorraCopa", 0.105, 0.07, centro - Vector((0, 0, 0.02)), verts=32, mat=verde)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.08, depth=0.008, location=centro + Vector((0, 0.07, -0.02)))
    vis = bpy.context.object; vis.name = "Visera"; vis.scale = (1, 0.55, 1)
    asignar(vis, E.mat_pintura("visera", (0.02, 0.02, 0.02), capa=0.4))
    for o in (copa, vis):
        _a_hueso(o, arm, "Head")


# ---------------------------------------------------------------- movimiento procedural (sin animaciones nuevas)
def girar(arm, sufijo, eje, grados):
    b = hueso(arm, sufijo)
    if b is None:
        return
    b.rotation_mode = "QUATERNION"
    b.rotation_quaternion = b.rotation_quaternion @ Quaternion(Vector(eje), math.radians(grados))


def guardar_pose(arm):
    if arm.get("maniqui"):
        return {}
    return {b.name: b.rotation_quaternion.copy() for b in arm.pose.bones}


def volver_pose(arm, base):
    for b in arm.pose.bones:
        if b.name in base:
            b.rotation_mode = "QUATERNION"
            b.rotation_quaternion = base[b.name].copy()


def respirar(arm, base, t, fase=0.0):
    """Micro-movimiento de alguien parado: el pecho sube y baja, la cabeza se mueve apenas (nada quieto)."""
    if arm.get("maniqui"):
        return
    volver_pose(arm, base)
    girar(arm, "Spine1", (1, 0, 0), 1.2 * math.sin(t * 1.6 + fase))
    girar(arm, "Head", (0, 1, 0), 2.0 * math.sin(t * 0.45 + fase * 2))
    girar(arm, "Head", (1, 0, 0), 1.2 * math.sin(t * 0.33 + fase))


def mirar_arriba(arm, base, x):
    """x 0→1: la cabeza y el pecho se van hacia atrás para mirar al cielo."""
    if arm.get("maniqui"):
        return
    girar(arm, "Neck", (1, 0, 0), -25 * x)
    girar(arm, "Head", (1, 0, 0), -28 * x)
    girar(arm, "Spine2", (1, 0, 0), -8 * x)


def paso(arm, base, p0, adelante, x):
    """Un paso al frente (x de 0 a 1): la pierna izquierda se levanta y avanza, el cuerpo la sigue y la derecha cierra.
    `adelante` = vector unitario en el piso. Mueve el armature ~0,55 m."""
    arm.location = Vector(p0) + Vector(adelante) * 0.55 * E.suave(x)
    if arm.get("maniqui"):
        return
    volver_pose(arm, base)
    a = math.sin(math.pi * E.clamp(x / 0.6)) if x < 0.6 else 0.0
    b = math.sin(math.pi * E.clamp((x - 0.4) / 0.6)) if x > 0.4 else 0.0
    girar(arm, "LeftUpLeg", (1, 0, 0), -32 * a); girar(arm, "LeftLeg", (1, 0, 0), 45 * a)
    girar(arm, "RightUpLeg", (1, 0, 0), -26 * b); girar(arm, "RightLeg", (1, 0, 0), 38 * b)
    arm.location.z = Vector(p0).z + 0.025 * math.sin(math.pi * x)
