"""Interior estilizado del Ep. 2 (dibujo animado): la lengua con sus sensores-alarma, la campanita y la molécula de capsaicina.
Metáfora declarada (no es anatomía real): un solo foco por plano, cámara S fija para la campanita."""
import math, random
import bmesh
import bpy
from mathutils import Vector, Matrix, Euler, noise

import props as P

PLATA = (0.80, 0.82, 0.86)
ROJO = (0.95, 0.04, 0.03)
NARANJO = (1.0, 0.38, 0.03)
CELESTE = (0.25, 0.70, 1.0)


def mat_lengua():
    m = bpy.data.materials.get("Lengua")
    if m:
        return m
    m = P.mat("Lengua", (0.72, 0.16, 0.24), rough=0.55, sss=0.45, coat=0.08)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Subsurface Radius"].default_value = (1.0, 0.25, 0.2)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 140.0
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    nt.links.new(vor.outputs["Distance"], inv.inputs[1])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    bump.inputs["Distance"].default_value = 0.002
    nt.links.new(inv.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def lengua(coll, largo=0.5, ancho=0.32):
    """Superficie de la lengua (vista de cerca): plano curvo y ondulado, con el surco central."""
    bm = bmesh.new()
    nx, ny = 60, 80
    vs = []
    for j in range(ny + 1):
        row = []
        for i in range(nx + 1):
            u, v = i / nx - 0.5, j / ny
            x, y = u * ancho, v * largo - largo * 0.3
            z = -abs(u) ** 2 * 0.35 - 0.01 * math.exp(-(u / 0.04) ** 2) + 0.006 * noise.noise(Vector((x * 30, y * 30, 0)))
            row.append(bm.verts.new((x, y, z)))
        vs.append(row)
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))
    ob = P.mesh_obj("Lengua", bm, coll, m=mat_lengua())
    s = ob.modifiers.new("Sub", "SUBSURF")
    s.levels = s.render_levels = 1
    return ob


def cupula(name, loc, r, coll, m=None):
    """Papila (textura de la lengua): cúpula chiquita rosada clara."""
    m = m or P.mat("SensorReposo", (0.95, 0.62, 0.62), rough=0.35, coat=0.4)   # papilas del color de la lengua (no se confunden con la campanita)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=r)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -r * 0.1], context="VERTS")
    ob = P.mesh_obj(name, bm, coll, m=m)
    ob.location = loc
    return ob


def mat_campana(color=None, brillo=0.0):
    nombre = "Campana" + ("" if color is None else f"_{int(color[0]*100)}_{int(color[1]*100)}_{int(color[2]*100)}")
    m = bpy.data.materials.get(nombre)
    if m:
        return m
    m = P.mat(nombre, PLATA if color is None else color, rough=0.18, metal=1.0 if color is None else 0.3)
    if color is not None:
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Emission Color"].default_value = (*color, 1)
        b.inputs["Emission Strength"].default_value = brillo
    return m


def campana(coll, loc=(0, 0, 0), r=0.035, color=None, brillo=0.0, nombre="Campanita"):
    """Campanita de alarma: campana clásica (boca abierta hacia abajo, con el labio ensanchado) montada sobre un pie,
    con el badajo colgando a la vista bajo el labio. Origen = base, sobre la lengua. Se lee "campana", no cúpula."""
    root = P.empty(nombre, loc=loc, coll=coll)
    m = mat_campana(color, brillo)
    metal = P.mat("BaseCampana", (0.25, 0.25, 0.28), rough=0.4, metal=0.6)
    base = P.prim("cyl", nombre + "_base", coll, metal, r=r * 0.55, r2=r * 0.45, h=r * 0.14, seg=32)
    base.location = (0, 0, r * 0.07)
    base.parent = root
    Z0 = r * 0.55                                          # altura del labio: se ve la boca y el badajo
    poste = P.prim("cyl", nombre + "_poste", coll, metal, r=r * 0.07, r2=r * 0.07, h=Z0 + r * 0.5, seg=16)
    poste.location = (0, 0, (Z0 + r * 0.5) / 2)
    poste.parent = root
    bm = bmesh.new()
    prof = [(r * 1.08, 0.0), (r * 1.02, r * 0.07), (r * 0.84, r * 0.25), (r * 0.70, r * 0.50), (r * 0.64, r * 0.75),
            (r * 0.56, r * 0.95), (r * 0.36, r * 1.08), (0.0001, r * 1.12)]
    segs = 48
    rings = [[bm.verts.new((rr * math.cos(2 * math.pi * k / segs), rr * math.sin(2 * math.pi * k / segs), z)) for k in range(segs)] for rr, z in prof]
    for i in range(len(rings) - 1):
        for k in range(segs):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % segs], rings[i + 1][(k + 1) % segs], rings[i + 1][k]))
    domo = P.mesh_obj(nombre + "_domo", bm, coll, m=m)
    sol = domo.modifiers.new("Grosor", "SOLIDIFY")
    sol.thickness = r * 0.06
    sub = domo.modifiers.new("Sub", "SUBSURF")
    sub.levels = sub.render_levels = 2
    domo.location = (0, 0, Z0)
    domo.parent = root
    perilla = P.prim("sphere", nombre + "_perilla", coll, m, r=r * 0.13)
    perilla.location = (0, 0, Z0 + r * 1.15)
    perilla.parent = root
    badajo = P.prim("sphere", nombre + "_badajo", coll, P.mat("Badajo", (0.15, 0.15, 0.17), rough=0.3, metal=0.8), r=r * 0.17)
    badajo.location = (r * 0.25, -r * 0.30, Z0 - r * 0.02)    # asoma bajo el labio, colgando del poste
    badajo.parent = root
    return root, domo


