"""Clip de prueba: personaje con una animación de Mixamo, encuadre vertical de plano medio."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import bpy
import escena, anim

OUT = os.environ.get("OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
bpy.ops.wm.open_mainfile(filepath=os.environ.get("IN_BLEND", f"{OUT}/personaje.blend"))
res = tuple(int(v) for v in os.environ.get("RES", "360x640").split("x"))
sc = escena.setup(res=res, samples=int(os.environ.get("SAMPLES", 10)))
sc.cycles.use_adaptive_sampling = True
sc.render.use_persistent_data = True
rig = bpy.data.objects["Rig"]
fbx = os.environ.get("FBX", "Focus")
act = anim.load_action(os.environ.get("MIXAMO_DIR", "/home/claude/work/mixamo") + f"/{fbx}.fbx", rig)
anim.assign(rig, act)
cam = escena.camera((-0.45, -2.3, 1.52), (0, 0, 1.38), 50)
EXPR = {  # frame: {shape key: valor}
    "Focus": [
        (1, {}), (6, {"eye-left-closure": .8, "eye-right-closure": .8, "eyebrows-left-inner-up": .7, "eyebrows-right-inner-up": .7,
                       "eyebrows-left-down": .5, "eyebrows-right-down": .5, "mouth-depression-retraction": .6, "nose-left-elevation": .5, "nose-right-elevation": .5}),
        (92, {"eye-left-closure": .7, "eye-right-closure": .7, "eyebrows-left-inner-up": .6, "eyebrows-right-inner-up": .6,
              "eyebrows-left-down": .4, "eyebrows-right-down": .4, "mouth-depression-retraction": .5, "nose-left-elevation": .4, "nose-right-elevation": .4}),
        (104, {"eyebrows-left-up": .6, "eyebrows-right-up": .6, "eye-left-opened-up": .4, "eye-right-opened-up": .4, "mouth-open": .25}),
        (126, {"eyebrows-left-up": .3, "eyebrows-right-up": .3, "mouth-open": .1}),
        (128, {"eye-left-closure": 1, "eye-right-closure": 1, "eyebrows-left-up": .3, "eyebrows-right-up": .3}),
        (131, {"eyebrows-left-up": .2, "eyebrows-right-up": .2}),
        (150, {"mouth-corner-puller": .35, "eyebrows-left-up": .15, "eyebrows-right-up": .15}),
    ],
}.get(fbx, [])
keyed = [o for o in bpy.data.objects if o.type == "MESH" and o.data.shape_keys]
names = sorted({k for _, d in EXPR for k in d})
for f, d in EXPR:
    for o in keyed:
        kb = o.data.shape_keys.key_blocks
        for n in names:
            if n in kb:
                kb[n].value = d.get(n, 0.0)
                kb[n].keyframe_insert("value", frame=f)
import mathutils
smooth_t = None
f0, f1, step = (int(x) for x in os.environ.get("FRAMES", "1,90,1").split(","))
d = os.path.join(OUT, f"clip_{fbx}")
os.makedirs(d, exist_ok=True)
for i, f in enumerate(range(f0, f1 + 1, step)):
    sc.frame_set(f)
    # cámara viva: sigue la cabeza suave, cara en el tercio superior, acercamiento lento
    t = i / max(1, (f1 - f0) // step)
    bpy.context.view_layer.update()
    H = rig.matrix_world @ rig.pose.bones["mixamorig:Head"].head
    tgt = mathutils.Vector((H.x * 0.6, H.y, H.z - 0.20))
    smooth_t = tgt if smooth_t is None else smooth_t.lerp(tgt, 0.15)
    dist = 1.55 - 0.25 * t
    cam.location = smooth_t + mathutils.Vector((-0.35 * dist / 1.55, -dist, 0.06))
    cam.rotation_euler = (smooth_t - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(d, f"{i:04d}.png")
    bpy.ops.render.render(write_still=True)
print("ok clip")
