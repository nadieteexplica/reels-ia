"""Ficha y 3 vistas de prueba de un personaje FBX (Mixamo With Skin).
  python ver_personaje.py <personaje.fbx> <estudio.hdr> <carpeta_salida>
Deja <nombre>_ficha.json (objetos, huesos, materiales, texturas con tamaño, medidas) y <nombre>_vistas.jpg."""
import json, math, os, sys
import bpy
from mathutils import Vector

fbx, hdr, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
nombre = os.path.splitext(os.path.basename(fbx))[0].lower()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=fbx, automatic_bone_orientation=False)
sc = bpy.context.scene
mallas = [o for o in sc.objects if o.type == "MESH"]
arm = next((o for o in sc.objects if o.type == "ARMATURE"), None)
pts = [o.matrix_world @ Vector(c) for o in mallas for c in o.bound_box]
lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
ficha = {"archivo": os.path.basename(fbx), "alto_m": round(hi.z - lo.z, 3), "ancho_m": round(hi.x - lo.x, 3),
         "mallas": [{"nombre": o.name, "vertices": len(o.data.vertices), "materiales": [m.name for m in o.data.materials if m],
                     "shape_keys": [k.name for k in o.data.shape_keys.key_blocks] if o.data.shape_keys else []} for o in mallas],
         "huesos": [b.name for b in arm.data.bones] if arm else [],
         "imagenes": [{"nombre": i.name, "tam": list(i.size), "empacada": bool(i.packed_file)} for i in bpy.data.images],
         "materiales": {}}
for m in bpy.data.materials:
    if not m.use_nodes:
        continue
    nodos = {}
    for n in m.node_tree.nodes:
        if n.type == "TEX_IMAGE" and n.image:
            destino = [l.to_socket.name for l in n.outputs[0].links]
            nodos[n.image.name] = destino
    ficha["materiales"][m.name] = nodos
json.dump(ficha, open(os.path.join(out, f"{nombre}_ficha.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: ficha[k] for k in ("alto_m", "ancho_m")}), len(ficha["huesos"]), "huesos")

# mundo: HDRI de estudio + piso gris; AgX; Cycles con denoise
w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
nt = w.node_tree
if os.path.exists(hdr):
    env = nt.nodes.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(hdr)
    nt.links.new(env.outputs[0], nt.nodes["Background"].inputs[0])
nt.nodes["Background"].inputs[1].default_value = 1.0
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, lo.z))
piso = bpy.context.object
pm = bpy.data.materials.new("piso"); pm.use_nodes = True
pm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.35, 0.55, 0.62, 1)
pm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
piso.data.materials.append(pm)
sc.render.engine = "CYCLES"; sc.cycles.samples = 48; sc.cycles.use_denoising = True
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
sc.render.resolution_x, sc.render.resolution_y = 540, 960
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
alto = hi.z - lo.z
centro = (lo + hi) / 2
vistas = [("frente", 0, 0.5, 4.2 * alto / 1.8, 50), ("tres_cuartos", 35, 0.55, 3.6 * alto / 1.8, 50),
          ("cara", 20, 0.92, 1.1 * alto / 1.8, 85)]
from PIL import Image
imgs = []
for nom, ang, alt, dist, lente in vistas:
    a = math.radians(ang)
    obj = Vector((centro.x, centro.y, lo.z + alto * alt))
    # Mixamo mira hacia -Y en Blender tras importar (frente = +Y de la cámara hacia -Y): se ubica la cámara en -Y
    cam.location = obj + Vector((math.sin(a) * dist, -math.cos(a) * dist, 0.05 * alto))
    d = obj - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lente
    cam.data.dof.use_dof = True; cam.data.dof.focus_distance = d.length; cam.data.dof.aperture_fstop = 2.8
    p = os.path.join(out, f"{nombre}_{nom}.png"); sc.render.filepath = p
    bpy.ops.render.render(write_still=True)
    imgs.append(Image.open(p).convert("RGB"))
hoja = Image.new("RGB", (540 * 3, 960))
for i, im in enumerate(imgs):
    hoja.paste(im, (540 * i, 0))
hoja.save(os.path.join(out, f"{nombre}_vistas.jpg"), quality=88)
for v in vistas:
    os.remove(os.path.join(out, f"{nombre}_{v[0]}.png"))
print("ok")