def capsaicina(coll, escala=0.012, color=ROJO, nombre="Capsaicina"):
    """Molécula de capsaicina (C18H27NO3) en bolitas y palitos, sin hidrógenos: anillo vanilílico (OH y OCH3),
    CH2–NH–C(=O) y la cadena de 8-metilnon-6-enoílo con su doble enlace trans. Coordenadas en un plano en zigzag."""
    root = P.empty(nombre, coll=coll)
    mC = P.mat(nombre + "_C", color, rough=0.25, coat=0.6, emit=0.3)
    mO = P.mat(nombre + "_O", (1.0, 0.55, 0.50), rough=0.25, coat=0.6, emit=0.3)
    mN = P.mat(nombre + "_N", (0.95, 0.80, 0.80), rough=0.25, coat=0.6, emit=0.3)
    mB = P.mat(nombre + "_enlace", (0.92, 0.88, 0.86), rough=0.4)
    L = 1.4
    at, en = {}, []
    # anillo (centro en el origen)
    for k in range(6):
        a = math.radians(90 + 60 * k)
        at[f"r{k}"] = ("C", Vector((L * math.cos(a), L * math.sin(a), 0)))
    for k in range(6):
        en.append((f"r{k}", f"r{(k + 1) % 6}", 2 if k % 2 == 0 else 1))

    def sale(desde, ang, nombre_at, elem="C", orden=1):
        p = at[desde][1] + Vector((L * math.cos(math.radians(ang)), L * math.sin(math.radians(ang)), 0))
        at[nombre_at] = (elem, p)
        en.append((desde, nombre_at, orden))

    sale("r0", 90, "CH2")                 # bencilo
    sale("CH2", 30, "N", "N")
    sale("N", 90, "Ccarb")                 # amida
    sale("Ccarb", 150, "Oc", "O", 2)
    x, ang = "Ccarb", 30
    for i in range(2, 8):                  # C2'..C7' en zigzag
        sale(x, ang, f"c{i}", "C", 2 if i == 7 else 1)
        x = f"c{i}"
        ang = 90 if ang == 30 else 30
    sale("c7", ang, "c8")
    sale("c8", 90 if ang == 30 else 30, "c9")
    sale("c8", -30 if ang == 30 else 150, "c8m")   # metilo
    sale("r2", 210, "Om", "O")             # metoxi en C3
    sale("Om", 270, "CMe")
    sale("r3", 270, "Oh", "O")             # hidroxilo en C4
    centro = sum((p for _, p in at.values()), Vector()) / len(at)
    for k, (e, p) in at.items():
        mm = {"C": mC, "O": mO, "N": mN}[e]
        b = P.prim("sphere", f"{nombre}_{k}", coll, mm, r=(0.42 if e == "C" else 0.48) * escala, u=24, v=12)
        b.location = (p - centro) * escala
        b.parent = root
    for a, b_, orden in en:
        pa, pb = (at[a][1] - centro) * escala, (at[b_][1] - centro) * escala
        d = (pb - pa)
        for o in ([0] if orden == 1 else [-1, 1]):
            off = d.cross(Vector((0, 0, 1))).normalized() * 0.12 * escala * o
            t = P.tube(f"{nombre}_e_{a}_{b_}_{o}", [tuple(pa + off), tuple((pa + pb) / 2 + off), tuple(pb + off)], 0.10 * escala, coll, mB, res=2)
            t.parent = root
    return root


def gota_sopa(coll, loc, r=0.02):
    """Gota de sopa hirviendo: naranja brillante, con vapor."""
    m = P.mat("SopaHirviendo", NARANJO, rough=0.1, emit=2.5)
    g = P.prim("sphere", "GotaSopa", coll, m, r=r)
    g.scale = (1, 1, 1.25)
    g.location = loc
    vap = P.mat("VaporSopa", (1, 1, 1), rough=0.9, alpha=0.5)
    for k in range(3):
        v = P.prim("sphere", f"VaporSopa{k}", coll, vap, r=r * (0.4 + 0.25 * k))
        v.location = Vector(loc) + Vector((0.01 * k, 0, r * (1.6 + 1.1 * k)))
    return g


def ondas(coll, centro, r0, color, n=3, nombre="Ondas"):
    """Arcos de \"está sonando\" alrededor de la campanita (dibujo animado)."""
    m = P.mat(nombre + "_m", color, rough=0.5, emit=1.5)
    out = []
    for k in range(n):
        for s in (-1, 1):
            R = r0 * (1.5 + 0.45 * k)
            pts = [Vector(centro) + Vector((s * R * math.cos(math.radians(a)), 0, R * math.sin(math.radians(a)))) for a in (-25, 0, 25)]
            t = P.tube(f"{nombre}{k}{s}", [tuple(p) for p in pts], r0 * 0.05, coll, m, res=6)
            out.append(t)
    return out
