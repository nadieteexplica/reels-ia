"""Sets del Ep. 10 (kamikazes, realista): E5 la mesa de la barraca (la foto real, la carta, la cinta, la copa),
E1 la pista del Ejército en Kagoshima (1945) y E3 el mar de Okinawa con el portaaviones.

Todo a escala real. Modelos de Objaverse (CC-BY, crédito en la descripción): ver MODELOS. La foto es la original del
26-may-1945 (72.ª Shinbu, dominio público; Santa Clara University / Wikimedia Commons), impresa con borde en tex/.
"""
import math, os, random
import bpy
from mathutils import Vector, Matrix, Euler

import ep10 as E
from ep10 import asset, _nodos, _ruido, _rampa, _mapa, _bump, asignar, liso, cilindro, caja, mat_emision, mat_vidrio

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "tex")

MODELOS = {   # uid de Objaverse → (nombre, autor, licencia)
    "zero": ("a0936456b4824de2959b38389717ab7a", "Mitsubishi A6M Zero (Free Model)", "Aidan6604", "CC-BY"),
    "hornet": ("858bbf73170b47ccb26407ee86d7fa81", "U.S. Navy Aircraft Carrier USS Hornet (CV-8)", "lxyun_2", "CC-BY"),
    "essex": ("c6094509b78b42f79a64eccc253edb3d", "uss Essex class", "tonkermansreal", "CC-BY"),
    "fletcher": ("e0bccc4636594a3eb0d0e57edccb7f76", "fletcher", "Eringi_n7d62", "CC-BY"),
    "oerlikon": ("81bf44146adc433797bb23fb5692d6d1", "20mm Oerlikon Rifle", "Memorie", "CC-BY"),
    "m1": ("6d7929b10c994db0b6b39e35b379bfbd", "M1 Helmet", "(ver ficha)", "CC-BY"),
    "casco": ("1e32e931ffc34fd5a4e839cb6131347c", "Aviator Helmet With Goggles", "enaphets", "CC-BY"),
    "sakura": ("f5e6f5a985ea4fc2a14ee0b4b37572b5", "Sakura Cherry Blossom (Somei Yoshino)", "(ver ficha)", "CC-BY"),
}


def glb(nombre):
    return asset(MODELOS[nombre][0] + ".glb")


def importar(nombre, largo=None, eje="y", borrar=None, nombre_raiz=None):
    """Importa un GLB bajo un vacío: lo centra en x/y, apoya su base en z=0 y lo escala para que mida `largo` en `eje`.
    `borrar`: función(objeto) → True para sacar piezas (p. ej. los B-25 del Hornet). Devuelve el vacío raíz."""
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=glb(nombre))
    nuevos = [o for o in bpy.data.objects if o not in antes]
    for o in nuevos:
        o.animation_data_clear() if o.animation_data else None
    if borrar:
        for o in [o for o in nuevos if o.type == "MESH" and borrar(o)]:
            nuevos.remove(o)
            bpy.data.objects.remove(o)
    mallas = [o for o in nuevos if o.type == "MESH"]
    bpy.context.view_layer.update()
    mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
    for o in mallas:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
    raiz = bpy.data.objects.new(nombre_raiz or nombre, None)
    bpy.context.scene.collection.objects.link(raiz)
    for o in nuevos:
        if o.parent is None:
            o.parent = raiz
    k = 1.0
    if largo:
        i = "xyz".index(eje)
        k = largo / max(1e-6, (mx - mn)[i])
    centro = Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
    for o in nuevos:
        if o.parent is raiz:
            o.matrix_world = Matrix.Translation(-centro) @ o.matrix_world
    raiz.scale = (k, k, k)
    raiz["tam"] = tuple((mx - mn) * k)
    for o in mallas:
        liso(o, 40) if not any(p.use_smooth for p in o.data.polygons[:1]) else None
    return raiz


def mallas_de(raiz):
    return [o for o in raiz.children_recursive if o.type == "MESH"]


