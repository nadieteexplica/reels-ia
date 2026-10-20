"""Personajes del Ep. 2, hechos para esta idea (dibujo animado 3D, propios, sin assets externos):
- Cuitlacoche (curve-billed thrasher, el pájaro del estudio de Arizona): gris café, pecho moteado, ojos naranjos, pico largo curvo.
- Ratón del cactus: canela con guata blanca, orejas enormes, ojos negros grandes.

Cada personaje es una raíz vacía con su esqueleto simple (huesos con nombre) y partes con nombre fijo, para animar por clave.
Origen = entre las patas, en el suelo; miran hacia -Y.
"""
import math
import bmesh
import bpy
from mathutils import Vector, Quaternion, Euler, Matrix

import props as P


# ---------------- utilidades ----------------
def metaball_mesh(name, elementos, coll, res=0.0035, thresh=0.6):
    """elementos: [(tipo, centro, radio, (sx, sy, sz), rot_euler_grados, stiffness)] → malla suave."""
    mb = bpy.data.metaballs.new(name + "_mb")
    mb.resolution = res
    mb.render_resolution = res
    mb.threshold = thresh
    for tipo, co, r, s, rot, st in elementos:
        e = mb.elements.new()
        e.type = tipo
        e.co = co
        e.radius = r
        if tipo == "ELLIPSOID":
            e.size_x, e.size_y, e.size_z = s
        e.rotation = Euler([math.radians(a) for a in rot]).to_quaternion()
        e.stiffness = st
    ob = bpy.data.objects.new(name + "_tmp", mb)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    bpy.data.metaballs.remove(mb)
    me.name = name
    out = bpy.data.objects.new(name, me)
    coll.objects.link(out)
    for p in me.polygons:
        p.use_smooth = True
    sm = out.modifiers.new("Suave", "CORRECTIVE_SMOOTH")
    sm.iterations = 8
    sm.smooth_type = "LENGTH_WEIGHTED"
    return out


def blob(name, elipsoides, coll, voxel=0.0007, suave=24):
    """elipsoides: [(centro, radios(x,y,z), rot_euler_grados)] → una sola malla orgánica (unión por voxeles + suavizado).
    Las uniones quedan redondeadas como plastilina; la malla final no tiene modificadores."""
    bm = bmesh.new()
    for co, rad, rot in elipsoides:
        tmp = bmesh.new()
        bmesh.ops.create_uvsphere(tmp, u_segments=40, v_segments=20, radius=1.0)
        M = Matrix.Translation(Vector(co)) @ Euler([math.radians(a) for a in rot]).to_matrix().to_4x4() @ Matrix.Diagonal((*rad, 1.0))
        bmesh.ops.transform(tmp, matrix=M, verts=tmp.verts)
        me_t = bpy.data.meshes.new("t")
        tmp.to_mesh(me_t)
        tmp.free()
        bm.from_mesh(me_t)
        bpy.data.meshes.remove(me_t)
    me = bpy.data.meshes.new(name + "_crudo")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name + "_tmp", me)
    bpy.context.scene.collection.objects.link(ob)
    r = ob.modifiers.new("Remesh", "REMESH")
    r.mode = "VOXEL"
    r.voxel_size = voxel
    r.adaptivity = 0.0
    sm = ob.modifiers.new("Suave", "SMOOTH")
    sm.factor = 1.0
    sm.iterations = suave
    sd = ob.modifiers.new("Sub", "SUBSURF")
    sd.levels = sd.render_levels = 1
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me2 = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    bpy.data.meshes.remove(me)
    me2.name = name
    out = bpy.data.objects.new(name, me2)
    coll.objects.link(out)
    for p in me2.polygons:
        p.use_smooth = True
    return out


