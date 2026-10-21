"""Dónde quedan los ojos de cada personaje en pantalla (para el chequeo automático "cara tapada").

Lo usa plano.py después de cada `actualizar(f)`: guarda en el meta del cuadro `"ojos": [[x, y, r, nombre], ...]`
(píxeles de 1080x1920, y hacia abajo; r = radio aproximado del ojo en pantalla). `tools/auditor/chequeo_planos.py`
cruza esos puntos con las cajas de los gráficos (`graficos.json`) y de los subtítulos (`subs_log.json`).

Un objeto cuenta como ojo si tiene la propiedad `ojo` (ob["ojo"] = 1) o si su nombre termina en `_ojo`, `_ojoL` u
`_ojoR` (así ya se llaman los de `personajes.py` del Ep. 2), o si se llama `Ojo.L` / `Ojo.R` (protagonista humano). Sólo se guardan los ojos que la cámara ve: dentro del
cuadro, delante de la cámara, sin ocultar y sin otro objeto entre medio (rayo desde la cámara).
"""
import re

import bpy
from mathutils import Vector

PATRON = re.compile(r"(^|[_.])[Oo]jo([._]?[LR])?(\.\d+)?$")     # Cuitlacoche_ojoR (Ep. 2) · Ojo.L (protagonista humano)


def es_ojo(ob):
    return ob.type == "MESH" and (bool(ob.get("ojo")) or bool(PATRON.search(ob.name)))


def marcar(*obs):
    """Marca objetos como ojos (para personajes nuevos cuyos ojos no se llamen *_ojoL / *_ojoR)."""
    for ob in obs:
        ob["ojo"] = 1


def _visible(ob):
    p = ob
    while p is not None:
        if p.hide_render:
            return False
        p = p.parent
    return True


def ojos_en_pantalla(sc, cam=None, w=1080, h=1920):
    from bpy_extras.object_utils import world_to_camera_view
    cam = cam or sc.camera
    if cam is None:
        return []
    dg = bpy.context.evaluated_depsgraph_get()
    origen = cam.matrix_world.translation
    out = []
    for ob in sc.objects:
        if not es_ojo(ob) or not _visible(ob):
            continue
        esquinas = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        centro = sum(esquinas, Vector()) / 8
        v = world_to_camera_view(sc, cam, centro)
        if v.z <= 0 or not (-0.05 <= v.x <= 1.05 and -0.05 <= v.y <= 1.05):
            continue
        radio = max((c - centro).length for c in esquinas) / 1.732          # esfera: esquina = r·√3
        borde = world_to_camera_view(sc, cam, centro + cam.matrix_world.to_3x3() @ Vector((radio, 0, 0)))
        r_px = max(4, round(abs(borde.x - v.x) * w))
        # oclusión: lo primero que toca el rayo desde la cámara tiene que ser el ojo (o algo pegado a él)
        d = centro - origen
        dist = d.length
        hit, loc, _n, _i, obj, _m = sc.ray_cast(dg, origen, d.normalized(), distance=dist + 0.01)
        if hit and obj is not None and obj != ob and obj.parent != ob and (loc - origen).length < dist - 2.5 * radio:
            continue
        out.append([round(v.x * w), round((1 - v.y) * h), r_px, ob.name])
    return out
