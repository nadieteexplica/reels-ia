"""PNG del cuadro de estilo → JPG (sin gradación: el look sale del render, AgX). Uso: post_estilo.py in.png out.jpg"""
import sys
from PIL import Image
Image.open(sys.argv[1]).convert("RGB").save(sys.argv[2], quality=92)
