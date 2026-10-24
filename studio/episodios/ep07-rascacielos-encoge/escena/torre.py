"""Ep. 7 — el rascacielos que se achica: la torre de 40 pisos con su "sombrero" (el último piso sobre gatas, con la
envoltura de paneles que tapa los 2 pisos de trabajo), la ciudad al atardecer y el corte del sombrero por dentro.

Todo procedural, a escala real (40 pisos × 3,5 m = 140 m; planta de 52 × 20 m), sobre el kit realista del Ep. 5
(ep07.py = copia de ep05.py: cielo físico, materiales sucios, Pete de Mixamo). Coordenadas: la torre centrada en el
origen, fachada larga mirando a -Y; el sol bajo del oeste-suroeste (de la izquierda y un poco de frente).

Estado de la torre: h = pisos enteros que quedan bajo la envoltura (float; 37 al comienzo → 37 + 2 de trabajo + 1 de
sombrero = 40 pisos). El sombrero (último piso + techo) y la envoltura bajan juntos con h.
"""
import math, random
import bpy
import bmesh
from mathutils import Vector

import ep07 as E

H = 3.5                    # alto de un piso (140 m / 40)
NP = 40
LX, LY = 52.0, 20.0        # planta de la torre
H0 = 37.0                  # pisos bajo la envoltura al comienzo (37 + 2 + 1 = 40)
POZO = 5.0                 # pozo central por donde bajan los escombros
SOL_AZ, SOL_EL = 250.0, 4.5
NEBLINA = (0.86, 0.6, 0.47)


