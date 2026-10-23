"""Planos de Rhein 01 (proceso v2): 4 escenas, 38 planos (storyboard.md). Los planos 30–36 y 38 son tomas reales de
Rhein (las mete el post); acá se renderizan los planos 3D.

E1 mar       — el bote, la grúa, los pollos, el niño, el mosasaurio y la micro: una sola escena (armar) y un estado por
               plano (act_e1), filmada con muchas cámaras.
E2 mecánica  — las piezas de la caña de cerca y en corte, sobre el mismo bote (pernos, cable trenzado, carrete con
               engranajes, freno y trinquete, arnés).
E3 radar     — la pantalla del radar (encendido, el punto que se acerca) y la explosión verde de la transición.

Cada pieza arma su escena y devuelve actualizar(f) (pose calculada, sin keyframes).
"""
import math, os, sys
import bpy
from mathutils import Vector, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../plantilla")))
import rhein01 as E
import mar as M
import pj_rhein as PJ
import nino as N
import utileria as U
import mecanica as K
from rhein01 import FR, F, lin, suave, sale, entra, rebote, resorte, tramo, ruido, clamp, mezcla

FPS = 30
Z_BOTE = 0.18                 # el bote flota más alto: la cubierta queda sobre el agua
Z_PISO = -0.19                # piso de la cubierta (en coordenadas del bote)
BASE_GRUA = (0.0, 1.25, Z_PISO + 0.02)
METRAJE = (30, 31, 32, 33, 34, 35, 38)


def TW(prefijo, desde=0.0):
    return E.t_palabra(prefijo, desde)


def t_de(f):
    return (f - 1) / FPS


# ================================================================== escena común
def armar(sc, quiero, mosa=True, nino=True, olas=0.34):
    """Arma el mar y lo que pida el plano. quiero ⊂ {grua, racimo, pila, asiento, consola, micro, carrete, gotas, huesos}."""
    coll = sc.collection
    S = {"quiero": quiero}
    sc.view_settings.exposure = -0.35
    S["sol"] = M.cielo(sc, sol_energia=4.0, sol_dir=(-0.35, 0.65, 0.68))
    S["mar"] = M.mar(coll, tam=60, repetir=3, res=7, olas=olas)
    M.nubes(coll)
    S["bote"] = bote = M.bote(coll)
    bote.location.z = Z_BOTE
    # el agua no entra al bote: el mar se corta con un volumen seco que sigue al bote
    seco = bpy.data.objects["Bote_seco"]
    bo = S["mar"].modifiers.new("Seco", "BOOLEAN")
    bo.operation = "DIFFERENCE"
    ids = [i.identifier for i in bo.bl_rna.properties["solver"].enum_items]
    for pref in ("FAST", "FLOAT"):
        if pref in ids:
            bo.solver = pref
            break
    bo.object = seco
    if "grua" in quiero or "racimo" in quiero or "carrete" in quiero:
        S["grua"], _ = M.grua(coll, base=BASE_GRUA, angulo=48, largo=6.2)
        S["grua"].parent = bote
        S["giro"] = bpy.data.objects["Grua_giro"]
        S["pluma"] = bpy.data.objects["Grua_pluma"]
        S["pernos"] = [o for o in bpy.data.objects if o.name.startswith("Grua_perno")]
    if "racimo" in quiero:
        S["racimo"], S["pollos"] = M.racimo(coll, (0, 0, 0), n=60, alto=2.0)
        S["cable"] = M.cable(coll, (0, 0, 0), (0, 0, 1), r=0.022)
    if "pila" in quiero:
        S["pila"], S["pila_pos"] = U.montana_pollos(coll, (0.0, 0.25, 0.0), n=200)
        for o in S["pila"]:
            o.parent = bote
            o.location.z += Z_PISO
    if "asiento" in quiero:
        S["asiento"], S["arnes"] = U.asiento(coll)
        S["asiento"].parent = bote
        S["asiento"].location = (0, -0.45, Z_PISO)
    if "consola" in quiero:
        S["consola"], S["pantalla"] = U.consola(coll)
        S["consola"].parent = bote
        S["consola"].location = (0.42, -1.15, Z_PISO)
        S["consola"].rotation_euler = (0, 0, math.radians(180))
    if "micro" in quiero:
        S["micro"] = U.micro(coll)
    if "carrete" in quiero:
        S["carrete"], S["car"] = K.carrete(coll)
        S["carrete"].parent = bote
        S["carrete"].location = (0.0, 0.40, Z_PISO + 0.55)
        S["carrete"].rotation_euler = (0, 0, 0)
    if "gotas" in quiero:
        S["gotas"] = U.gotas(coll, n=170)
    if "huesos" in quiero:
        S["huesos"] = U.huesos(coll)
    if mosa:
        S["mosa"] = PJ.mosasaurio(coll)
        S["ondula"] = PJ.Ondula(S["mosa"])
    if nino:
        S["pj"] = N.cargar(sc, x=0.25, y=-0.8, z=Z_PISO, rot_z=0.0)
        S["pj"]["rig"].parent = bote
    U.realismo_bote()
    fm = bpy.data.objects.get("FondoMar")
    if fm:
        fm.location.z = -6.5
        bpy.data.materials["FondoMar"].node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.05, 0.32, 0.42, 1)
    return S


