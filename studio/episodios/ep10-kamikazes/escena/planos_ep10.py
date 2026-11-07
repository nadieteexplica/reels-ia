"""Planos del Ep. 10 (kamikazes, realista): 4 sets y 6 actuaciones (storyboard.md v2, 53,7 s).

A mesa (E5): 1, 2, 9, 10, 26 (y el loop final, que el post toma del plano 1).
B pista con aviones al amanecer (E1): 3, 5, 20, 21.   C la fila de pilotos (E1): 6, 7, 8.   F pista al atardecer (E1): 27.
D el ataque al portaaviones (E3): 11–17.   E el mapa (E4): 4, 18, 19, 22–25.

Cada pieza arma su set desde cero y devuelve actualizar(f) (todo calculado por cuadro, sin keyframes) y su meta.
"""
import math, os, sys, random
import bpy
from mathutils import Vector, Euler, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../plantilla")))
import ep10 as E
import sets10 as S
import gente10 as G
import mapa10 as M
from ep10 import F, FR, T, lin, suave, sale, tramo, ruido, clamp, mirar, pantalla

FPS = 30
ESCENA = {1: "E5", 2: "E5", 3: "E1", 4: "E4", 5: "E1", 6: "E1", 7: "E1", 8: "E1", 9: "E5", 10: "E5", 11: "E3", 12: "E3",
          13: "E3", 14: "E3", 15: "E3", 16: "E3", 17: "E3", 18: "E4", 19: "E4", 20: "E1", 21: "E1", 22: "E4", 23: "E4",
          24: "E4", 25: "E4", 26: "E5", 27: "E1"}
PILOTOS = ["joe.fbx", "chad.fbx", "brian.fbx", "DAVID_nonPBR.fbx", "remy.fbx"]
OFICIAL = "STEVE_nonPBR.fbx"
MARINEROS = ["PETE_nonPBR.fbx", "chad.fbx"]
DECK = 16.4          # altura de la cubierta de vuelo sobre el agua (medida con rayos: 24,2 − 7,8)


def tf(f):
    return (f - 1) / FPS


def TW(prefijo, desde=0.0):
    return E.t_palabra(prefijo, desde)


# ============================================================ A · la mesa
def armar_mesa(sc):
    Mx = S.mesa(sc)
    cam = E.camara(sc, (0, 0, 1.5), (0, 0, 0.76), lente=50, fstop=4.0)
    sc.view_settings.exposure = 0.35
    return Mx, cam


def foto_punto(Mx, u, v):
    """Punto de la foto impresa en coordenadas de la imagen (u 0→1 izquierda a derecha, v 0→1 arriba a abajo)."""
    f = Mx["foto"]
    w, h = 0.12, 0.12 * 2323 / 1888
    return f.matrix_world @ Vector(((u - 0.5) * w, (0.5 - v) * h, 0.001))


CARAS_FOTO = [(0.265, 0.103), (0.68, 0.14), (0.87, 0.37), (0.20, 0.52), (0.54, 0.47)]   # (u, v) de las 5 caras en foto_impresa.jpg


def ojos_foto(sc, cam, Mx):
    out = []
    for i, (u, v) in enumerate(CARAS_FOTO):
        for du in (-0.028, 0.028):
            x, y = pantalla(sc, cam, foto_punto(Mx, u + du, v - 0.01))
            out.append([x, y, 14, f"cara{i}"])
    return out


def p1(sc, a, b):
    # CUADRO 0 · "Este kamikaze tiene diecisiete años.": la foto real llena el cuadro; el chico del centro en y ≈ 640
    Mx, cam = armar_mesa(sc)
    tgt0 = foto_punto(Mx, 0.5, 0.78)

    def act(f):
        t = tf(f)
        S.mesa_viva(Mx, t)
        x = sale(lin(f, a, b - 1))
        d = 0.56 - 0.025 * x
        mirar(cam, tgt0 + Vector((0, -0.07, d)), tgt0, lente=50, foco=foto_punto(Mx, 0.52, 0.45))
        return {"chico": pantalla(sc, cam, foto_punto(Mx, 0.54, 0.47)), "casco": pantalla(sc, cam, foto_punto(Mx, 0.54, 0.38)),
                "cachorro": pantalla(sc, cam, foto_punto(Mx, 0.635, 0.705)), "foto_top": pantalla(sc, cam, foto_punto(Mx, 0.5, 0.0)),
                "ojos": ojos_foto(sc, cam, Mx)}
    return {"actualizar": act}