# ---------------------------------------------------------------- materiales
def neblina(m, k=2600.0, color=NEBLINA, fuerza=1.0):
    """Perspectiva aérea: mezcla el material con el color de la neblina según la distancia a la cámara."""
    nt = m.node_tree
    out = nt.nodes["Material Output"]
    src = out.inputs[0].links[0].from_socket
    cd = nt.nodes.new("ShaderNodeCameraData")
    ex = nt.nodes.new("ShaderNodeMath"); ex.operation = "MULTIPLY"; ex.inputs[1].default_value = -1.0 / k
    nt.links.new(cd.outputs["View Distance"], ex.inputs[0])
    e2 = nt.nodes.new("ShaderNodeMath"); e2.operation = "EXPONENT"; nt.links.new(ex.outputs[0], e2.inputs[0])
    inv = nt.nodes.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
    nt.links.new(e2.outputs[0], inv.inputs[1])
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (*color, 1); em.inputs[1].default_value = fuerza
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(inv.outputs[0], mx.inputs[0]); nt.links.new(src, mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    return m


def _m(nt, op, a=None, b=None, va=None, vb=None):
    n = nt.nodes.new("ShaderNodeMath"); n.operation = op
    if a is not None:
        nt.links.new(a, n.inputs[0])
    elif va is not None:
        n.inputs[0].default_value = va
    if b is not None:
        nt.links.new(b, n.inputs[1])
    elif vb is not None:
        n.inputs[1].default_value = vb
    return n.outputs[0]


def mat_fachada(nombre, piso=3.5, modulo=1.8, banda=(0.32, 0.94), marco=0.12, col_panel=(0.78, 0.77, 0.74),
                metal=0.35, luces=0.0, col_luz=(1.0, 0.72, 0.45), cortinas=(0.04, 0.1), vidrio_oscuro=0.025,
                k_neblina=2600.0, techo=(0.3, 0.3, 0.29)):
    """Fachada de pisos con ventanas en banda: paneles de aluminio con chorreados (antepecho), vidrio que refleja el cielo
    con el cuarto detrás (cortinas al azar), parteluces cada `modulo` m. Coordenadas de objeto con el origen al pie del
    objeto (z = 0 en su base). Las caras horizontales son techo de concreto. `luces` = fracción de ventanas prendidas."""
    m, nt, b = E._nodos(nombre)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sep.inputs[0])
    sn = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Normal"], sn.inputs[0])
    ax = _m(nt, "GREATER_THAN", _m(nt, "ABSOLUTE", sn.outputs[0]), vb=0.5)            # 1 = cara que mira a ±X
    u = nt.nodes.new("ShaderNodeMix"); u.data_type = "FLOAT"
    nt.links.new(ax, u.inputs[0]); nt.links.new(sep.outputs[0], u.inputs[2]); nt.links.new(sep.outputs[1], u.inputs[3])
    uu = _m(nt, "DIVIDE", u.outputs[0], vb=modulo)
    zz = _m(nt, "DIVIDE", sep.outputs[2], vb=piso)
    fu = _m(nt, "FRACT", uu); fz = _m(nt, "FRACT", zz)
    cu = _m(nt, "FLOOR", uu); cz = _m(nt, "FLOOR", zz)
    vent = _m(nt, "MULTIPLY",
              _m(nt, "MULTIPLY", _m(nt, "GREATER_THAN", fz, vb=banda[0]), _m(nt, "LESS_THAN", fz, vb=banda[1])),
              _m(nt, "MULTIPLY", _m(nt, "GREATER_THAN", fu, vb=marco), _m(nt, "LESS_THAN", fu, vb=1 - marco * 0.3)))
    horiz = _m(nt, "GREATER_THAN", _m(nt, "ABSOLUTE", sn.outputs[2]), vb=0.5)
    vent = _m(nt, "MULTIPLY", vent, _m(nt, "SUBTRACT", va=1.0, b=horiz))
    # azar por ventana (y por edificio)
    oi = nt.nodes.new("ShaderNodeObjectInfo")
    cb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(cu, cb.inputs[0]); nt.links.new(cz, cb.inputs[1]); nt.links.new(_m(nt, "MULTIPLY", oi.outputs["Random"], vb=97.0), cb.inputs[2])
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise"); wn.noise_dimensions = "3D"; nt.links.new(cb.outputs[0], wn.inputs["Vector"])
    cuarto = E._rampa(nt, wn.outputs["Value"], (vidrio_oscuro, vidrio_oscuro * 1.05, vidrio_oscuro * 1.15),
                      (cortinas[1], cortinas[1] * 0.92, cortinas[1] * 0.8), pos=(0.55, 0.95))
    # paneles: chorreados verticales y manchas
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.06, 0.06, 0.006)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    ch = nt.nodes.new("ShaderNodeTexNoise"); ch.inputs["Scale"].default_value = 6.0; ch.inputs["Detail"].default_value = 12
    nt.links.new(mp.outputs[0], ch.inputs["Vector"])
    gr = E._ruido(nt, escala=0.04, detalle=6)
    base = E._rampa(nt, gr.outputs["Fac"], tuple(c * 0.8 for c in col_panel), col_panel, pos=(0.3, 0.7))
    suc = nt.nodes.new("ShaderNodeMix"); suc.data_type = "RGBA"
    k = E._mapa(nt, ch.outputs["Fac"], 0.0, 0.55); k.inputs["From Min"].default_value = 0.48; k.inputs["From Max"].default_value = 0.72
    nt.links.new(k.outputs[0], suc.inputs[0]); nt.links.new(base.outputs[0], suc.inputs[6])
    suc.inputs[7].default_value = (col_panel[0] * 0.5, col_panel[1] * 0.48, col_panel[2] * 0.45, 1)
    # mugre bajo cada ventana (la lluvia lava el antepecho hacia abajo)
    bajo = _m(nt, "MULTIPLY", _m(nt, "LESS_THAN", fz, vb=banda[0]), _m(nt, "SUBTRACT", va=1.0, b=_m(nt, "DIVIDE", fz, vb=banda[0])))
    suc2 = nt.nodes.new("ShaderNodeMix"); suc2.data_type = "RGBA"
    nt.links.new(_m(nt, "MULTIPLY", bajo, vb=0.0), suc2.inputs[0])
    nt.links.new(suc.outputs[2], suc2.inputs[6]); suc2.inputs[7].default_value = (0.3, 0.28, 0.26, 1)
    # techo (caras horizontales)
    tch = E._rampa(nt, gr.outputs["Fac"], tuple(c * 0.7 for c in techo), techo)
    col = nt.nodes.new("ShaderNodeMix"); col.data_type = "RGBA"
    nt.links.new(horiz, col.inputs[0]); nt.links.new(suc2.outputs[2], col.inputs[6]); nt.links.new(tch.outputs[0], col.inputs[7])
    col2 = nt.nodes.new("ShaderNodeMix"); col2.data_type = "RGBA"
    nt.links.new(vent, col2.inputs[0]); nt.links.new(col.outputs[2], col2.inputs[6]); nt.links.new(cuarto.outputs[0], col2.inputs[7])
    nt.links.new(col2.outputs[2], b.inputs["Base Color"])
    rug = nt.nodes.new("ShaderNodeMix"); rug.data_type = "FLOAT"
    nt.links.new(vent, rug.inputs[0])
    nt.links.new(E._mapa(nt, ch.outputs["Fac"], 0.32, 0.75).outputs[0], rug.inputs[2]); rug.inputs[3].default_value = 0.04
    nt.links.new(rug.outputs[0], b.inputs["Roughness"])
    met = nt.nodes.new("ShaderNodeMix"); met.data_type = "FLOAT"
    nt.links.new(vent, met.inputs[0]); met.inputs[2].default_value = metal; met.inputs[3].default_value = 0.0
    nt.links.new(_m(nt, "MULTIPLY", met.outputs[0], _m(nt, "SUBTRACT", va=1.0, b=horiz)), b.inputs["Metallic"])
    b.inputs["Specular IOR Level"].default_value = 0.5
    # ventanas prendidas (atardecer)
    if luces > 0:
        on = _m(nt, "MULTIPLY", vent, _m(nt, "GREATER_THAN", wn.outputs["Value"], vb=1.0 - luces))
        b.inputs["Emission Color"].default_value = (*col_luz, 1)
        nt.links.new(_m(nt, "MULTIPLY", on, vb=0.7), b.inputs["Emission Strength"])
    # relieve: el canto de los parteluces y la junta de los paneles
    bp_in = _m(nt, "ADD", _m(nt, "MULTIPLY", vent, vb=-1.0), _m(nt, "MULTIPLY", ch.outputs["Fac"], vb=0.2))
    E._bump(nt, b, bp_in, 0.25, 0.03)
    return neblina(m, k_neblina) if k_neblina else m


