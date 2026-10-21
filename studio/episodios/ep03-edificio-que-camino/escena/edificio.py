"""La escuela de 1935 (cinco pisos, planta en T) con sus 198 patas en dos grupos, y la regla con que camina.

Nada se anima a mano: `Edificio.poner(dist, pose)` calcula, para la distancia recorrida, dónde está cada pata.
- La planta: ala delantera 44 × 12 m (22 × 6 patas) + ala de atrás 12 × 22 m (6 × 11 patas) = 198 patas, cada 2 m.
- Grupos: A (amarillo) y B (celeste) en damero. Mientras un grupo aguanta (pie fijo en el suelo), el otro se alza y da
  un paso; cada medio ciclo cambian (CNN 2020: "two groups which alternately rise up and down, imitating the human stride").
- El cuerpo se mueve según `pose(d) -> (x, y, yaw)` en función de la distancia d: así se puede caminar en curva y girar.
"""
import math
import bmesh
import bpy
from mathutils import Vector, Matrix, Euler

import props as P

AMARILLO = (1.0, 0.70, 0.05)
CELESTE = (0.18, 0.62, 1.0)
PASO = 1.2          # largo del paso de cada pata respecto del edificio (m)
ALZA = 0.55         # cuánto sube la pata en el aire (m)
ALTO_PATA = 3.0     # altura del marco de acero sobre el suelo cuando camina (m; algo exagerada para que las patas se lean)
PISO = 3.6
PISOS = 5


def _nodo(nt, tipo, x=0, y=0, **kw):
    n = nt.nodes.new(tipo)
    n.location = (x, y)
    for k, v in kw.items():
        n.inputs[k].default_value = v
    return n


def mat_ladrillo():
    m = bpy.data.materials.get("Ladrillo1935")
    if m:
        return m
    m = bpy.data.materials.new("Ladrillo1935")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = _nodo(nt, "ShaderNodeTexCoord", -900, 0)
    br = _nodo(nt, "ShaderNodeTexBrick", -600, 100)
    br.inputs["Color1"].default_value = (0.34, 0.10, 0.055, 1)
    br.inputs["Color2"].default_value = (0.46, 0.15, 0.075, 1)
    br.inputs["Mortar"].default_value = (0.40, 0.35, 0.30, 1)
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Mortar Size"].default_value = 0.008
    br.inputs["Brick Width"].default_value = 0.24
    br.inputs["Row Height"].default_value = 0.075
    br.offset = 0.5
    # coordenadas: ladrillos en las caras verticales (x+y, z)
    sep = _nodo(nt, "ShaderNodeSeparateXYZ", -800, -100)
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    add = _nodo(nt, "ShaderNodeMath", -700, -100)
    add.operation = "ADD"
    nt.links.new(sep.outputs["X"], add.inputs[0])
    nt.links.new(sep.outputs["Y"], add.inputs[1])
    comb = _nodo(nt, "ShaderNodeCombineXYZ", -650, -60)
    nt.links.new(add.outputs[0], comb.inputs["X"])
    nt.links.new(sep.outputs["Z"], comb.inputs["Y"])
    nt.links.new(comb.outputs[0], br.inputs["Vector"])
    noi = _nodo(nt, "ShaderNodeTexNoise", -600, -250, Scale=3.0, Detail=6.0)
    mix = _nodo(nt, "ShaderNodeMix", -300, 100)
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 0.25
    nt.links.new(br.outputs["Color"], mix.inputs[6])
    nt.links.new(noi.outputs["Color"], mix.inputs[7])
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.85
    bump = _nodo(nt, "ShaderNodeBump", -250, -200, Strength=0.25, Distance=0.02)
    nt.links.new(br.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs[0], b.inputs["Normal"])
    return m