def p2(sc, a, b):
    # "La foto es de 1945,": la cámara entra hasta el chico y el cachorro
    Mx, cam = armar_mesa(sc)
    t0 = foto_punto(Mx, 0.5, 0.78); t1 = foto_punto(Mx, 0.58, 0.72)

    def act(f):
        S.mesa_viva(Mx, tf(f))
        x = suave(lin(f, a, b - 1))
        tgt = t0.lerp(t1, x)
        d = 0.535 - 0.175 * x
        mirar(cam, tgt + Vector((0, -0.06 * d / 0.5, d)), tgt, lente=50, foco=foto_punto(Mx, 0.53, 0.45))
        cam.data.dof.aperture_fstop = 4.0 + 2.0 * x
        return {"chico": pantalla(sc, cam, foto_punto(Mx, 0.54, 0.47)), "ojos": ojos_foto(sc, cam, Mx)}
    return {"actualizar": act}


def p9(sc, a, b):
    # "Antes de despegar, le escriben a su familia…": la carta a pincel, el gorro del piloto al lado
    Mx, cam = armar_mesa(sc)
    c = Mx["carta"].matrix_world.translation

    def act(f):
        S.mesa_viva(Mx, tf(f))
        x = suave(lin(f, a, b - 1))
        tgt = c + Vector((0.03, 0.09 - 0.12 * x, 0))
        mirar(cam, tgt + Vector((0.1, -0.24, 0.3)), tgt, lente=50, foco=tgt)
        cam.data.dof.aperture_fstop = 4.0
        return {"carta": pantalla(sc, cam, c)}
    return {"actualizar": act}


def p10(sc, a, b):
    # "y le piden perdón.": la columna "先立つ不孝を お許しください"; detrás, la cinta y la copa
    Mx, cam = armar_mesa(sc)
    c = Mx["carta"].matrix_world.translation
    col = c + Vector((0.03, 0.0, 0.0))

    def act(f):
        S.mesa_viva(Mx, tf(f))
        x = sale(lin(f, a, b - 1))
        p = col + Vector((0.02, -0.26 - 0.12 * x, 0.16 + 0.06 * x))
        mirar(cam, p, col + Vector((0, 0.05, 0)), lente=50, foco=col)
        cam.data.dof.aperture_fstop = 2.8
        return {"columna": pantalla(sc, cam, col + Vector((0, 0.04, 0)))}
    return {"actualizar": act}


def p26(sc, a, b):
    # "Y el día que Japón se rinde…": la radio de madera encendida junto a la foto y la carta
    Mx, cam = armar_mesa(sc)
    r = bpy.data.objects["Radio"].matrix_world.translation

    def act(f):
        t = tf(f)
        S.mesa_viva(Mx, t)
        S.radio_dial(Mx, 0.8 * suave(lin(f, a, a + 18)) * (1 + 0.05 * math.sin(t * 40)))
        x = suave(lin(f, a, b - 1))
        fp = Mx["foto"].matrix_world.translation
        mirar(cam, Vector((0.10 - 0.03 * x, -0.50 + 0.06 * x, 0.90)), fp.lerp(r, 0.55) + Vector((0, 0, 0.02)), lente=50, foco=fp)
        cam.data.dof.aperture_fstop = 1.8
        return {"radio": pantalla(sc, cam, r)}
    return {"actualizar": act}


# ============================================================ B · la pista con aviones (amanecer)
def armar_pista(sc, hora="amanecer", pasto_en=None):
    P = S.pista(sc, hora=hora, pasto_en=pasto_en)
    cam = E.camara(sc, (0, 0, 2), (0, -10, 2), lente=35, fstop=None)
    sc.view_settings.exposure = -0.35
    return P, cam


def fila_aviones(sc, n=6, x=-30.0, y0=40.0, dy=-19.0, rot=0.0, bomba=True, vuelo=False):
    """Aviones estacionados en fila al costado de la pista (el primero real, el resto copias enlazadas)."""
    base = S.avion(sc, con_bomba=bomba, vuelo=vuelo, nombre="Fila0")
    base.location = (x, y0, 0)
    base.rotation_euler.z = math.pi + rot
    out = [base]
    col = bpy.data.collections.new("AvionCol")
    for o in [base] + list(base.children_recursive):
        col.objects.link(o)
    for i in range(1, n):
        inst = bpy.data.objects.new(f"Fila{i}", None)
        inst.instance_type = "COLLECTION"; inst.instance_collection = col
        sc.collection.objects.link(inst)
        inst.location = (x - base.location.x, y0 + i * dy - base.location.y, 0)
        inst.rotation_euler.z = 0.0 + random.uniform(-0.03, 0.03)
        out.append(inst)
    col.instance_offset = base.location.copy()
    for i, inst in enumerate(out[1:], 1):
        inst.location = Vector((x, y0 + i * dy, 0)) - Vector((0, 0, 0))
    return out


