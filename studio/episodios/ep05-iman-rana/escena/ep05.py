"""Base del Ep. 5 (imán y rana), estilo REALISTA = "realista pero en un mundo animado" (Tomás, 22-oct-2026; referencia de
calidad Zack D. Films): proporciones reales, materiales con imperfecciones, luz con dirección y sombras de contacto, lente y
profundidad de campo de cámara real, AgX. Nada de pastel ni de caricatura.

Assets (fuera del repo, los baja el workflow a $ASSETS):
  - rana: escaneo "Pond Frog, Pelophylax nigromaculatus" de ffishAsia-and-floraZia (Sketchfab, CC-BY: crédito en la descripción)
    → ef8d05d060a9442297fa7b4542e6d86e.glb (prerelease ep05-modelos)
  - HDRI CC0 de Poly Haven: studio_small_09, empty_warehouse_01, machine_shop_02 (studio.hdr, warehouse.hdr, machine.hdr)
  - Pete: Mixamo "With Skin" (Release privado Personajes del repo nadieteexplica/assets): PETE_nonPBR.fbx. NUNCA al repo público.
"""
import math, os, random
import bpy
from mathutils import Vector, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.environ.get("ASSETS", os.path.join(HERE, "_assets"))
RANA_GLB = "ef8d05d060a9442297fa7b4542e6d86e.glb"


def asset(nombre):
    p = os.path.join(ASSETS, nombre)
    if not os.path.exists(p):
        raise FileNotFoundError(p)
    return p


# ---------------------------------------------------------------- escena y render
def escena(nombre="E", res=(1080, 1920), samples=64):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.name = nombre
    sc.render.engine = "CYCLES"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.max_bounces = 8
    sc.cycles.transparent_max_bounces = 8
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.view_settings.exposure = 0.0
    sc.render.image_settings.file_format = "PNG"
    return sc


def mundo(sc, hdr="studio.hdr", fuerza=0.6, rot=0.0, color_mezcla=None):
    w = bpy.data.worlds.new("Mundo")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(asset(hdr))
    mp = nt.nodes.new("ShaderNodeMapping")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    mp.inputs["Rotation"].default_value[2] = math.radians(rot)
    nt.links.new(mp.outputs[0], env.inputs[0])
    nt.links.new(env.outputs[0], bg.inputs[0])
    bg.inputs[1].default_value = fuerza
    return w


def camara(sc, pos, mira, lente=50, fstop=2.8, foco=None, sensor=36):
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.lens = lente
    cam.data.sensor_width = sensor
    cam.data.sensor_fit = "VERTICAL"   # vertical: el ángulo vertical manda (9:16)
    cam.data.sensor_height = 24
    cam.data.clip_start = 0.005
    cam.data.clip_end = 60000      # cerros a 9–14 km y la central a ~2,4 km
    apuntar(cam, pos, mira)
    cam.data.dof.use_dof = fstop is not None
    if fstop:
        cam.data.dof.aperture_fstop = fstop
        cam.data.dof.focus_distance = foco if foco else (Vector(mira) - Vector(pos)).length
        cam.data.dof.aperture_blades = 7
    return cam


def apuntar(obj, pos, mira, roll=0.0):
    obj.location = Vector(pos)
    d = Vector(mira) - Vector(pos)
    q = d.to_track_quat("-Z", "Y")
    obj.rotation_euler = q.to_euler()
    if roll:
        obj.rotation_euler.rotate_axis("Z", math.radians(roll))


def luz_area(sc, nombre, pos, mira, energia, color=(1, 1, 1), tam=1.0, tam_y=None, forma="RECTANGLE", spread=180):
    l = bpy.data.lights.new(nombre, "AREA")
    l.spread = math.radians(spread)
    l.energy = energia
    l.color = color
    l.shape = forma
    l.size = tam
    l.size_y = tam_y if tam_y else tam
    o = bpy.data.objects.new(nombre, l)
    sc.collection.objects.link(o)
    apuntar(o, pos, mira)
    return o


def luz_punto(sc, nombre, pos, energia, color=(1, 1, 1), radio=0.05):
    l = bpy.data.lights.new(nombre, "POINT")
    l.energy = energia
    l.color = color
    l.shadow_soft_size = radio
    o = bpy.data.objects.new(nombre, l)
    sc.collection.objects.link(o)
    o.location = pos
    return o


# ---------------------------------------------------------------- materiales con imperfecciones (procedurales)
def _nodos(nombre):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    return m, nt, bsdf


def _ruido(nt, escala=8.0, detalle=8.0, estirar=(1, 1, 1), coord="Object"):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = estirar
    nt.links.new(tc.outputs[coord], mp.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = escala
    nz.inputs["Detail"].default_value = detalle
    nt.links.new(mp.outputs[0], nz.inputs["Vector"])
    return nz


def _rampa(nt, entrada, a, b, pos=(0.35, 0.65)):
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.elements[0].position, r.color_ramp.elements[1].position = pos
    r.color_ramp.elements[0].color = a if len(a) == 4 else (*a, 1)
    r.color_ramp.elements[1].color = b if len(b) == 4 else (*b, 1)
    nt.links.new(entrada, r.inputs[0])
    return r


def _mapa(nt, entrada, a, b):
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = a
    mr.inputs["To Max"].default_value = b
    nt.links.new(entrada, mr.inputs["Value"])
    return mr


def _bump(nt, bsdf, entrada, fuerza=0.15, distancia=0.002):
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = fuerza
    bp.inputs["Distance"].default_value = distancia
    nt.links.new(entrada, bp.inputs["Height"])
    nt.links.new(bp.outputs[0], bsdf.inputs["Normal"])
    return bp


def mat_metal_cepillado(nombre="acero", color=(0.62, 0.63, 0.65), rugo=(0.18, 0.38), escala=6.0):
    """Acero/aluminio cepillado: vetas finas estiradas + manchas grandes (huellas, polvo) en la rugosidad."""
    m, nt, b = _nodos(nombre)
    b.inputs["Metallic"].default_value = 1.0
    vetas = _ruido(nt, escala=60, detalle=4, estirar=(1, 1, 90))
    manchas = _ruido(nt, escala=escala, detalle=6)
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "FLOAT"
    mix.inputs[0].default_value = 0.45
    nt.links.new(vetas.outputs["Fac"], mix.inputs[2]); nt.links.new(manchas.outputs["Fac"], mix.inputs[3])
    nt.links.new(_mapa(nt, mix.outputs[0], *rugo).outputs[0], b.inputs["Roughness"])
    col = _rampa(nt, manchas.outputs["Fac"], tuple(c * 0.82 for c in color), color)
    nt.links.new(col.outputs[0], b.inputs["Base Color"])
    _bump(nt, b, vetas.outputs["Fac"], 0.04, 0.0005)
    return m


def mat_pintura(nombre="pintura", color=(0.08, 0.2, 0.32), rugo=(0.3, 0.55), sucio=0.25, capa=0.25):
    """Pintura esmaltada de equipo industrial, con desgaste y mugre suave."""
    m, nt, b = _nodos(nombre)
    nz = _ruido(nt, escala=4, detalle=10)
    nt.links.new(_mapa(nt, nz.outputs["Fac"], *rugo).outputs[0], b.inputs["Roughness"])
    oscuro = tuple(c * (1 - sucio) for c in color)
    nt.links.new(_rampa(nt, nz.outputs["Fac"], oscuro, color).outputs[0], b.inputs["Base Color"])
    fino = _ruido(nt, escala=180, detalle=2)
    _bump(nt, b, fino.outputs["Fac"], 0.03, 0.0003)
    b.inputs["Coat Weight"].default_value = capa
    b.inputs["Coat Roughness"].default_value = 0.2
    if capa == 0.0:
        b.inputs["Specular IOR Level"].default_value = 0.3      # pintura mate: no refleja el cielo como vidrio
    return m


def mat_cobre(nombre="cobre"):
    m, nt, b = _nodos(nombre)
    b.inputs["Metallic"].default_value = 1.0
    nz = _ruido(nt, escala=12, detalle=8)
    nt.links.new(_rampa(nt, nz.outputs["Fac"], (0.55, 0.26, 0.14), (0.93, 0.56, 0.38)).outputs[0], b.inputs["Base Color"])
    nt.links.new(_mapa(nt, nz.outputs["Fac"], 0.22, 0.42).outputs[0], b.inputs["Roughness"])
    return m


def mat_goma(nombre="goma", color=(0.025, 0.025, 0.028), rugo=0.55):
    m, nt, b = _nodos(nombre)
    nz = _ruido(nt, escala=30, detalle=6)
    nt.links.new(_mapa(nt, nz.outputs["Fac"], rugo - 0.1, rugo + 0.15).outputs[0], b.inputs["Roughness"])
    nt.links.new(_rampa(nt, nz.outputs["Fac"], color, tuple(min(1, c * 1.8) for c in color)).outputs[0], b.inputs["Base Color"])
    b.inputs["Coat Weight"].default_value = 0.15
    return m


def mat_concreto(nombre="concreto", color=(0.36, 0.36, 0.35), escala=3.0):
    """Piso de concreto pulido: manchas grandes, poros, pulido desparejo (reflejos que se cortan)."""
    m, nt, b = _nodos(nombre)
    grande = _ruido(nt, escala=escala, detalle=10, coord="Object")
    poros = _ruido(nt, escala=400, detalle=2)
    nt.links.new(_rampa(nt, grande.outputs["Fac"], tuple(c * 0.7 for c in color), color).outputs[0], b.inputs["Base Color"])
    nt.links.new(_mapa(nt, grande.outputs["Fac"], 0.25, 0.75).outputs[0], b.inputs["Roughness"])
    _bump(nt, b, poros.outputs["Fac"], 0.08, 0.001)
    return m


def mat_pared(nombre="pared", color=(0.42, 0.52, 0.55)):
    m, nt, b = _nodos(nombre)
    nz = _ruido(nt, escala=2.5, detalle=8)
    nt.links.new(_rampa(nt, nz.outputs["Fac"], tuple(c * 0.86 for c in color), color).outputs[0], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.85
    fino = _ruido(nt, escala=300, detalle=2)
    _bump(nt, b, fino.outputs["Fac"], 0.05, 0.0005)
    return m


def mat_emision(nombre, color, fuerza):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*color, 1)
    em.inputs[1].default_value = fuerza
    nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs[0])
    return m


