"""PNG del cuadro de estilo → JPG con la misma gradación que el post del video (grado.py). Uso: post_estilo.py in.png out.jpg"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from grado import grado
grado(Image.open(sys.argv[1]).convert("RGB")).save(sys.argv[2], quality=92)
