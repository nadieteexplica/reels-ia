"""Set principal del Ep. 2: desierto de Sonora (Arizona) al atardecer, en escala de animalito.
Roca plana de arenisca donde viven las escenas, arena, matas, saguaros y mesetas a lo lejos; sol bajo y cálido + cielo.
Todo procedural. Unidades en metros (el pájaro mide ~0,2 m)."""
import math, random
import bmesh
import bpy
from mathutils import Vector, Matrix, Euler, noise

import props as P
import props_ep02 as E


def _nodo(nt, tipo, **kw):
    n = nt.nodes.new(tipo)
    for k, v in kw.items():
        n.inputs[k].default_value = v
    return n


def mat_arena():
    m = bpy.data.materials.get("Arena")
    if m:
        return m
    m = P.mat("Arena", (0.78, 0.46, 0.24), rough=0.9)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = _nodo(nt, "ShaderNodeTexNoise", Scale=900.0, Detail=4.0)
    nz2 = _nodo(nt, "ShaderNodeTexNoise", Scale=6.0, Detail=3.0)
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    nt.links.new(tc.outputs["Object"], nz2.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.60, 0.30, 0.13, 1)
    ramp.color_ramp.elements[1].color = (0.86, 0.55, 0.30, 1)
    nt.links.new(nz2.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    bump = _nodo(nt, "ShaderNodeBump", Strength=0.25, Distance=0.001)
    nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def mat_arenisca():
    """Arenisca rojiza con estratos (bandas) y grano."""
    m = bpy.data.materials.get("Arenisca")
    if m:
        return m
    m = P.mat("Arenisca", (0.55, 0.22, 0.10), rough=0.85)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    nzb = _nodo(nt, "ShaderNodeTexNoise", Scale=3.0, Detail=2.0)
    nt.links.new(tc.outputs["Object"], nzb.inputs["Vector"])
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "MULTIPLY_ADD"
    add.inputs[1].default_value = 0.04
    nt.links.new(nzb.outputs["Fac"], add.inputs[0])
    nt.links.new(sep.outputs["Z"], add.inputs[2])
    wave = _nodo(nt, "ShaderNodeTexWave", Scale=1.0, Distortion=2.0, Detail=2.0)
    wave.bands_direction = "Z"
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(add.outputs[0], comb.inputs["Z"])
    nt.links.new(comb.outputs[0], wave.inputs["Vector"])
    wave.inputs["Scale"].default_value = 9.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].color = (0.56, 0.22, 0.10, 1)
    cr.elements[1].color = (0.78, 0.40, 0.20, 1)
    e = cr.elements.new(0.5)
    e.color = (0.68, 0.30, 0.14, 1)
    nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    grano = _nodo(nt, "ShaderNodeTexNoise", Scale=300.0, Detail=6.0)
    nt.links.new(tc.outputs["Object"], grano.inputs["Vector"])
    bump = _nodo(nt, "ShaderNodeBump", Strength=0.35, Distance=0.002)
    nt.links.new(grano.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def roca(name, centro, tam, coll, seed=0, alto=None):
    """Roca de arenisca de cima plana (meseta en miniatura): caja biselada + desplazamiento de ruido; la cima queda casi plana."""
    rnd = random.Random(seed)
    sx, sy, sz = tam
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=bm.verts)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=min(sx, sy, sz) * 0.18, segments=4, affect="EDGES")
    bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=6, use_grid_fill=True)
    for v in bm.verts:
        k = 1.0 if v.co.z < sz * 0.42 else 0.15            # la cima casi no se deforma (ahí se paran los personajes)
        n = noise.noise(v.co * (3.0 / max(sx, sy)) + Vector((seed, 0, 0)))
        v.co += v.normal * n * min(sx, sy) * 0.10 * k
        v.co.z += noise.noise(v.co * 4.0 / max(sx, sy)) * sz * 0.08 if v.co.z > sz * 0.42 else 0
    ob = P.mesh_obj(name, bm, coll, m=mat_arenisca())
    sub = ob.modifiers.new("Sub", "SUBSURF")
    sub.levels = sub.render_levels = 1
    ob.location = (centro[0], centro[1], centro[2] + sz / 2)
    return ob