def mat_vidrio(nombre="vidrio", rugo=0.02, tinte=(0.95, 0.98, 1.0)):
    m, nt, b = _nodos(nombre)
    b.inputs["Transmission Weight"].default_value = 1.0
    b.inputs["Roughness"].default_value = rugo
    b.inputs["IOR"].default_value = 1.47
    b.inputs["Base Color"].default_value = (*tinte, 1)
    return m


def asignar(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj


def liso(obj, ang=40):
    for p in obj.data.polygons:
        p.use_smooth = True
    try:
        obj.data.set_sharp_from_angle(angle=math.radians(ang))
    except Exception:
        pass
    return obj


# ---------------------------------------------------------------- geometría básica
def cilindro(sc, nombre, r, alto, pos=(0, 0, 0), verts=96, mat=None, bisel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=alto, location=(pos[0], pos[1], pos[2] + alto / 2))
    o = bpy.context.object
    o.name = nombre
    if bisel:
        bv = o.modifiers.new("bisel", "BEVEL"); bv.width = bisel; bv.segments = 3; bv.limit_method = "ANGLE"
    liso(o)
    if mat:
        asignar(o, mat)
    return o


def tubo(sc, nombre, r_ext, r_int, alto, pos=(0, 0, 0), verts=128, mat=None, bisel=0.004):
    """Cilindro hueco (anillo grueso) con bordes biselados."""
    o = cilindro(sc, nombre, r_ext, alto, pos, verts, mat)
    hueco = cilindro(sc, nombre + "_h", r_int, alto * 1.2, (pos[0], pos[1], pos[2] - alto * 0.1), verts)
    bo = o.modifiers.new("hueco", "BOOLEAN"); bo.object = hueco; bo.operation = "DIFFERENCE"; bo.solver = "EXACT"
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier="hueco")
    bpy.data.objects.remove(hueco)
    if bisel:
        bv = o.modifiers.new("bisel", "BEVEL"); bv.width = bisel; bv.segments = 3; bv.limit_method = "ANGLE"
    liso(o)
    return o


def manguera(sc, nombre, puntos, r=0.02, mat=None, res=24):
    cu = bpy.data.curves.new(nombre, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 6
    cu.resolution_u = res
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(puntos) - 1)
    for bp, p in zip(sp.bezier_points, puntos):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    o = bpy.data.objects.new(nombre, cu)
    sc.collection.objects.link(o)
    if mat:
        o.data.materials.append(mat)
    return o


def caja(sc, nombre, tam, pos, mat=None, bisel=0.004, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos, rotation=rot)
    o = bpy.context.object
    o.name = nombre
    o.scale = tam
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)   # la ubicación queda en el objeto
    if bisel:
        bv = o.modifiers.new("bisel", "BEVEL"); bv.width = bisel; bv.segments = 3
    if mat:
        asignar(o, mat)
    return o


# ---------------------------------------------------------------- la rana (escaneo real, CC-BY)
def rana(sc, largo=0.085, mojada=1.0):
    """Importa el escaneo, borra la carta de color, la deja centrada en el origen con el largo pedido (m) y le da piel
    mojada: rugosidad baja con variación, una capa (coat) brillante y algo de translucidez. Devuelve un vacío padre."""
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=asset(RANA_GLB))
    nuevos = [o for o in bpy.data.objects if o not in antes]
    mallas = [o for o in nuevos if o.type == "MESH"]
    for o in list(mallas):
        if len(o.data.vertices) < 100:           # la carta de color del escaneo
            mallas.remove(o)
            nuevos.remove(o)
            bpy.data.objects.remove(o)
    pts = [o.matrix_world @ Vector(c) for o in mallas for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    centro = (lo + hi) / 2
    esc = largo / (hi.x - lo.x)
    padre = bpy.data.objects.new("Rana", None)
    sc.collection.objects.link(padre)
    raiz = [o for o in nuevos if o.parent is None]
    for o in raiz:
        o.location -= centro
    for o in raiz:
        o.parent = padre
    padre.scale = (esc, esc, esc)
    for m in {s.material for o in mallas for s in o.material_slots if s.material}:
        piel_mojada(m, mojada)
    for o in mallas:
        liso(o, 180)
    return padre


def piel_mojada(m, k=1.0):
    nt = m.node_tree
    b = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if not b:
        return
    for l in list(b.inputs["Roughness"].links):
        nt.links.remove(l)
    nz = _ruido(nt, escala=40, detalle=6)
    nt.links.new(_mapa(nt, nz.outputs["Fac"], 0.12, 0.32).outputs[0], b.inputs["Roughness"])
    b.inputs["Coat Weight"].default_value = 0.85 * k
    b.inputs["Coat Roughness"].default_value = 0.06
    b.inputs["Coat IOR"].default_value = 1.33
    b.inputs["Subsurface Weight"].default_value = 0.12
    b.inputs["Subsurface Radius"].default_value = (0.6, 0.4, 0.25)
    b.inputs["Subsurface Scale"].default_value = 0.004
    b.inputs["Specular IOR Level"].default_value = 0.55
    # micro relieve de piel (poros) sobre la normal del escaneo
    poros = _ruido(nt, escala=900, detalle=3)
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.12
    bp.inputs["Distance"].default_value = 0.0002
    nt.links.new(poros.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs[0], b.inputs["Coat Normal"])


def gotitas(sc, padre, n=60, radio=(0.0006, 0.0016), semilla=3):
    """Gotitas de agua sobre la piel (esferitas de agua pegadas a la superficie con rayos)."""
    random.seed(semilla)
    mat = mat_vidrio("gota", 0.0, (1, 1, 1))
    mat.node_tree.nodes["Principled BSDF"].inputs["IOR"].default_value = 1.33
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for _ in range(n * 6):
        if len(pts) >= n:
            break
        d = Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(0.2, 1))).normalized()
        o = padre.matrix_world.translation + d * 0.2
        hit, loc, nor, *_ = sc.ray_cast(dg, o, -d)
        if hit and nor.z > 0.2:
            pts.append((loc, nor))
    for i, (loc, nor) in enumerate(pts):
        r = random.uniform(*radio)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc + nor * r * 0.35, segments=16, ring_count=8)
        g = bpy.context.object
        g.name = f"gota{i}"
        g.scale = (1, 1, 0.55)
        g.rotation_euler = nor.to_track_quat("Z", "Y").to_euler()
        liso(g, 180)
        asignar(g, mat)
        g.parent = padre
        g.matrix_parent_inverse = padre.matrix_world.inverted()
    return pts


