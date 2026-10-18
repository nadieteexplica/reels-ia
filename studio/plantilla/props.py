"""Utilería y escenarios reutilizables (todo procedural, sin assets externos)."""
import math
import bmesh
import bpy
import numpy as np
from mathutils import Vector, Matrix

# ---------------- materiales ----------------
PAL = {
    "coral": (1.0, 0.16, 0.10), "turquesa": (0.0, 0.50, 0.52), "blanco": (0.86, 0.86, 0.84),
    "amarillo": (1.0, 0.62, 0.04), "negro": (0.02, 0.02, 0.022), "crema": (0.92, 0.80, 0.60),
    "frutilla": (0.92, 0.22, 0.32), "chocolate": (0.10, 0.035, 0.015), "vainilla": (0.95, 0.80, 0.52),
    "menta": (0.30, 0.78, 0.52), "galleta": (0.62, 0.30, 0.08), "pasto": (0.12, 0.42, 0.10),
    "hoja": (0.10, 0.45, 0.12), "tronco": (0.20, 0.10, 0.05), "cielo": (0.20, 0.55, 0.95),
}


def mat(name, color=None, rough=0.5, metal=0.0, emit=0.0, sss=0.0, coat=0.0, alpha=1.0, transmission=0.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    col = PAL.get(color, color) if isinstance(color, str) else (color or (0.8, 0.8, 0.8))
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*col, 1)
        b.inputs["Emission Strength"].default_value = emit
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Scale"].default_value = 0.02
    if coat:
        b.inputs["Coat Weight"].default_value = coat
    if transmission:
        b.inputs["Transmission Weight"].default_value = transmission
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
    return m


def nodes(m):
    return m.node_tree.nodes, m.node_tree.links, m.node_tree.nodes["Principled BSDF"]


def link(ob, coll=None):
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def collection(name, parent=None):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in [x.name for x in (parent or bpy.context.scene.collection).children]:
        (parent or bpy.context.scene.collection).children.link(c)
    return c


def mesh_obj(name, bm, coll=None, smooth=True, m=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    link(ob, coll)
    if m:
        me.materials.append(m)
    return ob


def prim(kind, name, coll=None, m=None, smooth=True, **kw):
    bm = bmesh.new()
    if kind == "cube":
        bmesh.ops.create_cube(bm, size=1.0)
    elif kind == "cyl":
        bmesh.ops.create_cone(bm, cap_ends=True, segments=kw.pop("seg", 48), radius1=kw.pop("r", 0.5), radius2=kw.pop("r2", kw.get("r_top", 0.5)), depth=kw.pop("h", 1.0))
        kw.pop("r_top", None)
    elif kind == "sphere":
        bmesh.ops.create_uvsphere(bm, u_segments=kw.pop("u", 48), v_segments=kw.pop("v", 24), radius=kw.pop("r", 0.5))
    elif kind == "ico":
        bmesh.ops.create_icosphere(bm, subdivisions=kw.pop("sub", 4), radius=kw.pop("r", 0.5))
    elif kind == "torus":
        R, r = kw.pop("R", 0.5), kw.pop("r", 0.1)
        bm.free()
        bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=48, minor_segments=16)
        ob = bpy.context.active_object
        ob.name = name
        for c in ob.users_collection:
            c.objects.unlink(ob)
        link(ob, coll)
        if m:
            ob.data.materials.append(m)
        bpy.ops.object.shade_smooth()
        return ob
    ob = mesh_obj(name, bm, coll, smooth=smooth, m=m)
    return ob


def bevel(ob, w=0.02, seg=3):
    b = ob.modifiers.new("Bevel", "BEVEL")
    b.width, b.segments = w, seg
    b.limit_method = "ANGLE"
    return b


def place(ob, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None):
    ob.location, ob.rotation_euler, ob.scale = loc, rot, scale
    if parent:
        ob.parent = parent
    return ob


def empty(name, loc=(0, 0, 0), coll=None, parent=None):
    e = bpy.data.objects.new(name, None)
    link(e, coll)
    e.location = loc
    if parent:
        e.parent = parent
    return e


FONTS = __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "fonts")


def text3d(name, body, size=0.3, extrude=0.03, bevel_d=0.006, font=None, coll=None, m=None, align="CENTER"):
    font = font or __import__("os").path.join(FONTS, "Inter-Black.otf")
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.font = bpy.data.fonts.load(font, check_existing=True)
    cu.size, cu.extrude, cu.bevel_depth = size, extrude, bevel_d
    cu.align_x, cu.align_y = align, "CENTER"
    ob = bpy.data.objects.new(name, cu)
    link(ob, coll)
    if m:
        cu.materials.append(m)
    return ob


