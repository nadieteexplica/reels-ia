"""Planos del Ep. 6 (proceso v2, estilo realista): 5 escenas, 25 planos (storyboard.md v2, puerta 3 APROBADO).

E1 cabina en plano  — el 4x4 detenido en el camino de tierra; el caballero contra el cinturón. Planos 1–4, 6, 10, 12.
E2 retractor        — el mecanismo por dentro del pilar. Planos 5, 7–9, 11, 17, 18.
E3 exterior cerro   — el 4x4 trepa el cerro de roca y llega arriba. Planos 13, 19, 21.
E4 cabina en subida — la cabina inclinada 30°: se traban los cuatro. Planos 14–16, 20.
E5 cabina arriba    — en plano otra vez: el truco y el doctor. Planos 22–25 (el 25 termina en la cámara del cuadro 0).

Cada pieza arma su escena y devuelve actualizar(f) (todo calculado por cuadro, sin keyframes) y su meta para el post.
"""
import math, os, random, sys
import bpy
from mathutils import Vector, Quaternion, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../plantilla")))
import ep06 as E
import kit5 as K
from kit5 import F, FR, T, lin, suave, sale, tramo, ruido, clamp, mirar, pantalla, oculto, mezcla

FPS = 30
ESCENA = {1: "E1", 2: "E1", 3: "E1", 4: "E1", 5: "E2", 6: "E1", 7: "E2", 8: "E2", 9: "E2", 10: "E1", 11: "E2", 12: "E1",
          13: "E3", 14: "E4", 15: "E4", 16: "E4", 17: "E2", 18: "E2", 19: "E3", 20: "E4", 21: "E3", 22: "E5", 23: "E5",
          24: "E5", 25: "E5"}
SENTADO = os.path.join(K.ASSETS, E.SENTADO_FBX)
PRIV = os.environ.get("PRIV_MIXAMO", "")          # carpeta mixamo/ del repo privado (Arm Gesture, Shrugging…)


def tf(f):
    return (f - 1) / FPS


def TW(prefijo, desde=0.0):
    return K.t_palabra(prefijo, desde)


def anim(nombre):
    """Ruta de una animación de Mixamo (Without Skin) del repo privado o de los assets."""
    for d in (PRIV, K.ASSETS):
        if d and os.path.isdir(d):
            for raiz, _, fs in os.walk(d):
                for x in fs:
                    if x.lower().replace(" ", "").replace(".", "").startswith(nombre.lower().replace(" ", "").replace(".", "")) and x.lower().endswith(".fbx"):
                        return os.path.join(raiz, x)
    return None


# ------------------------------------------------------------------ poses: guardar / restaurar (sin acumular giros)
def guardar(arm):
    return {b.name: b.rotation_quaternion.copy() for b in arm.pose.bones}


def restaurar(arm, d):
    for b in arm.pose.bones:
        b.rotation_mode = "QUATERNION"
        if b.name in d:
            b.rotation_quaternion = d[b.name].copy()


def respirar(arm, f, semilla=0, k=1.0):
    """Vida (≤ 1 s quieto): pecho que respira, cabeza que deriva y hombros que se acomodan."""
    E.girar(arm, "Spine2", (1, 0, 0), 1.6 * k * math.sin(f * 0.21 + semilla))
    E.girar(arm, "Neck", (0, 0, 1), 4.0 * k * ruido(f, semilla + 3, 0.6))
    E.girar(arm, "Head", (1, 0, 0), 2.5 * k * ruido(f, semilla + 7, 0.5))


def ojos(sc, arm, quien):
    hb = next((b for b in arm.data.bones if b.name.split(":")[-1] == "Head"), None)
    if hb is None:
        return
    for s, lado in ((1, "L"), (-1, "R")):
        o = K.marca_ojo(sc, f"{quien}_ojo{lado}", arm, (0, 0, 0), 0.012)
        o.parent_type = "BONE"; o.parent_bone = hb.name
        o.location = (s * 3.2, 8.5, 9.0)