# ---------------------------------------------------------------- el imán de laboratorio (electroimán de campos altos)
def iman_lab(sc, alto=1.25, r=0.42, r_hueco=0.028):
    """Electroimán de laboratorio, vertical, con el hueco arriba. Cuerpo azul de equipo industrial, tapa de acero con
    pernos, aros de abrazadera, barras de cobre y mangueras de agua de enfriamiento. La boca del hueco queda en z = alto."""
    acero = mat_metal_cepillado("acero_tapa", (0.30, 0.31, 0.33), (0.2, 0.3), escala=1.5)
    pintura = mat_pintura("cuerpo_iman", (0.07, 0.19, 0.30))
    cobre = mat_cobre()
    goma = mat_goma()
    oscuro = mat_metal_cepillado("acero_oscuro", (0.22, 0.22, 0.23), (0.3, 0.5))
    piezas = []
    piezas.append(tubo(sc, "Iman_cuerpo", r, r_hueco * 1.03, alto - 0.08, (0, 0, 0), mat=pintura, bisel=0.01))
    piezas.append(tubo(sc, "Iman_tapa", r * 1.02, r_hueco, 0.08, (0, 0, alto - 0.08), mat=acero, bisel=0.006))
    piezas.append(tubo(sc, "Iman_boca", r_hueco * 1.6, r_hueco, 0.025, (0, 0, alto), mat=mat_metal_cepillado("boca", (0.32, 0.33, 0.35), (0.08, 0.18)), bisel=0.003))
    # el hueco: un tubo negro mate que baja hondo (se lee como agujero, no como plato)
    negro = mat_pintura("hueco_negro", (0.01, 0.01, 0.012), rugo=(0.6, 0.8), sucio=0.0)
    piezas.append(tubo(sc, "Iman_hueco", r_hueco * 1.02, r_hueco * 0.94, 0.6, (0, 0, alto - 0.58), mat=negro, bisel=0))
    piezas.append(cilindro(sc, "Iman_fondo_hueco", r_hueco, 0.01, (0, 0, alto - 0.58), mat=negro))
    piezas.append(tubo(sc, "Iman_base", r * 1.08, r * 0.3, 0.06, (0, 0, 0), mat=oscuro, bisel=0.008))
    for z in (0.2, alto * 0.55, alto - 0.2):
        piezas.append(tubo(sc, f"Iman_aro{z:.2f}", r * 1.012, r * 0.99, 0.035, (0, 0, z), mat=oscuro, bisel=0.004))
    # pernos de la tapa (dos anillos)
    for k, (rr, n) in enumerate(((r * 0.88, 24), (r * 0.42, 12))):
        for i in range(n):
            a = 2 * math.pi * i / n + k * 0.1
            p = cilindro(sc, f"perno{k}_{i}", 0.008, 0.008, (rr * math.cos(a), rr * math.sin(a), alto), verts=6, mat=oscuro, bisel=0.0015)
            piezas.append(p)
    # barras de cobre (alimentación) y mangueras de enfriamiento que bajan al piso
    for i, a in enumerate((math.radians(200), math.radians(235))):
        x, y = (r + 0.03) * math.cos(a), (r + 0.03) * math.sin(a)
        piezas.append(caja(sc, f"barra{i}", (0.05, 0.012, alto * 0.85), (x, y, alto * 0.45), cobre, 0.003,
                           rot=(0, 0, a + math.pi / 2)))
    for i, a in enumerate((math.radians(-30), math.radians(-5), math.radians(20), math.radians(140))):
        x, y = r * math.cos(a), r * math.sin(a)
        z0 = alto * (0.82 - 0.12 * (i % 2))
        out = Vector((x, y, 0)).normalized()
        pts = [(x, y, z0), (x + out.x * 0.12, y + out.y * 0.12, z0 - 0.05), (x + out.x * 0.35, y + out.y * 0.35, 0.35),
               (x + out.x * 0.7, y + out.y * 0.7, 0.03), (x + out.x * 1.6, y + out.y * 1.6, 0.03)]
        piezas.append(manguera(sc, f"manguera{i}", pts, 0.028, goma))
        piezas.append(cilindro(sc, f"acople{i}", 0.038, 0.06, (x - out.x * 0.01, y - out.y * 0.01, z0 - 0.03), mat=acero, bisel=0.004))
    return piezas


