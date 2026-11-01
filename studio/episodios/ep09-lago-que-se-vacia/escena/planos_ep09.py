"""Planos del Ep. 9 (estilo realista): 3 escenas, 15 planos (storyboard.md v2, 45 s).

E1 valle — el lago (lleno, vaciándose o vacío) contra el glaciar: planos 1, 2, 3, 9, 11 y 12.
E2 corte — la represa de hielo abierta de costado: planos 5, 6, 7, 8 y 10.
E3 vaso  — un vaso con un cubo de hielo en una roca de la orilla: plano 4.

Cada pieza arma su escena y devuelve actualizar(f) (todo calculado por cuadro, sin keyframes) y su meta para el post.
"""
import math, os, sys
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../plantilla")))
import ep09 as E
import lago as L
import vistas as V
from ep09 import F, FR, T, lin, suave, sale, tramo, ruido, clamp, mirar, pantalla, oculto

FPS = 30
ESCENA = {1: "E1", 2: "E1", 3: "E1", 4: "E2", 5: "E2", 6: "E2", 7: "E2", 8: "E2", 9: "E1", 10: "E4", 11: "E4", 12: "E4", 13: "E2", 14: "E1", 15: "E1"}
DET = float(os.environ.get("DET", 1.0))
EXPO = -0.8


def TW(prefijo, desde=0.0):
    return E.t_palabra(prefijo, desde)


def tf(f):
    return (f - 1) / FPS


def armar_valle(sc, nivel, **kw):
    S = L.valle(sc, nivel=nivel, detalle=DET, **kw)
    S["cam"] = E.camara(sc, (0, 0, 0), (0, -1, 0), lente=30, fstop=None)
    sc.view_settings.exposure = EXPO
    return S


def fase_agua(S, f):
    """Las ondas del lago se mueven (nada quieto)."""
    m = bpy.data.materials.get("agua_lago")
    if m is None:
        return
    for n in m.node_tree.nodes:
        if n.type == "MAPPING":
            n.inputs["Location"].default_value = (0.004 * f, 0.011 * f, 0.0)


# ---------------------------------------------------------------- cámaras de E1
C0 = V.VISTAS["c0"]


def c0_pose(x=0.0):
    """x = 0: la cámara exacta del cuadro 0; x > 0 avanza hacia el témpano (dolly in)."""
    px, py, _, sobre = C0["pos"]
    z = V.z_suelo(px, py) + sobre
    p = Vector((px, py, z))
    m = Vector(C0["mira"])
    d = (m - p).normalized()
    return p + d * (2.2 * x), m + d * (2.2 * x)


def cuadro0_meta(sc, S):
    t = S["tempanos"][0]
    return {"tempano": pantalla(sc, S["cam"], t.matrix_world.translation + Vector((0, 0, t["alto"] * 0.4))),
            "muro": pantalla(sc, S["cam"], Vector((20, -4, 30)))}


def trozo_que_cae(sc, S):
    """Un trozo de hielo (~1,6 m) se suelta del borde del témpano del cuadro 0 y cae al barro (acción desde el cuadro 0;
    puerta 3: "no hay acción en curso en el primer segundo")."""
    t0 = S["tempanos"][0]
    tr = L.roca_hielo(sc, "TrozoCae", (1.6, 1.2, 1.0), 77, bpy.data.materials["hielo_tempano"])
    tope = t0.matrix_world.translation + Vector((t0.dimensions.x * 0.33, t0.dimensions.y * 0.38, t0.dimensions.z * 0.3))
    piso = V.z_suelo(tope.x, tope.y) + 0.35

    def pos(t):
        caida = max(0.0, t - 0.12)
        z = max(piso, tope.z - 0.5 * 9.81 * caida * caida)
        rot = min(1.0, caida / 0.75)
        tr.location = (tope.x + 0.6 * rot, tope.y + 0.4 * rot, z)
        tr.rotation_euler = (1.4 * rot, 0.5 * rot, 0.3)
    return pos


def p1(sc, a, b):
    # CUADRO 0 · "Anoche, aquí había un lago.": el fondo vacío, témpanos varados, el muro de hielo atrás
    S = armar_valle(sc, L.NIVEL_VACIO)
    cae = trozo_que_cae(sc, S)

    def act(f):
        fase_agua(S, f)
        cae(tf(f))
        p, m = c0_pose(sale(lin(f, a, b - 1)))
        mirar(S["cam"], p, m, lente=C0["lente"])
        return cuadro0_meta(sc, S)
    return {"actualizar": act}


