"""Hoja de revisión: renderiza vistas del personaje en una pose de Mixamo."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import bpy
import escena, anim

OUT = os.environ.get("OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
bpy.ops.wm.open_mainfile(filepath=os.environ.get("IN_BLEND", f"{OUT}/dressed.blend"))
res = tuple(int(v) for v in os.environ.get("RES", "540x960").split("x"))
sc = escena.setup(res=res, samples=int(os.environ.get("SAMPLES", 24)))
rig = bpy.data.objects["Rig"]
fbx = os.environ.get("FBX", "Happy_Idle")
frame = int(os.environ.get("FRAME", "30"))
if fbx != "rest":
    act = anim.load_action(os.environ.get("MIXAMO_DIR", "/home/claude/work/mixamo") + f"/{fbx}.fbx", rig)
    anim.assign(rig, act)
    sc.frame_set(frame)
views = {
    "cuerpo": ((0.0, -4.6, 1.25), (0, 0, 0.92), 50),
    "medio": ((-0.35, -2.0, 1.55), (0, 0, 1.32), 50),
    "cara": ((-0.22, -0.85, 1.68), (0, 0, 1.64), 70),
    "perfil": ((-0.8, -0.35, 1.68), (0, 0, 1.66), 70),
}
bpy.context.view_layer.update()
H = rig.matrix_world @ rig.pose.bones["mixamorig:Head"].head
from mathutils import Vector
def rel(v):
    return (H.x + v[0], H.y + v[1], v[2] - 1.62 + H.z)
views = {k: (rel(loc), rel(tgt), lens) if k != "cuerpo" else (loc, tgt, lens) for k, (loc, tgt, lens) in views.items()}
want = os.environ.get("VIEWS", "cuerpo,medio,cara").split(",")
tag = os.environ.get("TAG", "look")
for name in want:
    loc, tgt, lens = views[name]
    escena.camera(loc, tgt, lens)
    sc.render.filepath = f"{OUT}/{tag}_{name}.png"
    bpy.ops.render.render(write_still=True)
print("ok")