def p3(sc, a, b):
    # "el día antes de su misión.": la base al amanecer con bruma; aviones en fila, una barraca, el volcán al sur
    P, cam = armar_pista(sc, pasto_en=(10, 30))
    fila_aviones(sc, n=6, x=-28, y0=10, dy=-21)
    manga = bpy.data.objects["Manga"]; manga.location = (24, -46, 5.8)
    cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 5.6

    def act(f):
        t = tf(f)
        x = lin(f, a, b - 1)
        pos = Vector((-20.5, 23.0, 1.45)).lerp(Vector((-20.0, 20.0, 1.4)), x)
        mirar(cam, pos, Vector((-33, -60, 3.5)), lente=24, foco=Vector((-28, 10, 1.5)))
        manga.rotation_euler = (math.radians(-84 + 3 * math.sin(t * 2.3)), 0, math.radians(8 * math.sin(t * 1.1)))
        return {}
    return {"actualizar": act}


def p5(sc, a, b):
    # "y manda a sus pilotos a no volver.": detrás de las ramas del cerezo, un avión corre por la pista y despega
    P, cam = armar_pista(sc, pasto_en=(22, -18))
    av = S.avion(sc, con_bomba=True, vuelo=False, nombre="Despega")
    av.rotation_euler.z = math.pi           # nariz hacia −y (despega hacia el sur)
    tren = [o for o in S.mallas_de(av) if o.name in S.TREN]
    t_desp = T[5][0] + 0.9
    cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 4.0

    def act(f):
        t = tf(f)
        u = max(0.0, t - T[5][0])
        y = 34 - (9 * u + 8 * u * u)                 # acelera: pasa frente a la cámara a mitad del plano
        sube = max(0.0, t - t_desp)
        av.location = (0, y, 1.2 * sube * sube + 0.0)
        av.rotation_euler.x = -math.radians(min(9, 12 * sube))
        for o in tren:
            o.hide_render = sube > 0.8
        S.girar_helice(av, t * 40)
        mirar(cam, Vector((23, -26, 1.3)), av.location + Vector((0, -7, 1.8)), lente=35, foco=av.location)
        return {"avion": pantalla(sc, cam, av.location)}
    return {"actualizar": act}


def campo_redes(sc, filas=10, cols=8, x0=-160, y0=-40, dx=20, dy=22):
    """Plano 20: filas de aviones bajo redes de camuflaje en un campo junto a la pista."""
    base = S.avion(sc, con_bomba=False, vuelo=False, nombre="Red0")
    col = bpy.data.collections.new("RedCol")
    for o in [base] + list(base.children_recursive):
        col.objects.link(o)
    base.hide_render = True
    for o in base.children_recursive:
        o.hide_render = False
    random.seed(9)
    for i in range(filas):
        for j in range(cols):
            x, y = x0 - j * dx + random.uniform(-2, 2), y0 - i * dy + random.uniform(-2, 2)
            inst = bpy.data.objects.new(f"R{i}_{j}", None)
            inst.instance_type = "COLLECTION"; inst.instance_collection = col
            sc.collection.objects.link(inst)
            inst.location = (x, y, 0); inst.rotation_euler.z = math.pi + random.uniform(-0.15, 0.15)
    base.location = (0, 0, -50)
    col.instance_offset = (0, 0, -50)          # las copias no se van bajo tierra con el original


def p20(sc, a, b):
    # "Pero Japón junta casi trece mil aviones:": desde arriba, filas y filas bajo redes, hasta la bruma
    P, cam = armar_pista(sc)
    campo_redes(sc)

    def act(f):
        x = lin(f, a, b - 1)
        pos = Vector((-112, 22, 26)).lerp(Vector((-122, 8, 24)), x)
        mirar(cam, pos, Vector((-240, -150, 0)), lente=35)
        return {}
    return {"actualizar": act}


