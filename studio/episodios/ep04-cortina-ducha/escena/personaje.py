"""Personaje del Ep. 4: "Don Héctor", hombre de ~45 años (MakeHuman CC0, rig propio con nombres mixamorig:*).

Se ve SIEMPRE de los hombros para arriba, mojado, con espuma de champú en la cabeza y bigote (decisión de Tomás:
nada de desnudos; detrás de la cortina o tapado con espuma). La actuación es procedural (cabeza, cuello, hombros y
expresiones con las 34 shape keys FACS), sin animaciones de Mixamo: así el render no depende del repo privado.

  pj = cargar(sc)                     # trae el personaje a la escena (desde pj/hector.blend)
  pose(pj, f, susto=..., mirar=..., ...)  # pone la pose del cuadro f
"""
import math, os
import bpy
import numpy as np
from mathutils import Vector, Euler, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
BLEND = os.path.join(HERE, "pj", "hector.blend")
P = "mixamorig:"


def _mat(nombre, color, rough=0.5, sss=0.0, coat=0.0, emis=None, alpha=1.0):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Radius"].default_value = (0.6, 0.6, 0.6)
    if coat:
        b.inputs["Coat Weight"].default_value = coat
        b.inputs["Coat Roughness"].default_value = 0.08
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
    return m