def tela(nombre, color, rugo=0.85, escala=220, sucio=0.18):
    """Tela con trama fina y variación (ropa, cinta, bufanda)."""
    m, nt, b = _nodos(nombre)
    nz = _ruido(nt, escala=6, detalle=6)
    nt.links.new(_rampa(nt, nz.outputs["Fac"], tuple(c * (1 - sucio) for c in color), color).outputs[0], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rugo
    b.inputs["Specular IOR Level"].default_value = 0.2
    b.inputs["Sheen Weight"].default_value = 0.4
    tr = _ruido(nt, escala=escala, detalle=2)
    _bump(nt, b, tr.outputs["Fac"], 0.08, 0.0004)
    return m


def textura(nombre, archivo, rugo=0.6, especular=0.25, bump=0.0, sss=0.0):
    m, nt, b = _nodos(nombre)
    im = nt.nodes.new("ShaderNodeTexImage")
    im.image = bpy.data.images.load(os.path.join(TEX, archivo))
    nt.links.new(im.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rugo
    b.inputs["Specular IOR Level"].default_value = especular
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Radius"].default_value = (0.4, 0.35, 0.3)
        b.inputs["Subsurface Scale"].default_value = 0.002
    if bump:
        fn = _ruido(nt, escala=900, detalle=3)
        _bump(nt, b, fn.outputs["Fac"], bump, 0.0002)
    return m


def madera(nombre, color=(0.20, 0.11, 0.055), oscuro=0.5, escala_veta=(1.0, 22.0, 1.0), rugo=(0.32, 0.6), escala=3.0):
    """Madera con vetas (ruido muy estirado), nudos y rayas: mesas, tablas de las barracas, mangos."""
    m, nt, b = _nodos(nombre)
    vt = _ruido(nt, escala=escala, detalle=12, estirar=escala_veta)
    ondas = nt.nodes.new("ShaderNodeTexWave"); ondas.wave_type = "BANDS"; ondas.inputs["Scale"].default_value = escala * 3
    ondas.inputs["Distortion"].default_value = 6.0; ondas.inputs["Detail"].default_value = 4
    tc = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["Object"], ondas.inputs["Vector"])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "FLOAT"; mx.inputs[0].default_value = 0.5
    nt.links.new(vt.outputs["Fac"], mx.inputs[2]); nt.links.new(ondas.outputs["Fac"], mx.inputs[3])
    col = _rampa(nt, mx.outputs[0], tuple(c * oscuro for c in color), color, pos=(0.3, 0.7))
    nt.links.new(col.outputs[0], b.inputs["Base Color"])
    rg = _ruido(nt, escala=40, detalle=6)
    nt.links.new(_mapa(nt, rg.outputs["Fac"], *rugo).outputs[0], b.inputs["Roughness"])
    _bump(nt, b, mx.outputs[0], 0.12, 0.001)
    return m


# ===================================================================== E5 · la mesa de la barraca
def mesa(sc):
    """Mesa de madera gastada en una barraca de noche, con una lámpara de queroseno. Sobre la mesa: la foto real impresa,
    la carta a pincel, el pincel y el tintero, la cinta con el sol rojo y una copa chica de porcelana. Medidas reales."""
    S = {}
    E.mundo_oscuro = True
    w = bpy.data.worlds.new("Noche"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.012, 0.014, 0.02, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.4
    tabla = caja(sc, "Mesa", (1.5, 0.85, 0.045), (0, 0, 0.7375), madera("mesa", (0.22, 0.12, 0.06), escala_veta=(1, 26, 1)), bisel=0.004)
    for i, (x, y) in enumerate(((-0.68, -0.36), (0.68, -0.36), (-0.68, 0.36), (0.68, 0.36))):
        caja(sc, f"Pata{i}", (0.06, 0.06, 0.715), (x, y, 0.3575), bpy.data.materials["mesa"], bisel=0.003)
    # pared de tablas detrás y piso
    pared = madera("tablas", (0.13, 0.085, 0.055), oscuro=0.45, escala_veta=(1, 1, 18), escala=1.2)
    for i in range(16):
        caja(sc, f"Tabla{i}", (0.19, 0.03, 2.6), (-1.5 + i * 0.2, 0.9, 1.3), pared, bisel=0.002)
    piso = caja(sc, "Piso", (5, 5, 0.02), (0, 0, -0.01), madera("piso", (0.12, 0.08, 0.05), escala_veta=(1, 30, 1)))
    # la foto impresa (papel fotográfico con su borde): 12 × 14,8 cm, un poco curvada
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=24, y_subdivisions=30, size=1, location=(0, 0, 0))
    foto = bpy.context.object; foto.name = "Foto"
    ar = 2323 / 1888
    foto.scale = (0.12, 0.12 * ar, 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for v in foto.data.vertices:       # curva suave del papel viejo (las puntas levantan ~3 mm)
        v.co.z = 0.0035 * (abs(v.co.x) / 0.06) ** 2 + 0.0006 * (1 + math.sin(v.co.y * 30))   # nunca bajo la mesa
    foto.location = (-0.12, -0.05, 0.761)
    foto.rotation_euler = (0, 0, 0)
    asignar(foto, textura("foto_papel", "foto_impresa.jpg", rugo=0.42, especular=0.35))
    liso(foto, 180)
    S["foto"] = foto
    # la carta (washi) 24 × 33 cm, a la derecha
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=20, y_subdivisions=26, size=1, location=(0, 0, 0))
    carta = bpy.context.object; carta.name = "Carta"
    carta.scale = (0.24, 0.33, 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for v in carta.data.vertices:
        v.co.z = 0.0008 * (1 + math.sin(v.co.x * 22)) + 0.0005 * (1 + math.cos(v.co.y * 17))
    carta.location = (0.2, 0.02, 0.7605)
    carta.rotation_euler = (0, 0, math.radians(4))
    asignar(carta, textura("washi", "carta.jpg", rugo=0.75, especular=0.15, sss=0.25))
    liso(carta, 180)
    S["carta"] = carta
    # pincel de bambú y tintero (suzuri) con tinta negra brillante
    mango = cilindro(sc, "Pincel", 0.0055, 0.2, (0, 0, 0), verts=24, mat=madera("bambu", (0.55, 0.42, 0.22), escala_veta=(1, 1, 20), escala=8))
    mango.rotation_euler = (0, math.radians(90), math.radians(-25)); mango.location = (0.36, -0.22, 0.766)
    punta = bpy.data.objects.new("Punta", bpy.data.meshes.new("Punta")); sc.collection.objects.link(punta)
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.006, radius2=0.0005, depth=0.03, location=(0, 0, 0))
    pt = bpy.context.object; pt.name = "PuntaPincel"; pt.parent = mango; pt.location = (0, 0, -0.012); pt.rotation_euler = (math.pi, 0, 0)
    tinta = _nodos("tinta_pelo")[0]; tinta.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.01, 0.01, 0.01, 1)
    tinta.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.35
    asignar(pt, tinta); liso(pt, 180)
    piedra = _nodos("suzuri")[0]; bp = piedra.node_tree.nodes["Principled BSDF"]
    bp.inputs["Base Color"].default_value = (0.03, 0.03, 0.035, 1); bp.inputs["Roughness"].default_value = 0.55
    suz = caja(sc, "Tintero", (0.09, 0.16, 0.022), (0.43, 0.06, 0.771), piedra, bisel=0.006)
    liq = _nodos("tinta")[0]; bl = liq.node_tree.nodes["Principled BSDF"]
    bl.inputs["Base Color"].default_value = (0.004, 0.004, 0.005, 1); bl.inputs["Roughness"].default_value = 0.04
    caja(sc, "Tinta", (0.066, 0.05, 0.002), (0.43, 0.115, 0.7825), liq, bisel=0.0)
    # la cinta (hachimaki) doblada en una tira larga con el sol rojo y 神風
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=120, y_subdivisions=4, size=1, location=(0, 0, 0))
    cinta = bpy.context.object; cinta.name = "Cinta"
    cinta.scale = (0.62, 0.054, 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for v in cinta.data.vertices:   # serpentea sobre la mesa y se levanta un poco en los dobleces
        x = v.co.x
        v.co.y += 0.05 * math.sin(x * 9.0)
        v.co.z = 0.0025 + 0.004 * max(0, math.sin(x * 9.0 + 1.2)) ** 6
    cinta.location = (-0.02, 0.24, 0.76); cinta.rotation_euler = (0, 0, math.radians(-12))
    asignar(cinta, textura("hachimaki", "hachimaki.jpg", rugo=0.9, especular=0.1, bump=0.06)); liso(cinta, 180)
    S["cinta"] = cinta
    # copa chica de porcelana blanca (choko) con sake
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.026, depth=0.035, location=(0, 0, 0))
    copa = bpy.context.object; copa.name = "Copa"
    sol = copa.modifiers.new("hueco", "SOLIDIFY"); sol.thickness = 0.0025
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="DESELECT"); bpy.ops.object.mode_set(mode="OBJECT")
    for f in copa.data.polygons:
        if f.normal.z > 0.9:
            f.select = True
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.delete(type="FACE"); bpy.ops.object.mode_set(mode="OBJECT")
    for v in copa.data.vertices:
        if v.co.z > 0:
            v.co.x *= 1.25; v.co.y *= 1.25
    copa.location = (-0.33, 0.2, 0.7775)
    por = _nodos("porcelana")[0]; pb = por.node_tree.nodes["Principled BSDF"]
    pb.inputs["Base Color"].default_value = (0.86, 0.85, 0.81, 1); pb.inputs["Roughness"].default_value = 0.12
    pb.inputs["Subsurface Weight"].default_value = 0.3; pb.inputs["Subsurface Scale"].default_value = 0.003
    asignar(copa, por); liso(copa, 180)
    sake = cilindro(sc, "Sake", 0.028, 0.001, (-0.33, 0.2, 0.787), verts=48, mat=mat_vidrio("sake", 0.0, (0.98, 0.96, 0.88)))
    # lámpara de queroseno: base de lata, tubo de vidrio y la llama (con su luz)
    lata = E.mat_metal_cepillado("lata", (0.35, 0.3, 0.22), rugo=(0.3, 0.55))
    cilindro(sc, "LamparaBase", 0.055, 0.07, (-0.55, 0.28, 0.76), verts=48, mat=lata, bisel=0.004)
    cilindro(sc, "LamparaCuello", 0.028, 0.03, (-0.55, 0.28, 0.83), verts=32, mat=lata)
    vid = cilindro(sc, "LamparaVidrio", 0.035, 0.13, (-0.55, 0.28, 0.86), verts=48, mat=mat_vidrio("vidrio_lampara", 0.03, (1.0, 0.97, 0.9)))
    vid.visible_shadow = False
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.008, location=(-0.55, 0.28, 0.91))
    llama = bpy.context.object; llama.name = "Llama"; llama.scale = (1, 1, 2.6)
    asignar(llama, mat_emision("llama", (1.0, 0.55, 0.18), 60))
    luz = E.luz_punto(sc, "LuzLampara", (-0.55, 0.28, 0.92), 70, (1.0, 0.62, 0.32), radio=0.02)
    E.luz_area(sc, "RebotePapel", (0.3, -0.9, 1.4), (0, 0, 0.76), 6, (1.0, 0.8, 0.62), tam=0.8)   # rebote cálido suave del lado de la cámara
    bpy.data.objects["RebotePapel"].visible_glossy = False
    S["llama"], S["luz"] = llama, luz
    # radio de madera de los años 40 (para el 15 de agosto, plano 26): caja, tela del parlante, dial que se enciende
    caja_r = caja(sc, "Radio", (0.36, 0.2, 0.25), (-0.38, 0.33, 0.885), madera("radio", (0.16, 0.08, 0.035), escala_veta=(1, 1, 16), escala=5), bisel=0.012)
    caja(sc, "RadioTela", (0.2, 0.004, 0.13), (-0.42, 0.229, 0.905), tela("tela_radio", (0.32, 0.24, 0.14), rugo=0.95, escala=600))
    dial = caja(sc, "RadioDial", (0.08, 0.004, 0.045), (-0.27, 0.229, 0.93), mat_emision("dial", (1.0, 0.62, 0.25), 0.0))
    for i, x in enumerate((-0.29, -0.25)):
        k = cilindro(sc, f"Perilla{i}", 0.013, 0.016, (0, 0, 0), verts=24, mat=E.mat_pintura("perilla", (0.05, 0.035, 0.02), capa=0.3))
        k.rotation_euler = (math.radians(90), 0, 0); k.location = (x, 0.226, 0.85)
    S["dial"] = dial
    # el gorro de cuero con antiparras del piloto, junto a la carta (plano 9)
    try:
        casco = importar("casco", largo=0.26, eje="z", nombre_raiz="Gorro")
        casco.location = (0.46, -0.12, 0.76); casco.rotation_euler = (math.radians(80), 0, math.radians(200))
        S["gorro"] = casco
    except Exception as e:
        print("sin gorro:", e)
    # ventana fría a la izquierda (luz de luna) para separar la mesa del fondo
    E.luz_area(sc, "Luna", (-2.2, -1.2, 2.0), (0, 0, 0.75), 9, (0.55, 0.65, 1.0), tam=1.2)
    # polvo en el aire (motas que brillan con la lámpara)
    random.seed(11)
    mota = mat_emision("mota", (1.0, 0.85, 0.6), 1.2)
    S["motas"] = []
    for i in range(60):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=random.uniform(0.0004, 0.0009),
                                              location=(random.uniform(-0.6, 0.4), random.uniform(-0.4, 0.4), random.uniform(0.78, 1.15)))
        o = bpy.context.object; asignar(o, mota); o.visible_shadow = False
        S["motas"].append((o, o.location.copy(), random.uniform(0, 6.28)))
    return S