def p21(sc, a, b):
    # "todos, para chocar.": la fila de aviones desde la altura de las ruedas, cada uno con su bomba
    P, cam = armar_pista(sc, pasto_en=(-24, -20))
    fila_aviones(sc, n=5, x=-30, y0=20, dy=-16)

    def act(f):
        x = lin(f, a, b - 1)
        pos = Vector((-17.5, 12 - 26 * x, 0.6))
        mirar(cam, pos, Vector((-31, pos.y - 17, 1.4)), lente=24, foco=Vector((-30, pos.y - 8, 1.0)))
        return {}
    return {"actualizar": act}


# ============================================================ C · la fila de pilotos
LINEA_Y = 10.0


def armar_fila(sc):
    P, cam = armar_pista(sc, pasto_en=(0, 8))
    fila_aviones(sc, n=3, x=-14, y0=-6, dy=-20)
    pil = []
    for i, arch in enumerate(PILOTOS):
        x = -2.4 + 1.2 * i
        arm = G.persona(sc, arch, "piloto", (x, LINEA_Y, 0), rot_z=math.pi, pose="Happy Idle", frame=40 + 7 * i)
        pil.append((arm, G.guardar_pose(arm), Vector((x, LINEA_Y, 0))))
    of = G.persona(sc, OFICIAL, "oficial", (0, LINEA_Y - 4.2, 0), rot_z=0.0, pose="Happy Idle", frame=10)
    return P, cam, pil, (of, G.guardar_pose(of), Vector((0, LINEA_Y - 4.2, 0)))


ADELANTE = Vector((0, -1, 0))        # la fila mira al oficial (hacia −y)
T_PASO = None


def pasos(pil, t):
    """Los cuatro dan el paso al frente juntos (en el 7) y el del extremo, Fila 3, se queda y lo da después (en el 8)."""
    ta = T[7][0] + 0.3
    tb = T[8][0] + 0.6
    for i, (arm, base, p0) in enumerate(pil):
        t0 = tb if i == 3 else ta
        x = clamp((t - t0) / 0.55)
        if x <= 0:
            G.respirar(arm, base, t, fase=i * 1.3); arm.location = p0
        else:
            G.paso(arm, base, p0, ADELANTE, x)


def p6(sc, a, b):
    # "Oficialmente son voluntarios.": la fila de espalda frente al oficial con las manos atrás
    P, cam, pil, (of, ofb, ofp) = armar_fila(sc)
    cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 4.0

    def act(f):
        t = tf(f)
        pasos(pil, t)
        G.paso(of, ofb, ofp, Vector((0, 1, 0)), clamp((t - T[6][0] - 0.5) / 0.7) * 0.6)
        x = suave(lin(f, a, b - 1))
        mirar(cam, Vector((-3.0 + 2.4 * x, LINEA_Y + 6.0, 1.55)), Vector((0, LINEA_Y - 3.0, 1.3)), lente=50, foco=Vector((0, LINEA_Y, 1.4)))
        return {"oficial": pantalla(sc, cam, of.location + Vector((0, 0, 1.6)))}
    return {"actualizar": act}


def p7(sc, a, b):
    # "Pero decirle que no a tu escuadrón": las botas en fila, a ras del suelo; cuatro se adelantan y una se queda
    P, cam, pil, _ = armar_fila(sc)
    cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 2.8

    def act(f):
        t = tf(f)
        pasos(pil, t)
        mirar(cam, Vector((-6.5, LINEA_Y - 0.5, 0.3)), Vector((2.5, LINEA_Y - 0.3, 0.15)), lente=35, foco=Vector((0.3, LINEA_Y, 0.1)))
        return {}
    return {"actualizar": act}


def p8(sc, a, b):
    # "es casi imposible.": la fila ya adelantada; el último también da el paso
    P, cam, pil, _ = armar_fila(sc)
    cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 4.0

    def act(f):
        t = tf(f)
        pasos(pil, t)
        x = lin(f, a, b - 1)
        mirar(cam, Vector((-8.5 - 0.8 * x, LINEA_Y - 1.5, 1.5)), Vector((0.5, LINEA_Y - 0.4, 1.0)), lente=50, foco=Vector((0, LINEA_Y - 0.3, 1.2)))
        return {}
    return {"actualizar": act}