def P_cubo(coll, nombre, escala, loc):
    import props as P
    c = P.prim("cube", nombre, coll, None)
    c.scale = escala
    c.location = loc
    c.display_type = "WIRE"
    c.hide_render = True
    return c


def bote_mece(S, t, extra_pitch=0.0, extra_y=0.0, extra_x=0.0):
    b = S["bote"]
    b.rotation_euler = (math.radians(1.6 * math.sin(t * 1.3) + extra_pitch), math.radians(2.2 * math.sin(t * 0.9 + 1.0)), 0)
    b.location = (extra_x, extra_y, Z_BOTE + 0.05 * math.sin(t * 1.3 + 0.5))


def punta_pluma(S):
    bpy.context.view_layer.update()
    return S["pluma"].matrix_world @ Vector((0, -6.25, -0.16))


def colgar_racimo(S, t, arriba=None, balanceo=6.0, largo=1.6):
    """El racimo cuelga del cable bajo la punta de la pluma (o en `arriba`), balanceándose."""
    tip = punta_pluma(S) if arriba is None else Vector(arriba)
    r = S["racimo"]
    r.location = tip - Vector((0, 0, largo))
    r.rotation_euler = (math.radians(balanceo * math.sin(t * 1.7)), math.radians(balanceo * 0.6 * math.sin(t * 1.1 + 0.7)), 0)
    sp = S["cable"].data.splines[0]
    sp.points[0].co = (*tip, 1)
    sp.points[-1].co = (*(r.location + Vector((0, 0, 0.05))), 1)


def luz_cara(sc, cam, objetivo, energia=60):
    """Relleno suave desde la cámara para los primeros planos del niño."""
    L = bpy.data.lights.new("RellenoCara", "AREA")
    L.energy, L.size, L.color = energia, 1.2, (1.0, 0.95, 0.9)
    o = bpy.data.objects.new("RellenoCara", L)
    sc.collection.objects.link(o)
    o.location = cam.location + (cam.location - Vector(objetivo)).normalized() * 0.4 + Vector((0.3, 0, 0.4))
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = (Vector(objetivo) - o.location).to_track_quat("-Z", "Y")
    return o


def cara_mundo(S):
    bpy.context.view_layer.update()
    rig = S["pj"]["rig"]
    return rig.matrix_world @ S["pj"]["pb"]["mixamorig:Head"].head + Vector((0, 0, 0.06))


def mosa_en(S, loc, rot_z=0.0, cabeceo=0.0, boca=0.0, t=0.0, amp=0.35):
    m = S["mosa"]
    m.location = loc
    m.rotation_euler = (math.radians(cabeceo), 0, math.radians(rot_z))
    bpy.data.objects["Mosa_mandibula"].rotation_euler = (math.radians(34 * boca), 0, 0)
    S["ondula"].aplicar(t, amp=amp)


def lejos(ob):
    """Saca un objeto (y sus hijos) del render."""
    U.ocultar(ob, True)