def mesa_viva(S, t):
    """La llama tiembla, la luz respira y el polvo flota (nada quieto)."""
    k = 1.0 + 0.08 * math.sin(t * 13.0) + 0.05 * math.sin(t * 29.0 + 1.3)
    S["luz"].data.energy = 70 * k
    S["llama"].scale = (1, 1, 2.6 * (0.95 + 0.08 * math.sin(t * 17.0)))
    for o, p0, ph in S["motas"]:
        o.location = p0 + Vector((0.012 * math.sin(t * 0.7 + ph), 0.01 * math.cos(t * 0.5 + ph), 0.006 * t))


def radio_dial(S, fuerza):
    m = S["dial"].data.materials[0]
    m.node_tree.nodes["Emission"].inputs[1].default_value = fuerza


# ===================================================================== E1 · la pista de Kagoshima (1945)
def mat_pasto_tierra(nombre="pista"):
    """Pasto y tierra: la franja de la pista (|x| < 22 m) es tierra apisonada con huellas a lo largo; el resto, pasto con
    manchas secas. Coordenadas Object (el plano no se escala)."""
    m, nt, b = _nodos(nombre)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sep.inputs[0])
    ab = nt.nodes.new("ShaderNodeMath"); ab.operation = "ABSOLUTE"; nt.links.new(sep.outputs[0], ab.inputs[0])
    borde = _ruido(nt, escala=0.08, detalle=4)
    ofs = nt.nodes.new("ShaderNodeMath"); ofs.operation = "MULTIPLY_ADD"; ofs.inputs[1].default_value = 6.0; ofs.inputs[2].default_value = 0.0
    nt.links.new(borde.outputs["Fac"], ofs.inputs[0])
    suma = nt.nodes.new("ShaderNodeMath"); suma.operation = "SUBTRACT"; nt.links.new(ab.outputs[0], suma.inputs[0]); nt.links.new(ofs.outputs[0], suma.inputs[1])
    mk = _mapa(nt, suma.outputs[0], 1.0, 0.0); mk.inputs["From Min"].default_value = 16.0; mk.inputs["From Max"].default_value = 22.0
    pasto_n = _ruido(nt, escala=0.6, detalle=10)
    pasto = _rampa(nt, pasto_n.outputs["Fac"], (0.055, 0.075, 0.022), (0.17, 0.19, 0.07))
    seco = _ruido(nt, escala=0.05, detalle=6)
    ks = _mapa(nt, seco.outputs["Fac"], 0.0, 1.0); ks.inputs["From Min"].default_value = 0.5; ks.inputs["From Max"].default_value = 0.68
    pasto2 = nt.nodes.new("ShaderNodeMix"); pasto2.data_type = "RGBA"
    nt.links.new(ks.outputs[0], pasto2.inputs[0]); nt.links.new(pasto.outputs[0], pasto2.inputs[6]); pasto2.inputs[7].default_value = (0.26, 0.22, 0.11, 1)
    huella = _ruido(nt, escala=0.8, detalle=8, estirar=(1.0, 0.04, 1.0))
    tierra = _rampa(nt, huella.outputs["Fac"], (0.16, 0.115, 0.075), (0.31, 0.24, 0.16))
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
    nt.links.new(mk.outputs[0], mx.inputs[0]); nt.links.new(pasto2.outputs[2], mx.inputs[6]); nt.links.new(tierra.outputs[0], mx.inputs[7])
    nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.95
    b.inputs["Specular IOR Level"].default_value = 0.2
    fino = _ruido(nt, escala=40, detalle=6)
    _bump(nt, b, fino.outputs["Fac"], 0.35, 0.02)
    return m