def tube(name, pts, radius, coll=None, m=None, res=12):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth, cu.bevel_resolution = radius, 4
    cu.use_fill_caps = True
    sp = cu.splines.new("NURBS")
    sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts):
        p.co = (*q, 1)
    sp.use_endpoint_u = True
    sp.order_u = min(4, len(pts))
    sp.resolution_u = res
    ob = bpy.data.objects.new(name, cu)
    link(ob, coll)
    if m:
        cu.materials.append(m)
    return ob


# ---------------- helado ----------------
def scoop(name, color, r=0.045, coll=None, seed=0):
    ob = prim("ico", name, coll, m=mat("Helado_" + color, color, rough=0.55, sss=0.25, coat=0.15), sub=4, r=r)
    d = ob.modifiers.new("Bultos", "DISPLACE")
    tx = bpy.data.textures.new(name + "_tx", "CLOUDS")
    tx.noise_scale = 0.35
    tx.noise_depth = 2
    d.texture, d.strength, d.mid_level = tx, r * 0.18, 0.5
    # rulo de borde ("labio" del helado al servir con cuchara)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=False, segments=40, radius1=r * 1.08, radius2=r * 1.0, depth=r * 0.25)
    for v in bm.verts:
        a = math.atan2(v.co.y, v.co.x)
        v.co.z += math.sin(a * 7 + seed) * r * 0.06
        v.co.z -= r * 0.45
    lip = mesh_obj(name + "_borde", bm, coll, m=ob.data.materials[0])
    sol = lip.modifiers.new("S", "SOLIDIFY")
    sol.thickness = r * 0.12
    lip.modifiers.new("Sub", "SUBSURF").levels = 1
    lip.parent = ob
    ob.modifiers.new("Sub", "SUBSURF").render_levels = 1
    return ob


def cone(name="Cono", scale=1.0, flavors=("frutilla", "chocolate", "vainilla"), coll=None):
    """Cono de galleta con bolas apiladas. Origen = punta del cono (para tomarlo con la mano)."""
    root = empty(name, coll=coll)
    h, r = 0.15 * scale, 0.042 * scale
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=0.002, radius2=r, depth=h)
    bmesh.ops.translate(bm, vec=(0, 0, h / 2), verts=bm.verts)
    m = mat("Galleta", "galleta", rough=0.7)
    # textura de waffle: dos familias de rayas en diagonal
    nt, lk, b = nodes(m)
    if not any(n.type == "TEX_WAVE" for n in nt):
        tc = nt.new("ShaderNodeTexCoord")
        w1, w2 = nt.new("ShaderNodeTexWave"), nt.new("ShaderNodeTexWave")
        for w, rot in ((w1, 1.0), (w2, -1.0)):
            w.wave_profile = "TRI"
            w.inputs["Scale"].default_value = 9.0
            mp = nt.new("ShaderNodeMapping")
            mp.inputs["Rotation"].default_value = (0, 0, 0.78 * rot)
            lk.new(tc.outputs["Object"], mp.inputs["Vector"])
            lk.new(mp.outputs["Vector"], w.inputs["Vector"])
        mx = nt.new("ShaderNodeMath")
        mx.operation = "MINIMUM"
        lk.new(w1.outputs["Fac"], mx.inputs[0])
        lk.new(w2.outputs["Fac"], mx.inputs[1])
        bp = nt.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = 0.6
        lk.new(mx.outputs[0], bp.inputs["Height"])
        lk.new(bp.outputs["Normal"], b.inputs["Normal"])
        ramp = nt.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (0.33, 0.13, 0.03, 1)
        ramp.color_ramp.elements[1].color = (0.72, 0.38, 0.12, 1)
        lk.new(mx.outputs[0], ramp.inputs["Fac"])
        lk.new(ramp.outputs["Color"], b.inputs["Base Color"])
    c = mesh_obj(name + "_galleta", bm, coll, m=m)
    c.parent = root
    scoops = []
    z = h + 0.018 * scale
    for i, fl in enumerate(flavors):
        rr = (0.046 - 0.004 * i) * scale
        s = scoop(f"{name}_bola{i}", fl, rr, coll, seed=i)
        s.parent = root
        s.location = (0.004 * (i % 2) * scale, 0, z + rr * 0.55)
        z += rr * 1.45
        scoops.append(s)
    root["bolas"] = [s.name for s in scoops]
    return root, c, scoops


