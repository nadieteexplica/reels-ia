"""Escena de estudio reutilizable: fondo celeste/turquesa, luz suave de 3 puntos, cámara vertical."""
import math
import bpy
from mathutils import Vector


def material(name, color, rough=0.5, sss=0.0, sss_radius=(0.8, 0.35, 0.2), metallic=0.0, sheen=0.0, coat=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    if sss:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Radius"].default_value = sss_radius
        b.inputs["Subsurface Scale"].default_value = 0.012
    if sheen:
        b.inputs["Sheen Weight"].default_value = sheen
    if coat:
        b.inputs["Coat Weight"].default_value = coat
    return m


def setup(res=(1080, 1920), samples=64, bg_top=(0.10, 0.52, 0.78), bg_bottom=(0.03, 0.30, 0.42)):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.cycles.transparent_max_bounces = 8
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
    sc.render.image_settings.file_format = "PNG"

    # Mundo: luz ambiente suave
    w = bpy.data.worlds.get("Estudio") or bpy.data.worlds.new("Estudio")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (*bg_top, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25

    # Ciclorama (piso curvo) con degradado vertical
    if "Ciclorama" not in bpy.data.objects:
        bpy.ops.mesh.primitive_plane_add(size=1)
        cyc = bpy.context.active_object
        cyc.name = "Ciclorama"
        me = cyc.data
        import bmesh
        bm = bmesh.new()
        W, R, H, D = 12.0, 1.5, 8.0, 6.0
        n = 16
        pts = [(0, -D, 0), (0, 2.0, 0)]
        for i in range(1, n + 1):
            a = i / n * math.pi / 2
            pts.append((0, 2.0 + R * math.sin(a), R - R * math.cos(a)))
        pts.append((0, 2.0 + R, H))
        rows = []
        for x in (-W / 2, W / 2):
            rows.append([bm.verts.new((x, y, z)) for _, y, z in pts])
        for i in range(len(pts) - 1):
            bm.faces.new((rows[0][i], rows[1][i], rows[1][i + 1], rows[0][i + 1]))
        bm.to_mesh(me)
        bm.free()
        for p in me.polygons:
            p.use_smooth = True
        m = bpy.data.materials.new("Fondo")
        m.use_nodes = True
        nt = m.node_tree
        bsdf = nt.nodes["Principled BSDF"]
        bsdf.inputs["Roughness"].default_value = 0.9
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = 0.0
        mr.inputs["From Max"].default_value = 3.0
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (*bg_bottom, 1)
        ramp.color_ramp.elements[1].color = (*bg_top, 1)
        nt.links.new(geo.outputs["Position"], sep.inputs[0])
        nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
        nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        me.materials.append(m)

    def area(name, loc, energy, size, color=(1, 1, 1)):
        L = bpy.data.lights.get(name) or bpy.data.lights.new(name, "AREA")
        L.energy, L.size, L.color = energy, size, color
        L.shape = "DISK"
        ob = bpy.data.objects.get(name) or bpy.data.objects.new(name, L)
        if ob.name not in sc.collection.objects:
            sc.collection.objects.link(ob)
        ob.location = loc
        d = Vector((0, 0, 1.3)) - Vector(loc)
        ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        return ob

    area("Key", (-1.6, -2.4, 2.6), 160, 2.0, (1.0, 0.96, 0.9))
    area("Fill", (2.2, -2.0, 1.6), 45, 2.5, (0.9, 0.95, 1.0))
    area("Rim", (1.2, 2.2, 2.8), 220, 1.2, (1.0, 0.97, 0.92))
    area("RimL", (-1.5, 1.8, 2.4), 110, 1.0, (0.85, 0.95, 1.0))
    return sc


def camera(loc, target, lens=50):
    sc = bpy.context.scene
    cam = bpy.data.objects.get("Cam")
    if cam is None:
        cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
        sc.collection.objects.link(cam)
    cam.data.lens = lens
    cam.data.sensor_fit = "VERTICAL"
    cam.data.sensor_height = 24 * 16 / 9 * 0.5 + 12  # vertical cómodo
    cam.location = loc
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    return cam
