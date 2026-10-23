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
    cam.data.clip_end = 500
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


def mat_pintura(nombre="pintura", color=(0.08, 0.2, 0.32), rugo=(0.3, 0.55), sucio=0.25):
    """Pintura esmaltada de equipo industrial, con desgaste y mugre suave."""
    m, nt, b = _nodos(nombre)
    nz = _ruido(nt, escala=4, detalle=10)
    nt.links.new(_mapa(nt, nz.outputs["Fac"], *rugo).outputs[0], b.inputs["Roughness"])
    oscuro = tuple(c * (1 - sucio) for c in color)
    nt.links.new(_rampa(nt, nz.outputs["Fac"], oscuro, color).outputs[0], b.inputs["Base Color"])
    fino = _ruido(nt, escala=180, detalle=2)
    _bump(nt, b, fino.outputs["Fac"], 0.03, 0.0003)
    b.inputs["Coat Weight"].default_value = 0.25
    b.inputs["Coat Roughness"].default_value = 0.2
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
    bpy.ops.object.transform_apply(scale=True)
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
    acero = mat_metal_cepillado("acero_tapa", (0.42, 0.43, 0.45), (0.14, 0.3))
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
def iman_gigante(sc, r=2.5, r_hueco=0.95, alto=3.1, z0=0.45):
    """Bobina superconductora gigante, de pie, con el hueco vertical: cuerpo azul de criostato con aros de acero,
    bandas de cobre a la vista arriba, escarcha abajo (frío), plataforma de concreto y cables gruesos al piso.
    La boca del hueco queda en z = z0 + alto."""
    pintura = mat_pintura("criostato", (0.035, 0.11, 0.2), rugo=(0.22, 0.48), sucio=0.35)
    acero = mat_metal_cepillado("acero_g", (0.45, 0.46, 0.48), (0.2, 0.42))
    cobre = mat_cobre("cobre_g")
    goma = mat_goma("cable_g", (0.02, 0.02, 0.022), 0.5)
    hueco = mat_pintura("hueco_g", (0.02, 0.02, 0.025), rugo=(0.5, 0.7), sucio=0.0)
    esc = mat_pintura("escarcha", (0.62, 0.68, 0.74), rugo=(0.7, 0.95), sucio=0.45)
    cilindro(sc, "G_plataforma", r * 1.18, z0, (0, 0, 0), verts=160, mat=mat_concreto("plataforma", (0.42, 0.42, 0.41), 1.0), bisel=0.02)
    tubo(sc, "G_cuerpo", r, r_hueco, alto, (0, 0, z0), verts=192, mat=pintura, bisel=0.03)
    tubo(sc, "G_escarcha", r * 1.004, r * 0.98, 0.35, (0, 0, z0), verts=192, mat=esc, bisel=0.02)
    tubo(sc, "G_hueco", r_hueco * 1.002, r_hueco * 0.97, alto * 1.01, (0, 0, z0), verts=160, mat=hueco, bisel=0)
    # costillas verticales de acero y un pórtico (grúa puente) encima: le dan escala de máquina, no de torta
    for i in range(16):
        a = 2 * math.pi * i / 16
        caja(sc, f"G_costilla{i}", (0.09, 0.14, alto * 0.96), (r * 1.01 * math.cos(a), r * 1.01 * math.sin(a), z0 + alto / 2),
             acero, 0.01, rot=(0, 0, a))
    gris = mat_pintura("portico", (0.55, 0.42, 0.06), rugo=(0.35, 0.6), sucio=0.4)
    for sx in (-1, 1):
        caja(sc, f"G_columna{sx}", (0.45, 0.45, 9.0), (sx * (r + 2.2), 1.4, 4.5), gris, 0.02)
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
        a = math.radians(70 + 8 * i)
        x, y = r * math.cos(a), r * math.sin(a)
        out = Vector((math.cos(a), math.sin(a), 0))
        zc = z0 + 0.9 + 0.12 * (i % 3)
        pts = [(x, y, zc), (x + out.x * 0.5, y + out.y * 0.5, zc - 0.2), (x + out.x * 1.2, y + out.y * 1.2, 0.35),
               (x + out.x * 2.0, y + out.y * 2.0, 0.09), (x + out.x * 6 + 0.3 * i, y + out.y * 6, 0.09),
               (x + out.x * 18 + 0.3 * i, y + out.y * 18, 0.09)]
        manguera(sc, f"G_cable{i}", pts, 0.085, goma)
        cilindro(sc, f"G_conector{i}", 0.13, 0.25, (x, y, zc - 0.12), verts=32, mat=acero, bisel=0.01).rotation_euler = (0, math.radians(90), a)
    return z0 + alto


def nave(sc, lado=80.0):
    piso = caja(sc, "Piso_nave", (lado, lado, 0.02), (0, 0, -0.01), mat_concreto("concreto_nave", (0.38, 0.38, 0.37), 0.4), 0)
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
    b.inputs["Subsurface Scale"].default_value = 0.6
    b.inputs["Roughness"].default_value = 0.25
    b.inputs["Coat Weight"].default_value = 0.4
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