# ============================================================ F · la pista al atardecer (15 de agosto)
def p27(sc, a, b):
    # "todavía despegan kamikazes.": tres aviones despegan uno tras otro contra el cielo naranjo
    P, cam = armar_pista(sc, hora="atardecer")
    sol = P["sol"]
    sol.rotation_euler = (-Vector((math.sin(math.radians(165)) * 0.999, math.cos(math.radians(165)) * 0.999, math.sin(math.radians(1.5))))).to_track_quat("-Z", "Y").to_euler()
    sky = next(n for n in bpy.context.scene.world.node_tree.nodes if n.type == "TEX_SKY")
    sky.sun_rotation = math.radians(165); sky.sun_elevation = math.radians(1.5)
    avs = [S.avion(sc, con_bomba=True, vuelo=False, nombre=f"Sale{i}") for i in range(3)]
    for av in avs:
        av.rotation_euler.z = math.pi
    sc.view_settings.exposure = -0.1

    def act(f):
        t = tf(f)
        for i, av in enumerate(avs):
            ts = T[27][0] + 0.4 + 0.7 * i - 1.6
            u = max(0.0, t - ts)
            y = 40 - (10 * u + 8 * u * u)
            sube = max(0.0, t - ts - 1.4)
            av.location = (-3 + 6 * (i % 2), y, 1.5 * sube * sube)
            av.rotation_euler.x = -math.radians(min(10, 12 * sube))
            S.girar_helice(av, t * 40)
        mirar(cam, Vector((24, 14, 1.4)), Vector((-6, -45, 7)), lente=28)
        return {}
    return {"actualizar": act}


# ============================================================ D · el ataque al portaaviones
def armar_mar(sc, tiempo=0.0):
    S.cielo_mar(sc)
    S.mar(sc, tiempo=tiempo)
    pa = S.portaaviones(sc)
    S.barco_lejano(sc, "Essex", "essex", 266.0, (-900, 1600, -6), rot=-12)
    S.barco_lejano(sc, "Fletcher", "fletcher", 115.0, (650, 900, -4), rot=8)
    cam = E.camara(sc, (0, 0, 30), (0, 50, 30), lente=50, fstop=None)
    sc.view_settings.exposure = -0.3
    return pa, cam


def flak(sc, centro, n=10, r=180.0, semilla=3):
    """Nubecitas negras de la artillería antiaérea alrededor de un punto: aparecen, crecen y se deshacen."""
    random.seed(semilla)
    out = []
    for i in range(n):
        p = Vector(centro) + Vector((random.uniform(-r, r), random.uniform(-r, r), random.uniform(-r * 0.4, r * 0.4)))
        o = S.bocanada(sc, f"Flak{i}", p, 0.01, S.humo_mat("flak", (0.045, 0.043, 0.04), densidad=0.35, escala=2.2))
        out.append((o, p, random.uniform(0, 1.6), random.uniform(5, 9)))
    return out


def flak_vivo(lista, t, t0):
    for o, p, ret, rmax in lista:
        u = t - t0 - ret
        o.hide_render = u < 0
        if u >= 0:
            k = rmax * (1 - math.exp(-u * 3.0)) + 0.6 * u
            o.scale = (k, k, k * 0.85)
            o.location = p + Vector((1.5 * u, 0, 0.4 * u))


def estela(sc, nombre, n=14):
    """Humo detrás de un avión: esferas volumétricas que se quedan atrás y crecen."""
    m = S.humo_mat("estela", (0.05, 0.05, 0.05), densidad=0.7, escala=1.8)
    return [S.bocanada(sc, f"{nombre}{i}", (0, 0, -1000), 0.01, m) for i in range(n)]


def estela_viva(bolas, camino, t, paso=0.06, r0=1.2, crece=3.0):
    for i, o in enumerate(bolas):
        ti = t - i * paso
        p = camino(ti)
        k = r0 + crece * i * paso
        o.location = p; o.scale = (k, k, k)


def zero_vuelo(sc, nombre="Ataca", bomba=True):
    av = S.avion(sc, con_bomba=bomba, vuelo=True, nombre=nombre)
    return av


def orientar(av, d):
    """La nariz del avión (+y local) apunta en la dirección d."""
    q = Vector(d).normalized().to_track_quat("Y", "Z")
    av.rotation_mode = "QUATERNION"; av.rotation_quaternion = q


