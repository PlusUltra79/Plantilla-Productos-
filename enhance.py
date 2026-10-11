"""Mejora de calidad sin internet: aumenta resolución, reduce ruido, afina detalles y avivar color."""
from PIL import Image, ImageFilter, ImageEnhance, ImageOps

TARGET = 2000   # lado mayor deseado (px)
MAXSIDE = 3000  # tope para no gastar memoria

def enhance(img):
    img = img.convert("RGBA")
    a, rgb = img.getchannel("A"), img.convert("RGB")
    w, h = rgb.size; m = max(w, h)
    if m < 700:                                    # fotos pequeñas: suaviza artefactos JPEG antes de ampliar
        rgb = rgb.filter(ImageFilter.MedianFilter(3))
    k = min(TARGET / m, 4.0) if m < TARGET else (MAXSIDE / m if m > MAXSIDE else 1.0)
    if abs(k - 1) > 0.01:
        size = (max(1, round(w * k)), max(1, round(h * k)))
        rgb, a = rgb.resize(size, Image.LANCZOS), a.resize(size, Image.LANCZOS)
    rgb = rgb.filter(ImageFilter.UnsharpMask(radius=min(3.0, 1.2 + 0.5 * k), percent=130, threshold=2))
    rgb = rgb.filter(ImageFilter.UnsharpMask(radius=0.7, percent=50, threshold=1))
    try: rgb = ImageOps.autocontrast(rgb, cutoff=0.4, mask=a)
    except Exception: rgb = ImageOps.autocontrast(rgb, cutoff=0.4)
    rgb = ImageEnhance.Color(rgb).enhance(1.10)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.04)
    out = rgb.convert("RGBA"); out.putalpha(a)
    return out
