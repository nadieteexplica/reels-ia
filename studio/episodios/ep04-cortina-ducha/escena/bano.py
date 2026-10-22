"""Set del Ep. 4: el baño con tina, ducha en la pared del fondo y cortina (semi-realista, look R4: azulejos celestes,
luz suave de estudio, colores saturados).

Ejes: Z arriba. La tina va a lo largo de X (x -0,85 a 0,85). Pared del fondo (con la ducha) en y = +0,40; la cortina
cuelga del riel en y = -0,40 (lado del baño). Adentro de la tina el piso está en z = 0,12; el borde, en z = 0,55.

  S = armar(sc, corte=False, cortina="liviana")   # set completo
  deformar_cortina(S, f, inflar=0..1, objetivo=[obs], ...)   # la cortina se mete hacia adentro (y +)
  gotas(S, t, caliente=0..1) · remolino(S, t, fuerza) · vapor(S, t, caliente)   # partículas
"""
import math
import bpy
import bmesh
import numpy as np
from mathutils import Vector, Matrix, Euler
from mathutils.bvhtree import BVHTree

X0, X1 = -0.85, 0.85
Y_PARED, Y_CORT = 0.40, -0.40
Z_PISO, Z_BORDE, Z_RIEL = 0.12, 0.55, 2.02
DUCHA = Vector((0.0, 0.33, 1.98))          # boca de la ducha (en la pared del fondo, al centro)


# ---------------- materiales ----------------
def _bsdf(m):
    return m.node_tree.nodes["Principled BSDF"]


def mat(nombre, color, rough=0.5, metal=0.0, emis=0.0, alpha=1.0, trans=0.0, coat=0.0):
    m = bpy.data.materials.get(nombre) or bpy.data.materials.new(nombre)
    m.use_nodes = True
    b = _bsdf(m)
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emis:
        b.inputs["Emission Color"].default_value = (*color, 1)
        b.inputs["Emission Strength"].default_value = emis
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
    if trans:
        b.inputs["Transmission Weight"].default_value = trans
    if coat:
        b.inputs["Coat Weight"].default_value = coat
    return m


