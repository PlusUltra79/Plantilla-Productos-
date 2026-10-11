"""AnuncioFácil · todoshop — generador de anuncios 1:1. Funciona sin internet."""
import json, os, queue, threading, tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import render, bgremove, enhance

CFG = os.path.join(os.path.expanduser("~"), ".anuncio_facil.json")
VARS = {"Producto nuevo": "nuevo", "Oferta": "oferta", "Catálogo": "catalogo"}
FMTS = {"Cuadrado 1080×1080": "cuadrado", "Vertical 1080×1350": "vertical", "Horizontal 1920×1080": "horizontal"}
STYLES = {"Con detalles": "detalles", "Minimalista": "minimal"}
CTAS = ["Escríbenos por WhatsApp", "Consulta disponibilidad", "Pide el tuyo hoy"]
FIELDS = ("fmt", "style", "variant", "name", "price", "old", "offer", "cta", "phone", "page")
DEF = dict(fmt="Cuadrado 1080×1080", style="Con detalles", variant="Producto nuevo", name="Nombre del producto", price="$00.00", old="$00.00",
           offer="OFERTA ESPECIAL", cta=CTAS[0], phone="", page="1 de 20")

def open_img(p):
    return ImageOps.exif_transpose(Image.open(p)).convert("RGBA")

