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
V.poner(vista, cam, S)
sc.view_settings.exposure = float(os.environ.get("EXPO", -0.3))
sc.render.filepath = sys.argv[-1]
bpy.ops.render.render(write_still=True)
print("ok", sys.argv[-1])