def mat_asfalto(nombre="asfalto"):
    m, nt, b = E._nodos(nombre)
    g = E._ruido(nt, escala=0.02, detalle=8)
    f = E._ruido(nt, escala=3.0, detalle=4)
    nt.links.new(E._rampa(nt, g.outputs["Fac"], (0.035, 0.035, 0.037), (0.09, 0.088, 0.085)).outputs[0], b.inputs["Base Color"])
    nt.links.new(E._mapa(nt, f.outputs["Fac"], 0.55, 0.95).outputs[0], b.inputs["Roughness"])
    E._bump(nt, b, E._ruido(nt, escala=300, detalle=2).outputs["Fac"], 0.2, 0.002)
    return neblina(m, 2600.0)


def mat_simple(nombre, color, rugo=0.6, metal=0.0, neb=True, k=2600.0):
    m = E.mat_pintura(nombre, color, rugo=(rugo - 0.15, rugo + 0.15), sucio=0.3, capa=0.0)
    m.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = metal
    return neblina(m, k) if neb else m


def mat_paneles(nombre="paneles"):
    """Paneles antirruido de la envoltura: blanco grisáceo con costillas verticales, juntas y chorreados."""
    m, nt, b = E._nodos(nombre)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sep.inputs[0])
    sn = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Normal"], sn.inputs[0])
    ax = _m(nt, "GREATER_THAN", _m(nt, "ABSOLUTE", sn.outputs[0]), vb=0.5)
    u = nt.nodes.new("ShaderNodeMix"); u.data_type = "FLOAT"
    nt.links.new(ax, u.inputs[0]); nt.links.new(sep.outputs[0], u.inputs[2]); nt.links.new(sep.outputs[1], u.inputs[3])
    cost = _m(nt, "FRACT", _m(nt, "DIVIDE", u.outputs[0], vb=0.6))
    jun = _m(nt, "FRACT", _m(nt, "DIVIDE", sep.outputs[2], vb=1.75))
    rel = _m(nt, "ADD", _m(nt, "MULTIPLY", _m(nt, "LESS_THAN", cost, vb=0.12), vb=1.0), _m(nt, "LESS_THAN", jun, vb=0.03))
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.08, 0.08, 0.008)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    ch = nt.nodes.new("ShaderNodeTexNoise"); ch.inputs["Scale"].default_value = 6.0; ch.inputs["Detail"].default_value = 12
    nt.links.new(mp.outputs[0], ch.inputs["Vector"])
    g = E._ruido(nt, escala=0.05, detalle=6)
    base = E._rampa(nt, g.outputs["Fac"], (0.36, 0.37, 0.37), (0.48, 0.49, 0.48))
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
    k = E._mapa(nt, ch.outputs["Fac"], 0.0, 0.5); k.inputs["From Min"].default_value = 0.5; k.inputs["From Max"].default_value = 0.72
    nt.links.new(k.outputs[0], mx.inputs[0]); nt.links.new(base.outputs[0], mx.inputs[6]); mx.inputs[7].default_value = (0.32, 0.31, 0.29, 1)
    nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    nt.links.new(E._mapa(nt, ch.outputs["Fac"], 0.5, 0.85).outputs[0], b.inputs["Roughness"])
    E._bump(nt, b, rel, 0.35, 0.04)
    # alfa para el corte (0 = transparente): lo maneja set_alfa()
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mxs = nt.nodes.new("ShaderNodeMixShader"); mxs.name = "ALFA"; mxs.inputs[0].default_value = 1.0
    out = nt.nodes["Material Output"]
    nt.links.new(tr.outputs[0], mxs.inputs[1]); nt.links.new(b.outputs[0], mxs.inputs[2]); nt.links.new(mxs.outputs[0], out.inputs[0])
    return neblina(m, 2600.0)


def set_alfa(m, a):
    m.node_tree.nodes["ALFA"].inputs[0].default_value = a


def mat_brillo(nombre, color, fuerza):
    """Capa de explicación (estilizada): emisión pura, no tira sombra (se le apaga en el objeto)."""
    return E.mat_emision(nombre, color, fuerza)


# ---------------------------------------------------------------- geometría
def caja(nombre, tam, pos, mat, origen_pie=True):
    """Caja con el origen al pie (z = 0 en la base) para que las fachadas cuenten los pisos desde abajo."""
    me = bpy.data.meshes.new(nombre)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= tam[0]; v.co.y *= tam[1]; v.co.z = (v.co.z + 0.5) * tam[2] if origen_pie else v.co.z * tam[2]
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(nombre, me)
    bpy.context.scene.collection.objects.link(o)
    o.location = pos
    if mat:
        o.data.materials.append(mat)
    return o


