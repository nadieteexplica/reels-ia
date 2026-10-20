"""Set del plano 23 (muelas): MODO=cara (el ratón de perfil) o MODO=lupa (primer plano de las muelas). Sale de
estilo_muelas.py (cuadro de estilo aprobado en la puerta 4, c3 r3). armar(sc, modo) devuelve sus piezas."""
import math, os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.abspath(os.path.join(HERE, "../../.."))
for p in (HERE, os.path.join(STUDIO, "plantilla")):
    if p not in sys.path:
        sys.path.insert(0, p)
import bpy
from mathutils import Vector
import props as P
import personajes as PJ

# los valores con que estilo_muelas2.py arma el cuadro aprobado
DEF_CARA = {"TGT_Y": "0.0581", "TGT_Z": "-0.0371", "CAMOFF": "1.075,0.0,0.0", "LENS": "50"}
DEF_LUPA = {"TGT_Y": "0.0581", "TGT_Z": "-0.0371", "CAMOFF": "1.075,0.0,0.0", "LENS": "65"}


def armar(sc, modo="cara"):
    for k, v in (DEF_CARA if modo == "cara" else DEF_LUPA).items():
        os.environ.setdefault(k, v)
    os.environ["MODO"] = modo
    C = P.collection("Muelas")
    rt = PJ.raton(C)
    # de perfil: el ratón mira hacia -Y y la cámara lo ve desde +X
    bpy.context.view_layer.update()
    cab = rt["cabeza_malla"]
    # de perfil el ojo se veía de costado (esclerótica blanca); en la ficha los ojos se ven negros y brillantes:
    # el ojo del lado de la cámara mira hacia la cámara (como en un dibujo animado de perfil) y su párpado lo sigue
    from mathutils import Vector as _V
    for o, pv in zip(rt["ojos"], rt["parpados"]):
        if o.matrix_world.translation.x > 0:
            rot = _V(tuple(float(x) for x in os.environ.get("MIRADA", "1.0,-0.45,0.05").split(","))).normalized().to_track_quat("-Y", "Z").to_euler()
            o.rotation_euler = rot
            pv.rotation_euler = rot
    # bigotes del otro lado: de perfil cruzaban por detrás de la nariz
    for ob in bpy.data.objects:
        if ob.name.startswith("Raton_bigoteL"):
            ob.hide_render = True
        if ob.name.startswith("Raton_bigote"):
            ob.visible_glossy = False          # su reflejo dibujaba rayitas sobre el ojo
    # la patita del otro lado queda casi tapada por el cuerpo y de perfil se cruzaba con la de adelante: no se renderiza
    for ob in bpy.data.objects:
        if ob.name in ("Raton_brazoL", "Raton_manoL"):
            ob.hide_render = True
    # orejas como en la ficha (apenas echadas atrás); la de la cámara gira hacia ella para que se vea redonda y rosada
    # (de perfil puro se veía de canto, como una punta beige)
    for k, ob in enumerate(rt["orejas"]):
        ob.rotation_euler = (math.radians(float(os.environ.get("OREJA_X", -12))), 0, math.radians(float(os.environ.get("OREJA_GIRO", 55)) * (1 if k else -1)))
    # patitas como en la ficha: dobladas, con la palma rosada frente al pecho
    for k, br in enumerate(rt["brazos"]):
        br.rotation_euler = (math.radians(float(os.environ.get("BRAZO_X", 0))), 0, math.radians(float(os.environ.get("BRAZO_Z", 0)) * (1 if k else -1)))
    # puerta 4 c2 r2: de perfil, el brazo de tres globos se leía como bolas sueltas. La pata de la cámara se arma como un tubo
    # continuo que sale del pecho (codo metido en el cuerpo), va hacia adelante y termina en la palma rosada frente al pecho
    if os.environ.get("BRAZO_TUBO", "1") == "1":
        canela_m = bpy.data.objects["Raton_brazoR"].data.materials[0]
        rosado_m = bpy.data.objects["Raton_manoR"].data.materials[0]
        for nm in ("Raton_brazoR", "Raton_manoR"):
            bpy.data.objects[nm].hide_render = True
        _pts = [(0.020, -0.018, 0.103), (0.027, -0.019, 0.083), (0.026, -0.035, 0.083), (0.023, -0.047, 0.090)]
        P.tube("Raton_brazoR_tubo", _pts, float(os.environ.get("BRAZO_R", 0.0071)), C, canela_m)
        PJ.esfera("Raton_palmaR", (0.0225, -0.0505, 0.0925), 0.0056, C, rosado_m, escala=(0.8, 0.75, 1.15))
    # la cola entra al cuadro: termina en punta (con el radio parejo se veía como un tubo cortado)
    rt["cola"].rotation_euler.z = math.radians(float(os.environ.get("COLA_Z", 62)))   # la cola va hacia atrás, no hacia la cámara (se veía la punta abierta)
    _cola = bpy.data.objects.get("Raton_cola")
    if _cola and _cola.type == "CURVE":
        _pts = _cola.data.splines[0].points
        for _k, _pt in enumerate(_pts):
            _pt.radius = max(0.18, 1.0 - 0.85 * (_k / (len(_pts) - 1)) ** 1.5)
    # c3 (puerta 4): la cola se veía gris con la luz turquesa (el SSS del rosado deja pasar el fondo en un tubo tan fino):
    # copia del rosado sin SSS, sólo para la cola
    if _cola and _cola.type == "CURVE":
        _rc = PJ.mat_simple("RosadoColaRaton", (0.86, 0.46, 0.48), rough=0.5)
        _cola.data.materials.clear()
        _cola.data.materials.append(_rc)
    # bigotes largos como en la ficha: de perfil los de la cámara apuntaban hacia ella y se veían como 3 trazos cortos.
    # Se rehacen en el plano de la imagen, abriéndose hacia adelante desde el hocico
    _bm_big = None
    for ob in list(bpy.data.objects):
        if ob.name.startswith("Raton_bigoteR"):
            _bm_big = ob.data.materials[0] if ob.data.materials else None
            ob.hide_render = True
    _cab_c = Vector((0, -0.016, 0.150))
    for _k, (_dz, _ang) in enumerate([(0.003, 32), (0.0, 7), (-0.003, -20)]):
        _o = _cab_c + Vector((0.012, -0.051, -0.009 + _dz))
        _dv = Vector((0.30, -math.cos(math.radians(_ang)), math.sin(math.radians(_ang)))).normalized()
        _w = P.tube(f"Raton_bigoteP{_k}", [tuple(_o), tuple(_o + _dv * 0.019 + Vector((0, 0, 0.0012))), tuple(_o + _dv * 0.037)], 0.00045, C, _bm_big)
        _w.visible_glossy = False
    # torso: de perfil se leían bultos apilados (cuello y pecho). Relleno en la garganta y suavizado del cuerpo -> pera continua
    _cu = bpy.data.objects.get("Raton_cuerpo")
    if _cu:
        _sm = _cu.modifiers.new("SuavePerfil", "SMOOTH")
        _sm.factor, _sm.iterations = 1.0, int(os.environ.get("SUAVE_CUERPO", 30))
        _gar = PJ.blob("Raton_garganta", [((0, -0.017, 0.127), (0.027, 0.029, 0.024), (0, 0, 0))], C)
        _gar.data.materials.append(_cu.data.materials[0])
    # c3 r2: la base de la cola se veía como la boca de un tubo hueco, y la cola salía del recuadro: se tapa la base con una
    # esfera del mismo rosado metida en el anca, y la cola se acorta y sube (la punta entra entera en el recuadro)
    if _cola and _cola.type == "CURVE":
        _tapa = PJ.esfera("Raton_colaBase", (0, 0.044, 0.021), 0.0052, C, _cola.data.materials[0])
        rt["cola"].scale = (0.62, 0.62, 0.62)
        rt["cola"].rotation_euler.x = math.radians(float(os.environ.get("COLA_SUBE", -14)))
    # párpados del color del lomo (de perfil, la máscara de guata los pintaba blancos)
    lomo_m = PJ.mat_simple("LomoParpado", (0.42, 0.20, 0.08), rough=0.7, sheen=0.9)
    for pv in rt["parpados"]:
        for ch in pv.children:
            ch.data.materials.clear()
            ch.data.materials.append(lomo_m)
    # ventanita: en la mejilla, bajo el ojo y detrás del hocico, la piel pasa a ser transparente dentro de un círculo
    # chico (coordenadas del objeto = mundo, el ratón se arma en el origen). Borde con un anillo crema para que se lea "ventana".
    centro_loc = Vector((0.0165, -0.036, 0.1355))   # delante del cuello (el cuello tapaba la muela de atrás)
    MODO = os.environ.get("MODO", "cara")
    R_VEN = float(os.environ.get("R_VEN", 0.045 if MODO == "lupa" else 0.0138))
    m = cab.data.materials[0].copy()
    m.name = "PelajeVentana"
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    out = nt.nodes["Material Output"]
    for nd in nt.nodes:                                    # de perfil la guata dejaba una franja blanca ojo→cuello: se acota
        if nd.type == "MAP_RANGE" and abs(nd.inputs["From Min"].default_value - 0.72) < 1e-6:
            nd.inputs["From Min"].default_value = 0.86
    tc = nt.nodes.new("ShaderNodeTexCoord")
    # distancia en el plano Y-Z (la cámara mira desde +X): cilindro, así el círculo se ve redondo
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(sep.outputs["Y"], comb.inputs["Y"])
    nt.links.new(sep.outputs["Z"], comb.inputs["Z"])
    dist = nt.nodes.new("ShaderNodeVectorMath")
    dist.operation = "DISTANCE"
    dist.inputs[1].default_value = (0, centro_loc.y, centro_loc.z)
    nt.links.new(comb.outputs["Vector"], dist.inputs[0])
    # sólo el lado que mira a la cámara (x > 0): el otro lado de la cabeza queda con piel
    lado = nt.nodes.new("ShaderNodeMath")
    lado.operation = "GREATER_THAN"
    lado.inputs[1].default_value = 0.004
    nt.links.new(sep.outputs["X"], lado.inputs[0])
    dentro_c = nt.nodes.new("ShaderNodeMapRange")          # 1 dentro de la ventana, 0 fuera
    dentro_c.inputs["From Min"].default_value = R_VEN
    dentro_c.inputs["From Max"].default_value = R_VEN * 0.62
    dentro_c.inputs["To Max"].default_value = 0.92          # la piel no desaparece del todo: se ve "de vidrio"
    nt.links.new(dist.outputs["Value"], dentro_c.inputs["Value"])
    anillo_a = nt.nodes.new("ShaderNodeMapRange")          # 1 dentro del borde exterior del anillo
    anillo_a.inputs["From Min"].default_value = R_VEN * 1.10
    anillo_a.inputs["From Max"].default_value = R_VEN * 1.02
    anillo_a.inputs["To Max"].default_value = float(os.environ.get("ANILLO", 0.0))   # la marca de la mejilla se dibuja en 2D
    nt.links.new(dist.outputs["Value"], anillo_a.inputs["Value"])
    ven = nt.nodes.new("ShaderNodeMath"); ven.operation = "MULTIPLY"
    nt.links.new(dentro_c.outputs["Result"], ven.inputs[0]); nt.links.new(lado.outputs[0], ven.inputs[1])
    if MODO == "cara":
        ven.inputs[1].default_value = 0.0                   # sin ventana: la piel queda entera
        nt.links.remove(ven.inputs[1].links[0])
    ani = nt.nodes.new("ShaderNodeMath"); ani.operation = "MULTIPLY"
    nt.links.new(anillo_a.outputs["Result"], ani.inputs[0]); nt.links.new(lado.outputs[0], ani.inputs[1])
    transp = nt.nodes.new("ShaderNodeBsdfTransparent")
    transp.inputs["Color"].default_value = (1.0, 0.97, 0.95, 1)
    borde = nt.nodes.new("ShaderNodeBsdfPrincipled")
    borde.inputs["Base Color"].default_value = (0.98, 0.93, 0.82, 1)
    borde.inputs["Roughness"].default_value = 0.35
    borde.inputs["Coat Weight"].default_value = 0.6
    mix1 = nt.nodes.new("ShaderNodeMixShader")             # piel → anillo
    nt.links.new(ani.outputs[0], mix1.inputs["Fac"])
    nt.links.new(b.outputs[0], mix1.inputs[1])
    nt.links.new(borde.outputs[0], mix1.inputs[2])
    mix2 = nt.nodes.new("ShaderNodeMixShader")             # → transparente dentro
    nt.links.new(ven.outputs[0], mix2.inputs["Fac"])
    nt.links.new(mix1.outputs[0], mix2.inputs[1])
    nt.links.new(transp.outputs[0], mix2.inputs[2])
    nt.links.new(mix2.outputs[0], out.inputs["Surface"])
    cab.data.materials.clear()
    cab.data.materials.append(m)
    # interior: todo cabe dentro de la cabeza (x 0.000–0.012) y dentro del círculo de la ventana
    diente = P.mat("Muela", (0.78, 0.62, 0.36), rough=0.5, coat=0.05, emit=float(os.environ.get("BRILLO", 0.0)))   # marfil amarillento de roedor   # bajo el umbral del brillo del post (si no, se queman)
    encia = P.mat("Encia", (0.78, 0.36, 0.40), rough=0.55, sss=0.0)   # c3: encía rosada y gruesa que abraza la base de las muelas (oscura y fina se leía como palitos)
    semilla = P.mat("SemillaAji", (0.96, 0.86, 0.46), rough=0.5, coat=0.2)   # semilla de ají real: disco plano amarillo pálido
    borde_s = P.mat("SemillaBorde", (0.74, 0.56, 0.20), rough=0.55)          # con el borde un poco más oscuro
    miga_m = semilla                                   # las migas son la misma semilla, molida
    M = cab.matrix_world
    X_M = 0.0070                                           # plano de las muelas, bien adentro de la piel
    # fondo del interior: una cápsula oscura (azul noche, como la "cabeza de vidrio") que tapa el revés de la piel
    fondo_m = P.mat("InteriorFondo", (0.03, 0.05, 0.10), rough=0.8)
    cavidad = P.prim("sphere", "MejillaDentro", C, fondo_m, r=1.0)
    cavidad.scale = (0.0040, 0.0165, 0.0128)   # cabe entera dentro de la mejilla (no asoma bajo el mentón)
    cavidad.location = Vector((0.0005, centro_loc.y, centro_loc.z))
    def muela(name, centro, ancho, alto, arriba):
        """Muela de roedor: corona baja y alargada (de adelante hacia atrás) con tres crestas transversales en la cara que muerde."""
        cx, cy, cz = centro
        sg = -1 if arriba else 1                          # las crestas miran hacia la otra fila
        el = [((cx, cy, cz), (ancho * 0.40, ancho * 0.52, alto * 0.48), (0, 0, 0))]
        for k in (-1, 0, 1):
            el.append(((cx, cy + k * ancho * 0.30, cz + sg * alto * 0.40), (ancho * 0.38, ancho * 0.12, alto * 0.22), (0, 0, 0)))
        ob = PJ.blob(name, el, C, voxel=0.00016, suave=5)
        ob.data.materials.append(diente)
        return ob
    ANCHO, ALTO, GAP = 0.0092, 0.0042, 0.0042        # 2 muelas grandes por fila (con 3 chicas se leía como dientes de persona)
    for fila, arriba in (("sup", True), ("inf", False)):
        zc = centro_loc.z + (1 if arriba else -1) * (GAP / 2 + ALTO / 2)
        zg = zc + (1 if arriba else -1) * (ALTO / 2 + 0.0002)
        base = PJ.blob(f"Encia_{fila}", [((X_M - 0.0008, centro_loc.y - ANCHO * 0.52 + ANCHO * 1.04 * kk, zg), (0.0030, ANCHO * 0.50, 0.0017), (0, 0, 0)) for kk in range(2)], C, voxel=0.0002, suave=4)
        base.data.materials.append(encia)
        for k in range(2):
            muela(f"Muela_{fila}{k}", (X_M, centro_loc.y - ANCHO * 0.52 + ANCHO * 1.04 * k, zc), ANCHO, ALTO, arriba)
    rnd = random.Random(1)
    # semillas enteras entrando por delante (hacia el hocico) y migas saliendo por detrás, entre las dos filas
    R_SEM = ANCHO * 0.17                                       # ~1/3 de la corona de diámetro
    for k in range(3):                                        # 3 semillas enteras, planas: disco con borde oscuro, inclinado (se ve el canto)
        g = P.prim("cyl", f"Semilla{k}", C, borde_s, r=R_SEM, r2=R_SEM, h=R_SEM * 0.30, seg=32)
        P.bevel(g, R_SEM * 0.08, 2)
        tapa = P.prim("cyl", f"Semilla{k}_cara", C, semilla, r=R_SEM * 0.80, r2=R_SEM * 0.80, h=R_SEM * 0.12, seg=32)
        tapa.location = (0, 0, R_SEM * 0.15)
        tapa.parent = g
        g.rotation_euler = (math.radians(rnd.uniform(-25, 25)), math.radians(40 + rnd.uniform(-8, 8)), 0)
        g.location = Vector((X_M + 0.0020, centro_loc.y - 0.0105 + 0.0034 * k, centro_loc.z + rnd.uniform(-0.0006, 0.0006)))
    for k in range(14):                                       # migas: astillas planas del mismo amarillo
        g = P.prim("ico", f"Miga{k}", C, miga_m if k % 3 else borde_s, r=rnd.uniform(0.0005, 0.0009), sub=1)
        g.scale = (1.0, rnd.uniform(0.7, 1.2), rnd.uniform(0.35, 0.55))
        g.rotation_euler = (rnd.uniform(0, 3.1), rnd.uniform(0, 3.1), rnd.uniform(0, 3.1))
        g.location = Vector((X_M + 0.0012, centro_loc.y + 0.0028 + rnd.uniform(0, 0.0058), centro_loc.z + rnd.uniform(-0.0008, 0.0008)))
    luz_in = bpy.data.lights.new("LuzMejilla", "POINT")
    luz_in.energy, luz_in.color, luz_in.shadow_soft_size = float(os.environ.get("LUZ_IN", 0.012)), (1.0, 0.88, 0.78), 0.004
    lo_in = bpy.data.objects.new("LuzMejilla", luz_in)
    sc.collection.objects.link(lo_in)
    lo_in.location = M @ Vector((0.013, centro_loc.y - 0.002, centro_loc.z + 0.004))
    L = bpy.data.lights.new("Key", "AREA")
    L.energy, L.size, L.shape = float(os.environ.get("KEY", 30)), 0.5, "DISK"   # reflejo redondo en el ojo (no un parche cuadrado)
    lo = bpy.data.objects.new("Key", L)
    sc.collection.objects.link(lo)
    lo.location = (0.6, -0.5, 0.6)
    lo.rotation_euler = (Vector((0, 0, 0.13)) - lo.location).to_track_quat("-Z", "Y").to_euler()
    # c3 r2: el pelaje salía caramelo oscuro (en la ficha es durazno-tostado claro): relleno suave y cálido desde la cámara,
    # sin reflejo en el ojo
    _Lf = bpy.data.lights.new("RellenoRaton", "AREA")
    _Lf.energy, _Lf.size, _Lf.shape, _Lf.color = float(os.environ.get("FILL", 9)), 0.8, "DISK", (1.0, 0.93, 0.85)
    _lf = bpy.data.objects.new("RellenoRaton", _Lf)
    sc.collection.objects.link(_lf)
    _lf.location = (0.9, 0.25, 0.25)
    _lf.rotation_euler = (Vector((0, 0, 0.11)) - _lf.location).to_track_quat("-Z", "Y").to_euler()
    _lf.visible_glossy = False
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.lens = float(os.environ.get("LENS", 65))
    cam.data.sensor_fit = "VERTICAL"
    cam.data.sensor_height = 24
    tgt = M @ (centro_loc + Vector((0.0, float(os.environ.get("TGT_Y", 0.004)), float(os.environ.get("TGT_Z", -0.008)))))
    cam.location = tgt + Vector(tuple(float(x) for x in os.environ.get("CAMOFF", "0.71,-0.053,0.02").split(",")))
    cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
    if MODO == "lupa":
        # primer plano de las muelas: fondo oscuro del interior, nada de cara alrededor
        sc.render.resolution_x = sc.render.resolution_y = int(os.environ.get("LADO", 1080))
        sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.02, 0.03, 0.06, 1)
        for ob in bpy.data.objects:
            if ob.type == "MESH" and ob.name.startswith("Raton") and ob.name != "Raton_cabeza":
                ob.hide_render = True
        cavidad.scale = (0.0035, 0.030, 0.022)
        tgt = M @ Vector((X_M, centro_loc.y - 0.0015, centro_loc.z))
        cam.location = tgt + Vector((float(os.environ.get("LUPA_D", 0.12)), 0.0, 0.0))
        cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
        luz_in.energy = float(os.environ.get("LUZ_LUPA", 0.022))   # c3: con 0,03 la muela de arriba se quemaba
        lo_in.location = M @ Vector((0.02, centro_loc.y - 0.004, centro_loc.z + 0.008))

    return dict(locals())