def mat_estuco(name="Estuco1935", color=(0.86, 0.78, 0.62)):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    noi = _nodo(nt, "ShaderNodeTexNoise", -600, 0, Scale=1.5, Detail=8.0, Roughness=0.6)
    ramp = _nodo(nt, "ShaderNodeValToRGB", -350, 0)
    ramp.color_ramp.elements[0].color = (color[0] * 0.86, color[1] * 0.84, color[2] * 0.80, 1)
    ramp.color_ramp.elements[1].color = (*color, 1)
    nt.links.new(noi.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.8
    n2 = _nodo(nt, "ShaderNodeTexNoise", -600, -250, Scale=40.0, Detail=4.0)
    bump = _nodo(nt, "ShaderNodeBump", -250, -200, Strength=0.12, Distance=0.01)
    nt.links.new(n2.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs[0], b.inputs["Normal"])
    return m


def mat_vidrio():
    m = bpy.data.materials.get("Vidrio1935")
    if m:
        return m
    m = P.mat("Vidrio1935", (0.05, 0.09, 0.12), rough=0.06, metal=0.0)
    nds, lk, b = P.nodes(m)
    b.inputs["Specular IOR Level"].default_value = 0.9
    return m


def _caja(name, x0, x1, y0, y1, z0, z1, coll, m, parent=None, bisel=0.0):
    """Caja con las medidas dentro de la malla (no en la escala): así las texturas por coordenadas del objeto quedan en metros."""
    ob = P.prim("cube", name, coll, m, smooth=False)
    ob.data.transform(Matrix.Diagonal((x1 - x0, y1 - y0, z1 - z0, 1)))
    ob.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    if bisel:
        P.bevel(ob, bisel, 2)
    if parent:
        ob.parent = parent
    return ob


def _ventana_malla(coll):
    """Una ventana de acero de los años 30 (marco crema, vidrio oscuro, travesaños): se instancia en todas las fachadas.
    Local: centrada en x, apoyada en z=0 (antepecho), mirando a -Y (sale 0,05 m de la pared)."""
    w, h = 1.6, 2.1
    crema, vid = mat_estuco(), mat_vidrio()
    acero = P.mat("MarcoAcero", (0.08, 0.16, 0.13), rough=0.4, metal=0.5)
    piezas = []
    piezas.append(_caja("_vid", -w / 2, w / 2, -0.05, -0.04, 0, h, coll, vid))            # vidrio hundido 11 cm en el recuadro
    piezas.append(_caja("_fondo", -w / 2, w / 2, -0.02, -0.01, 0, h, coll, P.mat("InteriorOscuro", (0.03, 0.03, 0.035), rough=0.9)))
    t = 0.05
    for (x0, x1, z0, z1) in [(-w / 2, -w / 2 + t, 0, h), (w / 2 - t, w / 2, 0, h), (-w / 2, w / 2, h - t, h), (-w / 2, w / 2, 0, t),
                             (-0.025, 0.025, 0, h), (-w / 2, w / 2, h * 0.64, h * 0.64 + 0.04),
                             (-w / 4 - 0.015, -w / 4 + 0.015, h * 0.64, h), (w / 4 - 0.015, w / 4 + 0.015, h * 0.64, h)]:
        piezas.append(_caja("_mar", x0, x1, -0.09, -0.04, z0, z1, coll, acero))
    # recuadro de estuco alrededor (sobresale 6 cm de la pared) y alféizar
    b = 0.16
    for (x0, x1, z0, z1) in [(-w / 2 - b, -w / 2, -0.05, h + b), (w / 2, w / 2 + b, -0.05, h + b), (-w / 2 - b, w / 2 + b, h, h + b)]:
        piezas.append(_caja("_rec", x0, x1, -0.16, 0.0, z0, z1, coll, crema))
    piezas.append(_caja("_alf", -w / 2 - 0.22, w / 2 + 0.22, -0.24, 0.0, -0.14, 0.0, coll, crema))
    for o in piezas:
        o.select_set(True)
    bpy.context.view_layer.objects.active = piezas[0]
    with bpy.context.temp_override(active_object=piezas[0], selected_editable_objects=piezas):
        bpy.ops.object.join()
    ob = piezas[0]
    ob.name = "VentanaBase"
    ob.data.name = "VentanaBase"
    return ob


class Edificio:
    def __init__(self, sc, coll=None, color_patas=True):
        self.sc = sc
        self.coll = coll or P.collection("Edificio")
        self.raiz = P.empty("Edificio", coll=self.coll)
        self.raiz.rotation_mode = "XYZ"
        self._cuerpo()
        self._patas(color_patas)
        self.dist0 = 0.0

    # ---------------- cuerpo ----------------
    def _alas(self):
        return [(-22, 22, -6, 6), (-6, 6, 6, 28)]

    def _cuerpo(self):
        c, r = self.coll, self.raiz
        lad, est, base = mat_ladrillo(), mat_estuco(), P.mat("Zocalo1935", (0.30, 0.29, 0.27), rough=0.7)
        acero = P.mat("Acero", (0.22, 0.23, 0.25), rough=0.45, metal=0.8)
        z0 = 0.7                              # el marco de acero mide 0,7 m
        H = z0 + 1.0 + PISOS * PISO
        self.alto = H
        # marco de acero (vigas en grilla) bajo todo el edificio
        self.marco = []
        for (x0, x1, y0, y1) in self._alas():
            self.marco.append(_caja("MarcoBorde", x0 - 0.3, x1 + 0.3, y0 - 0.3, y1 + 0.3, 0.0, 0.25, c, acero, r))
            x = x0
            while x <= x1 + 0.01:
                self.marco.append(_caja("Viga", x - 0.18, x + 0.18, y0 - 0.3, y1 + 0.3, 0.25, z0, c, acero, r))
                x += 2.0
        for (x0, x1, y0, y1) in self._alas():
            _caja("Zocalo", x0, x1, y0, y1, z0, z0 + 1.0, c, base, r)
            _caja("Muro", x0 + 0.05, x1 - 0.05, y0 + 0.05, y1 - 0.05, z0 + 1.0, H, c, lad, r)
            for k in range(PISOS + 1):         # fajas de estuco entre pisos (la firma de los 30)
                zz = z0 + 1.0 + k * PISO
                _caja("Faja", x0 - 0.12, x1 + 0.12, y0 - 0.12, y1 + 0.12, zz - 0.18, zz + 0.12, c, est, r)
            _caja("Parapeto", x0 - 0.15, x1 + 0.15, y0 - 0.15, y1 + 0.15, H, H + 0.9, c, est, r)
            _caja("Techo", x0 + 0.2, x1 - 0.2, y0 + 0.2, y1 - 0.2, H, H + 0.5, c, P.mat("TechoGris", (0.35, 0.34, 0.33), rough=0.9), r)
            for (xa, ya) in [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]:   # pilastras de esquina
                _caja("Pilastra", xa - 0.45, xa + 0.45, ya - 0.45, ya + 0.45, z0 + 1.0, H + 0.9, c, est, r)
        # torreón de la escalera y entrada con marquesina al centro de la fachada
        _caja("Torre", -3.5, 3.5, -2.5, 2.5, H, H + 3.4, c, est, r)
        _caja("TorreRemate", -3.8, 3.8, -2.8, 2.8, H + 3.4, H + 3.8, c, est, r)
        _caja("Marquesina", -4.0, 4.0, -8.0, -6.0, z0 + 1.0 + 2.95, z0 + 1.0 + 3.65, c, est, r)
        _caja("Puerta", -1.6, 1.6, -6.12, -6.0, z0 + 1.0, z0 + 1.0 + 2.8, c, P.mat("PuertaMadera", (0.26, 0.12, 0.05), rough=0.6), r)
        txt = P.text3d("Placa1935", "1935", size=0.62, extrude=0.05, coll=c, m=P.mat("PlacaOscura", (0.20, 0.14, 0.08), rough=0.5, metal=0.3))
        txt.parent = r
        txt.location = (0, -8.04, z0 + 1.0 + 3.02)
        txt.rotation_euler = (math.radians(90), 0, 0)
        self.placa = txt
        # ventanas (instancias)
        vb = _ventana_malla(c)
        vb.hide_render = True
        vb.hide_viewport = True
        self.ventanas = []

        def fila(xs, y, yaw, nx=None):
            for k in range(PISOS):
                zz = z0 + 1.0 + k * PISO + 0.8
                for x in xs:
                    if k == 0 and abs(x) < 2.5 and abs(y + 6) < 0.5:
                        continue                   # la puerta
                    o = bpy.data.objects.new("Ventana", vb.data)
                    c.objects.link(o)
                    o.parent = r
                    if nx is None:
                        o.location = (x, y, zz)
                    else:
                        o.location = (nx, x, zz)
                    o.location += Matrix.Rotation(yaw, 3, 'Z') @ Vector((0, 0.07, 0))
                    o.rotation_euler = (0, 0, yaw)
                    self.ventanas.append(o)

        xs_frente = [-19.5 + 3.0 * i for i in range(14)]
        fila(xs_frente, -6.02, 0.0)
        fila([x for x in xs_frente if abs(x) > 7.5], 6.02, math.pi)
        fila([-3.0, 0.0, 3.0][::1], 28.02, math.pi)
        ys_tallo = [9.0 + 3.0 * i for i in range(7)]
        fila(ys_tallo, None, math.pi / 2, nx=6.02)
        fila(ys_tallo, None, -math.pi / 2, nx=-6.02)
        fila([-3.0, 3.0], None, math.pi / 2, nx=22.02)
        fila([-3.0, 3.0], None, -math.pi / 2, nx=-22.02)
        self.z_cuerpo = z0

    # ---------------- patas ----------------
    def _patas(self, color):
        c = self.coll
        ma = P.mat("PataA", AMARILLO if color else (0.5, 0.5, 0.5), rough=0.35, metal=0.2)
        mb = P.mat("PataB", CELESTE if color else (0.5, 0.5, 0.5), rough=0.35, metal=0.2)
        cromo = P.mat("Cromo", (0.78, 0.79, 0.80), rough=0.28, metal=1.0)
        goma = P.mat("Goma", (0.06, 0.06, 0.065), rough=0.8)
        self.carcasa_h = 1.3
        mesh_ca = P.prim("cyl", "_carcasaA", c, ma, r=0.36, r2=0.36, h=self.carcasa_h, seg=24)
        mesh_cb = P.prim("cyl", "_carcasaB", c, mb, r=0.36, r2=0.36, h=self.carcasa_h, seg=24)
        mesh_v = P.prim("cyl", "_vastago", c, cromo, r=0.17, r2=0.17, h=1.0, seg=20)
        mesh_p = P.prim("cube", "_pie", c, goma, smooth=False)
        for o in (mesh_ca, mesh_cb, mesh_v):        # origen arriba: la pieza cuelga hacia -Z
            o.data.transform(Matrix.Translation((0, 0, -0.5 * (self.carcasa_h if o is not mesh_v else 1.0))))
        mesh_p.data.transform(Matrix.Diagonal((1.05, 1.05, 0.30, 1)) @ Matrix.Translation((0, 0, 0.5)))
        for o in (mesh_ca, mesh_cb, mesh_v, mesh_p):
            o.hide_render = True
            o.hide_viewport = True
        self.patas = []
        pts = [(-21 + 2 * i, -5 + 2 * j) for i in range(22) for j in range(6)]
        pts += [(-5 + 2 * i, 7 + 2 * j) for i in range(6) for j in range(11)]
        assert len(pts) == 198
        for n, (x, y) in enumerate(pts):
            ii, jj = round((x + 21) / 2), round((y + 5) / 2)
            g = (ii + jj) % 2                  # damero: 0 = A (amarillo), 1 = B (celeste)
            ca = bpy.data.objects.new(f"Pata{n:03d}_c", (mesh_ca if g == 0 else mesh_cb).data)
            va = bpy.data.objects.new(f"Pata{n:03d}_v", mesh_v.data)
            pi = bpy.data.objects.new(f"Pata{n:03d}_p", mesh_p.data)
            for o in (ca, va, pi):
                c.objects.link(o)
                o.rotation_mode = "QUATERNION"
            self.patas.append(dict(x=x, y=y, g=g, c=ca, v=va, p=pi, n=n))

    # ---------------- caminar ----------------
    @staticmethod
    def matriz(x, y, yaw, z=0.0):
        return Matrix.Translation((x, y, z)) @ Matrix.Rotation(yaw, 4, "Z")

    def poner(self, dist, pose, alto=ALTO_PATA, bob=0.10, visibles=None, extension=1.0, sin_pasos=False, suelo=0.0, marco=True):
        """Pone el edificio y las 198 patas para la distancia recorrida `dist` (m).
        pose(d) -> (x, y, yaw). extension < 1 encoge las patas (el edificio baja); visibles = cuántas patas se ven (contador)."""
        x, y, yaw = pose(dist)
        ciclo = 2 * PASO
        fase_a = (dist / ciclo) % 1.0
        # el cuerpo baja apenas cuando el peso pasa de un grupo al otro
        z = suelo + alto * extension - (0 if sin_pasos else bob * (0.5 - 0.5 * math.cos(4 * math.pi * fase_a)))
        for o in self.marco:
            o.hide_render = not marco
        self.raiz.location = (x, y, z)
        self.raiz.rotation_euler = (0, 0, yaw)
        Mc = self.matriz(x, y, yaw, z)
        for k, pt in enumerate(self.patas):
            vis = visibles is None or k < visibles
            for o in (pt["c"], pt["v"], pt["p"]):
                o.hide_render = not vis
            if not vis:
                continue
            fase = (fase_a + 0.5 * pt["g"]) % 1.0
            if sin_pasos:
                fase = 0.25
            if fase < 0.5:     # apoyo: el pie quedó fijo donde aterrizó
                d0 = dist - fase * ciclo
                px, py, pyaw = pose(d0)
                pie = self.matriz(px, py, pyaw) @ Vector((pt["x"] + PASO / 2, pt["y"], 0))
                pie.z = suelo
            else:              # en el aire: del despegue al aterrizaje, con arco
                s = (fase - 0.5) / 0.5
                d_lo = dist - (fase - 0.5) * ciclo
                a = self.matriz(*pose(d_lo)) @ Vector((pt["x"] - PASO / 2, pt["y"], 0))
                b = self.matriz(*pose(d_lo + PASO)) @ Vector((pt["x"] + PASO / 2, pt["y"], 0))
                e = s * s * (3 - 2 * s)
                pie = a.lerp(b, e)
                pie.z = suelo + ALZA * math.sin(math.pi * s) * extension
            arriba = Mc @ Vector((pt["x"], pt["y"], 0.0))
            d = pie + Vector((0, 0, 0.28)) - arriba          # hasta la cara de arriba del pie
            L = max(d.length, self.carcasa_h + 0.05)
            q = (-d).to_track_quat("Z", "Y")                 # el eje +Z local apunta hacia arriba (las piezas cuelgan en -Z)
            pt["c"].location = arriba
            pt["c"].rotation_quaternion = q
            pt["v"].location = arriba + d.normalized() * (self.carcasa_h - 0.05)
            pt["v"].rotation_quaternion = q
            pt["v"].scale = (1, 1, max(0.05, L - self.carcasa_h + 0.05))
            pt["p"].location = pie
            pt["p"].rotation_quaternion = Euler((0, 0, yaw)).to_quaternion()
        return dict(x=x, y=y, yaw=yaw, fase=fase_a)


    def quieto(self, x=0.0, y=0.0, yaw=0.0):
        """Antes de la mudanza: sin patas ni marco, el zócalo apoyado en el suelo."""
        self.poner(0.0, recta(x, y, yaw), alto=-self.z_cuerpo, visibles=0, sin_pasos=True, marco=False)


def recta(x0=0.0, y0=0.0, yaw=0.0):
    """Camina derecho por +x local de su orientación."""
    def pose(d):
        return (x0 + d * math.cos(yaw), y0 + d * math.sin(yaw), yaw)
    return pose


def curva(total=62.0, giro=math.radians(21), x0=0.0, y0=0.0, yaw0=0.0):
    """El trayecto real: 62 m en curva, girando 21° parejo a lo largo del camino."""
    def pose(d):
        d = max(0.0, min(total, d)) if total else d
        k = giro / total
        if abs(k) < 1e-9:
            return (x0 + d * math.cos(yaw0), y0 + d * math.sin(yaw0), yaw0)
        th = yaw0 + k * d
        R = 1 / k
        return (x0 + R * (math.sin(th) - math.sin(yaw0)), y0 - R * (math.cos(th) - math.cos(yaw0)), th)
    return pose