def laboratorio(sc, ancho=8.0, fondo=7.0, alto=3.6, pared=(0.40, 0.50, 0.53)):
    """Sala de laboratorio: piso de concreto pulido, paredes de pintura gris verdosa, bandejas de cables en el techo,
    estantes y equipos al fondo (fuera de foco), tubos fluorescentes y una lámpara cálida."""
    piso = caja(sc, "Piso", (ancho * 2, fondo * 2, 0.02), (0, 0, -0.01), mat_concreto(), 0)
    m_pared = mat_pared("pared", pared)
    caja(sc, "Pared_fondo", (ancho * 2, 0.1, alto), (0, fondo * 0.55, alto / 2), m_pared, 0)
    caja(sc, "Pared_izq", (0.1, fondo * 2, alto), (-ancho * 0.6, 0, alto / 2), m_pared, 0)
    caja(sc, "Pared_der", (0.1, fondo * 2, alto), (ancho * 0.6, 0, alto / 2), m_pared, 0)
    caja(sc, "Techo", (ancho * 2, fondo * 2, 0.05), (0, 0, alto), mat_pared("techo", (0.5, 0.52, 0.52)), 0)
    gris = mat_pintura("equipo", (0.55, 0.57, 0.58), sucio=0.15)
    negro = mat_pintura("equipo_negro", (0.04, 0.04, 0.045), sucio=0.1)
    # racks y armarios de equipos contra la pared del fondo
    for i, x in enumerate((-2.6, -1.9, 1.7, 2.4, 3.1)):
        h = 1.9 + 0.15 * (i % 2)
        caja(sc, f"rack{i}", (0.6, 0.6, h), (x, fondo * 0.55 - 0.4, h / 2), negro if i % 2 else gris, 0.01)
        for j in range(5):
            led = (0.2, 1.0, 0.3) if (i + j) % 3 else (1.0, 0.45, 0.1)
            caja(sc, f"led{i}_{j}", (0.012, 0.004, 0.012), (x - 0.2 + 0.05 * j, fondo * 0.55 - 0.705, 1.2 + 0.1 * i % 3),
                 mat_emision(f"led{i}{j}", led, 30), 0)
    # mesón con un monitor y una lámpara cálida a la izquierda
    caja(sc, "meson", (1.6, 0.7, 0.05), (-2.2, 1.2, 0.9), mat_metal_cepillado("meson_acero", (0.7, 0.7, 0.72)), 0.01)
    caja(sc, "meson_pata", (1.5, 0.6, 0.85), (-2.2, 1.2, 0.45), gris, 0.01)
    caja(sc, "monitor", (0.6, 0.04, 0.38), (-2.3, 1.35, 1.2), negro, 0.008)
    caja(sc, "pantalla", (0.56, 0.005, 0.33), (-2.3, 1.327, 1.2), mat_emision("pantalla", (0.25, 0.55, 0.85), 2.5), 0)
    # bandejas de cables en el techo
    for i, y in enumerate((-1.0, 1.5)):
        caja(sc, f"bandeja{i}", (ancho * 1.6, 0.3, 0.06), (0, y, alto - 0.35), mat_metal_cepillado(f"bandeja{i}", (0.5, 0.5, 0.5), (0.4, 0.6)), 0.005)
    # tubos fluorescentes (emisión) en el techo
    for i, (x, y) in enumerate(((-1.5, 0.2), (1.5, 0.2), (-1.5, 2.6), (1.5, 2.6))):
        caja(sc, f"fluor{i}", (1.2, 0.06, 0.03), (x, y, alto - 0.05), mat_emision(f"fluor{i}", (0.85, 0.95, 1.0), 12), 0)
    # fondo cercano detrás del imán (lo que se ve desenfocado en los planos cerrados): rack con luces, lámpara cálida,
    # cables colgando y una segunda bobina más chica
    caja(sc, "rack_fondo", (0.7, 0.55, 2.0), (0.55, 2.1, 1.0), negro, 0.01)
    for j in range(8):
        led = (0.25, 1.0, 0.35) if j % 3 else (1.0, 0.5, 0.12)
        caja(sc, f"ledf{j}", (0.014, 0.004, 0.014), (0.35 + 0.055 * j, 1.82, 1.15 + 0.12 * (j % 4)), mat_emision(f"ledf{j}", led, 60), 0)
    caja(sc, "panel_fondo", (0.5, 0.01, 0.3), (0.55, 1.82, 1.6), mat_emision("panel_f", (0.2, 0.5, 0.9), 3), 0)
    cilindro(sc, "bobina2", 0.3, 0.9, (-0.9, 2.3, 0), mat=mat_pintura("bobina2", (0.55, 0.12, 0.06)), bisel=0.01)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.022, location=(-0.6, 2.6, 1.75))
    foco = bpy.context.object; asignar(foco, mat_emision("ampolleta", (1.0, 0.62, 0.3), 40))
    luz_punto(sc, "Lampara", (-0.6, 2.6, 1.75), 30, (1.0, 0.62, 0.3), 0.03)
    goma = mat_goma("cable_f")
    for i in range(5):
        x = -0.3 + 0.18 * i
        manguera(sc, f"cable_f{i}", [(x, 2.0, 3.3), (x + 0.05, 1.95, 2.4), (x - 0.04, 1.9, 1.9), (x + 0.1, 1.95, 0.02)], 0.012, goma)
    return piso


# ---------------------------------------------------------------- Pete (Mixamo With Skin, privado) y su pose
PETE_FBX = "PETE_nonPBR.fbx"


def pete(sc, pose_fbx=None, frame=40):
    """Importa a Pete, baja el brillo de sus materiales (el mapa de especular de Mixamo lo deja de plástico mojado) y,
    si se pasa una animación de Mixamo (Without Skin), le copia la pose de ese cuadro hueso por hueso.
    Devuelve el armature (su origen queda en los pies)."""
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=asset(PETE_FBX), automatic_bone_orientation=False)
    nuevos = [o for o in bpy.data.objects if o not in antes]
    arm = next(o for o in nuevos if o.type == "ARMATURE")
    arm.animation_data_clear()   # el FBX "With Skin" trae una acción en T que pisa cualquier pose al renderizar
    for m in {s.material for o in nuevos if o.type == "MESH" for s in o.material_slots if s.material}:
        nt = m.node_tree
        b = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if not b:
            continue
        for nombre, (a, z) in (("Specular IOR Level", (0.0, 0.35)), ("Roughness", (0.45, 0.95))):
            ent = b.inputs[nombre]
            if ent.links:
                src = ent.links[0].from_socket
                nt.links.remove(ent.links[0])
                mr = nt.nodes.new("ShaderNodeMapRange")
                mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = a, z
                nt.links.new(src, mr.inputs["Value"])
                nt.links.new(mr.outputs[0], ent)
            else:
                ent.default_value = (a + z) / 2
        if "hair" in m.name.lower():
            b.inputs["Roughness"].default_value = 0.6
    for o in nuevos:
        if o.type == "MESH":
            liso(o, 180)
    if pose_fbx:
        copiar_pose(arm, pose_fbx, frame)
    return arm


def copiar_pose(arm, fbx, frame):
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=fbx, automatic_bone_orientation=False)
    nuevos = [o for o in bpy.data.objects if o not in antes]
    src = next(o for o in nuevos if o.type == "ARMATURE")
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()
    dst = {b.name.split(":")[-1]: b for b in arm.pose.bones}
    for b in src.pose.bones:
        d = dst.get(b.name.split(":")[-1])
        if d is None:
            continue
        d.rotation_mode = "QUATERNION"
        b.rotation_mode = "QUATERNION"
        d.rotation_quaternion = b.rotation_quaternion.copy()
    for o in nuevos:
        bpy.data.objects.remove(o)
    for a in list(bpy.data.actions):
        if a.users == 0:
            bpy.data.actions.remove(a)


def girar_hueso(arm, sufijo, eje, grados):
    pb = next(b for b in arm.pose.bones if b.name.endswith(":" + sufijo))
    pb.rotation_mode = "QUATERNION"
    from mathutils import Quaternion
    pb.rotation_quaternion = pb.rotation_quaternion @ Quaternion(Vector(eje), math.radians(grados))