# ---------------- carrito de helados ----------------
def stripes_mat(name, c1, c2, n=8, mode="angle"):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = mat(name, c1, rough=0.6)
    nt, lk, b = nodes(m)
    tc = nt.new("ShaderNodeTexCoord")
    sep = nt.new("ShaderNodeSeparateXYZ")
    lk.new(tc.outputs["Object"], sep.inputs[0])
    if mode == "angle":
        at = nt.new("ShaderNodeMath")
        at.operation = "ARCTAN2"
        lk.new(sep.outputs["Y"], at.inputs[0])
        lk.new(sep.outputs["X"], at.inputs[1])
        mul = nt.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = n / (2 * math.pi)
        lk.new(at.outputs[0], mul.inputs[0])
    else:
        mul = nt.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = n
        lk.new(sep.outputs["X"], mul.inputs[0])
    fr = nt.new("ShaderNodeMath")
    fr.operation = "FRACT"
    lk.new(mul.outputs[0], fr.inputs[0])
    gt = nt.new("ShaderNodeMath")
    gt.operation = "GREATER_THAN"
    gt.inputs[1].default_value = 0.5
    lk.new(fr.outputs[0], gt.inputs[0])
    mix = nt.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*PAL.get(c1, c1), 1)
    mix.inputs["B"].default_value = (*PAL.get(c2, c2), 1)
    lk.new(gt.outputs[0], mix.inputs["Factor"])
    lk.new(mix.outputs["Result"], b.inputs["Base Color"])
    return m


def cart(coll=None, loc=(0, 0, 0), rot_z=0.0):
    root = empty("Carrito", loc=loc, coll=coll)
    root.rotation_euler.z = rot_z
    body = prim("cube", "Carrito_cuerpo", coll, m=mat("CarroCoral", "coral", rough=0.35, coat=0.6))
    place(body, (0, 0, 0.66), scale=(1.25, 0.62, 0.62), parent=root)
    bevel(body, 0.06, 4)
    band = prim("cube", "Carrito_franja", coll, m=mat("CarroBlanco", "blanco", rough=0.35, coat=0.5))
    place(band, (0, 0, 0.83), scale=(1.27, 0.64, 0.09), parent=root)
    bevel(band, 0.03, 3)
    top = prim("cube", "Carrito_tapa", coll, m=mat("CarroCromo", (0.8, 0.8, 0.82), rough=0.18, metal=1.0))
    place(top, (0, 0, 0.985), scale=(1.30, 0.67, 0.05), parent=root)
    bevel(top, 0.02, 3)
    # pocillos de helado en la tapa
    for i, fl in enumerate(("frutilla", "chocolate", "vainilla", "menta")):
        x = -0.45 + i * 0.30
        tub = prim("cyl", f"Pocillo{i}", coll, m=mat("CarroCromo", None), r=0.11, r2=0.11, h=0.06)
        place(tub, (x, -0.08, 1.02), parent=root)
        mound = prim("ico", f"Monton{i}", coll, m=mat("Helado_" + fl, fl, rough=0.55, sss=0.25, coat=0.15), sub=3, r=0.10)
        place(mound, (x, -0.08, 1.04), scale=(1, 1, 0.55), parent=root)
        d = mound.modifiers.new("Bultos", "DISPLACE")
        tx = bpy.data.textures.get("BultosHelado") or bpy.data.textures.new("BultosHelado", "CLOUDS")
        tx.noise_scale = 0.08
        d.texture, d.strength = tx, 0.03
        mound.modifiers.new("Sub", "SUBSURF").render_levels = 1
    # letrero frontal
    sign = text3d("Carrito_letrero", "HELADOS", size=0.19, extrude=0.008, coll=coll, m=mat("LetraBlanca", "blanco", rough=0.4))
    place(sign, (-0.12, -0.325, 0.62), rot=(math.pi / 2, 0, 0), parent=root)
    # ruedas (un eje) y patas
    for sy in (-1, 1):
        tire = prim("torus", f"Rueda{sy}", coll, m=mat("Goma", "negro", rough=0.8), R=0.2, r=0.055)
        place(tire, (0.32, sy * 0.36, 0.255), rot=(math.pi / 2, 0, 0), parent=root)
        hub = prim("cyl", f"Maza{sy}", coll, m=mat("CarroBlanco", None), r=0.15, r2=0.15, h=0.05)
        place(hub, (0.32, sy * 0.36, 0.255), rot=(math.pi / 2, 0, 0), parent=root)
        leg = prim("cyl", f"Pata{sy}", coll, m=mat("CarroCromo", None), r=0.025, r2=0.025, h=0.36)
        place(leg, (-0.5, sy * 0.24, 0.18), parent=root)
    # manillar
    h = tube("Carrito_manillar", [(0.66, 0.25, 0.85), (0.86, 0.25, 0.95), (0.86, -0.25, 0.95), (0.66, -0.25, 0.85)], 0.018, coll, m=mat("CarroCromo", None))
    h.parent = root
    # quitasol
    pole = prim("cyl", "Quitasol_palo", coll, m=mat("CarroCromo", None), r=0.02, r2=0.02, h=1.45)
    place(pole, (0, 0.05, 1.72), parent=root)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=False, segments=64, radius1=1.0, radius2=0.03, depth=0.38)
    for v in bm.verts:  # ondas en el borde
        if v.co.z < 0:
            a = math.atan2(v.co.y, v.co.x)
            v.co.z += 0.025 * abs(math.sin(a * 4))
    um = mesh_obj("Quitasol", bm, coll, m=stripes_mat("Rayas", "turquesa", "blanco", n=8))
    um.modifiers.new("S", "SOLIDIFY").thickness = 0.01
    um.modifiers.new("Sub", "SUBSURF").render_levels = 1
    place(um, (0, 0.05, 2.38), parent=root)
    knob = prim("sphere", "Quitasol_punta", coll, m=mat("CarroBlanco", None), r=0.035)
    place(knob, (0, 0.05, 2.58), parent=root)
    return root