def mat_azulejo():
    m = bpy.data.materials.new("Azulejo")
    m.use_nodes = True
    nt = m.node_tree
    b = _bsdf(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1, 1, 1)
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.inputs["Scale"].default_value = 6.6
    br.inputs["Mortar Size"].default_value = 0.012
    br.inputs["Brick Width"].default_value = 0.5
    br.inputs["Row Height"].default_value = 0.25
    br.offset = 0.5
    br.inputs["Color1"].default_value = (0.10, 0.50, 0.58, 1)
    br.inputs["Color2"].default_value = (0.13, 0.56, 0.63, 1)
    br.inputs["Mortar"].default_value = (0.78, 0.85, 0.85, 1)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    # el ladrillo de Blender usa x,y: las paredes se mapean con (x o y, z)
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    com = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(mp.outputs["Vector"], sep.inputs["Vector"])
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    nt.links.new(sep.outputs["X"], add.inputs[0])
    nt.links.new(sep.outputs["Y"], add.inputs[1])
    nt.links.new(add.outputs[0], com.inputs["X"])
    nt.links.new(sep.outputs["Z"], com.inputs["Y"])
    nt.links.new(com.outputs["Vector"], br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.18
    b.inputs["Coat Weight"].default_value = 0.4
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.25
    bump.invert = True
    nt.links.new(br.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def mat_cortina(pesada=False):
    """Cortina blanca con franjas verde menta y lunares: liviana = plástico translúcido (se ve la silueta);
    pesada = tela gruesa opaca con la misma estampa (el loop empalma)."""
    m = bpy.data.materials.new("CortinaPesada" if pesada else "Cortina")
    m.use_nodes = True
    nt = m.node_tree
    b = _bsdf(m)
    out = nt.nodes["Material Output"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["UV"], sep.inputs["Vector"])
    # franjas verticales (en u) + lunares
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 9.0
    nt.links.new(sep.outputs["X"], mul.inputs[0])
    fr = nt.nodes.new("ShaderNodeMath"); fr.operation = "PINGPONG"; fr.inputs[1].default_value = 0.5
    nt.links.new(mul.outputs[0], fr.inputs[0])
    st = nt.nodes.new("ShaderNodeMath"); st.operation = "GREATER_THAN"; st.inputs[1].default_value = 0.30
    nt.links.new(fr.outputs[0], st.inputs[0])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (0.72, 0.86, 0.80, 1)
    mix.inputs["B"].default_value = (0.10, 0.52, 0.46, 1)
    nt.links.new(st.outputs[0], mix.inputs["Factor"])
    b.inputs["Roughness"].default_value = 0.65 if pesada else 0.32
    if pesada:
        b.inputs["Sheen Weight"].default_value = 0.6
        nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
        noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 900
        bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.25
        nt.links.new(noise.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    else:
        nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
        b.inputs["Coat Weight"].default_value = 0.3
        tr = nt.nodes.new("ShaderNodeBsdfTranslucent")
        nt.links.new(mix.outputs["Result"], tr.inputs["Color"])
        ms = nt.nodes.new("ShaderNodeMixShader")
        ms.inputs["Fac"].default_value = 0.30
        nt.links.new(b.outputs["BSDF"], ms.inputs[1])
        nt.links.new(tr.outputs["BSDF"], ms.inputs[2])
        nt.links.new(ms.outputs["Shader"], out.inputs["Surface"])
    return m


# ---------------- utilería ----------------
def caja(nombre, a, b, material, bisel=0.0):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(a + b) / 2)
    ob = bpy.context.active_object
    ob.name = nombre
    ob.scale = (b - a)
    bpy.ops.object.transform_apply(scale=True)
    if bisel:
        bv = ob.modifiers.new("Bisel", "BEVEL")
        bv.width, bv.segments = bisel, 3
    ob.data.materials.append(material)
    return ob


def tina(blanco, corte_x=None):
    """Tina de cerámica: caja con el interior vaciado y bordes redondeados. corte_x: corta todo lo que está en x > corte_x."""
    ext = caja("Tina", (X0, Y_CORT - 0.06, 0.0), (X1, Y_PARED, Z_BORDE), blanco, bisel=0.03)
    hueco = caja("TinaHueco", (X0 + 0.07, Y_CORT + 0.02, Z_PISO), (X1 - 0.07, Y_PARED - 0.07, Z_BORDE + 0.3), blanco, bisel=0.06)
    bo = ext.modifiers.new("Hueco", "BOOLEAN")
    bo.object, bo.operation = hueco, "DIFFERENCE"
    hueco.display_type = "WIRE"
    hueco.hide_render = True
    bpy.context.view_layer.objects.active = ext
    bpy.ops.object.modifier_apply(modifier="Hueco")
    bpy.data.objects.remove(hueco)
    return ext


def pato(blanco, amarillo, naranjo, loc):
    """Patito de goma (genérico, propio): cuerpo, cabeza, pico, ojos."""
    raiz = bpy.data.objects.new("Pato", None)
    bpy.context.scene.collection.objects.link(raiz)
    raiz.location = loc
    partes = []
    for nombre, l, r, s, mt in (("PatoCuerpo", (0, 0, 0.032), 0.045, (1.25, 1.0, 0.75), amarillo),
                                ("PatoCabeza", (0.035, 0, 0.078), 0.028, (1, 1, 1), amarillo),
                                ("PatoPico", (0.065, 0, 0.073), 0.012, (1.6, 1.1, 0.55), naranjo),
                                ("PatoPupilaL", (0.055, 0.014, 0.088), 0.0045, (1, 1, 1), mat("PatoOjo", (0.02, 0.02, 0.03), 0.2)),
                                ("PatoPupilaR", (0.055, -0.014, 0.088), 0.0045, (1, 1, 1), mat("PatoOjo", (0.02, 0.02, 0.03), 0.2))):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=l, segments=24, ring_count=12)
        ob = bpy.context.active_object
        ob.name = nombre
        ob.scale = s
        bpy.ops.object.shade_smooth()
        ob.data.materials.append(mt)
        ob.parent = raiz
        partes.append(ob)
    # cola
    bpy.ops.mesh.primitive_cone_add(radius1=0.02, depth=0.04, location=(-0.05, 0, 0.05), rotation=(0, math.radians(-60), 0))
    c = bpy.context.active_object
    c.name = "PatoCola"
    c.data.materials.append(amarillo)
    c.parent = raiz
    return raiz


def botella(nombre, loc, color, alto=0.2, r=0.035):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=alto, location=(loc[0], loc[1], loc[2] + alto / 2), vertices=32)
    ob = bpy.context.active_object
    ob.name = nombre
    bv = ob.modifiers.new("Bisel", "BEVEL"); bv.width, bv.segments = r * 0.5, 4
    ob.data.materials.append(mat(nombre + "Mat", color, rough=0.25, coat=0.5))
    bpy.ops.mesh.primitive_cylinder_add(radius=r * 0.55, depth=0.03, location=(loc[0], loc[1], loc[2] + alto + 0.015), vertices=24)
    t = bpy.context.active_object
    t.name = nombre + "Tapa"
    t.data.materials.append(mat("TapaBlanca", (0.95, 0.95, 0.95), 0.3))
    t.parent = ob
    t.matrix_parent_inverse = ob.matrix_world.inverted()
    return ob