def p11(sc, a, b):
    # "Los estadounidenses no saben cómo frenar": un marinero con casco mira al cielo desde la cubierta
    pa, cam = armar_mar(sc)
    mar_arm = G.persona(sc, MARINEROS[0], "marinero", (7.0, 32.0, DECK), rot_z=math.radians(150), pose="Happy Idle", frame=30)
    base = G.guardar_pose(mar_arm)
    fl = flak(sc, (-120, -300, 420), n=8, r=160)
    cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 2.8

    def act(f):
        t = tf(f)
        G.respirar(mar_arm, base, t)
        G.mirar_arriba(mar_arm, base, suave(clamp((t - T[11][0] - 0.2) / 0.6)))
        flak_vivo(fl, t, T[11][0] - 1.0)
        x = lin(f, a, b - 1)
        mirar(cam, Vector((10.5 + 0.4 * x, 36.5, DECK + 1.0)), Vector((6.2, 31.0, DECK + 1.9)), lente=50, foco=Vector((7.0, 32.0, DECK + 1.6)))
        return {"marinero": pantalla(sc, cam, Vector((7.0, 32.0, DECK + 1.65)))}
    return {"actualizar": act}


CAM_CUB = Vector((4.0, 40.0, DECK + 1.7))      # un marinero en la cubierta, mirando al cielo hacia popa


def p12(sc, a, b):
    # "a alguien que no quiere volver.": el Zero en picada directo a la cámara, con humo detrás y flak alrededor
    pa, cam = armar_mar(sc)
    av = zero_vuelo(sc)
    humo = estela(sc, "Estela", 12)
    fl = flak(sc, (60, -320, 380), n=10, r=120, semilla=5)
    d0 = Vector((70, -420, 520)); d1 = Vector((12, -15, 55))

    def camino(t):
        u = clamp((t - T[12][0]) / (T[12][1] - T[12][0] + 0.15))
        return d0.lerp(d1, u ** 1.4)

    def act(f):
        t = tf(f)
        p = camino(t)
        av.location = p
        orientar(av, (CAM_CUB - p))
        S.girar_helice(av, t * 45)
        estela_viva(humo, camino, t - 0.08, paso=0.07)
        flak_vivo(fl, t, T[12][0] - 0.8)
        mirar(cam, CAM_CUB, p, lente=85)
        return {"avion": pantalla(sc, cam, p)}
    return {"actualizar": act}


def p13(sc, a, b):
    # "Llenan el cielo de balas": el Oerlikon de 20 mm dispara hacia arriba (fogonazo, trazadoras); el artillero de espalda
    pa, cam = armar_mar(sc)
    gpos = Vector((12.0, 22.0, DECK))
    mira = Vector((60, -220, 300))
    g, boca, dirf = S.oerlikon(sc, gpos, mira)
    art = G.persona(sc, MARINEROS[1], "marinero", (12.25, 23.35, DECK), rot_z=math.radians(172), pose="Happy Idle", frame=12)
    base = G.guardar_pose(art)
    fog = S.fogonazo(sc, "Fogonazo")
    traz = [S.trazadora(sc, f"Traz{i}") for i in range(8)]
    fl = flak(sc, (60, -260, 330), n=16, r=170, semilla=8)

    def act(f):
        t = tf(f)
        G.respirar(art, base, t)
        G.mirar_arriba(art, base, 0.8)
        k = int(t * 12) % 2 == 0
        fog.hide_render = not k
        fog.location = boca + dirf * 0.25
        orientar(fog, dirf)
        fog.rotation_quaternion = fog.rotation_quaternion @ Quaternion((1, 0, 0), math.radians(-90))
        for i, tr in enumerate(traz):
            u = (t * 6 + i / 8.0) % 1.0
            tr.location = boca + dirf * (8 + 320 * u)
            orientar(tr, dirf)
            tr.rotation_quaternion = tr.rotation_quaternion @ Quaternion((1, 0, 0), math.radians(90))
        flak_vivo(fl, t, T[13][0] - 1.2)
        x = lin(f, a, b - 1)
        mirar(cam, Vector((13.9 - 0.15 * x, 27.4, DECK + 1.55)), Vector((11.4, 18.0, DECK + 4.2)), lente=32, foco=Vector((12.2, 23.3, DECK + 1.5)))
        return {}
    return {"actualizar": act}


