"""Prueba local rápida del set (sin Pete): renderiza una vista y la guarda.
Uso: VISTA=c0|lleno|corte|vaso RES=270x480 SAMPLES=12 NIVEL=-29 DET=0.5 python3 prueba_set.py salida.png"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
import numpy as np
import ep09 as K
import lago as L
import vistas as V

vista = os.environ.get("VISTA", "c0")
w, h = (int(v) for v in os.environ.get("RES", "270x480").split("x"))
sc = K.escena("prueba", (w, h), int(os.environ.get("SAMPLES", 12)))
nivel = float(os.environ.get("NIVEL", L.NIVEL_VACIO if vista == "c0" else L.NIVEL_LLENO))
S = L.valle(sc, nivel=nivel, detalle=float(os.environ.get("DET", 0.5)))
cam = K.camara(sc, (0, 0, 0), (0, -1, 0), lente=35, fstop=None)
if vista == "corte":
    C = L.Corte(sc, S)
    C.estado(float(os.environ.get("NIVEL", 0)), lift=float(os.environ.get("LIFT", 0)), lengua=float(os.environ.get("LENGUA", 0)),
             radio=float(os.environ.get("RADIO", 0)))
    K.mirar(cam, (L.XC + 260, -25, 8), (L.XC, -25, -6), lente=35)
elif vista == "vaso":
    xo, zo = L.orilla(520.0, 1)
    Vv = L.vaso(sc, (xo + 1.2, 520.0, zo))
    K.mirar(cam, (xo + 1.2 + 0.08, 520.0 + 0.36, zo + 0.36), (xo + 1.2, 520.0, zo + 0.27), lente=50)
    cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 2.8; cam.data.dof.focus_distance = 0.37
else:
    V.poner(vista, cam, S)
sc.view_settings.exposure = float(os.environ.get("EXPO", -0.3))
sc.render.filepath = sys.argv[-1]
bpy.ops.render.render(write_still=True)
print("ok", sys.argv[-1])