# ================================================================== E1 · planos
def _e1(sc, a, b, k):
    Q = {1: {"grua", "racimo"}, 2: {"pila"}, 3: {"racimo"}, 4: set(), 5: {"micro"}, 6: {"grua"}, 8: {"grua", "gotas"},
         10: {"grua", "racimo"}, 14: {"grua", "racimo"}, 15: {"asiento", "grua"}, 17: {"asiento"}, 19: {"grua", "racimo"},
         20: {"asiento", "consola"}, 22: {"asiento"}, 23: {"grua", "racimo"}, 24: {"asiento", "grua", "racimo"},
         25: {"grua", "racimo", "gotas"}, 26: {"asiento", "grua", "gotas"}, 27: {"asiento", "huesos"}, 28: {"asiento"},
         37: {"asiento"}}[k]
    con_nino = k not in (1, 3, 4, 5, 19, 23, 25)
    con_mosa = k in (1, 4, 5, 19, 23, 25)
    S = armar(sc, Q, mosa=con_mosa, nino=con_nino)
    cam = E.camara(sc, lens=30)
    pj = S.get("pj")
    if pj and k in (15, 17, 20, 22, 24, 26, 27, 28, 37):        # sentado en el asiento de montaña rusa
        pj["rig"].location = (0, -0.44, Z_PISO - 0.31)
        pj["rig"].rotation_euler = (0, 0, 0)
    huesos_fin = k in (28, 37)
    if huesos_fin:          # un hueso quedó sobre el gorro
        h = U.huesos(sc.collection, n=1, semilla=2)[0]
        h.parent = pj["gorro"]
        h.location = (0.0, 0.02, 0.10)
        h.rotation_euler = (0.2, 0.1, 0.9)
    if k in (19, 23):
        U.niebla(sc.collection, densidad=0.025)
        S["mar"].visible_shadow = False
        if bpy.data.objects.get("FondoMar"):
            bpy.data.objects["FondoMar"].hide_render = True
    if k == 3:
        E.area(sc, "RellenoPollos", (2.5, -3.5, 1.0), 900, 3.0, (1.0, 0.92, 0.8), (0, -0.2, 1.4))
    flecha_roja = None
    if k == 14:
        flecha_roja = U.flecha(sc.collection, "TiraAgua", (1.0, 0.12, 0.05), largo=1.2, grosor=0.035)
    fill = None
    if pj and k in (2, 6, 8, 10, 14, 15, 17, 20, 22, 24, 26, 27, 28, 37):
        fill = True
    mojado = k in (27, 28, 37)
    if mojado and "Impermeable" in bpy.data.materials:
        bp = bpy.data.materials["Impermeable"].node_tree.nodes["Principled BSDF"]
        bp.inputs["Roughness"].default_value = 0.12
        bp.inputs["Coat Weight"].default_value = 1.0

    def act(f):
        t = t_de(f)
        u = lin(f, a, b)
        tl = (f - a) / FPS
        bote_mece(S, t)
        info = {}
        if k == 1:      # CUADRO 0: racimo sobre el mar, la sombra pasa por debajo
            colgar_racimo(S, t)
            tip = punta_pluma(S)
            mosa_en(S, (tip.x + 10 - 20 * u, tip.y - 0.5, -2.6), rot_z=-90, t=t, amp=0.4)
            E.empujar(cam, f, a, b, tip + Vector((4.2, 3.6, -0.6)), tip + Vector((0, -0.6, -3.4)), cuanto=0.08, lens=24)
        elif k == 2:    # la montaña de 200 pollos y el niño orgulloso
            N.pose(pj, f, expr={"orgullo": 1}, brazoL=N.brazo("arriba", 0.7), brazoR=N.brazo("jarra"), cabeza=(0, 0, 8),
                   parpadeo=N.parpadeo(f))
            pj["rig"].location = (0.55, -0.55, Z_PISO)
            pj["rig"].rotation_euler = (0, 0, math.radians(-20))
            E.empujar(cam, f, a, b, (1.25, -3.1, 1.75), (0.25, -0.1, 0.45), cuanto=0.07, lens=32)
        elif k == 3:    # los pollos vuelan a la cuerda y forman el racimo
            centro = Vector((0, -0.2, 2.35))
            r = S["racimo"]
            r.location = centro
            r.rotation_euler = (0, 0, 0)
            sp = S["cable"].data.splines[0]
            sp.points[0].co = (*(centro + Vector((0, 0, 3))), 1)
            sp.points[-1].co = (*(centro + Vector((0, 0, 0.05))), 1)
            n = len(S["pollos"])
            origen = Vector((0.0, 0.25, 0.4))
            for i, p in enumerate(S["pollos"]):
                if "dest" not in p:
                    p["dest"] = tuple(p.location)
                ti = 0.25 + 0.95 * i / n                    # cada pollo llega a su tiempo
                x = clamp((tl - ti + 0.35) / 0.35)
                dest = Vector(p["dest"])
                o_l = origen - centro
                pos = o_l.lerp(dest, sale(x)) + Vector((0, 0, 1.1 * math.sin(math.pi * x)))
                p.location = pos
                p.hide_render = x <= 0 and i > n * 0.35
                for c in p.children:
                    c.hide_render = p.hide_render
            E.mirar(cam, centro + Vector((1.7 - 0.25 * u, -2.0, -1.0 + 0.4 * u)), centro + Vector((0, 0, -1.2)), lens=38)
        elif k == 4:    # cenital: el bote chico y la silueta enorme
            mosa_en(S, (1.4, 6 - 12 * u, -1.25), rot_z=0, t=t, amp=0.45)
            q = math.radians(-12 + 10 * u)
            E.mirar(cam, (math.sin(q) * 2, -0.5, 30), (0.0, -0.5, 0), lens=40, giro=-10 + 25 * u)
        elif k == 5:    # la micro flotando al lado del lomo
            S["micro"].location = (1.6, -1.0, -0.45)
            S["micro"].rotation_euler = (math.radians(1.5 * math.sin(t)), math.radians(2 * math.sin(t * 0.7)), 0)
            mosa_en(S, (6.4, -0.6 + 0.2 * u, -0.12), rot_z=0, t=t, amp=0.15)
            lejos(S["bote"])
            S["bote"].location.x = 200                 # el corte seco del mar se va con el bote
            S["mar"].modifiers["Seco"].show_render = False
            E.empujar(cam, f, a, b, (1.3, -10.5, 20.5), (4.0, -0.8, 0.3), cuanto=0.08, lens=34)
            bpy.context.view_layer.update()
            info["regla"] = [E.pantalla(sc, cam, (-0.35, -7.0, 2.9)), E.pantalla(sc, cam, (-0.35, 5.0, 2.9))]
        elif k == 6:    # la pluma baja del cielo; el niño hace señas
            S["giro"].rotation_euler = (math.radians(-48 - 40 * (1 - sale(u))), 0, 0)
            N.pose(pj, f, expr={"concentrado": 1}, brazoR=N.brazo("senal"), brazoL=N.brazo("arriba", 0.5 + 0.3 * math.sin(t * 9)),
                   cabeza=(-22, 0, 0), parpadeo=N.parpadeo(f))
            pj["rig"].location = (0.2, -1.25, Z_PISO)
            pj["rig"].rotation_euler = (0, 0, math.radians(180))
            E.empujar(cam, f, a, b, (1.6, -3.4, 0.45), (0.0, 0.3, 2.3), cuanto=0.05, lens=24)
        elif k == 8:    # la popa se hunde con el peso de la grúa
            x = rebote(lin(f, a, a + 8))
            bote_mece(S, t, extra_pitch=-5.0 * x)
            U.mover_gotas(S["gotas"], tl - 0.08, (0.0, 1.9, -0.05), escala=0.45)
            N.pose(pj, f, expr={"susto": 1}, brazoL=N.brazo("arriba", 0.6), brazoR=N.brazo("arriba", 0.6),
                   torso=(-6 * math.sin(tl * 18) * (1 - u), 0, 8 * math.sin(tl * 14) * (1 - u)), parpadeo=0)
            pj["rig"].location = (0.25, -0.6, Z_PISO)
            pj["rig"].rotation_euler = (0, 0, math.radians(200))
            E.mirar(cam, (3.6, 2.6, 0.55), (0, 0.6, 0.65), lens=30)
        elif k == 10:   # el cable se tensa y levanta el racimo de la cubierta
            tip = punta_pluma(S)
            sube = sale(lin(f, a + 3, b))
            largo = 1.6 + 3.2 * (1 - sube)
            colgar_racimo(S, t, balanceo=10 * sube, largo=largo)
            N.pose(pj, f, expr={"sonrisa": 1}, brazoL=N.brazo("arriba", 0.8), cabeza=(-30, 0, 0), parpadeo=N.parpadeo(f))
            pj["rig"].location = (0.35, -0.3, Z_PISO)
            pj["rig"].rotation_euler = (0, 0, math.radians(160))
            E.mirar(cam, (1.4, 0.9, 0.5), tip + Vector((0, 0.5, -2.6)), lens=22)
        elif k == 14:   # tirón: el freno aguanta y el niño se va de poto
            x = lin(f, a + 3, a + 8)
            tiron = math.sin(math.pi * x) * 0.35
            bote_mece(S, t, extra_y=-tiron, extra_pitch=3 * math.sin(math.pi * x))
            colgar_racimo(S, t, balanceo=14)
            tip = punta_pluma(S)                       # la flecha roja sale del agua y tira del cable
            r0 = S["racimo"].location
            flecha_roja.location = (r0.x, r0.y - 0.6, -0.4 + 0.6 * sale(lin(f, a, a + 6)))
            flecha_roja.rotation_euler = (0, math.radians(90), 0)
            flecha_roja.scale = (1, 1, 1)
            caida = sale(lin(f, a + 8, a + 16))
            N.pose(pj, f, expr={"susto": 1}, brazoL=N.brazo("arriba", caida), brazoR=N.brazo("arriba", caida), sentado=caida,
                   parpadeo=0)
            pj["rig"].location = (0.2, -0.75 + 0.15 * caida, Z_PISO - 0.56 * caida)
            pj["rig"].rotation_euler = (0, 0, math.radians(100))
            E.mirar(cam, (3.4, -0.9, 0.95), (0.1, -0.7, 0.35), lens=32)
        elif k == 15:   # el asiento de montaña rusa en la cubierta
            S["arnes"].rotation_euler = (math.radians(-100 + 30 * u), 0, 0)
            N.pose(pj, f, expr={"picaro": 1}, sentado=1.0, brazoL=N.brazo("agarra", 0.3), brazoR=N.brazo("agarra", 0.3),
                   parpadeo=N.parpadeo(f))
            E.empujar(cam, f, a, b, (0.55, -2.9, 0.95), (0, -0.5, 0.65), cuanto=0.09, lens=34)
        elif k == 17:   # pulgar arriba trabado en el asiento
            S["arnes"].rotation_euler = (0, 0, 0)
            x = sale(lin(f, a, a + 7))
            N.pose(pj, f, expr={"sonrisa": 1}, sentado=1.0, brazoL=N.brazo("pulgar", x), brazoR=N.brazo("agarra", 0.4),
                   cabeza=(0, 0, 8), parpadeo=N.parpadeo(f))
            cara = cara_mundo(S)
            E.empujar(cam, f, a, b, cara + Vector((-0.45, -1.25, 0.05)), cara + Vector((0, 0, -0.08)), cuanto=0.06, lens=50)
        elif k == 19:   # bajo el agua: el mosasaurio sube desde lo oscuro
            colgar_racimo(S, t, balanceo=5)
            mosa_en(S, (0.5, -3.0, -11 + 5 * sale(u)), rot_z=150, cabeceo=-50, t=t, amp=0.4)
            E.mirar(cam, (6.5, -8.0, -4.2), (0.0, -2.0, -1.0), lens=24)
        elif k == 20:   # silba mirando al otro lado
            S["arnes"].rotation_euler = (0, 0, 0)
            g = 22 * math.sin(tl * 3.4)
            N.pose(pj, f, expr={"concentrado": 0.4}, sentado=1.0, brazoL=N.brazo("agarra", 0.4), brazoR=N.brazo("agarra", 0.4),
                   cabeza=(-4, g, 0), parpadeo=N.parpadeo(f, fase=20))
            if "mouth-pursing" in pj["keys"]:
                pj["keys"]["mouth-pursing"].value = 0.9
            cara = cara_mundo(S)
            E.empujar(cam, f, a, b, cara + Vector((0.35, -1.2, 0.0)), cara + Vector((0, 0, -0.08)), cuanto=0.05, lens=52)
        elif k == 22:   # se le abren los ojos
            S["arnes"].rotation_euler = (0, 0, 0)
            x = sale(lin(f, a + 2, a + 10))
            N.pose(pj, f, expr={"susto": x}, sentado=1.0, brazoL=N.brazo("agarra", 0.5), brazoR=N.brazo("agarra", 0.5),
                   hombros=x, parpadeo=0)
            cara = cara_mundo(S)
            E.empujar(cam, f, a, b, cara + Vector((0.0, -1.1, 0.02)), cara + Vector((0, 0, -0.06)), cuanto=0.22, lens=55, curva=sale)
        elif k == 23:   # bajo el agua: la boca se abre bajo los pollos
            colgar_racimo(S, t, balanceo=5)
            tip = punta_pluma(S)
            mosa_en(S, (tip.x, tip.y - 3.3, -4.7), rot_z=180, cabeceo=-38, boca=sale(u), t=t, amp=0.2)
            E.mirar(cam, (tip.x + 3.6, tip.y - 2.2, -2.6), (tip.x, tip.y - 0.4, -1.6), lens=26)
        elif k == 24:   # se prepara: aprieta los dientes
            S["arnes"].rotation_euler = (0, 0, 0)
            colgar_racimo(S, t, balanceo=3)
            N.pose(pj, f, expr={"asco": 0.6, "concentrado": 0.6}, sentado=1.0, brazoL=N.brazo("agarra", 0.7),
                   brazoR=N.brazo("agarra", 0.7), hombros=0.8, parpadeo=0.8)
            E.empujar(cam, f, a, b, (0.35, -2.2, 1.05), (0, -0.5, 0.85), cuanto=0.08, lens=40)
        elif k == 25:   # sale del agua y se traga el racimo
            tip = punta_pluma(S)
            x = lin(f, a, b)
            z = -2.2 + 9.0 * sale(x) - 6 * max(0, x - 0.6) ** 2
            mosa_en(S, (tip.x, tip.y + 0.8, z), rot_z=180, cabeceo=-72 + 20 * x, boca=1 - sale(lin(f, a + 10, a + 16)), t=t, amp=0.3)
            comido = f >= a + 14
            colgar_racimo(S, t, balanceo=4)
            U.ocultar(S["racimo"], comido)
            U.mover_gotas(S["gotas"], tl - 0.15, (tip.x, tip.y, 0.0), escala=1.0)
            E.mirar(cam, (tip.x + 8.5, tip.y - 8.5, 0.9), (tip.x, tip.y, 1.6), lens=22)
        elif k == 26:   # remolcado a toda velocidad
            S["arnes"].rotation_euler = (0, 0, 0)
            vel = 7.0
            y = -vel * tl
            bote_mece(S, t * 3, extra_y=y, extra_pitch=-6 + 3 * math.sin(t * 9))
            S["giro"].rotation_euler = (math.radians(-38), 0, 0)
            U.mover_gotas(S["gotas"], (tl % 0.9), (0.0, y - 1.9, 0.1), escala=0.35)
            N.pose(pj, f, expr={"grito": 1}, sentado=1.0, brazoL=N.brazo("arriba"), brazoR=N.brazo("arriba"),
                   cabeza=(10 + 4 * math.sin(t * 20), 0, 0), parpadeo=0)
            E.mirar(cam, (5.5, y + 2.2, 2.0), (0.0, y - 0.6, 0.7), lens=26)
        elif k == 27:   # lluvia de huesos
            S["arnes"].rotation_euler = (0, 0, 0)
            U.mover_huesos(S["huesos"], tl, (0.0, -0.47, Z_BOTE + Z_PISO + 0.6))
            N.pose(pj, f, expr={"asco": 0.5, "susto": 0.4}, sentado=1.0, brazoL=N.brazo("agarra", 0.4), brazoR=N.brazo("agarra", 0.4),
                   hombros=0.6, parpadeo=N.parpadeo(f))
            E.empujar(cam, f, a, b, (0.35, -2.4, 1.15), (0, -0.5, 0.9), cuanto=0.06, lens=36)
        elif k in (28, 37):   # mojado con el hueso en el gorro: "ups" / encoge los hombros
            S["arnes"].rotation_euler = (0, 0, 0)
            x = sale(lin(f, a + 4, a + 12))
            expr = {"picaro": 1.0} if k == 28 else {"sonrisa": 1.0}
            N.pose(pj, f, expr=expr, sentado=1.0, brazoL=N.brazo("agarra", 0.4), brazoR=N.brazo("agarra", 0.4),
                   hombros=x if k == 37 else 0.0, cabeza=(0, 0, 10 * x if k == 37 else -6), parpadeo=N.parpadeo(f, fase=60))
            cara = cara_mundo(S)
            E.empujar(cam, f, a, b, cara + Vector((-0.2, -1.2, 0.03)), cara + Vector((0, 0, -0.06)), cuanto=0.06, lens=50)
        M.olas_t(S["mar"], t)
        bpy.context.view_layer.update()
        if S.get("fill") is None and fill:
            S["fill"] = luz_cara(sc, cam, cara_mundo(S))
        return info

    return {"actualizar": act}


