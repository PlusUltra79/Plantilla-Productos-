"""Motor de dibujo del anuncio (1080x1080). Se dibuja al doble y se reduce para bordes suaves."""
import os, sys
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2
FORMATS = {'cuadrado': (1080, 1080), 'vertical': (1080, 1350), 'horizontal': (1920, 1080)}
INK, AC = (22, 22, 22), (255, 210, 31)

def base():
    return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))

DIRS = [os.path.join(base(), "fonts"), r"C:\Windows\Fonts", "/usr/share/fonts/truetype/dejavu",
        "/System/Library/Fonts/Supplemental", "/Library/Fonts"]
NAMES = {
    "black": ["Montserrat-ExtraBold.ttf", "ariblk.ttf", "Arial Black.ttf", "DejaVuSans-Bold.ttf"],
    "bold": ["Montserrat-Bold.ttf", "arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf"],
    "semi": ["Montserrat-SemiBold.ttf", "segoeuib.ttf", "arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf"],
}

@lru_cache(maxsize=None)
def _font(kind, px):
    for n in NAMES[kind]:
        for d in DIRS:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, px)
    return ImageFont.load_default(px)

def fnt(kind, size): return _font(kind, int(size * S))
def sc(*v): return [int(x * S) for x in v]

def tw(d, t, f): return d.textlength(t, font=f)

def fit(d, t, maxw, size, mn, kind):
    while size > mn and tw(d, t, fnt(kind, size)) > maxw * S:
        size -= 2
    return fnt(kind, size)

def wrap(d, t, f, maxw):
    lines, cur = [], ""
    for w in t.split():
        n = (cur + " " + w).strip()
        if tw(d, n, f) > maxw * S and cur:
            lines.append(cur); cur = w
        else:
            cur = n
    return lines + ([cur] if cur else [])

def put(d, x, y, t, f, anchor="ls", fill=INK):
    d.text((x * S, y * S), t, font=f, fill=fill, anchor=anchor)

def _star(dl, cx, cy, R, r, fill):
    dl.polygon([(cx, cy - R), (cx + r, cy - r), (cx + R, cy), (cx + r, cy + r), (cx, cy + R),
                (cx - r, cy + r), (cx - R, cy), (cx - r, cy - r)], fill=fill)

def _decor_box(im, x0, y0, x1, y1, p, pp):
    """Fondo decorado del recuadro de la foto: degradado, círculo, anillos, puntos, destellos y sombra."""
    bw, bh = (x1 - x0) * S, (y1 - y0) * S
    yy, xx = np.mgrid[0:bh, 0:bw].astype(np.float32)
    r = np.hypot((xx - bw / 2) / (bw / 2), (yy - bh / 2) / (bh / 2))
    t = np.clip(r / 1.25, 0, 1)[..., None] ** 1.6
    L = Image.fromarray((np.array((255, 255, 255), np.float32) * (1 - t) + np.array((255, 240, 184), np.float32) * t).astype("uint8"))
    dl = ImageDraw.Draw(L)
    cx, cy, R0 = bw / 2, bh / 2 + 10 * S, min(bw, bh) * 0.38
    dl.ellipse((cx - R0, cy - R0, cx + R0, cy + R0), fill=(255, 233, 140))
    R1 = R0 + 34 * S; dl.ellipse((cx - R1, cy - R1, cx + R1, cy + R1), outline=AC, width=3 * S)
    R2 = R0 + 70 * S
    for a in range(0, 360, 12):
        dl.arc((cx - R2, cy - R2, cx + R2, cy + R2), a, a + 6, fill=AC, width=3 * S)
    g = 24 * S
    for ox, oy in ((28 * S, 28 * S), (bw - 28 * S - 5 * g, bh - 28 * S - 3 * g)):
        for i in range(6):
            for j in range(4):
                x, y = ox + i * g, oy + j * g
                dl.ellipse((x - 4 * S, y - 4 * S, x + 4 * S, y + 4 * S), fill=AC)
    _star(dl, bw * .17, bh * .62, 26 * S, 7 * S, AC); _star(dl, bw * .85, bh * .30, 34 * S, 9 * S, AC)
    _star(dl, bw * .78, bh * .80, 18 * S, 5 * S, INK); _star(dl, bw * .22, bh * .22, 14 * S, 4 * S, INK)
    if p is not None and p.getchannel("A").getextrema()[0] < 250:      # sombra de suelo solo si el producto está recortado
        sh = Image.new("L", L.size, 0)
        px, py = pp[0] - x0 * S + p.width / 2, pp[1] - y0 * S + p.height
        ImageDraw.Draw(sh).ellipse((px - p.width * .28, py - 14 * S, px + p.width * .28, py + 14 * S), fill=120)
        L.paste((70, 55, 10), mask=sh.filter(ImageFilter.GaussianBlur(10 * S)))
    mask = Image.new("L", L.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, bw - 1, bh - 1), radius=28 * S, fill=255)
    im.paste(L, (x0 * S, y0 * S), mask)

