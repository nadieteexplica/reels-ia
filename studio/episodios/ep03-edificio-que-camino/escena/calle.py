"""Set principal del Ep. 3: la obra en Shanghái donde camina la escuela (todo procedural).

Planta (m): el edificio camina por +x entre x≈-31 y x≈+31 con la fachada mirando a -y. La cámara suele estar en y<0.
- Suelo de obra (tierra apisonada con huellas), rejas azules de obra alrededor, calle con plátanos orientales detrás,
  casas bajas de ladrillo gris (shikumen) y torres lejanas; grúa torre, contenedores-oficina, conos y vigas apiladas.
- Cielo físico (sol + cielo celeste) con un sol cálido de costado: fondo vivo, nunca lavado.
"""
import math, random
import bpy
from mathutils import Vector

import props as P
from edificio import _nodo, _caja, mat_estuco


def mat_tierra():
    m = bpy.data.materials.get("TierraObra")
    if m:
        return m
    m = bpy.data.materials.new("TierraObra")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = _nodo(nt, "ShaderNodeTexCoord", -900, 0)
    n1 = _nodo(nt, "ShaderNodeTexNoise", -700, 100, Scale=0.08, Detail=6.0, Roughness=0.55)
    nt.links.new(tc.outputs["Object"], n1.inputs["Vector"])
    n2 = _nodo(nt, "ShaderNodeTexNoise", -700, -150, Scale=1.6, Detail=10.0, Roughness=0.7)
    nt.links.new(tc.outputs["Object"], n2.inputs["Vector"])
    ramp = _nodo(nt, "ShaderNodeValToRGB", -400, 100)
    ramp.color_ramp.elements[0].color = (0.36, 0.22, 0.12, 1)
    ramp.color_ramp.elements[1].color = (0.62, 0.44, 0.27, 1)
    nt.links.new(n1.outputs["Fac"], ramp.inputs["Fac"])
    mix = _nodo(nt, "ShaderNodeMix", -200, 100)
    mix.data_type = "RGBA"
    mix.blend_type = "OVERLAY"
    mix.inputs["Factor"].default_value = 0.35
    nt.links.new(ramp.outputs["Color"], mix.inputs[6])
    nt.links.new(n2.outputs["Color"], mix.inputs[7])
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.95
    bump = _nodo(nt, "ShaderNodeBump", -200, -200, Strength=0.35, Distance=0.05)
    nt.links.new(n2.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs[0], b.inputs["Normal"])
    return m


def mat_asfalto():
    m = bpy.data.materials.get("Asfalto")
    if m:
        return m
    m = bpy.data.materials.new("Asfalto")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    n = _nodo(nt, "ShaderNodeTexNoise", -600, 0, Scale=30.0, Detail=8.0)
    ramp = _nodo(nt, "ShaderNodeValToRGB", -350, 0)
    ramp.color_ramp.elements[0].color = (0.05, 0.05, 0.055, 1)
    ramp.color_ramp.elements[1].color = (0.14, 0.14, 0.15, 1)
    nt.links.new(n.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.8
    return m


def cielo(sc, elev=30.0, azim=-58.0, fuerza=4.6, cielo_f=1.0):
    """Cielo físico + sol. azim 0 = el sol viene de -y (de frente a la fachada); negativo = desde la izquierda."""
    w = sc.world
    nt = w.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_WORLD":
            nt.nodes.remove(n)
    bg = nt.nodes.new("ShaderNodeBackground")
    sky = nt.nodes.new("ShaderNodeTexSky")
    ok = False
    for tipo in ("MULTIPLE_SCATTERING", "NISHITA", "SINGLE_SCATTERING", "HOSEK_WILKIE"):
        try:
            sky.sky_type = tipo
            ok = True
            break
        except TypeError:
            continue
    for attr, val in (("sun_disc", False), ("sun_elevation", math.radians(elev)), ("sun_rotation", math.radians(180 + azim)),
                      ("altitude", 30.0), ("air_density", 0.8), ("aerosol_density", 0.9), ("ozone_density", 1.2)):
        try:
            setattr(sky, attr, val)
        except Exception:
            pass
    # el cielo físico sale muy claro: se baja y se satura un poco hacia el celeste
    hsv = nt.nodes.new("ShaderNodeHueSaturation")
    hsv.inputs["Saturation"].default_value = 1.25
    hsv.inputs["Value"].default_value = 1.0
    nt.links.new(sky.outputs["Color"], hsv.inputs["Color"])
    nt.links.new(hsv.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.22 * cielo_f
    nt.links.new(bg.outputs[0], nt.nodes["World Output"].inputs["Surface"])
    L = bpy.data.lights.get("Sol") or bpy.data.lights.new("Sol", "SUN")
    L.energy, L.color, L.angle = fuerza, (1.0, 0.88, 0.72), math.radians(1.2)
    ob = bpy.data.objects.get("Sol") or bpy.data.objects.new("Sol", L)
    if ob.name not in sc.collection.objects:
        sc.collection.objects.link(ob)
    el, az = math.radians(elev), math.radians(azim)
    d = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))   # hacia el sol
    ob.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    return ob, sky, bg