# ---------------------------------------------------------------- el imán gigante (hipotético, para una persona)
def iman_gigante(sc, r=2.5, r_hueco=0.95, alto=3.1, z0=0.45, portico=False):
    """Bobina superconductora gigante, de pie, con el hueco vertical: cuerpo azul de criostato con aros de acero,
    bandas de cobre a la vista arriba, escarcha abajo (frío), plataforma de concreto y cables gruesos al piso.
    La boca del hueco queda en z = z0 + alto."""
    pintura = mat_pintura("criostato", (0.018, 0.05, 0.17), rugo=(0.72, 0.9), sucio=0.4, capa=0.0)
    acero = mat_metal_cepillado("acero_g", (0.27, 0.28, 0.3), (0.32, 0.55))
    cobre = mat_cobre("cobre_g")
    goma = mat_goma("cable_g", (0.02, 0.02, 0.022), 0.5)
    hueco = mat_pintura("hueco_g", (0.02, 0.02, 0.025), rugo=(0.5, 0.7), sucio=0.0)
    esc = mat_pintura("escarcha", (0.62, 0.68, 0.74), rugo=(0.7, 0.95), sucio=0.45)
    cilindro(sc, "G_plataforma", r * 1.18, z0, (0, 0, 0), verts=160, mat=mat_concreto("plataforma", (0.24, 0.24, 0.24), 1.0), bisel=0.02)
    tubo(sc, "G_cuerpo", r, r_hueco, alto, (0, 0, z0), verts=192, mat=pintura, bisel=0.03)
    tubo(sc, "G_escarcha", r * 1.004, r * 0.98, 0.35, (0, 0, z0), verts=192, mat=esc, bisel=0.02)
    tubo(sc, "G_hueco", r_hueco * 1.002, r_hueco * 0.97, alto * 1.01, (0, 0, z0), verts=160, mat=hueco, bisel=0)
    # costillas verticales de acero y un pórtico (grúa puente) encima: le dan escala de máquina, no de torta
    for i in range(16):
        a = 2 * math.pi * i / 16
        caja(sc, f"G_costilla{i}", (0.09, 0.14, alto * 0.96), (r * 1.01 * math.cos(a), r * 1.01 * math.sin(a), z0 + alto / 2),
             acero, 0.01, rot=(0, 0, a))
    gris = mat_pintura("portico", (0.55, 0.42, 0.06), rugo=(0.35, 0.6), sucio=0.4)
    for sx in ((-1, 1) if portico else ()):
        caja(sc, f"G_columna{sx}", (0.45, 0.45, 9.0), (sx * (r + 2.2), 1.4, 4.5), gris, 0.02)
    if portico:
        caja(sc, "G_viga", (2 * (r + 2.2) + 0.6, 0.6, 0.7), (0, 1.4, 9.2), gris, 0.02)
        caja(sc, "G_carro", (1.0, 1.0, 0.6), (0.6, 1.4, 8.6), mat_pintura("carro", (0.12, 0.12, 0.13)), 0.02)
        manguera(sc, "G_gancho_cable", [(0.6, 1.4, 8.3), (0.6, 1.4, 6.8)], 0.02, goma)
    for i, z in enumerate((0.55, 1.2, 1.85, 2.5)):
        tubo(sc, f"G_aro{i}", r * 1.01, r * 0.99, 0.09, (0, 0, z0 + z), verts=192, mat=acero, bisel=0.01)
    # tapa: bandas de cobre concéntricas (la bobina a la vista) entre dos aros de acero
    tubo(sc, "G_tapa_ext", r * 1.01, r * 0.92, 0.06, (0, 0, z0 + alto), verts=192, mat=acero, bisel=0.01)
    tubo(sc, "G_tapa_int", r_hueco * 1.12, r_hueco, 0.06, (0, 0, z0 + alto), verts=160, mat=acero, bisel=0.01)
    k = 7
    for i in range(k):
        r1 = r_hueco * 1.12 + (r * 0.92 - r_hueco * 1.12) * i / k
        r2 = r1 + (r * 0.92 - r_hueco * 1.12) / k * 0.82
        tubo(sc, f"G_cobre{i}", r2, r1, 0.035, (0, 0, z0 + alto), verts=192, mat=cobre, bisel=0.004)
    for i in range(36):
        a = 2 * math.pi * i / 36
        cilindro(sc, f"G_perno{i}", 0.035, 0.03, ((r * 0.965) * math.cos(a), (r * 0.965) * math.sin(a), z0 + alto + 0.06),
                 verts=6, mat=acero, bisel=0.006)
    # cables de alimentación: salen por el costado y se van por el piso hacia el fondo
    for i in range(6):
        a = math.radians(105 + 8 * i)
        x, y = r * math.cos(a), r * math.sin(a)
        out = Vector((math.cos(a), math.sin(a), 0))
        zc = z0 + 0.9 + 0.12 * (i % 3)
        lejos = Vector((-1150, 2080, 0)) - Vector((x, y, 0))
        lejos.normalize()
        p2 = Vector((x, y, 0)) + out * 2.0
        pts = [(x, y, zc), (x + out.x * 0.5, y + out.y * 0.5, zc - 0.2), (x + out.x * 1.2, y + out.y * 1.2, 0.35),
               (p2.x, p2.y, 0.09), tuple(p2 + lejos * 12 + Vector((0.35 * i, 0, 0.09))), tuple(p2 + lejos * 60 + Vector((0.35 * i, 0, 0.09))),
               tuple(p2 + lejos * 400 + Vector((0.35 * i, 0, 0.09)))]
        manguera(sc, f"G_cable{i}", pts, 0.085, goma)
        cilindro(sc, f"G_conector{i}", 0.13, 0.25, (x, y, zc - 0.12), verts=32, mat=acero, bisel=0.01).rotation_euler = (0, math.radians(90), a)
    return z0 + alto


def nave(sc, lado=80.0):
    piso = caja(sc, "Piso_nave", (lado, lado, 0.02), (0, 0, -0.01), mat_concreto("concreto_nave", (0.27, 0.27, 0.26), 0.4), 0)
    # marcas amarillas de seguridad en el piso alrededor del imán (pintura gastada)
    amarillo = mat_pintura("amarillo", (0.75, 0.55, 0.05), rugo=(0.5, 0.8), sucio=0.4)
    tubo(sc, "linea_seg", 4.6, 4.45, 0.004, (0, 0, 0.0), verts=192, mat=amarillo, bisel=0)
    return piso


# ---------------------------------------------------------------- adentro de la rana: el agua y el empujón del imán
def mat_molecula(nombre, color, rugo=0.18):
    m, nt, b = _nodos(nombre)
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rugo
    b.inputs["Coat Weight"].default_value = 0.6
    b.inputs["Coat Roughness"].default_value = 0.05
    b.inputs["Subsurface Weight"].default_value = 0.25
    b.inputs["Subsurface Radius"].default_value = tuple(min(1, c * 1.5 + 0.2) for c in color)
    b.inputs["Subsurface Scale"].default_value = 0.05
    return m


def molecula_agua(sc, pos, rot, esc=1.0, mats=None, nombre="H2O"):
    """H2O con el ángulo real (104,5°): oxígeno rojo grande, dos hidrógenos blancos. Devuelve el vacío padre."""
    o_m, h_m = mats
    padre = bpy.data.objects.new(nombre, None)
    sc.collection.objects.link(padre)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5 * esc, location=(0, 0, 0), segments=32, ring_count=16)
    ox = bpy.context.object; liso(ox, 180); asignar(ox, o_m); ox.parent = padre
    for s in (-1, 1):
        a = math.radians(104.5 / 2) * s
        d = Vector((math.sin(a), 0, math.cos(a))) * 0.48 * esc
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3 * esc, location=d, segments=24, ring_count=12)
        hh = bpy.context.object; liso(hh, 180); asignar(hh, h_m); hh.parent = padre
    padre.location = pos
    padre.rotation_euler = rot
    return padre


