"""Cámaras de referencia del Ep. 9 (las usan prueba_set.py, los cuadros de estilo y planos_ep09.py)."""
import numpy as np
import ep09 as K
import lago as L


def z_suelo(x, y):
    return float(L.altura_terreno(np.array([x], np.float32), np.array([y], np.float32))[0])


VISTAS = {
    # cuadro 0: en el fondo seco, a 2,2 m del barro, entre témpanos, mirando al muro de hielo (sur)
    "c0": dict(pos=(96, 440, None, 1.7), mira=(20, 0, 16), lente=26),
    # general: el lago lleno contra el glaciar, desde la ladera este a ~120 m de alto
    "lleno": dict(pos=(230, 1350, 230, None), mira=(-20, 40, 5), lente=30),
    # a ras del agua, avanzando hacia el pie del muro
    "ras": dict(pos=(40, 360, 2.5, None), mira=(0, 0, 14), lente=35),
}


def poner(nombre, cam, S, f_aux=0.0):
    v = VISTAS[nombre]
    x, y, z, sobre = v["pos"]
    if z is None:
        z = z_suelo(x, y) + sobre
    K.mirar(cam, (x, y, z), v["mira"], lente=v["lente"])
    return cam