def cuerno(name, base, direccion, curva_hacia, largo, r0, r1=0.0006, coll=None, m=None, curv=0.35, n=24, seg=20, aplastar=1.0):
    """Cono curvo (pico, garra): parte en `base`, avanza por `direccion` y se curva hacia `curva_hacia`."""
    d = Vector(direccion).normalized()
    c = Vector(curva_hacia).normalized()
    bm = bmesh.new()
    rings = []
    for i in range(n + 1):
        t = i / n
        ang = curv * t
        eje = (d * math.cos(ang) + c * math.sin(ang)).normalized()
        pos = Vector(base) + (d * math.sin(curv * t) / max(curv, 1e-4) + c * (1 - math.cos(curv * t)) / max(curv, 1e-4)) * largo if curv > 1e-4 \
            else Vector(base) + d * largo * t
        r = r0 + (r1 - r0) * t ** 0.9
        lado = eje.cross(c).normalized() if abs(eje.dot(c)) < 0.99 else eje.orthogonal().normalized()
        arr = lado.cross(eje).normalized()
        ring = [bm.verts.new(pos + (lado * math.cos(2 * math.pi * j / seg) + arr * math.sin(2 * math.pi * j / seg) * aplastar) * r) for j in range(seg)]
        rings.append(ring)
    for i in range(n):
        for j in range(seg):
            bm.faces.new((rings[i][j], rings[i][(j + 1) % seg], rings[i + 1][(j + 1) % seg], rings[i + 1][j]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    return P.mesh_obj(name, bm, coll, m=m)


def esfera(name, centro, radio, coll, m, escala=(1, 1, 1), seg=48):
    ob = P.prim("sphere", name, coll, m, r=radio, u=seg, v=seg // 2)
    ob.location = centro
    ob.scale = escala
    return ob


def ojo(name, centro, radio, mirar, coll, iris_col, iris_frac=0.62, pupila_frac=0.42):
    """Ojo de dibujo animado: globo con iris y pupila pintados en el shader (mirando hacia `mirar`) y brillo propio."""
    m = bpy.data.materials.new(name + "_mat")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.05
    b.inputs["Coat Weight"].default_value = 1.0
    b.inputs["Coat Roughness"].default_value = 0.02
    tc = nt.nodes.new("ShaderNodeTexCoord")
    # distancia angular al eje de la mirada (coordenadas del objeto: -Y local = mirada)
    dot = nt.nodes.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    dot.inputs[1].default_value = (0, -1, 0)
    nrm = nt.nodes.new("ShaderNodeVectorMath")
    nrm.operation = "NORMALIZE"
    nt.links.new(tc.outputs["Object"], nrm.inputs[0])
    nt.links.new(nrm.outputs["Vector"], dot.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.interpolation = "EASE"
    c_iris = math.cos(math.radians(70 * iris_frac))
    c_pup = math.cos(math.radians(70 * pupila_frac * iris_frac / 0.62))
    cr.elements[0].position = 0.0
    cr.elements[0].color = (0.92, 0.90, 0.86, 1)       # blanco (casi no se ve en el pájaro)
    cr.elements[1].position = 1.0
    cr.elements[1].color = (0.01, 0.008, 0.006, 1)
    e = cr.elements.new(c_iris - 0.02)
    e.color = (0.92, 0.90, 0.86, 1)
    e = cr.elements.new(c_iris)
    e.color = (*[x * 0.55 for x in iris_col], 1)
    e = cr.elements.new((c_iris + c_pup) / 2)
    e.color = (*iris_col, 1)
    e = cr.elements.new(c_pup - 0.004)
    e.color = (*[x * 0.8 for x in iris_col], 1)
    e = cr.elements.new(c_pup)
    e.color = (0.01, 0.008, 0.006, 1)
    nt.links.new(dot.outputs["Value"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    ob = esfera(name, centro, radio, coll, m, seg=64)
    d = (Vector(mirar) - Vector(centro)).normalized()
    ob.rotation_euler = d.to_track_quat("-Y", "Z").to_euler()
    return ob


def parpado(name, ojo_ob, radio, coll, m, abierto=0.0):
    """Párpado: casquete un poco más grande que el ojo; rotando en X baja y cierra (rot 0 = abierto)."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=radio * 1.08)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -radio * 0.05], context="VERTS")
    ob = P.mesh_obj(name, bm, coll, m=m)
    s = ob.modifiers.new("Grosor", "SOLIDIFY")
    s.thickness = radio * 0.08
    ob.parent = ojo_ob          # pivote con la orientación del ojo: -Y local = mirada
    ob.location = (0, 0, 0)
    ob.rotation_euler = (math.radians(-100 + 100 * abierto), 0, 0)
    return ob


# ---------------- materiales ----------------
def mat_plumas():
    m = bpy.data.materials.get("Plumas")
    if m:
        return m
    m = bpy.data.materials.new("Plumas")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.62
    b.inputs["Sheen Weight"].default_value = 0.6
    b.inputs["Sheen Roughness"].default_value = 0.35
    b.inputs["Sheen Tint"].default_value = (1.0, 0.95, 0.88, 1)
    b.inputs["Subsurface Weight"].default_value = 0.08
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    # pecho más claro y moteado: zona de adelante y abajo (y < 0, z bajo) en coordenadas del objeto
    sepn = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Normal"], sepn.inputs[0])     # normal en espacio del objeto: el pecho no "nada" al girar
    vm = nt.nodes.new("ShaderNodeMath")
    vm.operation = "MULTIPLY"
    vm.inputs[1].default_value = -1.0
    nt.links.new(sepn.outputs["Y"], vm.inputs[0])
    vm2 = nt.nodes.new("ShaderNodeMath")
    vm2.operation = "MULTIPLY"
    vm2.inputs[1].default_value = -0.8
    nt.links.new(sepn.outputs["Z"], vm2.inputs[0])
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    nt.links.new(vm.outputs[0], add.inputs[0])
    nt.links.new(vm2.outputs[0], add.inputs[1])
    pecho = nt.nodes.new("ShaderNodeMapRange")
    pecho.inputs["From Min"].default_value = 0.25
    pecho.inputs["From Max"].default_value = 0.85
    nt.links.new(add.outputs[0], pecho.inputs["Value"])
    base = nt.nodes.new("ShaderNodeMix")
    base.data_type = "RGBA"
    base.inputs["A"].default_value = (0.095, 0.068, 0.050, 1)    # lomo gris café
    base.inputs["B"].default_value = (0.36, 0.27, 0.19, 1)     # pecho beige grisáceo
    nt.links.new(pecho.outputs["Result"], base.inputs["Factor"])
    # motas del pecho (voronoi)
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 95.0
    vor.inputs["Randomness"].default_value = 0.8
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
    mot = nt.nodes.new("ShaderNodeMapRange")
    mot.inputs["From Min"].default_value = 0.10
    mot.inputs["From Max"].default_value = 0.22
    mot.inputs["To Min"].default_value = 1.0
    mot.inputs["To Max"].default_value = 0.0
    nt.links.new(vor.outputs["Distance"], mot.inputs["Value"])
    mm = nt.nodes.new("ShaderNodeMath")
    mm.operation = "MULTIPLY"
    nt.links.new(mot.outputs["Result"], mm.inputs[0])
    nt.links.new(pecho.outputs["Result"], mm.inputs[1])
    mm2 = nt.nodes.new("ShaderNodeMath")
    mm2.operation = "MULTIPLY"
    mm2.inputs[1].default_value = 0.22
    nt.links.new(mm.outputs[0], mm2.inputs[0])
    spots = nt.nodes.new("ShaderNodeMix")
    spots.data_type = "RGBA"
    spots.inputs["B"].default_value = (0.12, 0.09, 0.07, 1)
    nt.links.new(base.outputs["Result"], spots.inputs["A"])
    nt.links.new(mm2.outputs[0], spots.inputs["Factor"])
    # textura de plumas: ondas suaves
    wav = nt.nodes.new("ShaderNodeTexWave")
    wav.wave_type = "RINGS"
    wav.inputs["Scale"].default_value = 26.0
    wav.inputs["Distortion"].default_value = 3.0
    nt.links.new(tc.outputs["Object"], wav.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.05
    bump.inputs["Distance"].default_value = 0.001
    nt.links.new(wav.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    nt.links.new(spots.outputs["Result"], b.inputs["Base Color"])
    return m


def mat_simple(name, col, rough=0.5, sheen=0.0, sss=0.0, coat=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Sheen Weight"].default_value = sheen
    b.inputs["Subsurface Weight"].default_value = sss
    b.inputs["Coat Weight"].default_value = coat
    return m


# ---------------- cuitlacoche ----------------
def colgar(hijo, padre):
    """Emparenta sin mover (guarda la posición en el mundo)."""
    bpy.context.view_layer.update()
    mw = hijo.matrix_world.copy()
    hijo.parent = padre
    hijo.matrix_parent_inverse = padre.matrix_world.inverted()
    hijo.matrix_world = mw
    return hijo


def pajaro(coll, nombre="Cuitlacoche"):
    """Cuitlacoche de dibujo animado: cuerpo de huevo, cabeza grande, ojos naranjos, pico largo curvo, patas cortas.
    ~0,20 m de alto. Construido en el origen mirando a -Y. Devuelve la raíz y los pivotes animables."""
    root = P.empty(nombre, coll=coll)
    plum = mat_plumas()
    oscuro = mat_simple("PlumaOscura", (0.055, 0.042, 0.035), rough=0.6, sheen=0.5)
    clara = mat_simple("PlumaClara", (0.80, 0.76, 0.70), rough=0.6, sheen=0.5)
    pico_m = mat_simple("Pico", (0.03, 0.027, 0.025), rough=0.28, coat=0.5)
    pata_m = mat_simple("Pata", (0.09, 0.08, 0.075), rough=0.45)
    cuerpo = blob(nombre + "_cuerpo", [
        ((0, 0.012, 0.088), (0.046, 0.066, 0.048), (-20, 0, 0)),     # cuerpo (huevo)
        ((0, -0.012, 0.074), (0.043, 0.046, 0.043), (0, 0, 0)),      # guata
        ((0, -0.030, 0.112), (0.033, 0.030, 0.034), (0, 0, 0)),      # cuello
        ((0, 0.062, 0.094), (0.030, 0.040, 0.026), (-15, 0, 0)),     # rabadilla
    ], coll)
    cuerpo.data.materials.append(plum)
    colgar(cuerpo, root)
    cabeza_c = Vector((0, -0.046, 0.142))
    piv_cab = P.empty(nombre + "_piv_cabeza", loc=(0, -0.030, 0.112), coll=coll)
    colgar(piv_cab, root)
    cabeza = blob(nombre + "_cabeza", [
        (tuple(cabeza_c), (0.043, 0.042, 0.041), (0, 0, 0)),
        (tuple(cabeza_c + Vector((0, 0.010, -0.024))), (0.032, 0.030, 0.028), (0, 0, 0)),
    ], coll)
    cabeza.data.materials.append(plum)
    colgar(cabeza, piv_cab)
    pb = cabeza_c + Vector((0, -0.036, -0.006))
    piv_pico = P.empty(nombre + "_piv_pico", loc=pb, coll=coll)
    colgar(piv_pico, piv_cab)
    sup = cuerno(nombre + "_pico_sup", pb, (0, -1, 0.06), (0, 0, -1), 0.072, 0.0105, 0.0008, coll, pico_m, curv=0.6, aplastar=0.78)
    colgar(sup, piv_pico)
    piv_inf = P.empty(nombre + "_piv_mandibula", loc=pb + Vector((0, 0.002, -0.004)), coll=coll)
    colgar(piv_inf, piv_pico)
    inf = cuerno(nombre + "_pico_inf", pb + Vector((0, 0.001, -0.0055)), (0, -1, -0.05), (0, 0, -1), 0.060, 0.0078, 0.0008, coll, pico_m, curv=0.5, aplastar=0.62)
    colgar(inf, piv_inf)
    ojos, parps = [], []
    for s in (-1, 1):
        oc = cabeza_c + Vector((s * 0.026, -0.026, 0.010))
        o = ojo(f"{nombre}_ojo{'LR'[s > 0]}", oc, 0.0150, oc + Vector((s * 0.5, -1.0, 0.03)), coll, (1.0, 0.42, 0.03), iris_frac=0.80, pupila_frac=0.36)
        colgar(o, piv_cab)
        pv = P.empty(f"{nombre}_piv_parpado{'LR'[s > 0]}", loc=oc, coll=coll)
        pv.rotation_euler = o.rotation_euler.copy()
        colgar(pv, piv_cab)
        parpado(f"{nombre}_parpado{'LR'[s > 0]}", pv, 0.0150, coll, plum)
        ojos.append(o)
        parps.append(pv)
    alas = []
    for s in (-1, 1):
        piv = P.empty(f"{nombre}_piv_ala{'LR'[s > 0]}", loc=(s * 0.036, -0.012, 0.110), coll=coll)
        colgar(piv, root)
        a = blob(f"{nombre}_ala{'LR'[s > 0]}", [
            ((s * 0.040, 0.020, 0.095), (0.011, 0.056, 0.030), (-22, s * 6, 0)),
            ((s * 0.036, 0.070, 0.080), (0.008, 0.030, 0.016), (-28, s * 4, 0)),
        ], coll, voxel=0.0009, suave=8)
        a.data.materials.append(oscuro)
        colgar(a, piv)
        alas.append(piv)
    piv_cola = P.empty(nombre + "_piv_cola", loc=(0, 0.080, 0.090), coll=coll)
    colgar(piv_cola, root)
    cola = blob(nombre + "_cola", [((0, 0.140, 0.064), (0.024, 0.078, 0.007), (26, 0, 0)), ((0, 0.205, 0.035), (0.028, 0.020, 0.006), (26, 0, 0))], coll, voxel=0.0007, suave=8)
    cola.data.materials.append(oscuro)
    colgar(cola, piv_cola)
    for s in (-1, 1):
        x = s * 0.016
        pierna = P.tube(f"{nombre}_pata{'LR'[s > 0]}", [(x, 0.002, 0.052), (x, -0.002, 0.026), (x, 0.0, 0.004)], 0.0030, coll, pata_m)
        colgar(pierna, root)
        for ang in (-32, 0, 32, 180):
            d = Vector((math.sin(math.radians(ang)), -math.cos(math.radians(ang)), 0))
            L = 0.020 if ang != 180 else 0.012
            dedo = P.tube(f"{nombre}_dedo{'LR'[s > 0]}{ang}", [(x, 0.0, 0.004), tuple(Vector((x, 0, 0.003)) + d * L * 0.6), tuple(Vector((x, 0, 0.0016)) + d * L)], 0.0017, coll, pata_m)
            colgar(dedo, root)
    return {"root": root, "cuerpo": cuerpo, "cabeza": piv_cab, "pico": piv_pico, "mandibula": piv_inf, "ojos": ojos, "parpados": parps,
            "alas": alas, "cola": piv_cola, "punta_pico": pb + Vector((0, -0.068, -0.022))}


# ---------------- ratón del cactus ----------------
def mat_pelaje(nombre="Pelaje", lomo=(0.42, 0.20, 0.08), guata=(0.86, 0.82, 0.76)):
    """Pelaje con guata clara (máscara por la normal del objeto: adelante/abajo = guata)."""
    m = bpy.data.materials.get(nombre)
    if m:
        return m
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.7
    b.inputs["Sheen Weight"].default_value = 0.9
    b.inputs["Sheen Roughness"].default_value = 0.3
    b.inputs["Subsurface Weight"].default_value = 0.12
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Normal"], sep.inputs[0])
    vm = nt.nodes.new("ShaderNodeMath")
    vm.operation = "MULTIPLY_ADD"          # -Ny*1.0 + (-Nz)*0.9
    vm.inputs[1].default_value = -1.0
    nz = nt.nodes.new("ShaderNodeMath")
    nz.operation = "MULTIPLY"
    nz.inputs[1].default_value = -0.35
    nt.links.new(sep.outputs["Z"], nz.inputs[0])
    nt.links.new(sep.outputs["Y"], vm.inputs[0])
    nt.links.new(nz.outputs[0], vm.inputs[2])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.72
    mr.inputs["From Max"].default_value = 0.95
    nt.links.new(vm.outputs[0], mr.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*lomo, 1)
    mix.inputs["B"].default_value = (*guata, 1)
    nt.links.new(mr.outputs["Result"], mix.inputs["Factor"])
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    nz2 = nt.nodes.new("ShaderNodeTexNoise")
    nz2.inputs["Scale"].default_value = 400.0
    nz2.inputs["Detail"].default_value = 2.0
    nt.links.new(tc.outputs["Object"], nz2.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.08
    bump.inputs["Distance"].default_value = 0.0005
    nt.links.new(nz2.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def raton(coll, nombre="Raton", lomo=(0.42, 0.20, 0.08), guata=(0.86, 0.82, 0.76), oreja=0.026, hocico=1.0):
    """Ratón del cactus de dibujo animado, sentado sobre las patas traseras (pose de comer). ~0,16 m de alto sentado.
    Construido en el origen mirando a -Y. Devuelve la raíz y los pivotes animables: cabeza, orejas, ojos, párpados, boca, brazos, cola."""
    root = P.empty(nombre, coll=coll)
    pel = mat_pelaje(nombre + "_pelaje", lomo, guata)
    canela = mat_simple(nombre + "_lomo", lomo, rough=0.7, sheen=0.9)
    rosado = mat_simple("RosadoRaton", (0.85, 0.42, 0.42), rough=0.5, sss=0.5)
    oreja_in = mat_simple("OrejaDentro", (0.80, 0.30, 0.32), rough=0.55, sss=0.15)
    nariz_m = mat_simple("NarizRaton", (0.75, 0.22, 0.26), rough=0.25, coat=0.6)
    boca_m = mat_simple("BocaRaton", (0.12, 0.02, 0.02), rough=0.6)
    diente_m = mat_simple("Diente", (0.95, 0.90, 0.78), rough=0.3)
    bigote_m = mat_simple("Bigote", (0.9, 0.88, 0.84), rough=0.4)
    cuerpo = blob(nombre + "_cuerpo", [
        ((0, 0.010, 0.050), (0.042, 0.040, 0.048), (12, 0, 0)),     # caderas
        ((0, -0.002, 0.090), (0.034, 0.032, 0.040), (12, 0, 0)),    # pecho
        ((0, -0.006, 0.118), (0.026, 0.026, 0.022), (0, 0, 0)),     # cuello
    ], coll)
    cuerpo.data.materials.append(pel)
    colgar(cuerpo, root)
    cab_c = Vector((0, -0.016, 0.150))
    piv_cab = P.empty(nombre + "_piv_cabeza", loc=(0, -0.006, 0.120), coll=coll)
    colgar(piv_cab, root)
    cabeza = blob(nombre + "_cabeza", [
        (tuple(cab_c), (0.036, 0.034, 0.033), (0, 0, 0)),
        (tuple(cab_c + Vector((0, -0.034 * hocico, -0.010))), (0.020, 0.030 * hocico, 0.018), (12, 0, 0)),   # hocico
        (tuple(cab_c + Vector((0, -0.024, -0.020))), (0.018, 0.018, 0.012), (0, 0, 0)),    # mejillas/mentón
    ], coll)
    cabeza.data.materials.append(pel)
    colgar(cabeza, piv_cab)
    nariz = esfera(nombre + "_nariz", cab_c + Vector((0, -0.034 * hocico - 0.030, -0.004)), 0.0068, coll, nariz_m)
    colgar(nariz, piv_cab)
    # boca: abertura oscura (se escala para abrirla) + dos incisivos
    piv_boca = P.empty(nombre + "_piv_boca", loc=cab_c + Vector((0, -0.050, -0.022)), coll=coll)
    colgar(piv_boca, piv_cab)
    boca = esfera(nombre + "_boca", cab_c + Vector((0, -0.050, -0.022)), 0.010, coll, boca_m, escala=(1.0, 0.45, 0.35))
    colgar(boca, piv_boca)
    for s in (-1, 1):
        d = P.prim("cube", f"{nombre}_diente{'LR'[s > 0]}", coll, diente_m)
        d.scale = (0.0028, 0.0014, 0.0042)
        d.location = cab_c + Vector((s * 0.0016, -0.0565, -0.0185))
        colgar(d, piv_boca)
    # ojos grandes, negros con brillo (cartoon), y párpados
    ojos, parps = [], []
    for s in (-1, 1):
        oc = cab_c + Vector((s * 0.019, -0.026, 0.010))
        o = ojo(f"{nombre}_ojo{'LR'[s > 0]}", oc, 0.0118, oc + Vector((s * 0.35, -1.0, 0.0)), coll, (0.16, 0.08, 0.04), iris_frac=0.88, pupila_frac=0.48)
        colgar(o, piv_cab)
        pv = P.empty(f"{nombre}_piv_parpado{'LR'[s > 0]}", loc=oc, coll=coll)
        pv.rotation_euler = o.rotation_euler.copy()
        colgar(pv, piv_cab)
        parpado(f"{nombre}_parpado{'LR'[s > 0]}", pv, 0.0118, coll, pel)
        ojos.append(o)
        parps.append(pv)
    # orejas enormes (rasgo del ratón del cactus)
    orejas = []
    for s in (-1, 1):
        base = cab_c + Vector((s * 0.022, 0.006, 0.022))
        piv = P.empty(f"{nombre}_piv_oreja{'LR'[s > 0]}", loc=base, coll=coll)
        colgar(piv, piv_cab)
        ext = oreja_ahuecada(f"{nombre}_oreja{'LR'[s > 0]}", base + Vector((s * 0.014, 0.002, 0.016)), oreja, coll, canela, oreja_in)
        ext.rotation_euler = (math.radians(-10), math.radians(s * 35), 0)
        colgar(ext, piv)
        orejas.append(piv)
    # bigotes
    for s in (-1, 1):
        for k, (dz, ang) in enumerate([(0.003, 10), (0.0, 0), (-0.003, -12)]):
            o = cab_c + Vector((s * 0.011, -0.049 * hocico - 0.002, -0.009 + dz))
            dirv = Vector((s * math.cos(math.radians(ang)), 0.30, math.sin(math.radians(ang)) * 0.6)).normalized()
            w = P.tube(f"{nombre}_bigote{'LR'[s > 0]}{k}", [tuple(o), tuple(o + dirv * 0.022 + Vector((0, 0, 0.002))), tuple(o + dirv * 0.042)], 0.0004, coll, bigote_m)
            colgar(w, piv_cab)
    # brazos (patitas delanteras) con pivote en el hombro
    brazos = []
    for s in (-1, 1):
        hom = Vector((s * 0.022, -0.020, 0.105))
        piv = P.empty(f"{nombre}_piv_brazo{'LR'[s > 0]}", loc=hom, coll=coll)
        colgar(piv, root)
        br = blob(f"{nombre}_brazo{'LR'[s > 0]}", [
            (tuple(hom + Vector((-s * 0.003, 0.004, 0.002))), (0.011, 0.011, 0.012), (0, 0, 0)),   # hombro metido en el cuerpo: el brazo nunca se despega al girar
            (tuple(hom + Vector((s * 0.004, -0.010, -0.012))), (0.009, 0.010, 0.016), (30, 0, 0)),
            (tuple(hom + Vector((s * 0.004, -0.022, -0.026))), (0.008, 0.009, 0.007), (0, 0, 0)),
        ], coll, voxel=0.0006, suave=10)
        br.data.materials.append(canela)
        colgar(br, piv)
        mano = esfera(f"{nombre}_mano{'LR'[s > 0]}", hom + Vector((s * 0.004, -0.028, -0.030)), 0.0062, coll, rosado, escala=(1.1, 0.9, 0.8))
        colgar(mano, piv)
        brazos.append(piv)
    # patas traseras grandes
    for s in (-1, 1):
        pie = esfera(f"{nombre}_pie{'LR'[s > 0]}", (s * 0.030, -0.022, 0.006), 0.011, coll, rosado, escala=(0.85, 2.0, 0.6))
        colgar(pie, root)
        muslo = blob(f"{nombre}_muslo{'LR'[s > 0]}", [((s * 0.034, 0.002, 0.034), (0.020, 0.030, 0.026), (-20, 0, 0))], coll, voxel=0.0007, suave=10)
        muslo.data.materials.append(canela)
        colgar(muslo, root)
    # cola larga
    piv_cola = P.empty(nombre + "_piv_cola", loc=(0, 0.045, 0.020), coll=coll)
    colgar(piv_cola, root)
    pts = [(0, 0.045, 0.020), (0.02, 0.09, 0.006), (0.07, 0.12, 0.004), (0.12, 0.11, 0.010), (0.15, 0.08, 0.020)]
    cola = P.tube(nombre + "_cola", pts, 0.0035, coll, rosado)
    cola.data.bevel_factor_mapping_end = "SPLINE"
    cola.data.use_fill_caps = True
    colgar(cola, piv_cola)
    return {"root": root, "cuerpo": cuerpo, "cabeza": piv_cab, "cabeza_malla": cabeza, "boca": piv_boca, "ojos": ojos, "parpados": parps,
            "orejas": orejas, "brazos": brazos, "cola": piv_cola, "boca_pos": cab_c + Vector((0, -0.056, -0.022)), "nombre": nombre}


def cara_roja(rt, lomo=(0.62, 0.07, 0.04), guata=(0.95, 0.52, 0.48)):
    """Cara roja de picante: cambia el material de la cabeza del ratón por una versión enrojecida."""
    m = mat_pelaje(rt["nombre"] + "_pelaje_rojo", lomo, guata)
    me = rt["cabeza_malla"].data
    me.materials.clear()
    me.materials.append(m)



def oreja_ahuecada(name, centro, r, coll, m_fuera, m_dentro):
    """Oreja de ratón de una sola pieza: disco grueso con la cara de adelante hundida (cuenco) y el interior rosado.
    Se modela como esfera aplastada; el cuenco es un desplazamiento hacia atrás de los vértices de la cara frontal."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=1.0)
    for v in bm.verts:
        x, y, z = v.co
        rad = math.sqrt(x * x + z * z)
        y *= 0.24
        if y < 0 and rad < 0.82:                       # cara de adelante: se hunde en el centro
            y += 0.16 * (1 - (rad / 0.82) ** 2)
        v.co = Vector((x * r, y * r, z * r))
    ob = P.mesh_obj(name, bm, coll)
    ob.data.materials.append(mat_oreja(m_fuera, m_dentro, r))
    ob.location = centro
    return ob


def mat_oreja(m_fuera, m_dentro, r):
    """Interior rosado con borde suave: mezcla por la normal (cara de adelante) y la distancia al centro, en coordenadas del objeto."""
    nombre = f"Oreja_{m_fuera.name}_{m_dentro.name}_{int(r * 10000)}"
    m = bpy.data.materials.get(nombre)
    if m:
        return m
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    nt = m.node_tree
    out = nt.nodes["Material Output"]
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    def bsdf(src):
        b = nt.nodes.new("ShaderNodeBsdfPrincipled")
        sb = src.node_tree.nodes["Principled BSDF"]
        for k in ("Base Color", "Roughness", "Sheen Weight", "Subsurface Weight"):
            b.inputs[k].default_value = sb.inputs[k].default_value
        return b
    bf, bd = bsdf(m_fuera), bsdf(m_dentro)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    sepn = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Normal"], sepn.inputs[0])
    x2 = nt.nodes.new("ShaderNodeMath"); x2.operation = "POWER"; x2.inputs[1].default_value = 2.0
    z2 = nt.nodes.new("ShaderNodeMath"); z2.operation = "POWER"; z2.inputs[1].default_value = 2.0
    nt.links.new(sep.outputs["X"], x2.inputs[0]); nt.links.new(sep.outputs["Z"], z2.inputs[0])
    sm = nt.nodes.new("ShaderNodeMath"); sm.operation = "ADD"
    nt.links.new(x2.outputs[0], sm.inputs[0]); nt.links.new(z2.outputs[0], sm.inputs[1])
    sq = nt.nodes.new("ShaderNodeMath"); sq.operation = "SQRT"
    nt.links.new(sm.outputs[0], sq.inputs[0])
    rad = nt.nodes.new("ShaderNodeMapRange")          # 1 dentro del círculo, 0 en el borde (transición suave)
    rad.inputs["From Min"].default_value = 0.80 * r
    rad.inputs["From Max"].default_value = 0.70 * r
    nt.links.new(sq.outputs[0], rad.inputs["Value"])
    frente = nt.nodes.new("ShaderNodeMapRange")       # 1 en la cara de adelante (normal -Y)
    frente.inputs["From Min"].default_value = -0.10
    frente.inputs["From Max"].default_value = -0.45
    nt.links.new(sepn.outputs["Y"], frente.inputs["Value"])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    nt.links.new(rad.outputs["Result"], mul.inputs[0]); nt.links.new(frente.outputs["Result"], mul.inputs[1])
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mul.outputs[0], mix.inputs["Fac"])
    nt.links.new(bf.outputs[0], mix.inputs[1]); nt.links.new(bd.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def lentes(name, centro, ancho, coll, mirando=(0, -1, 0)):
    """Lentes de sol de dibujo animado (rígidos): dos micas redondeadas oscuras y un puente. Origen = centro del puente."""
    mica = mat_simple("Mica", (0.01, 0.01, 0.015), rough=0.05, coat=1.0)
    marco = mat_simple("MarcoLentes", (0.02, 0.02, 0.02), rough=0.3)
    root = P.empty(name, loc=centro, coll=coll)
    for s in (-1, 1):
        m_ = P.prim("cyl", f"{name}_mica{'LR'[s > 0]}", coll, mica, r=ancho * 0.27, r2=ancho * 0.27, h=ancho * 0.06, seg=40)
        m_.scale = (1.15, 1.0, 1.0)
        m_.rotation_euler = (math.radians(90), 0, 0)
        m_.location = (s * ancho * 0.27, 0, 0)
        P.bevel(m_, ancho * 0.02, 2)
        m_.parent = root
    pu = P.prim("cube", name + "_puente", coll, marco)
    pu.scale = (ancho * 0.12, ancho * 0.04, ancho * 0.03)
    pu.location = (0, 0, ancho * 0.06)
    pu.parent = root
    root.rotation_euler = Vector(mirando).to_track_quat("-Y", "Z").to_euler()
    return root


def medalla(name, centro, r, coll):
    """Medalla dorada rígida con cinta (sin tela)."""
    oro = mat_simple("Oro", (1.0, 0.62, 0.08), rough=0.28, coat=0.5)
    oro.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.35   # con 1.0 reflejaba el cactus y se veía verde
    cinta = mat_simple("Cinta", (0.85, 0.08, 0.10), rough=0.5)
    root = P.empty(name, loc=centro, coll=coll)
    d = P.prim("cyl", name + "_disco", coll, oro, r=r, r2=r, h=r * 0.25, seg=40)
    d.rotation_euler = (math.radians(90), 0, 0)
    P.bevel(d, r * 0.08, 2)
    d.parent = root
    for s in (-1, 1):
        c = P.prim("cube", f"{name}_cinta{s}", coll, cinta)
        c.scale = (r * 0.5, r * 0.08, r * 2.2)
        c.location = (s * r * 0.6, r * 0.05, r * 2.0)
        c.rotation_euler = (0, math.radians(-s * 22), 0)
        c.parent = root
    return root


def aji_guardia(coll, nombre="AjiGuardia", alto=0.32):
    """El ají guardia: ají rojo grande parado sobre la punta, con lentes de sol, cejas serias y brazos cruzados (fijos).
    Origen = punta en el suelo; mira hacia -Y."""
    import props_ep02 as E
    root = P.empty(nombre, coll=coll)
    cuerpo = E.aji(nombre + "_cuerpo", largo=alto, grosor=alto * 0.17, coll=coll, seed=9, curva=0.25)
    cuerpo.location = (0, 0, alto * 0.80)
    for ch in cuerpo.children:
        if ch.name.endswith("_tallo"):
            ch.scale = (1, 1, 0.45)
    colgar(cuerpo, root)
    piv_cab = P.empty(nombre + "_piv_cabeza", loc=(0, 0, alto * 0.78), coll=coll)
    colgar(piv_cab, root)
    yf = -alto * 0.165
    nariz = esfera(nombre + "_nariz", (0.0, yf * 1.10, alto * 0.735), alto * 0.032, coll, bpy.data.materials.get("Aji") or E.mat_aji())
    colgar(nariz, piv_cab)
    blanco = mat_simple("OjoGuardia", (0.95, 0.94, 0.90), rough=0.2, coat=0.5)
    negro_o = mat_simple("PupilaGuardia", (0.01, 0.01, 0.01), rough=0.2)
    ceja_m = mat_simple("CejaGuardia", (0.05, 0.02, 0.01), rough=0.5)
    for sx in (-1, 1):
        oj = esfera(f"{nombre}_ojo{'LR'[sx > 0]}", (sx * alto * 0.075, yf * 0.92, alto * 0.815), alto * 0.042, coll, blanco, escala=(1.0, 0.45, 0.8))
        colgar(oj, piv_cab)
        pu = esfera(f"{nombre}_pupila{'LR'[sx > 0]}", (sx * alto * 0.070, yf * 1.00, alto * 0.805), alto * 0.016, coll, negro_o, escala=(1.0, 0.5, 1.0))
        colgar(pu, piv_cab)
        cj = P.prim("cube", f"{nombre}_ceja{'LR'[sx > 0]}", coll, ceja_m)
        cj.scale = (alto * 0.07, alto * 0.012, alto * 0.012)
        cj.location = (sx * alto * 0.075, yf * 0.97, alto * 0.872)
        cj.rotation_euler = (0, math.radians(sx * 12), 0)
        colgar(cj, piv_cab)
    piv_lentes = P.empty(nombre + "_piv_lentes", loc=(0.0, yf * 1.05, alto * 0.80), coll=coll)
    colgar(piv_lentes, piv_cab)
    lt = lentes(nombre + "_lentes", (0.0, yf * 1.18, alto * 0.80), alto * 0.30, coll)
    colgar(lt, piv_lentes)
    negro = mat_simple("BocaGuardia", (0.05, 0.01, 0.01), rough=0.6)
    boca = P.tube(nombre + "_boca", [(-alto * 0.05, yf * 0.99, alto * 0.66), (0.0, yf * 1.02, alto * 0.655), (alto * 0.05, yf * 0.97, alto * 0.672)], alto * 0.006, coll, negro)
    colgar(boca, piv_cab)
    rojo = cuerpo.data.materials[0]
    brazos = []
    for s in (-1, 1):
        z0 = alto * (0.50 if s < 0 else 0.46)
        pts = [(s * alto * 0.15, -alto * 0.01, z0 + alto * 0.04), (s * alto * 0.11, yf * 1.30, z0), (-s * alto * 0.08, yf * 1.30, z0 - alto * 0.01)]
        b = P.tube(f"{nombre}_brazo{'LR'[s > 0]}", pts, alto * 0.03, coll, rojo)
        colgar(b, root)
        mano = esfera(f"{nombre}_mano{'LR'[s > 0]}", pts[-1], alto * 0.035, coll, rojo)
        colgar(mano, root)
        brazos.append(b)
    # la punta del ají queda apoyada en el suelo (z = 0)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = cuerpo.evaluated_get(dg)
    mev = ev.to_mesh()
    zmin = min((cuerpo.matrix_world @ v.co).z for v in mev.vertices)
    ev.to_mesh_clear()
    for ch in list(root.children):
        ch.location.z -= zmin
    return {"root": root, "cabeza": piv_cab, "lentes": piv_lentes, "alto": alto}


def tupaya(coll, nombre="Tupaya"):
    """Tupaya (modelo de la ficha.jpg: no cambiar sin volver a renderizar la ficha)
    Tupaya (Tupaia belangeri) de dibujo animado, en cuatro patas sobre una rama: café oliva, raya clara en el hombro,
    hocico largo, orejas chicas, ojos grandes y cola peluda. ~0,30 m con cola. Mira hacia -Y."""
    root = P.empty(nombre, coll=coll)
    pel = mat_pelaje(nombre + "_pelaje", (0.22, 0.17, 0.08), (0.72, 0.60, 0.42))
    lomo = mat_simple(nombre + "_lomo", (0.22, 0.17, 0.08), rough=0.7, sheen=0.9)
    nariz_m = mat_simple(nombre + "_nariz", (0.06, 0.04, 0.035), rough=0.25, coat=0.6)
    cuerpo = blob(nombre + "_cuerpo", [
        ((0, 0.010, 0.060), (0.032, 0.060, 0.032), (6, 0, 0)),
        ((0, -0.045, 0.072), (0.028, 0.030, 0.030), (0, 0, 0)),
    ], coll)
    cuerpo.data.materials.append(pel)
    colgar(cuerpo, root)
    for s in (-1, 1):
        raya = esfera(f"{nombre}_raya{'LR'[s > 0]}", (s * 0.031, -0.022, 0.072), 0.012, coll, mat_simple(nombre + "_raya", (0.80, 0.72, 0.55), rough=0.7, sheen=0.8), escala=(0.25, 1.4, 0.6))
        colgar(raya, root)
    cab_c = Vector((0, -0.080, 0.092))
    piv_cab = P.empty(nombre + "_piv_cabeza", loc=(0, -0.060, 0.080), coll=coll)
    colgar(piv_cab, root)
    cab = blob(nombre + "_cabeza", [
        (tuple(cab_c), (0.025, 0.026, 0.023), (0, 0, 0)),
        (tuple(cab_c + Vector((0, -0.030, -0.006))), (0.012, 0.030, 0.012), (8, 0, 0)),
    ], coll)
    cab.data.materials.append(pel)
    colgar(cab, piv_cab)
    nz = esfera(nombre + "_naricita", cab_c + Vector((0, -0.060, -0.009)), 0.0055, coll, nariz_m)
    colgar(nz, piv_cab)
    ojos = []
    for s in (-1, 1):
        oc = cab_c + Vector((s * 0.016, -0.014, 0.008))
        o = ojo(f"{nombre}_ojo{'LR'[s > 0]}", oc, 0.0095, oc + Vector((s * 0.6, -1.0, 0.0)), coll, (0.18, 0.09, 0.03), iris_frac=0.9, pupila_frac=0.5)
        colgar(o, piv_cab)
        ojos.append(o)
        orj = esfera(f"{nombre}_oreja{'LR'[s > 0]}", cab_c + Vector((s * 0.020, 0.006, 0.018)), 0.0085, coll, lomo, escala=(1.0, 0.4, 1.0))
        colgar(orj, piv_cab)
    for (x, y) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        pata = blob(f"{nombre}_pata{x}{y}", [((x * 0.020, y * 0.035 - 0.005, 0.028), (0.008, 0.009, 0.026), (0, 0, 0)),
                                            ((x * 0.021, y * 0.035 - 0.010, 0.004), (0.008, 0.012, 0.005), (0, 0, 0))], coll, voxel=0.0006, suave=10)
        pata.data.materials.append(lomo)
        colgar(pata, root)
    pts = [(0, 0.060, 0.058), (0, 0.095, 0.066), (0, 0.130, 0.080), (0, 0.165, 0.100), (0, 0.192, 0.126), (0, 0.205, 0.150)]
    cola = P.tube(nombre + "_cola", pts, 0.017, coll, lomo, res=16)
    for pt, r in zip(cola.data.splines[0].points, (0.55, 0.85, 1.0, 1.05, 0.95, 0.55)):
        pt.radius = r
    cola.data.bevel_resolution = 8
    colgar(cola, root)
    return {"root": root, "cabeza": piv_cab, "ojos": ojos, "parpados": []}