def saguaro(name, base, alto, coll, seed=0, brazos=2):
    """Saguaro: columna con costillas (sección de estrella) y brazos curvos."""
    rnd = random.Random(seed)
    verde = P.mat("Saguaro", (0.13, 0.30, 0.10), rough=0.55, sss=0.05)
    root = P.empty(name, loc=base, coll=coll)

    def columna(nm, pts, r):
        bm = bmesh.new()
        costillas, seg = 14, 28
        rings = []
        L = len(pts)
        for i, p in enumerate(pts):
            t = i / (L - 1)
            d = (Vector(pts[min(i + 1, L - 1)]) - Vector(pts[max(i - 1, 0)])).normalized()
            lado = d.orthogonal().normalized()
            arr = d.cross(lado)
            rr = r * (1.0 if t < 0.85 else math.cos((t - 0.85) / 0.15 * math.pi / 2) * 0.95 + 0.05)
            ring = []
            for j in range(seg):
                a = 2 * math.pi * j / seg
                rib = 1 + 0.10 * math.cos(costillas * a)
                ring.append(bm.verts.new(Vector(p) + (lado * math.cos(a) + arr * math.sin(a)) * rr * rib))
            rings.append(ring)
        for i in range(L - 1):
            for j in range(seg):
                bm.faces.new((rings[i][j], rings[i][(j + 1) % seg], rings[i + 1][(j + 1) % seg], rings[i + 1][j]))
        bm.faces.new(rings[-1])
        ob = P.mesh_obj(nm, bm, coll, m=verde)
        ob.parent = root
        s = ob.modifiers.new("Sub", "SUBSURF")
        s.levels = s.render_levels = 1
        return ob

    r = alto * 0.07
    n = 16
    columna(name + "_tronco", [(0, 0, alto * i / n) for i in range(n + 1)], r)
    for k in range(brazos):
        lado = 1 if k % 2 == 0 else -1
        h0 = alto * rnd.uniform(0.35, 0.55)
        ang = rnd.uniform(-0.6, 0.6) + (0 if lado > 0 else math.pi)
        dx, dy = math.cos(ang), math.sin(ang)
        sale = alto * rnd.uniform(0.16, 0.22)
        sube = alto * rnd.uniform(0.25, 0.38)
        pts = []
        for i in range(n + 1):
            t = i / n
            if t < 0.45:
                u = t / 0.45
                x = sale * math.sin(u * math.pi / 2)
                z = h0 + sale * (1 - math.cos(u * math.pi / 2)) * 0.6
            else:
                u = (t - 0.45) / 0.55
                x = sale
                z = h0 + sale * 0.6 + sube * u
            pts.append((dx * x, dy * x, z))
        columna(f"{name}_brazo{k}", pts, r * 0.75)
    return root


def mata(name, base, coll, alto=0.35, seed=0, frutos=24, fruto_r=0.006, hoja=(0.030, 0.012)):
    """Mata de chiltepín: ramitas finas, hojitas verdes y frutitos rojos casi redondos. Devuelve (raíz, frutos)."""
    rnd = random.Random(seed)
    root = P.empty(name, loc=base, coll=coll)
    tallo = P.mat("TalloChiltepin", (0.20, 0.17, 0.07), rough=0.7)
    hoja_m = P.mat("HojaChiltepin", (0.07, 0.24, 0.05), rough=0.45, sss=0.2)
    fruto_m = E.mat_aji()
    puntas = []
    for k in range(9):
        a = rnd.uniform(0, 2 * math.pi)
        incl = rnd.uniform(0.25, 0.75)
        L = alto * rnd.uniform(0.6, 1.0)
        p0 = Vector((0, 0, 0))
        p1 = Vector((math.cos(a) * L * incl * 0.4, math.sin(a) * L * incl * 0.4, L * 0.5))
        p2 = Vector((math.cos(a) * L * incl, math.sin(a) * L * incl, L))
        t = P.tube(f"{name}_rama{k}", [p0, p1, p2], alto * 0.012, coll, tallo)
        t.parent = root
        for j in range(8):
            q = p1.lerp(p2, j / 8) if j < 4 else p0.lerp(p1, 0.4 + 0.15 * (j - 4))
            q = q + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.5, 0.5))) * alto * 0.04
            bm = bmesh.new()
            Lh, Wh = hoja[0] * rnd.uniform(0.8, 1.2), hoja[1] * rnd.uniform(0.8, 1.2)
            pts = [(0, 0), (Lh * 0.3, Wh * 0.5), (Lh * 0.7, Wh * 0.4), (Lh, 0), (Lh * 0.7, -Wh * 0.4), (Lh * 0.3, -Wh * 0.5)]
            vs = [bm.verts.new((x, y, 0.15 * Wh * math.sin(x / Lh * math.pi))) for x, y in pts]
            bm.faces.new(vs)
            h = P.mesh_obj(f"{name}_hoja{k}_{j}", bm, coll, m=hoja_m)
            h.location = q
            h.rotation_euler = (rnd.uniform(-.5, .5), rnd.uniform(-.7, .1), rnd.uniform(0, 2 * math.pi))
            h.parent = root
            s = h.modifiers.new("Sub", "SUBSURF")
            s.levels = s.render_levels = 2
        puntas.append((p1, p2))
    fr = []
    for i in range(frutos):
        p1, p2 = puntas[i % len(puntas)]
        q = p1.lerp(p2, rnd.uniform(0.3, 1.0)) + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 0.3))) * alto * 0.05
        f = P.prim("sphere", f"{name}_fruto{i}", coll, fruto_m, r=fruto_r, u=24, v=12)
        f.scale = (1.0, 1.0, 1.25)
        f.location = q
        f.parent = root
        fr.append(f)
    return root, fr