def p2(sc, a, b):
    # "En la Patagonia chilena, un glaciar lo tapaba como una represa.": ANTES, el lago lleno contra el glaciar, desde arriba
    S = armar_valle(sc, L.NIVEL_LLENO)
    pa, pb = Vector((250, 1380, 245)), Vector((205, 1180, 210))

    def act(f):
        fase_agua(S, f)
        x = suave(lin(f, a, b - 1))
        mirar(S["cam"], pa.lerp(pb, x), Vector((-20, 40, 4)), lente=30)
        return {"glaciar": pantalla(sc, S["cam"], Vector((20, -40, 45))), "lago": pantalla(sc, S["cam"], Vector((30, 500, 0)))}
    return {"actualizar": act}


def p3(sc, a, b):
    # "¿Por dónde se fue el agua?": a ras del agua llena, avanzando hacia el pie del muro de hielo
    S = armar_valle(sc, L.NIVEL_LLENO)
    pa, pb = Vector((48, 330, 2.2)), Vector((40, 250, 1.6))

    def act(f):
        fase_agua(S, f)
        x = lin(f, a, b - 1)
        mirar(S["cam"], pa.lerp(pb, x), Vector((10, 0, 10)), lente=32)
        return {"pie": pantalla(sc, S["cam"], Vector((15, 0, 1)))}
    return {"actualizar": act}


def p4(sc, a, b):
    # "El hielo flota, como el de tu vaso.": un vaso con un cubo de hielo en una roca de la orilla, el glaciar atrás
    S = armar_valle(sc, L.NIVEL_LLENO)
    xo, zo = L.orilla(560.0, 1)
    g = Vector((xo + 1.5, 560.0, zo))
    VV = L.vaso(sc, tuple(g))
    cam = S["cam"]
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 3.2
    rel = E.luz_area(sc, "RellenoVaso", tuple(g + Vector((0.5, 0.9, 0.6))), tuple(g + Vector((0, 0, 0.25))), 6.0, tam=0.8)
    rel.visible_glossy = False
    cubo = VV["cubo"]
    c0 = cubo.location.copy()
    t_fl = TW("flota", a / FPS - 0.3)

    def act(f):
        fase_agua(S, f)
        t = tf(f)
        x = lin(f, a, b - 1)
        cubo.location = c0 + Vector((0.004 * math.sin(t * 2.1), 0.003 * math.sin(t * 1.6), 0.0018 * math.sin(t * 3.3)))
        cubo.rotation_euler = (0.04 * math.sin(t * 2.7), 0.03 * math.sin(t * 2.2), 0.6 + 0.25 * t)
        ojo = g + Vector((0.30, 0.40, 0.30)) - Vector((0.036, 0.048, 0.0)) * x
        mira = g + Vector((0, 0, 0.27))
        mirar(cam, ojo, mira, lente=42, foco=mira)
        return {"cubo": pantalla(sc, cam, cubo.location), "vaso": pantalla(sc, cam, g + Vector((0, 0, 0.36)))}
    return {"actualizar": act}


# ---------------------------------------------------------------- E2: el corte
CAMS_CORTE = {   # (posición, mira): el contacto hielo-roca queda sobre la franja de subtítulos (y ≈ 820–890)
    "lejos": (Vector((L.XC + 200, 30, 15)), Vector((L.XC, -5, -40))),
    "cerca": (Vector((L.XC + 110, 16, -15)), Vector((L.XC, 2, -40))),
}


def armar_corte(sc, nivel):
    # en el corte el sol entra del noreste y más alto: rasante sobre la cara cortada (de frente quedaba plana y blanca)
    # y sin la sombra del glaciar que queda fuera del corte
    S = armar_valle(sc, nivel, sol_elev=20.0, sol_rot=35.0, xmax=L.XC)
    C = L.Corte(sc, S)
    return S, C


def cam_corte(S, modo="lejos", x=0.0, lente=30):
    """modo = "lejos" | "cerca"; x = avance del dolly (0–1)."""
    p, m = CAMS_CORTE[modo]
    p = p + (m - p) * 0.06 * x
    mirar(S["cam"], p, m, lente=lente)