# ---------------- partículas por instancias (puntos + Geometry Nodes) ----------------
def nube(nombre, n, proto):
    """Objeto de n puntos que instancia `proto` en cada punto, con rotación ("rot") y escala ("esc") por punto."""
    me = bpy.data.meshes.new(nombre)
    me.from_pydata([(0, 0, -50)] * n, [], [])
    for a in ("rot", "esc"):
        me.attributes.new(a, "FLOAT_VECTOR", "POINT")
    ob = bpy.data.objects.new(nombre, me)
    bpy.context.scene.collection.objects.link(ob)
    ng = bpy.data.node_groups.new(nombre + "GN", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    gi = ng.nodes.new("NodeGroupInput")
    go = ng.nodes.new("NodeGroupOutput")
    iop = ng.nodes.new("GeometryNodeInstanceOnPoints")
    oi = ng.nodes.new("GeometryNodeObjectInfo")
    oi.inputs["As Instance"].default_value = True
    oi.inputs["Object"].default_value = proto
    nr = ng.nodes.new("GeometryNodeInputNamedAttribute"); nr.data_type = "FLOAT_VECTOR"; nr.inputs["Name"].default_value = "rot"
    ns = ng.nodes.new("GeometryNodeInputNamedAttribute"); ns.data_type = "FLOAT_VECTOR"; ns.inputs["Name"].default_value = "esc"
    ng.links.new(gi.outputs[0], iop.inputs["Points"])
    ng.links.new(oi.outputs["Geometry"], iop.inputs["Instance"])
    ng.links.new(nr.outputs["Attribute"], iop.inputs["Rotation"])
    ng.links.new(ns.outputs["Attribute"], iop.inputs["Scale"])
    ng.links.new(iop.outputs["Instances"], go.inputs[0])
    md = ob.modifiers.new("GN", "NODES")
    md.node_group = ng
    proto.location = (0, 0, -60)        # el prototipo queda lejos y fuera de cuadro
    return ob


def poner(ob, pos, rot, esc):
    me = ob.data
    n = len(me.vertices)
    pos = np.asarray(pos, dtype=np.float32).reshape(-1, 3)
    k = len(pos)
    P = np.full((n, 3), (0, 0, -50), np.float32); P[:k] = pos
    R = np.zeros((n, 3), np.float32); R[:k] = np.asarray(rot, np.float32).reshape(-1, 3)
    E = np.zeros((n, 3), np.float32); E[:k] = np.asarray(esc, np.float32).reshape(-1, 3)
    me.vertices.foreach_set("co", P.ravel())
    me.attributes["rot"].data.foreach_set("vector", R.ravel())
    me.attributes["esc"].data.foreach_set("vector", E.ravel())
    me.update()


def _alinear(v):
    """Euler (XYZ) que lleva el eje Z local a la dirección v (para gotas y estelas alargadas)."""
    out = np.zeros((len(v), 3), np.float32)
    for i, d in enumerate(v):
        d = Vector(d)
        if d.length < 1e-6:
            continue
        out[i] = d.to_track_quat("Z", "Y").to_euler()
    return out


# ---------------- set ----------------
def armar(sc, corte=False, cortina="liviana", pato_en=None):
    S = {"sc": sc}
    blanco = mat("Ceramica", (0.80, 0.82, 0.82), rough=0.14, coat=0.5)
    cromo = mat("Cromo", (0.9, 0.9, 0.92), rough=0.08, metal=1.0)
    azulejo = mat_azulejo()
    piso = mat("PisoBano", (0.55, 0.60, 0.62), rough=0.35)
    S["paredes"] = []
    fondo = caja("ParedFondo", (X0 - 0.6, Y_PARED, 0.0), (X1 + 0.6, Y_PARED + 0.12, 2.9), azulejo)
    izq = caja("ParedIzq", (X0 - 0.12, Y_CORT - 1.6, 0.0), (X0, Y_PARED + 0.12, 2.9), azulejo)
    S["paredes"] += [fondo, izq]
    if not corte:
        der = caja("ParedDer", (X1, Y_CORT - 1.6, 0.0), (X1 + 0.12, Y_PARED + 0.12, 2.9), azulejo)
        S["paredes"].append(der)
    caja("Piso", (X0 - 2, Y_CORT - 3, -0.02), (X1 + 2, Y_PARED + 0.2, 0.0), piso)
    S["tina"] = tina(blanco)
    # ducha: brazo y cabezal cromados en la pared del fondo
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.16, location=(DUCHA.x, Y_PARED - 0.07, DUCHA.z + 0.05),
                                        rotation=(math.radians(70), 0, 0))
    brazo = bpy.context.active_object; brazo.name = "DuchaBrazo"; brazo.data.materials.append(cromo)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.025, location=(DUCHA.x, DUCHA.y - 0.02, DUCHA.z),
                                        rotation=(math.radians(-35), 0, 0), vertices=48)
    cab = bpy.context.active_object; cab.name = "Ducha"; cab.data.materials.append(cromo)
    bv = cab.modifiers.new("Bisel", "BEVEL"); bv.width, bv.segments = 0.008, 3
    # llave (mezcladora) con marca roja/azul
    bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.05, location=(0.0, Y_PARED - 0.02, 1.15), rotation=(math.radians(90), 0, 0))
    llave = bpy.context.active_object; llave.name = "Llave"; llave.data.materials.append(cromo)
    # riel y argollas
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=X1 - X0 + 0.24, location=(0, Y_CORT, Z_RIEL), rotation=(0, math.radians(90), 0))
    riel = bpy.context.active_object; riel.name = "Riel"; riel.data.materials.append(cromo)
    S["argollas"] = []
    for i in range(14):
        x = X0 + 0.04 + i * (X1 - X0 - 0.08) / 13
        bpy.ops.mesh.primitive_torus_add(major_radius=0.022, minor_radius=0.0035, location=(x, Y_CORT, Z_RIEL - 0.008), rotation=(0, math.radians(90), 0))
        a = bpy.context.active_object; a.name = f"Argolla{i}"; a.data.materials.append(cromo)
        S["argollas"].append(a)
    # repisa con champú (pared izquierda) y patito en el borde de la tina
    caja("Repisa", (X0, 0.05, 1.10), (X0 + 0.14, 0.36, 1.125), blanco, bisel=0.005)
    S["botellas"] = [botella("Champu", (X0 + 0.06, 0.12, 1.125), (0.95, 0.35, 0.55), 0.21),
                     botella("Bálsamo", (X0 + 0.07, 0.24, 1.125), (0.35, 0.55, 0.95), 0.17, 0.03)]
    amarillo = mat("PatoAmarillo", (1.0, 0.78, 0.05), rough=0.3, coat=0.4)
    naranjo = mat("PatoNaranjo", (1.0, 0.38, 0.05), rough=0.35)
    S["pato"] = pato(blanco, amarillo, naranjo, pato_en or (X0 + 0.20, Y_PARED - 0.05, Z_BORDE))
    # cortina
    S["cortina"] = crear_cortina(pesada=(cortina == "pesada"), corte=corte)
    # luz: ventana cálida + relleno frío + contorno
    S["luces"] = luces(sc)
    mundo(sc)
    return S


