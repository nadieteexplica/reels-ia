"""Kit de anatomía real a partir de Z-Anatomy (CC BY-SA 4.0, modelos derivados de BodyParts3D CC BY-SA 2.1 JP).

Extrae del atlas las piezas de la cabeza que usan los videos del cuerpo y las guarda unidas por grupo
en `anatomia_cabeza.blend` (coordenadas del atlas, en metros, con -Y hacia adelante como nuestro personaje).

Uso: ZANAT=/ruta/Startup.blend OUT=carpeta python anatomia_kit.py
Créditos obligatorios en la descripción del video: ver studio/plantilla/LICENCIAS_ANATOMIA.md
"""
import os, re, json
import bpy, bmesh
from mathutils import Vector

SRC = os.environ.get("ZANAT", "/tmp/zanat/Z-Anatomy/Startup.blend")
OUT = os.environ.get("OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=SRC)
dg = bpy.context.evaluated_depsgraph_get()


def objs_in(coll_name):
    c = bpy.data.collections.get(coll_name)
    out = set()
    if not c:
        return out

    def rec(cc):
        for o in cc.objects:
            out.add(o)
        for ch in cc.children:
            rec(ch)
    rec(c)
    return out


def real(o):
    if o.type == "MESH":
        return len(o.data.vertices) > 8
    if o.type == "CURVE":
        return len(o.data.splines) > 0
    return False


INTERNO = re.compile(r"ventricle|nucleus|nuclei|thalam|putamen|pallid|hippocamp|amygdal|fornix|commissure|callosum|septum|septal|stria|habenula|"
                     r"geniculate|mamillary|optic|white matter|caudate|lentiform|grey matter|aqueduct|rhomboid|roof of|tract|lemniscus|peduncle", re.I)

groups = {}
cerebrum = [o for o in objs_in("Cerebrum") if real(o) and not INTERNO.search(o.name)]
SENS = re.compile(r"^Postcentral gyrus")
groups["Cerebro"] = [o for o in cerebrum if not SENS.match(o.name)]
groups["CortezaSensitiva"] = [o for o in cerebrum if SENS.match(o.name)]
groups["Cerebelo"] = [o for o in objs_in("Cerebellum") if real(o) and not INTERNO.search(o.name)]
groups["TroncoEncefalico"] = [o for o in objs_in("Brainstem") if real(o) and not INTERNO.search(o.name)]
allm = [o for o in bpy.data.objects if real(o)]
HUESO = re.compile(r"^(Frontal bone|Parietal bone|Occipital bone|Sphenoid bone|Temporal bone|Ethmoid bone|Maxilla|Palatine bone|Zygomatic bone|"
                   r"Nasal bone|Lacrimal bone|Vomer|Inferior nasal concha)(\.[lr])?$")
huesos = [o for o in allm if o.type == "MESH" and HUESO.match(o.name)]
BOVEDA = re.compile(r"^(Frontal bone|Parietal bone|Occipital bone)")
groups["Boveda"] = [o for o in huesos if BOVEDA.search(o.name)]
groups["CraneoBase"] = [o for o in huesos if not BOVEDA.search(o.name)]
groups["Mandibula"] = [o for o in allm if o.name == "Mandible"]
groups["Dientes"] = [o for o in allm if re.search(r"(incisor|canine|premolar|molar tooth)\.[lr]$", o.name, re.I) and o.type == "MESH"]
groups["Lengua"] = [o for o in allm if o.name == "Tongue"]
groups["PaladarBlando"] = [o for o in allm if o.name in ("Soft palate", "Uvula of palate")]
groups["Ojos"] = [o for o in allm if re.match(r"^(Sclera|Cornea|Lens)\.[lr]$", o.name)]
trig = [o for o in objs_in("Trigeminal nerve (V)") if real(o) and not re.search(r"muscle|masseter|belly", o.name, re.I)]
groups["TrigeminoV1"] = [o for o in trig if o.name.startswith("Ophthalmic nerve")]
groups["TrigeminoV2"] = [o for o in trig if o.name.startswith(("Maxillary nerve", "Meningeal branch of maxillary"))]
groups["TrigeminoRaiz"] = [o for o in trig if o.name.startswith(("Trigeminal nerve (V)", "Sensory root", "Motor root"))]
groups["TrigeminoV3"] = [o for o in trig if o not in groups["TrigeminoV1"] + groups["TrigeminoV2"] + groups["TrigeminoRaiz"]]
groups["ArteriaCerebralAnterior"] = [o for o in allm if re.match(r"^(Anterior cerebral artery|Orbitofrontal branches of anterior cerebral artery)\.[lr]$", o.name)]
groups["Arterias"] = [o for o in allm if re.match(r"^(Internal carotid artery|Middle cerebral artery.*|Posterior cerebral artery|Basilar artery|"
                                                  r"Insular branches of middle cerebral artery.*|Temporal branches of middle cerebral artery|"
                                                  r"Parietal branches of middle cerebral artery|Ophthalmic artery)(\.[lr])?$", o.name)]

def mucosa():
    bm = bmesh.new()
    for n in ("Maxilla.l", "Maxilla.r", "Palatine bone.l", "Palatine bone.r"):
        o = bpy.data.objects.get(n)
        if not o:
            continue
        me = o.data.copy()
        me.transform(o.matrix_world)
        tmp = bmesh.new()
        tmp.from_mesh(me)
        tmp.normal_update()
        keep = [f for f in tmp.faces if f.normal.z < -0.55 and abs(f.calc_center_median().x) < 0.021 and 1.535 < f.calc_center_median().z < 1.575]
        kill = [f for f in tmp.faces if f not in set(keep)]
        bmesh.ops.delete(tmp, geom=kill, context="FACES")
        tmp.to_mesh(me)
        tmp.free()
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    return bm


RADIO = {"TrigeminoV1": 0.0012, "TrigeminoV2": 0.0012, "TrigeminoV3": 0.0012, "TrigeminoRaiz": 0.0014, "ArteriaCerebralAnterior": 0.0016, "Arterias": 0.0014}

info = {}
new_objs = []
for gname, members in groups.items():
    bm = bmesh.new()
    names = []
    for o in sorted(members, key=lambda x: x.name):
        if o.type == "CURVE":
            r = RADIO.get(gname, 0.001)
            o.data.bevel_depth = r
            o.data.bevel_resolution = 3
            o.data.use_fill_caps = True
        oe = o.evaluated_get(bpy.context.evaluated_depsgraph_get())
        try:
            me = oe.to_mesh()
        except RuntimeError:
            continue
        if me is None or len(me.vertices) == 0:
            oe.to_mesh_clear()
            continue
        me = me.copy()
        oe.to_mesh_clear()
        me.transform(o.matrix_world)
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
        names.append(o.name)
    if len(bm.verts) == 0:
        print("vacío", gname)
        bm.free()
        continue
    me = bpy.data.meshes.new(f"Anat_{gname}")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(f"Anat_{gname}", me)
    new_objs.append(ob)
    info[gname] = {"piezas": len(names), "vertices": len(me.vertices), "nombres": names}
    print(f"{gname}: {len(names)} piezas, {len(me.vertices)} vértices")


bmm = mucosa()
if len(bmm.verts):
    for v in bmm.verts:
        v.co.z -= 0.0008
    me = bpy.data.meshes.new("Anat_PaladarMucosa")
    bmm.to_mesh(me)
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new("Anat_PaladarMucosa", me)
    new_objs.append(ob)
    print("PaladarMucosa:", len(me.vertices), "vértices")
bmm.free()


def center(names):
    pts = []
    for n in names:
        o = bpy.data.objects.get(n)
        if o and o.type == "MESH":
            pts += [o.matrix_world @ v.co for v in o.data.vertices]
    return sum(pts, Vector()) / len(pts)


eL = center(["Posterior segment of eyeball.l", "Anterior segment of eyeball.l"])
eR = center(["Posterior segment of eyeball.r", "Anterior segment of eyeball.r"])
inc = center(["Upper medial incisor.l", "Upper medial incisor.r"])
meta = {"ojo_l": list(eL), "ojo_r": list(eR), "ojos_centro": list((eL + eR) / 2), "distancia_ojos": (eL - eR).length,
        "incisivos_sup": list(inc), "grupos": info,
        "licencia": "Z-Anatomy CC BY-SA 4.0 (https://www.z-anatomy.com) · BodyParts3D, The Database Center for Life Science, CC BY-SA 2.1 JP"}
json.dump(meta, open(os.path.join(OUT, "anatomia_cabeza.json"), "w"), indent=1)
path = os.path.join(OUT, "anatomia_cabeza.blend")
bpy.data.libraries.write(path, set(new_objs), fake_user=True)
print("ok", path, os.path.getsize(path) // 1e6, "MB")
