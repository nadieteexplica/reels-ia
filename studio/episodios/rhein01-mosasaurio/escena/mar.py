"""Escenario de Rhein 01: mar abierto de dibujo animado (cielo turquesa, olas, nubes), el bote del niño con la grúa
atornillada, el cable de ascensor, el gancho y el racimo de 200 pollos asados. Todo procedural y propio.

Escala en metros. El bote mira hacia -Y (proa); la grúa va atornillada en la popa y su pluma apunta hacia -Y y arriba.
"""
import math, os, random, sys
import bmesh
import bpy
from mathutils import Vector, Euler, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../plantilla")))
import props as P
from base_pj import blob, esfera, mat_simple, colgar, cuerno


# ---------------------------------------------------------------- cielo y luz
def cielo(sc, sol_energia=4.2, sol_dir=(-0.45, 0.55, 0.70)):
    w = sc.world
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 1.0
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = -0.05
    mr.inputs["From Max"].default_value = 0.40
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.30, 0.76, 0.93, 1)       # horizonte celeste claro
    ramp.color_ramp.elements[1].color = (0.07, 0.42, 0.78, 1)       # cenit turquesa-azul
    e = ramp.color_ramp.elements.new(0.35)
    e.color = (0.14, 0.58, 0.92, 1)
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    L = bpy.data.lights.new("Sol", "SUN")
    L.energy = sol_energia
    L.angle = math.radians(3)
    L.color = (1.0, 0.95, 0.86)
    sol = bpy.data.objects.new("Sol", L)
    sc.collection.objects.link(sol)
    sol.rotation_euler = Vector(sol_dir).to_track_quat("Z", "Y").to_euler()
    return sol


def nubes(coll, semilla=3, n=9, radio=140, alto=(18, 34)):
    r = random.Random(semilla)
    m = mat_simple("Nube", (1.0, 1.0, 1.0), rough=0.9, sss=0.0)
    obs = []
    for i in range(n):
        ang = r.uniform(-1.9, 1.9) - math.pi / 2           # nubes hacia adelante (-Y) y los lados
        c = Vector((radio * math.cos(ang), radio * math.sin(ang), r.uniform(*alto)))
        els = []
        for j in range(r.randint(4, 7)):
            els.append(((c.x + r.uniform(-9, 9), c.y + r.uniform(-3, 3), c.z + r.uniform(-1.5, 2.5)),
                        (r.uniform(4, 8), r.uniform(3, 5), r.uniform(2.5, 4.5)), (0, 0, r.uniform(0, 90))))
        ob = blob(f"Nube{i}", els, coll, voxel=0.9, suave=6)
        ob.data.materials.append(m)
        ob.visible_shadow = False
        obs.append(ob)
    return obs