def meta_corte(sc, S, C, extra=None):
    d = {"pie": pantalla(sc, S["cam"], Vector(C.contacto(L.Y_FRENTE + 8)) + Vector((0, 0, 3))),
         "tunel": pantalla(sc, S["cam"], Vector(C.contacto(-12)) + Vector((0, 0, 2))),
         "lago": pantalla(sc, S["cam"], Vector((L.XC, 30, -12)))}
    d.update(extra or {})
    return d


def p5(sc, a, b):
    # "Por eso, cuando el lago se llena, levanta el borde del glaciar.": el agua sube contra el hielo y el pie se despega
    S, C = armar_corte(sc, -8.0)
    t_ll, t_lv = TW("llena", a / FPS - 0.3), TW("levanta", a / FPS - 0.3)

    def act(f):
        t = tf(f)
        nivel = -8.0 + 8.0 * sale(lin(t, a / FPS, t_ll + 0.25))
        lift = 4.0 * suave(lin(t, t_lv, t_lv + 0.9))
        C.estado(nivel, lift=lift, fase=0.0)
        fase_agua(S, f)
        if t < t_lv - 0.05:                     # puerta 3: en "levanta", corte seco a la cámara cercana (4 m de lejos no se ven)
            cam_corte(S, "lejos", suave(lin(t, a / FPS, t_lv)))
        else:
            cam_corte(S, "cerca", suave(lin(t, t_lv, b / FPS)))
        return meta_corte(sc, S, C, {"lift": round(lift, 2)})
    return {"actualizar": act}


def p6(sc, a, b):
    # "Y el agua se cuela por abajo.": una lengua de agua avanza bajo el hielo
    S, C = armar_corte(sc, 0.0)
    t0 = TW("agua", a / FPS - 0.3)

    def act(f):
        t = tf(f)
        len_ = L.Y_FRENTE + L.TOE - (L.TOE + 420.0) * sale(lin(t, t0 - 0.2, b / FPS - 0.2))
        C.estado(0.0, lift=4.0, lengua=len_, fase=-0.02 * f)
        fase_agua(S, f)
        cam_corte(S, "cerca", suave(lin(f, a, b - 1)))
        return meta_corte(sc, S, C, {"lengua": pantalla(sc, S["cam"], Vector(C.contacto(max(len_ * 0.06, -22))) + Vector((0, 0, 1)))})
    return {"actualizar": act}


def p7(sc, a, b):
    # "Al pasar, derrite el hielo y abre un túnel cada vez más ancho.": el conducto crece de un hilo a un túnel
    S, C = armar_corte(sc, 0.0)
    t0 = TW("derrite", a / FPS - 0.3)

    def act(f):
        t = tf(f)
        r = 0.5 + 5.5 * suave(lin(t, t0, b / FPS - 0.15))
        C.estado(0.0, lift=4.0 - 2.5 * lin(t, t0, b / FPS), lengua=-420.0, radio=r, fase=-0.035 * f)
        fase_agua(S, f)
        cam_corte(S, "cerca", 1.0 - 0.6 * suave(lin(f, a, b - 1)))
        return meta_corte(sc, S, C, {"radio": round(r, 2)})
    return {"actualizar": act}


def p8(sc, a, b):
    # "Así que en una sola noche,": el agua corre por el túnel y el lago baja (cámara rápida)
    S, C = armar_corte(sc, 0.0)

    def act(f):
        x = lin(f, a, b - 1)
        nivel = -14.0 * x
        C.estado(nivel, lift=1.5 * (1 - x), lengua=-420.0, radio=6.0 + 1.5 * x, fase=-0.07 * f)
        fase_agua(S, f)
        cam_corte(S, "lejos", -0.5 * suave(x))
        return meta_corte(sc, S, C)
    return {"actualizar": act}


