"""Carga la malla base de MakeHuman (CC0) y aplica targets con los pesos macro de MakeHuman 1.1.

Unidades de MakeHuman: decímetros, eje Y hacia arriba.
"""
import os
import numpy as np

MH = os.environ.get("MH_DATA", "/tmp/mhcheck/makehuman/data")


def load_obj(path=None):
    path = path or os.path.join(MH, "3dobjs", "base.obj")
    verts, uvs, faces, groups = [], [], [], []
    cur = None
    with open(path) as f:
        for line in f:
            if line.startswith("v "):
                verts.append([float(x) for x in line.split()[1:4]])
            elif line.startswith("vt "):
                uvs.append([float(x) for x in line.split()[1:3]])
            elif line.startswith("g "):
                cur = line.split(None, 1)[1].strip()
            elif line.startswith("f "):
                vi, ti = [], []
                for tok in line.split()[1:]:
                    p = tok.split("/")
                    vi.append(int(p[0]) - 1)
                    ti.append(int(p[1]) - 1 if len(p) > 1 and p[1] else -1)
                faces.append((vi, ti))
                groups.append(cur)
    return np.array(verts, dtype=np.float64), np.array(uvs), faces, groups


_cache = {}


def load_target(rel):
    if rel in _cache:
        return _cache[rel]
    idx, off = [], []
    with open(os.path.join(MH, "targets", rel)) as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            p = line.split()
            idx.append(int(p[0]))
            off.append([float(p[1]), float(p[2]), float(p[3])])
    t = (np.array(idx, dtype=np.int64), np.array(off, dtype=np.float64).reshape(-1, 3))
    _cache[rel] = t
    return t


def add(v, rel, w):
    if abs(w) < 1e-6:
        return
    i, o = load_target(rel)
    v[i] += o * w


def macro_weights(gender=1.0, age_years=25, muscle=0.5, weight=0.5, race=None):
    """Pesos de MakeHuman 1.1 (humanmodifier.MacroModifier)."""
    race = race or {"caucasian": 1 / 3, "african": 1 / 3, "asian": 1 / 3}
    s = sum(race.values())
    race = {k: v / s for k, v in race.items()}
    # años -> slider
    age = (age_years - 1) / 48.0 if age_years < 25 else 0.5 + (age_years - 25) / 130.0
    if age < 0.5:
        old = 0.0
        baby = max(0.0, 1 - age * 5.333)
        young = max(0.0, (age - 0.1875) * 3.2)
        child = max(0.0, min(1.0, 5.333 * age) - young)
    else:
        child = baby = 0.0
        old = max(0.0, age * 2 - 1)
        young = 1 - old
    ages = {"baby": baby, "child": child, "young": young, "old": old}
    genders = {"male": gender, "female": 1 - gender}

    def tri(x, lo, mid, hi):
        if x < 0.5:
            return {lo: 1 - x * 2, mid: x * 2, hi: 0.0}
        return {lo: 0.0, mid: 1 - (x - 0.5) * 2, hi: (x - 0.5) * 2}

    muscles = tri(muscle, "minmuscle", "averagemuscle", "maxmuscle")
    weights = tri(weight, "minweight", "averageweight", "maxweight")
    return genders, ages, muscles, weights, race


def apply_macros(v, gender=1.0, age_years=25, muscle=0.5, weight=0.5, race=None,
                 height=0.5, proportions=0.5):
    g, a, m, w, r = macro_weights(gender, age_years, muscle, weight, race)
    for gk, gv in g.items():
        for ak, av in a.items():
            for rk, rv in r.items():
                add(v, f"macrodetails/{rk}-{gk}-{ak}.target", rv * gv * av)
            for mk, mv in m.items():
                for wk, wv in w.items():
                    base = gv * av * mv * wv
                    if base < 1e-6:
                        continue
                    add(v, f"macrodetails/universal-{gk}-{ak}-{mk}-{wk}.target", base)
                    if height > 0.5:
                        add(v, f"macrodetails/height/{gk}-{ak}-{mk}-{wk}-maxheight.target", base * (height - 0.5) * 2)
                    elif height < 0.5:
                        add(v, f"macrodetails/height/{gk}-{ak}-{mk}-{wk}-minheight.target", base * (0.5 - height) * 2)
                    if proportions > 0.5:
                        add(v, f"macrodetails/proportions/{gk}-{ak}-{mk}-{wk}-idealproportions.target", base * (proportions - 0.5) * 2)
                    elif proportions < 0.5:
                        add(v, f"macrodetails/proportions/{gk}-{ak}-{mk}-{wk}-uncommonproportions.target", base * (0.5 - proportions) * 2)
    return v


def expression_units(race):
    """Devuelve {nombre: (idx, offsets)} mezclando las unidades de expresión por raza."""
    s = sum(race.values())
    names = sorted(n[:-7] for n in os.listdir(os.path.join(MH, "targets/expression/units/caucasian")) if n.endswith(".target"))
    out = {}
    for n in names:
        acc = {}
        for rk, rv in race.items():
            i, o = load_target(f"expression/units/{rk}/{n}.target")
            for ii, oo in zip(i, o):
                acc[ii] = acc.get(ii, 0) + oo * (rv / s)
        idx = np.array(sorted(acc))
        out[n] = (idx, np.array([acc[k] for k in idx]))
    return out


def group_vertices(faces, groups, name):
    s = set()
    for (vi, _), g in zip(faces, groups):
        if g == name:
            s.update(vi)
    return sorted(s)


def joint_positions(v, faces, groups):
    js = {}
    for g in set(groups):
        if g and g.startswith("joint-"):
            idx = group_vertices(faces, groups, g)
            js[g[6:]] = v[idx].mean(axis=0)
    return js