# ================================================================== E2 · mecánica
def _e2(sc, a, b, k):
    Q = {7: {"grua"}, 9: set(), 11: {"grua", "carrete"}, 12: {"grua", "carrete"}, 13: {"grua", "carrete"}, 16: {"asiento"}}[k]
    S = armar(sc, Q, mosa=False, nino=(k == 16), olas=0.3)
    cam = E.camara(sc, lens=50, fstop=2.8)
    flechas = []
    if k == 7:
        for i, pb in enumerate(S["pernos"]):
            fl = U.flecha(sc.collection, f"GiroPerno{i}", (0.1, 1.0, 0.25), curva=True, radio=0.075, arco=260, grosor=0.007)
            flechas.append((fl, pb))
        E.area(sc, "KeyPernos", (0.55, 0.35, 0.95), 140, 0.8, (1.0, 0.93, 0.82), (0.0, 1.0, 0.1))
    if k == 9:
        alma, hilos, info_t = K.cable_trenzado(sc.collection)
        raiz = bpy.data.objects.new("TrenzaRaiz", None)
        sc.collection.objects.link(raiz)
        for o in [alma] + hilos:
            o.parent = raiz
        raiz.location = (-0.8, -2.6, 2.8)
        raiz.rotation_euler = (0, math.radians(-25), math.radians(15))
        # el acero refleja el cielo y se veía como tubos azules: luces cálidas que den brillos de metal
        bpy.data.materials["HiloAcero"].node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.85
        E.area(sc, "KeyTrenza", (-0.3, -3.3, 3.8), 260, 0.6, (1.0, 0.86, 0.66), (-0.1, -2.41, 3.1))
        E.area(sc, "RimTrenza", (0.4, -1.5, 3.6), 160, 0.4, (0.75, 0.88, 1.0), (-0.1, -2.41, 3.1))
    if k in (11, 12, 13):
        verde = U.flecha(sc.collection, "GiroEngranaje", (0.1, 1.0, 0.25), curva=True, radio=0.36, arco=240, grosor=0.012)
        rojo1 = U.flecha(sc.collection, "Pinza1", (1.0, 0.1, 0.05), largo=0.14, grosor=0.012)
        rojo2 = U.flecha(sc.collection, "Pinza2", (1.0, 0.1, 0.05), largo=0.14, grosor=0.012)
        tira = U.flecha(sc.collection, "Tira", (1.0, 0.1, 0.05), largo=0.45, grosor=0.016)
        for o in (verde, rojo1, rojo2, tira):
            o.parent = S["carrete"]
        verde.location = (0.33, 0, 0)
        verde.rotation_euler = (0, math.radians(90), 0)
        rojo1.location = (-0.27 - 0.22, 0, 0.215)
        rojo2.location = (-0.27 + 0.22, 0, 0.215)
        rojo2.rotation_euler = (0, 0, math.radians(180))
        tira.location = (0, -0.25, 0.20)
        tira.rotation_euler = (0, 0, math.radians(-90))
        chispas = U.gotas(sc.collection, n=40, semilla=12, nombre="Chispa")
        m_ch = bpy.data.materials.new("Chispa")
        m_ch.use_nodes = True
        bch = m_ch.node_tree.nodes["Principled BSDF"]
        bch.inputs["Emission Color"].default_value = (1.0, 0.55, 0.1, 1)
        bch.inputs["Emission Strength"].default_value = 12.0
        bch.inputs["Base Color"].default_value = (1.0, 0.45, 0.08, 1)
        for c in chispas:
            c.data = chispas[0].data
        chispas[0].data.materials.clear()
        chispas[0].data.materials.append(m_ch)
    if k == 16:
        pj = S["pj"]
        pj["rig"].location = (0, -0.44, Z_PISO - 0.31)

    def act(f):
        t = t_de(f)
        u = lin(f, a, b)
        tl = (f - a) / FPS
        bote_mece(S, t)
        if k == 7:      # los pernos bajan girando y aprietan
            for i, (fl, pb) in enumerate(flechas):
                x = sale(lin(f, a + 2 + 3 * i % 30, a + 9 + 3 * i % 30))
                if "z0" not in pb:
                    pb["z0"] = pb.location.z
                pb.location.z = pb["z0"] + 0.10 * (1 - x)
                pb.rotation_euler = (0, 0, 14 * x)
                bpy.context.view_layer.update()
                fl.location = pb.matrix_world.translation + Vector((0, 0, 0.05))
                fl.rotation_euler = (0, 0, 6 * tl)
                U.ocultar(fl, x >= 1.0 or x <= 0.0)
            bpy.context.view_layer.update()
            base = S["bote"].matrix_world @ Vector(BASE_GRUA)
            E.empujar(cam, f, a, b, base + Vector((0.35, -0.90, 0.74)), base + Vector((0.08, -0.27, 0.08)), cuanto=0.12, lens=40)
        elif k == 9:    # el cable se trenza
            K.pose_trenzado(hilos, info_t, giro=3.0 * tl, cierre=0.05 + 0.9 * u)
            bpy.context.view_layer.update()
            c = raiz.matrix_world @ Vector((0.4 + 0.8 * u, 0, 0))
            E.mirar(cam, c + Vector((0.05, -0.55, 0.12)), c, lens=55, foco=c)
        elif k in (11, 12, 13):
            car = S["car"]
            giro = 2.2 * t
            # los engranajes giran sobre su propio eje (Z local del cilindro, girado 90° en Y): orden ZYX
            for nm, w in (("g1", 1.0), ("tambor", 1.0), ("trinquete", 1.0), ("disco", 1.0), ("g2", -36 / 16)):
                o = car[nm]
                o.rotation_mode = "ZYX"
                o.rotation_euler = (0, math.radians(90), giro * w)
            K.corte(sale(lin(f, a, a + 12)) if k == 11 else 1.0)
            U.ocultar(verde, k != 11)
            verde.rotation_mode = "ZYX"
            verde.rotation_euler = (0, math.radians(90), giro)
            for o in (rojo1, rojo2):
                U.ocultar(o, k != 12)
            U.ocultar(tira, k != 13)
            if k == 12:
                x = sale(lin(f, a + 4, a + 8))
                car["pastillas"][0].location.x = -0.27 - 0.045 - 0.02 * (1 - x)
                car["pastillas"][1].location.x = -0.27 + 0.045 + 0.02 * (1 - x)
                rojo1.location.x = -0.27 - 0.22 + 0.06 * x
                rojo2.location.x = -0.27 + 0.22 - 0.06 * x
                bpy.context.view_layer.update()
                pc = S["carrete"].matrix_world @ Vector((-0.27, 0.0, 0.215))
                U.mover_gotas(chispas, (tl - 0.25) % 0.6, pc, escala=0.06)
                for c in chispas:
                    c.scale = (c.scale.x * 0.35, c.scale.y * 0.35, c.scale.z * 0.9)
            else:
                for c in chispas:
                    c.hide_render = True
            if k == 13:     # el pestillo cae diente por diente
                paso = int(tl / 0.2)
                fr = (tl % 0.2) / 0.2
                car["trinquete"].rotation_euler = (0, math.radians(90), math.radians(20) * (paso + sale(min(1, fr * 2.5))))
                car["pestillo"].rotation_euler = (math.radians(-18 * (1 - abs(1 - 2 * fr))), 0, 0)
                tira.scale = (1 + 0.15 * math.sin(tl * 30), 1, 1)
            bpy.context.view_layer.update()
            M_c = S["carrete"].matrix_world
            if k == 11:
                E.empujar(cam, f, a, b, M_c @ Vector((0.6, -1.2, 1.25)), M_c @ Vector((0.05, 0, 0.05)), cuanto=0.14, lens=38)
            elif k == 12:
                E.empujar(cam, f, a, b, M_c @ Vector((-0.9, -0.75, 0.55)), M_c @ Vector((-0.27, 0, 0.18)), cuanto=0.10, lens=48)
            else:
                E.empujar(cam, f, a, b, M_c @ Vector((-0.35, -0.95, 0.42)), M_c @ Vector((-0.12, -0.05, 0.22)), cuanto=0.08, lens=50)
        elif k == 16:   # el arnés baja y traba diente por diente
            pasos = [0.15, 0.45, 0.75]
            ang = -100
            for i, ts in enumerate(pasos):
                ang += 33.3 * sale(clamp((tl - ts) / 0.12))
            S["arnes"].rotation_euler = (math.radians(min(0, ang)), 0, 0)
            N.pose(S["pj"], f, expr={"susto": 0.5}, sentado=1.0, brazoL=N.brazo("agarra", 0.3), brazoR=N.brazo("agarra", 0.3),
                   parpadeo=0)
            bpy.context.view_layer.update()
            M_a = S["asiento"].matrix_world
            E.empujar(cam, f, a, b, M_a @ Vector((1.15, -0.55, 1.05)), M_a @ Vector((0.25, 0.02, 0.85)), cuanto=0.08, lens=40)
        M.olas_t(S["mar"], t)
        bpy.context.view_layer.update()
        return {}

    return {"actualizar": act}


