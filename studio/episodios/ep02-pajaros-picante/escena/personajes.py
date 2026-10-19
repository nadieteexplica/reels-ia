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
    sm = ob.modifiers.new("Suave", "LAPLACIANSMOOTH")
    sm.iterations = suave
    sm.lambda_factor = 0.9
    sm.use_volume_preserve = True
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
    pecho.inputs["From Min"].default_value = 0.35
    pecho.inputs["From Max"].default_value = 0.85
    nt.links.new(add.outputs[0], pecho.inputs["Value"])
    base = nt.nodes.new("ShaderNodeMix")
    base.data_type = "RGBA"
    base.inputs["A"].default_value = (0.085, 0.064, 0.050, 1)    # lomo gris café
    base.inputs["B"].default_value = (0.34, 0.26, 0.20, 1)     # pecho beige grisáceo
    nt.links.new(pecho.outputs["Result"], base.inputs["Factor"])
    # motas del pecho (voronoi)
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 55.0
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
    mm2.inputs[1].default_value = 0.55
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
