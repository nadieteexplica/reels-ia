"""Efectos de dibujo animado del Ep. 2 (sin simulación): llamas, lágrimas, vapor."""
import math, random
import bmesh
import bpy
from mathutils import Vector, Matrix, noise

import props as P


def mat_llama():
    m = bpy.data.materials.get("Llama")
    if m:
        return m
    m = bpy.data.materials.new("Llama")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    out = nt.nodes["Material Output"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    # a lo largo de la llama (Z generado: 0 base → 1 punta): amarillo → naranjo → rojo
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position = 0.0
    cr.elements[0].color = (1.0, 0.95, 0.55, 1)
    cr.elements[1].position = 1.0
    cr.elements[1].color = (0.9, 0.08, 0.01, 1)
    e = cr.elements.new(0.45)
    e.color = (1.0, 0.45, 0.04, 1)
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 9.0
    nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.45
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lw.outputs["Facing"], mix.inputs["Fac"])
    nt.links.new(em.outputs[0], mix.inputs[1])
    nt.links.new(tr.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def lengua_de_fuego(name, largo, ancho, coll, seed=0, curva=0.25):
    """Una lengua de fuego: gota alargada, ondulada, con base ancha en z=0 y punta en z=largo (eje +Z local)."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    n, seg = 26, 20
    rings = []
    for i in range(n + 1):
        t = i / n
        r = ancho * (math.sin(min(1, t * 3.2) * math.pi / 2)) * (1 - t) ** 1.1 + 0.0003
        cx = curva * largo * math.sin(t * math.pi * 0.8 + seed) * t
        cy = 0.15 * largo * noise.noise(Vector((t * 2.0, seed, 0)))
        ring = [bm.verts.new((cx + r * math.cos(2 * math.pi * j / seg), cy + r * math.sin(2 * math.pi * j / seg) * 0.8, largo * t)) for j in range(seg)]
        rings.append(ring)
    for i in range(n):
        for j in range(seg):
            bm.faces.new((rings[i][j], rings[i][(j + 1) % seg], rings[i + 1][(j + 1) % seg], rings[i + 1][j]))
    bm.faces.new(list(reversed(rings[0])))
    ob = P.mesh_obj(name, bm, coll, m=mat_llama())
    ob.visible_shadow = False
    return ob


def llamarada(name, origen, direccion, coll, escala=1.0, seed=3, n=5):
    """Llamarada que sale de una boca: varias lenguas de fuego en abanico + luz naranja. Devuelve la raíz (empty)."""
    rnd = random.Random(seed)
    root = P.empty(name, loc=origen, coll=coll)
    d = Vector(direccion).normalized()
    root.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    for k in range(n):
        L = escala * rnd.uniform(0.07, 0.13) * (1.3 if k == 0 else 1.0)
        f = lengua_de_fuego(f"{name}_{k}", L, escala * rnd.uniform(0.012, 0.02), coll, seed=seed + k, curva=rnd.uniform(-0.3, 0.3))
        f.parent = root
        f.rotation_euler = (rnd.uniform(-0.35, 0.35), rnd.uniform(-0.35, 0.35), rnd.uniform(0, math.pi))
    luz = bpy.data.lights.new(name + "_luz", "POINT")
    luz.energy, luz.color, luz.shadow_soft_size = 6.0 * escala, (1.0, 0.45, 0.10), 0.03
    lo = bpy.data.objects.new(name + "_luz", luz)
    coll.objects.link(lo)
    lo.parent = root
    lo.location = (0, 0, 0.04 * escala)
    return root


def mat_lagrima():
    m = bpy.data.materials.get("Lagrima")
    if m:
        return m
    m = P.mat("Lagrima", (0.70, 0.88, 1.0), rough=0.03, transmission=1.0)
    m.node_tree.nodes["Principled BSDF"].inputs["IOR"].default_value = 1.33
    return m


def lagrimas(name, ojo_world, abajo, coll, largo=0.03, r=0.0022, gotas=2, seed=0):
    """Chorro de lágrima desde el ojo por la mejilla + gotas que saltan."""
    rnd = random.Random(seed)
    o = Vector(ojo_world)
    a = Vector(abajo).normalized()
    pts = [o, o + a * largo * 0.4 + Vector((0, -0.003, 0)), o + a * largo + Vector((0, -0.004, 0))]
    t = P.tube(name + "_chorro", [tuple(p) for p in pts], r, coll, mat_lagrima())
    out = [t]
    for k in range(gotas):
        g = P.prim("sphere", f"{name}_gota{k}", coll, mat_lagrima(), r=r * 1.6)
        g.scale = (1, 1, 1.4)
        g.location = pts[-1] + Vector((rnd.uniform(-1, 1) * 0.01, -0.006 - 0.008 * k, -0.006 * k))
        out.append(g)
    return out
