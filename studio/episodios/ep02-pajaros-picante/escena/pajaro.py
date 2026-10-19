"""Importa un modelo de animal (glb/gltf/fbx/obj/blend) y lo deja listo para el set:
raíz vacía con origen en las patas (z mínima), escalado a un largo dado y mirando a -Y."""
import os
import bpy
from mathutils import Vector


def _importar_archivo(path):
    antes = set(bpy.data.objects)
    ext = os.path.splitext(path)[1].lower()
    if ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=path)
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=path)
    elif ext == ".obj":
        bpy.ops.wm.obj_import(filepath=path)
    elif ext == ".ply":
        bpy.ops.wm.ply_import(filepath=path)
    elif ext == ".stl":
        bpy.ops.wm.stl_import(filepath=path)
    elif ext == ".blend":
        with bpy.data.libraries.load(path) as (src, dst):
            dst.objects = list(src.objects)
        for o in dst.objects:
            if o:
                bpy.context.scene.collection.objects.link(o)
    else:
        raise ValueError(f"formato no soportado: {ext}")
    return [o for o in bpy.data.objects if o not in antes]


def bbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def importar(path, coll=None, largo=0.22, nombre="Pajaro", eje_largo=None):
    nuevos = _importar_archivo(path)
    bpy.context.view_layer.update()
    raiz = bpy.data.objects.new(nombre, None)
    (coll or bpy.context.scene.collection).objects.link(raiz)
    tops = [o for o in nuevos if o.parent is None or o.parent not in nuevos]
    for o in nuevos:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        (coll or bpy.context.scene.collection).objects.link(o)
    lo, hi = bbox(nuevos)
    size = hi - lo
    L = eje_largo or max(size.x, size.y)   # largo del cuerpo en el plano horizontal
    s = largo / L if L > 0 else 1.0
    centro = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    for o in tops:
        mw = o.matrix_world.copy()
        o.parent = raiz
        o.matrix_parent_inverse.identity()
        o.matrix_basis = mw
        o.location = (o.location - centro)
    raiz.scale = (s, s, s)
    bpy.context.view_layer.update()
    return raiz