def pasto_pelos(sc, centro, lado=60.0, n=90000, semilla=3, hueco_x=18.0):
    """Pasto con geometría cerca de la cámara (hebras de 5–14 cm), fuera de la franja de la pista."""
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=60, y_subdivisions=60, size=lado, location=(centro[0], centro[1], 0.002))
    g = bpy.context.object; g.name = "PastoBase"
    asignar(g, bpy.data.materials["pista"])
    vg = g.vertex_groups.new(name="pasto")
    for v in g.data.vertices:
        x = (g.matrix_world @ v.co).x
        vg.add([v.index], 0.0 if abs(x) < hueco_x else min(1.0, (abs(x) - hueco_x) / 4.0), "REPLACE")
    ps = g.modifiers.new("pasto", "PARTICLE_SYSTEM").particle_system
    st = ps.settings
    st.type = "HAIR"; st.count = n; st.hair_length = 0.1; st.vertex_group_density = "pasto"
    st.use_advanced_hair = True; st.normal_factor = 1.0; st.factor_random = 0.6; st.brownian_factor = 0.0
    st.child_type = "NONE"; ps.seed = semilla
    st.root_radius = 0.0012; st.tip_radius = 0.0001; st.radius_scale = 1.0
    hm = _nodos("hebras")[0]; hb = hm.node_tree.nodes["Principled BSDF"]
    nz = _ruido(hm.node_tree, escala=0.5, detalle=4)
    hm.node_tree.links.new(_rampa(hm.node_tree, nz.outputs["Fac"], (0.05, 0.08, 0.02), (0.24, 0.24, 0.09)).outputs[0], hb.inputs["Base Color"])
    hb.inputs["Roughness"].default_value = 0.7
    g.data.materials.append(hm); st.material = 2
    return g


