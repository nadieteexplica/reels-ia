"""Recortes de la NASA (Blue Marble Next Generation, dic-2004, relieve + batimetría; dominio público) para mapa10.py.
L1: Pacífico occidental del mundo 21600×10800 (60 px/°) · L2: Japón y Ryukyu del mosaico D1 (90°E–180°, 0–90°N; 240 px/°).
Uso: python3 mapa_recortes.py <carpeta con los originales>   (escribe L1_pacifico.jpg y L2_japon.jpg ahí mismo)"""
import os, sys
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
d = sys.argv[1]
L1 = (100, -5, 170, 50)          # lon0, lat0, lon1, lat1 (los mismos de mapa10.py)
L2 = (122, 24, 146, 42)
w = Image.open(os.path.join(d, "world.topo.bathy.200412.3x21600x10800.jpg"))
px = lambda lon: int((lon + 180) * 60); py = lambda lat: int((90 - lat) * 60)
w.crop((px(L1[0]), py(L1[3]), px(L1[2]), py(L1[1]))).save(os.path.join(d, "L1_pacifico.jpg"), quality=95)
c = Image.open(os.path.join(d, "world.topo.bathy.200412.3x21600x21600.D1.jpg"))
px2 = lambda lon: int((lon - 90) * 240); py2 = lambda lat: int((90 - lat) * 240)
c.crop((px2(L2[0]), py2(L2[3]), px2(L2[2]), py2(L2[1]))).save(os.path.join(d, "L2_japon.jpg"), quality=95)
print("ok recortes")