def tejido(sc, n=40, caja_xy=8.0, z=(-3, 6), semilla=5):
    """Células del tejido de la rana alrededor (fuera de foco): globos translúcidos rosados con núcleo."""
    random.seed(semilla)
    m, nt, b = _nodos("celula")
    b.inputs["Base Color"].default_value = (0.55, 0.11, 0.09, 1)
    b.inputs["Subsurface Weight"].default_value = 1.0
    b.inputs["Subsurface Radius"].default_value = (1.0, 0.3, 0.2)
    b.inputs["Subsurface Scale"].default_value = 0.9
    b.inputs["Roughness"].default_value = 0.5
    b.inputs["Coat Weight"].default_value = 0.15
    b.inputs["Coat Roughness"].default_value = 0.3
    # tejido: manchas y venitas (no un globo de plástico)
    nz = _ruido(nt, escala=3.0, detalle=12, coord="Generated")
    nt.links.new(_rampa(nt, nz.outputs["Fac"], (0.32, 0.05, 0.05), (0.62, 0.16, 0.12)).outputs[0], b.inputs["Base Color"])
    fino = _ruido(nt, escala=40, detalle=6, coord="Generated")
    _bump(nt, b, fino.outputs["Fac"], 0.25, 0.02)
    for i in range(n):
        x, y = random.uniform(-caja_xy, caja_xy), random.uniform(3, 14)
        bpy.ops.mesh.primitive_ico_sphere_add(radius=random.uniform(1.2, 2.4), subdivisions=4, location=(x, y, random.uniform(*z)))
        c = bpy.context.object
        c.scale = (1, random.uniform(0.7, 1.0), random.uniform(0.6, 0.9))
        d = c.modifiers.new("bulto", "DISPLACE"); tx = bpy.data.textures.new(f"cel{i}", "CLOUDS"); tx.noise_scale = 1.2; d.texture = tx; d.strength = 0.25
        liso(c, 180); asignar(c, m)


def linea_campo(sc, nombre, pts, r=0.03, color=(0.2, 0.85, 1.0), fuerza=6.0):
    """Línea del campo del imán: tubo fino que brilla (capa de explicación, estilizada encima del mundo real)."""
    return manguera(sc, nombre, pts, r, mat_emision(nombre + "_m", color, fuerza))


def flecha(sc, nombre, base, largo=0.9, r=0.06, color=(1.0, 0.45, 0.05), fuerza=2.2):
    """Flecha hacia arriba (el empujón del imán): cilindro + cono que brillan."""
    m = mat_emision(nombre + "_m", color, fuerza)
    bx, by, bz = base
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=largo * 0.7, location=(bx, by, bz + largo * 0.35), vertices=24)
    c = bpy.context.object; asignar(c, m)
    bpy.ops.mesh.primitive_cone_add(radius1=r * 2.4, depth=largo * 0.3, location=(bx, by, bz + largo * 0.85), vertices=24)
    p = bpy.context.object; asignar(p, m)
    return c, p


def rotar_hueso_mundo(arm, sufijo, eje_mundo, grados):
    """Gira un hueso alrededor de un eje del MUNDO que pasa por su cabeza (no depende de los ejes locales de Mixamo)."""
    from mathutils import Matrix
    bpy.context.view_layer.update()
    pb = next(b for b in arm.pose.bones if b.name.endswith(":" + sufijo))
    mw = arm.matrix_world @ pb.matrix
    cabeza = mw.to_translation()
    R = Matrix.Rotation(math.radians(grados), 4, Vector(eje_mundo))
    nueva = Matrix.Translation(cabeza) @ R @ Matrix.Translation(-cabeza) @ mw
    pb.matrix = arm.matrix_world.inverted() @ nueva
    bpy.context.view_layer.update()


def pose_flotando(arm):
    """Desde la T de Mixamo: brazos abajo y un poco abiertos, codos apenas doblados, cabeza que mira abajo (sorpresa tranquila).
    Pete mira hacia -Y; su brazo izquierdo apunta a +X."""
    rotar_hueso_mundo(arm, "LeftArm", (0, 1, 0), 58)
    rotar_hueso_mundo(arm, "RightArm", (0, 1, 0), -58)
    rotar_hueso_mundo(arm, "LeftForeArm", (0, 1, 0), 12)
    rotar_hueso_mundo(arm, "RightForeArm", (0, 1, 0), -12)
    rotar_hueso_mundo(arm, "Head", (1, 0, 0), 14)
    rotar_hueso_mundo(arm, "LeftUpLeg", (0, 1, 0), 4)
    rotar_hueso_mundo(arm, "RightUpLeg", (0, 1, 0), -4)


# ================================================================ EXTERIOR: salar de Atacama al atardecer
# Tomás (23-oct 00:23): la escena abierta y espaciosa, no dentro de un edificio ("que sea choro"), y todo a escala real.
def cielo_atardecer(sc, elev=4.0, rot=200.0, fuerza=0.32, sol=3.5, color_sol=(1.0, 0.64, 0.42)):
    """Cielo físico (dispersión múltiple) con el sol bajo + una luz de sol para las sombras largas."""
    w = bpy.data.worlds.new("Cielo")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "MULTIPLE_SCATTERING"
    sky.sun_elevation = math.radians(elev)
    sky.sun_rotation = math.radians(rot)
    sky.altitude = 2300          # el salar está a ~2.300 m: aire más limpio
    sky.air_density = 1.0
    sky.aerosol_density = 1.4
    sky.sun_disc = True
    nt.links.new(sky.outputs[0], nt.nodes["Background"].inputs[0])
    nt.nodes["Background"].inputs[1].default_value = fuerza
    s = bpy.data.lights.new("Sol", "SUN")
    s.energy = sol
    s.color = color_sol
    s.angle = math.radians(0.6)
    o = bpy.data.objects.new("Sol", s)
    sc.collection.objects.link(o)
    # el sol de la luz apunta igual que el del cielo
    az = math.radians(rot)
    d = Vector((math.sin(az) * math.cos(math.radians(elev)), math.cos(az) * math.cos(math.radians(elev)), math.sin(math.radians(elev))))
    o.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    return w, o, d


def mat_sal(nombre="costra_sal", escala=1.3):
    """Costra de sal del salar: polígonos de sal (voronoi) con bordes levantados más blancos, polvo y variación grande."""
    m, nt, b = _nodos(nombre)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    vo = nt.nodes.new("ShaderNodeTexVoronoi")
    vo.feature = "DISTANCE_TO_EDGE"
    vo.inputs["Scale"].default_value = escala
    vo.inputs["Randomness"].default_value = 1.0
    dist = nt.nodes.new("ShaderNodeTexNoise"); dist.inputs["Scale"].default_value = 0.6; dist.inputs["Detail"].default_value = 4
    nt.links.new(tc.outputs["Object"], dist.inputs["Vector"])
    mezcla = nt.nodes.new("ShaderNodeMix"); mezcla.data_type = "VECTOR"; mezcla.inputs[0].default_value = 0.18
    nt.links.new(tc.outputs["Object"], mezcla.inputs[4]); nt.links.new(dist.outputs["Color"], mezcla.inputs[5])
    nt.links.new(mezcla.outputs[1], vo.inputs["Vector"])
    borde = _mapa(nt, vo.outputs["Distance"], 1.0, 0.0)
    borde.inputs["From Max"].default_value = 0.06
    grande = _ruido(nt, escala=0.08, detalle=6)
    base = _rampa(nt, grande.outputs["Fac"], (0.62, 0.58, 0.53), (0.80, 0.77, 0.72))
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    nt.links.new(borde.outputs[0], mix.inputs[0])
    nt.links.new(base.outputs[0], mix.inputs[6])
    mix.inputs[7].default_value = (0.93, 0.92, 0.9, 1)
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.88
    fino = _ruido(nt, escala=60, detalle=4)
    suma = nt.nodes.new("ShaderNodeMath"); suma.operation = "ADD"
    nt.links.new(borde.outputs[0], suma.inputs[0])
    esc = nt.nodes.new("ShaderNodeMath"); esc.operation = "MULTIPLY"; esc.inputs[1].default_value = 0.25
    nt.links.new(fino.outputs["Fac"], esc.inputs[0]); nt.links.new(esc.outputs[0], suma.inputs[1])
    _bump(nt, b, suma.outputs[0], 0.5, 0.03)
    return m