def cerros_kagoshima(sc, semilla=5):
    """Lomas verdes (1–5 km) y, al sur con bruma, un volcán de cono de ~920 m a 14 km (como el Kaimondake de Chiran)."""
    random.seed(semilla)
    lejos = E.mat_lejano("lomas", (0.07, 0.1, 0.05), neblina=(0.62, 0.62, 0.66), k=0.38, color2=(0.09, 0.11, 0.07))
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=220, y_subdivisions=220, size=16000, location=(0, 0, 0))
    lo = bpy.context.object; lo.name = "Lomas"
    for v in lo.data.vertices:
        x, y = v.co.x, v.co.y
        r = math.hypot(x, y)
        k = max(0.0, min(1.0, (r - 900) / 1400)) * max(0.0, min(1.0, (7600 - r) / 1200))
        h = 70 * (math.sin(x / 610 + 1.3) * math.cos(y / 520) + 0.6 * math.sin(x / 260 + y / 330) + 0.3 * math.sin(x / 95 - y / 120))
        v.co.z = k * max(0.0, 55 + h)
    asignar(lo, lejos); liso(lo, 180)
    volc = E.mat_lejano("volcan", (0.09, 0.1, 0.08), neblina=(0.72, 0.7, 0.75), k=0.62, color2=(0.12, 0.12, 0.1))
    bpy.ops.mesh.primitive_cone_add(vertices=128, radius1=3600, radius2=120, depth=920, location=(-2000, -14000, 460))
    vo = bpy.context.object; vo.name = "Volcan"
    sub = vo.modifiers.new("sub", "SUBSURF"); sub.levels = 2
    tx = bpy.data.textures.new("volc", "CLOUDS"); tx.noise_scale = 0.35
    dp = vo.modifiers.new("relieve", "DISPLACE"); dp.texture = tx; dp.strength = 120
    asignar(vo, volc); liso(vo, 180)
    return lo, vo


def barraca(sc, nombre, pos, largo=28.0, ancho=7.0, alto=3.2, rot=0.0):
    tablas = bpy.data.materials.get("tablas_ext") or madera("tablas_ext", (0.16, 0.11, 0.07), oscuro=0.5, escala_veta=(1, 1, 14), escala=1.0)
    techo = bpy.data.materials.get("calamina") or E.mat_pintura("calamina", (0.13, 0.13, 0.12), rugo=(0.5, 0.85), sucio=0.5, capa=0.0)
    c = caja(sc, nombre, (ancho, largo, alto), (pos[0], pos[1], alto / 2), tablas, bisel=0.02)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=ancho * 0.78, radius2=0, depth=1.6, location=(pos[0], pos[1], alto + 0.8))
    t = bpy.context.object; t.name = nombre + "_techo"; t.scale = (1.0, largo / ancho * 0.92, 1); t.rotation_euler = (0, 0, math.radians(45))
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    asignar(t, techo)
    for o in (c, t):
        o.rotation_euler.z += math.radians(rot)
    vent = mat_emision("ventana_oscura", (0.02, 0.018, 0.015), 0.2)
    for i in range(6):
        v = caja(sc, f"{nombre}_v{i}", (0.05, 1.2, 0.9), (pos[0] - ancho / 2 - 0.01, pos[1] - largo / 2 + 3 + i * 4.4, 1.7), vent)
    return c


def pintar_avion(raiz, tipo="ejercito"):
    """Pintura de época sobre el Zero de Objaverse (venía sin texturas): verde arriba, gris claro abajo, capó negro,
    hélice café, cabina de vidrio. Ejército: verde oliva moteado; Armada: verde oscuro."""
    arriba = (0.11, 0.14, 0.06) if tipo == "ejercito" else (0.05, 0.08, 0.05)
    verde = E.mat_pintura("verde_" + tipo, arriba, rugo=(0.45, 0.8), sucio=0.45, capa=0.0)
    gris = E.mat_pintura("gris_avion", (0.5, 0.5, 0.46), rugo=(0.4, 0.7), sucio=0.3, capa=0.0)
    negro = E.mat_pintura("capo", (0.02, 0.02, 0.02), rugo=(0.35, 0.6), sucio=0.2, capa=0.0)
    vidrio = mat_vidrio("cabina", 0.05, (0.85, 0.9, 0.95))
    for o in mallas_de(raiz):
        n = o.name.lower()
        z = (o.matrix_world @ Vector(o.bound_box[0])).z
        if any(k in n for k in ("glass", "canopy", "vidr", "cockpit_g")):
            asignar(o, vidrio)
        elif any(k in n for k in ("prop", "helic", "spinner")):
            asignar(o, negro)
        elif any(k in n for k in ("cowl", "engine", "motor")):
            asignar(o, negro)
        else:
            o.data.materials.clear(); o.data.materials.append(verde); o.data.materials.append(gris)
            # cara de abajo en gris (normal hacia abajo)
            for p in o.data.polygons:
                p.material_index = 1 if (o.matrix_world.to_3x3() @ p.normal).z < -0.35 else 0