# ------------------------------------------------------------------ la cabina (E1, E4, E5)
class Cabina:
    """El 4x4 con los cuatro sentados y sus cinturones. `incl` inclina todo (E4)."""

    def __init__(self, sc, incl=0.0, cerro=False, sol_az=None):
        self.sc = sc
        E.sol(sc, fuerza_cielo=0.25, sol=4.5, az=sol_az)
        sc.view_settings.exposure = 0.0
        E.desierto(sc)
        E.cerros(sc)
        self.zc = E.cerro_roca(sc, pendiente=30, origen=(0, -2.0, 0)) if cerro else None
        self.auto = E.auto(sc)
        self.arms, self.base = {}, {}
        for q in ("caballero", "piloto", "mascara", "doctor"):
            a = E.sentado(sc, q, SENTADO)
            if a is not None and E.tiene_esqueleto(a):
                self.arms[q] = a
        self.manos_al_volante()
        for q, a in self.arms.items():
            self.base[q] = guardar(a)
            ojos(sc, a, q)
        self.cintas = {}
        self.bolsa = E.bolsa(sc, E.BOLSA, rot=(math.radians(-80), 0, math.radians(15)))
        # todo cuelga del auto: inclinar el auto inclina la cabina entera
        for q, a in self.arms.items():
            a.parent = self.auto; a.matrix_parent_inverse = self.auto.matrix_world.inverted()
        self.bolsa.parent = self.auto; self.bolsa.matrix_parent_inverse = self.auto.matrix_world.inverted()
        reb = E.luz_area(sc, "Rebote", (0.1, -0.55, 1.5), (-0.37, 0.30, 1.45), 4, (1.0, 0.9, 0.82), 0.3, spread=60)
        reb.visible_glossy = False
        reb.parent = self.auto
        # la luz que rebota en el tapiz de atrás: sin esto los de atrás quedan en negro (muestras v2)
        reb2 = E.luz_area(sc, "Rebote2", (0.0, 1.50, 1.70), (0.0, 0.80, 1.15), 8.0, (1.0, 0.88, 0.75), 0.7, spread=80)
        reb2.visible_glossy = False
        reb2.parent = self.auto
        self.incl = incl
        self.poner(incl)

    def poner(self, grados, y_contacto=E.EJE_TRASERO_Y):
        z = self.zc(y_contacto) if self.zc else 0.0
        E.poner_auto(self.auto, grados, y_contacto=y_contacto, z_contacto=z)

    def manos_al_volante(self):
        p = self.arms.get("piloto")
        if not p:
            return
        vol = E.en_auto((0.37, -0.22, 1.28))
        for lado, dx in (("Left", 0.16), ("Right", -0.16)):
            mano = vol + E.dir_auto((dx, 0, 0.02))
            hombro = E.pos_hueso(p, f"{lado}Arm")
            codo = hombro.lerp(mano, 0.5) + E.dir_auto((0, 0.05, -0.15))
            E.apuntar_hueso(p, f"{lado}Arm", codo - hombro)
            E.apuntar_hueso(p, f"{lado}ForeArm", mano - E.pos_hueso(p, f"{lado}ForeArm"))

    def mundo(self, p):
        return self.auto.matrix_world @ Vector(p)

    def pose(self, q, f, lanza=0.0, palmas=0.0, mimica=0.0, encoge=0.0, mira=0.0):
        a = self.arms.get(q)
        if not a:
            return
        restaurar(a, self.base[q])
        if q == "piloto":
            self.manos_al_volante()
        bpy.context.view_layer.update()
        respirar(a, f, semilla=len(q))
        if lanza:
            E.lanzarse(a, lanza, hacia=(self.mundo(E.BOLSA) - E.pos_hueso(a, "LeftArm")))
        if palmas:
            for lado, s in (("Left", 1), ("Right", -1)):
                E.girar(a, f"{lado}Arm", (0, 1, 0), s * 35 * palmas)
                E.girar(a, f"{lado}ForeArm", (0, 0, 1), s * 55 * palmas)
                E.girar(a, f"{lado}Hand", (0, 1, 0), s * 60 * palmas)
        if mimica:
            E.girar(a, "LeftArm", (0, 1, 0), 30 * mimica)
            E.girar(a, "LeftForeArm", (1, 0, 0), -60 * mimica - 12 * math.sin(f * 0.15))
            E.girar(a, "RightArm", (0, 1, 0), -30 * mimica)
            E.girar(a, "RightForeArm", (1, 0, 0), -60 * mimica - 12 * math.sin(f * 0.15 + 1.2))
        if encoge:
            for lado in ("Left", "Right"):
                E.girar(a, f"{lado}Shoulder", (1, 0, 0), -14 * encoge)
            E.girar(a, "Head", (1, 0, 0), 6 * encoge)
        if mira:
            E.girar(a, "Neck", (0, 0, 1), 35 * mira)
            E.girar(a, "Head", (0, 0, 1), 25 * mira)

    def cinturones(self, quienes=None, capa=None, comba=None):
        """Rehace las cintas de los que se movieron (una curva de 3 anclas colgada de los huesos). `capa` = {quien: "roja" |
        "verde"} pone la capa de explicación (roja = trabada y tensa, verde = suelta); `comba` = {quien: metros}."""
        capa = capa or {}; comba = comba or {}
        for q, a in self.arms.items():
            if quienes is not None and q not in quienes and q in self.cintas:
                continue
            for o in self.cintas.get(q, ()):
                bpy.data.objects.remove(o, do_unlink=True)
            bpy.context.view_layer.update()
            objs = list(E.cinturon_de(self.sc, a, q, raiz=None, comba=comba.get(q, 0.0)))
            if capa.get(q):
                color = (0.95, 0.12, 0.08) if capa[q] == "roja" else (0.15, 0.85, 0.3)
                E.capa_cinta(self.sc, objs[0], color)
            self.cintas[q] = tuple(objs)


