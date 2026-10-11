"""Quitar fondo sin internet (tras descargar el modelo una sola vez). Usa onnxruntime + modelo IS-Net."""
import os, urllib.request
import numpy as np
from PIL import Image, ImageFilter
import render

MODEL = "isnet-general-use.onnx"
URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/" + MODEL
MIN_SIZE = 170_000_000
USER_DIR = os.path.join(os.path.expanduser("~"), ".anuncio_facil_models")
_sess = None

class ModeloNoDisponible(Exception): pass

def model_path():
    for d in (os.path.join(render.base(), "models"), USER_DIR):
        p = os.path.join(d, MODEL)
        if os.path.exists(p) and os.path.getsize(p) > MIN_SIZE:
            return p
    return None

def download(progress=None):
    os.makedirs(USER_DIR, exist_ok=True)
    dst, tmp = os.path.join(USER_DIR, MODEL), os.path.join(USER_DIR, MODEL + ".part")
    try:
        with urllib.request.urlopen(URL, timeout=30) as r, open(tmp, "wb") as f:
            total = int(r.headers.get("Content-Length", 0)); done = 0
            while True:
                b = r.read(1 << 20)
                if not b: break
                f.write(b); done += len(b)
                if progress and total: progress(f"Descargando modelo (solo la primera vez)… {done * 100 // total}%")
        if os.path.getsize(tmp) < MIN_SIZE: raise OSError("descarga incompleta")
        os.replace(tmp, dst)
    except Exception as e:
        if os.path.exists(tmp): os.remove(tmp)
        raise ModeloNoDisponible(
            "No se pudo descargar el modelo de recorte. La primera vez necesita internet (~180 MB). "
            f"También puedes copiar el archivo {MODEL} a la carpeta:\n{USER_DIR}\n\nDetalle: {e}")
    return dst

def session(progress=None):
    global _sess
    if _sess is None:
        import onnxruntime as ort
        p = model_path() or download(progress)
        _sess = ort.InferenceSession(p, providers=["CPUExecutionProvider"])
    return _sess

def _fill_holes(b):
    """Rellena huecos interiores de una máscara binaria (L, 0/255)."""
    from PIL import ImageDraw, ImageOps
    pad = ImageOps.expand(b, 2, 0)
    inv = ImageOps.invert(pad)
    ImageDraw.floodfill(inv, (0, 0), 128)
    holes = inv.point(lambda v: 255 if v == 255 else 0)
    return ImageOps.crop(Image.fromarray(np.maximum(np.asarray(pad), np.asarray(holes))), 2)

def remove_bg(img, progress=None):
    """img: PIL RGBA/RGB. Devuelve RGBA con fondo transparente, recortado al producto."""
    sess = session(progress)
    if progress: progress("Detectando el producto…")
    rgb = img.convert("RGB")
    if max(rgb.size) > 2400:
        k = 2400 / max(rgb.size); rgb = rgb.resize((int(rgb.width * k), int(rgb.height * k)), Image.LANCZOS)
    x = np.asarray(rgb.resize((1024, 1024), Image.LANCZOS), dtype=np.float32)
    x = x / max(x.max(), 1e-6) - 0.5
    x = x.transpose(2, 0, 1)[None].astype(np.float32)
    m = sess.run(None, {sess.get_inputs()[0].name: x})[0][0, 0]
    m = (m - m.min()) / max(m.max() - m.min(), 1e-6)
    a = Image.fromarray((m * 255).astype("uint8")).resize(rgb.size, Image.LANCZOS)
    a = np.asarray(a, dtype=np.float32) / 255
    a = np.clip((a - 0.10) / 0.60, 0, 1)                      # contraste: limpia halos grises
    soft = Image.fromarray((a * 255).astype("uint8"))
    solid = _fill_holes(soft.point(lambda v: 255 if v > 60 else 0)).filter(ImageFilter.MinFilter(5))
    a = np.maximum(np.asarray(soft, dtype=np.float32), np.asarray(solid, dtype=np.float32))   # interior sólido, borde suave
    a = Image.fromarray(a.astype("uint8")).filter(ImageFilter.GaussianBlur(1.0))
    out = rgb.convert("RGBA"); out.putalpha(a)
    box = a.point(lambda v: 255 if v > 12 else 0).getbbox()
    if not box: raise ValueError("No se detectó ningún producto en la imagen.")
    pad = int(max(box[2] - box[0], box[3] - box[1]) * 0.03)
    box = (max(box[0] - pad, 0), max(box[1] - pad, 0), min(box[2] + pad, out.width), min(box[3] + pad, out.height))
    return out.crop(box)
