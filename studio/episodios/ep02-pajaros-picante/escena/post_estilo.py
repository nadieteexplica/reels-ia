"""Post simple para cuadros de estilo: brillo (bloom) suave sobre lo más luminoso, como el post del video."""
import sys
import numpy as np
from PIL import Image, ImageFilter
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32) / 255
lum = a.max(axis=2)
mask = np.clip((lum - 0.80) / 0.2, 0, 1)[..., None] * a
r = max(4, im.size[0] // 60)
glow = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255
out = np.clip(a + glow * 0.55, 0, 1)
Image.fromarray((out * 255).astype(np.uint8)).save(dst, quality=93)