# ================================================================== E3 · radar
def _e3(sc, a, b, k):
    S = armar(sc, {"consola"}, mosa=False, nino=False, olas=0.3)
    cam = E.camara(sc, lens=50, fstop=2.0)
    esfera = None
    if k == 29:
        S["mochila"], S["m_luz"], S["luz_m"] = U.mochila(sc.collection)
        S["mochila"].parent = S["bote"]
        S["mochila"].location = (-0.35, -0.95, Z_PISO)
        S["mochila"].rotation_euler = (0, 0, math.radians(200))
    if k == 29:
        import props as P
        m = bpy.data.materials.new("Energia")
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = (0.2, 1.0, 0.4, 1)
        em.name = "E"
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        lw = nt.nodes.new("ShaderNodeLayerWeight")
        lw.inputs["Blend"].default_value = 0.35
        mx = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(lw.outputs["Facing"], mx.inputs["Fac"])
        nt.links.new(em.outputs[0], mx.inputs[1])
        nt.links.new(tr.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs["Surface"])
        esfera = P.prim("ico", "Energia", sc.collection, m, sub=4, r=1.0)
        esfera.visible_shadow = False

    def act(f):
        t = t_de(f)
        u = lin(f, a, b)
        tl = (f - a) / FPS
        bote_mece(S, t)
        bpy.context.view_layer.update()
        pant = S["pantalla"]
        P0 = pant.matrix_world.translation
        normal = (pant.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()     # la cara de la pantalla
        cen = S["consola"].matrix_world.translation
        if normal.dot(P0 - cen) < 0:
            normal = -normal
        barrido = 2 * math.pi * (tl / 1.2)
        if k == 18:     # se enciende y barre
            U.radar_estado(barrido, brillo=sale(lin(f, a, a + 8)))
            E.empujar(cam, f, a, b, P0 + normal * 0.75 + Vector((0.12, 0, 0.18)), P0, cuanto=0.12, lens=50)
        elif k == 21:   # el punto entra y se acerca al centro
            d = 0.13 * (1 - sale(u))
            U.radar_estado(barrido * 1.6, punto=(d * 0.8, d * 0.6), tam=0.012 + 0.008 * u, brillo=1.0)
            E.empujar(cam, f, a, b, P0 + normal * 0.55 + Vector((0.05, 0, 0.08)), P0, cuanto=0.15, lens=55)
        elif k == 29:   # la mochila brilla en verde por el cierre y explota en energía verde
            U.radar_estado(barrido * 2, brillo=1.0)
            bpy.context.view_layer.update()
            Mm = S["mochila"].matrix_world
            C = Mm @ Vector((0, -0.03, 0.43))
            x = entra(u)
            S["m_luz"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 2 + 30 * x
            S["luz_m"].energy = 5 + 60 * x
            S["mochila"].scale = (1 + 0.06 * math.sin(tl * 40) * x, 1 + 0.06 * math.sin(tl * 37) * x, 1 + 0.08 * x)
            r = 0.02 + 3.0 * entra(lin(f, a + 26, b))
            esfera.location = C
            esfera.scale = (r, r, r)
            esfera.hide_render = r < 0.03
            bpy.data.materials["Energia"].node_tree.nodes["E"].inputs["Strength"].default_value = 4 + 12 * u
            E.empujar(cam, f, a, b, C + Vector((0.55, 1.35, 0.55)), C + Vector((0, 0, -0.10)), cuanto=0.40, lens=40, curva=entra)
        M.olas_t(S["mar"], t)
        bpy.context.view_layer.update()
        return {}

    return {"actualizar": act}


# ==================================================================
def _mk(fn, plano):
    return lambda sc, a, b: fn(sc, a, b, plano)


ESCENA = {**{k: "E1" for k in (1, 2, 3, 4, 5, 6, 8, 10, 14, 15, 17, 19, 20, 22, 23, 24, 25, 26, 27, 28, 37)},
          **{k: "E2" for k in (7, 9, 11, 12, 13, 16)}, **{k: "E3" for k in (18, 21, 29)}}
FUNC = {k: _mk({"E1": _e1, "E2": _e2, "E3": _e3}[e], k) for k, e in ESCENA.items()}


def _pieza(k, fn, **kw):
    a, b = FR(k)
    return dict(a=a, b=b, fn=fn, plano=k, **kw)


PIEZAS = {str(k): _pieza(k, fn) for k, fn in sorted(FUNC.items()) if k in E.T}
