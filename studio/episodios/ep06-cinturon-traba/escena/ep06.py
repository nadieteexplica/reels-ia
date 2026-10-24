"""Base del Ep. 6 (el cinturón que se traba), estilo REALISTA (el del Ep. 5): reusa el kit del Ep. 5 (`kit5.py`: materiales
sucios, cielo físico, cerros con neblina, cámara y luces) y agrega lo de esta idea:
  - el desierto de Atacama con un camino de tierra y un cerro de roca empinado (30°);
  - el 4x4 "A Land Explorer (Free)" de Danila Davydov (Sketchfab, CC-BY: crédito en la descripción), con interior;
  - los 4 personajes de Mixamo With Skin (Release privado Personajes: RACE, castle.guard, GAS.MASK, chad), sentados;
  - el cinturón de cada uno (cinta sobre una curva de 3 anclas colgada de los huesos);
  - el retractor por dentro (carrete, rueda dentada, anillo dentado, pestillo, tacita, bolita y palanquita);
  - la bolsa de papas genérica (sin marca).
Coordenadas del auto: la trompa mira a −y, el copiloto va del lado −x (volante a la izquierda, Latam), piso en z = 0.
Sol fijo (storyboard v2): del lado del copiloto, adelantado 30° desde el costado → azimut 240°, 3,5° de alto."""
import math, os, random, sys
import bpy, bmesh
from mathutils import Vector, Euler, Matrix, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit5 as K
from kit5 import (asset, escena, camara, apuntar, luz_area, luz_punto, asignar, liso, cilindro, caja, _nodos, _ruido,
                  _rampa, _mapa, _bump, mat_metal_cepillado, mat_pintura, mat_goma, mat_emision, mat_vidrio, mat_lejano,
                  cerros, cielo_atardecer)
from kit5 import T, F, FR, FPS, FIN     # tiempos de los planos (la hoja de muestras de render-planos los lee de acá)

AUTO_GLB = "343551d39d87444997962ed73a924917.glb"
SOL_AZ, SOL_ELEV = 240.0, 3.5
FBX = {"piloto": "RACE.fbx", "caballero": "castle.guard.fbx", "mascara": "GAS.MASK.fbx", "doctor": "chad.fbx"}
SENTADO_FBX = "Sitting.Laughing.fbx"
# asientos (centro de la cadera sentada, en coordenadas del auto; medidos en el modelo: delanteros y ≈ 0,27, banca y ≈ 1,23)
# medidos con rayos en el modelo: cojín delantero z 0,92 (y −0,05…0,3), respaldo y 0,4–0,6; tablero arriba z 1,31–1,36
# (y −0,6…−0,35), cara del tablero y −0,33; banca de atrás z 0,95 (y 0,8–1,0), respaldo y 1,2–1,35; pilar B x ±0,72, y 0,7–0,85
# medido con rayos en el modelo (23-oct): cojín adelante z 0,92 y respaldo en y 0,34–0,54; cojín atrás z 0,95 y respaldo en
# y 1,1–1,3; techo por dentro a 1,73–1,79; tablero arriba z ~1,32 entre y −0,55 y −0,29; parabrisas muy inclinado de
# (y −0,55, z 1,33) a (y −0,15, z 1,70); pilar B en y ~0,40–0,45 (cara de adentro en |x| 0,59); pilar C en y ~1,2–1,4.
ASIENTO = {"piloto": (0.37, 0.20, 1.00), "caballero": (-0.37, 0.20, 1.00),
           "doctor": (0.40, 0.95, 1.03), "mascara": (-0.40, 0.95, 1.03)}
PILAR_GUIA = {"caballero": (-0.60, 0.45, 1.55), "piloto": (0.60, 0.45, 1.55),
              "mascara": (-0.62, 1.25, 1.55), "doctor": (0.62, 1.25, 1.55)}
RETRACTOR = (-0.62, 0.45, 0.75)      # abajo en el pilar B del copiloto, a la altura del asiento
TABLERO_CENTRO = (0.0, -0.40, 1.34)
BOLSA = (0.0, -0.40, 1.36)
# el techo de la cabina queda a 0,84 m del cojín: con su altura de Mixamo (1,77–1,97 m) las cabezas lo atraviesan
ESCALA = {"caballero": 0.80, "piloto": 0.87, "mascara": 0.87, "doctor": 0.87}


SOL_AZ_CERRO = 270.0     # en la subida (E3): de costado puro desde el lado del copiloto, para que la ladera reciba luz rasante


def sol(sc, fuerza_cielo=0.22, sol=4.0, az=None, elev=None):
    return cielo_atardecer(sc, elev=SOL_ELEV if elev is None else elev, rot=SOL_AZ if az is None else az, fuerza=fuerza_cielo, sol=sol)


