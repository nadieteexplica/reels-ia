"""E4 del Ep. 10: la Tierra de verdad (NASA Blue Marble Next Generation, dic-2004, relieve y batimetría; dominio público),
sobre la base del mapa del Ep. 9. Tres niveles de imagen sin costura:
  L0 mundo 5400×2700 · L1 Pacífico occidental del 21600×10800 (1,85 km/px) · L2 Japón y Ryukyu del mosaico C1 (500 m/px).
Los recortes los hace mapa_recortes.py en la máquina (assets.txt: `mapas mapa_recortes.py`). 1 unidad = 1.000 km.
Las capas (islas, flechas, manchas, barras, destellos) van en el post, con las posiciones en pantalla que da puntos()."""
import math, os
import bpy
from mathutils import Vector

import ep10 as E

R = 6.371
L1 = (100.0, -5.0, 170.0, 50.0)          # lon0, lat0, lon1, lat1 (los mismos de mapa_recortes.py)
L2 = (122.0, 24.0, 146.0, 42.0)
LUGARES = {
    "japon": (36.2, 138.3), "tokio": (35.68, 139.69), "kyushu": (32.6, 130.9), "okinawa": (26.45, 127.85),
    "hiroshima": (34.39, 132.45), "nagasaki": (32.75, 129.88), "kagoshima": (31.4, 130.4),
    # islas que Japón perdió en 1944–45 (plano 4), del sur hacia Japón
    "guadalcanal": (-9.6, 160.1), "nueva_guinea": (-5.5, 145.5), "saipan": (15.2, 145.75), "guam": (13.45, 144.8),
    "leyte": (10.9, 124.9), "luzon": (16.0, 121.0), "iwo_jima": (24.78, 141.32),
}


def xyz(lat, lon, r=R):
    la, lo = math.radians(lat), math.radians(lon)
    return Vector((r * math.cos(la) * math.cos(lo), r * math.cos(la) * math.sin(lo), r * math.sin(la)))


def norte(lat, lon):
    la, lo = math.radians(lat), math.radians(lon)
    return Vector((-math.sin(la) * math.cos(lo), -math.sin(la) * math.sin(lo), math.cos(la)))


def _op(nt, o, a, b=None):
    n = nt.nodes.new("ShaderNodeMath"); n.operation = o
    for i, s in enumerate((a, b)):
        if s is None:
            continue
        if isinstance(s, (int, float)):
            n.inputs[i].default_value = s
        else:
            nt.links.new(s, n.inputs[i])
    return n.outputs[0]


def _imagen(nt, ruta, u, v):
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(ruta); t.interpolation = "Linear"; t.extension = "EXTEND"
    cv = nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(u, cv.inputs[0]); nt.links.new(v, cv.inputs[1])
    nt.links.new(cv.outputs[0], t.inputs["Vector"])
    return t.outputs["Color"]


def _mascara(nt, uu, vv, borde=0.02):
    def lado(x):
        a = _op(nt, "MINIMUM", _op(nt, "DIVIDE", x, borde), 1.0)
        b = _op(nt, "MINIMUM", _op(nt, "DIVIDE", _op(nt, "SUBTRACT", 1.0, x), borde), 1.0)
        return _op(nt, "MAXIMUM", _op(nt, "MINIMUM", a, b), 0.0)
    return _op(nt, "MULTIPLY", lado(uu), lado(vv))