def salar(sc, lado=6000.0):
    bpy.ops.mesh.primitive_plane_add(size=lado, location=(0, 0, 0))
    piso = bpy.context.object
    piso.name = "Salar"
    asignar(piso, mat_sal())
    return piso


def mat_lejano(nombre, color, neblina=(0.78, 0.55, 0.52), k=0.55):
    """Cerros lejanos: roca + neblina del atardecer (perspectiva aérea falsa: se mezcla con el color del cielo)."""
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    nz = _ruido(nt, escala=0.004, detalle=10)
    nt.links.new(_rampa(nt, nz.outputs["Fac"], tuple(c * 0.6 for c in color), color).outputs[0], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 1.0
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*neblina, 1)
    em.inputs[1].default_value = 0.35
    mx = nt.nodes.new("ShaderNodeMixShader")
    mx.inputs[0].default_value = k
    nt.links.new(b.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], nt.nodes["Material Output"].inputs[0])
    return m


def cerros(sc, semilla=7):
    """Cordillera lejana (5–12 km) y un volcán de cono perfecto (como los del borde del salar), todo con neblina."""
    random.seed(semilla)
    for i, (ang, dist, alto, ancho) in enumerate(((150, 9000, 900, 9000), (190, 11000, 1500, 12000), (230, 8000, 700, 8000),
                                                 (270, 12000, 1300, 10000), (110, 10000, 1100, 9000), (330, 9000, 800, 9000),
                                                 (20, 11000, 1000, 12000), (60, 10000, 900, 10000))):
        a = math.radians(ang)
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=420, y_subdivisions=60, size=1, location=(math.sin(a) * dist, math.cos(a) * dist, 0))
        g = bpy.context.object
        g.name = f"Cerro{i}"
        g.scale = (ancho, ancho * 0.3, 1)
        g.rotation_euler = (0, 0, -a)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        tx = bpy.data.textures.new(f"cerro{i}", "CLOUDS"); tx.noise_scale = 2200; tx.noise_depth = 5
        for v in g.data.vertices:
            u = (v.co.x / ancho) if abs(math.cos(a)) > 0.5 else (v.co.y / ancho)
            borde = max(0.0, 1 - abs(2 * (v.co - Vector((0, 0, 0))).length / ancho))
            v.co.z = 0
        d = g.modifiers.new("relieve", "DISPLACE"); d.texture = tx; d.strength = alto * 2.2; d.mid_level = 0.35
        d.texture_coords = "GLOBAL"
        tx2 = bpy.data.textures.new(f"cerro_det{i}", "CLOUDS"); tx2.noise_scale = 260; tx2.noise_depth = 6
        d2 = g.modifiers.new("detalle", "DISPLACE"); d2.texture = tx2; d2.strength = alto * 0.35; d2.mid_level = 0.5
        d2.texture_coords = "GLOBAL"
        liso(g, 180)
        asignar(g, mat_lejano(f"cerro_m{i}", (0.30, 0.2, 0.18), k=0.32 + 0.1 * (dist > 10000)))
    # volcán (cono perfecto con cumbre nevada), lejos
    a = math.radians(205)
    dist = 14000
    bpy.ops.mesh.primitive_cone_add(vertices=160, radius1=6500, radius2=350, depth=2600, location=(math.sin(a) * dist, math.cos(a) * dist, 1300))
    v = bpy.context.object; v.name = "Volcan"
    tx = bpy.data.textures.new("volcan", "CLOUDS"); tx.noise_scale = 0.08
    sub = v.modifiers.new("sub", "SUBSURF"); sub.levels = 2; sub.subdivision_type = "SIMPLE"
    d = v.modifiers.new("relieve", "DISPLACE"); d.texture = tx; d.strength = 120
    liso(v, 180)
    asignar(v, mat_lejano("volcan_m", (0.48, 0.3, 0.26), k=0.55))


def central_nuclear(sc, pos=(0, 2500, 0), rot=0.0):
    """Central nuclear a escala real en el horizonte: 2 torres de enfriamiento (~150 m), el domo del reactor y la casa de
    turbinas, con su vapor. Concreto con manchas."""
    hormigon = mat_concreto("hormigon_central", (0.62, 0.6, 0.57), 0.02)
    px, py, pz = pos
    torres = []
    for i, dx in enumerate((-110, 70)):
        # hiperboloide: r(z) = a * sqrt(1 + ((z - z0) / c)^2)
        prof = []
        for k in range(25):
            z = 150 * k / 24
            r = 34 * math.sqrt(1 + ((z - 105) / 55) ** 2)
            prof.append((r, z))
        verts, caras, n = [], [], 64
        for (r, z) in prof:
            for j in range(n):
                t = 2 * math.pi * j / n
                verts.append((r * math.cos(t), r * math.sin(t), z))
        for k in range(len(prof) - 1):
            for j in range(n):
                a0, a1 = k * n + j, k * n + (j + 1) % n
                caras.append((a0, a1, a1 + n, a0 + n))
        me = bpy.data.meshes.new(f"torre{i}"); me.from_pydata(verts, [], caras)
        t = bpy.data.objects.new(f"Torre{i}", me); sc.collection.objects.link(t)
        t.location = (px + dx, py + (i * 40), pz)
        sol = t.modifiers.new("grosor", "SOLIDIFY"); sol.thickness = 1.2
        liso(t, 180); asignar(t, hormigon)
        torres.append(t)
        # vapor: volumen suave sobre la boca
        caja(sc, f"Vapor{i}", (150, 150, 300), (px + dx + 25, py + i * 40 + 10, 150 + 150), mat_vapor(), 0)
    # domo del reactor y casa de turbinas
    cilindro(sc, "Reactor", 24, 45, (px + 200, py - 30, pz), verts=64, mat=hormigon)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=24, location=(px + 200, py - 30, pz + 45), segments=48, ring_count=24)
    dm = bpy.context.object; dm.name = "Domo"; liso(dm, 180); asignar(dm, hormigon)
    caja(sc, "Turbinas", (160, 50, 32), (px + 300, py - 10, pz + 16), mat_pintura("turbinas", (0.55, 0.57, 0.6), sucio=0.3), 0.5)
    return torres