# ---------------------------------------------------------------- suelo del desierto y cerro de roca
def mat_tierra(nombre="tierra", escala=1.0):
    """Tierra suelta del desierto: polvo café claro con manchas grandes, piedrecillas (voronoi) y huellas finas."""
    m, nt, b = _nodos(nombre)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    grande = _ruido(nt, escala=0.05 * escala, detalle=8)
    medio = _ruido(nt, escala=0.8 * escala, detalle=10)
    base0 = _rampa(nt, grande.outputs["Fac"], (0.30, 0.20, 0.13), (0.52, 0.38, 0.26))
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs[0].default_value = 0.45
    nt.links.new(base0.outputs[0], mix.inputs[6])
    nt.links.new(_rampa(nt, medio.outputs["Fac"], (0.7, 0.66, 0.62), (1.0, 1.0, 1.0)).outputs[0], mix.inputs[7])
    vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 18 * escala; vo.inputs["Randomness"].default_value = 1
    nt.links.new(tc.outputs["Object"], vo.inputs["Vector"])
    piedra = _mapa(nt, vo.outputs["Distance"], 1.0, 0.0); piedra.inputs["From Max"].default_value = 0.22
    pc = nt.nodes.new("ShaderNodeMix"); pc.data_type = "RGBA"
    k = nt.nodes.new("ShaderNodeMath"); k.operation = "GREATER_THAN"; k.inputs[1].default_value = 0.55
    nt.links.new(piedra.outputs[0], k.inputs[0])
    nt.links.new(k.outputs[0], pc.inputs[0]); nt.links.new(mix.outputs[2], pc.inputs[6]); pc.inputs[7].default_value = (0.24, 0.19, 0.16, 1)
    nt.links.new(pc.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.95
    b.inputs["Specular IOR Level"].default_value = 0.25
    fino = _ruido(nt, escala=90 * escala, detalle=4)
    suma = nt.nodes.new("ShaderNodeMath"); suma.operation = "ADD"
    nt.links.new(piedra.outputs[0], suma.inputs[0]); nt.links.new(fino.outputs["Fac"], suma.inputs[1])
    _bump(nt, b, suma.outputs[0], 0.6, 0.01)
    return m


def mat_roca(nombre="roca", color=(0.30, 0.22, 0.18), escala=0.6):
    """Roca de cerro cerca: capas inclinadas, manchas de óxido, vetas claras y polvo encima de lo que mira arriba (sin
    patrones repetidos: el voronoi de grietas se leía como barro seco de maqueta)."""
    m, nt, b = _nodos(nombre)
    capas = _ruido(nt, escala=escala, detalle=12, estirar=(1, 1, 5))
    manchas = _ruido(nt, escala=escala * 0.22, detalle=8)
    fino = _ruido(nt, escala=escala * 18, detalle=6)
    r0 = _rampa(nt, capas.outputs["Fac"], tuple(c * 0.5 for c in color), color, pos=(0.3, 0.7))
    ox = nt.nodes.new("ShaderNodeMix"); ox.data_type = "RGBA"
    kox = _mapa(nt, manchas.outputs["Fac"], 0.0, 0.55); kox.inputs["From Min"].default_value = 0.5; kox.inputs["From Max"].default_value = 0.7
    nt.links.new(kox.outputs[0], ox.inputs[0]); nt.links.new(r0.outputs[0], ox.inputs[6]); ox.inputs[7].default_value = (0.40, 0.21, 0.12, 1)
    vt = nt.nodes.new("ShaderNodeMix"); vt.data_type = "RGBA"
    kv = _mapa(nt, manchas.outputs["Fac"], 0.0, 0.5); kv.inputs["From Min"].default_value = 0.30; kv.inputs["From Max"].default_value = 0.2
    nt.links.new(kv.outputs[0], vt.inputs[0]); nt.links.new(ox.outputs[2], vt.inputs[6]); vt.inputs[7].default_value = (0.5, 0.45, 0.4, 1)
    geo = nt.nodes.new("ShaderNodeNewGeometry"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Normal"], sep.inputs[0])
    pv = _mapa(nt, sep.outputs["Z"], 0.0, 0.65); pv.inputs["From Min"].default_value = 0.6
    po = nt.nodes.new("ShaderNodeMix"); po.data_type = "RGBA"
    nt.links.new(pv.outputs[0], po.inputs[0]); nt.links.new(vt.outputs[2], po.inputs[6]); po.inputs[7].default_value = (0.5, 0.38, 0.27, 1)
    nt.links.new(po.outputs[2], b.inputs["Base Color"])
    nt.links.new(_mapa(nt, fino.outputs["Fac"], 0.75, 0.98).outputs[0], b.inputs["Roughness"])
    suma = nt.nodes.new("ShaderNodeMath"); suma.operation = "ADD"
    nt.links.new(capas.outputs["Fac"], suma.inputs[0]); nt.links.new(fino.outputs["Fac"], suma.inputs[1])
    _bump(nt, b, suma.outputs[0], 0.7, 0.04)
    return m


def desierto(sc, lado=40000.0):
    """Llano de tierra del desierto (40 km: llega hasta los cerros) con un relieve suave cerca."""
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=240, y_subdivisions=240, size=400, location=(0, 0, 0))
    cerca = bpy.context.object; cerca.name = "TierraCerca"
    tx = bpy.data.textures.new("lomas", "CLOUDS"); tx.noise_scale = 30
    d = cerca.modifiers.new("lomas", "DISPLACE"); d.texture = tx; d.strength = 0.6; d.mid_level = 0.5; d.texture_coords = "GLOBAL"
    liso(cerca, 180); asignar(cerca, mat_tierra())
    bpy.ops.mesh.primitive_plane_add(size=lado, location=(0, 0, -0.35))
    lejos = bpy.context.object; lejos.name = "TierraLejos"
    asignar(lejos, mat_tierra("tierra_lejos", escala=0.2))
    return cerca


def cerro_roca(sc, pendiente=30.0, origen=(0.0, -2.0, 0.0), largo=20.0, ancho=30.0):
    """Ladera de roca que sube hacia −y con la pendiente dada (el camino que trepa el 4x4) y que cae a un precipicio del lado −x.
    Devuelve una función z(y) de la ladera para apoyar el auto."""
    ox, oy, oz = origen
    t = math.tan(math.radians(pendiente))
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=200, y_subdivisions=260, size=1, location=(0, 0, 0))
    g = bpy.context.object; g.name = "Cerro"
    for v in g.data.vertices:
        x = v.co.x * ancho; y = -v.co.y * largo - largo / 2      # de y = 0 a y = −largo
        z = min(max(0.0, -y), largo * 0.92) * t        # arriba, una cima plana (plano 21)
        # precipicio del lado −x (donde mira el de la máscara): el borde cae
        if x < -6:
            z -= (-6 - x) ** 1.6 * 0.9
        v.co = Vector((ox + x, oy + y, oz + z))
    # la huella del camino (x entre −1,4 y 1,4) queda casi lisa; afuera, roca con bloques grandes
    vg = g.vertex_groups.new(name="roca")
    for v in g.data.vertices:
        k = min(1.0, max(0.0, (abs(v.co.x - ox) - 1.4) / 1.6))
        vg.add([v.index], k, "REPLACE")
    tx = bpy.data.textures.new("rocas", "CLOUDS"); tx.noise_scale = 2.4; tx.noise_depth = 6; tx.noise_type = "HARD_NOISE"
    d = g.modifiers.new("rocas", "DISPLACE"); d.texture = tx; d.strength = 1.1; d.mid_level = 0.45; d.texture_coords = "GLOBAL"; d.vertex_group = "roca"
    tx3 = bpy.data.textures.new("piedrecillas", "CLOUDS"); tx3.noise_scale = 0.25; tx3.noise_depth = 3
    d3 = g.modifiers.new("piedrecillas", "DISPLACE"); d3.texture = tx3; d3.strength = 0.05; d3.texture_coords = "GLOBAL"
    liso(g, 180)
    g.data.materials.append(mat_roca()); g.data.materials.append(mat_tierra("tierra_camino", escala=1.5))
    for p in g.data.polygons:
        c = sum((g.data.vertices[i].co for i in p.vertices), Vector()) / len(p.vertices)
        p.material_index = 1 if abs(c.x - ox) < 1.6 else 0
    # piedras sueltas al lado del camino
    random.seed(4)
    roca = mat_roca("roca_suelta", (0.34, 0.25, 0.2), escala=2.0)
    for i in range(45):
        y = -random.uniform(0, largo * 0.9); x = random.choice((-1, 1)) * random.uniform(2.4, 7)
        z = min(max(0.0, -y), largo * 0.92) * t
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=random.uniform(0.15, 0.6), location=(ox + x, oy + y, oz + z))
        p = bpy.context.object; p.scale = (1, random.uniform(0.6, 1.3), random.uniform(0.4, 0.8))
        p.rotation_euler = (random.random() * 3, random.random() * 3, random.random() * 3)
        dd = p.modifiers.new("d", "DISPLACE"); tt = bpy.data.textures.new(f"p{i}", "CLOUDS"); tt.noise_scale = 0.4; dd.texture = tt; dd.strength = 0.12
        liso(p, 180); asignar(p, roca)
    return lambda y: min(max(0.0, -(y - oy)), largo * 0.92) * t + oz