def tierra(sc):
    mapas = os.path.join(E.ASSETS, "mapas")
    sc.view_settings.view_transform = "Standard"       # los colores de la NASA tal cual
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    sc.cycles.max_bounces = 2; sc.cycles.diffuse_bounces = 1; sc.cycles.glossy_bounces = 1
    bpy.ops.mesh.primitive_uv_sphere_add(segments=512, ring_count=256, radius=R, location=(0, 0, 0))
    t = bpy.context.object; t.name = "Tierra"
    bpy.ops.object.shade_smooth()
    m = bpy.data.materials.new("tierra"); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    nrm = nt.nodes.new("ShaderNodeVectorMath"); nrm.operation = "NORMALIZE"; nt.links.new(geo.outputs["Position"], nrm.inputs[0])
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(nrm.outputs[0], sp.inputs[0])
    lon = _op(nt, "MULTIPLY", _op(nt, "ARCTAN2", sp.outputs["Y"], sp.outputs["X"]), 180.0 / math.pi)
    lat = _op(nt, "MULTIPLY", _op(nt, "ARCSINE", sp.outputs["Z"]), 180.0 / math.pi)
    c0 = _imagen(nt, os.path.join(mapas, "world.topo.bathy.200412.3x5400x2700.jpg"),
                 _op(nt, "ADD", _op(nt, "DIVIDE", lon, 360.0), 0.5), _op(nt, "ADD", _op(nt, "DIVIDE", lat, 180.0), 0.5))
    u1 = _op(nt, "DIVIDE", _op(nt, "SUBTRACT", lon, L1[0]), L1[2] - L1[0]); v1 = _op(nt, "DIVIDE", _op(nt, "SUBTRACT", lat, L1[1]), L1[3] - L1[1])
    c1 = _imagen(nt, os.path.join(mapas, "L1_pacifico.jpg"), u1, v1)
    u2 = _op(nt, "DIVIDE", _op(nt, "SUBTRACT", lon, L2[0]), L2[2] - L2[0]); v2 = _op(nt, "DIVIDE", _op(nt, "SUBTRACT", lat, L2[1]), L2[3] - L2[1])
    c2 = _imagen(nt, os.path.join(mapas, "L2_japon.jpg"), u2, v2)
    m1 = nt.nodes.new("ShaderNodeMix"); m1.data_type = "RGBA"
    nt.links.new(_mascara(nt, u1, v1, 0.03), m1.inputs[0]); nt.links.new(c0, m1.inputs[6]); nt.links.new(c1, m1.inputs[7])
    m2 = nt.nodes.new("ShaderNodeMix"); m2.data_type = "RGBA"
    nt.links.new(_mascara(nt, u2, v2, 0.05), m2.inputs[0]); nt.links.new(m1.outputs[2], m2.inputs[6]); nt.links.new(c2, m2.inputs[7])
    # un poco más oscuro y frío que la NASA: es 1945 y una guerra, no una postal
    hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.inputs["Saturation"].default_value = 0.8; hsv.inputs["Value"].default_value = 0.82
    nt.links.new(m2.outputs[2], hsv.inputs["Color"])
    col = hsv.outputs[0]
    nt.links.new(col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.85
    nt.links.new(col, b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = 0.5
    t.data.materials.append(m)
    # atmósfera (halo en el borde)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=256, ring_count=128, radius=R * 1.022)
    atm = bpy.context.object; atm.name = "Atmosfera"; bpy.ops.object.shade_smooth()
    ma = bpy.data.materials.new("atm"); ma.use_nodes = True; na = ma.node_tree
    na.nodes.remove(na.nodes["Principled BSDF"])
    lw = na.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
    fac = _op(na, "POWER", lw.outputs["Facing"], 6.0)
    em = na.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (0.35, 0.62, 1.0, 1); em.inputs[1].default_value = 1.6
    tr = na.nodes.new("ShaderNodeBsdfTransparent")
    ms = na.nodes.new("ShaderNodeMixShader"); na.links.new(fac, ms.inputs[0]); na.links.new(tr.outputs[0], ms.inputs[1]); na.links.new(em.outputs[0], ms.inputs[2])
    na.links.new(ms.outputs[0], na.nodes["Material Output"].inputs[0])
    atm.data.materials.append(ma); atm.visible_shadow = False
    # espacio negro con estrellas finas y un sol de la mañana desde el Pacífico
    wd = bpy.data.worlds.new("espacio"); sc.world = wd; wd.use_nodes = True; nw = wd.node_tree
    tc = nw.nodes.new("ShaderNodeTexCoord"); vor = nw.nodes.new("ShaderNodeTexVoronoi"); vor.inputs["Scale"].default_value = 420.0
    nw.links.new(tc.outputs["Generated"], vor.inputs["Vector"])
    br = _op(nw, "MULTIPLY", _op(nw, "LESS_THAN", vor.outputs["Distance"], 0.05), 1.0)
    cg = nw.nodes.new("ShaderNodeCombineColor"); [nw.links.new(br, cg.inputs[i]) for i in range(3)]
    nw.links.new(cg.outputs[0], nw.nodes["Background"].inputs["Color"])
    bpy.ops.object.light_add(type="SUN")
    sol = bpy.context.object; sol.data.energy = 2.4; sol.data.angle = math.radians(1.0)
    d = xyz(20.0, 160.0).normalized()
    sol.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    return t


def mirar_latlon(cam, lat, lon, alt_km, incl=0.0, rumbo=0.0, lente=35):
    """La cámara sobre (lat, lon) a alt_km; incl > 0 inclina hacia el norte (se ve el horizonte); rumbo gira el norte."""
    p0 = xyz(lat, lon)
    up = p0.normalized()
    n = norte(lat, lon)
    e = n.cross(up)
    a = math.radians(rumbo)
    n2 = n * math.cos(a) + e * math.sin(a)
    i = math.radians(incl)
    pos = p0 + up * (alt_km / 1000.0) * math.cos(i) - n2 * (alt_km / 1000.0) * math.sin(i)
    cam.location = pos
    q = (p0 - pos).to_track_quat("-Z", "Y")
    cam.rotation_mode = "QUATERNION"; cam.rotation_quaternion = q
    # el norte arriba en el cuadro
    bpy.context.view_layer.update()
    cam_up = cam.matrix_world.to_3x3() @ Vector((0, 1, 0))
    ang = math.atan2((cam_up.cross(n2)).dot((p0 - pos).normalized()), cam_up.dot(n2))
    cam.rotation_quaternion = cam.rotation_quaternion @ __import__("mathutils").Quaternion((0, 0, 1), -ang)
    cam.data.lens = lente
    cam.data.clip_start = 0.001; cam.data.clip_end = 100.0
    cam.data.dof.use_dof = False


def puntos(sc, cam, nombres=None):
    """Dónde cae cada lugar en pantalla (1080×1920) y si está del lado visible del globo."""
    out = {}
    for k, (la, lo) in LUGARES.items():
        if nombres and k not in nombres:
            continue
        p = xyz(la, lo, R * 1.001)
        vis = (cam.location - p).dot(p.normalized()) > 0
        x, y = E.pantalla(sc, cam, p)
        out[k] = (x, y) if vis else None
    return out


def lat_lon_pantalla(sc, cam, lat, lon):
    return E.pantalla(sc, cam, xyz(lat, lon, R * 1.001))
