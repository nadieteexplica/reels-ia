"""Interior "lengua" (cámara S) del Ep. 2, animable: lengua de plastilina con papilas, campanita plateada, ondas, luz,
molécula de capsaicina y gota de sopa. Sale de estilo_lengua.py (cuadro de estilo aprobado en la puerta 4, c3 r3).

armar(sc) devuelve un dict S con las piezas; poner(S, ...) deja el estado de un cuadro."""
import math, os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.abspath(os.path.join(HERE, "../../.."))
for p in (HERE, os.path.join(STUDIO, "plantilla")):
    if p not in sys.path:
        sys.path.insert(0, p)
import bpy
from mathutils import Vector, Euler
import props as P
import lengua as LG
import ep02 as E2

COLORES = {"roja": LG.ROJO, "naranja": LG.NARANJO, "celeste": LG.CELESTE}


def armar(sc):
    w = sc.world.node_tree.nodes["Background"]
    w.inputs["Color"].default_value = (0.20, 0.03, 0.05, 1)
    w.inputs["Strength"].default_value = 0.6
    C = P.collection("Lengua")
    XL = -0.055
    LG.lengua(C, largo=1.0, y0=-0.62, ancho=0.27, x0=XL, surco=0.016)
    pal = P.prim("sphere", "Paladar", C, P.mat("Paladar", (0.35, 0.05, 0.07), rough=0.5, sss=0.3), r=0.6)
    pal.scale = (1.0, 1.4, 0.7)
    pal.location = (0, 0.25, 0.05)
    for p_ in pal.data.polygons:
        p_.flip()
    bpy.context.view_layer.update()
    lg = bpy.data.objects["Lengua"]
    dg = bpy.context.evaluated_depsgraph_get()
    Mi = lg.matrix_world.inverted()

    def sobre(x, y):
        hit, loc, nor, _ = lg.evaluated_get(dg).ray_cast(Mi @ Vector((x, y, 0.5)), Vector((0, 0, -1)))
        return (loc.z, nor) if hit else (None, None)

    chica = P.mat("SensorReposo", (0.74, 0.38, 0.42), rough=0.75)
    grande = P.mat("PapilaGrande", (0.70, 0.29, 0.34), rough=0.72)
    for m_ in (chica, grande):
        m_.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.2
    # material de papila "encendida" (plano 7: se encienden en fila, blanco neutro)
    enc = P.mat("PapilaEncendida", (0.95, 0.93, 0.90), rough=0.5, emit=0.0)
    rp = random.Random(5)
    puestas, papilas, intentos = [], [], 0
    while len(puestas) < 420 and intentos < 40000:
        intentos += 1
        x, y = rp.uniform(XL - 0.15, XL + 0.15), rp.uniform(-0.34, 0.32)
        big = rp.random() < 0.07
        r = rp.uniform(0.0052, 0.0064) if big else rp.uniform(0.0026, 0.0046)
        if (x ** 2 + (y - 0.02) ** 2) ** 0.5 < 0.05 or abs(x - XL) < 0.011:
            continue
        if any((x - a) ** 2 + (y - b) ** 2 < (r + c + 0.0035) ** 2 for a, b, c in puestas):
            continue
        z, nor = sobre(x, y)
        if z is None or nor.z < 0.55:
            continue
        puestas.append((x, y, r))
        cp = LG.cupula(f"Sensor{len(puestas)}", (x, y, z - 0.0006), r, C, m=grande if big else chica)
        cp.rotation_euler = Vector(nor).to_track_quat("Z", "Y").to_euler()
        cp.scale = (1, 1, 0.65)
        papilas.append((cp, x, y, r))
    ZC = sobre(0, 0.02)[0] - 0.0008
    camp, domo = LG.campana(C, loc=(0, 0.02, ZC), r=0.035, color=None)
    # el domo y la perilla mezclan plata con celeste (plano 15 y 31: "queda celeste")
    plata = domo.data.materials[0]
    m = plata.copy()
    m.name = "CampanaMezcla"
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    out = nt.nodes["Material Output"]
    cel = nt.nodes.new("ShaderNodeBsdfPrincipled")
    cel.inputs["Base Color"].default_value = (*LG.CELESTE, 1)
    cel.inputs["Roughness"].default_value = 0.35
    cel.inputs["Metallic"].default_value = 0.4
    cel.inputs["Emission Color"].default_value = (*LG.CELESTE, 1)
    cel.inputs["Emission Strength"].default_value = 0.25
    mix = nt.nodes.new("ShaderNodeMixShader")
    val = nt.nodes.new("ShaderNodeValue")
    val.outputs[0].default_value = 0.0
    nt.links.new(val.outputs[0], mix.inputs["Fac"])
    nt.links.new(b.outputs[0], mix.inputs[1])
    nt.links.new(cel.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    domo.data.materials[0] = m
    perilla = bpy.data.objects["Campanita_perilla"]
    perilla.data.materials[0] = m
    ondas = LG.ondas(C, (0, 0.02, 0.050 + ZC), 0.040, LG.ROJO, tope_izq=12, tope_der=12)
    ondas_m = sorted({o.data.materials[0] for o in ondas}, key=lambda mm: mm.name)
    luz = bpy.data.lights.new("LuzCampana", "POINT")
    luz.energy, luz.color, luz.shadow_soft_size = 0.0, LG.ROJO, 0.02
    lo = bpy.data.objects.new("LuzCampana", luz)
    C.objects.link(lo)
    lo.location = (0, -0.035, 0.03 + ZC)
    # molécula: posición calzada sobre la perilla (como en el cuadro de estilo)
    ESC = 0.0050
    mol = LG.capsaicina(C, escala=ESC)
    mol.rotation_euler = (math.radians(90), math.radians(-100), 0)
    bpy.context.view_layer.update()
    oh = bpy.data.objects["Capsaicina_Oh"]
    r_at = 0.48 * ESC
    piezas = [o for o in bpy.data.objects if o.name.startswith("Campanita") and o.type == "MESH"]
    dg = bpy.context.evaluated_depsgraph_get()

    def techo(p):
        best = None
        for o in piezas:
            Mo = o.matrix_world.inverted()
            hit, loc, *_ = o.evaluated_get(dg).ray_cast(Mo @ Vector((p.x, p.y, 1.0)), (Mo.to_3x3() @ Vector((0, 0, -1))).normalized())
            if hit:
                z = (o.matrix_world @ loc).z
                best = z if best is None else max(best, z)
        return best

    perilla_w = perilla.matrix_world.translation
    mol.location = mol.location + (perilla_w + Vector((0, 0, 0.035 * 0.13 + r_at * 0.85)) - oh.matrix_world.translation)
    bpy.context.view_layer.update()
    alza = 0.0
    for a_ in [a for a in mol.children if "_e_" not in a.name]:
        wpos = a_.matrix_world.translation
        for dx, dy in ((0, 0), (r_at * 0.7, 0), (-r_at * 0.7, 0), (0, r_at * 0.7), (0, -r_at * 0.7)):
            t = techo(wpos + Vector((dx, dy, 0)))
            if t is not None and t + r_at * 0.9 - wpos.z > alza:
                alza = t + r_at * 0.9 - wpos.z
    mol.location.z += alza
    mol_calzada = mol.location.copy()
    mol_rot = mol.rotation_euler.copy()
    gota = LG.gota_sopa(C, (0.05, -0.01, 0.03 + ZC), r=0.012)
    gota_obs = [gota] + [o for o in bpy.data.objects if o.name.startswith("VaporSopa")]
    for o in gota_obs:                                  # apoyada en la lengua (no flotando)
        o.location.z -= 0.03 - 0.0135
    gota_base = {o.name: o.location.copy() for o in gota_obs}
    E2.area(sc, "Key", (-0.25, -0.30, 0.35 + ZC), 4, 0.35, (1.0, 0.92, 0.85), (0, 0.02, 0.03 + ZC))
    E2.area(sc, "Rim", (0.25, 0.35, 0.25 + ZC), 7, 0.3, (1.0, 0.6, 0.6), (0, 0.02, 0.03 + ZC))
    cam = E2.camara(sc, "CamS", lens=30, fstop=3.5)
    cam_pos = Vector((0.0, -0.36, 0.17 + ZC))
    cam_tgt = Vector((0, 0.05, -0.023 + ZC))
    foco = Vector((0, 0.02, 0.04 + ZC))
    E2.mirar(cam, cam_pos, cam_tgt, foco=foco)
    S = dict(C=C, ZC=ZC, camp=camp, domo=domo, mix=val, perilla=perilla, ondas=ondas, ondas_m=ondas_m, luz=luz, luz_ob=lo,
             mol=mol, mol_calzada=mol_calzada, mol_rot=mol_rot, gota_obs=gota_obs, gota_base=gota_base, cam=cam,
             cam_pos=cam_pos, cam_tgt=cam_tgt, foco=foco, papilas=papilas, enc=enc, sc=sc)
    poner(S)
    return S


def poner(S, color=None, suena=0.0, fase=0.0, celeste=0.0, mol=None, gota=None, empuje=0.0):
    """Estado de un cuadro.
    color: 'roja'|'naranja'|'celeste'|None (de las ondas y la luz) · suena: 0..1 (intensidad del timbre) · fase: s (vibración)
    celeste: 0..1 (tinte del domo) · mol: None (oculta) o 0..1 (0 = afuera a la izquierda, 1 = calzada) o Vector (posición)
    gota: None (oculta) o 0..1 (0 = arriba, 1 = apoyada junto a la campana) · empuje: 0..1 del push-in de la cámara S."""
    S["mix"].outputs[0].default_value = celeste
    col = COLORES.get(color)
    # vibración del timbre: la campana se mece y las ondas laten de adentro hacia afuera
    S["camp"].rotation_euler = (0, math.radians(7.0 * suena * math.sin(fase * 2 * math.pi * 9)), 0)
    for k, m in enumerate(S["ondas_m"]):
        em = m.node_tree.nodes["Emission"]
        if col and suena > 0:
            em.inputs["Color"].default_value = (*col, 1)
            pulso = 0.55 + 0.45 * math.sin(fase * 2 * math.pi * 3 - k * 1.3)
            em.inputs["Strength"].default_value = 2.2 * (0.62 ** k) * suena * pulso
        else:
            em.inputs["Strength"].default_value = 0.0
    for o in S["ondas"]:
        o.hide_render = not (col and suena > 0.02)
    if col and suena > 0:
        S["luz"].color = col
        S["luz"].energy = 0.6 * suena * (0.85 + 0.15 * math.sin(fase * 2 * math.pi * 6))
    else:
        S["luz"].energy = 0.0
    m = S["mol"]
    if mol is None:
        E2.oculto(m, True)
    else:
        E2.oculto(m, False)
        if isinstance(mol, (int, float)):
            afuera = S["mol_calzada"] + Vector((-0.20, -0.02, 0.07))
            m.location = afuera.lerp(S["mol_calzada"], mol)
            m.rotation_euler = Euler((S["mol_rot"].x, S["mol_rot"].y + math.radians(25) * (1 - mol), S["mol_rot"].z))
        else:
            m.location = Vector(mol)
    for o in S["gota_obs"]:
        o.hide_render = gota is None
        if gota is not None:
            base = S["gota_base"][o.name]
            o.location = base + Vector((0, 0, 0.12 * (1 - E2.entra(gota)) ** 1.0))
    E2.mirar(S["cam"], S["cam_pos"].lerp(S["cam_tgt"], 0.08 * empuje), S["cam_tgt"], foco=S["foco"])