# ---------------------------------------------------------------- el 4x4
def ensuciar(mat, polvo=(0.56, 0.45, 0.34), k=0.45):
    """Capa de polvo procedural sobre el material del modelo (todo sucio: lo limpio delata la maqueta). Más polvo abajo y en
    lo que mira arriba; también mancha la tapicería crema de adentro."""
    nt = mat.node_tree
    b = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if not b:
        return
    ent = b.inputs["Base Color"]
    src = ent.links[0].from_socket if ent.links else None
    nz = _ruido(nt, escala=3.0, detalle=10)
    nz2 = _ruido(nt, escala=40.0, detalle=4)
    k1 = _mapa(nt, nz.outputs["Fac"], 0.0, k); k1.inputs["From Min"].default_value = 0.42; k1.inputs["From Max"].default_value = 0.7
    k2 = nt.nodes.new("ShaderNodeMath"); k2.operation = "MULTIPLY"
    nt.links.new(k1.outputs[0], k2.inputs[0]); nt.links.new(_mapa(nt, nz2.outputs["Fac"], 0.6, 1.0).outputs[0], k2.inputs[1])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    nt.links.new(k2.outputs[0], mix.inputs[0])
    if src:
        nt.links.remove(ent.links[0]); nt.links.new(src, mix.inputs[6])
    else:
        mix.inputs[6].default_value = ent.default_value
    mix.inputs[7].default_value = (*polvo, 1)
    nt.links.new(mix.outputs[2], ent)
    r = b.inputs["Roughness"]
    if r.links:
        s2 = r.links[0].from_socket; nt.links.remove(r.links[0])
        mx = nt.nodes.new("ShaderNodeMath"); mx.operation = "MAXIMUM"
        nt.links.new(s2, mx.inputs[0]); nt.links.new(k2.outputs[0], mx.inputs[1]); nt.links.new(mx.outputs[0], r)


def auto(sc, sin_vidrios=False):
    """Importa el 4x4 (CC-BY), lo ensucia y lo cuelga de un vacío 'Auto' con el origen en el piso, en el centro de las ruedas
    traseras (así inclinarlo en la subida lo hace pivotar en el eje de atrás). Devuelve el vacío."""
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=asset(AUTO_GLB))
    nuevos = [o for o in bpy.data.objects if o not in antes]
    raiz = bpy.data.objects.new("Auto", None); sc.collection.objects.link(raiz)
    for o in nuevos:
        if o.parent is None:
            o.parent = raiz
        if o.type == "MESH" and "Glass" in o.name:
            o.hide_render = sin_vidrios
            # en Cycles el vidrio con transmisión corta el sol directo: la cabina quedaba negra. El vidrio refleja
            # igual, pero deja pasar la sombra (la luz del sol entra por las ventanas como en la vida real).
            o.visible_shadow = False
    for m in {s.material for o in nuevos if o.type == "MESH" for s in o.material_slots if s.material}:
        if "glass" not in m.name.lower():
            ensuciar(m)
        else:
            vidrio_delgado(m)
    return raiz


def vidrio_delgado(m):
    """El vidrio del modelo era alfa con una textura en grilla (oscuro y con cuadritos desde adentro). Lo cambio por vidrio
    delgado: transparente levemente verdoso + reflejo según Fresnel, con polvo que lo opaca un poco en manchas."""
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); tr.inputs["Color"].default_value = (0.86, 0.9, 0.88, 1)
    gl = nt.nodes.new("ShaderNodeBsdfGlossy"); gl.inputs["Roughness"].default_value = 0.04
    fr = nt.nodes.new("ShaderNodeFresnel"); fr.inputs["IOR"].default_value = 1.52
    nz = _ruido(nt, escala=6.0, detalle=8)
    polvo = _mapa(nt, nz.outputs["Fac"], 0.0, 0.10); polvo.inputs["From Min"].default_value = 0.45; polvo.inputs["From Max"].default_value = 0.75
    df = nt.nodes.new("ShaderNodeBsdfDiffuse"); df.inputs["Color"].default_value = (0.5, 0.42, 0.33, 1)
    mx1 = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(fr.outputs[0], mx1.inputs[0]); nt.links.new(tr.outputs[0], mx1.inputs[1]); nt.links.new(gl.outputs[0], mx1.inputs[2])
    mx2 = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(polvo.outputs[0], mx2.inputs[0]); nt.links.new(mx1.outputs[0], mx2.inputs[1]); nt.links.new(df.outputs[0], mx2.inputs[2])
    nt.links.new(mx2.outputs[0], out.inputs["Surface"])
    try:
        m.surface_render_method = "BLENDED"
    except Exception:
        pass


EJE_TRASERO_Y = 1.44     # contacto de la rueda de atrás con el suelo (medido en el modelo; trompa a −y)


def poner_auto(raiz, grados=0.0, y_contacto=EJE_TRASERO_Y, z_contacto=0.0):
    """Apoya el auto con la rueda de atrás en (0, y_contacto, z_contacto) e inclinado `grados` con la trompa arriba
    (pivota en el contacto de la rueda trasera)."""
    R = Matrix.Rotation(math.radians(-grados), 4, "X")
    piv = Vector((0, EJE_TRASERO_Y, 0))
    raiz.rotation_euler = (math.radians(-grados), 0, 0)
    raiz.location = Vector((0, y_contacto, z_contacto)) - (R @ piv)
    bpy.context.view_layer.update()
    global MARCO
    MARCO = raiz.matrix_world.copy()


# ---------------------------------------------------------------- bolsa de papas genérica
def mat_bolsa(nombre="bolsa"):
    """Bolsa metalizada arrugada, naranja con una franja crema (genérica: sin marca, sin letras, sin colores de una marca)."""
    m, nt, b = _nodos(nombre)
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    fr = _mapa(nt, sep.outputs["Z"], 0.0, 1.0); fr.inputs["From Min"].default_value = -0.01; fr.inputs["From Max"].default_value = 0.01
    col = nt.nodes.new("ShaderNodeMix"); col.data_type = "RGBA"
    nt.links.new(fr.outputs[0], col.inputs[0]); col.inputs[6].default_value = (0.75, 0.28, 0.06, 1); col.inputs[7].default_value = (0.85, 0.75, 0.55, 1)
    nt.links.new(col.outputs[2], b.inputs["Base Color"])
    b.inputs["Metallic"].default_value = 0.55
    arr = _ruido(nt, escala=45, detalle=6)
    nt.links.new(_mapa(nt, arr.outputs["Fac"], 0.25, 0.5).outputs[0], b.inputs["Roughness"])
    _bump(nt, b, arr.outputs["Fac"], 0.5, 0.002)
    return m