def arbol(name, loc, s=1.0, coll=None, seed=0):
    """Plátano oriental de las calles de Shanghái: tronco claro moteado y copa de varias masas."""
    rnd = random.Random(seed)
    tronco = P.mat("TroncoPlatano", (0.52, 0.48, 0.40), rough=0.8)
    hoja = P.mat(f"CopaPlatano{seed % 3}", [(0.16, 0.40, 0.08), (0.20, 0.45, 0.10), (0.13, 0.36, 0.07)][seed % 3], rough=0.7)
    t = P.prim("cyl", name + "_t", coll, tronco, r=0.22 * s, r2=0.16 * s, h=5.5 * s, seg=12)
    t.location = (loc[0], loc[1], 2.75 * s)
    for k in range(5):
        b = P.prim("ico", name + f"_c{k}", coll, hoja, sub=2, r=rnd.uniform(1.6, 2.4) * s)
        b.location = (loc[0] + rnd.uniform(-1.6, 1.6) * s, loc[1] + rnd.uniform(-1.6, 1.6) * s, rnd.uniform(5.8, 7.6) * s)
        d = b.modifiers.new("D", "DISPLACE")
        tx = bpy.data.textures.get("RuidoCopa") or bpy.data.textures.new("RuidoCopa", "CLOUDS")
        tx.noise_scale = 0.6
        d.texture, d.strength = tx, 0.9 * s


