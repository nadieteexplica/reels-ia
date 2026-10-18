"""Interior de la cabeza: piel fantasma + cerebro, paladar, lengua, vasos y trigémino.

Todo va emparentado al hueso de la cabeza del rig, así sigue al personaje.
Coordenadas en reposo (pose T, cabeza igual que en MakeHuman).
"""
import math
import bpy
import numpy as np
from mathutils import Vector, Matrix
import props as P

HEAD_BONE = "mixamorig:Head"


def parent_head(ob, rig):
    bpy.context.view_layer.update()
    mw = ob.matrix_world.copy()
    ob.parent = rig
    ob.parent_type = "BONE"
    ob.parent_bone = HEAD_BONE
    bpy.context.view_layer.update()
    ob.matrix_world = mw
    return ob


def ghost_skin(skin_mat):
    """Agrega a la piel un control 'Fantasma' (0 = piel normal, 1 = piel translúcida con borde)."""
    nt = skin_mat.node_tree
    if "Fantasma" in nt.nodes:
        return nt.nodes["Fantasma"]
    out = nt.nodes["Material Output"]
    src = out.inputs["Surface"].links[0].from_socket
    val = nt.nodes.new("ShaderNodeValue")
    val.name = val.label = "Fantasma"
    val.outputs[0].default_value = 0.0
    fres = nt.nodes.new("ShaderNodeLayerWeight")
    fres.inputs["Blend"].default_value = 0.35
    glass = nt.nodes.new("ShaderNodeBsdfPrincipled")
    glass.inputs["Base Color"].default_value = (0.95, 0.75, 0.65, 1)
    glass.inputs["Roughness"].default_value = 0.25
    glass.inputs["Emission Color"].default_value = (1.0, 0.75, 0.6, 1)
    glass.inputs["Emission Strength"].default_value = 0.35
    glass.inputs["Coat Weight"].default_value = 1.0
    transp = nt.nodes.new("ShaderNodeBsdfTransparent")
    edge = nt.nodes.new("ShaderNodeMapRange")
    edge.interpolation_type = "SMOOTHERSTEP"
    edge.inputs["From Min"].default_value = 0.30
    edge.inputs["From Max"].default_value = 0.95
    edge.inputs["To Min"].default_value = 0.05
    edge.inputs["To Max"].default_value = 0.95
    nt.links.new(fres.outputs["Facing"], edge.inputs["Value"])
    mix_g = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(edge.outputs["Result"], mix_g.inputs[0])
    nt.links.new(transp.outputs[0], mix_g.inputs[1])
    nt.links.new(glass.outputs[0], mix_g.inputs[2])
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(val.outputs[0], mix.inputs[0])
    nt.links.new(src, mix.inputs[1])
    nt.links.new(mix_g.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return val


def frost_layer(skin_mat, mask_img):
    """Capa de escarcha (azul hielo brillante) y de dolor (rojo) sobre la frente, controladas por valores animables."""
    nt = skin_mat.node_tree
    if "Escarcha" in nt.nodes:
        return nt.nodes["Escarcha"], nt.nodes["Dolor"]
    b = nt.nodes["Principled BSDF"]
    base_link = b.inputs["Base Color"].links[0].from_socket
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = mask_img
    tex.image.colorspace_settings.name = "Non-Color"
    uvn = nt.nodes.new("ShaderNodeUVMap")
    uvn.uv_map = "UV"
    nt.links.new(uvn.outputs["UV"], tex.inputs["Vector"])
    fr = nt.nodes.new("ShaderNodeValue")
    fr.name = fr.label = "Escarcha"
    pa = nt.nodes.new("ShaderNodeValue")
    pa.name = pa.label = "Dolor"
    # la escarcha crece desde el centro de la frente: umbral sobre la máscara (R = distancia, G = cristales)
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(tex.outputs["Color"], sep.inputs[0])
    thr = nt.nodes.new("ShaderNodeMath")
    thr.operation = "SUBTRACT"
    nt.links.new(fr.outputs[0], thr.inputs[0])
    nt.links.new(sep.outputs["Red"], thr.inputs[1])
    cl = nt.nodes.new("ShaderNodeMapRange")
    cl.inputs["From Min"].default_value = 0.0
    cl.inputs["From Max"].default_value = 0.08
    nt.links.new(thr.outputs[0], cl.inputs["Value"])
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.feature = "DISTANCE_TO_EDGE"
    vor.inputs["Scale"].default_value = 900.0
    nt.links.new(uvn.outputs["UV"], vor.inputs["Vector"])
    crk = nt.nodes.new("ShaderNodeMapRange")
    crk.inputs["From Min"].default_value = 0.0
    crk.inputs["From Max"].default_value = 0.12
    crk.inputs["To Min"].default_value = 1.0
    crk.inputs["To Max"].default_value = 0.85
    nt.links.new(vor.outputs["Distance"], crk.inputs["Value"])
    cr0 = nt.nodes.new("ShaderNodeMath")
    cr0.operation = "MULTIPLY"
    nt.links.new(cl.outputs["Result"], cr0.inputs[0])
    nt.links.new(crk.outputs["Result"], cr0.inputs[1])
    # sólo en la frente (canal B de la máscara, ampliado)
    fb = nt.nodes.new("ShaderNodeMapRange")
    fb.inputs["From Min"].default_value = 0.0
    fb.inputs["From Max"].default_value = 0.35
    nt.links.new(sep.outputs["Blue"], fb.inputs["Value"])
    cr = nt.nodes.new("ShaderNodeMath")
    cr.operation = "MULTIPLY"
    nt.links.new(cr0.outputs[0], cr.inputs[0])
    nt.links.new(fb.outputs["Result"], cr.inputs[1])
    mixc = nt.nodes.new("ShaderNodeMix")
    mixc.data_type = "RGBA"
    mixc.inputs["B"].default_value = (0.42, 0.72, 1.0, 1)
    nt.links.new(cr.outputs[0], mixc.inputs["Factor"])
    nt.links.new(base_link, mixc.inputs["A"])
    # dolor: rojo pulsante en la frente (canal B = máscara de frente suave)
    pm = nt.nodes.new("ShaderNodeMath")
    pm.operation = "MULTIPLY"
    nt.links.new(pa.outputs[0], pm.inputs[0])
    nt.links.new(sep.outputs["Blue"], pm.inputs[1])
    mixp = nt.nodes.new("ShaderNodeMix")
    mixp.data_type = "RGBA"
    mixp.inputs["B"].default_value = (0.9, 0.05, 0.03, 1)
    nt.links.new(pm.outputs[0], mixp.inputs["Factor"])
    nt.links.new(mixc.outputs["Result"], mixp.inputs["A"])
    nt.links.new(mixp.outputs["Result"], b.inputs["Base Color"])
    em = nt.nodes.new("ShaderNodeMath")
    em.operation = "MULTIPLY"
    em.inputs[1].default_value = 1.5
    nt.links.new(pm.outputs[0], em.inputs[0])
    b.inputs["Emission Color"].default_value = (1.0, 0.1, 0.05, 1)
    nt.links.new(em.outputs[0], b.inputs["Emission Strength"])
    # escarcha más brillante y menos rugosa
    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = 0.48
    rr.inputs["To Max"].default_value = 0.12
    nt.links.new(cr.outputs[0], rr.inputs["Value"])
    nt.links.new(rr.outputs["Result"], b.inputs["Roughness"])
    return fr, pa


def ellipsoid(name, center, radii, color, coll, rough=0.5, sss=0.2, disp=0.0, disp_scale=0.02, emit=0.0):
    ob = P.prim("sphere", name, coll, m=P.mat(name + "Mat", color, rough=rough, sss=sss, emit=emit), r=1.0, u=64, v=32)
    ob.location, ob.scale = center, radii
    ob.modifiers.new("Sub0", "SUBSURF").render_levels = 2
    if disp:
        d = ob.modifiers.new("Pliegues", "DISPLACE")
        tx = bpy.data.textures.new(name + "_tx", "MARBLE")
        tx.noise_scale = disp_scale
        tx.turbulence = 9.0
        tx.marble_type = "SHARPER"
        tx.noise_depth = 3
        d.texture, d.strength, d.texture_coords = tx, disp, "LOCAL"
        d.mid_level = 0.5
    return ob


def build(rig, eyes_center, coll):
    """Crea los órganos. Devuelve dict con los objetos y controles animables."""
    E = Vector(eyes_center)
    out = {}
    # cerebro: dos hemisferios + cerebelo
    brain_c = E + Vector((0, 0.096, 0.037))
    hemis = []
    for s in (-1, 1):
        h = ellipsoid(f"Cerebro{'LR'[s > 0]}", brain_c + Vector((s * 0.034, 0, 0)), (0.034, 0.086, 0.06), (0.86, 0.42, 0.50), coll, rough=0.45, sss=0.35, disp=0.10, disp_scale=0.18)
        hemis.append(h)
    cb = ellipsoid("Cerebelo", E + Vector((0, 0.165, -0.03)), (0.05, 0.03, 0.024), (0.80, 0.38, 0.48), coll, rough=0.45, sss=0.3, disp=0.06, disp_scale=0.12)
    out["cerebro"] = hemis + [cb]
    # lengua y paladar
    pal_pts = [(0, E.y - 0.012, E.z - 0.050), (0, E.y + 0.02, E.z - 0.044), (0, E.y + 0.055, E.z - 0.048), (0, E.y + 0.075, E.z - 0.06)]
    pal = P.tube("Paladar", pal_pts, 0.0, coll)
    pal.data.extrude = 0.0
    pal.data.bevel_depth = 0.0
    # paladar como lámina curva: perfil arqueado extruido a lo ancho
    import bmesh
    bm = bmesh.new()
    rows = []
    for i in range(14):
        t = i / 13
        y = E.y - 0.015 + 0.085 * t
        z = E.z - 0.050 + 0.008 * math.sin(math.pi * min(1, t * 1.2)) - 0.012 * max(0, t - 0.75) * 4
        row = []
        for j in range(9):
            u = (j / 8 - 0.5) * 2
            x = u * 0.023
            row.append(bm.verts.new((x, y, z - 0.006 * u * u)))
        rows.append(row)
    for i in range(13):
        for j in range(8):
            bm.faces.new((rows[i][j], rows[i][j + 1], rows[i + 1][j + 1], rows[i + 1][j]))
    palm = P.mat("PaladarMat", (0.78, 0.26, 0.30), rough=0.35, sss=0.3)
    paladar = P.mesh_obj("PaladarLamina", bm, coll, m=palm)
    paladar.modifiers.new("S", "SOLIDIFY").thickness = 0.004
    paladar.modifiers.new("Sub", "SUBSURF").render_levels = 2
    bpy.data.objects.remove(pal)
    out["paladar"] = paladar
    lengua = ellipsoid("Lengua3D", E + Vector((0, 0.030, -0.075)), (0.022, 0.048, 0.012), (0.85, 0.32, 0.36), coll, rough=0.35, sss=0.3)
    lengua.rotation_euler.x = math.radians(-6)
    out["lengua"] = lengua
    # vasos del paladar (2) — su grosor se anima
    vasos = []
    vm = P.mat("Vaso", (0.75, 0.03, 0.04), rough=0.3, sss=0.2, emit=0.0)
    for s in (-1, 1):
        pts = []
        for i in range(7):
            t = i / 6
            y = E.y + 0.062 - 0.075 * t
            pts.append((s * (0.012 - 0.004 * t), y, E.z - 0.0565 + 0.006 * math.sin(math.pi * t)))
        v = P.tube(f"VasoPaladar{'LR'[s > 0]}", pts, 0.0026, coll, m=vm)
        vasos.append(v)
        # ramitas
        for k in range(3):
            t = 0.25 + k * 0.25
            y = E.y + 0.062 - 0.075 * t
            base = (s * (0.012 - 0.004 * t), y, E.z - 0.054)
            tip = (s * 0.02, y - 0.01, E.z - 0.056)
            r = P.tube(f"Ramita{'LR'[s > 0]}{k}", [base, ((base[0] + tip[0]) / 2, y - 0.004, E.z - 0.0575), tip], 0.0014, coll, m=vm)
            vasos.append(r)
    out["vasos"] = vasos
    # trigémino: ganglio y 3 ramas por lado
    nm = P.mat("Nervio", (1.0, 0.75, 0.10), rough=0.35, emit=0.0)
    nervios = []
    for s in (-1, 1):
        g = (s * 0.042, E.y + 0.085, E.z - 0.03)
        v1 = [g, (s * 0.04, E.y + 0.04, E.z + 0.01), (s * 0.032, E.y - 0.005, E.z + 0.022), (s * 0.03, E.y - 0.022, E.z + 0.045), (s * 0.026, E.y - 0.018, E.z + 0.085)]
        v2 = [g, (s * 0.045, E.y + 0.03, E.z - 0.02), (s * 0.04, E.y - 0.01, E.z - 0.035), (s * 0.045, E.y - 0.03, E.z - 0.03)]
        v2p = [(s * 0.042, E.y + 0.02, E.z - 0.03), (s * 0.02, E.y + 0.015, E.z - 0.048), (s * 0.01, E.y - 0.0, E.z - 0.052)]
        v3 = [g, (s * 0.05, E.y + 0.06, E.z - 0.06), (s * 0.05, E.y + 0.035, E.z - 0.10), (s * 0.035, E.y - 0.01, E.z - 0.12)]
        for nmn, pts, r in (("V1", v1, 0.0011), ("V2", v2, 0.0011), ("V2pal", v2p, 0.0008), ("V3", v3, 0.0011)):
            nervios.append(P.tube(f"Trigemino{nmn}{'LR'[s > 0]}", pts, r, coll, m=nm))
        gang = P.prim("sphere", f"Ganglio{'LR'[s > 0]}", coll, m=nm, r=0.006)
        gang.location = g
        gang.scale = (1, 1.6, 0.8)
        nervios.append(gang)
    out["nervios"] = nervios
    # arteria cerebral anterior (línea media, sobre el cerebro)
    am = P.mat("Arteria", (0.85, 0.05, 0.05), rough=0.3, sss=0.2)
    art = P.tube("ArteriaCerebral", [(0, E.y + 0.06, E.z - 0.02), (0, E.y + 0.02, E.z - 0.005), (0, E.y + 0.0, E.z + 0.03), (0, E.y + 0.02, E.z + 0.07), (0, E.y + 0.08, E.z + 0.088), (0, E.y + 0.14, E.z + 0.07)], 0.0022, coll, m=am)
    out["arteria"] = art
    # signos de interrogación sobre el cerebro
    qs = []
    for k in range(3):
        q = P.text3d(f"Pregunta{k}", "?", size=0.06, extrude=0.004, bevel_d=0.0008, coll=coll, m=P.mat("Amarillo", "amarillo", rough=0.3, emit=0.4))
        q.location = brain_c + Vector((0.07 * math.cos(k * 2.1), 0.07 * math.sin(k * 2.1), 0.09))
        q.rotation_euler = (math.pi / 2, 0, 0)
        qs.append(q)
    out["preguntas"] = qs
    # helado en la boca (plano 10)
    bocado = P.prim("ico", "Bocado", coll, m=P.mat("Helado_frutilla", "frutilla"), sub=3, r=0.016)
    bocado.location = E + Vector((0, -0.005, -0.062))
    out["bocado"] = bocado
    for group in out.values():
        for ob in (group if isinstance(group, list) else [group]):
            parent_head(ob, rig)
    return out