def p14(sc, a, b):
    # "y derriban a la mayoría.": dos aviones con humo caen al mar y levantan columnas de agua
    pa, cam = armar_mar(sc)
    avs = [zero_vuelo(sc, f"Cae{i}", bomba=False) for i in range(2)]
    humos = [estela(sc, f"HumoCae{i}", 14) for i in range(2)]
    golpe = [T[14][0] + 0.75, T[14][0] + 1.35]
    ini = [Vector((-150, -390, 150)), Vector((150, -760, 260))]
    fin = [Vector((-95, -350, 0)), Vector((205, -700, 0))]
    spl = [S.salpicadura(sc, f"Salp{i}", (fin[i].x, fin[i].y, 0), alto=26 - 6 * i) for i in range(2)]
    fl = flak(sc, (0, -500, 260), n=16, r=220, semilla=11)

    def camino_i(i):
        def c(t):
            u = clamp((t - (golpe[i] - 1.7)) / 1.7)
            return ini[i].lerp(fin[i], u) + Vector((0, 0, 40 * (1 - u) * u))
        return c

    def act(f):
        t = tf(f)
        for i, av in enumerate(avs):
            c = camino_i(i)
            p = c(t)
            av.hide_render = t > golpe[i]
            av.location = p
            dv = c(t + 0.05) - p
            orientar(av, dv if dv.length > 1e-3 else Vector((0, -1, -1)))
            estela_viva(humos[i], c, min(t, golpe[i]), paso=0.08, r0=2.0, crece=7.0)
            sp = spl[i]
            u = t - golpe[i]
            sp.hide_render = u < 0
            h = sp["alto"]
            k = max(0.02, min(1.0, u * 2.5))
            sp.scale = (h * 0.28 * (0.6 + 0.4 * k), h * 0.28 * (0.6 + 0.4 * k), h * 0.55 * k)
            sp.location.z = h * 0.55 * k * 0.8
        flak_vivo(fl, t, T[14][0] - 1.5)
        mirar(cam, Vector((14.0, 30.0, DECK + 1.6)), Vector((-10, -400, 70)), lente=50)
        return {}
    return {"actualizar": act}


def p15(sc, a, b):
    # "Pero el que pasa…": un avión sale entero de una nube de humo negro y sigue bajando
    pa, cam = armar_mar(sc)
    random.seed(15)
    mn = S.humo_mat("nube_flak", (0.04, 0.04, 0.04), densidad=0.16, escala=1.3)
    nube = [S.bocanada(sc, f"Nube{i}", (random.uniform(-25, 25), -260 + random.uniform(-20, 20), 230 + random.uniform(-15, 15)), random.uniform(16, 26), mn) for i in range(7)]
    av = zero_vuelo(sc)
    d0 = Vector((0, -300, 268)); d1 = Vector((10, -190, 170))

    def act(f):
        t = tf(f)
        u = clamp((t - T[15][0] - 0.2) / (T[15][1] - T[15][0]))
        p = d0.lerp(d1, u)
        av.location = p
        orientar(av, CAM_CUB - p)
        S.girar_helice(av, t * 45)
        for i, o in enumerate(nube):
            o.location.x += 0.02 * math.sin(t + i)
        mirar(cam, CAM_CUB, Vector((4, -230, 215)), lente=50)
        return {"avion": pantalla(sc, cam, p)}
    return {"actualizar": act}


def p16(sc, a, b):
    # "casi siempre pega.": el avión llena el cuadro sobre la cubierta; el post corta a blanco antes del choque
    pa, cam = armar_mar(sc)
    av = zero_vuelo(sc)
    humo = estela(sc, "EstelaF", 10)
    d0 = Vector((8, -150, 150)); d1 = Vector((5, 22, DECK + 9))

    def camino(t):
        u = clamp((t - T[16][0]) / (T[16][1] - T[16][0] - 0.1))
        return d0.lerp(d1, u ** 1.6)

    def act(f):
        t = tf(f)
        p = camino(t)
        av.location = p
        orientar(av, CAM_CUB - p)
        S.girar_helice(av, t * 45)
        estela_viva(humo, camino, t - 0.05, paso=0.06)
        mirar(cam, Vector((34.0, 50.0, DECK + 2.5)), p.lerp(Vector((8, 20, DECK + 6)), 0.35), lente=50)
        return {"avion": pantalla(sc, cam, p)}
    return {"actualizar": act}