def mat_vapor():
    """Pluma de vapor: densidad = ruido × forma de pluma (más ancha arriba, se deshace hacia los bordes y arriba)."""
    if "vapor" in bpy.data.materials:
        return bpy.data.materials["vapor"]
    m = bpy.data.materials.new("vapor")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    v = nt.nodes.new("ShaderNodeVolumePrincipled")
    v.inputs["Color"].default_value = (1.0, 0.96, 0.93, 1)
    v.inputs["Anisotropy"].default_value = 0.45
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    # distancia al eje de la pluma (x, y en 0..1 → centrado), que se abre con la altura z
    def m_(op, a=None, b=None, v1=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        if a is not None: nt.links.new(a, n.inputs[0])
        elif v1 is not None: n.inputs[0].default_value = v1
        if b is not None:
            if isinstance(b, float): n.inputs[1].default_value = b
            else: nt.links.new(b, n.inputs[1])
        return n.outputs[0]
    dx = m_("SUBTRACT", sep.outputs["X"], 0.5); dy = m_("SUBTRACT", sep.outputs["Y"], 0.5)
    r = m_("SQRT", m_("ADD", m_("MULTIPLY", dx, dx), m_("MULTIPLY", dy, dy)))
    ancho = m_("ADD", m_("MULTIPLY", sep.outputs["Z"], 0.32), 0.12)       # radio de la pluma según la altura
    forma = m_("SUBTRACT", None, m_("DIVIDE", r, ancho), v1=1.0)
    forma = m_("MAXIMUM", forma, 0.0)
    arriba = m_("SUBTRACT", None, sep.outputs["Z"], v1=1.0)
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 4.0; nz.inputs["Detail"].default_value = 8
    nt.links.new(tc.outputs["Generated"], nz.inputs["Vector"])
    nzr = _mapa(nt, nz.outputs["Fac"], 0.0, 1.0); nzr.inputs["From Min"].default_value = 0.42; nzr.inputs["From Max"].default_value = 0.72
    dens = m_("MULTIPLY", m_("MULTIPLY", forma, arriba), nzr.outputs[0])
    nt.links.new(m_("MULTIPLY", dens, 0.16), v.inputs["Density"])
    # brillo propio suave (imita la luz que rebota dentro del vapor: si no, se ve como humo oscuro)
    v.inputs["Emission Color"].default_value = (1.0, 0.86, 0.74, 1)
    nt.links.new(m_("MULTIPLY", dens, 2.2), v.inputs["Emission Strength"])
    nt.links.new(v.outputs[0], nt.nodes["Material Output"].inputs["Volume"])
    return m


def mat_acrilico(nombre="acrilico"):
    """Tubo de vidrio delgado que se lee limpio: transparente al centro y con reflejos en los bordes (fresnel), sin la
    refracción gruesa que con un tubo de 3 cm frente a un lente macro borraba la rana."""
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    tr.inputs[0].default_value = (0.97, 0.99, 1.0, 1)
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.03
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.12
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lw.outputs["Fresnel"], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], nt.nodes["Material Output"].inputs[0])
    return m


def plataforma(sc, lado=3.2):
    """Losa de acero con grip (donde está el imán del laboratorio, en medio del salar)."""
    return caja(sc, "Plataforma", (lado, lado, 0.08), (0, 0, 0.04), mat_metal_cepillado("losa", (0.36, 0.37, 0.39), (0.35, 0.6), 0.4), 0.01)


# ================================================================ tiempos del video (planos) y curvas
import json as _json
from mathutils import Quaternion

FPS = 30
EPI = os.path.abspath(os.path.join(HERE, ".."))
_tp = os.path.join(EPI, "tiempos.json")
T = {int(k): tuple(v) for k, v in _json.load(open(_tp)).items()} if os.path.exists(_tp) else {1: (0.0, 42.0)}


def F(t):
    return int(round(t * FPS)) + 1


def FR(k):
    a, b = T[k]
    return F(a), F(b)


FIN = FR(max(T))[1]


def palabras():
    return _json.load(open(os.path.join(EPI, "words.json")))


def t_palabra(prefijo, desde=0.0):
    for w in palabras():
        if w["s"] >= desde - 1e-6 and w["w"].lower().strip("¡!¿?.,:;…").startswith(prefijo.lower()):
            return w["s"]
    raise KeyError(prefijo)


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lin(f, f0, f1):
    if f1 == f0:
        return 1.0 if f >= f1 else 0.0
    return clamp((f - f0) / (f1 - f0))


def suave(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def sale(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def mezcla(a, b, x):
    if isinstance(a, (int, float)):
        return a + (b - a) * x
    return Vector(a).lerp(Vector(b), x)


def ruido(f, seed=0, vel=1.0):
    r = random.Random(seed)
    s = 0.0
    for k in range(3):
        s += math.sin(f * vel * r.uniform(0.15, 0.5) * (k + 1) + r.uniform(0, 6.28)) / (k + 1)
    return s / 1.83


def tramo(f, claves):
    if f <= claves[0][0]:
        return claves[0][1]
    for (fa, va), (fb, vb) in zip(claves, claves[1:]):
        if f <= fb:
            return mezcla(va, vb, suave(lin(f, fa, fb)))
    return claves[-1][1]


def mirar(cam, pos, tgt, lente=None, foco=None, giro=0.0):
    cam.location = Vector(pos)
    q = (Vector(tgt) - Vector(pos)).to_track_quat("-Z", "Y")
    if giro:
        q = q @ Quaternion((0, 0, 1), math.radians(giro))
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = q
    if lente:
        cam.data.lens = lente
    if cam.data.dof.use_dof:
        cam.data.dof.focus_distance = ((Vector(foco) if foco is not None else Vector(tgt)) - Vector(pos)).length


def orbita(centro, radio, ang, alto):
    a = math.radians(ang)
    c = Vector(centro)
    return Vector((c.x + radio * math.sin(a), c.y - radio * math.cos(a), c.z + alto))


def pantalla(sc, cam, punto):
    from bpy_extras.object_utils import world_to_camera_view
    v = world_to_camera_view(sc, cam, Vector(punto))
    return round(v.x * 1080), round((1 - v.y) * 1920)


def oculto(ob, si=True):
    ob.hide_render = si
    ob.hide_viewport = si
    for ch in ob.children_recursive:
        ch.hide_render = si
        ch.hide_viewport = si


def marca_ojo(sc, nombre, padre, pos_local, r=0.004):
    """Esferita invisible en el ojo de un personaje (chequeo automático 'cara tapada': studio/plantilla/caras.py)."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=8, ring_count=6, location=(0, 0, 0))
    o = bpy.context.object
    o.name = nombre
    o["ojo"] = 1
    m = bpy.data.materials.get("invisible")
    if m is None:
        m = bpy.data.materials.new("invisible")
        m.use_nodes = True
        nt = m.node_tree
        for n in list(nt.nodes):
            if n.type != "OUTPUT_MATERIAL":
                nt.nodes.remove(n)
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        nt.links.new(tr.outputs[0], nt.nodes["Material Output"].inputs[0])
    asignar(o, m)
    # no se ve en el render (ni en reflejos ni sombras) pero sí la tocan los rayos del chequeo de ojos
    for k in ("visible_camera", "visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter", "visible_shadow"):
        setattr(o, k, False)
    o.parent = padre
    o.location = pos_local
    return o


def ojos_pete(sc, arm):
    """Marcas en los ojos de Pete, colgadas del hueso de la cabeza (Mixamo; Pete mira hacia -Y local del armature)."""
    hb = next(b for b in arm.data.bones if b.name.endswith(":Head"))
    out = []
    for s, lado in ((1, "L"), (-1, "R")):
        o = marca_ojo(sc, f"Pete_ojo{lado}", arm, (0, 0, 0), 0.012)
        o.parent_type = "BONE"
        o.parent_bone = hb.name
        o.location = (s * 3.2, 8.5, 9.0)        # cm en el espacio del hueso (FBX de Mixamo en centímetros)
        out.append(o)
    return out


def ojos_rana(sc, rana_padre, largo=0.028):
    """Marcas en los ojos de la rana (cabeza hacia -X del escaneo, ojos arriba)."""
    out = []
    for s, lado in ((1, "L"), (-1, "R")):
        o = marca_ojo(sc, f"Rana_ojo{lado}", rana_padre, (0, 0, 0), 0.0016 / rana_padre.scale.x)
        o.location = (-0.36 * largo / rana_padre.scale.x, s * 0.11 * largo / rana_padre.scale.x, 0.17 * largo / rana_padre.scale.x)
        out.append(o)
    return out