def render(data, prod=None, logo=None, fmt="cuadrado"):
    W, H = FORMATS.get(fmt, FORMATS["cuadrado"])
    hz = fmt == "horizontal"; dy = 0 if hz else H - 1080
    v = data.get("variant", "nuevo")
    im = Image.new("RGB", (W * S, H * S), "white")
    d = ImageDraw.Draw(im)

    if logo is not None:
        h = 100.0; w = logo.width * h / logo.height
        if w > 320: h *= 320 / w; w = 320
        lg = logo.convert("RGBA").resize((int(w * S), int(h * S)), Image.LANCZOS)
        im.paste(lg, (60 * S, 52 * S), lg)

    det = data.get("style", "detalles") == "detalles"
    bx0, by0, bx1, by1 = (60, 160, 1100, 1020) if hz else (60, 160, 1020, 650 + dy)
    mx, my = (bx0 + bx1) / 2, (by0 + by1) / 2
    p = pp = None
    if prod is not None:
        k = min((bx1 - bx0 - 40) / prod.width, (by1 - by0 - 40) / prod.height)
        p = prod.convert("RGBA").resize((max(1, int(prod.width * k * S)), max(1, int(prod.height * k * S))), Image.LANCZOS)
        pp = (int(mx * S - p.width / 2), int(my * S - p.height / 2))
    if det:
        _decor_box(im, bx0, by0, bx1, by1, p, pp)
        d.rounded_rectangle(sc(bx0, by0, bx1, by1), radius=28 * S, outline=AC, width=4 * S)
        for x in range(250, W - 290, 16):
            d.ellipse(sc(x - 2.5, 99.5, x + 2.5, 104.5), fill=AC)
    else:
        d.rectangle(sc(bx0, by0, bx1, by1), outline=AC, width=4 * S)
    if p is not None: im.paste(p, pp, p)
    else: put(d, mx, my + 10, "SUBE AQUÍ LA FOTO DEL PRODUCTO", fnt("bold", 30), "ms", (150, 150, 150))

    if v == "nuevo":
        d.polygon(sc(W - 240, 0, W - 140, 0, W, 140, W, 240), fill=AC)
        t = Image.new("RGBA", sc(400, 80), (0, 0, 0, 0))
        put(ImageDraw.Draw(t), 200, 52, "¡NUEVO!", fnt("black", 34), "ms")
        t = t.rotate(-45, expand=True, resample=Image.BICUBIC)
        im.paste(t, (int((W - 90) * S - t.width / 2), int(95 * S - t.height / 2)), t)

    feats = [x.strip() for x in data.get("feat", "").splitlines() if x.strip()][:4]
    if hz:
        nx, nw, ny, maxl, s0 = 1160, 700, 250, 3, 64
        fb = (1160, 610, 1860, 810) if feats else None
        X, CW, py, by, fx, fy = 1160, 700, 826, 946, 1860, 1040
    else:
        nx, nw, ny, maxl, s0 = 60, 960, 692 + dy, 2, 60
        fb = (60, 830 + dy, 520, 1003 + dy) if feats else None
        X, CW = (560, 460) if feats else (60, 960)
        py, by, fx, fy = 830 + dy, 947 + dy, 1020, 1048 + dy
    cx = X + CW / 2

    nm = (data.get("name", "").strip() or "NOMBRE DEL PRODUCTO").upper()
    s = s0
    while True:
        lines = wrap(d, nm, fnt("black", s), nw)
        if len(lines) <= maxl or s <= 34: break
        s -= 2
    for i, l in enumerate(lines[:maxl]):
        put(d, nx, ny + s * .9 + i * s * 1.1, l, fnt("black", s))
    if det and (hz or len(lines) <= 1):
        n = min(len(lines), maxl); bl = ny + s * .9 + (n - 1) * s * 1.1
        wd = min(max(tw(d, l, fnt("black", s)) for l in lines[:n]) / S * .45, 320)
        d.rounded_rectangle(sc(nx, bl + 12, nx + wd, bl + 22), radius=5 * S, fill=AC)

    if fb:
        d.rounded_rectangle(sc(*fb), radius=18 * S, fill=(255, 246, 207))
        put(d, fb[0] + 24, fb[1] + 33, "CARACTERÍSTICAS", fnt("bold", 17))
        for i, t in enumerate(feats):
            put(d, fb[0] + 24, fb[1] + 72 + i * 31, "• " + t, fit(d, "• " + t, fb[2] - fb[0] - 50, 26, 16, "semi"))

    d.rounded_rectangle(sc(X, py, X + CW, py + 105), radius=18 * S, fill=(255, 249, 220), outline=AC, width=4 * S)
    price = data.get("price", "").strip() or "$00.00"
    if v == "oferta":
        put(d, cx, py + 23, (data.get("offer") or "OFERTA").upper(), fnt("bold", 17), "ms")
        old = data.get("old", "").strip()
        if old:
            f = fnt("semi", 22); put(d, cx, py + 50, old, f, "ms", (119, 119, 119))
            hw = tw(d, old, f) / S / 2
            d.line(sc(cx - hw, py + 43, cx + hw, py + 43), fill=(119, 119, 119), width=2 * S)
        put(d, cx, py + 96, price, fit(d, price, CW - 40, 44, 24, "black"), "ms")
    else:
        put(d, cx, py + 77, price, fit(d, price, CW - 40, 70, 28, "black"), "ms")

    d.rounded_rectangle(sc(X, by, X + CW, by + 56), radius=16 * S, fill=AC)
    cta = (data.get("cta", "").strip() or "Consulta disponibilidad").upper()
    put(d, cx, by + 38, cta, fit(d, cta, CW - 30, 24, 13, "black"), "ms")

    phone = data.get("phone", "").strip()
    foot = "Pág. " + data.get("page", "") if v == "catalogo" else ("Pedidos y consultas: " + phone if phone else "")
    if foot: put(d, fx, fy, foot, fnt("semi", 22), "rs")
    return im.resize((W, H), Image.LANCZOS)