def hinomaru(sc, padre, pos, normal, r, borde=0.0):
    """El círculo rojo (y, si se pide, su borde blanco) apenas sobre la superficie."""
    rojo = bpy.data.materials.get("hinomaru") or E.mat_pintura("hinomaru", (0.45, 0.025, 0.02), rugo=(0.45, 0.75), sucio=0.3, capa=0.0)
    blanco = bpy.data.materials.get("blanco_av") or E.mat_pintura("blanco_av", (0.75, 0.74, 0.7), rugo=(0.45, 0.75), sucio=0.3, capa=0.0)
    out = []
    for rr, mt, dz in ((r + borde, blanco, 0.0), (r, rojo, 0.002)):
        if rr <= 0 or (mt is blanco and borde <= 0):
            continue
        bpy.ops.mesh.primitive_circle_add(vertices=48, radius=rr, fill_type="NGON", location=(0, 0, 0))
        c = bpy.context.object; asignar(c, mt)
        q = Vector(normal).to_track_quat("Z", "Y")
        c.rotation_mode = "QUATERNION"; c.rotation_quaternion = q
        c.location = Vector(pos) + Vector(normal).normalized() * (0.004 + dz)
        c.parent = padre
        out.append(c)
    return out


def bomba(sc, padre, pos, largo=1.5, r=0.16):
    """Bomba de 250 kg bajo el fuselaje: cuerpo, nariz, aletas."""
    met = bpy.data.materials.get("bomba") or E.mat_pintura("bomba", (0.07, 0.075, 0.06), rugo=(0.4, 0.7), sucio=0.4, capa=0.0)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=r, location=(0, 0, 0))
    b = bpy.context.object; b.name = "Bomba"; b.scale = (1, largo / (2 * r), 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for v in b.data.vertices:
        if v.co.y < 0:
            v.co.x *= 0.7 + 0.3 * (1 + v.co.y / (largo / 2)); v.co.z *= 0.7 + 0.3 * (1 + v.co.y / (largo / 2))
    asignar(b, met); liso(b, 180)
    for i in range(4):
        a = caja(sc, f"Aleta{i}", (0.008, 0.28, 0.24), (0, -largo / 2 + 0.05, 0), met)
        a.rotation_euler = (0, math.radians(45 + 90 * i), 0); a.parent = b
    b.parent = padre
    b.location = pos
    return b


TREN = ("Circle_0", "Circle_0.001", "Circle_1", "Circle.001_0", "Circle.001_1", "Torus_0", "Torus_1")   # ruedas y patas
TANQUE = "Cylinder.003_0"          # el tanque bajo el fuselaje: en un kamikaze va la bomba
HELICE = ("Cube.006_0", "Cube.006_0.001", "Cube.006_0.002", "Cube.006_0.003", "Cube.006_1", "Cylinder.001_0")


def ensuciar(m, sucio=0.35):
    """Mugre, polvo y desgaste sobre la pintura del modelo (venía limpia: plástico)."""
    if not m or not m.use_nodes:
        return
    nt = m.node_tree
    b = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if b is None or b.inputs["Base Color"].links:
        return
    c = tuple(b.inputs["Base Color"].default_value[:3])
    nz = _ruido(nt, escala=3.0, detalle=10)
    chorreo = _ruido(nt, escala=1.2, detalle=8, estirar=(1, 6, 1))
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "FLOAT"; mx.inputs[0].default_value = 0.5
    nt.links.new(nz.outputs["Fac"], mx.inputs[2]); nt.links.new(chorreo.outputs["Fac"], mx.inputs[3])
    nt.links.new(_rampa(nt, mx.outputs[0], tuple(x * (1 - sucio) for x in c), tuple(min(1, x * 1.08) for x in c)).outputs[0], b.inputs["Base Color"])
    nt.links.new(_mapa(nt, nz.outputs["Fac"], 0.45, 0.85).outputs[0], b.inputs["Roughness"])
    b.inputs["Specular IOR Level"].default_value = 0.35
    fino = _ruido(nt, escala=260, detalle=2)
    _bump(nt, b, fino.outputs["Fac"], 0.04, 0.0003)


def avion(sc, con_bomba=True, vuelo=False, nombre="Avion"):
    """Un Zero (A6M) a escala real (12 m de envergadura), con la pintura de fines de la guerra que trae el modelo (verde
    oscuro, capó negro, franjas amarillas de las alas, hinomaru con borde blanco), ensuciado. La nariz mira hacia +y.
    vuelo=True: sin tren de aterrizaje. con_bomba: la bomba de 250 kg en lugar del tanque."""
    r = importar("zero", largo=12.0, eje="x", nombre_raiz=nombre)
    r.rotation_euler.z = math.pi          # el modelo venía con la nariz hacia −y
    vistos = set()
    for o in mallas_de(r):
        for s in o.material_slots:
            if s.material and s.material.name not in vistos:
                vistos.add(s.material.name); ensuciar(s.material)
        if (vuelo and o.name in TREN) or (con_bomba and o.name == TANQUE):
            o.hide_render = True
    k = r.scale.x
    if con_bomba:
        bomba(sc, r, (0, -1.85 / k, 0.85 / k), largo=1.5 / k, r=0.16 / k).rotation_euler.z = math.pi
    # la hélice gira alrededor de su eje: las aspas cuelgan de un vacío en el centro del cubo
    bpy.context.view_layer.update()
    aspas = [o for o in mallas_de(r) if o.name in HELICE]
    if aspas:
        cubo = next((o for o in aspas if o.name == "Cylinder.001_0"), aspas[0])
        c = sum((cubo.matrix_world @ Vector(b) for b in cubo.bound_box), Vector()) / 8
        hub = bpy.data.objects.new(nombre + "_Hub", None); bpy.context.scene.collection.objects.link(hub)
        hub.matrix_world = Matrix.Translation(c) @ r.matrix_world.to_3x3().normalized().to_4x4()
        bpy.context.view_layer.update()
        for o in aspas:
            mw = o.matrix_world.copy(); o.parent = hub; o.matrix_world = mw
        mw = hub.matrix_world.copy(); hub.parent = r; hub.matrix_world = mw
        r["hub"] = hub.name
    return r


def girar_helice(raiz, ang):
    """ang en radianes alrededor del eje largo del avión (y local)."""
    h = bpy.data.objects.get(raiz.get("hub", ""))
    if h:
        h.rotation_mode = "XYZ"
        h.rotation_euler.y = ang


def helice(raiz):
    """Las piezas de la hélice (para hacerlas girar o reemplazarlas por un disco)."""
    return [o for o in mallas_de(raiz) if any(k in o.name.lower() for k in ("prop", "helic", "blade"))]


def manga(sc, pos):
    poste = cilindro(sc, "Poste", 0.05, 6, pos, verts=16, mat=E.mat_pintura("poste", (0.3, 0.3, 0.28), sucio=0.4, capa=0.0))
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.35, radius2=0.16, depth=1.8, location=(pos[0], pos[1] + 0.9, 5.8))
    m = bpy.context.object; m.name = "Manga"; m.rotation_euler = (math.radians(-84), 0, 0)
    asignar(m, tela("manga", (0.7, 0.32, 0.12), rugo=0.9))
    return m


