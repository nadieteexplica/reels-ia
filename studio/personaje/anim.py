"""Aplica una animación de Mixamo (FBX 'Without Skin') al rig propio."""
import os
import bpy

P = "mixamorig:"


DAMP = {"Neck": 0.7, "Head": 0.7}  # la captura de Mixamo exagera la cabeza: se suaviza un 30 %
# por animación: Drinking echa la cabeza atrás (tomar de botella); para comer helado la cabeza va derecha
DAMP_ACT = {"Drinking": {"Neck": 0.15, "Head": 0.15, "Spine2": 0.5, "Spine1": 0.6}}


def damp_rotations(act, damp=DAMP):
    from mathutils import Quaternion
    fcs = _fcurves(act)
    for bone, f in damp.items():
        path = f'pose.bones["{P}{bone}"].rotation_quaternion'
        q = {fc.array_index: fc for fc in fcs if fc.data_path == path}
        if len(q) != 4:
            continue
        n = len(q[0].keyframe_points)
        if any(len(q[i].keyframe_points) != n for i in range(4)):
            continue
        ident = Quaternion()
        for k in range(n):
            cur = Quaternion([q[i].keyframe_points[k].co.y for i in range(4)])
            new = ident.slerp(cur, f)
            for i in range(4):
                kp = q[i].keyframe_points[k]
                d = new[i] - kp.co.y
                kp.co.y += d
                kp.handle_left.y += d
                kp.handle_right.y += d


def load_action(fbx_path, rig, name=None, damp=True):
    before = set(bpy.data.objects)
    acts_before = set(bpy.data.actions)
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    new_objs = [o for o in bpy.data.objects if o not in before]
    src = [o for o in new_objs if o.type == "ARMATURE"][0]
    act = src.animation_data.action
    act = act.copy()
    act.name = name or os.path.splitext(os.path.basename(fbx_path))[0]
    scale = 0.01 * rig["hips_z"] / rig["src_hips_z"]
    for fc in _fcurves(act):
        if fc.data_path == f'pose.bones["{P}Hips"].location':
            for kp in fc.keyframe_points:
                kp.co.y *= scale
                kp.handle_left.y *= scale
                kp.handle_right.y *= scale
    if damp:
        base = os.path.splitext(os.path.basename(fbx_path))[0]
        damp_rotations(act, DAMP_ACT.get(base, DAMP))
    for o in new_objs:
        bpy.data.objects.remove(o)
    for a in set(bpy.data.actions) - acts_before - {act}:
        bpy.data.actions.remove(a)
    act.use_fake_user = True
    return act


def _fcurves(act):
    # Blender 5: acciones por capas/slots
    if hasattr(act, "fcurves") and act.fcurves:
        return list(act.fcurves)
    out = []
    for layer in act.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                out.extend(bag.fcurves)
    return out


def assign(rig, act):
    if not rig.animation_data:
        rig.animation_data_create()
    rig.animation_data.action = act
    if hasattr(rig.animation_data, "action_slot") and act.slots:
        rig.animation_data.action_slot = act.slots[0]
    return act.frame_range