def crear_cortina(pesada=False, corte=False, nx=96, nz=84):
    x1 = 0.30 if corte else X1 + 0.06
    xs = np.linspace(X0 - 0.06, x1, nx)
    zs = np.linspace(0.30 if not pesada else 0.26, Z_RIEL - 0.03, nz)
    verts = [(x, Y_CORT, z) for z in zs for x in xs]
    caras = [(j * nx + i, j * nx + i + 1, (j + 1) * nx + i + 1, (j + 1) * nx + i) for j in range(nz - 1) for i in range(nx - 1)]
    me = bpy.data.meshes.new("Cortina")
    me.from_pydata(verts, [], caras)
    uv = me.uv_layers.new(name="UV")
    for poly in me.polygons:
        for li, vi in zip(poly.loop_indices, poly.vertices):
            i, j = vi % nx, vi // nx
            uv.data[li].uv = (i / (nx - 1) * (x1 - X0) / 1.0, j / (nz - 1))
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    ob = bpy.data.objects.new("Cortina", me)
    bpy.context.scene.collection.objects.link(ob)
    so = ob.modifiers.new("Grosor", "SOLIDIFY"); so.thickness = 0.008 if pesada else 0.0015
    sub = ob.modifiers.new("Sub", "SUBSURF"); sub.levels = sub.render_levels = 1
    if corte:      # en el corte: la misma estampa, sin translucidez; su Alpha baja para "ver por dentro"
        m = mat_cortina(pesada)
        b = _bsdf(m)
        out = m.node_tree.nodes["Material Output"]
        m.node_tree.links.new(b.outputs["BSDF"], out.inputs["Surface"])
        ob.data.materials.append(m)
        ob["mat_alpha"] = m.name
    else:
        ob.data.materials.append(mat_cortina(pesada))
    base = np.array(verts, np.float32)
    ob["pesada"] = pesada
    return {"ob": ob, "base": base, "nx": nx, "nz": nz, "pesada": pesada}