def pista(sc, hora="amanecer", pasto_en=None):
    """E1: la pista (franja de tierra a lo largo de y), lomas, volcán, barracas, manga de viento, cerezos y cielo físico.
    hora: 'amanecer' (sol de la mañana, cálido) o 'atardecer' (15 de agosto, naranjo y bajo)."""
    S = {}
    if hora == "amanecer":
        w, sol, d = E.cielo_atardecer(sc, elev=5.0, rot=110.0, fuerza=0.28, sol=3.2, color_sol=(1.0, 0.7, 0.48))
    else:
        w, sol, d = E.cielo_atardecer(sc, elev=2.2, rot=20.0, fuerza=0.24, sol=2.6, color_sol=(1.0, 0.5, 0.26))
    sky = next(n for n in w.node_tree.nodes if n.type == "TEX_SKY")
    sky.sun_disc = False                    # lección 122: cielo físico + lámpara sol → sin disco
    sky.altitude = 50; sky.aerosol_density = 3.0
    S["sol"] = sol
    mat_pasto_tierra("pista")
    bpy.ops.mesh.primitive_plane_add(size=6000, location=(0, 0, 0))
    piso = bpy.context.object; piso.name = "Pista"; asignar(piso, bpy.data.materials["pista"])
    cerros_kagoshima(sc)
    for i, (x, y, r) in enumerate(((-62, 40, 0), (-62, 85, 0), (70, -30, 0))):
        barraca(sc, f"Barraca{i}", (x, y), rot=r)
    manga(sc, (40, 120, 0))
    tambor = E.mat_pintura("tambor", (0.12, 0.13, 0.1), rugo=(0.4, 0.8), sucio=0.55, capa=0.0)
    for i in range(7):
        cilindro(sc, f"Tambor{i}", 0.29, 0.88, (-52 + (i % 3) * 0.62, 18 + (i // 3) * 0.62, 0), verts=32, mat=tambor, bisel=0.01)
    if pasto_en:
        pasto_pelos(sc, pasto_en)
    return S


def cerezos(sc, posiciones, escala=1.0):
    """El escaneo del cerezo (Somei Yoshino) duplicado (linked) en los bordes de la pista."""
    base = importar("sakura", largo=9.0 * escala, eje="z", nombre_raiz="Cerezo0")
    out = [base]
    base.location = posiciones[0]
    for i, p in enumerate(posiciones[1:], 1):
        n = base.copy(); bpy.context.scene.collection.objects.link(n)
        for ch in base.children:
            c = ch.copy(); c.parent = n; bpy.context.scene.collection.objects.link(c)
        n.location = p; n.rotation_euler.z = random.uniform(0, 6.28)
        out.append(n)
    return out


def red_camuflaje(sc, pos, lado=(16, 13), alto=3.2):
    """Red de camuflaje con hojas sobre un avión (en filas, plano 20)."""
    m = bpy.data.materials.get("red")
    if not m:
        m, nt, b = _nodos("red")
        nz = _ruido(nt, escala=1.6, detalle=10)
        hoja = _rampa(nt, nz.outputs["Fac"], (0.05, 0.07, 0.025), (0.16, 0.15, 0.07))
        nt.links.new(hoja.outputs[0], b.inputs["Base Color"])
        hueco = _ruido(nt, escala=4.0, detalle=4)
        ka = _mapa(nt, hueco.outputs["Fac"], 0.0, 1.0); ka.inputs["From Min"].default_value = 0.42; ka.inputs["From Max"].default_value = 0.5
        nt.links.new(ka.outputs[0], b.inputs["Alpha"])
        b.inputs["Roughness"].default_value = 0.95
        _bump(nt, b, nz.outputs["Fac"], 0.6, 0.08)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=24, y_subdivisions=20, size=1, location=(0, 0, 0))
    r = bpy.context.object; r.name = "Red"; r.scale = (lado[0], lado[1], 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for v in r.data.vertices:
        u, w = v.co.x / (lado[0] / 2), v.co.y / (lado[1] / 2)
        v.co.z = alto * (1 - 0.85 * max(abs(u), abs(w)) ** 3) + 0.25 * math.sin(v.co.x * 1.7) * math.cos(v.co.y * 1.3)
    r.location = pos
    asignar(r, m); liso(r, 180)
    return r


# ===================================================================== E3 · el mar de Okinawa (1945)
def mat_mar(nombre="mar"):
    m, nt, b = _nodos(nombre)
    b.inputs["Base Color"].default_value = (0.008, 0.022, 0.03, 1)
    b.inputs["Roughness"].default_value = 0.06
    b.inputs["IOR"].default_value = 1.333
    b.inputs["Specular IOR Level"].default_value = 0.6
    ol = _ruido(nt, escala=0.35, detalle=10)
    _bump(nt, b, ol.outputs["Fac"], 0.28, 0.25)
    return m


def mar(sc, resolucion=11, lado=600.0, tiempo=0.0):
    """Océano: malla con el modificador Ocean cerca (olas reales de ~1 m) y un plano grande sin costura hacia el horizonte."""
    mm = mat_mar()
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    o = bpy.context.object; o.name = "Olas"
    oc = o.modifiers.new("ocean", "OCEAN")
    oc.geometry_mode = "GENERATE"; oc.resolution = resolucion; oc.spatial_size = int(lado); oc.size = 1.0
    oc.wave_scale = 1.1; oc.choppiness = 1.0; oc.wind_velocity = 9.0; oc.wave_alignment = 0.35; oc.time = tiempo
    oc.repeat_x = oc.repeat_y = 3
    asignar(o, mm)
    bpy.ops.mesh.primitive_plane_add(size=60000, location=(0, 0, -0.25))
    lejos = bpy.context.object; lejos.name = "MarLejos"; asignar(lejos, mm)
    return o, lejos


def cielo_mar(sc, fuerza=0.75, rot=40.0):
    """Mañana gris sobre Okinawa: HDRI de cielo parcialmente nublado (CC0, Poly Haven) + un sol frío y débil."""
    w = E.mundo(sc, "cielo_nubes.hdr", fuerza=fuerza, rot=rot)
    s = bpy.data.lights.new("SolFrio", "SUN"); s.energy = 1.6; s.color = (0.82, 0.88, 1.0); s.angle = math.radians(3.0)
    o = bpy.data.objects.new("SolFrio", s); sc.collection.objects.link(o)
    o.rotation_euler = Euler((math.radians(52), 0, math.radians(rot + 160)))
    return w, o


def es_b25(o):
    n = o.name.lower() + " " + " ".join(s.material.name.lower() for s in o.material_slots if s.material)
    return "b-25" in n or "mitchell" in n


def portaaviones(sc, largo=251.0):
    """El portaaviones (clase Yorktown, como el Enterprise de 1945) sin los B-25 del modelo (eran del ataque de 1942)."""
    r = importar("hornet", largo=largo, eje="y", borrar=es_b25, nombre_raiz="Portaaviones")
    r.location.z = -7.8          # calado ~8 m: la cubierta de vuelo queda a ~16 m del agua
    return r


def barco_lejano(sc, nombre, modelo, largo, pos, rot=0.0):
    r = importar(modelo, largo=largo, eje="x" if modelo in ("essex",) else "y", nombre_raiz=nombre)
    r.location = pos
    r.rotation_euler.z = math.radians(rot)
    return r


def humo_mat(nombre="humo_negro", color=(0.02, 0.02, 0.02), densidad=2.0, escala=1.4):
    m = bpy.data.materials.get(nombre)
    if m:
        return m
    m = bpy.data.materials.new(nombre); m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    vol = nt.nodes.new("ShaderNodePrincipledVolume")
    vol.inputs["Color"].default_value = (*color, 1)
    vol.inputs["Anisotropy"].default_value = 0.2
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = escala; nz.inputs["Detail"].default_value = 6
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    # se apaga hacia el borde de la esfera (sin cáscara dura)
    gr = nt.nodes.new("ShaderNodeTexGradient"); gr.gradient_type = "SPHERICAL"
    nt.links.new(tc.outputs["Object"], gr.inputs["Vector"])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    nt.links.new(nz.outputs["Fac"], mul.inputs[0]); nt.links.new(gr.outputs["Fac"], mul.inputs[1])
    mr = _mapa(nt, mul.outputs[0], 0.0, densidad); mr.inputs["From Min"].default_value = 0.12; mr.inputs["From Max"].default_value = 0.42
    nt.links.new(mr.outputs[0], vol.inputs["Density"])
    nt.links.new(vol.outputs[0], nt.nodes["Material Output"].inputs["Volume"])
    return m


def bocanada(sc, nombre, pos, r, mat=None):
    """Una nube de humo (esfera volumétrica)."""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0, location=pos)
    o = bpy.context.object; o.name = nombre; o.scale = (r, r, r)
    asignar(o, mat or humo_mat())
    o.visible_shadow = True
    return o


def trazadora(sc, nombre):
    m = bpy.data.materials.get("trazadora") or mat_emision("trazadora", (1.0, 0.42, 0.12), 40)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.025, depth=6.0, location=(0, 0, 0))
    o = bpy.context.object; o.name = nombre; asignar(o, m); o.visible_shadow = False
    return o


def fogonazo(sc, nombre):
    m = bpy.data.materials.get("fogonazo") or mat_emision("fogonazo", (1.0, 0.7, 0.3), 80)
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.18, radius2=0.0, depth=0.6, location=(0, 0, 0))
    o = bpy.context.object; o.name = nombre; asignar(o, m); o.visible_shadow = False
    return o


def oerlikon(sc, pos, mira):
    """Cañón Oerlikon de 20 mm (modelo CC-BY) en su pedestal, apuntando a `mira`."""
    r = importar("oerlikon", largo=2.2, eje="x", nombre_raiz="Oerlikon")
    r.location = pos
    d = Vector(mira) - Vector(pos)
    r.rotation_euler = (0, -math.atan2(d.z, Vector((d.x, d.y, 0)).length) * 0.0, math.atan2(d.y, d.x))
    return r


def salpicadura(sc, nombre, pos, alto=14.0):
    blanco = humo_mat("espuma", (0.85, 0.87, 0.88), densidad=3.0, escala=2.0)
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=5.0, radius2=1.2, depth=alto, location=(pos[0], pos[1], alto / 2))
    o = bpy.context.object; o.name = nombre; asignar(o, blanco)
    return o
