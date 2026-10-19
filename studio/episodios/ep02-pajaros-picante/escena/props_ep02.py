"""Utilería y set del Ep. 2 (pájaros y picante). Todo procedural, sin assets externos (salvo los animales, que se importan aparte)."""
import math, random
import bmesh
import bpy
from mathutils import Vector, Matrix, noise

import props as P

ROJO_AJI = (0.62, 0.012, 0.008)
VERDE_TALLO = (0.10, 0.26, 0.05)


def mat_aji():
    m = bpy.data.materials.get("Aji")
    if m:
        return m
    m = P.mat("Aji", ROJO_AJI, rough=0.16, sss=0.25, coat=0.6)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Subsurface Radius"].default_value = (1.0, 0.15, 0.08)
    b.inputs["Coat Roughness"].default_value = 0.08
    # variación sutil de rojo (más oscuro en pliegues) para que no se vea plástico
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 18.0
    nz.inputs["Detail"].default_value = 4.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.38, 0.006, 0.004, 1)
    ramp.color_ramp.elements[1].color = (0.75, 0.025, 0.012, 1)
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.08
    nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def aji(name="Aji", largo=0.12, grosor=0.016, curva=0.35, coll=None, seed=0):
    """Ají tipo cacho de cabra: cuerno curvo y brillante con cáliz y tallo verdes.
    Origen = base del tallo; el ají se extiende hacia -Z local (cuelga) y se curva hacia +X."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    n_l, n_c = 28, 20
    rings = []
    for i in range(n_l + 1):
        t = i / n_l
        # eje curvo
        ang = curva * t * t * math.pi / 2
        c = Vector((math.sin(ang) * largo * 0.55 * t, 0, -largo * t * (1 - 0.18 * t)))
        tang = Vector((math.cos(ang) * 0.35 * curva + 1e-3, 0, -1)).normalized()
        # perfil: hombro redondo arriba, punta fina abajo
        r = grosor * (math.sin(min(1.0, t * 6) * math.pi / 2) * (1 - t) ** 0.85 + 0.04 * (1 - t))
        if i == n_l:
            r = 0.0004
        side = tang.cross(Vector((0, 1, 0))).normalized()
        up = side.cross(tang).normalized()
        ring = []
        for j in range(n_c):
            a = 2 * math.pi * j / n_c
            lobe = 1 + 0.06 * math.cos(3 * a + seed) + 0.025 * noise.noise(Vector((t * 6, a, seed)))
            ring.append(bm.verts.new(c + (side * math.cos(a) + up * math.sin(a)) * r * lobe))
        rings.append(ring)
    for i in range(n_l):
        for j in range(n_c):
            bm.faces.new((rings[i][j], rings[i][(j + 1) % n_c], rings[i + 1][(j + 1) % n_c], rings[i + 1][j]))
    top = bm.faces.new(list(reversed(rings[0])))
    bmesh.ops.remove_doubles(bm, verts=rings[-1], dist=0.0006)
    ob = P.mesh_obj(name, bm, coll, m=mat_aji())
    sub = ob.modifiers.new("Sub", "SUBSURF")
    sub.levels = sub.render_levels = 1
    # cáliz y tallo
    mv = P.mat("TalloAji", VERDE_TALLO, rough=0.45, sss=0.1)
    cal = P.prim("cyl", name + "_caliz", coll, mv, r=grosor * 1.05, r2=grosor * 0.55, h=grosor * 0.55, seg=20)
    cal.location = (0, 0, grosor * 0.1)
    cal.parent = ob
    tallo = P.tube(name + "_tallo", [(0, 0, 0), (0.002, 0, grosor * 0.9), (-0.004 + rnd.uniform(-.003, .003), 0, grosor * 1.9),
                                      (-0.009, 0, grosor * 2.6)], grosor * 0.17, coll, mv)
    tallo.parent = ob
    return ob


def vaso_leche(name="VasoLeche", coll=None, alto=0.13, r=0.034, nivel=0.8):
    """Vaso de vidrio con leche. Origen = base del vaso."""
    vidrio = P.mat("Vidrio", (0.95, 0.97, 1.0), rough=0.02, transmission=1.0)
    vidrio.node_tree.nodes["Principled BSDF"].inputs["IOR"].default_value = 1.45
    leche = P.mat("Leche", (0.93, 0.92, 0.88), rough=0.25, sss=0.6)
    leche.node_tree.nodes["Principled BSDF"].inputs["Subsurface Radius"].default_value = (1.0, 0.9, 0.7)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=r * 0.88, radius2=r, depth=alto)
    v = P.mesh_obj(name, bm, coll, m=vidrio)
    for vv in v.data.vertices:
        vv.co.z += alto / 2
    sol = v.modifiers.new("Grosor", "SOLIDIFY")
    sol.thickness = 0.0025
    P.bevel(v, 0.0012, 2)
    bm = bmesh.new()
    h = alto * nivel
    bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=r * 0.88 - 0.003, radius2=r * (0.88 + 0.12 * nivel) - 0.003, depth=h - 0.004)
    l = P.mesh_obj(name + "_leche", bm, coll, m=leche)
    for vv in l.data.vertices:
        vv.co.z += (h - 0.004) / 2 + 0.004
    l.parent = v
    return v


def mat_pared(color=(0.13, 0.48, 0.78)):
    m = bpy.data.materials.get("ParedCeleste")
    if m:
        return m
    m = P.mat("ParedCeleste", color, rough=0.85)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 60.0
    nz.inputs["Detail"].default_value = 8.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.05
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def mat_madera(name="MaderaClara", c1=(0.55, 0.33, 0.16), c2=(0.36, 0.19, 0.08)):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = P.mat(name, c1, rough=0.45, coat=0.25)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, 14.0, 1.0)
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.inputs["Scale"].default_value = 3.0
    wave.inputs["Distortion"].default_value = 6.0
    wave.inputs["Detail"].default_value = 3.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*c2, 1)
    ramp.color_ramp.elements[1].color = (*c1, 1)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], wave.inputs["Vector"])
    nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    return m


def plato(name="Plato", r=0.075, coll=None):
    m = P.mat("Ceramica", (0.92, 0.90, 0.86), rough=0.18, coat=0.5)
    bm = bmesh.new()
    prof = [(0.0, 0.0), (r * 0.62, 0.0), (r * 0.72, 0.004), (r * 0.98, 0.012), (r, 0.014)]
    segs = 64
    rings = []
    for (rr, z) in prof:
        rings.append([bm.verts.new((rr * math.cos(2 * math.pi * k / segs), rr * math.sin(2 * math.pi * k / segs), z)) for k in range(segs)])
    for i in range(len(rings) - 1):
        for k in range(segs):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % segs], rings[i + 1][(k + 1) % segs], rings[i + 1][k]))
    ob = P.mesh_obj(name, bm, coll, m=m)
    s = ob.modifiers.new("Grosor", "SOLIDIFY")
    s.thickness = 0.004
    sub = ob.modifiers.new("Sub", "SUBSURF")
    sub.levels = sub.render_levels = 2
    return ob


def maceta_aji(name="MacetaAji", coll=None, seed=3):
    """Maceta de greda con una mata de ají: hojas verdes y 5 ajíes rojos colgando. Origen = base de la maceta."""
    rnd = random.Random(seed)
    root = P.empty(name, coll=coll)
    greda = P.mat("Greda", (0.55, 0.20, 0.09), rough=0.75)
    pot = P.prim("cyl", name + "_maceta", coll, greda, r=0.07, r2=0.09, h=0.14, seg=40)
    pot.location = (0, 0, 0.07)
    pot.parent = root
    P.bevel(pot, 0.006, 2)
    tierra = P.prim("cyl", name + "_tierra", coll, P.mat("Tierra", (0.09, 0.05, 0.03), rough=0.95), r=0.083, r2=0.083, h=0.01, seg=40)
    tierra.location = (0, 0, 0.13)
    tierra.parent = root
    hoja_m = P.mat("HojaAji", (0.06, 0.30, 0.06), rough=0.4, sss=0.2)
    tallo_m = P.mat("TalloAji", VERDE_TALLO, rough=0.45, sss=0.1)
    tallos = []
    for k in range(7):
        a = 2 * math.pi * k / 7 + rnd.uniform(-.3, .3)
        h = rnd.uniform(0.16, 0.26)
        p0 = Vector((0, 0, 0.13))
        p1 = Vector((math.cos(a) * 0.03, math.sin(a) * 0.03, 0.13 + h * 0.5))
        p2 = Vector((math.cos(a) * 0.08, math.sin(a) * 0.08, 0.13 + h))
        t = P.tube(f"{name}_tallo{k}", [p0, p1, p2], 0.0035, coll, tallo_m)
        t.parent = root
        tallos.append((p1, p2, a))
        for j in range(4):
            q = p1.lerp(p2, 0.25 + 0.25 * j) + Vector((rnd.uniform(-.01, .01), rnd.uniform(-.01, .01), 0))
            bm = bmesh.new()
            L, W = rnd.uniform(0.05, 0.075), rnd.uniform(0.018, 0.026)
            pts = [(0, 0), (L * 0.3, W * 0.5), (L * 0.7, W * 0.42), (L, 0), (L * 0.7, -W * 0.42), (L * 0.3, -W * 0.5)]
            vs = [bm.verts.new((x, y, 0.004 * math.sin(x / L * math.pi))) for x, y in pts]
            bm.faces.new(vs)
            hoja = P.mesh_obj(f"{name}_hoja{k}_{j}", bm, coll, m=hoja_m)
            hoja.location = q
            hoja.rotation_euler = (rnd.uniform(-.4, .4), rnd.uniform(-.6, -.1), a + rnd.uniform(-1.2, 1.2))
            hoja.parent = root
            s = hoja.modifiers.new("Sub", "SUBSURF")
            s.levels = s.render_levels = 2
    ajies = []
    for k, (p1, p2, a) in enumerate(tallos[:5]):
        aj = aji(f"{name}_aji{k}", largo=rnd.uniform(0.07, 0.10), grosor=rnd.uniform(0.010, 0.013), coll=coll, seed=k + seed)
        aj.location = p2 + Vector((0, 0, -0.01))
        aj.rotation_euler = (rnd.uniform(-.25, .25), rnd.uniform(-.25, .25), a)
        aj.parent = root
        ajies.append(aj)
    return root, ajies


def terraza(coll=None):
    """Terraza: pared celeste con zócalo, mesón de madera clara con frente menta. El mesón mide 1,02 m de alto (el personaje queda de pie detrás).
    Devuelve la altura de la cubierta del mesón."""
    pared = P.prim("cube", "Pared", coll, mat_pared(), smooth=False)
    pared.scale = (12.0, 0.1, 6.0)
    pared.location = (0, 1.2, 3.0)
    zocalo = P.prim("cube", "Zocalo", coll, P.mat("Zocalo", (0.94, 0.92, 0.86), rough=0.6), smooth=False)
    zocalo.scale = (12.0, 0.12, 0.9)
    zocalo.location = (0, 1.16, 0.45)
    piso = P.prim("cube", "Piso", coll, P.mat("Baldosa", (0.70, 0.36, 0.22), rough=0.7), smooth=False)
    piso.scale = (8, 8, 0.05)
    piso.location = (0, 0, -0.025)
    H = 1.02
    top = P.prim("cube", "Meson", coll, mat_madera(), smooth=False)
    top.scale = (1.8, 0.62, 0.05)
    top.location = (0, -0.42, H - 0.025)
    P.bevel(top, 0.008, 3)
    frente = P.prim("cube", "MesonFrente", coll, P.mat("Menta", (0.20, 0.66, 0.45), rough=0.55), smooth=False)
    frente.scale = (1.74, 0.56, H - 0.05)
    frente.location = (0, -0.42, (H - 0.05) / 2)
    P.bevel(frente, 0.01, 2)
    return H


def morder(aji_ob, centro_local, r=0.012):
    """Mordida en un ají: resta una esfera (forma fija) en coordenadas locales del ají."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=r)
    me = bpy.data.meshes.new(aji_ob.name + "_mordida")
    bm.to_mesh(me)
    bm.free()
    cort = bpy.data.objects.new(aji_ob.name + "_mordida", me)
    for c in aji_ob.users_collection:
        c.objects.link(cort)
    cort.parent = aji_ob
    cort.location = centro_local
    cort.hide_render = True
    cort.display_type = "WIRE"
    b = aji_ob.modifiers.new("Mordida", "BOOLEAN")
    b.operation = "DIFFERENCE"
    b.object = cort
    # la mordida deja ver el interior claro del ají
    blanco = P.mat("AjiInterior", (0.95, 0.85, 0.62), rough=0.6, sss=0.3)
    aji_ob.data.materials.append(blanco)
    b.material_mode = "TRANSFER"
    cort.data.materials.append(blanco)
    return cort