def deformar_cortina(C, f, inflar=0.0, centro=(0.0, 1.05), radio=(0.55, 0.45), aleteo=1.0, objetivos=(), cara=None,
                     empuje_cara=0.0, cara_dentro=False, tope_y=None):
    """Pone la forma de la cortina en el cuadro f.
    inflar: cuánto se mete hacia adentro (m, hacia +y) en el centro (x, z) del bulto; aleteo: ondas chicas de aire.
    objetivos: objetos contra los que la cortina se pega (la cabeza: no los atraviesa, se moldea encima).
    cara/empuje_cara: (x, z) y profundidad de una 'cara' que empuja desde afuera (el fantasma del cierre)."""
    t = f / 30.0
    B = C["base"].copy()
    x, z = B[:, 0], B[:, 2]
    ztop = Z_RIEL - 0.03
    pesada = C["pesada"]
    # pliegues de colgar (más hondos en la pesada)
    amp = 0.022 if pesada else 0.016
    y = Y_CORT + amp * np.sin(x * (2 * math.pi / 0.16)) * (0.6 + 0.4 * (z - 0.3) / (ztop - 0.3))
    # el borde de abajo cuelga adentro de la tina (más adentro cuando se infla)
    colg = np.clip((ztop - z) / (ztop - 0.3), 0, 1)
    g = np.exp(-((x - centro[0]) / radio[0]) ** 2 - ((z - centro[1]) / radio[1]) ** 2)
    bulto = inflar * g * np.clip(colg * 4.0, 0, 1) ** 0.6
    fl = aleteo * (0.006 if pesada else 0.018) * np.sin(x * 9 + t * 7.3) * np.sin(z * 6 - t * 5.1) * np.clip(colg * 2, 0, 1)
    fl += aleteo * (0.004 if pesada else 0.012) * np.sin(x * 23 - t * 11) * colg
    y = y + bulto + fl * (0.4 + inflar * 3)
    if cara is not None and empuje_cara > 0:
        cx, cz = cara
        r = np.hypot((x - cx) / 0.11, (z - cz) / 0.14)
        cabeza = np.clip(1 - r ** 2, 0, None) ** 0.5
        nariz = np.exp(-((x - cx) / 0.018) ** 2 - ((z - cz + 0.01) / 0.03) ** 2) * 0.35
        ojos = -0.65 * (np.exp(-((x - cx - 0.036) / 0.022) ** 2 - ((z - cz - 0.035) / 0.02) ** 2)
                        + np.exp(-((x - cx + 0.036) / 0.022) ** 2 - ((z - cz - 0.035) / 0.02) ** 2))
        boca = -0.75 * np.exp(-((x - cx) / 0.026) ** 2 - ((z - cz + 0.065) / 0.032) ** 2)     # boca en "O" (¡uuuh!)
        relieve = empuje_cara * (cabeza + nariz + ojos + boca) * np.clip(r < 1.25, 0, 1) + empuje_cara * 0.35 * np.exp(-r ** 2 / 3)
    else:
        relieve = 0.0
    if tope_y is not None:                 # la cortina no pasa de aquí (no atraviesa al personaje)
        y = np.where(y > tope_y, tope_y - 0.02 * np.tanh((y - tope_y) * 8), y)
    y = y - relieve if cara_dentro else y + relieve
    P = np.stack([x, y, z], 1)
    # pegarse a la cabeza: lo que quedaría adentro se pone en la superficie (+ 6 mm)
    if objetivos:
        dg = bpy.context.evaluated_depsgraph_get()
        for ob in objetivos:
            ev = ob.evaluated_get(dg)
            try:
                bvh = BVHTree.FromObject(ev, dg)
            except Exception:
                continue
            Mi = ob.matrix_world.inverted()
            M = ob.matrix_world
            bb = [M @ Vector(c) for c in ob.bound_box]
            lo = np.min(np.array(bb), 0) - 0.05
            hi = np.max(np.array(bb), 0) + 0.05
            cerca = np.where(np.all((P[:, [0, 2]] > lo[[0, 2]]) & (P[:, [0, 2]] < hi[[0, 2]]), 1) & (P[:, 1] > lo[1]))[0]
            d_loc = (Mi.to_3x3() @ Vector((0, 1, 0))).normalized()
            for i in cerca:
                o = Mi @ Vector((P[i][0], Y_CORT - 0.3, P[i][2]))       # rayo desde afuera de la cortina hacia adentro
                loc, nor, _idx, dist = bvh.ray_cast(o, d_loc, 2.0)
                if loc is None:
                    continue
                q = M @ loc
                if P[i][1] > q.y - 0.006:
                    P[i][1] = q.y - 0.006
    me = C["ob"].data
    me.vertices.foreach_set("co", P.astype(np.float32).ravel())
    me.update()