# ------------------------------------------------------------------ escenas
def cam_cabina(sc, pos, mira, lente=35, fstop=5.6, foco=None):
    return E.camara(sc, pos, mira, lente=lente, fstop=fstop, foco=foco)


def pieza_cabina(sc, a, b, k):
    incl = 30.0 if ESCENA[k] == "E4" else 0.0
    cab = Cabina(sc, incl=incl, cerro=ESCENA[k] == "E4", sol_az=E.SOL_AZ_CERRO if ESCENA[k] == "E4" else None)
    if ESCENA[k] == "E4":
        cab.poner(30.0, y_contacto=-9.0)
    cam = cam_cabina(sc, (0, 0, 0), (0, 1, 0))
    W = cab.mundo
    # atrás y en el pilar llega menos sol: la cámara expone más (como una de verdad), sin subir luces falsas
    sc.view_settings.exposure = {25: 0.9, 4: 0.4, 22: 0.5, 20: 0.9}.get(k, 0.0)
    # plano 1 (y su repetición en el 10 y el loop del 25): foco corto, la mano que se acerca queda blanda como en una cámara real
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = {1: 2.0, 10: 2.0, 25: 2.8}.get(k, 5.6)
    if k == 24:      # la bolsa ya no está en el tablero (cayó atrás en la subida): sólo migas (puerta 6 r1, B2)
        E.migas(sc, tuple(W((0.0, -0.40, 1.335))), n=60, r=0.07, semilla=5)
    if k == 25:      # el remate: migas naranjas sobre el delantal del doctor y luz que entra por su ventana al regazo
        E.migas(sc, tuple(W((0.40, 0.74, 1.17))), n=45, r=0.07, semilla=7)
        luz = E.luz_area(sc, "LuzDoctor", tuple(W((0.62, 0.62, 1.66))), tuple(W((0.40, 0.80, 1.12))), 9.0, (1.0, 0.82, 0.62), 0.45, spread=70)
        luz.visible_glossy = False
    t0, t1 = T[k]

    def actualizar(f):
        t = tf(f)
        u = lin(t, t0, t1)
        info = {}
        if k in (1, 10):
            # lanzarse y el CLAC: en el 1 ya va lanzado desde el cuadro 0; el tope a 0,9 s, rebote
            tc = t0 + (0.9 if k == 1 else 0.05)
            lanza = 1.0 if t < tc else max(0.0, 1.0 - 2.2 * (t - tc)) * 0.55 + 0.25 * math.exp(-6 * (t - tc))
            cab.pose("caballero", f, lanza=lanza)
            sac = 0.012 * math.exp(-18 * max(0, t - tc)) * math.sin(70 * max(0, t - tc)) if t >= tc else 0
            mirar(cam, W((-0.08 + sac, -1.30, 1.58 + sac)), W((-0.25, 0.10, 1.42)), lente=35, foco=W((-0.32, 0.10, 1.50)))
        elif k == 2:
            cab.pose("caballero", f, lanza=0.95)
            cab.bolsa.location.x = 0.03 * sale(lin(t, t0 + 0.6, t0 + 1.2))
            fo = W((-0.10, -0.28, 1.40)).lerp(W(E.BOLSA), suave(lin(t, t0 + 0.5, t0 + 0.9)))
            mirar(cam, W((0.12, -1.00, 1.45)), W(E.BOLSA), lente=85, foco=fo)
        elif k in (3, 12):
            cab.pose("caballero", f, lanza=0.6 * suave(lin(t, t0 + 0.4, t1)) + 0.15)
            cab.pose("mascara", f, mira=0.6 * suave(lin(t, t0 + 1.8, t0 + 2.3)) if k == 3 else 0.0)
            x = mezcla(0.02, -0.20, suave(u)); y = mezcla(0.90, 0.85, suave(u))
            mirar(cam, W((1.05, mezcla(-0.25, -0.18, suave(u)), 1.47)), W((-0.40, 0.28, 1.48)), lente=50, foco=W((-0.40, 0.28, 1.50)))
        elif k == 4:
            cab.pose("caballero", f, lanza=0.15)
            guia = W(E.PILAR_GUIA["caballero"]); ret = W(E.RETRACTOR)
            m = guia.lerp(ret, 0.5 * suave(lin(t, t0 + 0.4, t1)))
            mirar(cam, W((-0.15, 0.85, 1.70)), m, lente=50, foco=m)
        elif k == 6:
            cab.pose("caballero", f, lanza=suave(lin(t, t0, t0 + 0.5)))
            mirar(cam, W((-0.20, -1.55, 1.62)), W((-0.37, 0.30, 1.40)), lente=50, foco=W((-0.37, 0.25, 1.42)))
        elif k in (14, 15, 16, 20):
            if k in (16, 20):
                cab.bolsa.location = Vector((0.18, 0.80, 1.00))     # ya cayó atrás, junto al doctor (puerta 6 r1, B2)
            for q in cab.arms:
                cab.pose(q, f, palmas=(suave(lin(t, t0 + 0.2, t0 + 0.7)) if (k == 16 and q != "piloto") else 0.0),
                         mira=(0.5 * math.sin(t * 2.0 + len(q)) * suave(lin(t, t0, t0 + 0.4)) if k == 16 else 0.0))
            if k == 15:
                cab.bolsa.location = Vector(E.BOLSA).lerp(Vector((0.18, 0.80, 1.00)), sale(lin(t, t0 + 0.05, t0 + 0.45)))
            if k == 20:
                mirar(cam, W((0.0, -0.05, 1.69)), W((-0.40, 0.95, 1.52)), lente=85, foco=W((-0.40, 0.90, 1.55)))
                info["gota"] = round(lin(t, t0, t1), 3)
            elif k == 15:
                fb = cab.bolsa.matrix_world.translation
                mirar(cam, W((0.10, -1.10, 1.50)), W((0.10, 0.60, 1.25)), lente=35, foco=fb)
            else:
                mirar(cam, W((0.0, -1.05, 1.55)), W((0.0, 0.40, 1.50)), lente=35, foco=W((0.0, 0.3, 1.5)))
        elif k == 22:
            # "déjalo volver un poquito": se echa atrás y la cinta entra por la ranura; la cámara se acerca a la guía
            cab.bolsa.location = Vector((0.40, 0.78, 1.14))
            cab.pose("caballero", f, lanza=0.45 * (1 - suave(lin(t, t0 + 0.1, t0 + 0.9))))
            m = W(E.PILAR_GUIA["caballero"])
            mirar(cam, W((-0.15, 0.85, 1.70)).lerp(m, 0.25 * suave(u)), m, lente=mezcla(50, 65, suave(u)), foco=m)
        elif k == 23:
            cab.bolsa.location = Vector((0.40, 0.78, 1.14))
            cab.pose("caballero", f, lanza=0.5 * suave(lin(t, t0 + 0.3, t1)))
            cab.pose("mascara", f, mimica=suave(lin(t, t0, t0 + 0.3)))
            mirar(cam, W((-0.10, -1.05, 1.55)), W((-0.30, 0.60, 1.55)), lente=40, foco=W((-0.35, 0.30, 1.55)))
        elif k == 24:
            cab.pose("caballero", f, lanza=0.9)
            cab.bolsa.location = Vector((0.40, 0.78, 1.14))     # en la falda del doctor, fuera de cuadro
            fo = W((-0.10, -0.28, 1.40)).lerp(W(E.TABLERO_CENTRO), suave(lin(t, t0 + 1.1, t0 + 1.5)))
            mirar(cam, W((0.12, -1.00, 1.45)), W(E.TABLERO_CENTRO), lente=85, foco=fo)
        elif k == 25:
            cab.pose("doctor", f, encoge=suave(lin(t, t0 + 1.3, t0 + 1.8)))
            cab.bolsa.location = Vector((0.40, 0.78, 1.14))
            if t < t0 + 2.1:
                mirar(cam, W((0.88, 0.66, 1.64)).lerp(W((0.84, 0.70, 1.60)), suave(u)), W((0.40, 0.80, 1.14)), lente=50, foco=W((0.40, 0.78, 1.14)))
            else:     # loop: corte a la cámara del cuadro 0
                cab.bolsa.location = Vector(E.BOLSA)
                cab.pose("caballero", f, lanza=1.0)
                mirar(cam, W((-0.08, -1.30, 1.58)), W((-0.25, 0.10, 1.42)), lente=35, foco=W((-0.32, 0.10, 1.50)))
        # sin capa de color en 3D: la cinta teñida no pasó la puerta 4 en dos rondas (se leía como una franja plana); la
        # cinta queda negra de verdad y el rojo/verde lo ponen las píldoras y los subtítulos del post (regla v2: lo que falla
        # dos veces se simplifica)
        capa, comba = {}, {}
        if k in (3, 12, 23):
            comba["caballero"] = 0.035 * suave(lin(t, t0 + 0.8, t0 + 1.6)) if k in (3, 23) else 0.035
        cab.cinturones(quienes=("caballero",) if k not in (14, 15, 16, 20) else None, capa=capa, comba=comba)
        return info

    return {"actualizar": actualizar, "meta": {"escena": ESCENA[k]}}