def p9(sc, a, b):
    # "el lago entero se va por ahí.": desde arriba, el lago se vacía y los témpanos se posan en el barro (cámara rápida)
    S = armar_valle(sc, 0.0)
    pa, pb = Vector((330, 1150, 330)), Vector((300, 1050, 300))

    def act(f):
        x = lin(f, a, b - 1)
        nivel = -14.0 + (L.NIVEL_VACIO + 14.0) * sale(min(1.0, x * 1.25))
        S["agua"].location.z = nivel
        L.ubicar_tempanos(S["tempanos"], nivel)
        fase_agua(S, f)
        mirar(S["cam"], pa.lerp(pb, suave(x)), Vector((-10, 120, -20)), lente=28)
        return {"lago": pantalla(sc, S["cam"], Vector((20, 300, nivel)))}
    return {"actualizar": act}


def p10(sc, a, b):
    # "El hielo se cierra,": vacío el lago, el hielo baja y aprieta el túnel hasta cerrarlo
    S, C = armar_corte(sc, L.NIVEL_VACIO)
    t0 = TW("hielo", a / FPS - 0.3)

    def act(f):
        t = tf(f)
        r = 7.5 * (1 - sale(lin(t, t0, b / FPS - 0.25)))
        C.estado(L.NIVEL_VACIO, lift=0.0, lengua=-420.0 if r > 0.3 else 0.0, radio=r, fase=-0.02 * f)
        fase_agua(S, f)
        cam_corte(S, "cerca", suave(lin(f, a, b - 1)))
        return meta_corte(sc, S, C, {"radio": round(r, 2)})
    return {"actualizar": act}


def p11(sc, a, b):
    # "el lago se llena…": desde la ladera, el agua vuelve a subir y los témpanos vuelven a flotar (cámara rápida)
    S = armar_valle(sc, L.NIVEL_VACIO)
    pa, pb = Vector((250, 1380, 245)), Vector((236, 1320, 236))

    def act(f):
        x = lin(f, a, b - 1)
        nivel = L.NIVEL_VACIO * (1 - sale(x))
        S["agua"].location.z = nivel
        L.ubicar_tempanos(S["tempanos"], nivel)
        fase_agua(S, f)
        mirar(S["cam"], pa.lerp(pb, suave(x)), Vector((-20, 40, 4)), lente=30)
        return {"lago": pantalla(sc, S["cam"], Vector((30, 500, nivel)))}
    return {"actualizar": act}


def p12(sc, a, b):
    # "y otra vez…": el lago se vuelve a ir; la cámara baja con el agua y termina en la cámara exacta del cuadro 0 (loop)
    S = armar_valle(sc, 0.0)
    p_fin, m_fin = c0_pose(0.0)
    trozo_que_cae(sc, S)(0.0)                    # el trozo que cae en el plano 1 todavía está arriba (loop)

    def act(f):
        x = lin(f, a, b - 1)
        nivel = L.NIVEL_VACIO * sale(min(1.0, x * 1.15))
        S["agua"].location.z = nivel
        L.ubicar_tempanos(S["tempanos"], nivel)
        fase_agua(S, f)
        p = Vector((p_fin.x, p_fin.y, max(p_fin.z, nivel + 2.4)))
        mirar(S["cam"], p, m_fin + Vector((0, 0, p.z - p_fin.z)) * 0.6, lente=C0["lente"])
        return cuadro0_meta(sc, S)
    return {"actualizar": act}


# ---------------------------------------------------------------- v2 (45 s): el témpano en corte y el río de abajo
def p_flota(sc, a, b):
    # "El hielo flota, como el de tu vaso.": en el corte, un témpano flota en el lago con casi todo bajo el agua
    S, C = armar_corte(sc, 0.0)
    C.estado(0.0)
    tem = L.tempano_corte(sc)
    z0 = tem.location.z
    p0, m0 = Vector((L.XC + 175, 95, 6)), Vector((L.XC, 52, -12))

    def act(f):
        t = tf(f)
        tem.location.z = z0 + 0.35 * math.sin(t * 2.2)            # se mece en el agua
        fase_agua(S, f)
        x = suave(lin(f, a, b - 1))
        mirar(S["cam"], p0 + (m0 - p0) * 0.07 * x, m0, lente=30)
        return {"tempano": pantalla(sc, S["cam"], Vector((L.XC, 58, 2))), "linea": pantalla(sc, S["cam"], Vector((L.XC, 30, 0)))}
    return {"actualizar": act}


def armar_rio(sc):
    R = L.rio(sc, detalle=DET)
    R["cam"] = E.camara(sc, (0, 0, 0), (0, -1, 0), lente=26, fstop=None)
    sc.view_settings.exposure = EXPO
    return R