def cilindro(nombre, r, alto, pos, mat, verts=24):
    me = bpy.data.meshes.new(nombre)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r, depth=alto)
    for v in bm.verts:
        v.co.z += alto / 2
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(nombre, me)
    bpy.context.scene.collection.objects.link(o)
    o.location = pos
    if mat:
        o.data.materials.append(mat)
    return o


DIENTE, PROF = 4.0, 2.0     # fachada dentada (la de la torre real): dientes de 4 m de ancho que salen 2 m


def planta_dentada():
    """Planta de la torre: núcleo de 52 × 16 m con las dos fachadas largas en diente de sierra hasta ±10 m."""
    n = int(LX / DIENTE)
    yc = LY / 2 - PROF
    sur = []
    for i in range(n):
        x0 = -LX / 2 + i * DIENTE
        sur += [(x0, -yc), (x0 + DIENTE / 2, -LY / 2)]
    sur.append((LX / 2, -yc))
    norte = [(x, -y) for x, y in reversed(sur)]
    return sur + norte


def prisma(nombre, pts, alto, pos, mat):
    me = bpy.data.meshes.new(nombre)
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, 0.0)) for x, y in pts]
    f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [e for e in r["geom"] if isinstance(e, bmesh.types.BMVert)]:
        v.co.z = alto
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(nombre, me)
    bpy.context.scene.collection.objects.link(o)
    o.location = pos
    o.data.materials.append(mat)
    return o


def cajas_unidas(nombre, lista, mat):
    """Muchas cajas en una sola malla (ciudad lejana): lista de (cx, cy, ancho, fondo, alto)."""
    me = bpy.data.meshes.new(nombre)
    bm = bmesh.new()
    for cx, cy, w, d, h in lista:
        r = bmesh.ops.create_cube(bm, size=1.0)
        for v in r["verts"]:
            v.co.x = cx + v.co.x * w; v.co.y = cy + v.co.y * d; v.co.z = (v.co.z + 0.5) * h
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(nombre, me)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


# ---------------------------------------------------------------- la ciudad
LOTE = (70.0, 52.0)        # medio ancho del lote despejado alrededor de la torre (plaza + calles)
VECINA = (120.0, 110.0)    # torre vecina de vidrio (al noreste): de fondo de Pete en el techo


VISTAS = [((172, -360, 30), (0, 0, 8)), ((110, -230, 30), (0, 0, 8)), ((60, -260, 130), (0, 0, 8)), ((40.5, -142, 2.3), (0, 0, 10))]
AVENIDA = (16.0, 64.0, -215.0, -60.0)     # avenida despejada al sur de la torre (plano 11: la torre al fondo de la calle)


def _bajo_vista(cx, cy, alto, ancho):
    """Altura máxima que puede tener un edificio en (cx, cy) para no tapar la torre en las tomas generales."""
    lim = alto
    for (px, py, pz), (tx, ty, tz) in VISTAS:
        vx, vy = tx - px, ty - py
        L2 = vx * vx + vy * vy
        s = ((cx - px) * vx + (cy - py) * vy) / L2
        if not 0.0 < s < 1.0:
            continue
        d = math.hypot(px + s * vx - cx, py + s * vy - cy)
        if d < ancho / 2 + 34:
            lim = min(lim, max(6.0, pz + (tz - pz) * s - 6.0))
    return lim