def casa_baja(name, x0, x1, y0, y1, h, coll, seed=0):
    """Fila de casas shikumen: ladrillo gris, techo de dos aguas de teja oscura, puertas de piedra."""
    gris = P.mat("LadrilloGris", (0.38, 0.38, 0.37), rough=0.85)
    teja = P.mat("TejaOscura", (0.12, 0.12, 0.13), rough=0.7)
    _caja(name, x0, x1, y0, y1, 0, h, coll, gris)
    import bmesh
    bm = bmesh.new()
    ym = (y0 + y1) / 2
    v = [bm.verts.new(p) for p in ((x0 - 0.3, y0 - 0.4, h), (x1 + 0.3, y0 - 0.4, h), (x1 + 0.3, ym, h + 2.2), (x0 - 0.3, ym, h + 2.2),
                                     (x0 - 0.3, y1 + 0.4, h), (x1 + 0.3, y1 + 0.4, h))]
    bm.faces.new((v[0], v[1], v[2], v[3]))
    bm.faces.new((v[3], v[2], v[5], v[4]))
    bm.faces.new((v[0], v[3], v[4]))
    bm.faces.new((v[1], v[5], v[2]))
    P.mesh_obj(name + "_techo", bm, coll, smooth=False, m=teja)
    piedra = P.mat("PiedraPuerta", (0.70, 0.66, 0.58), rough=0.8)
    for x in [x0 + 2 + 4 * i for i in range(int((x1 - x0 - 2) // 4))]:
        _caja(name + "_p", x - 0.8, x + 0.8, y0 - 0.12, y0 + 0.02, 0, 2.6, coll, piedra)


def torre(name, x, y, w, d, h, coll, seed=0):
    rnd = random.Random(seed)
    m = bpy.data.materials.get(f"Torre{seed % 3}")
    if not m:
        m = bpy.data.materials.new(f"Torre{seed % 3}")
        m.use_nodes = True
        nt = m.node_tree
        b = nt.nodes["Principled BSDF"]
        br = _nodo(nt, "ShaderNodeTexBrick", -500, 0)
        c1 = [(0.32, 0.42, 0.52), (0.55, 0.58, 0.62), (0.40, 0.48, 0.55)][seed % 3]
        br.inputs["Color1"].default_value = (*c1, 1)
        br.inputs["Color2"].default_value = (c1[0] * 0.8, c1[1] * 0.85, c1[2] * 0.95, 1)
        br.inputs["Mortar"].default_value = (0.75, 0.76, 0.78, 1)
        br.inputs["Scale"].default_value = 0.35
        br.inputs["Mortar Size"].default_value = 0.08
        br.inputs["Brick Width"].default_value = 0.9
        br.inputs["Row Height"].default_value = 0.6
        br.offset = 0.0
        nt.links.new(br.outputs["Color"], b.inputs["Base Color"])
        b.inputs["Roughness"].default_value = 0.25
        b.inputs["Metallic"].default_value = 0.35
    _caja(name, x - w / 2, x + w / 2, y - d / 2, y + d / 2, 0, h, coll, m)


def grua(coll, x=78.0, y=34.0, h=60.0, yaw=200.0):
    amarillo = P.mat("GruaAmarilla", (0.95, 0.62, 0.05), rough=0.5, metal=0.3)
    _caja("GruaMastil", x - 1, x + 1, y - 1, y + 1, 0, h, coll, amarillo)
    pluma = _caja("GruaPluma", -14, 46, -0.7, 0.7, h, h + 1.6, coll, amarillo)
    pluma.location.x += x
    pluma.location.y += y
    r = math.radians(yaw)
    pluma.rotation_euler = (0, 0, r)
    pluma.location = (x + 16 * math.cos(r), y + 16 * math.sin(r), h + 0.8)
    _caja("GruaCabina", x - 1.6, x + 1.6, y - 1.6, y + 1.6, h - 2.5, h, coll, P.mat("Blanco", (0.85, 0.85, 0.85), rough=0.5))


def contenedor(name, x, y, coll, yaw=0.0, color=(0.15, 0.35, 0.75)):
    m = P.mat(f"Cont{color}", color, rough=0.5, metal=0.2)
    ob = _caja(name, -3, 3, -1.2, 1.2, 0, 2.6, coll, m)
    ob.location = (x, y, 1.3)
    ob.rotation_euler = (0, 0, math.radians(yaw))


def reja(name, x0, y0, x1, y1, coll):
    """Reja de obra azul con franja blanca (2,5 m)."""
    azul = P.mat("RejaAzul", (0.06, 0.28, 0.72), rough=0.45)
    blanco = P.mat("RejaBlanca", (0.92, 0.93, 0.94), rough=0.45)
    L = math.hypot(x1 - x0, y1 - y0)
    a = math.atan2(y1 - y0, x1 - x0)
    for nom, z0, z1, m in (("_az", 0, 2.0, azul), ("_bl", 2.0, 2.5, blanco)):
        ob = _caja(name + nom, -L / 2, L / 2, -0.05, 0.05, z0, z1, coll, m)
        ob.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
        ob.rotation_euler = (0, 0, a)


def cono(name, x, y, coll):
    nar = P.mat("ConoNaranjo", (1.0, 0.30, 0.02), rough=0.5)
    c = P.prim("cyl", name, coll, nar, r=0.22, r2=0.03, h=0.75, seg=16)
    c.location = (x, y, 0.375)


def armar(sc, seed=3):
    coll = P.collection("Calle")
    rnd = random.Random(seed)
    # suelo: obra (tierra) y alrededor pavimento
    tierra = _caja("SueloObra", -90, 120, -60, 42, -0.3, 0.0, coll, mat_tierra())
    _caja("Pavimento", -400, 400, -400, 400, -0.5, -0.32, coll, P.mat("PavGris", (0.30, 0.30, 0.31), rough=0.85))
    _caja("Calle", -400, 400, 46, 60, -0.31, -0.02, coll, mat_asfalto())
    for x in range(-380, 400, 12):                         # línea discontinua
        _caja("Linea", x, x + 5, 52.85, 53.15, -0.02, -0.005, coll, P.mat("LineaBlanca", (0.9, 0.9, 0.86), rough=0.6))
    _caja("Vereda", -400, 400, 42, 46, -0.3, 0.12, coll, P.mat("Vereda", (0.55, 0.53, 0.50), rough=0.8))
    _caja("Vereda2", -400, 400, 60, 64, -0.3, 0.12, coll, P.mat("Vereda", (0.55, 0.53, 0.50), rough=0.8))
    # rejas de la obra (atrás y a los lados, con un portón abierto atrás)
    reja("RejaFondo1", -90, 41.5, 10, 41.5, coll)
    reja("RejaFondo2", 30, 41.5, 120, 41.5, coll)
    reja("RejaIzq", -90, -60, -90, 41.5, coll)
    reja("RejaDer", 120, -60, 120, 41.5, coll)
    # árboles de la calle
    for i, x in enumerate(range(-120, 160, 14)):
        arbol(f"Platano{i}", (x + rnd.uniform(-2, 2), 44.0), s=1.15, coll=coll, seed=i)
        arbol(f"PlatanoB{i}", (x + 7 + rnd.uniform(-2, 2), 62.0), s=1.1, coll=coll, seed=i + 7)
    # casas bajas al otro lado de la calle y torres lejanas
    x = -160
    k = 0
    while x < 200:
        w = rnd.uniform(18, 30)
        casa_baja(f"Casa{k}", x, x + w, 66, 78, rnd.uniform(7.5, 10.5), coll, seed=k)
        x += w + rnd.uniform(1, 3)
        k += 1
    for k in range(16):
        torre(f"Torre{k}", rnd.uniform(-260, 300), rnd.uniform(140, 420), rnd.uniform(24, 40), rnd.uniform(24, 40), rnd.uniform(70, 190), coll, seed=k)
    # utilería de obra
    grua(coll)
    contenedor("Oficina1", -70, -40, coll, 10, (0.15, 0.35, 0.75))
    contenedor("Oficina2", -70, -36.8, coll, 10, (0.85, 0.85, 0.86))
    contenedor("Oficina3", 96, -30, coll, -25, (0.15, 0.35, 0.75))
    for i in range(14):
        cono(f"Cono{i}", -40 + 6 * i + rnd.uniform(-1, 1), -14 + rnd.uniform(-1, 1), coll)
    # montones de tierra y huellas de neumático
    for i in range(7):
        b = P.prim("sphere", f"Monton{i}", coll, mat_tierra(), u=24, v=12, r=1.0)
        b.scale = (rnd.uniform(4, 7), rnd.uniform(3, 5), rnd.uniform(1.2, 2.2))
        b.location = (rnd.choice([-78, -62, 88, 104]) + rnd.uniform(-6, 6), rnd.uniform(-50, 30), 0.0)
    huella = P.mat("Huella", (0.26, 0.17, 0.10), rough=1.0)
    for i in range(6):
        _caja(f"Huella{i}", -90, 120, -24 + 0.9 * (i % 2) + 9 * (i // 2), -23.6 + 0.9 * (i % 2) + 9 * (i // 2), -0.02, 0.004, coll, huella)
    vigas = P.mat("VigasOxido", (0.42, 0.20, 0.10), rough=0.7, metal=0.4)
    for i in range(5):
        _caja(f"VigaPila{i}", 60, 72, -40 + i * 0.5, -39.6 + i * 0.5, 0, 0.4 + 0.4 * (i % 3), coll, vigas)
    return dict(coll=coll)
