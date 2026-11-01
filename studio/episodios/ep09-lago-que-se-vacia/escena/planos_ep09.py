"""Planos del Ep. 9 (estilo realista): 3 escenas, 12 planos (storyboard.md v1).

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
ESCENA = {1: "E1", 2: "E1", 3: "E1", 4: "E3", 5: "E2", 6: "E2", 7: "E2", 8: "E2", 9: "E1", 10: "E2", 11: "E1", 12: "E1"}
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


def p1(sc, a, b):
    # CUADRO 0 · "Anoche, aquí había un lago.": el fondo vacío, témpanos varados, el muro de hielo atrás
    S = armar_valle(sc, L.NIVEL_VACIO)

    def act(f):
        fase_agua(S, f)
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
    t_fl = TW("flota", 7.0)

    def act(f):
        fase_agua(S, f)
        t = tf(f)
        x = lin(f, a, b - 1)
        cubo.location = c0 + Vector((0.004 * math.sin(t * 2.1), 0.003 * math.sin(t * 1.6), 0.0018 * math.sin(t * 3.3)))
        cubo.rotation_euler = (0.04 * math.sin(t * 2.7), 0.03 * math.sin(t * 2.2), 0.6 + 0.25 * t)
        ojo = g + Vector((0.16, 0.30, 0.31)) - Vector((0.03, 0.05, 0.02)) * x
        mira = g + Vector((0, 0, 0.255))
        mirar(cam, ojo, mira, lente=50, foco=mira)
        return {"cubo": pantalla(sc, cam, cubo.location), "vaso": pantalla(sc, cam, g + Vector((0, 0, 0.36)))}
    return {"actualizar": act}


# ---------------------------------------------------------------- E2: el corte
CAM_CORTE = (Vector((L.XC + 250, 45, 62)), Vector((L.XC, -18, -14)))


def armar_corte(sc, nivel):
    # en el corte el sol entra del noreste y más alto: rasante sobre la cara cortada (de frente quedaba plana y blanca)
    # y sin la sombra del glaciar que queda fuera del corte
    S = armar_valle(sc, nivel, sol_elev=20.0, sol_rot=35.0)
    C = L.Corte(sc, S)
    return S, C


def cam_corte(S, x=0.0, cerca=0.0, lente=30):
    p, m = CAM_CORTE
    p = p + Vector((-70 * cerca, -15 * cerca, -30 * cerca)) + Vector((-10, -6, -4)) * x
    mirar(S["cam"], p, m + Vector((0, 0, -6 * cerca)), lente=lente)


def meta_corte(sc, S, C, extra=None):
    d = {"pie": pantalla(sc, S["cam"], Vector((L.XC, -40, float(C.bed[C.hielo_y][-40]) + 4))),
         "tunel": pantalla(sc, S["cam"], Vector((L.XC, -60, float(C.bed[C.hielo_y][-60]) + 3))),
         "lago": pantalla(sc, S["cam"], Vector((L.XC, 60, -10)))}
    d.update(extra or {})
    return d


def p5(sc, a, b):
    # "Por eso, cuando el lago se llena, levanta el borde del glaciar.": el agua sube contra el hielo y el pie se despega
    S, C = armar_corte(sc, -8.0)
    t_ll, t_lv = TW("llena", 9.4), TW("levanta", 9.4)

    def act(f):
        t = tf(f)
        nivel = -8.0 + 8.0 * sale(lin(t, a / FPS, t_ll + 0.25))
        lift = 4.0 * suave(lin(t, t_lv, t_lv + 0.9))
        C.estado(nivel, lift=lift, fase=0.0)
        fase_agua(S, f)
        cam_corte(S, suave(lin(f, a, b - 1)))
        return meta_corte(sc, S, C, {"lift": round(lift, 2)})
    return {"actualizar": act}


def p6(sc, a, b):
    # "Y el agua se cuela por abajo.": una lengua de agua avanza bajo el hielo
    S, C = armar_corte(sc, 0.0)
    t0 = TW("agua", 12.9)

    def act(f):
        t = tf(f)
        len_ = -6.0 - 400.0 * sale(lin(t, t0 - 0.2, b / FPS - 0.2))
        C.estado(0.0, lift=4.0, lengua=len_, fase=-0.02 * f)
        fase_agua(S, f)
        cam_corte(S, 0.4 + 0.3 * suave(lin(f, a, b - 1)), cerca=0.35)
        return meta_corte(sc, S, C, {"lengua": pantalla(sc, S["cam"], Vector((L.XC, max(len_, -400), -30)))})
    return {"actualizar": act}


def p7(sc, a, b):
    # "Al pasar, derrite el hielo y abre un túnel cada vez más ancho.": el conducto crece de un hilo a un túnel
    S, C = armar_corte(sc, 0.0)
    t0 = TW("derrite", 15.0)

    def act(f):
        t = tf(f)
        r = 0.5 + 5.5 * suave(lin(t, t0, b / FPS - 0.15))
        C.estado(0.0, lift=4.0 - 2.5 * lin(t, t0, b / FPS), lengua=-420.0, radio=r, fase=-0.035 * f)
        fase_agua(S, f)
        cam_corte(S, 0.2 * suave(lin(f, a, b - 1)), cerca=0.25)
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
        cam_corte(S, -0.3 * suave(x), cerca=0.0)
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
    t0 = TW("hielo", 22.2)

    def act(f):
        t = tf(f)
        r = 7.5 * (1 - sale(lin(t, t0, b / FPS - 0.25)))
        C.estado(L.NIVEL_VACIO, lift=0.0, lengua=-420.0 if r > 0.3 else 0.0, radio=r, fase=-0.02 * f)
        fase_agua(S, f)
        cam_corte(S, 0.5 + 0.3 * suave(lin(f, a, b - 1)), cerca=0.3)
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


# ===================================== piezas ======================================
FUN = {1: p1, 2: p2, 3: p3, 4: p4, 5: p5, 6: p6, 7: p7, 8: p8, 9: p9, 10: p10, 11: p11, 12: p12}
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
