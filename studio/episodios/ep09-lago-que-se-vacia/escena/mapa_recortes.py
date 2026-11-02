"""Recortes de la NASA (Blue Marble Next Generation, dic-2004, relieve + batimetría) para mapa.py.
L1: Sudamérica del mundo 21600×10800 (60 px/°) · L2: Aysén del mosaico B2 500 m (240 px/°; B2 = 90°O–0°, 0°–90°S).
Uso: python3 mapa_recortes.py <carpeta con los originales>   (escribe L1_sudamerica.jpg y L2_aysen.jpg en la misma carpeta)"""
import os, sys
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
d = sys.argv[1]
L1 = (-100, -62, -20, 16)        # lon0, lat0, lon1, lat1 (los mismos de mapa.py)
L2 = (-80, -53, -66, -40)
w = Image.open(os.path.join(d, "world.topo.bathy.200412.3x21600x10800.jpg"))
px = lambda lon: int((lon + 180) * 60); py = lambda lat: int((90 - lat) * 60)
w.crop((px(L1[0]), py(L1[3]), px(L1[2]), py(L1[1]))).save(os.path.join(d, "L1_sudamerica.jpg"), quality=95)
b = Image.open(os.path.join(d, "world.topo.bathy.200412.3x21600x21600.B2.jpg"))
px2 = lambda lon: int((lon + 90) * 240); py2 = lambda lat: int(-lat * 240)
b.crop((px2(L2[0]), py2(L2[3]), px2(L2[2]), py2(L2[1]))).save(os.path.join(d, "L2_aysen.jpg"), quality=95)
print("ok recortes")