def luces(sc):
    def area(nombre, loc, tgt, e, size, col):
        L = bpy.data.lights.new(nombre, "AREA")
        L.energy, L.size, L.color = e, size, col
        o = bpy.data.objects.new(nombre, L)
        sc.collection.objects.link(o)
        o.location = loc
        o.rotation_mode = "QUATERNION"
        o.rotation_quaternion = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y")
        return o
    return {"techo": area("LuzTecho", (0, -0.1, 2.75), (0, 0, 1.0), 230, 1.4, (1.0, 0.90, 0.76)),
            "relleno": area("LuzRelleno", (0.4, -2.2, 1.7), (0, 0, 1.3), 140, 2.5, (0.85, 0.92, 1.0)),
            "contra": area("LuzContra", (-0.6, 1.2, 2.4), (0, 0, 1.4), 120, 0.8, (0.8, 0.95, 1.0))}


def mundo(sc):
    w = bpy.data.worlds.new("Mundo")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.72, 0.78, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.25


# ---------------- agua, aire y vapor ----------------
def sistema_agua(n_gotas=900, n_aire=700, n_vapor=40):
    gota_m = mat("Gota", (0.80, 0.92, 1.0), rough=0.05, emis=0.25)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=1.0, subdivisions=2)
    g = bpy.context.active_object; g.name = "ProtoGota"; g.data.materials.append(gota_m)
    aire_m = mat("Aire", (0.0, 0.62, 1.0), rough=0.5, emis=2.2)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=1.0, subdivisions=2)
    a = bpy.context.active_object; a.name = "ProtoAire"; a.data.materials.append(aire_m)
    vap_m = mat("Vapor", (1.0, 1.0, 1.0), rough=1.0, alpha=0.05)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=1.0, subdivisions=3)
    v = bpy.context.active_object; v.name = "ProtoVapor"; v.data.materials.append(vap_m)
    bpy.ops.object.shade_smooth()
    return {"gotas": nube("Gotas", n_gotas, g), "aire": nube("AireNube", n_aire, a), "vapor": nube("VaporNube", n_vapor, v),
            "mat_gota": gota_m, "mat_aire": aire_m, "mat_vapor": vap_m, "n": (n_gotas, n_aire, n_vapor)}