def cielo(sc, sol_elev=11.0, sol_azim=-150.0, fuerza=3.2):
    """Cielo de atardecer: turquesa arriba, durazno en el horizonte, y un sol bajo y cálido (luz principal)."""
    w = sc.world
    nt = w.node_tree
    for n in list(nt.nodes):
        if n.type not in ("OUTPUT_WORLD",):
            nt.nodes.remove(n)
    bg = nt.nodes.new("ShaderNodeBackground")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.interpolation = "LINEAR"
    cr.elements[0].position = 0.0
    cr.elements[0].color = (0.40, 0.18, 0.08, 1)
    cr.elements[1].position = 0.80
    cr.elements[1].color = (0.02, 0.22, 0.48, 1)
    e = cr.elements.new(0.50)
    e.color = (1.00, 0.52, 0.25, 1)
    e = cr.elements.new(0.54)
    e.color = (0.85, 0.60, 0.45, 1)
    e = cr.elements.new(0.62)
    e.color = (0.12, 0.48, 0.66, 1)
    mr = nt.nodes.new("ShaderNodeMapRange")          # dirección del rayo: z de -1 (abajo) a 1 (cenit) → 0..1
    mr.inputs["From Min"].default_value = -1.0
    mr.inputs["From Max"].default_value = 1.0
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.9
    nt.links.new(bg.outputs[0], nt.nodes["World Output"].inputs["Surface"])
    L = bpy.data.lights.get("SolTarde") or bpy.data.lights.new("SolTarde", "SUN")
    L.energy, L.color, L.angle = fuerza, (1.0, 0.70, 0.42), math.radians(1.5)
    ob = bpy.data.objects.get("SolTarde") or bpy.data.objects.new("SolTarde", L)
    if ob.name not in sc.collection.objects:
        sc.collection.objects.link(ob)
    el, az = math.radians(sol_elev), math.radians(sol_azim)
    d = Vector((math.cos(el) * math.sin(az), -math.cos(el) * math.cos(az), math.sin(el)))   # dirección hacia el sol
    ob.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    return ob


def armar(coll, seed=7):
    """Arma el set. Devuelve dict con la roca principal (cima en z=ROCA_Z) y referencias."""
    rnd = random.Random(seed)
    piso = P.prim("cube", "Arena", coll, mat_arena(), smooth=False)
    piso.scale = (80, 80, 0.02)
    piso.location = (0, 0, -0.01)
    roca_p = roca("RocaPrincipal", (0, -0.45, 0), (1.8, 1.7, 0.24), coll, seed=1)
    top = 0.24
    # rocas y matas alrededor
    for i, (x, y, s) in enumerate([(-1.4, 1.6, 0.5), (1.6, 2.4, 0.8), (-2.8, 5.0, 1.4), (3.5, 7.0, 2.2), (-0.3, -1.6, 0.25)]):
        roca(f"Roca{i}", (x, y, 0), (s * 1.3, s, s * 0.6), coll, seed=10 + i)
    for i, (x, y, h) in enumerate([(-1.2, 4.0, 3.2), (2.2, 6.5, 4.5), (-4.5, 9.0, 5.5), (6.0, 14.0, 7.0), (-9.0, 18.0, 8.0), (11.0, 22.0, 9.0)]):
        saguaro(f"Saguaro{i}", (x, y, 0), h, coll, seed=20 + i, brazos=rnd.choice([1, 2, 2, 3]))
    for i, (x, y) in enumerate([(-0.9, 1.0), (0.9, 1.3), (-2.0, 2.6), (1.9, 3.6), (0.4, 2.2)]):
        mata(f"Matorral{i}", (x, y, 0), coll, alto=rnd.uniform(0.35, 0.6), seed=40 + i, frutos=0)
    # mesetas lejanas (más claras, como vistas a través del aire)
    lejos = P.mat("MesetaLejana", (0.70, 0.40, 0.30), rough=0.9)
    for i, (x, y, w, h) in enumerate([(-40, 120, 40, 12), (30, 140, 60, 16), (90, 170, 70, 20)]):
        m_ = roca(f"Meseta{i}", (x, y, 0), (w, w * 0.4, h), coll, seed=60 + i)
        m_.data.materials.clear()
        m_.data.materials.append(lejos)
    return {"roca": roca_p, "top": top}
