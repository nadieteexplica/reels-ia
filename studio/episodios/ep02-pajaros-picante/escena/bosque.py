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
    tope = P.prim("sphere", name + "_tope", coll, m, r=r * 0.98)        # arriba también redondeada
    tope.location = pts[0]
    tope.parent = t
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


# =====================================================================================================
# v2 (20-oct, rediseño pedido por Tomás): bosque húmedo en capas, con luz cálida filtrada entre las hojas,
# niebla con rayos de luz, musgo de verdad, helechos y hojas con grosor. Ninguna hoja flota: todas cuelgan
# de una ramita, una liana o un helecho que sale de cuadro.
# =====================================================================================================
def mat_corteza2():
    m = bpy.data.materials.get("Corteza2")
    if m:
        return m
    m = P.mat("Corteza2", (0.10, 0.065, 0.04), rough=0.9)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0, 1.0, 0.25)          # grietas alargadas a lo largo del tronco
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.feature = "DISTANCE_TO_EDGE"
    vor.inputs["Scale"].default_value = 30.0
    nt.links.new(mp.outputs["Vector"], vor.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 12.0
    nz.inputs["Detail"].default_value = 8.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position, cr.elements[0].color = 0.35, (0.055, 0.035, 0.02, 1)
    cr.elements[1].position, cr.elements[1].color = 0.75, (0.20, 0.15, 0.09, 1)
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    # líquenes verde grisáceo en manchas
    nz2 = nt.nodes.new("ShaderNodeTexNoise")
    nz2.inputs["Scale"].default_value = 5.0
    nz2.inputs["Detail"].default_value = 4.0
    nt.links.new(tc.outputs["Object"], nz2.inputs["Vector"])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.55
    mr.inputs["From Max"].default_value = 0.62
    nt.links.new(nz2.outputs["Fac"], mr.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["B"].default_value = (0.20, 0.30, 0.10, 1)
    nt.links.new(ramp.outputs["Color"], mix.inputs["A"])
    nt.links.new(mr.outputs["Result"], mix.inputs["Factor"])
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    nt.links.new(vor.outputs["Distance"], add.inputs[0])
    nt.links.new(nz.outputs["Fac"], add.inputs[1])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.9
    bump.inputs["Distance"].default_value = 0.004
    nt.links.new(add.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def mat_musgo():
    m = bpy.data.materials.get("Musgo")
    if m:
        return m
    m = P.mat("Musgo", (0.12, 0.30, 0.04), rough=0.95, sss=0.0)   # sin SSS: en la sombra se veía una mancha naranja (óxido)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Sheen Weight"].default_value = 0.5
    b.inputs["Sheen Tint"].default_value = (0.75, 0.95, 0.45, 1)
    b.inputs["Sheen Roughness"].default_value = 0.3
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 300.0
    nz.inputs["Detail"].default_value = 6.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.03, 0.12, 0.01, 1)
    ramp.color_ramp.elements[1].color = (0.24, 0.48, 0.04, 1)
    nz_g = nt.nodes.new("ShaderNodeTexNoise")
    nz_g.inputs["Scale"].default_value = 25.0
    nt.links.new(tc.outputs["Object"], nz_g.inputs["Vector"])
    mezc = nt.nodes.new("ShaderNodeMath")
    mezc.operation = "MULTIPLY"
    nt.links.new(nz.outputs["Fac"], mezc.inputs[0])
    nt.links.new(nz_g.outputs["Fac"], mezc.inputs[1])
    mr_g = nt.nodes.new("ShaderNodeMapRange")
    mr_g.inputs["From Min"].default_value = 0.1
    mr_g.inputs["From Max"].default_value = 0.45
    nt.links.new(mezc.outputs[0], mr_g.inputs["Value"])
    nt.links.new(mr_g.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 1.0
    bump.inputs["Distance"].default_value = 0.003
    nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def mat_hoja2(nombre, col, col2):
    """Hoja con grosor, nervadura y luz que la atraviesa (translúcida al contraluz)."""
    m = bpy.data.materials.get(nombre)
    if m:
        return m
    m = P.mat(nombre, col, rough=0.42, sss=0.0, coat=0.25)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Transmission Weight"].default_value = 0.0
    b.inputs["Subsurface Weight"].default_value = 0.35
    b.inputs["Subsurface Radius"].default_value = (0.6, 1.0, 0.3)
    b.inputs["Subsurface Scale"].default_value = 0.004
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["UV"], sep.inputs[0])
    # nervadura: vena central (u≈0.5) y venas laterales en ángulo
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.inputs["Scale"].default_value = 7.0
    wave.inputs["Distortion"].default_value = 0.5
    nt.links.new(tc.outputs["UV"], wave.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 8.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*col, 1)
    mix.inputs["B"].default_value = (*col2, 1)
    nt.links.new(nz.outputs["Fac"], mix.inputs["Factor"])
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.25
    bump.inputs["Distance"].default_value = 0.0008
    nt.links.new(wave.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def hoja2(name, coll, L, W, m, curva=0.25, torsion=0.0, grosor=0.0012):
    """Hoja lanceolada con grosor (solidify), curvatura a lo largo y doblez en V por la vena central. Origen = pecíolo; crece hacia +Y."""
    bm = bmesh.new()
    n, k = 14, 4
    uv_l = bm.loops.layers.uv.new()
    filas = []
    for i in range(n + 1):
        t = i / n
        w = W * (math.sin(math.pi * min(1, t * 1.08)) ** 0.75) * (1 - 0.25 * t) + 1e-4
        fila = []
        for j in range(-k, k + 1):
            u = j / k
            x = u * w / 2
            z = -curva * L * t * t + abs(u) * w * 0.18 + torsion * u * t * w
            fila.append(bm.verts.new((x, t * L, z)))
        filas.append(fila)
    for i in range(n):
        for j in range(2 * k):
            f = bm.faces.new((filas[i][j], filas[i][j + 1], filas[i + 1][j + 1], filas[i + 1][j]))
            for lp in f.loops:
                lp[uv_l].uv = ((lp.vert.co.x / max(W, 1e-4)) + 0.5, lp.vert.co.y / L)
    ob = P.mesh_obj(name, bm, coll, m=m)
    s = ob.modifiers.new("Grosor", "SOLIDIFY")
    s.thickness = grosor
    s.offset = 0
    sub = ob.modifiers.new("Sub", "SUBSURF")
    sub.levels = sub.render_levels = 1
    return ob


def ramita_con_hojas(name, coll, puntos, n_hojas, m_hoja, m_tallo, rnd, L=(0.08, 0.14), W=(0.035, 0.06), radio=0.004):
    """Ramita (o liana) por los puntos dados, con hojas pegadas a lo largo (alternas). Devuelve la lista de objetos."""
    tallo = P.tube(name, puntos, radio, coll, m_tallo, res=12)
    pts = [Vector(p) for p in puntos]
    out = [tallo]
    for i in range(n_hojas):
        t = (i + 0.5) / n_hojas
        seg = min(int(t * (len(pts) - 1)), len(pts) - 2)
        u = t * (len(pts) - 1) - seg
        p = pts[seg].lerp(pts[seg + 1], u)
        d = (pts[seg + 1] - pts[seg]).normalized()
        lado = 1 if i % 2 == 0 else -1
        h = hoja2(f"{name}_h{i}", coll, rnd.uniform(*L), rnd.uniform(*W), m_hoja, curva=rnd.uniform(0.15, 0.4), torsion=rnd.uniform(-0.3, 0.3))
        h.location = p
        perp = d.cross(Vector((0, 1, 0)))
        if perp.length < 1e-3:
            perp = d.cross(Vector((1, 0, 0)))
        perp = perp.normalized() * lado
        dir_h = (perp * 0.8 + d * 0.4 + Vector((0, 0, -0.35))).normalized()
        h.rotation_euler = dir_h.to_track_quat("Y", "Z").to_euler()
        h.rotation_euler.rotate_axis("Y", math.radians(rnd.uniform(-40, 40)))
        out.append(h)
    return out


def helecho(name, coll, base, direccion, largo, m, rnd, pinnas=16):
    """Fronda de helecho: raquis curvo con pinnas (hojitas) a ambos lados que se achican hacia la punta. Una sola malla."""
    bm = bmesh.new()
    d = Vector(direccion).normalized()
    lado = d.cross(Vector((0, 0, 1)))
    if lado.length < 1e-3:
        lado = Vector((1, 0, 0))
    lado.normalize()
    arriba = lado.cross(d).normalized()
    def eje(t):
        return Vector(base) + d * largo * t - arriba * largo * 0.35 * t * t
    for i in range(1, pinnas + 1):
        t = i / (pinnas + 1)
        p = eje(t)
        tang = (eje(min(1, t + 0.01)) - eje(max(0, t - 0.01))).normalized()
        Lp = largo * 0.22 * (1 - t) ** 0.8 + largo * 0.02
        Wp = Lp * 0.28
        for s in (-1, 1):
            dirp = (lado * s * 0.9 + tang * 0.45).normalized()
            n = 6
            izq, der = [], []
            for j in range(n + 1):
                u = j / n
                c = p + dirp * Lp * u - arriba * Lp * 0.15 * u * u
                w = Wp * math.sin(math.pi * min(1, u * 1.1)) ** 0.7 + 1e-4
                izq.append(bm.verts.new(c + tang * w / 2))
                der.append(bm.verts.new(c - tang * w / 2))
            for j in range(n):
                bm.faces.new((izq[j], izq[j + 1], der[j + 1], der[j]))
    ob = P.mesh_obj(name, bm, coll, m=m)
    sol = ob.modifiers.new("Grosor", "SOLIDIFY")
    sol.thickness = 0.0008
    raquis = P.tube(name + "_raquis", [tuple(eje(t)) for t in (0, 0.33, 0.66, 1.0)], largo * 0.008, coll,
                    bpy.data.materials.get("TalloOscuro") or P.mat("TalloOscuro", (0.05, 0.10, 0.03), rough=0.6), res=8)
    return [ob, raquis]


def musgo_en_rama(name, coll, rama_pts, radio, rnd, n=140, excluir=None):
    """Matas de musgo sobre la cara de arriba de la rama (esferas aplastadas, hundidas en la corteza)."""
    pts = [Vector(p) for p in rama_pts]
    m = mat_musgo()
    out = []
    for i in range(n):
        t = rnd.random()
        seg = min(int(t * (len(pts) - 1)), len(pts) - 2)
        u = t * (len(pts) - 1) - seg
        c = pts[seg].lerp(pts[seg + 1], u)
        if excluir and excluir[0] < c.x < excluir[1]:
            continue
        ang = rnd.uniform(-1.1, 1.1)                       # alrededor de la cara de arriba
        off = Vector((0, math.sin(ang), math.cos(ang))) * radio * 0.92
        r = rnd.uniform(0.005, 0.013)
        b = P.prim("ico", f"{name}{i}", coll, m, r=r, sub=2)
        b.location = c + off
        b.scale = (rnd.uniform(1.0, 2.2), rnd.uniform(0.9, 1.6), rnd.uniform(0.35, 0.6))
        b.rotation_euler = (ang * 0.9, 0, rnd.uniform(0, math.pi))
        out.append(b)
    return out


def capa_musgo(name, coll, pts, radio):
    """Capa de musgo sobre la cara de arriba de una rama: tubo apenas más grueso que sólo se ve donde la normal mira hacia
    arriba, con borde irregular y relieve de musgo (se ve como un manto, no como bolitas)."""
    m = bpy.data.materials.get("MantoMusgo")
    if not m:
        base = mat_musgo()
        m = base.copy()
        m.name = "MantoMusgo"
        nt = m.node_tree
        out = nt.nodes["Material Output"]
        b = nt.nodes["Principled BSDF"]
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(geo.outputs["Normal"], sep.inputs[0])
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 18.0
        nz.inputs["Detail"].default_value = 5.0
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        add = nt.nodes.new("ShaderNodeMath")
        add.operation = "MULTIPLY_ADD"
        add.inputs[1].default_value = 1.3
        nt.links.new(nz.outputs["Fac"], add.inputs[0])
        nt.links.new(sep.outputs["Z"], add.inputs[2])
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = 1.15
        mr.inputs["From Max"].default_value = 1.19
        nt.links.new(add.outputs[0], mr.inputs["Value"])
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mx = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(mr.outputs["Result"], mx.inputs["Fac"])
        nt.links.new(tr.outputs[0], mx.inputs[1])
        nt.links.new(b.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs["Surface"])
    t = P.tube(name, pts, radio * 1.07, coll, m, res=24)
    return t


def armar_v2(coll, seed=11):
    rnd = random.Random(seed)
    corteza = mat_corteza2()
    tallo_m = P.mat("TalloOscuro", (0.05, 0.10, 0.03), rough=0.6)
    h_osc = mat_hoja2("HojaOscura", (0.025, 0.11, 0.025), (0.04, 0.16, 0.03))
    h_med = mat_hoja2("HojaMedia", (0.05, 0.22, 0.04), (0.10, 0.30, 0.05))
    h_cla = mat_hoja2("HojaClara", (0.14, 0.38, 0.06), (0.22, 0.45, 0.08))
    h_piper = mat_hoja2("HojaPiper2", (0.05, 0.25, 0.04), (0.08, 0.32, 0.05))
    # --- rama principal (misma curva que v1: la tupaya se apoya con un rayo) ---
    RAMA = [(-0.9, 0.05, 0.08), (-0.3, 0.02, 0.12), (0.2, 0.0, 0.10), (0.7, 0.05, 0.16)]
    rama = P.tube("Rama", RAMA, 0.035, coll, corteza, res=24)
    capa_musgo("MantoRama", coll, RAMA, 0.035)
    # (sin matas sueltas en la rama principal: de cerca se veían como huevos verdes; el manto basta)
    # ramita que sale de la rama principal hacia atrás-arriba, con hojas
    ramita_con_hojas("RamitaA", coll, [(0.35, 0.03, 0.13), (0.42, 0.12, 0.25), (0.50, 0.22, 0.42)], 7, h_med, tallo_m, rnd)
    # --- Piper (pimienta picante): rama con nudos en zigzag; en cada nudo una hoja ovalada con nervaduras y, del lado
    #     opuesto, la espiga colgando de un pedúnculo corto. Las espigas quedan junto al hocico, como en v1 ---
    espigas = []
    POS_ESP = [(0.085, -0.03, 0.33), (0.125, 0.0, 0.36), (0.045, 0.02, 0.38)]
    tallo_p = P.mat("TalloPiper", (0.07, 0.20, 0.05), rough=0.5)
    nudo_m = P.mat("NudoPiper", (0.10, 0.17, 0.05), rough=0.6)
    h_piper = mat_hoja2("HojaPiper2", (0.05, 0.25, 0.04), (0.08, 0.32, 0.05))
    orden = sorted(range(3), key=lambda k: -POS_ESP[k][2])          # de arriba hacia abajo
    nudos = [Vector(POS_ESP[k]) + Vector((0.0, 0.0, 0.035)) for k in orden]
    tope = Vector((0.22, 0.06, 0.95))
    camino = [tope, Vector((0.14, 0.04, 0.62))] + nudos + [nudos[-1] + Vector((-0.03, -0.01, -0.05))]
    P.tube("TalloPiperMadre", [tuple(p) for p in camino], 0.0042, coll, tallo_p, res=12)
    for n_i, (k, nd) in enumerate(zip(orden, nudos)):
        anillo = P.prim("sphere", f"NudoPiper{k}", coll, nudo_m, r=0.0062)
        anillo.scale = (1, 1, 0.7)
        anillo.location = nd
        # espiga con pedúnculo corto (2 cm), colgando
        x, y, z = POS_ESP[k]
        P.tube(f"Peduncolo{k}", [tuple(nd), tuple(nd + Vector((0.004, 0, -0.016))), (x, y, z)], 0.0020, coll, tallo_p, res=8)
        e = espiga(f"Espiga{k}", coll, largo=rnd.uniform(0.08, 0.11), seed=k)
        _b = e.data.materials[0].node_tree.nodes["Principled BSDF"]
        _b.inputs["Base Color"].default_value = (0.45, 0.55, 0.10, 1)
        _b.inputs["Subsurface Weight"].default_value = 0.0      # con SSS se veían rosadas a contraluz
        e.location = (x, y, z)
        espigas.append(e)
        # hoja ovalada al lado opuesto, apuntando hacia afuera y arriba (no tapa el hocico de la tupaya)
        lado = 1 if n_i % 2 == 0 else -1
        h = hoja2(f"HojaPiperN{k}", coll, 0.115, 0.075, h_piper, curva=0.22, torsion=0.1, grosor=0.0014)
        h.location = nd
        dir_h = Vector((0.55 * lado + 0.35, 0.35, 0.55)).normalized()
        h.rotation_euler = dir_h.to_track_quat("Y", "Z").to_euler()
    # dos hojas más en el tramo de arriba de la rama
    for q, (pa, pb) in enumerate(((camino[0], camino[1]), (camino[1], camino[2]))):
        h = hoja2(f"HojaPiperA{q}", coll, 0.12, 0.08, h_piper, curva=0.25, grosor=0.0014)
        h.location = pa.lerp(pb, 0.6)
        h.rotation_euler = Vector((0.6 if q else -0.4, 0.3, 0.45)).normalized().to_track_quat("Y", "Z").to_euler()
    # --- primer plano: dos ramitas que entran desde los bordes, con hojas oscuras desenfocadas ---
    ramita_con_hojas("FrenteIzq", coll, [(-0.55, -0.30, 0.55), (-0.32, -0.26, 0.42), (-0.20, -0.24, 0.30)], 5, h_osc, tallo_m, rnd,
                     L=(0.12, 0.18), W=(0.06, 0.09), radio=0.006)
    ramita_con_hojas("FrenteDer", coll, [(0.60, -0.28, -0.20), (0.36, -0.24, -0.06), (0.24, -0.22, 0.02)], 4, h_osc, tallo_m, rnd,
                     L=(0.12, 0.18), W=(0.06, 0.09), radio=0.006)
    # --- plano medio: helechos que suben desde abajo y lianas que bajan desde arriba ---
    m_hel = mat_hoja2("Helecho", (0.05, 0.30, 0.03), (0.14, 0.45, 0.04))
    for k in range(9):
        bx, by = rnd.uniform(-0.9, 0.9), rnd.uniform(0.35, 1.1)
        for j in range(3):
            a = rnd.uniform(0, 2 * math.pi)
            helecho(f"Helecho{k}_{j}", coll, (bx, by, -0.6), (math.cos(a) * 0.5, math.sin(a) * 0.5, 1.0), rnd.uniform(0.45, 0.75), m_hel, rnd)
    for k in range(5):
        x, y = rnd.uniform(-0.9, 0.9), rnd.uniform(0.5, 1.4)
        pts = [(x, y, 1.6), (x + rnd.uniform(-0.05, 0.05), y, 1.1), (x + rnd.uniform(-0.08, 0.08), y + 0.02, 0.6), (x + rnd.uniform(-0.1, 0.1), y, 0.25)]
        ramita_con_hojas(f"Liana{k}", coll, pts, 9, rnd.choice([h_med, h_cla]), tallo_m, rnd, L=(0.07, 0.11), W=(0.035, 0.05), radio=0.005)
    # --- fondo: troncos con corteza a distintas distancias (la niebla los aclara) y otra rama musgosa ---
    for k, (x, y, r) in enumerate([(-0.55, 1.4, 0.08), (0.65, 1.8, 0.11), (-0.15, 2.5, 0.14), (1.10, 2.8, 0.15), (-1.25, 2.3, 0.12), (0.30, 3.4, 0.18)]):
        tr = P.prim("cyl", f"Tronco{k}", coll, corteza, r=r, r2=r * 0.85, h=4.5, seg=32)
        tr.location = (x, y, 1.0)
        tr.rotation_euler = (math.radians(rnd.uniform(-5, 5)), math.radians(rnd.uniform(-6, 6)), 0)
        musgo_en_rama(f"MusgoTronco{k}", coll, [(x, y, -0.6), (x, y, 0.6)], r, rnd, n=30)
    RAMA2 = [(-1.2, 1.0, 0.55), (-0.5, 0.95, 0.70), (0.2, 1.05, 0.62)]
    P.tube("Rama2", RAMA2, 0.03, coll, corteza, res=16)
    capa_musgo("MantoRama2", coll, RAMA2, 0.03)
    musgo_en_rama("MusgoRama2", coll, RAMA2, 0.03, rnd, n=60)
    # --- copa (no se ve en cámara): planos de hojas que filtran el sol en manchas ---
    copa_m = bpy.data.materials.new("CopaFiltro")
    copa_m.use_nodes = True
    nt = copa_m.node_tree
    out = nt.nodes["Material Output"]
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.02, 0.08, 0.02, 1)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 6.0
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.26
    mr.inputs["From Max"].default_value = 0.30
    nt.links.new(vor.outputs["Distance"], mr.inputs["Value"])
    tr_ = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mr.outputs["Result"], mx.inputs["Fac"])
    nt.links.new(tr_.outputs[0], mx.inputs[1])
    nt.links.new(bsdf.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    copa = P.prim("cube", "Copa", coll, copa_m, smooth=False)
    copa.scale = (6, 6, 0.01)
    copa.location = (0, 0.6, 2.2)
    copa.visible_camera = False
    copa.visible_glossy = False
    # --- niebla con rayos de luz ---
    vol = bpy.data.materials.new("NieblaBosque")
    vol.use_nodes = True
    nt = vol.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    pv = nt.nodes.new("ShaderNodeVolumePrincipled")
    pv.inputs["Color"].default_value = (0.90, 0.92, 0.75, 1)
    pv.inputs["Density"].default_value = float(__import__("os").environ.get("NIEBLA", 0.032))
    pv.inputs["Anisotropy"].default_value = 0.55
    nt.links.new(pv.outputs[0], nt.nodes["Material Output"].inputs["Volume"])
    caja = P.prim("cube", "CajaNiebla", coll, vol, smooth=False)
    caja.scale = (4.0, 4.4, 3.0)       # la niebla también pasa por delante: ahí se ven los rayos de sol (sin ella el fondo se ve negro)
    caja.location = (0, 1.6, 0.6)
    return {"rama": rama, "espigas": espigas}


def luz_bosque(sc, fondo=(0.02, 0.065, 0.03)):
    """Mundo verde oscuro y sol cálido bajo, desde atrás a la izquierda (contraluz entre las hojas)."""
    w = sc.world
    nt = w.node_tree
    bg = nt.nodes["Background"]
    bg.inputs["Color"].default_value = (*fondo, 1)
    bg.inputs["Strength"].default_value = float(__import__("os").environ.get("AMBIENTE", 1.5))
    L = bpy.data.lights.new("SolBosque", "SUN")
    L.energy, L.color, L.angle = float(__import__("os").environ.get("SOL", 11.0)), (1.0, 0.80, 0.52), math.radians(1.0)
    ob = bpy.data.objects.new("SolBosque", L)
    sc.collection.objects.link(ob)
    # desde arriba, a la izquierda y detrás de la tupaya (los rayos vienen hacia la cámara)
    d = Vector((0.45, -0.55, -0.70)).normalized()
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return ob