def menu_board(coll=None, loc=(0, 0, 0)):
    """Cartel con 3 tamaños de cono (S, M, XL). Devuelve (raíz, cono XL)."""
    root = empty("Cartel", loc=loc, coll=coll)
    board = prim("cube", "Cartel_tabla", coll, m=mat("CartelCrema", "crema", rough=0.6))
    place(board, (0, 0, 1.25), scale=(0.95, 0.05, 0.62), parent=root)
    bevel(board, 0.03, 3)
    frame = prim("cube", "Cartel_marco", coll, m=mat("CarroCoral", None))
    place(frame, (0, 0.012, 1.25), scale=(1.02, 0.04, 0.69), parent=root)
    bevel(frame, 0.03, 3)
    for sx in (-1, 1):
        leg = prim("cyl", f"Cartel_pata{sx}", coll, m=mat("CarroCromo", None), r=0.015, r2=0.015, h=0.95)
        place(leg, (sx * 0.4, 0.02, 0.47), parent=root)
    xl = None
    for i, (lab, s) in enumerate((("S", 0.55), ("M", 0.8), ("XL", 1.15))):
        c, _, _ = cone(f"CartelCono{lab}", scale=s, coll=coll)
        c.parent = root
        c.location = (-0.3 + i * 0.3, -0.05, 1.02)
        t = text3d(f"CartelTxt{lab}", lab, size=0.13, extrude=0.008, coll=coll, m=mat("LetraCoral", "coral", rough=0.4))
        place(t, (-0.3 + i * 0.3, -0.04, 1.44), rot=(math.pi / 2, 0, 0), parent=root)
        if lab == "XL":
            xl = c
    return root, xl


# ---------------- plaza ----------------
def tree(name, loc, s=1.0, coll=None, seed=0):
    rng = np.random.default_rng(seed)
    root = empty(name, loc=loc, coll=coll)
    tr = prim("cyl", name + "_tronco", coll, m=mat("Tronco", "tronco", rough=0.9), r=0.12 * s, r2=0.08 * s, h=2.2 * s)
    place(tr, (0, 0, 1.1 * s), parent=root)
    leaf = mat("Hoja", "hoja", rough=0.7, sss=0.1)
    for k in range(7):
        b = prim("ico", f"{name}_copa{k}", coll, m=leaf, sub=3, r=(0.7 + 0.3 * rng.random()) * s)
        a = k / 7 * 2 * math.pi
        rr = 0.55 * s if k else 0
        place(b, (rr * math.cos(a), rr * math.sin(a), (2.6 + 0.5 * rng.random()) * s), parent=root)
        d = b.modifiers.new("Bultos", "DISPLACE")
        tx = bpy.data.textures.get("BultosHoja") or bpy.data.textures.new("BultosHoja", "CLOUDS")
        tx.noise_scale = 0.4
        d.texture, d.strength = tx, 0.25 * s
        b.modifiers.new("Sub", "SUBSURF").render_levels = 1
    return root