def ciudad(sc, semilla=11, radio=1100.0, lejos=5000.0):
    random.seed(semilla)
    asf = mat_asfalto()
    piso = caja("Suelo", (14000, 14000, 0.2), (0, 0, -0.2), asf)
    # vereda y plaza alrededor de la torre
    vereda = mat_simple("vereda", (0.32, 0.31, 0.29), rugo=0.8)
    caja("Plaza", (2 * LOTE[0] - 24, 2 * LOTE[1] - 24, 0.18), (0, 0, 0), vereda)
    mats = [mat_fachada("f_hormigon", piso=3.6, modulo=2.4, banda=(0.38, 0.9), col_panel=(0.5, 0.48, 0.45), metal=0.0, luces=0.03, cortinas=(0.03, 0.06)),
            mat_fachada("f_beige", piso=3.3, modulo=1.6, banda=(0.36, 0.88), col_panel=(0.62, 0.55, 0.46), metal=0.0, luces=0.04, cortinas=(0.03, 0.06)),
            mat_fachada("f_vidrio", piso=4.0, modulo=1.5, banda=(0.08, 0.97), marco=0.04, col_panel=(0.2, 0.24, 0.27), metal=0.6, luces=0.02, cortinas=(0.02, 0.05)),
            mat_fachada("f_gris", piso=3.8, modulo=3.0, banda=(0.3, 0.86), col_panel=(0.4, 0.41, 0.42), metal=0.2, luces=0.03, cortinas=(0.03, 0.06)),
            mat_fachada("f_ladrillo", piso=3.2, modulo=2.0, banda=(0.4, 0.86), col_panel=(0.42, 0.26, 0.2), metal=0.0, luces=0.04, cortinas=(0.03, 0.06))]
    equipo = mat_simple("equipos", (0.45, 0.46, 0.45), rugo=0.5, metal=0.4)
    paso = 46.0
    n = int(radio / paso)
    edificios = []
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            cx, cy = i * paso + random.uniform(-3, 3), j * paso + random.uniform(-3, 3)
            d = math.hypot(cx, cy)
            if d > radio or (abs(cx) < LOTE[0] + 14 and abs(cy) < LOTE[1] + 14):
                continue
            if AVENIDA[0] - 14 < cx < AVENIDA[1] + 14 and AVENIDA[2] < cy < AVENIDA[3]:
                continue
            if random.random() < 0.08:
                continue                                                   # un estacionamiento o una plaza
            w, dd = random.uniform(18, 34), random.uniform(16, 32)
            alto = random.choice([random.uniform(12, 40)] * 5 + [random.uniform(40, 90)] * 3 + [random.uniform(90, 150)])
            alto *= max(0.45, 1.15 - d / radio * 0.6)
            alto = _bajo_vista(cx, cy, alto, max(w, dd))
            o = caja(f"Edif{i}_{j}", (w, dd, alto), (cx, cy, 0), random.choice(mats))
            o.rotation_euler.z = math.radians(random.choice([0, 0, 0, 2, -2]))
            edificios.append(o)
            if d < 400 and random.random() < 0.7:                          # equipos en el techo (aire, estanques)
                for _ in range(random.randint(1, 3)):
                    ew, ed, eh = random.uniform(2, 6), random.uniform(2, 5), random.uniform(1.2, 3.5)
                    e = caja(f"Eq{i}_{j}_{_}", (ew, ed, eh), (cx + random.uniform(-w / 3, w / 3), cy + random.uniform(-dd / 3, dd / 3), alto), equipo)
    # la vecina alta (vidrio), al este de la torre
    v = caja("Vecina", (34, 30, 125), (VECINA[0], VECINA[1], 0), mats[2])
    caja("VecinaTecho", (30, 26, 4), (VECINA[0], VECINA[1], 125), equipo)
    # la avenida: veredas con solera y líneas de pista
    for x in (AVENIDA[0] + 4, AVENIDA[1] - 4):
        caja(f"Vereda{x}", (8, AVENIDA[3] - AVENIDA[2], 0.16), (x, (AVENIDA[2] + AVENIDA[3]) / 2, 0), vereda)
    linea = mat_simple("linea_pista", (0.7, 0.69, 0.64), rugo=0.75)
    for k in range(int((AVENIDA[3] - AVENIDA[2]) / 9)):
        caja(f"Linea{k}", (0.18, 4.0, 0.02), ((AVENIDA[0] + AVENIDA[1]) / 2, AVENIDA[2] + 4 + 9 * k, 0), linea)
    # ciudad lejana: una sola malla
    lst = []
    for _ in range(5200):
        a = random.uniform(0, 2 * math.pi)
        d = random.uniform(radio, lejos)
        lst.append((math.cos(a) * d, math.sin(a) * d, random.uniform(14, 40), random.uniform(14, 40),
                    random.choice([random.uniform(10, 35)] * 4 + [random.uniform(35, 90)])))
    lej = mat_fachada("f_lejos", piso=3.6, modulo=2.2, col_panel=(0.5, 0.47, 0.44), metal=0.1, luces=0.03, cortinas=(0.03, 0.05), k_neblina=1500.0)
    cajas_unidas("CiudadLejos", lst, lej)
    return {"edificios": edificios, "vecina": v}


def cielo(sc):
    w, sol, d = E.cielo_atardecer(sc, elev=SOL_EL, rot=SOL_AZ, fuerza=0.2, sol=4.6, color_sol=(1.0, 0.62, 0.4))
    sc.view_settings.exposure = -0.55
    return sol