def _bigote(rig, cuerpo):
    """Bigote frondoso (dos mechones caídos), hecho con curvas con grosor: oscuro, se lee en vertical."""
    cu = bpy.data.curves.new("Bigote", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 1.0
    cu.bevel_resolution = 4
    cu.resolution_u = 12
    cu.use_fill_caps = True
    for s in (1, -1):
        sp = cu.splines.new("BEZIER")
        sp.bezier_points.add(2)
        pts = [(0.0, -0.1665, 1.5455), (0.021 * s, -0.162, 1.5405), (0.036 * s, -0.150, 1.5225)]
        radios = [0.0085, 0.0075, 0.0032]
        for bp, p, r in zip(sp.bezier_points, pts, radios):
            bp.co = p
            bp.handle_left_type = bp.handle_right_type = "AUTO"
            bp.radius = r
    ob = bpy.data.objects.new("Bigote", cu)
    bpy.context.scene.collection.objects.link(ob)
    ob.scale = (1, 1, 1)
    ob.data.materials.append(_pelo_mat())
    _pegar_a_cabeza(ob, rig)
    return ob


def _pelo_mat():
    m = bpy.data.materials.get("PeloOscuro")
    if m:
        return m
    m = _mat("PeloOscuro", (0.035, 0.025, 0.02), rough=0.55)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    w = nt.nodes.new("ShaderNodeTexWave")          # vetas de pelo
    w.wave_type = "BANDS"
    w.inputs["Scale"].default_value = 180
    w.inputs["Distortion"].default_value = 4
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.5
    nt.links.new(w.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def _cejas(rig):
    """Cejas gruesas y oscuras sobre las pintadas: se leen en el susto (suben con las shape keys de cejas)."""
    obs = []
    for s, lado in ((1, "L"), (-1, "R")):
        cu = bpy.data.curves.new(f"Ceja.{lado}", "CURVE")
        cu.dimensions = "3D"
        cu.bevel_depth = 1.0
        cu.bevel_resolution = 3
        sp = cu.splines.new("BEZIER")
        sp.bezier_points.add(2)
        pts = [(0.012 * s, -0.1515, 1.6305), (0.032 * s, -0.1455, 1.6365), (0.050 * s, -0.1315, 1.6315)]
        for bp, p, r in zip(sp.bezier_points, pts, (0.0042, 0.0046, 0.0026)):
            bp.co = p
            bp.handle_left_type = bp.handle_right_type = "AUTO"
            bp.radius = r
        ob = bpy.data.objects.new(f"Ceja.{lado}", cu)
        bpy.context.scene.collection.objects.link(ob)
        ob.data.materials.append(_pelo_mat())
        ob.scale = (1, 0.55, 1)
        _pegar_a_cabeza(ob, rig)
        obs.append(ob)
    return obs


def _espuma(rig):
    """Espuma de champú en la cabeza: corona de burbujas (metaballs) blancas con algo de translucidez."""
    mb = bpy.data.metaballs.new("Espuma")
    mb.resolution = 0.006
    mb.render_resolution = 0.004
    mb.threshold = 0.6
    rng = np.random.default_rng(4)
    c = Vector((0.0, -0.045, 1.70))
    for i in range(170):          # sobre el cuero cabelludo (elipsoide pegado a la cabeza)
        th = rng.uniform(0, 2 * math.pi)
        ph = rng.uniform(0.0, 1.25)
        p = Vector((0.083 * math.sin(ph) * math.cos(th), -0.045 + 0.10 * math.sin(ph) * math.sin(th), 1.652 + 0.068 * math.cos(ph)))
        e = mb.elements.new()
        e.co = p
        e.radius = rng.uniform(0.014, 0.028)
    # copete de espuma arriba (el chiste: peinado de espuma)
    for k in range(9):
        e = mb.elements.new()
        e.co = c + Vector((0.004 * math.sin(k), -0.02 + 0.006 * k, 0.02 + 0.011 * k))
        e.radius = 0.030 - 0.0022 * k
    ob = bpy.data.objects.new("Espuma", mb)
    bpy.context.scene.collection.objects.link(ob)
    m = _mat("EspumaMat", (0.84, 0.86, 0.88), rough=0.45, sss=0.25)
    b = m.node_tree.nodes["Principled BSDF"]
    nt = m.node_tree
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 260
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    nt.links.new(vor.outputs["Distance"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    ob.data.materials.append(m)
    _pegar_a_cabeza(ob, rig)
    return ob


def _espuma_pecho(rig):
    """Espuma que le tapa el pecho y la espalda (decisión de Tomás: tapado con espuma): un 'poncho' de burbujas."""
    mb = bpy.data.metaballs.new("EspumaPecho")
    mb.resolution = 0.010
    mb.render_resolution = 0.006
    mb.threshold = 0.6
    rng = np.random.default_rng(9)
    for i in range(380):
        z = rng.uniform(1.00, 1.38)
        ang = rng.uniform(0, 2 * math.pi)
        rx = 0.165 + 0.035 * (1.40 - z) / 0.4
        ry = 0.125
        e = mb.elements.new()
        e.co = (rx * math.cos(ang), -0.03 + ry * math.sin(ang), z)
        e.radius = rng.uniform(0.03, 0.05)
    ob = bpy.data.objects.new("EspumaPecho", mb)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(bpy.data.materials["EspumaMat"])
    hb = rig.data.bones[P + "Spine2"]
    mw = ob.matrix_world.copy()
    ob.parent = rig
    ob.parent_type = "BONE"
    ob.parent_bone = P + "Spine2"
    bpy.context.view_layer.update()
    ob.matrix_world = mw
    return ob


def _pegar_a_cabeza(ob, rig):
    hb = rig.data.bones[P + "Head"]
    mw = ob.matrix_world.copy()
    ob.parent = rig
    ob.parent_type = "BONE"
    ob.parent_bone = P + "Head"
    bpy.context.view_layer.update()
    ob.matrix_world = mw


def cargar(sc, x=0.0, y=0.0, z=0.0, rot_z=0.0):
    """Trae el personaje del .blend del episodio a la escena sc. Devuelve un dict con rig, cuerpo y extras."""
    with bpy.data.libraries.load(BLEND, link=False) as (src, dst):
        dst.objects = [n for n in src.objects]
    for ob in dst.objects:
        if ob is not None:
            sc.collection.objects.link(ob)
    rig = bpy.data.objects["Rig"]
    cuerpo = bpy.data.objects["Cuerpo"]
    for n in ("Polera", "Jeans", "Zapatillas"):
        if n in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[n])
    if "Ocultar" in cuerpo.modifiers:
        cuerpo.modifiers.remove(cuerpo.modifiers["Ocultar"])
    # SEGURIDAD (decisión de Tomás: nada de desnudos): el cuerpo bajo el pecho no existe en el render. Si una cámara
    # encuadra de más, se ve un torso cortado (error visible para el auditor), nunca un desnudo.
    vg = cuerpo.vertex_groups.new(name="Visible")
    vg.add([v.index for v in cuerpo.data.vertices if v.co.z > 1.18], 1.0, "REPLACE")
    mk = cuerpo.modifiers.new("SoloPecho", "MASK")
    mk.vertex_group = "Visible"

    # piel morena y mojada (coat), un poco más saturada
    piel = bpy.data.materials["Piel"]
    nt = piel.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes["Image Texture"]
    hsv = nt.nodes.new("ShaderNodeHueSaturation")
    hsv.inputs["Hue"].default_value = 0.49
    hsv.inputs["Saturation"].default_value = 1.10
    hsv.inputs["Value"].default_value = 0.72
    nt.links.new(tex.outputs["Color"], hsv.inputs["Color"])
    nt.links.new(hsv.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Coat Weight"].default_value = 0.35
    b.inputs["Coat Roughness"].default_value = 0.12
    b.inputs["Roughness"].default_value = 0.42
    b.inputs["Subsurface Weight"].default_value = 0.12
    extras = [_bigote(rig, cuerpo), _espuma(rig)] + _cejas(rig)
    extras.append(_espuma_pecho(rig))
    rig.location = (x, y, z)
    rig.rotation_euler = (0, 0, rot_z)
    pb = rig.pose.bones
    for b_ in pb:
        b_.rotation_mode = "XYZ"
    pj = {"rig": rig, "cuerpo": cuerpo, "extras": extras, "pb": pb,
          "keys": cuerpo.data.shape_keys.key_blocks}
    pose(pj, 1)
    return pj


def _rot(pb, nombre, x=0.0, y=0.0, z=0.0):
    b = pb[P + nombre]
    b.rotation_euler = (math.radians(x), math.radians(y), math.radians(z))


EXPR = {
    "neutro": {},
    "susto": {"eye-left-opened-up": 1.0, "eye-right-opened-up": 1.0, "eyebrows-left-up": 1.0, "eyebrows-right-up": 1.0,
              "eyebrows-left-inner-up": 0.8, "eyebrows-right-inner-up": 0.8, "mouth-open": 1.0, "mouth-retraction": 0.4,
              "neck-platysma": 0.7, "nose-left-dilatation": 0.5, "nose-right-dilatation": 0.5},
    "duda": {"eyebrows-left-up": 0.8, "eyebrows-right-down": 0.5, "mouth-pursing": 0.4, "eye-right-slit": 0.3},
    "alivio": {"eye-left-closure": 0.55, "eye-right-closure": 0.55, "mouth-corner-puller": 0.7, "eyebrows-left-inner-up": 0.3,
               "eyebrows-right-inner-up": 0.3},
    "sonrisa": {"mouth-corner-puller": 1.0, "eyebrows-left-up": 0.3, "eyebrows-right-up": 0.3, "mouth-open": 0.15},
    "asco": {"mouth-upward-retraction": 0.7, "nose-left-elevation": 0.8, "nose-right-elevation": 0.8, "eye-left-slit": 0.6,
             "eye-right-slit": 0.6, "eyebrows-left-down": 0.6, "eyebrows-right-down": 0.6},
    "mirar": {"eyebrows-left-up": 0.35, "eyebrows-right-up": 0.35},
}


def pose(pj, f, expr=None, cabeza=(0, 0, 0), cuello=(0, 0, 0), torso=(0, 0, 0), hombros=0.0, parpadeo=0.0, respira=True):
    """Pose del cuadro f. expr = {nombre: peso} (mezcla de EXPR), cabeza/cuello/torso en grados (x: asentir, y: girar, z: ladear),
    hombros: 0 = relajados, 1 = encogidos (susto). Brazos siempre abajo (fuera de cuadro)."""
    pb = pj["pb"]
    for side, s in (("Left", 1), ("Right", -1)):
        pb[P + side + "Arm"].rotation_euler = Euler((math.radians(80), math.radians(6 * s), 0), "XYZ")
        pb[P + side + "ForeArm"].rotation_euler = Euler((0, 0, 0), "XYZ")
        pb[P + side + "Shoulder"].rotation_euler = Euler((math.radians(-16 * hombros), 0, 0), "XYZ")
    resp = math.sin(f / 30 * 2 * math.pi / 3.6) * (1.2 if respira else 0)
    pb[P + "Spine2"].rotation_euler = Euler((math.radians(torso[0] + resp), math.radians(torso[1]), math.radians(torso[2])), "XYZ")
    pb[P + "Neck"].rotation_euler = Euler([math.radians(v) for v in cuello], "XYZ")
    pb[P + "Head"].rotation_euler = Euler([math.radians(v) for v in cabeza], "XYZ")
    keys = pj["keys"]
    pesos = {}
    for nombre, w in (expr or {}).items():
        for k, v in EXPR[nombre].items():
            pesos[k] = pesos.get(k, 0.0) + v * w
    for kb in keys[1:]:
        kb.value = 0.0
    for k, v in pesos.items():
        if k in keys:
            keys[k].value = max(0.0, min(1.0, v))
    if parpadeo:
        for k in ("eye-left-closure", "eye-right-closure"):
            keys[k].value = max(keys[k].value, parpadeo)
    # las cejas de curva siguen a las shape keys de cejas
    up = (pesos.get("eyebrows-left-up", 0) + pesos.get("eyebrows-right-up", 0)) / 2
    dn = (pesos.get("eyebrows-left-down", 0) + pesos.get("eyebrows-right-down", 0)) / 2
    for ob in pj["extras"]:
        if ob.name.startswith("Ceja"):
            ob.delta_location = (0, 0, 0.0055 * up - 0.003 * dn)


def parpadeo(f, cada=95, fase=0):
    """Parpadeo natural: 1 en el cierre, cada ~3 s."""
    k = (f + fase) % cada
    return max(0.0, 1 - abs(k - 3) / 3) if k < 7 else 0.0