def pieza_retractor(sc, a, b, k):
    E.sol(sc, fuerza_cielo=0.15, sol=3.0)
    sc.view_settings.exposure = 0.3
    ret, RET = E.set_retractor(sc, giro=0.0, bolita=0.0)
    eje = bpy.data.objects["EjeCarrete"]; pes = bpy.data.objects["PivotePestillo"]
    taza = bpy.data.objects["Taza"]; bola = bpy.data.objects["Bolita"]; pal = bpy.data.objects["PivotePalanca"]
    bola0 = bola.location.copy()
    cam = E.camara(sc, tuple(RET + Vector((0.62, -0.42, 0.14))), tuple(RET), lente=100, fstop=5.6)
    t0, t1 = T[k]
    giro = {"g": 0.0, "f": None}

    def actualizar(f):
        t = tf(f)
        u = lin(t, t0, t1)
        vel = {5: 0.6, 7: 6.0 + 18 * u, 8: 3.0, 9: 0.0, 11: 0.7, 17: 0.0, 18: 0.0}.get(k, 0.0)
        giro["g"] = (f - a) * vel
        eje.rotation_euler.x = math.radians(giro["g"])
        pes.rotation_euler.x = math.radians(-38 * (suave(lin(t, t0 + 1.3, t1)) if k == 8 else (1.0 if k == 9 else 0.0)))
        tilt = 0.0
        if k in (17, 18):
            tilt = 24.0
            roll = suave(lin(t, t0 + 0.4, t1)) if k == 17 else 1.0
            ang = 0.25 + 0.6 * roll
            bola.location = bola0 + Vector((0, -math.sin(ang) * 0.007, (1 - math.cos(ang)) * 0.006))
            pal.rotation_euler.x = math.radians(-22 * (suave(lin(t, t0 + 0.6, t0 + 1.2)) if k == 18 else 0.0))
        taza.rotation_euler.x = math.radians(tilt)
        if k in (5, 7, 11):
            c = RET + Vector((0.62, -0.42, 0.14)) * (1 - 0.05 * u)
            mirar(cam, c, RET + Vector((0, 0, 0.012)), lente=100, foco=RET)
        elif k in (8, 9):
            sac = (0.002 * math.exp(-14 * (t - t0 - 0.4)) * math.sin(80 * (t - t0))) if (k == 9 and t > t0 + 0.4) else 0
            mirar(cam, RET + Vector((0.42 + sac, -0.20, 0.08)), RET + Vector((0.033, 0, 0.012)), lente=100, foco=RET + Vector((0.033, 0, 0.012)))
        else:   # 17, 18: la tacita, abajo
            c = taza.matrix_world.translation
            mirar(cam, c + Vector((0.30, -0.22, 0.10 + 0.02 * u)), c + Vector((0, 0, -0.022 + 0.01 * u)), lente=100, foco=c)
        return {}

    return {"actualizar": actualizar, "meta": {"escena": "E2"}}