# ---------------------------------------------------------------- mar
def mat_agua():
    m = bpy.data.materials.new("Agua")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.0, 0.42, 0.72, 1)
    b.inputs["Roughness"].default_value = 0.06
    b.inputs["Transmission Weight"].default_value = 0.6
    b.inputs["IOR"].default_value = 1.33
    # espuma en las crestas (capa de la modificación Ocean)
    at = nt.nodes.new("ShaderNodeAttribute")
    at.attribute_name = "espuma"
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.25
    mr.inputs["From Max"].default_value = 0.75
    nt.links.new(at.outputs["Fac"], mr.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMixShader")
    esp = nt.nodes.new("ShaderNodeBsdfPrincipled")
    esp.inputs["Base Color"].default_value = (0.92, 0.97, 1.0, 1)
    esp.inputs["Roughness"].default_value = 0.6
    out = nt.nodes["Material Output"]
    nt.links.new(mr.outputs["Result"], mix.inputs["Fac"])
    nt.links.new(b.outputs["BSDF"], mix.inputs[1])
    nt.links.new(esp.outputs["BSDF"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    return m


def mar(coll, tam=60.0, repetir=5, res=9, olas=0.55, z=0.0):
    me = bpy.data.meshes.new("Mar")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=2, y_segments=2, size=1.0)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("Mar", me)
    coll.objects.link(ob)
    ob.location.z = z
    oc = ob.modifiers.new("Olas", "OCEAN")
    oc.geometry_mode = "GENERATE"
    oc.resolution = res
    oc.viewport_resolution = 4
    oc.spatial_size = int(tam)
    oc.repeat_x = oc.repeat_y = repetir
    oc.wave_scale = olas
    oc.choppiness = 0.9
    oc.wind_velocity = 14.0
    oc.use_foam = True
    oc.foam_layer_name = "espuma"
    oc.foam_coverage = 0.25
    oc.random_seed = 7
    ob.location.x -= tam * repetir / 2
    ob.location.y -= tam * repetir / 2
    ob.data.materials.append(mat_agua())
    # fondo: azul profundo (lo que se ve bajo el agua)
    fondo = P.prim("cube", "FondoMar", coll, mat_simple("FondoMar", (0.0, 0.07, 0.16), rough=1.0))
    fondo.scale = (600, 600, 0.1)
    fondo.location = (0, 0, z - 9.0)
    return ob


def olas_t(mar_ob, t):
    mar_ob.modifiers["Olas"].time = 1.0 + t


# ---------------------------------------------------------------- bote
def bote(coll, nombre="Bote"):
    m_casco = mat_simple("Casco", (0.86, 0.09, 0.07), rough=0.35, coat=0.5)
    m_borde = mat_simple("BordeBote", (0.97, 0.95, 0.90), rough=0.4, coat=0.3)
    m_madera = mat_simple("MaderaBote", (0.55, 0.32, 0.15), rough=0.6)
    raiz = bpy.data.objects.new(nombre, None)
    coll.objects.link(raiz)
    L, B, H = 3.8, 1.55, 0.75
    bm = bmesh.new()
    nsec, nper = 28, 18
    secs = []
    for i in range(nsec + 1):
        u = i / nsec                       # 0 = proa (-Y), 1 = popa (+Y)
        y = -L / 2 + L * u
        ancho = B / 2 * (math.sin(math.pi * min(1.0, u * 1.35)) ** 0.7 if u < 0.74 else 0.92 + 0.08 * (1 - u) / 0.26)
        ancho = max(ancho, 0.02)
        borda = 0.40 + 0.28 * (1 - u) ** 3          # proa más alta
        quilla = -0.36 + 0.06 * (1 - u)
        ring = []
        for j in range(nper + 1):
            a = math.pi * j / nper                     # de borde izq. a borde der. pasando por la quilla
            x = -ancho * math.cos(a)
            z = borda - (borda - quilla) * (math.sin(a) ** 1.3)
            ring.append(bm.verts.new((x, y, z)))
        secs.append(ring)
    for i in range(nsec):
        for j in range(nper):
            bm.faces.new((secs[i][j], secs[i][j + 1], secs[i + 1][j + 1], secs[i + 1][j]))
    bm.faces.new(secs[-1][::-1])          # espejo de popa
    # borde (se toma antes de liberar la malla) blanco: tubo por el canto
    pts = []
    for i in range(nsec + 1):
        pts.append(secs[i][0].co.copy())
    for i in range(nsec, -1, -1):
        pts.append(secs[i][-1].co.copy())
    # volumen seco (para cortar el mar adentro del bote): casco achicado y cerrado por arriba
    seco_pts = []
    for ring in secs:
        for v in ring:
            seco_pts.append(Vector((v.co.x * 0.93, v.co.y * 0.985, v.co.z + 0.03)))
            seco_pts.append(Vector((v.co.x * 0.93, v.co.y * 0.985, v.co.z + 0.9)))
    bm_s = bmesh.new()
    vs = [bm_s.verts.new(p) for p in seco_pts]
    bmesh.ops.convex_hull(bm_s, input=vs)
    seco = P.mesh_obj(nombre + "_seco", bm_s, coll, smooth=False)
    seco.display_type = "WIRE"
    seco.hide_render = True
    seco.parent = raiz
    casco = P.mesh_obj(nombre + "_casco", bm, coll, m=m_casco)
    s = casco.modifiers.new("Grosor", "SOLIDIFY")
    s.thickness = 0.06
    sub = casco.modifiers.new("Sub", "SUBSURF")
    sub.levels = sub.render_levels = 2
    borde = P.tube(nombre + "_borde", pts, 0.055, coll, m=m_borde, res=10)
    # piso y banca de madera
    piso = P.prim("cube", nombre + "_piso", coll, m_madera)
    piso.scale = (B * 0.36, L * 0.38, 0.025)
    piso.location = (0, 0.15, -0.20)
    banca = P.prim("cube", nombre + "_banca", coll, m_madera)
    banca.scale = (B * 0.43, 0.16, 0.035)
    banca.location = (0, -0.45, 0.12)
    P.bevel(banca, 0.02)
    for o in (casco, borde, piso, banca):
        o.parent = raiz
    return raiz


# ---------------------------------------------------------------- grúa
def grua(coll, base=(0, 1.15, 0.0), angulo=48, largo=6.2, nombre="Grua"):
    """Torreta atornillada a la popa + pluma de reticulado amarilla. Devuelve (raíz, punta de la pluma en el mundo)."""
    m_am = mat_simple("Amarillo", (1.0, 0.74, 0.0), rough=0.35, coat=0.4)
    m_neg = mat_simple("NegroGrua", (0.03, 0.03, 0.035), rough=0.4, coat=0.3)
    m_acero = P.mat("Acero", (0.70, 0.71, 0.73), rough=0.25, metal=1.0)
    raiz = bpy.data.objects.new(nombre, None)
    coll.objects.link(raiz)
    raiz.location = base
    placa = P.prim("cyl", nombre + "_placa", coll, m_neg, r=0.42, r_top=0.42, h=0.06, seg=48)
    placa.location = (0, 0, 0.03)
    torre = P.prim("cyl", nombre + "_torre", coll, m_am, r=0.30, r_top=0.30, h=0.42, seg=48)
    torre.location = (0, 0, 0.27)
    P.bevel(torre, 0.03)
    pernos = []
    for k in range(10):
        a = 2 * math.pi * k / 10
        pb = P.prim("cyl", f"{nombre}_perno{k}", coll, m_acero, r=0.045, r_top=0.045, h=0.07, seg=6)
        pb.location = (0.36 * math.cos(a), 0.36 * math.sin(a), 0.08)
        pernos.append(pb)
    giro = bpy.data.objects.new(nombre + "_giro", None)      # pivote de la pluma (inclinación)
    coll.objects.link(giro)
    giro.location = (0, 0, 0.5)
    for o in [placa, torre] + pernos:
        o.parent = raiz
    giro.parent = raiz
    # pluma (en espacio del pivote: a lo largo de -Y)
    w = 0.30
    esquinas = [(-w / 2, -w / 2), (w / 2, -w / 2), (w / 2, w / 2), (-w / 2, w / 2)]
    barras = []
    for k, (x, z) in enumerate(esquinas):
        b = P.tube(f"{nombre}_larguero{k}", [(x, 0, z), (x * 0.6, -largo, z * 0.6)], 0.028, coll, m=m_am, res=8)
        barras.append(b)
    paso = 0.42
    n = int(largo / paso)
    for i in range(n):
        y0, y1 = -i * paso, -(i + 1) * paso
        s0, s1 = 1 - 0.4 * (i / n), 1 - 0.4 * ((i + 1) / n)
        for (a, bq) in ((0, 1), (1, 2), (2, 3), (3, 0)):
            pa = Vector((esquinas[a][0] * s0, y0, esquinas[a][1] * s0))
            pb_ = Vector((esquinas[bq][0] * s1, y1, esquinas[bq][1] * s1))
            barras.append(P.tube(f"{nombre}_diag{i}_{a}", [pa, pb_], 0.016, coll, m=m_am, res=6))
    punta = P.prim("cyl", nombre + "_polea", coll, m_neg, r=0.14, r_top=0.14, h=0.10, seg=32)
    punta.rotation_euler = (0, math.radians(90), 0)
    punta.location = (0, -largo - 0.05, 0.0)
    pl = bpy.data.objects.new(nombre + "_pluma", None)
    coll.objects.link(pl)
    pl.parent = giro
    for o in barras + [punta]:
        o.parent = pl
    giro.rotation_euler = (math.radians(-angulo), 0, 0)      # -X levanta la pluma (apunta a -Y y arriba)
    bpy.context.view_layer.update()
    tip = (pl.matrix_world @ Vector((0, -largo - 0.05, -0.16)))
    return raiz, tip


# ---------------------------------------------------------------- pollos
def mat_pollo():
    m = bpy.data.materials.get("Pollo")
    if m:
        return m
    m = bpy.data.materials.new("Pollo")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.28
    b.inputs["Coat Weight"].default_value = 0.35      # con 0,8 reflejaba el cielo azul y el dorado se veía verdoso
    b.inputs["Coat Roughness"].default_value = 0.22
    b.inputs["Subsurface Weight"].default_value = 0.1
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 9.0
    nz.inputs["Detail"].default_value = 4.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.62, 0.28, 0.05, 1)     # dorado tostado
    ramp.color_ramp.elements[1].position = 0.72
    ramp.color_ramp.elements[1].color = (0.30, 0.10, 0.02, 1)     # tostado oscuro
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.25
    nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def pollo(coll, nombre="Pollo"):
    """Un pollo asado de dibujo (pechuga redonda + 2 trutros con su huesito). Origen en el centro; ~0,34 m."""
    mp = mat_pollo()
    mh = mat_simple("HuesoPollo", (0.98, 0.95, 0.88), rough=0.4)
    cuerpo = blob(nombre + "_cuerpo", [((0, 0, 0), (0.17, 0.13, 0.11), (0, 0, 0)),
                                       ((0, -0.08, 0.02), (0.12, 0.08, 0.09), (0, 0, 0)),
                                       ((0.09, 0.07, -0.03), (0.07, 0.11, 0.065), (0, 0, -25)),
                                       ((-0.09, 0.07, -0.03), (0.07, 0.11, 0.065), (0, 0, 25))], coll, voxel=0.008, suave=8)
    cuerpo.data.materials.append(mp)
    huesos = []
    for s in (1, -1):
        h = cuerno(f"{nombre}_hueso{s}", (s * 0.11, 0.15, -0.02), (s * 0.35, 1, 0.25), (0, 0, 1), 0.08, 0.018, 0.015, coll=coll, m=mh, curv=0.1)
        bola = esfera(f"{nombre}_bola{s}", (s * 0.135, 0.225, 0.0), 0.022, coll, mh)
        huesos += [h, bola]
    for o in huesos:
        colgar(o, cuerpo)
    return cuerpo


def racimo(coll, gancho, n=60, alto=2.6, semilla=11):
    """Racimo de pollos colgando de `gancho` (mundo), como uvas: angosto arriba, ancho abajo. Devuelve la raíz (vacío en el gancho)."""
    r = random.Random(semilla)
    raiz = bpy.data.objects.new("Racimo", None)
    coll.objects.link(raiz)
    raiz.location = gancho
    base = pollo(coll, "PolloBase")
    base_obs = [base] + list(base.children)
    m_cuerda = mat_simple("Cuerda", (0.85, 0.74, 0.52), rough=0.8)
    cuerda = P.tube("RacimoCuerda", [(0, 0, 0), (0, 0, -alto * 0.75)], 0.03, coll, m=m_cuerda, res=8)
    cuerda.parent = raiz
    pollos = []
    for i in range(n):
        u = (i + 0.5) / n
        z = -0.25 - alto * u
        rad = 0.12 + 0.62 * math.sin(math.pi * min(1, u * 1.15)) ** 0.8
        a = i * 2.39996 + r.uniform(-0.3, 0.3)
        p = Vector((rad * math.cos(a) * r.uniform(0.7, 1.0), rad * math.sin(a) * r.uniform(0.7, 1.0), z))
        dup = base.copy()
        dup.data = base.data
        coll.objects.link(dup)
        dup.name = f"Pollo{i}"
        dup.parent = raiz
        dup.location = p
        dup.rotation_euler = (r.uniform(-0.8, 0.8), r.uniform(-0.8, 0.8), r.uniform(0, 6.28))
        s = r.uniform(0.9, 1.15)
        dup.scale = (s, s, s)
        for ch in base.children:
            c2 = ch.copy()
            c2.data = ch.data
            coll.objects.link(c2)
            c2.parent = dup
            c2.matrix_parent_inverse = ch.matrix_parent_inverse.copy()
        pollos.append(dup)
    for o in base_obs:
        o.hide_render = True
        o.hide_viewport = True
    gan = cuerno("Gancho", (0, 0, 0.05), (0, 0, -1), (0, -1, 0), 0.35, 0.045, 0.03, coll=coll, m=P.mat("AceroG", (0.6, 0.61, 0.63), rough=0.3, metal=1.0), curv=2.6)
    gan.parent = raiz
    return raiz, pollos


def cable(coll, a, b, nombre="Cable", r=0.025):
    m = P.mat("CableAcero", (0.32, 0.33, 0.35), rough=0.35, metal=1.0)
    return P.tube(nombre, [a, b], r, coll, m=m, res=10)