class App(tk.Tk):
    def __init__(s):
        super().__init__()
        s.title("AnuncioFácil · todoshop"); s.minsize(960, 720)
        s.prod = None; s.orig = None; s.cut = None; s.job = None; s.last = None; s.q = queue.Queue()
        s.usecut = tk.BooleanVar(value=True); s.ec = (None, None)
        s.logo = open_img(os.path.join(render.base(), "logo.png"))
        try: saved = json.load(open(CFG, encoding="utf8"))
        except Exception: saved = {}
        s.v = {k: tk.StringVar(value=saved.get(k, DEF[k])) for k in FIELDS}
        s.enh = tk.BooleanVar(value=saved.get('enh', True))
        s.build(); s.feat.insert("1.0", saved.get("feat", ""))
        for var in s.v.values(): var.trace_add("write", s.sched)
        s.protocol("WM_DELETE_WINDOW", s.close); s.toggle(); s.refresh()

    def build(s):
        L = ttk.Frame(s, padding=14); L.pack(side="left", fill="y")
        R = ttk.Frame(s, padding=14); R.pack(side="left", fill="both", expand=True)
        def lab(t, p=L): ttk.Label(p, text=t, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(10, 2))
        def ent(k, p=L): ttk.Entry(p, textvariable=s.v[k], width=40).pack(fill="x")
        lab("Formato")
        cf = ttk.Combobox(L, textvariable=s.v["fmt"], values=list(FMTS), state="readonly"); cf.pack(fill="x")
        lab("Estilo")
        cs = ttk.Combobox(L, textvariable=s.v["style"], values=list(STYLES), state="readonly"); cs.pack(fill="x")
        lab("Tipo de anuncio")
        cb = ttk.Combobox(L, textvariable=s.v["variant"], values=list(VARS), state="readonly"); cb.pack(fill="x")
        cb.bind("<<ComboboxSelected>>", lambda e: s.toggle())
        cf.bind("<<ComboboxSelected>>", lambda e: s.sched()); cs.bind("<<ComboboxSelected>>", lambda e: s.sched())
        lab("Foto del producto")
        ttk.Button(L, text="Elegir foto…", command=s.pick_prod).pack(fill="x")
        s.pl = ttk.Label(L, text="Ninguna foto seleccionada", foreground="#666"); s.pl.pack(anchor="w")
        s.bb = ttk.Button(L, text="✂  Quitar fondo del producto", command=s.cut_bg, state="disabled"); s.bb.pack(fill="x", pady=(6, 0))
        ttk.Checkbutton(L, text="Usar foto sin fondo", variable=s.usecut, command=s.sync).pack(anchor="w")
        ttk.Checkbutton(L, text="Mejorar calidad y resolución (recomendado)", variable=s.enh, command=s.sync).pack(anchor="w")
        s.pb = ttk.Progressbar(L, mode="indeterminate")
        lab("Nombre del producto"); ent("name")
        lab("Precio o promoción"); ent("price")
        s.fo = ttk.Frame(L); s.fo.pack(fill="x"); s.oin = ttk.Frame(s.fo)
        lab("Precio anterior (tachado)", s.oin); ent("old", s.oin); lab("Etiqueta de oferta", s.oin); ent("offer", s.oin)
        lab("Características (una por línea, máx. 4)")
        s.feat = tk.Text(L, height=4, width=40, wrap="word", font=("Segoe UI", 10)); s.feat.pack(fill="x")
        s.feat.bind("<KeyRelease>", s.sched)
        lab("Llamado a la acción")
        ttk.Combobox(L, textvariable=s.v["cta"], values=CTAS).pack(fill="x")
        lab("WhatsApp / contacto"); ent("phone")
        s.fp = ttk.Frame(L); s.fp.pack(fill="x"); s.pin = ttk.Frame(s.fp)
        lab("Página del catálogo", s.pin); ent("page", s.pin)
        lab("Logo")
        ttk.Button(L, text="Cambiar logo…", command=s.pick_logo).pack(fill="x")
        s.pv = ttk.Label(R); s.pv.pack()
        bf = ttk.Frame(R); bf.pack(pady=12)
        ttk.Button(bf, text="💾  Guardar anuncio PNG", command=s.save).pack(side="left", padx=4, ipady=4)
        s.bc = ttk.Button(bf, text="Guardar producto sin fondo", command=s.save_cut, state="disabled"); s.bc.pack(side="left", padx=4, ipady=4)
        s.st = ttk.Label(R, text=""); s.st.pack()

    def toggle(s):
        v = VARS.get(s.v["variant"].get(), "nuevo")
        s.oin.pack(fill="x") if v == "oferta" else s.oin.pack_forget()
        s.pin.pack(fill="x") if v == "catalogo" else s.pin.pack_forget()
        s.sched()

    def sched(s, *_):
        if s.job: s.after_cancel(s.job)
        s.job = s.after(250, s.refresh)

    def data(s):
        d = {k: s.v[k].get() for k in FIELDS}
        d["variant"] = VARS.get(d["variant"], "nuevo"); d["fmt"] = FMTS.get(d["fmt"], "cuadrado"); d["style"] = STYLES.get(d["style"], "detalles"); d["feat"] = s.feat.get("1.0", "end").strip()
        return d

    def refresh(s):
        s.job = None
        try:
            dd = s.data(); s.last = render.render(dd, s.prod, s.logo, dd["fmt"])
            k = min(640 / s.last.width, 640 / s.last.height)
            s.tkimg = ImageTk.PhotoImage(s.last.resize((int(s.last.width * k), int(s.last.height * k)), Image.LANCZOS))
            s.pv.configure(image=s.tkimg)
        except Exception as e:
            s.st.configure(text=f"No se pudo dibujar el anuncio: {e}")

    def pick(s, title):
        return filedialog.askopenfilename(title=title, filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp *.bmp"), ("Todos", "*.*")])

    def pick_prod(s):
        p = s.pick("Foto del producto")
        if not p: return
        try: s.orig = open_img(p); s.cut = None; s.pl.configure(text=os.path.basename(p)); s.bb.configure(state="normal"); s.bc.configure(state="disabled"); s.sync()
        except Exception: messagebox.showerror("Imagen no válida", "No se pudo abrir ese archivo. Prueba con un JPG o PNG.")

    def sync(s):
        src = s.cut if (s.cut is not None and s.usecut.get()) else s.orig
        if src is not None and s.enh.get():
            if s.ec[0] is not src:
                s.st.configure(text="Mejorando calidad de la imagen…"); s.update_idletasks()
                try: s.ec = (src, enhance.enhance(src))
                except Exception as e: s.ec = (src, src); s.st.configure(text=f"No se pudo mejorar la imagen: {e}")
            src = s.ec[1]
        s.prod = src
        s.refresh()

    def cut_bg(s):
        if s.orig is None: return
        s.bb.configure(state="disabled"); s.pb.pack(fill="x", pady=4); s.pb.start(12)
        def work():
            try: s.q.put(("ok", bgremove.remove_bg(s.orig, lambda m: s.q.put(("msg", m)))))
            except Exception as e: s.q.put(("err", str(e)))
        threading.Thread(target=work, daemon=True).start(); s.poll()

    def poll(s):
        try:
            while True:
                k, v = s.q.get_nowait()
                if k == "msg": s.st.configure(text=v)
                else:
                    s.pb.stop(); s.pb.pack_forget(); s.bb.configure(state="normal")
                    if k == "ok":
                        s.cut = v; s.usecut.set(True); s.bc.configure(state="normal"); s.st.configure(text="Fondo eliminado. Revisa los bordes en la vista previa."); s.sync()
                    else: s.st.configure(text=""); messagebox.showerror("No se pudo quitar el fondo", v)
                    return
        except queue.Empty: pass
        s.after(150, s.poll)

    def save_cut(s):
        if s.cut is None: return
        p = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")], initialfile="producto-sin-fondo.png")
        if p:
            try: (enhance.enhance(s.cut) if s.enh.get() else s.cut).save(p, "PNG"); s.st.configure(text=f"Guardado en: {p}")
            except Exception as e: messagebox.showerror("No se pudo guardar", str(e))

    def pick_logo(s):
        p = s.pick("Logo")
        if not p: return
        try: s.logo = open_img(p); s.refresh()
        except Exception: messagebox.showerror("Imagen no válida", "No se pudo abrir ese archivo. Prueba con un JPG o PNG.")

    def save(s):
        if s.prod is None and not messagebox.askyesno("Sin foto", "Aún no elegiste la foto del producto. ¿Guardar de todos modos?"): return
        p = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")],
                                         initialfile=f"anuncio-{s.data()['variant']}-{s.data()['fmt']}.png")
        if not p: return
        try:
            dd = s.data(); render.render(dd, s.prod, s.logo, dd["fmt"]).save(p, "PNG")
            s.st.configure(text=f"Guardado en: {p}")
        except Exception as e:
            messagebox.showerror("No se pudo guardar", f"Revisa que la carpeta permita escribir.\n\n{e}")

    def close(s):
        try: json.dump({**{k: s.v[k].get() for k in FIELDS}, "feat": s.feat.get("1.0", "end").strip(), "enh": s.enh.get()}, open(CFG, "w", encoding="utf8"))
        except Exception: pass
        s.destroy()

if __name__ == "__main__":
    App().mainloop()
