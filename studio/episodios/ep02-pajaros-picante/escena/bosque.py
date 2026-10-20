"""Set del bosque húmedo del sur de China (tupaya): rama con musgo, planta picante Piper con espigas colgando, hojas y niebla."""
import math, random
import bmesh
import bpy
from mathutils import Vector, noise
import props as P


def mat_corteza():
    m = bpy.data.materials.get("Corteza")
    if m:
        return m
    m = P.mat("Corteza", (0.16, 0.10, 0.06), rough=0.85)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 25.0
    nz.inputs["Detail"].default_value = 4.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.10, 0.06, 0.03, 1)
    ramp.color_ramp.elements[1].color = (0.18, 0.30, 0.08, 1)     # musgo
    ramp.color_ramp.elements[0].position = 0.40
    ramp.color_ramp.elements[1].position = 0.70
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.5
    nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def hoja(name, coll, L, W, m, curva=0.25):
    bm = bmesh.new()
    n = 10
    izq, der = [], []
    for i in range(n + 1):
        t = i / n
        w = W * math.sin(math.pi * t) ** 0.8 * (1 - 0.3 * t)
        z = -curva * L * t * t
        izq.append(bm.verts.new((-w / 2, t * L, z)))
        der.append(bm.verts.new((w / 2, t * L, z)))
    mid = [bm.verts.new((0, t / n * L, -curva * L * (t / n) ** 2 + 0.004 * L)) for t in range(n + 1)]
    for i in range(n):
        bm.faces.new((izq[i], mid[i], mid[i + 1], izq[i + 1]))
        bm.faces.new((mid[i], der[i], der[i + 1], mid[i + 1]))
    ob = P.mesh_obj(name, bm, coll, m=m)
    s = ob.modifiers.new("Sub", "SUBSURF")
    s.levels = s.render_levels = 1
    return ob


def espiga(name, coll, largo=0.09, r=0.0065, seed=0):
    """Espiga de Piper (inflorescencia cilíndrica, verde amarillenta con granitos). Origen = punta de arriba; cuelga hacia -Z."""
    m = P.mat("EspigaPiper", (0.55, 0.62, 0.18), rough=0.6, sss=0.2)
    nt = m.node_tree
    if len(nt.nodes) < 4:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        vor = nt.nodes.new("ShaderNodeTexVoronoi")
        vor.inputs["Scale"].default_value = 900.0
        nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.6
        nt.links.new(vor.outputs["Distance"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], nt.nodes["Principled BSDF"].inputs["Normal"])
    pts = [(0, 0, 0), (0.004, 0, -largo * 0.35), (0.002, 0.003, -largo * 0.7), (-0.003, 0.002, -largo)]
    t = P.tube(name, pts, r, coll, m, res=16)
    for k, pt in enumerate(t.data.splines[0].points):          # se afina hacia la punta
        pt.radius = (1.0, 1.0, 0.9, 0.55)[k]
    punta = P.prim("sphere", name + "_punta", coll, m, r=r * 0.55)   # punta redondeada (no cortada plana)
    punta.location = pts[-1]
    punta.parent = t
    return t