def fase_rio(f):
    m = bpy.data.materials.get("agua_rio")
    if m:
        for n in m.node_tree.nodes:
            if n.type == "MAPPING":
                n.inputs["Location"].default_value = (0.03 * f, 0.0, 0.0)


def flechas_rio(R, nivel, atras=0.0, f=0):
    """Flechas del río grande: río abajo (+x); con 'atras' (0–1) las de río arriba (x < 0) se dan vuelta."""
    for fl in R["flechas"]:
        fl.location.z = 20.0 + nivel + 0.6
        gira = atras if fl.location.x < 0 else 0.0
        fl.rotation_euler = (0, 0, math.pi * suave(gira))
        fl.location.x = fl.get("x0", fl.location.x)
        fl["x0"] = fl.get("x0", fl.location.x)
        fl.location.x = fl["x0"] + (12.0 if gira < 0.5 else -12.0) * math.sin(f * 0.12)


CAM_RIO = (Vector((-420, 620, 230)), Vector((180, -120, 12)))


def p_rio1(sc, a, b):
    # "Sale por el otro lado, y el río más caudaloso de Chile se triplica.": el agua café entra y el río se ensancha
    R = armar_rio(sc)
    t_tr = TW("triplica", a / FPS - 0.3)

    def act(f):
        t = tf(f)
        k = suave(lin(t, a / FPS + 0.3, t_tr + 0.4))
        nivel = L.RIO_NORMAL + (L.RIO_CRECIDA - L.RIO_NORMAL) * k
        L.estado_rio(R, nivel, 0.0 - 50 * k, -1000.0 + 3500.0 * sale(lin(t, a / FPS, a / FPS + 1.4)))
        flechas_rio(R, nivel, 0.0, f)
        fase_rio(f)
        p, m = CAM_RIO
        mirar(R["cam"], p + (m - p) * 0.08 * suave(lin(f, a, b - 1)), m, lente=26)
        return {"rio": pantalla(sc, R["cam"], Vector((150, 0, 20 + nivel))), "junta": pantalla(sc, R["cam"], Vector((0, -80, 20 + nivel)))}
    return {"actualizar": act}


def p_rio2(sc, a, b):
    # "Es tanta agua que frena al río y lo empuja hacia atrás.": las flechas de río arriba se dan vuelta y el café sube
    R = armar_rio(sc)
    t_at = TW("atrás", a / FPS - 0.3)
    p0, m0 = Vector((-650, 420, 190)), Vector((-120, -40, 14))

    def act(f):
        t = tf(f)
        k = suave(lin(t, TW("frena", a / FPS - 0.3) - 0.2, t_at + 0.3))
        L.estado_rio(R, L.RIO_CRECIDA, -60.0 - 700.0 * k, 2500.0)
        flechas_rio(R, L.RIO_CRECIDA, k, f)
        fase_rio(f)
        mirar(R["cam"], p0 + (m0 - p0) * 0.08 * suave(lin(f, a, b - 1)), m0, lente=26)
        return {"atras": pantalla(sc, R["cam"], Vector((-330, 0, 20 + L.RIO_CRECIDA)))}
    return {"actualizar": act}


def p_rio3(sc, a, b):
    # "Por eso hay una alarma que avisa a los que viven río abajo.": casas en la orilla, río abajo
    R = armar_rio(sc)
    p0, m0 = Vector((380, 60, 95)), Vector((660, -370, 22))

    def act(f):
        L.estado_rio(R, L.RIO_CRECIDA, -760.0, 2500.0)
        flechas_rio(R, L.RIO_CRECIDA, 1.0, f)
        fase_rio(f)
        x = suave(lin(f, a, b - 1))
        mirar(R["cam"], p0 + (m0 - p0) * 0.12 * x, m0, lente=35)
        return {"casas": pantalla(sc, R["cam"], R["casas"][0].matrix_world.translation + Vector((0, 0, 6)))}
    return {"actualizar": act}


# ===================================== piezas ======================================
FUN = {1: p1, 2: p2, 3: p3, 4: p_flota, 5: p5, 6: p6, 7: p7, 8: p8, 9: p9, 10: p_rio1, 11: p_rio2, 12: p_rio3, 13: p10, 14: p11, 15: p12}
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