def bolsa(sc, pos, rot=(0, 0, 0), vacia=False):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    o = bpy.context.object; o.name = "Bolsa"
    o.scale = (0.17, 0.05 if vacia else 0.09, 0.23)
    o.rotation_euler = rot
    bpy.ops.object.transform_apply(scale=True, rotation=False, location=False)
    s = o.modifiers.new("sub", "SUBSURF"); s.levels = 3; s.render_levels = 3
    tx = bpy.data.textures.new("arrugas", "VORONOI"); tx.noise_scale = 0.03
    d = o.modifiers.new("arrugas", "DISPLACE"); d.texture = tx; d.strength = 0.006
    liso(o, 180); asignar(o, mat_bolsa())
    return o


def migas(sc, centro, n=40, r=0.08, semilla=2):
    random.seed(semilla)
    mat = K.mat_pintura("miga", (0.72, 0.42, 0.12), capa=0.0)
    for i in range(n):
        a = random.random() * 6.283; d = r * math.sqrt(random.random())
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=random.uniform(0.002, 0.006),
                                              location=(centro[0] + math.cos(a) * d, centro[1] + math.sin(a) * d, centro[2]))
        p = bpy.context.object; p.scale = (1, random.uniform(0.5, 1), 0.4); asignar(p, mat)


# ---------------------------------------------------------------- personajes de Mixamo (With Skin)
def personaje(sc, quien):
    """Importa un personaje de Mixamo, le baja el brillo (el especular de Mixamo lo deja de plástico mojado), le borra la
    acción en T y devuelve el armature."""
    antes = set(bpy.data.objects)
    ruta = os.path.join(K.ASSETS, FBX[quien])
    proxy = not os.path.isfile(ruta) and os.path.isfile(os.environ.get("PROXY_FBX", ""))
    if not proxy:
        ruta = asset(FBX[quien])
    bpy.ops.import_scene.fbx(filepath=os.environ["PROXY_FBX"] if proxy else ruta, automatic_bone_orientation=False)
    nuevos = [o for o in bpy.data.objects if o not in antes]
    arm = next(o for o in nuevos if o.type == "ARMATURE")
    arm.animation_data_clear()
    arm.name = quien
    arm.scale = arm.scale * ESCALA.get(quien, 1.0)
    bpy.context.view_layer.update()
    if proxy:
        maniqui(sc, arm, quien)
        return arm
    for m in {s.material for o in nuevos if o.type == "MESH" for s in o.material_slots if s.material}:
        b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None) if m.node_tree else None
        if not b:
            continue
        for nombre, (a, z) in (("Specular IOR Level", (0.0, 0.35)), ("Roughness", (0.45, 0.95))):
            ent = b.inputs[nombre]
            if ent.links:
                srcs = ent.links[0].from_socket
                m.node_tree.links.remove(ent.links[0])
                mr = m.node_tree.nodes.new("ShaderNodeMapRange")
                mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = a, z
                m.node_tree.links.new(srcs, mr.inputs["Value"]); m.node_tree.links.new(mr.outputs[0], ent)
            else:
                ent.default_value = (a + z) / 2
    for o in nuevos:
        if o.type == "MESH":
            liso(o, 180)
            o["personaje"] = quien
    return arm


def maniqui(sc, arm, quien):
    """Sólo pruebas locales (los personajes están en el repo privado): un maniquí de cápsulas colgadas de los huesos de un
    esqueleto Mixamo (PROXY_FBX), con las proporciones del personaje, para ajustar cámaras, poses y cinturones."""
    bpy.context.view_layer.update()
    color = {"caballero": (0.45, 0.42, 0.38), "piloto": (0.6, 0.08, 0.05), "mascara": (0.1, 0.1, 0.1), "doctor": (0.3, 0.6, 0.6)}[quien]
    mat = K.mat_pintura("maniqui_" + quien, color)
    radio = {"Hips": 0.13, "Spine": 0.14, "Spine1": 0.15, "Spine2": 0.16, "Neck": 0.05, "Head": 0.10, "Shoulder": 0.05,
             "Arm": 0.055, "ForeArm": 0.045, "Hand": 0.04, "UpLeg": 0.08, "Leg": 0.06, "Foot": 0.045}
    for pb in arm.pose.bones:
        n = pb.name.split(":")[-1]
        clave = next((k for k in sorted(radio, key=len, reverse=True) if n.endswith(k) and not n.endswith("Top_End")), None)
        if clave is None or "Index" in n or "Thumb" in n or "Toe" in n:
            continue
        h = (arm.matrix_world @ pb.bone.head_local); t = (arm.matrix_world @ pb.bone.tail_local)
        largo = max((t - h).length, 0.02)
        r = radio[clave]
        if clave == "Head":
            bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=h + (t - h) * 0.5)
        else:
            bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=largo, location=(h + t) / 2)
            o = bpy.context.object
            o.rotation_mode = "QUATERNION"; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference((t - h).normalized())
        o = bpy.context.object; o.name = f"mq_{quien}_{n}"; asignar(o, mat); o["personaje"] = quien
        mw = o.matrix_world.copy()
        o.parent = arm; o.parent_type = "BONE"; o.parent_bone = pb.name
        bpy.context.view_layer.update()
        o.matrix_world = mw


def sentar_a_mano(arm):
    """Sin la pose de sentado (pruebas locales): muslos adelante, piernas abajo, pies adelante."""
    for lado in ("Left", "Right"):
        apuntar_hueso(arm, f"{lado}UpLeg", Vector((0, -1, -0.12)))
        apuntar_hueso(arm, f"{lado}Leg", Vector((0, -0.15, -1)))
        apuntar_hueso(arm, f"{lado}Foot", Vector((0, -1, -0.4)))


def hueso(arm, sufijo):
    return next((b for b in arm.pose.bones if b.name.split(":")[-1] == sufijo), None)


def pos_hueso(arm, sufijo, cola=False):
    bpy.context.view_layer.update()
    b = hueso(arm, sufijo)
    return arm.matrix_world @ (b.tail if cola else b.head)


def copiar_pose(arm, fbx, frame, solo=None, excepto=()):
    """Copia la pose de un cuadro de una animación de Mixamo (Without Skin), hueso por hueso (todos, o sólo los de `solo`)."""
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=fbx, automatic_bone_orientation=False)
    nuevos = [o for o in bpy.data.objects if o not in antes]
    src = next(o for o in nuevos if o.type == "ARMATURE")
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()
    dst = {b.name.split(":")[-1]: b for b in arm.pose.bones}
    for b in src.pose.bones:
        n = b.name.split(":")[-1]
        d = dst.get(n)
        if d is None or (solo and not any(n.startswith(s) for s in solo)) or any(n.startswith(e) for e in excepto):
            continue
        d.rotation_mode = "QUATERNION"; b.rotation_mode = "QUATERNION"
        d.rotation_quaternion = b.rotation_quaternion.copy()
    for o in nuevos:
        bpy.data.objects.remove(o)
    for a in list(bpy.data.actions):
        if a.users == 0:
            bpy.data.actions.remove(a)
    bpy.context.view_layer.update()


