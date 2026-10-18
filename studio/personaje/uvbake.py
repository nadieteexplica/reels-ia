"""Rasteriza texturas en espacio UV a partir de una función de la posición 3D (en reposo).

Sirve para pintar cejas, labios, base del pelo o el estampado de la polera directo en la textura,
así siguen a la malla cuando se deforma con huesos o shape keys.
"""
import numpy as np
import bpy


def mesh_triangles(ob, uv_name=None, filt=None):
    me = ob.data
    me.calc_loop_triangles()
    uvl = me.uv_layers[uv_name] if uv_name else me.uv_layers.active
    co = np.array([v.co[:] for v in me.vertices])
    co = (np.array(ob.matrix_world) @ np.c_[co, np.ones(len(co))].T).T[:, :3]
    uv = np.array([d.uv[:] for d in uvl.data])
    tris = np.array([t.loops[:] for t in me.loop_triangles])
    tv = np.array([t.vertices[:] for t in me.loop_triangles])
    P = co[tv]          # (n,3,3)
    U = uv[tris]        # (n,3,2)
    if filt is not None:
        keep = filt(P.mean(axis=1))
        P, U = P[keep], U[keep]
    return P, U


def rasterize(P, U, res, func, base):
    """func(pos (k,3)) -> (rgb (k,3) o None, alpha (k,)) ; se mezcla sobre 'base' (res,res,3)."""
    img = base.copy()
    pts_all, pix_all = [], []
    for p, u in zip(P, U):
        px = u * res
        x0, y0 = np.floor(px.min(axis=0)).astype(int)
        x1, y1 = np.ceil(px.max(axis=0)).astype(int)
        x0, y0 = max(x0, 0), max(y0, 0)
        x1, y1 = min(x1, res - 1), min(y1, res - 1)
        if x1 < x0 or y1 < y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        q = np.c_[gx.ravel(), gy.ravel()]
        a, b, c = px
        v0, v1 = b - a, c - a
        den = v0[0] * v1[1] - v1[0] * v0[1]
        if abs(den) < 1e-12:
            continue
        w = q - a
        l1 = (w[:, 0] * v1[1] - v1[0] * w[:, 1]) / den
        l2 = (v0[0] * w[:, 1] - w[:, 0] * v0[1]) / den
        l0 = 1 - l1 - l2
        m = (l0 >= -0.02) & (l1 >= -0.02) & (l2 >= -0.02)
        if not m.any():
            continue
        pos = l0[m, None] * p[0] + l1[m, None] * p[1] + l2[m, None] * p[2]
        pts_all.append(pos)
        pix_all.append(q[m].astype(int))
    if not pts_all:
        return img
    pos = np.concatenate(pts_all)
    pix = np.concatenate(pix_all)
    for rgb, alpha in func(pos):
        a = np.clip(alpha, 0, 1)[:, None]
        cur = img[pix[:, 1], pix[:, 0]]
        img[pix[:, 1], pix[:, 0]] = cur * (1 - a) + rgb * a
    return img


def to_image(name, arr, folder=None):
    """Guarda la textura (valores lineales) como PNG sRGB y la carga en Blender."""
    import os
    from PIL import Image
    folder = folder or os.path.join(os.environ.get("OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")), "tex")
    os.makedirs(folder, exist_ok=True)
    a = np.clip(arr, 0, 1)
    srgb = np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(a, 1 / 2.4) - 0.055)
    path = os.path.join(folder, name + ".png")
    Image.fromarray((np.flipud(srgb) * 255 + 0.5).astype(np.uint8)).save(path)
    im = bpy.data.images.get(name)
    if im:
        bpy.data.images.remove(im)
    im = bpy.data.images.load(path)
    im.name = name
    im.colorspace_settings.name = "sRGB"
    return im


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def vnoise(p, scale, seed=0):
    """Ruido de valor 3D barato (para variación de color)."""
    rng = np.random.default_rng(seed)
    perm = rng.random(4096)
    q = p * scale
    i = np.floor(q).astype(np.int64)
    f = q - i
    f = f * f * (3 - 2 * f)

    def h(ix, iy, iz):
        return perm[(ix * 73856093 ^ iy * 19349663 ^ iz * 83492791) % 4096]
    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[:, 0] if dx else 1 - f[:, 0]) * (f[:, 1] if dy else 1 - f[:, 1]) * (f[:, 2] if dz else 1 - f[:, 2])
                out = out + w * h(i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz)
    return out
