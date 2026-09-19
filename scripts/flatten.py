import sys, numpy as np
from PIL import Image
# Highlight clamp: values < LO untouched, LO..HI stretched up to TARGET, >= HI clamped to TARGET.
# Same curve is applied to videos with ffmpeg lutrgb so stills and clips match.
LO, HI, TARGET = 175, 226, 245
lut = np.array([v if v < LO else (LO + (v-LO)*(TARGET-LO)/(HI-LO) if v < HI else TARGET) for v in range(256)]).round().astype(np.uint8)
for src, dst in zip(sys.argv[1::2], sys.argv[2::2]):
    im = np.asarray(Image.open(src).convert('RGB'))
    Image.fromarray(lut[im]).save(dst); print(dst)