# marco del auto: los ejes de las poses y las anclas de los cinturones están en coordenadas del auto (trompa a −y). Con el
# auto inclinado en la subida (E4) hay que pasarlos al mundo; Cabina.poner lo actualiza.
MARCO = Matrix.Identity(4)


def en_auto(p):
    return MARCO @ Vector(p)


def dir_auto(v):
    return (MARCO.to_3x3().normalized() @ Vector(v))


def girar(arm, sufijo, eje_mundo, grados):
    """Gira un hueso alrededor de un eje del auto (más fácil de pensar que en el espacio del hueso)."""
    bpy.context.view_layer.update()
    pb = hueso(arm, sufijo)
    if pb is None:
        return
    pb.rotation_mode = "QUATERNION"
    m = (arm.matrix_world @ pb.matrix).to_3x3()
    eje_local = (m.inverted() @ dir_auto(eje_mundo)).normalized()
    pb.rotation_quaternion = pb.rotation_quaternion @ Quaternion(eje_local, math.radians(grados))
    bpy.context.view_layer.update()


def sentar(arm, quien, raiz_auto=None, sentado_fbx=None, frame=1):
    """Pone al personaje sentado en su asiento mirando hacia la trompa (−y): pose de piernas y cadera de Sitting Laughing
    (si está) y mueve el armature para que la cadera quede en el asiento."""
    if sentado_fbx and os.path.isfile(sentado_fbx):
        copiar_pose(arm, sentado_fbx, frame, solo=("Hips", "LeftUpLeg", "LeftLeg", "LeftFoot", "RightUpLeg", "RightLeg", "RightFoot", "Spine"))
    else:   # pose sentada a mano
        for lado in ("Left", "Right"):
            girar(arm, f"{lado}UpLeg", (1, 0, 0), 85)
            girar(arm, f"{lado}Leg", (1, 0, 0), -85)
    # mirar hacia −y (Mixamo mira a −y en Blender con este import; si no, se gira)
    bpy.context.view_layer.update()
    cad = pos_hueso(arm, "Hips")
    objetivo = Vector(ASIENTO[quien])
    arm.location += objetivo - cad
    if raiz_auto is not None:
        arm.parent = raiz_auto
        arm.matrix_parent_inverse = raiz_auto.matrix_world.inverted()
    bpy.context.view_layer.update()