def armar(coll, seed=4):
    rnd = random.Random(seed)
    rama = P.tube("Rama", [(-0.9, 0.05, 0.08), (-0.3, 0.02, 0.12), (0.2, 0.0, 0.10), (0.7, 0.05, 0.16)], 0.035, coll, mat_corteza(), res=24)
    verde = P.mat("HojaBosque", (0.06, 0.26, 0.05), rough=0.45, sss=0.25)
    verde2 = P.mat("HojaBosque2", (0.10, 0.34, 0.08), rough=0.45, sss=0.25)
    hoja_piper = P.mat("HojaPiper", (0.07, 0.30, 0.06), rough=0.35, sss=0.2, coat=0.3)
    # mata de Piper colgando sobre la rama (a la derecha de la tupaya)
    espigas = []
    tallo_m = P.mat("TalloPiper", (0.05, 0.18, 0.04), rough=0.5)
    POS_ESP = [(0.085, -0.03, 0.33), (0.125, 0.0, 0.36), (0.045, 0.02, 0.38)]     # cerca del hocico de la tupaya
    for k, (x, y, z) in enumerate(POS_ESP):
        tallo = P.tube(f"TalloPiper{k}", [(x, y, z + 0.15), (x + 0.01, y, z + 0.07), (x, y, z)], 0.0018, coll, tallo_m)   # sin SSS (en un tubo tan fino se veía amarillo)
        e = espiga(f"Espiga{k}", coll, largo=rnd.uniform(0.08, 0.11), seed=k)
        e.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.45, 0.55, 0.10, 1)
        e.location = (x, y, z)
        espigas.append(e)
        for j in range(3):
            h = hoja(f"HojaPiper{k}_{j}", coll, 0.10, 0.07, hoja_piper)
            h.location = (x, y, z + 0.05 + 0.04 * j)
            h.rotation_euler = (math.radians(rnd.uniform(-40, -10)), 0, math.radians(rnd.uniform(0, 360)))
    # follaje de fondo (se ve desenfocado)
    for k in range(110):
        h = hoja(f"Fondo{k}", coll, rnd.uniform(0.15, 0.35), rnd.uniform(0.08, 0.16), rnd.choice([verde, verde2]))
        h.location = (rnd.uniform(-1.2, 1.2), rnd.uniform(0.4, 2.5), rnd.uniform(-0.3, 1.4))
        h.rotation_euler = (math.radians(rnd.uniform(-60, 60)), math.radians(rnd.uniform(-30, 30)), math.radians(rnd.uniform(0, 360)))
    # profundidad: troncos a distintas distancias (desenfocados), follaje bajo la rama y hojas en primer plano
    corteza = mat_corteza()
    for k, (x, y, r) in enumerate([(-0.60, 1.5, 0.07), (0.55, 1.9, 0.10), (-0.10, 2.6, 0.13), (1.05, 2.7, 0.14), (-1.20, 2.2, 0.11)]):
        tr = P.prim("cyl", f"Tronco{k}", coll, corteza, r=r, r2=r * 0.85, h=4.0, seg=24)
        tr.location = (x, y, 0.8)
        tr.rotation_euler = (math.radians(rnd.uniform(-4, 4)), math.radians(rnd.uniform(-5, 5)), 0)
    for k in range(40):
        h = hoja(f"FondoBajo{k}", coll, rnd.uniform(0.12, 0.30), rnd.uniform(0.07, 0.14), rnd.choice([verde, verde2]))
        h.location = (rnd.uniform(-1.0, 1.0), rnd.uniform(0.25, 1.6), rnd.uniform(-0.9, 0.05))
        h.rotation_euler = (math.radians(rnd.uniform(-60, 60)), math.radians(rnd.uniform(-30, 30)), math.radians(rnd.uniform(0, 360)))
    for k in range(5):
        h = hoja(f"Frente{k}", coll, rnd.uniform(0.10, 0.16), rnd.uniform(0.06, 0.09), verde2)
        h.location = (rnd.choice([-0.30, -0.22, 0.30, 0.36, 0.26]), rnd.uniform(-0.30, -0.22), rnd.uniform(-0.05, 0.50))
        h.rotation_euler = (math.radians(rnd.uniform(-70, 70)), math.radians(rnd.uniform(-30, 30)), math.radians(rnd.uniform(0, 360)))
    fondo = P.prim("cube", "FondoNiebla", coll, P.mat("Niebla", (0.16, 0.42, 0.24), rough=1.0, emit=0.25), smooth=False)
    fondo.scale = (8, 0.05, 6)
    fondo.location = (0, 3.0, 0.5)
    return {"rama": rama, "espigas": espigas}


def cielo_bosque(sc):
    w = sc.world
    nt = w.node_tree
    bg = nt.nodes["Background"]
    bg.inputs["Color"].default_value = (0.16, 0.36, 0.24, 1)
    bg.inputs["Strength"].default_value = 0.8
    L = bpy.data.lights.new("SolBosque", "SUN")
    L.energy, L.color, L.angle = 1.4, (1.0, 0.90, 0.70), math.radians(4)
    ob = bpy.data.objects.new("SolBosque", L)
    sc.collection.objects.link(ob)
    ob.rotation_euler = (math.radians(40), math.radians(-25), math.radians(-30))