def p17(sc, a, b):
    # "En Okinawa mueren más marineros": el portaaviones visto desde un destructor, con humo negro saliendo de la cubierta
    pa, cam = armar_mar(sc)
    random.seed(17)
    columna = []
    mcol = S.humo_mat("columna", (0.03, 0.03, 0.03), densidad=0.3, escala=1.1)
    for i in range(22):
        columna.append((S.bocanada(sc, f"Col{i}", (0, 0, 0), 5 + i * 0.9, mcol), i))

    def act(f):
        t = tf(f)
        for o, i in columna:
            h = (i * 5.5 + 2.2 * t) % 121           # cada bocanada sube y vuelve a nacer en la cubierta
            o.location = (2 + 0.18 * h + 0.8 * math.sin(t * 0.6 + i), 8 + 0.12 * h, DECK + 2 + h)
            k = 4 + 0.16 * h
            o.scale = (k, k, k * 0.9)
        bob = 0.6 * math.sin(t * 0.9)
        mirar(cam, Vector((300, -160, 12 + bob)), Vector((0, 10, 30 + 0.3 * bob)), lente=85)
        return {}
    return {"actualizar": act}


# ============================================================ E · el mapa
def armar_mapa(sc):
    M.tierra(sc)
    cam = E.camara(sc, (0, 0, 20), (0, 0, 0), lente=35, fstop=None)
    return cam


def meta_mapa(sc, cam):
    return {k: v for k, v in M.puntos(sc, cam).items()}


def p4(sc, a, b):
    # "Japón está perdiendo la guerra…": el Pacífico; las islas perdidas se apagan y EE.UU. se acerca (capas en el post)
    cam = armar_mapa(sc)

    def act(f):
        x = suave(lin(f, a, b - 1))
        M.mirar_latlon(cam, 18 + 8 * x, 138 - 2 * x, 9000 - 3000 * x, incl=8)
        return {"lugares": meta_mapa(sc, cam)}
    return {"actualizar": act}


def p18(sc, a, b):
    # "que soldados del ejército en tierra.": Okinawa de cerca (barras en el post)
    cam = armar_mapa(sc)

    def act(f):
        x = suave(lin(f, a, b - 1))
        M.mirar_latlon(cam, 26.6, 128.0, 1350 - 100 * x, incl=10)
        return {"lugares": meta_mapa(sc, cam)}
    return {"actualizar": act}


def p19(sc, a, b):
    # "Y a Estados Unidos todavía le falta invadir Japón.": de Okinawa hacia Kyushu (flechas en el post)
    cam = armar_mapa(sc)

    def act(f):
        x = suave(lin(f, a, b - 1))
        M.mirar_latlon(cam, 27.2 + 3.4 * x, 128.6 + 1.6 * x, 1250 + 550 * x, incl=12)
        return {"lugares": meta_mapa(sc, cam)}
    return {"actualizar": act}


def p22(sc, a, b):
    cam = armar_mapa(sc)

    def act(f):
        x = suave(lin(f, a, b - 1))
        M.mirar_latlon(cam, 26.8, 128.2, 1350 - 80 * x, incl=10)
        return {"lugares": meta_mapa(sc, cam)}
    return {"actualizar": act}


def p23(sc, a, b):
    cam = armar_mapa(sc)

    def act(f):
        x = suave(lin(f, a, b - 1))
        M.mirar_latlon(cam, 29.5 + 3.5 * x, 130.0 + 3.0 * x, 1700 + 800 * x, incl=10)
        return {"lugares": meta_mapa(sc, cam)}
    return {"actualizar": act}


def p24(sc, a, b):
    cam = armar_mapa(sc)

    def act(f):
        x = lin(f, a, b - 1)
        M.mirar_latlon(cam, 33.0, 133.5, 2400 + 300 * x, incl=8)
        return {"lugares": meta_mapa(sc, cam)}
    return {"actualizar": act}


def p25(sc, a, b):
    cam = armar_mapa(sc)

    def act(f):
        x = lin(f, a, b - 1)
        M.mirar_latlon(cam, 33.0, 133.5, 2700 + 150 * x, incl=8)
        return {"lugares": meta_mapa(sc, cam)}
    return {"actualizar": act}


# ===================================== piezas ======================================
FUN = {1: p1, 2: p2, 3: p3, 4: p4, 5: p5, 6: p6, 7: p7, 8: p8, 9: p9, 10: p10, 11: p11, 12: p12, 13: p13, 14: p14,
       15: p15, 16: p16, 17: p17, 18: p18, 19: p19, 20: p20, 21: p21, 22: p22, 23: p23, 24: p24, 25: p25, 26: p26, 27: p27}
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