def plaza(coll=None):
    root = empty("Plaza", coll=coll)
    # piso de baldosas
    fl = prim("cube", "Plaza_piso", coll)
    place(fl, (0, 6, -0.05), scale=(70, 70, 0.1), parent=root)
    m = mat("Baldosa", (0.75, 0.62, 0.48), rough=0.8)
    nt, lk, b = nodes(m)
    tc = nt.new("ShaderNodeTexCoord")
    br = nt.new("ShaderNodeTexBrick")
    br.inputs["Color1"].default_value = (0.42, 0.26, 0.16, 1)
    br.inputs["Color2"].default_value = (0.36, 0.21, 0.13, 1)
    br.inputs["Mortar"].default_value = (0.25, 0.17, 0.12, 1)
    br.inputs["Scale"].default_value = 1.6
    br.inputs["Mortar Size"].default_value = 0.012
    lk.new(tc.outputs["Object"], br.inputs["Vector"])
    lk.new(br.outputs["Color"], b.inputs["Base Color"])
    bp = nt.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.25
    bp.invert = True
    lk.new(br.outputs["Fac"], bp.inputs["Height"])
    lk.new(bp.outputs["Normal"], b.inputs["Normal"])
    fl.data.materials.append(m)
    # pasto
    gm = mat("Pasto", "pasto", rough=0.9)
    for i, (x, y, sx, sy) in enumerate(((-6, 7, 4, 3), (6.5, 9, 4.5, 3.5), (0, 16, 12, 3))):
        g = prim("cyl", f"Pasto{i}", coll, m=gm, r=1, r2=1, h=0.06)
        place(g, (x, y, 0.0), scale=(sx, sy, 1), parent=root)
        bevel(g, 0.03, 2)
    # árboles
    for i, (x, y, s) in enumerate(((-5.5, 7.5, 1.0), (-7.5, 10, 1.25), (6, 8.5, 1.1), (8.5, 11, 1.3), (-2, 16, 1.2), (3, 15.5, 1.0))):
        tree(f"Arbol{i}", (x, y, 0), s, coll, seed=i)
    # edificios pastel al fondo
    pastel = [(0.90, 0.55, 0.25), (0.20, 0.62, 0.70), (0.95, 0.35, 0.30), (0.85, 0.75, 0.30), (0.45, 0.50, 0.90)]
    for i in range(9):
        bld = prim("cube", f"Edificio{i}", coll, m=mat(f"Pastel{i % 5}", pastel[i % 5], rough=0.8))
        h = 5 + 4 * ((i * 37) % 7) / 7
        place(bld, (-18 + i * 4.5, 22 + (i % 2) * 2, h / 2), scale=(4.2, 3, h), parent=root)
        bevel(bld, 0.05, 2)
    # banca y farol
    seat = mat("Madera", (0.45, 0.22, 0.08), rough=0.6)
    for k in range(3):
        sl = prim("cube", f"Banca_tabla{k}", coll, m=seat)
        place(sl, (-2.6, 2.6 + k * 0.13, 0.45), scale=(1.6, 0.1, 0.04), parent=root)
        bevel(sl, 0.01, 2)
    lamp = prim("cyl", "Farol", coll, m=mat("FarolNegro", (0.05, 0.08, 0.1), rough=0.4, metal=0.6), r=0.05, r2=0.04, h=3.2)
    place(lamp, (3.2, 3.5, 1.6), parent=root)
    bulb = prim("sphere", "Farol_globo", coll, m=mat("Globo", (0.95, 0.95, 0.9), rough=0.3), r=0.18)
    place(bulb, (3.2, 3.5, 3.3), parent=root)
    return root


def sun_and_sky(strength=2.6):
    sc = bpy.context.scene
    L = bpy.data.lights.get("Sol") or bpy.data.lights.new("Sol", "SUN")
    L.energy, L.color, L.angle = strength, (1.0, 0.94, 0.84), math.radians(3)
    ob = bpy.data.objects.get("Sol") or bpy.data.objects.new("Sol", L)
    if ob.name not in sc.collection.objects:
        sc.collection.objects.link(ob)
    ob.rotation_euler = (math.radians(50), 0, math.radians(-35))
    w = sc.world
    nt = w.node_tree
    bg = nt.nodes["Background"]
    # cielo con degradado vertical
    if not any(n.type == "VALTORGB" for n in nt.nodes):
        tc = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.0
        ramp.color_ramp.elements[0].color = (0.30, 0.62, 0.90, 1)
        ramp.color_ramp.elements[1].position = 0.5
        ramp.color_ramp.elements[1].color = (0.03, 0.22, 0.75, 1)
        nt.links.new(tc.outputs["Generated"], sep.inputs[0])
        nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.55
    return ob