# ---------------------------------------------------------------- la torre
def torre(sc, corte=False):
    """La torre: 40 objetos-piso (fachada blanca de bandas), el sombrero (último piso + techo con parapeto y equipos) y la
    envoltura de paneles. Con corte=True arma además lo de adentro de la zona de trabajo (columnas temporales, gatas,
    losa en piezas, pozo, grúa de techo, lámparas)."""
    blanco = mat_fachada("f_torre", piso=H, modulo=1.8, banda=(0.36, 0.9), marco=0.1, col_panel=(0.8, 0.79, 0.76), metal=0.3,
                         luces=0.0, cortinas=(0.035, 0.11), k_neblina=3200.0)
    pisos = []
    pl = planta_dentada()
    base = prisma("PisoBase", pl, H, (0, 0, 0), blanco)
    pisos.append(base)
    for i in range(1, NP):
        o = base.copy(); o.name = f"Piso{i:02d}"; o.location.z = i * H
        sc.collection.objects.link(o)
        pisos.append(o)
    # base: lobby más alto y oscuro (vidrio) — el piso 0 lleva otro material
    lobby = mat_fachada("f_lobby", piso=H, modulo=3.0, banda=(0.05, 0.92), marco=0.05, col_panel=(0.25, 0.26, 0.27), metal=0.6,
                        luces=0.6, cortinas=(0.08, 0.3), k_neblina=3200.0)
    pisos[0].data = pisos[0].data.copy(); pisos[0].data.materials[0] = lobby
    # sombrero: empty que baja; adentro el último piso (con su fachada), el techo, el parapeto y los equipos
    sb = bpy.data.objects.new("Sombrero", None); sc.collection.objects.link(sb)
    cap = prisma("SombreroPiso", planta_dentada(), H, (0, 0, 2 * H), blanco); cap.parent = sb
    conc = E.mat_pintura("techo_h", (0.31, 0.30, 0.28), rugo=(0.78, 0.95), sucio=0.45, capa=0.0)   # membrana mate (el concreto pulido reflejaba el cielo)
    techo = caja("Techo", (LX + 0.6, LY + 0.6, 0.45), (0, 0, 3 * H), conc); techo.parent = sb
    par = mat_simple("parapeto", (0.7, 0.69, 0.66), rugo=0.7, neb=True, k=3200.0)
    for nom, tam, pos in (("ParN", (LX + 0.6, 0.3, 1.1), (0, LY / 2 + 0.15, 3 * H + 0.45)), ("ParS", (LX + 0.6, 0.3, 1.1), (0, -LY / 2 - 0.15, 3 * H + 0.45)),
                          ("ParE", (0.3, LY + 0.6, 1.1), (LX / 2 + 0.15, 0, 3 * H + 0.45)), ("ParO", (0.3, LY + 0.6, 1.1), (-LX / 2 - 0.15, 0, 3 * H + 0.45))):
        o = caja(nom, tam, pos, par); o.parent = sb
    eq = mat_simple("eq_techo", (0.5, 0.51, 0.5), rugo=0.45, metal=0.5, k=3200.0)
    random.seed(5)
    for k, (x, y, w, d, h) in enumerate(((-12, 3, 9, 6, 3.2), (5, 5, 6, 5, 2.6), (8, -4, 5, 4, 2.0), (23, 6, 4, 4, 4.5), (-23, 6.5, 3, 3, 1.8))):
        o = caja(f"EqT{k}", (w, d, h), (x, y, 3 * H + 0.45), eq); o.parent = sb
    # envoltura: 4 paños de paneles que tapan los 2 pisos de trabajo (un poco más grandes que la planta)
    pm = mat_paneles()
    env = {}
    m = 0.9
    for nom, tam, pos in (("EnvS", (LX + 2 * m, 0.25, 2 * H + 0.6), (0, -LY / 2 - m, -0.3)), ("EnvN", (LX + 2 * m, 0.25, 2 * H + 0.6), (0, LY / 2 + m, -0.3)),
                          ("EnvE", (0.25, LY + 2 * m, 2 * H + 0.6), (LX / 2 + m, 0, -0.3)), ("EnvO", (0.25, LY + 2 * m, 2 * H + 0.6), (-LX / 2 - m, 0, -0.3))):
        o = caja(nom, tam, pos, pm); o.parent = sb
        env[nom] = o
    # el frente (S) con su propio material para poder volverlo transparente en el corte
    pm_s = pm.copy(); pm_s.name = "paneles_frente"
    env["EnvS"].data = env["EnvS"].data.copy(); env["EnvS"].data.materials[0] = pm_s
    S = {"pisos": pisos, "sombrero": sb, "cap": cap, "env": env, "pm_s": pm_s, "h": H0, "corte": None}
    if corte:
        S["corte"] = interior(sc, sb)
    estado(S, H0)
    return S


# ---------------------------------------------------------------- adentro del sombrero (corte)
GATA, P0, TEMP = 1.8, H + 0.2, 0.6      # alto del cuerpo de la gata, pistón estirado, columna temporal (+ viga 0,9 = 2H)


TR_LY = LY / 2


