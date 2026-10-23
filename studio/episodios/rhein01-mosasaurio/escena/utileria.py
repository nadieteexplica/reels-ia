"""Utilería semi-realista de Rhein 01: materiales con desgaste, montaña de 200 pollos, micro flotando, asiento de montaña
rusa con arnés, consola del radar, huesos de pollo, salpicaduras, flechas de fuerza y regla. Todo procedural y propio."""
import math, os, random, sys
import bmesh
import bpy
import numpy as np
from mathutils import Vector, Euler, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../plantilla")))
import props as P
from base_pj import blob, esfera, mat_simple, colgar, cuerno
import mar as M


# ---------------------------------------------------------------- materiales con desgaste
def _ruido_color(m, c1, c2, escala=6.0, detalle=6.0, rugo=(0.35, 0.6), bump=0.08):
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = escala
    nz.inputs["Detail"].default_value = detalle
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*c1, 1)
    ramp.color_ramp.elements[1].color = (*c2, 1)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[1].position = 0.75
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = rugo
    nt.links.new(nz.outputs["Fac"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], b.inputs["Roughness"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def madera(nombre="Madera", c1=(0.42, 0.22, 0.09), c2=(0.25, 0.12, 0.05)):
    m = bpy.data.materials.get(nombre)
    if m:
        return m
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (18.0, 1.2, 18.0)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    w = nt.nodes.new("ShaderNodeTexWave")
    w.wave_type = "BANDS"
    w.inputs["Scale"].default_value = 2.0
    w.inputs["Distortion"].default_value = 6.0
    w.inputs["Detail"].default_value = 4.0
    nt.links.new(mp.outputs["Vector"], w.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*c1, 1)
    ramp.color_ramp.elements[1].color = (*c2, 1)
    nt.links.new(w.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.62
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.12
    nt.links.new(w.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def pintura(nombre, c, sucio=0.25, escala=5.0):
    m = bpy.data.materials.get(nombre)
    if m:
        return m
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Coat Weight"].default_value = 0.35
    c2 = tuple(x * (1 - sucio) for x in c)
    return _ruido_color(m, c, c2, escala=escala, rugo=(0.28, 0.55), bump=0.05)


def acero(nombre="AceroReal", c=(0.62, 0.63, 0.65)):
    m = bpy.data.materials.get(nombre)
    if m:
        return m
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 1.0
    return _ruido_color(m, c, tuple(x * 0.75 for x in c), escala=40, rugo=(0.18, 0.42), bump=0.03)


def realismo_bote():
    """Cambia los materiales del bote y la grúa por versiones con desgaste (pintura, madera, acero)."""
    rep = {"Casco": pintura("CascoP", (0.72, 0.07, 0.05), 0.3), "BordeBote": pintura("BordeP", (0.92, 0.90, 0.84), 0.2),
           "MaderaBote": madera(), "Amarillo": pintura("AmarilloP", (0.95, 0.62, 0.0), 0.25, escala=8),
           "NegroGrua": pintura("NegroP", (0.03, 0.03, 0.035), 0.1), "Acero": acero()}
    for o in bpy.data.objects:
        if o.type in ("MESH", "CURVE") and o.data.materials:
            for i, m in enumerate(o.data.materials):
                if m and m.name in rep:
                    o.data.materials[i] = rep[m.name]


# ---------------------------------------------------------------- pollos
def montana_pollos(coll, centro, n=200, radio=0.62, alto=0.85, semilla=5):
    """Montaña de pollos asados (instancias del pollo base). Devuelve (lista de objetos, posiciones)."""
    r = random.Random(semilla)
    base = bpy.data.objects.get("PolloBase") or M.pollo(coll, "PolloBase")
    for o in [base] + list(base.children):
        o.hide_render = o.hide_viewport = True
    obs, pos = [], []
    for i in range(n):
        u = (i / n) ** 0.7
        h = alto * u
        rr = radio * (1 - u) ** 0.8 + 0.05
        a = i * 2.39996
        p = Vector(centro) + Vector((rr * math.cos(a) * r.uniform(0.6, 1.0), rr * math.sin(a) * r.uniform(0.6, 1.0), 0.10 + h))
        ob = _copia_pollo(base, coll, f"PolloPila{i}")
        ob.location = p
        ob.rotation_euler = (r.uniform(-0.6, 0.6), r.uniform(-0.6, 0.6), r.uniform(0, 6.28))
        s = r.uniform(0.85, 1.1)
        ob.scale = (s, s, s)
        obs.append(ob)
        pos.append(p.copy())
    return obs, pos


def _copia_pollo(base, coll, nombre):
    dup = base.copy()
    dup.data = base.data
    coll.objects.link(dup)
    dup.name = nombre
    dup.hide_render = dup.hide_viewport = False
    for ch in base.children:
        c2 = ch.copy()
        c2.data = ch.data
        coll.objects.link(c2)
        c2.parent = dup
        c2.matrix_parent_inverse = ch.matrix_parent_inverse.copy()
        c2.hide_render = c2.hide_viewport = False
    return dup


def ocultar(ob, si=True):
    ob.hide_render = si
    for c in ob.children_recursive:
        c.hide_render = si


# ---------------------------------------------------------------- micro
def micro(coll, nombre="Micro"):
    """Micro (bus urbano) blanca y roja, 12 m, con ventanas oscuras. Origen en el centro, a lo largo de Y."""
    raiz = bpy.data.objects.new(nombre, None)
    coll.objects.link(raiz)
    m_bl = pintura("MicroBlanco", (0.92, 0.92, 0.9), 0.15)
    m_ro = pintura("MicroRojo", (0.75, 0.04, 0.05), 0.15)
    m_vi = mat_simple("MicroVidrio", (0.03, 0.05, 0.07), rough=0.05, coat=1.0)
    m_ne = mat_simple("MicroGoma", (0.02, 0.02, 0.02), rough=0.8)
    cuerpo = P.prim("cube", nombre + "_cuerpo", coll, m_bl)
    cuerpo.scale = (2.5, 12.0, 2.9)
    cuerpo.location = (0, 0, 1.75)
    P.bevel(cuerpo, 0.18, 4)
    franja = P.prim("cube", nombre + "_franja", coll, m_ro)
    franja.scale = (2.52, 11.6, 0.55)
    franja.location = (0, 0, 0.75)
    P.bevel(franja, 0.1, 3)
    vent = P.prim("cube", nombre + "_ventanas", coll, m_vi)
    vent.scale = (2.53, 10.6, 1.05)
    vent.location = (0, 0.3, 2.35)
    P.bevel(vent, 0.08, 3)
    para = P.prim("cube", nombre + "_parabrisas", coll, m_vi)
    para.scale = (2.2, 0.1, 1.6)
    para.location = (0, -6.0, 2.1)
    obs = [cuerpo, franja, vent, para]
    for y in (-3.8, 3.6):
        for x in (-1.2, 1.2):
            rueda = P.prim("cyl", f"{nombre}_rueda{x}{y}", coll, m_ne, r=0.5, r_top=0.5, h=0.32, seg=32)
            rueda.rotation_euler = (0, math.radians(90), 0)
            rueda.location = (x, y, 0.5)
            obs.append(rueda)
    for o in obs:
        o.parent = raiz
    return raiz


# ---------------------------------------------------------------- asiento de montaña rusa
def asiento(coll, nombre="Asiento"):
    """Asiento rojo de montaña rusa con arnés que baja sobre los hombros (pivote <nombre>_arnes, rot X 0 = arriba).
    Origen en la base (piso). El niño se sienta en z ≈ 0.42 sobre la base, mirando a -Y."""
    raiz = bpy.data.objects.new(nombre, None)
    coll.objects.link(raiz)
    m_ro = pintura("AsientoRojo", (0.80, 0.05, 0.04), 0.12)
    m_ne = mat_simple("AsientoNegro", (0.02, 0.02, 0.025), rough=0.5, coat=0.3)
    m_am = pintura("ArnesAmarillo", (1.0, 0.70, 0.0), 0.1)
    base = P.prim("cube", nombre + "_base", coll, m_ne)
    base.scale = (0.62, 0.62, 0.10)
    base.location = (0, 0, 0.05)
    P.bevel(base, 0.03)
    banco = P.prim("cube", nombre + "_banco", coll, m_ro)
    banco.scale = (0.56, 0.52, 0.16)
    banco.location = (0, 0.02, 0.30)
    P.bevel(banco, 0.06, 4)
    respaldo = P.prim("cube", nombre + "_respaldo", coll, m_ro)
    respaldo.scale = (0.56, 0.14, 0.85)
    respaldo.location = (0, 0.26, 0.78)
    P.bevel(respaldo, 0.06, 4)
    cab = P.prim("cube", nombre + "_cabecera", coll, m_ne)
    cab.scale = (0.30, 0.14, 0.22)
    cab.location = (0, 0.22, 1.30)
    P.bevel(cab, 0.05, 4)
    pernos = []
    for x in (-0.25, 0.25):
        for y in (-0.25, 0.25):
            pb = P.prim("cyl", f"{nombre}_perno{x}{y}", coll, acero(), r=0.025, r_top=0.025, h=0.04, seg=6)
            pb.location = (x, y, 0.11)
            pernos.append(pb)
    piv = bpy.data.objects.new(nombre + "_arnes", None)     # bisagra arriba, detrás de los hombros
    coll.objects.link(piv)
    piv.location = (0, 0.16, 1.18)
    piv.parent = raiz
    barra = []
    for x in (-0.17, 0.17):
        barra.append(P.tube(f"{nombre}_barra{x}", [(x, 0.0, 0.0), (x * 1.05, -0.16, -0.05), (x * 1.1, -0.26, -0.32), (x * 0.9, -0.24, -0.55)],
                            0.035, coll, m=m_am, res=10))
    traba = P.tube(nombre + "_traba", [(-0.16, -0.24, -0.55), (0, -0.27, -0.58), (0.16, -0.24, -0.55)], 0.035, coll, m=m_am, res=10)
    barra.append(traba)
    for o in barra:
        o.parent = piv
    # pestillo dentado (cremallera) al costado: se ve en el detalle del arnés
    crem = P.prim("cube", nombre + "_cremallera", coll, m_ne)
    crem.scale = (0.03, 0.05, 0.35)
    crem.location = (0.31, 0.10, 0.85)
    dientes = []
    for k in range(7):
        d = P.prim("cube", f"{nombre}_diente{k}", coll, acero())
        d.scale = (0.035, 0.03, 0.018)
        d.rotation_euler = (math.radians(30), 0, 0)
        d.location = (0.31, 0.07, 0.72 + 0.045 * k)
        dientes.append(d)
    for o in [base, banco, respaldo, cab, crem] + pernos + dientes:
        o.parent = raiz
    return raiz, piv


# ---------------------------------------------------------------- consola del radar
def consola(coll, nombre="Consola"):
    """Caja metálica con pantalla redonda de radar (material con barrido animado: nodo 'Barrido' rotación Z)."""
    raiz = bpy.data.objects.new(nombre, None)
    coll.objects.link(raiz)
    caja = P.prim("cube", nombre + "_caja", coll, pintura("ConsolaGris", (0.18, 0.20, 0.22), 0.2))
    caja.scale = (0.46, 0.30, 0.42)
    caja.location = (0, 0, 0.21)
    P.bevel(caja, 0.03, 3)
    marco = P.prim("cyl", nombre + "_marco", coll, mat_simple("ConsolaNegro", (0.01, 0.01, 0.012), rough=0.3, coat=0.5),
                   r=0.17, r_top=0.17, h=0.03, seg=64)
    marco.rotation_euler = (math.radians(90), 0, 0)
    marco.location = (0, -0.155, 0.23)
    pant = P.prim("cyl", nombre + "_pantalla", coll, mat_radar(), r=0.15, r_top=0.15, h=0.02, seg=64)
    pant.rotation_euler = (math.radians(90), 0, 0)
    pant.location = (0, -0.168, 0.23)
    for o in (caja, marco, pant):
        o.parent = raiz
    return raiz, pant


def mat_radar():
    """Pantalla de radar verde: anillos, cruz, haz que barre (ángulo en el nodo 'Barrido') y un punto (nodo 'Punto')."""
    m = bpy.data.materials.get("Radar")
    if m:
        return m
    m = bpy.data.materials.new("Radar")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    # coordenadas del objeto (cilindro girado: x, y del disco = x, y locales)
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    def mathn(op, a=None, b=None, v1=None):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        if a is not None:
            nt.links.new(a, n.inputs[0])
        if b is not None:
            nt.links.new(b, n.inputs[1])
        if v1 is not None:
            n.inputs[1].default_value = v1
        return n
    x2 = mathn("MULTIPLY", sep.outputs["X"], sep.outputs["X"])
    y2 = mathn("MULTIPLY", sep.outputs["Y"], sep.outputs["Y"])
    r = mathn("SQRT", mathn("ADD", x2.outputs[0], y2.outputs[0]).outputs[0])
    ang = mathn("ARCTAN2", sep.outputs["Y"], sep.outputs["X"])
    barr = nt.nodes.new("ShaderNodeValue")
    barr.name = "Barrido"
    barr.outputs[0].default_value = 0.0
    d = mathn("SUBTRACT", barr.outputs[0], ang.outputs[0])
    dm = mathn("FLOORED_MODULO", d.outputs[0], v1=2 * math.pi)
    # estela del haz: 1 - dm/(2pi), elevado a 6 (brillante justo detrás del haz)
    sc = mathn("DIVIDE", dm.outputs[0], v1=2 * math.pi)
    uno = mathn("SUBTRACT", None, sc.outputs[0])
    uno.inputs[0].default_value = 1.0
    haz2 = mathn("POWER", uno.outputs[0], v1=6.0)
    anillos = mathn("FRACT", mathn("MULTIPLY", r.outputs[0], v1=26.0).outputs[0])
    an = mathn("GREATER_THAN", anillos.outputs[0], v1=0.9)
    cruzx = mathn("LESS_THAN", mathn("ABSOLUTE", sep.outputs["X"]).outputs[0], v1=0.0025)
    cruzy = mathn("LESS_THAN", mathn("ABSOLUTE", sep.outputs["Y"]).outputs[0], v1=0.0025)
    punto_x = nt.nodes.new("ShaderNodeValue")
    punto_x.name = "PuntoX"
    punto_x.outputs[0].default_value = 0.11
    punto_y = nt.nodes.new("ShaderNodeValue")
    punto_y.name = "PuntoY"
    punto_y.outputs[0].default_value = 0.05
    dx = mathn("SUBTRACT", sep.outputs["X"], punto_x.outputs[0])
    dy = mathn("SUBTRACT", sep.outputs["Y"], punto_y.outputs[0])
    dd = mathn("SQRT", mathn("ADD", mathn("MULTIPLY", dx.outputs[0], dx.outputs[0]).outputs[0],
                              mathn("MULTIPLY", dy.outputs[0], dy.outputs[0]).outputs[0]).outputs[0])
    tam = nt.nodes.new("ShaderNodeValue")
    tam.name = "PuntoTam"
    tam.outputs[0].default_value = 0.0
    pt = mathn("LESS_THAN", dd.outputs[0], tam.outputs[0])
    suma = mathn("ADD", mathn("MULTIPLY", haz2.outputs[0], v1=0.8).outputs[0], mathn("MULTIPLY", an.outputs[0], v1=0.45).outputs[0])
    suma = mathn("ADD", suma.outputs[0], mathn("MULTIPLY", mathn("ADD", cruzx.outputs[0], cruzy.outputs[0]).outputs[0], v1=0.35).outputs[0])
    suma = mathn("ADD", suma.outputs[0], mathn("MULTIPLY", pt.outputs[0], v1=3.0).outputs[0])
    suma = mathn("ADD", suma.outputs[0], v1=0.06)
    br = nt.nodes.new("ShaderNodeValue")
    br.name = "Brillo"
    br.outputs[0].default_value = 1.0
    fuerza = mathn("MULTIPLY", suma.outputs[0], br.outputs[0])
    col = nt.nodes.new("ShaderNodeRGB")
    col.outputs[0].default_value = (0.15, 1.0, 0.35, 1)
    nt.links.new(col.outputs[0], em.inputs["Color"])
    nt.links.new(mathn("MULTIPLY", fuerza.outputs[0], v1=4.0).outputs[0], em.inputs["Strength"])
    return m


def radar_estado(barrido, punto=None, tam=0.0, brillo=1.0):
    nt = bpy.data.materials["Radar"].node_tree
    nt.nodes["Barrido"].outputs[0].default_value = barrido
    if punto:
        nt.nodes["PuntoX"].outputs[0].default_value = punto[0]
        nt.nodes["PuntoY"].outputs[0].default_value = punto[1]
    nt.nodes["PuntoTam"].outputs[0].default_value = tam
    nt.nodes["Brillo"].outputs[0].default_value = brillo


# ---------------------------------------------------------------- huesos, gotas, flechas
def huesos(coll, n=26, semilla=8):
    r = random.Random(semilla)
    mh = mat_simple("HuesoPollo", (0.98, 0.95, 0.88), rough=0.4)
    base = cuerno("HuesoBase", (0, -0.05, 0), (0, 1, 0), (0, 0, 1), 0.10, 0.012, 0.010, coll=coll, m=mh, curv=0.15)
    obs = []
    for i in range(n):
        h = base.copy()
        h.data = base.data
        coll.objects.link(h)
        h.name = f"Hueso{i}"
        h["v"] = (r.uniform(-0.6, 0.6), r.uniform(-0.6, 0.6), r.uniform(-0.3, 0.6))
        h["giro"] = (r.uniform(-12, 12), r.uniform(-12, 12), r.uniform(-12, 12))
        h["t0"] = r.uniform(0.0, 0.5)
        obs.append(h)
    base.hide_render = base.hide_viewport = True
    return obs


def mover_huesos(obs, t, centro, g=9.8):
    """Huesos que caen desde ~2,5 m sobre `centro`, rebotan una vez y quedan en el piso (z del centro)."""
    for h in obs:
        tt = t - h["t0"]
        if tt < 0:
            h.hide_render = True
            continue
        h.hide_render = False
        vx, vy, vz = h["v"]
        z = 2.4 + vz * tt - 0.5 * g * tt * tt
        if z < 0.05:
            z = 0.05
        h.location = Vector(centro) + Vector((vx * tt, vy * tt, z))
        gx, gy, gz = h["giro"]
        h.rotation_euler = (gx * tt, gy * tt, gz * tt)


def gotas(coll, n=180, semilla=3, nombre="Gota"):
    """Salpicadura: esferitas de agua con velocidad propia (se mueven con mover_gotas)."""
    r = random.Random(semilla)
    m = bpy.data.materials.get("AguaGota") or mat_simple("AguaGota", (0.75, 0.9, 1.0), rough=0.02)
    if "Transmission Weight" in m.node_tree.nodes["Principled BSDF"].inputs:
        m.node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = 0.9
    base = P.prim("ico", nombre + "Base", coll, m, sub=2, r=1.0)
    obs = []
    for i in range(n):
        g = base.copy()
        g.data = base.data
        coll.objects.link(g)
        g.name = f"{nombre}{i}"
        a = r.uniform(0, 2 * math.pi)
        sp = r.uniform(2.0, 7.0)
        g["v"] = (sp * math.cos(a) * r.uniform(0.3, 1.0), sp * math.sin(a) * r.uniform(0.3, 1.0), r.uniform(5.0, 12.0))
        g["r"] = r.uniform(0.04, 0.16)
        obs.append(g)
    base.hide_render = base.hide_viewport = True
    return obs


def mover_gotas(obs, t, centro, g=9.8, escala=1.0):
    for d in obs:
        if t < 0 or t > 1.6:
            d.hide_render = True
            continue
        vx, vy, vz = d["v"]
        z = vz * t - 0.5 * g * t * t
        if z < -0.2:
            d.hide_render = True
            continue
        d.hide_render = False
        d.location = Vector(centro) + Vector((vx * t * escala, vy * t * escala, z * escala))
        s = d["r"] * escala * (1.0 - 0.3 * min(1, t))
        d.scale = (s, s, s * 1.3)


def flecha(coll, nombre, color, largo=0.35, grosor=0.03, curva=False, radio=0.18, arco=270):
    """Flecha 3D emisiva (recta o curva de giro). Apunta a +X (recta) o gira alrededor de Z (curva)."""
    m = bpy.data.materials.get("Flecha" + nombre)
    if not m:
        m = bpy.data.materials.new("Flecha" + nombre)
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*color, 1)
        b.inputs["Emission Color"].default_value = (*color, 1)
        b.inputs["Emission Strength"].default_value = 2.5
        b.inputs["Roughness"].default_value = 0.4
    if curva:
        pts = [(radio * math.cos(math.radians(a)), radio * math.sin(math.radians(a)), 0) for a in range(0, arco, 15)]
        cuerpo = P.tube(nombre, pts, grosor, coll, m=m, res=6)
        a1 = math.radians(arco)
        tip = Vector((radio * math.cos(a1), radio * math.sin(a1), 0))
        dirv = Vector((-math.sin(a1), math.cos(a1), 0))
    else:
        cuerpo = P.tube(nombre, [(0, 0, 0), (largo, 0, 0)], grosor, coll, m=m, res=6)
        tip = Vector((largo, 0, 0))
        dirv = Vector((1, 0, 0))
    punta = P.prim("cyl", nombre + "_punta", coll, m, r=grosor * 2.6, r_top=0.0005, h=grosor * 5, seg=24)
    punta.location = tip + dirv * grosor * 2.2
    punta.rotation_euler = dirv.to_track_quat("Z", "Y").to_euler()
    punta.parent = cuerpo
    cuerpo.visible_shadow = False
    punta.visible_shadow = False
    return cuerpo