# ---------------------------------------------------------------- cinturón (cinta)
def mat_cinta(nombre="cinta", color=(0.02, 0.02, 0.023)):
    """Cinta del cinturón: trama tejida (rayas finas a lo largo), bordes cosidos y polvo."""
    m, nt, b = _nodos(nombre)
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["UV"], sep.inputs[0])
    wave = nt.nodes.new("ShaderNodeTexWave"); wave.wave_type = "BANDS"; wave.inputs["Scale"].default_value = 140
    nt.links.new(tc.outputs["UV"], wave.inputs["Vector"])
    nz = _ruido(nt, escala=8, detalle=6)
    col = _rampa(nt, nz.outputs["Fac"], color, tuple(min(1, c * 2.2) for c in color))
    nt.links.new(col.outputs[0], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.85
    # tela de poliéster negra: casi sin brillo (con 0,2 de especular la cinta reflejaba el desierto y se veía café claro)
    b.inputs["Specular IOR Level"].default_value = 0.04
    b.inputs["Sheen Weight"].default_value = 0.06
    b.inputs["Sheen Tint"].default_value = (0.35, 0.35, 0.37, 1)
    _bump(nt, b, wave.outputs["Fac"], 0.3, 0.0006)
    return m


def cinta(sc, puntos, normales, ancho=0.048, nombre="Cinta", mat=None, res=10):
    """Malla de cinta que pasa por `puntos` (Catmull-Rom); `normales` dice hacia dónde mira la cara de la cinta en cada punto
    (afuera del cuerpo). Devuelve el objeto."""
    P = [Vector(p) for p in puntos]; N = [Vector(n).normalized() for n in normales]
    pts, nrs = [], []
    for i in range(len(P) - 1):
        p0 = P[max(0, i - 1)]; p1 = P[i]; p2 = P[i + 1]; p3 = P[min(len(P) - 1, i + 2)]
        for k in range(res):
            t = k / res
            t2, t3 = t * t, t * t * t
            q = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
            pts.append(q); nrs.append((N[i] * (1 - t) + N[i + 1] * t).normalized())
    pts.append(P[-1]); nrs.append(N[-1])
    verts, caras, uvs = [], [], []
    largo = 0.0
    for i, (p, n) in enumerate(zip(pts, nrs)):
        d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        lado = d.cross(n).normalized() * (ancho / 2)
        verts += [p - lado, p + lado]
        if i:
            largo += (p - pts[i - 1]).length
        uvs.append(largo)
    for i in range(len(pts) - 1):
        caras.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
    me = bpy.data.meshes.new(nombre); me.from_pydata(verts, [], caras)
    uv = me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            uv.data[li].uv = (vi % 2, uvs[vi // 2] * 10)
    o = bpy.data.objects.new(nombre, me); sc.collection.objects.link(o)
    s = o.modifiers.new("grosor", "SOLIDIFY"); s.thickness = 0.0015
    liso(o, 180)
    asignar(o, mat or mat_cinta())
    return o


def mat_capa(nombre, color, alfa=0.55, fuerza=2.5):
    """Capa de explicación sobre la cinta: color que brilla un poco y deja ver la tela (rojo = tensa/trabada, verde = suelta)."""
    m = bpy.data.materials.new(nombre); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (*color, 1); em.inputs[1].default_value = fuerza
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader"); mx.inputs[0].default_value = alfa
    nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    try:
        m.surface_render_method = "BLENDED"
    except Exception:
        pass
    return m


def capa_cinta(sc, cinta_obj, color, alfa=0.55):
    """Copia la cinta un pelo más gruesa con la capa de color encima (no proyecta sombra ni se refleja)."""
    o = cinta_obj.copy(); o.data = cinta_obj.data.copy(); sc.collection.objects.link(o)
    o.name = cinta_obj.name + "_capa"
    for md in o.modifiers:
        if md.type == "SOLIDIFY":
            md.thickness = md.thickness + 0.004; md.offset = 0.0
    o.data.materials.clear(); o.data.materials.append(mat_capa(o.name, color, alfa))
    o.visible_shadow = False; o.visible_glossy = False; o.visible_diffuse = False
    return o


def cinturon_de(sc, arm, quien, raiz=None, separacion=0.03, lejos_pecho=0.05, comba=0.0):
    """Cinturón de tres puntas para un personaje sentado: guía del pilar → frente del hombro de afuera → pecho → hebilla
    en la cadera de adentro; y la parte de la falda de la hebilla al anclaje de afuera. Las anclas del cuerpo salen de los
    huesos con `separacion` sobre la ropa o la armadura (puerta 3: la cinta nunca la atraviesa)."""
    afuera = -1 if ASIENTO[quien][0] < 0 else 1          # el pilar está del lado de afuera del asiento
    lado_af = "Right" if afuera < 0 else "Left"          # mirando a −y, la derecha del personaje es −x
    lado_ad = "Left" if afuera < 0 else "Right"
    frente = dir_auto((0, -1, 0)); arriba = dir_auto((0, 0, 1)); lado = dir_auto((1, 0, 0))
    g = en_auto(PILAR_GUIA[quien])
    hom = pos_hueso(arm, f"{lado_af}Shoulder", cola=True) + frente * (0.06 + separacion) + arriba * 0.04
    pecho = pos_hueso(arm, "Spine2") + frente * (0.12 + lejos_pecho)
    cad_ad = pos_hueso(arm, f"{lado_ad}UpLeg") + frente * (0.10 + separacion) + lado * (-afuera * 0.06) + arriba * 0.02
    cad_af = pos_hueso(arm, f"{lado_af}UpLeg") + frente * (0.10 + separacion) + lado * (afuera * 0.08) + arriba * 0.02
    anc_af = en_auto((ASIENTO[quien][0] + afuera * 0.30, ASIENTO[quien][1] + 0.12, 0.90))
    n_f = dir_auto((0, -1, 0.2))
    if comba > 0:      # cinta que salió con soltura: cuelga un poco entre la guía y el hombro
        medio = g.lerp(hom, 0.5) - arriba * comba + frente * (comba * 0.5)
        a = cinta(sc, [g, medio, hom, pecho, cad_ad], [dir_auto((-afuera, -0.6, 0)), dir_auto((-afuera, -0.6, 0.3)), n_f, n_f, n_f], nombre=f"Cinta_{quien}")
    else:
        a = cinta(sc, [g, hom, pecho, cad_ad], [dir_auto((-afuera, -0.6, 0)), n_f, n_f, n_f], nombre=f"Cinta_{quien}")
    b = cinta(sc, [cad_ad, (cad_ad + cad_af) / 2 + arriba * 0.02, cad_af, anc_af], [dir_auto((0, -0.3, 1))] * 4, nombre=f"Falda_{quien}")
    for o in (a, b):
        if raiz is not None:
            o.parent = raiz; o.matrix_parent_inverse = raiz.matrix_world.inverted()
    return a, b


# ---------------------------------------------------------------- el retractor por dentro (E2)
def engranaje(sc, nombre, r, alto, dientes, prof, interno=False, mat=None, pos=(0, 0, 0)):
    """Rueda dentada (o anillo con dientes hacia adentro) como malla extruida a lo largo de x."""
    bm = bmesh.new()
    pts = []
    for i in range(dientes * 4):
        a = 2 * math.pi * i / (dientes * 4)
        fase = i % 4
        rr = r + (prof if fase in (1, 2) else 0) * (-1 if interno else 1)
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    vs = [bm.verts.new((-alto / 2, y, z)) for (y, z) in pts]
    vs2 = [bm.verts.new((alto / 2, y, z)) for (y, z) in pts]
    if interno:
        R = r + prof * 2.2
        ext = [bm.verts.new((-alto / 2, R * math.cos(2 * math.pi * i / len(pts)), R * math.sin(2 * math.pi * i / len(pts)))) for i in range(len(pts))]
        ext2 = [bm.verts.new((alto / 2, v.co.y, v.co.z)) for v in ext]
        n = len(pts)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((vs[i], vs[j], vs2[j], vs2[i]))
            bm.faces.new((ext[i], ext2[i], ext2[j], ext[j]))
            bm.faces.new((vs[i], ext[i], ext[j], vs[j]))
            bm.faces.new((vs2[i], vs2[j], ext2[j], ext2[i]))
    else:
        bm.faces.new(vs); bm.faces.new(list(reversed(vs2)))
        n = len(pts)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((vs[i], vs[j], vs2[j], vs2[i]))
    me = bpy.data.meshes.new(nombre); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(nombre, me); sc.collection.objects.link(o)
    o.location = pos
    bv = o.modifiers.new("bisel", "BEVEL"); bv.width = prof * 0.08; bv.segments = 2
    asignar(o, mat or mat_metal_cepillado(nombre + "_m"))
    return o


def mat_grasa(nombre="acero_grasa", color=(0.5, 0.5, 0.52)):
    """Acero de mecanismo: cepillado, con grasa vieja oscura en los rincones y rayas de uso."""
    m = mat_metal_cepillado(nombre, color=color, rugo=(0.25, 0.55), escala=14)
    nt = m.node_tree; b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    ent = b.inputs["Base Color"]; src = ent.links[0].from_socket; nt.links.remove(ent.links[0])
    nz = _ruido(nt, escala=22, detalle=8)
    k = _mapa(nt, nz.outputs["Fac"], 0.0, 0.85); k.inputs["From Min"].default_value = 0.55; k.inputs["From Max"].default_value = 0.72
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    nt.links.new(k.outputs[0], mix.inputs[0]); nt.links.new(src, mix.inputs[6]); mix.inputs[7].default_value = (0.06, 0.05, 0.035, 1)
    nt.links.new(mix.outputs[2], ent)
    return m


def mat_zinc(nombre="zinc"):
    """Acero zincado amarillo (el marco de un retractor de verdad): dorado verdoso tornasol, manchado, con grasa y polvo."""
    m, nt, b = _nodos(nombre)
    nz = _ruido(nt, escala=9, detalle=10)
    col = _rampa(nt, nz.outputs["Fac"], (0.46, 0.41, 0.28), (0.38, 0.39, 0.34), pos=(0.3, 0.7))
    nz2 = _ruido(nt, escala=35, detalle=6)
    k = _mapa(nt, nz2.outputs["Fac"], 0.0, 0.85); k.inputs["From Min"].default_value = 0.52; k.inputs["From Max"].default_value = 0.72
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    nt.links.new(k.outputs[0], mix.inputs[0]); nt.links.new(col.outputs[0], mix.inputs[6]); mix.inputs[7].default_value = (0.07, 0.06, 0.04, 1)
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    b.inputs["Metallic"].default_value = 0.9
    r = _mapa(nt, nz2.outputs["Fac"], 0.35, 0.7); nt.links.new(r.outputs[0], b.inputs["Roughness"])
    for clave, v in (("Thin Film Thickness", 220.0), ("Thin Film IOR", 1.45)):
        if clave in b.inputs:
            b.inputs[clave].default_value = v
    _bump(nt, b, nz2.outputs["Fac"], 0.12, 0.0004)
    return m


def mat_pom(nombre="pom", color=(0.025, 0.025, 0.027)):
    """Plástico negro de ingeniería (el disco del sensor y la tacita): satinado, con rayas finas y polvo en lo que mira arriba."""
    m, nt, b = _nodos(nombre)
    nz = _ruido(nt, escala=60, detalle=4, estirar=(1, 1, 12))
    nt.links.new(_rampa(nt, nz.outputs["Fac"], color, tuple(c * 3.0 for c in color)).outputs[0], b.inputs["Base Color"])
    r = _mapa(nt, nz.outputs["Fac"], 0.3, 0.55); nt.links.new(r.outputs[0], b.inputs["Roughness"])
    return m


def set_retractor(sc, giro=25.0, pestillo=0.0, bolita=0.35, palanca=0.0, key=2.5, rebote=6.0, fondo=True):
    """El set completo del retractor (estilo C y planos de E2): el mecanismo en el pilar, la chapa del pilar angosta detrás
    (10 cm, como un pilar B de verdad) con el desierto desenfocado a los lados, la cinta que sube y la luz del sol de la
    ventana. Devuelve (raiz, RET)."""
    RET = Vector(RETRACTOR)
    if fondo:
        desierto(sc); cerros(sc)
    ret = retractor(sc, tuple(RET), giro_carrete=giro, pestillo=pestillo, bolita=bolita, palanca=palanca)
    chapa = K.mat_acero_industrial("chapa_pilar", (0.13, 0.135, 0.14), sucio=0.9)
    # soporte del pilar: sólo la placa donde va apernado (capa de explicación); atrás, el mundo desenfocado
    caja(sc, "ChapaPilar", (0.004, 0.075, 0.13), tuple(RET + Vector((-0.045, 0.0, 0.0))), mat=chapa, bisel=0.002)
    # pernos que sujetan el marco al pilar (lo que no está apernado parece maqueta)
    for dy, dz in ((0.028, 0.036), (0.028, -0.036)):
        cilindro(sc, "Perno", 0.0045, 0.004, tuple(RET + Vector((-0.033, dy, dz))), verts=6,
                 mat=mat_grasa("perno", (0.4, 0.4, 0.42))).rotation_euler = (0, math.radians(90), 0)
    # la cinta sale tangente por delante del rollo (−y) y sube; la cara mira hacia −y, el ancho va a lo largo del eje (x)
    cinta(sc, [RET + Vector((0.0, -0.0175, 0.012)), RET + Vector((0.0, -0.0185, 0.06)), RET + Vector((0.0, -0.02, 0.6))],
          [Vector((0, -1, 0))] * 3, nombre="CintaSube")
    luz_area(sc, "SolVentana", tuple(RET + Vector((-0.45, -0.5, 0.3))), tuple(RET), key, (1.0, 0.72, 0.5), 0.5, spread=50)
    luz_area(sc, "Contra", tuple(RET + Vector((-0.35, 0.25, 0.2))), tuple(RET), key * 0.35, (1.0, 0.8, 0.6), 0.15, spread=50)
    # el rebote del tapiz crema del otro lado: es lo que reflejan las caras de metal que miran a la cámara (brillo del metal)
    luz_area(sc, "Rebote", tuple(RET + Vector((0.45, 0.35, 0.12))), tuple(RET), rebote, (1.0, 0.9, 0.78), 0.7)
    return ret, RET


def mat_plastico_pilar(nombre="plastico_pilar", alfa=1.0):
    """Plástico gris texturado del pilar (con su grano y rayas); con alfa < 1 se ve el retractor a través (capa de explicación)."""
    m, nt, b = _nodos(nombre)
    nz = _ruido(nt, escala=300, detalle=2)
    nt.links.new(_rampa(nt, nz.outputs["Fac"], (0.16, 0.155, 0.15), (0.22, 0.215, 0.21)).outputs[0], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.7
    _bump(nt, b, nz.outputs["Fac"], 0.2, 0.0004)
    b.inputs["Alpha"].default_value = alfa
    return m


def retractor(sc, pos=(0, 0, 0), escala=1.0, giro_carrete=0.0, pestillo=0.0, bolita=0.0, palanca=0.0, cinta_fuera=0.0):
    """El retractor real a escala (~8 cm), armado alrededor de `pos`, con el eje del carrete a lo largo de x. Los parámetros
    animan el mecanismo: giro_carrete (grados), pestillo (0 adentro → 1 enganchado), bolita (0 en el centro de la tacita → 1
    en el borde), palanca (0 abajo → 1 en los dientes). Devuelve un vacío padre."""
    px, py, pz = pos
    s = escala
    raiz = bpy.data.objects.new("Retractor", None); sc.collection.objects.link(raiz)
    raiz.location = pos
    acero = mat_grasa("acero_ret", (0.62, 0.62, 0.64))
    oscuro = mat_zinc("zinc_marco")          # marco y anillo: acero zincado amarillo, como los de verdad
    pom = mat_pom("pom_sensor")              # disco del sensor y tacita: plástico negro
    objs = []
    # marco en U (chapa de acero)
    # marco en U: sólo la chapa del lado de la rueda; la del lado del pestillo está cortada (capa de explicación)
    objs.append(caja(sc, "Marco", (0.003 * s, 0.07 * s, 0.09 * s), (-0.036 * s, 0.0, 0.0), mat=oscuro, bisel=0.0008))
    objs.append(caja(sc, "MarcoAtras", (0.067 * s, 0.003 * s, 0.09 * s), (0.0, 0.035 * s, 0.0), mat=oscuro, bisel=0.0008))
    # carrete con la cinta enrollada (capas)
    eje = bpy.data.objects.new("EjeCarrete", None); sc.collection.objects.link(eje)
    eje.location = (0, 0, 0.012 * s); eje.rotation_euler = (math.radians(giro_carrete), 0, 0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.017 * s, depth=0.05 * s, location=(0, 0, 0), rotation=(0, math.radians(90), 0))
    rollo = bpy.context.object; rollo.name = "RolloCinta"; asignar(rollo, mat_cinta("cinta_rollo")); rollo.parent = eje
    for dx in (-0.027, 0.027):
        bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.021 * s, depth=0.003 * s, location=(dx * s, 0, 0), rotation=(0, math.radians(90), 0))
        o = bpy.context.object; o.name = "Tapa"; asignar(o, acero); o.parent = eje
    rueda = engranaje(sc, "RuedaDentada", 0.022 * s, 0.004 * s, 18, 0.0035 * s, mat=acero, pos=(-0.0305 * s, 0, 0)); rueda.parent = eje
    # disco del sensor de la cinta con su pestillo (del lado +x) dentro del anillo dentado fijo
    disco = cilindro(sc, "DiscoPestillo", 0.02 * s, 0.003 * s, (0.031 * s, 0, 0), mat=pom)
    disco.rotation_euler = (0, math.radians(90), 0); disco.parent = eje
    piv = bpy.data.objects.new("PivotePestillo", None); sc.collection.objects.link(piv)
    piv.parent = eje; piv.location = (0.033 * s, 0.0, 0.011 * s)
    pes = caja(sc, "Pestillo", (0.003 * s, 0.014 * s, 0.004 * s), (0, -0.007 * s, 0), mat=mat_grasa("pestillo", (0.62, 0.6, 0.55)), bisel=0.0005)
    pes.parent = piv; piv.rotation_euler = (math.radians(-38 * pestillo), 0, 0)
    anillo = engranaje(sc, "AnilloDentado", 0.025 * s, 0.004 * s, 22, 0.0025 * s, interno=True, mat=oscuro, pos=(0.0335 * s, 0, 0.012 * s))
    # sensor del auto: tacita con la bolita y la palanquita, abajo
    taza = bpy.data.objects.new("Taza", None); sc.collection.objects.link(taza); taza.location = (-0.03 * s, -0.012 * s, -0.035 * s)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=0.011 * s, location=(0, 0, 0.008 * s))
    cup = bpy.context.object; cup.name = "Tacita"; cup.scale = (1, 1, 0.45)
    bm_cut = cup.modifiers.new("corte", "BOOLEAN")
    bpy.ops.mesh.primitive_cube_add(size=0.03 * s, location=(0, 0, 0.023 * s)); cortador = bpy.context.object; cortador.hide_render = True
    cortador.display_type = "WIRE"; bm_cut.object = cortador
    sol = cup.modifiers.new("grosor", "SOLIDIFY"); sol.thickness = 0.0012 * s
    asignar(cup, pom); cup.parent = taza; cortador.parent = taza
    ang = bolita * 0.85
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=0.0055 * s,
                                          location=(0, -math.sin(ang) * 0.007 * s, 0.0055 * s + (1 - math.cos(ang)) * 0.006 * s))
    bola = bpy.context.object; bola.name = "Bolita"; asignar(bola, mat_metal_cepillado("bolita_m", (0.85, 0.86, 0.88), rugo=(0.05, 0.15)))
    liso(bola, 180); bola.parent = taza
    piv2 = bpy.data.objects.new("PivotePalanca", None); sc.collection.objects.link(piv2); piv2.parent = taza
    piv2.location = (0, 0.012 * s, 0.014 * s)
    pal = caja(sc, "Palanquita", (0.004 * s, 0.028 * s, 0.0025 * s), (0, -0.012 * s, 0), mat=mat_grasa("palanca", (0.6, 0.58, 0.55)), bisel=0.0004)
    pal.parent = piv2; piv2.rotation_euler = (math.radians(-22 * palanca), 0, 0)
    for o in (eje, anillo, taza) + tuple(objs):
        o.parent = raiz
    return raiz


# ---------------------------------------------------------------- posar personajes
def apuntar_hueso(arm, sufijo, dir_mundo):
    """Gira un hueso para que apunte (de cabeza a cola) en la dirección del mundo dada."""
    bpy.context.view_layer.update()
    pb = hueso(arm, sufijo)
    if pb is None:
        return
    M = arm.matrix_world @ pb.matrix
    actual = (M.to_3x3() @ Vector((0, 1, 0))).normalized()
    q = actual.rotation_difference(Vector(dir_mundo).normalized())
    R = q.to_matrix().to_4x4()
    t = M.to_translation()
    nueva = Matrix.Translation(t) @ R @ Matrix.Translation(-t) @ M
    pb.matrix = arm.matrix_world.inverted() @ nueva
    bpy.context.view_layer.update()


def mirar_adelante(arm, adelante=Vector((0, -1, 0))):
    """Gira el armature en z para que los pies (y el personaje) miren hacia `adelante`."""
    bpy.context.view_layer.update()
    try:
        pie = pos_hueso(arm, "LeftToeBase") - pos_hueso(arm, "LeftFoot")
    except Exception:
        return
    pie.z = 0
    if pie.length < 1e-4:
        return
    ang = pie.to_2d().angle_signed(adelante.to_2d())
    arm.rotation_euler.z -= ang
    bpy.context.view_layer.update()


def tiene_esqueleto(arm):
    return hueso(arm, "Hips") is not None and hueso(arm, "Spine2") is not None


def sentado(sc, quien, sentado_fbx, raiz=None, frame=1):
    """Importa, sienta y ubica a un personaje en su asiento (mirando a la trompa, −y). Devuelve el armature o None."""
    try:
        arm = personaje(sc, quien)
    except Exception as e:
        print("sin personaje", quien, e)
        return None
    if not tiene_esqueleto(arm):
        print("sin esqueleto Mixamo:", quien)
        return arm
    if sentado_fbx and os.path.isfile(sentado_fbx):
        copiar_pose(arm, sentado_fbx, frame)
        mirar_adelante(arm)
    else:
        mirar_adelante(arm)
        sentar_a_mano(arm)
    cad = pos_hueso(arm, "Hips")
    arm.location += Vector(ASIENTO[quien]) - cad
    bpy.context.view_layer.update()
    return arm


def lanzarse(arm, cuanto=1.0, hacia=Vector((0.35, -1.0, -0.15))):
    """El caballero se lanza hacia la bolsa del centro del tablero: columna adelante y el brazo de adentro estirado."""
    for s, g in (("Spine", 8), ("Spine1", 6), ("Spine2", 5)):     # el CLAC lo para a los pocos cm
        girar(arm, s, (1, 0, 0), g * cuanto)
    lado = "Left"     # copiloto: su izquierda (+x) da a la consola
    hacia = Vector(hacia).normalized()
    c = max(0.0, min(1.0, cuanto))
    for parte in ("Arm", "ForeArm", "Hand"):
        d0 = (pos_hueso(arm, f"{lado}{parte}", cola=True) - pos_hueso(arm, f"{lado}{parte}")).normalized()
        d = d0.lerp(hacia + (dir_auto((0, 0, -0.1)) if parte == "Hand" else Vector()), c)
        apuntar_hueso(arm, f"{lado}{parte}", d)


def placeholder(sc, quien, alto=0.85):
    """Muñeco de prueba (cilindro + esfera) donde va un personaje, para ajustar cámaras sin Mixamo (sólo pruebas locales)."""
    x, y, z = ASIENTO[quien]
    c = cilindro(sc, f"pp_{quien}", 0.16, alto * 0.7, (x, y, z), mat=K.mat_pintura("pp", (0.5, 0.3, 0.2)))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=(x, y, z + alto * 0.7 + 0.12))
    asignar(bpy.context.object, K.mat_pintura("pp2", (0.6, 0.45, 0.35)))