def interior(sc, sb):
    """Zona de trabajo bajo el sombrero. Dos padres: "Obra" (fijo: la losa del último piso en pie, sus columnas, las
    gatas y la losa de arriba en 8 piezas) y el sombrero (baja: columnas temporales, vigas, grúa, lámparas, borde del
    corte). Coordenadas locales: z = 0 es la losa de abajo; z = 2H es la cara de abajo del sombrero."""
    ob = bpy.data.objects.new("Obra", None); sc.collection.objects.link(ob)
    hor = E.mat_hormigon("losa", (0.42, 0.41, 0.39))
    col = E.mat_hormigon("columna", (0.5, 0.49, 0.47))
    acero = E.mat_acero_industrial("acero_temp", (0.24, 0.12, 0.07), sucio=0.5)            # vigas con anticorrosivo rojizo
    amarillo = E.mat_pintura("gata", (0.85, 0.6, 0.04), rugo=(0.35, 0.6), sucio=0.35, capa=0.2)
    cromo = E.mat_metal_cepillado("piston", (0.62, 0.62, 0.63), rugo=(0.25, 0.4))
    out = {"obra": ob, "piezas": [], "cols_a": [], "cols_b": [], "gatas": [], "pistones": [], "temp": [], "lamparas": [], "luces": []}
    e = 0.3
    LY = 2 * (TR_LY - PROF)
    for nom, tam, pos in (("LosaA", (LX, (LY - POZO) / 2, e), (0, -(LY + POZO) / 4, -e)), ("LosaB", (LX, (LY - POZO) / 2, e), (0, (LY + POZO) / 4, -e)),
                          ("LosaC", ((LX - POZO) / 2, POZO, e), (-(LX + POZO) / 4, 0, -e)), ("LosaD", ((LX - POZO) / 2, POZO, e), ((LX + POZO) / 4, 0, -e))):
        o = caja(nom, tam, pos, hor); o.parent = ob
    pozo = caja("PozoNegro", (POZO, POZO, 0.05), (0, 0, -6.0), E.mat_hormigon("pozo_fondo", (0.12, 0.12, 0.12))); pozo.parent = ob
    saco = mat_simple("sacos", (0.55, 0.5, 0.42), rugo=0.9, neb=False)
    fierro = E.mat_acero_industrial("fierros", (0.2, 0.12, 0.08), sucio=0.6)
    random.seed(3)
    for k in range(16):
        x, y = random.uniform(-23, 23), random.choice([-1, 1]) * random.uniform(3.4, 7.2)
        if abs(abs(x) - 10.5) < 1.3 or abs(abs(x) - 21) < 1.3 or abs(abs(x) - 8) < 1.2 or abs(abs(x) - 24) < 1.2:
            continue
        m = fierro if k % 3 == 0 else saco
        o = caja(f"Saco{k}", (random.uniform(0.8, 1.8), random.uniform(0.7, 1.3), random.uniform(0.4, 0.9)), (x, y, 0), m)
        o.rotation_euler.z = random.uniform(-0.4, 0.4); o.parent = ob
    xs = (-LX / 2, -LX / 4, 0, LX / 4, LX / 2)
    for i in range(4):
        for j, (y0, y1) in enumerate(((-LY / 2, -POZO / 2), (POZO / 2, LY / 2))):
            x0, x1 = xs[i], xs[i + 1]
            o = caja(f"Pieza{i}{j}", (x1 - x0 - 0.15, y1 - y0 - 0.15, e), ((x0 + x1) / 2, (y0 + y1) / 2, H - e), hor)
            o.parent = ob
            o["base"] = tuple(o.location)
            out["piezas"].append(o)
    for x in (-21.0, -10.5, 10.5, 21.0):
        for y in (-6.5, 6.5):
            o = caja(f"ColB{x}{y}", (0.8, 0.8, H - e), (x, y, 0.0), col); o.parent = ob; out["cols_b"].append(o)
            o = caja(f"ColA{x}{y}", (0.8, 0.8, H - e), (x, y, H), col); o.parent = ob; out["cols_a"].append(o)
    for x in (-24.0, -16.0, -8.0, 8.0, 16.0, 24.0):
        for y in (-7.3, 7.3):
            g = cilindro(f"Gata{x}{y}", 0.45, GATA, (x, y, 0.0), amarillo, verts=32); g.parent = ob
            p = cilindro(f"Piston{x}{y}", 0.25, 1.0, (x, y, GATA), cromo, verts=24); p.parent = ob
            t = caja(f"Temp{x}{y}", (0.62, 0.62, TEMP), (x, y, GATA + P0), acero); t.parent = sb
            out["gatas"].append(g); out["pistones"].append(p); out["temp"].append(t)
    for y in (-7.3, 0.0, 7.3):
        o = caja(f"VigaR{y}", (LX - 1, 0.6, 0.9), (0, y, 2 * H - 0.9), acero); o.parent = sb
    viga = caja("GruaViga", (LX - 4, 1.0, 0.8), (0, 0, 2 * H - 1.75), acero); viga.parent = sb
    carro = caja("GruaCarro", (2.6, 2.2, 0.9), (0, 0, 2 * H - 2.65), amarillo); carro.parent = sb
    tambor = cilindro("GruaTambor", 0.5, 2.0, (0, 1.0, 2 * H - 3.1), E.mat_metal_cepillado("tambor", (0.55, 0.55, 0.57)), verts=32)
    tambor.rotation_euler.x = math.radians(90); tambor.parent = sb
    motor = caja("GruaMotor", (1.3, 1.6, 1.1), (-2.0, 0, 2 * H - 2.75), E.mat_pintura("motor", (0.12, 0.3, 0.42), capa=0.2)); motor.parent = sb
    aro = cilindro("GeneradorAro", 0.85, 0.3, (-2.75, 0, 2 * H - 2.2), mat_brillo("gen_brillo", (1.0, 0.72, 0.18), 0.0), verts=40)
    aro.rotation_euler.y = math.radians(90); aro.parent = sb; aro.visible_shadow = False
    bat = caja("Bateria", (2.4, 1.2, 1.4), (-17.0, 6.2, 0.0), E.mat_pintura("bateria", (0.2, 0.22, 0.24), capa=0.1)); bat.parent = ob
    cable = cilindro("GruaCable", 0.035, 1.0, (0, 0, 0), E.mat_cable("cable_grua", (0.09, 0.09, 0.09)), verts=8); cable.parent = sb
    gancho = caja("Gancho", (0.5, 0.35, 0.7), (0, 0, 0), E.mat_pintura("gancho", (0.85, 0.45, 0.05), capa=0.2)); gancho.parent = sb
    bulto = caja("Bulto", (3.0, 2.2, 1.4), (0, 0, 0), saco); bulto.parent = sb
    elec = mat_brillo("elec", (1.0, 0.78, 0.22), 0.0)
    ce = caja("CableLuz", (LX - 8, 0.16, 0.16), (0, -0.75, 2 * H - 1.95), elec); ce.parent = sb; ce.visible_shadow = False
    for k, x in enumerate((-20, -13, -5, 5, 13, 20)):
        lm = caja(f"Lampara{k}", (1.3, 0.5, 0.22), (x, 3.6, 2 * H - 1.75), mat_brillo(f"lamp{k}", (1.0, 0.86, 0.65), 0.0)); lm.parent = sb
        lm.visible_shadow = False
        lt = bpy.data.lights.new(f"LuzObra{k}", "AREA"); lt.energy = 0.0; lt.size = 1.3; lt.color = (1.0, 0.84, 0.62)
        lo = bpy.data.objects.new(f"LuzObra{k}", lt); sc.collection.objects.link(lo); lo.parent = sb
        lo.location = (x, 3.6, 2 * H - 1.95)
        lo.visible_glossy = False
        out["lamparas"].append(lm); out["luces"].append(lt)
    borde = mat_brillo("borde_corte", (1.0, 0.45, 0.08), 0.0)
    for nom, tam, pos in (("BordeAb", (LX + 1.9, 0.09, 0.09), (0, -TR_LY - 0.9, -0.3)), ("BordeAr", (LX + 1.9, 0.09, 0.09), (0, -TR_LY - 0.9, 2 * H + 0.3)),
                          ("BordeI", (0.09, 0.09, 2 * H + 0.6), (-LX / 2 - 0.95, -TR_LY - 0.9, -0.3)), ("BordeD", (0.09, 0.09, 2 * H + 0.6), (LX / 2 + 0.95, -TR_LY - 0.9, -0.3))):
        o = caja(nom, tam, pos, borde); o.parent = sb
        o.visible_shadow = False
    rl = bpy.data.lights.new("RellenoObra", "AREA"); rl.energy = 0.0; rl.size = 24.0; rl.color = (1.0, 0.8, 0.62)
    ro = bpy.data.objects.new("RellenoObra", rl); sc.collection.objects.link(ro); ro.parent = ob
    ro.location = (-6, -24, 4.0); ro.rotation_euler = (math.radians(78), 0, math.radians(-12))
    ro.visible_glossy = False
    fondo = bpy.data.lights.new("FondoObra", "AREA"); fondo.energy = 0.0; fondo.size = 30.0; fondo.color = (1.0, 0.86, 0.7)
    fo = bpy.data.objects.new("FondoObra", fondo); sc.collection.objects.link(fo); fo.parent = ob
    fo.location = (0, 4.0, 5.6); fo.rotation_euler = (0, 0, 0); fo.visible_glossy = False
    out["fondo"] = fondo
    out.update({"cable": cable, "gancho": gancho, "bulto": bulto, "aro": aro, "tambor": tambor, "elec": elec, "borde": borde,
                "carro": carro, "relleno": rl})
    return out


def estado(S, h, baja=0.0):
    """Deja la torre con h pisos bajo la envoltura (float). Con corte, la losa de abajo y las gatas ("Obra") quedan en
    h·H y el sombrero baja `baja` m sobre ellas (0 = gatas estiradas; H = bajó un piso)."""
    S["h"] = h
    S["sombrero"].location.z = h * H - baja
    tope = math.ceil(h - 1e-6)
    for i, o in enumerate(S["pisos"]):
        vis = i < tope
        o.hide_render = not vis
        o.hide_viewport = not vis
    c = S.get("corte")
    if c:
        c["obra"].location.z = h * H
        largo = max(0.2, P0 - baja)
        for p in c["pistones"]:
            p.scale.z = largo
    return S


def pisos_totales(h):
    return int(round(h)) + 3


def brillo(m, fuerza):
    em = next(n for n in m.node_tree.nodes if n.type == "EMISSION")
    em.inputs[1].default_value = fuerza