def gotas(A, t, caliente=1.0, x_lim=(-0.8, 0.8), densidad=1.0):
    """Chorro de la ducha: gotas que salen del cabezal en cono y caen (cada una con su fase)."""
    n = A["n"][0]
    rng = np.random.default_rng(7)
    fase = rng.uniform(0, 1, n)
    ang = rng.uniform(0, 2 * math.pi, n)
    ab = rng.uniform(0, 0.35, n) ** 0.7
    vida = 0.55
    tau = ((t / vida + fase) % 1.0) * vida
    v0 = 3.2
    d = np.stack([np.sin(ab) * np.cos(ang), -np.cos(ab) * 0.55 - 0.35 + np.sin(ab) * np.sin(ang) * 0.4, -np.cos(ab)], 1)
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    p = np.array(DUCHA) + d * v0 * tau[:, None] + np.array([0, 0, -4.9]) * (tau ** 2)[:, None]
    vel = d * v0 + np.array([0, 0, -9.8]) * tau[:, None]
    vivo = (p[:, 2] > Z_PISO + 0.01) & (rng.uniform(0, 1, n) < densidad) & (p[:, 0] > x_lim[0]) & (p[:, 0] < x_lim[1]) & (p[:, 1] > Y_CORT + 0.12)
    p, vel = p[vivo], vel[vivo]
    esc = np.tile([0.0035, 0.0035, 0.022], (len(p), 1))
    poner(A["gotas"], p, _alinear(vel), esc)
    m = A["mat_gota"]
    col = (0.55 + 0.45 * caliente, 0.82 - 0.40 * caliente, 1.0 - 0.70 * caliente)
    _bsdf(m).inputs["Base Color"].default_value = (*col, 1)
    _bsdf(m).inputs["Emission Color"].default_value = (*col, 1)


def remolino(A, t, fuerza=1.0, centro=(-0.30, 1.12), y_lim=(-0.30, 0.24), giro=1.0, visible=1.0, brillo=2.2, rmax=0.38):
    """El remolino acostado: su eje es PERPENDICULAR a la cortina (a lo largo de y, de la pared a la cortina; Schmidt en
    Scientific American), así que la rueda gira en el plano XZ, paralela a la cortina. centro = (x, z).
    Sentido: baja por el lado del chorro (x mayor), sube por el otro lado."""
    n = A["n"][1]
    rng = np.random.default_rng(11)
    r = 0.05 + (rmax - 0.05) * np.sqrt(rng.uniform(0, 1, n))
    th0 = rng.uniform(0, 2 * math.pi, n)
    ys = rng.uniform(y_lim[0], y_lim[1], n)
    w = 2.6 * giro * (0.32 / (r + 0.10))
    th = th0 - w * t * fuerza                         # horario visto desde afuera: baja por el lado del chorro
    xc, zc = centro
    x = xc + r * np.cos(th)
    z = zc + r * np.sin(th)
    p = np.stack([x, ys, z], 1)
    tang = np.stack([r * np.sin(th), np.zeros(n), -r * np.cos(th)], 1)
    sel = rng.uniform(0, 1, n) < visible
    largo = 0.010 + 0.05 * fuerza
    esc = np.stack([np.full(n, 0.006), np.full(n, 0.006), np.full(n, largo)], 1)
    poner(A["aire"], p[sel], _alinear(tang[sel]), esc[sel])
    _bsdf(A["mat_aire"]).inputs["Emission Strength"].default_value = brillo * min(1.0, fuerza + 0.15)


def vapor(A, t, caliente=1.0):
    """Vapor del agua caliente: bolitas blandas que suben y se abren; con agua fría se va."""
    n = A["n"][2]
    rng = np.random.default_rng(3)
    fase = rng.uniform(0, 1, n)
    x = rng.uniform(-0.45, 0.25, n)
    vida = 2.5
    tau = ((t / vida + fase) % 1.0)
    y = 0.22 - 0.25 * tau + 0.04 * np.sin(t * 2 + fase * 9)
    z = 1.1 + 1.0 * tau
    s = 0.03 + 0.09 * tau
    vivo = rng.uniform(0, 1, n) < caliente
    p = np.stack([x, y, z], 1)[vivo]
    esc = np.stack([s, s, s], 1)[vivo]
    poner(A["vapor"], p, np.zeros((len(p), 3)), esc)
    _bsdf(A["mat_vapor"]).inputs["Alpha"].default_value = 0.05 * caliente