def pieza_exterior(sc, a, b, k):
    E.sol(sc, fuerza_cielo=0.2, sol=4.0, az=E.SOL_AZ_CERRO, elev=4.0)
    sc.view_settings.exposure = -0.4
    E.desierto(sc)
    E.cerros(sc)
    zc = E.cerro_roca(sc, pendiente=30, origen=(0, -2.0, 0))
    auto = E.auto(sc)
    for q in ("caballero", "piloto", "mascara", "doctor"):
        arm = E.sentado(sc, q, SENTADO)
        if arm is not None:
            arm.parent = auto; arm.matrix_parent_inverse = auto.matrix_world.inverted()
    cam = E.camara(sc, (0, 0, 0), (0, 1, 0), lente=35, fstop=8.0)
    t0, t1 = T[k]
    BASE = 2.66      # distancia entre ejes (m)

    def perfil(y):
        return zc(y)

    def actualizar(f):
        t = tf(f)
        u = lin(t, t0, t1)
        if k == 13:
            yr = mezcla(0.5, -4.0, sale(u))
        elif k == 19:
            yr = mezcla(-9.0, -11.0, u)
        else:   # 21: llega arriba (el cerro tiene 20 m: la cima plana desde y = −22)
            yr = mezcla(-19.5, -23.0, sale(u))
        yf = yr - BASE
        zr, zf = perfil(yr), perfil(yf)
        ang = math.degrees(math.atan2(zf - zr, BASE))
        E.poner_auto(auto, ang + 0.4 * math.sin(f * 0.9), y_contacto=yr + E.EJE_TRASERO_Y - 1.44, z_contacto=zr)
        c = auto.matrix_world @ Vector((0, 0.3, 1.2))
        az = math.radians(225)
        d = {13: 12.0, 19: 13.0, 21: 12.0}[k]
        # cámara un poco sobre el auto mirando a la ladera: menos cielo vacío y, a la izquierda, el llano de abajo como
        # referencia horizontal de los 30° (puerta 4 r1)
        pos = c + Vector((math.sin(az) * d, -math.cos(az) * d, 0.8))
        mirar(cam, pos, c + Vector((0, 0, 0.5)), lente={13: 35, 19: 40, 21: 35}[k], foco=c)
        return {"inclinacion": round(ang, 1)}

    return {"actualizar": actualizar, "meta": {"escena": "E3"}}


FUN = {}
for k in T:
    e = ESCENA[k]
    FUN[k] = (lambda kk: (lambda sc, a, b: pieza_cabina(sc, a, b, kk)))(k) if e in ("E1", "E4", "E5") else \
             (lambda kk: (lambda sc, a, b: pieza_retractor(sc, a, b, kk)))(k) if e == "E2" else \
             (lambda kk: (lambda sc, a, b: pieza_exterior(sc, a, b, kk)))(k)

PIEZAS = {}
for k in T:
    a, b = FR(k)
    n = b - a
    partes = 2 if n > int(os.environ.get("PARTIR", 45)) else 1
    if partes == 1:
        PIEZAS[str(k)] = {"a": a, "b": b, "fn": FUN[k], "base": str(k)}
    else:
        m = a + n // 2
        PIEZAS[f"{k}@1"] = {"a": a, "b": b, "fn": FUN[k], "base": str(k), "rango": (a, m)}
        PIEZAS[f"{k}@2"] = {"a": a, "b": b, "fn": FUN[k], "base": str(k), "rango": (m, b)}
