# AnuncioFácil · todoshop
Generador de anuncios con el logo de todoshop (cuadrado 1080×1080, vertical 1080×1350, horizontal 1920×1080; variantes Nuevo, Oferta y Catálogo).

Este repositorio compila **dos programas** en GitHub, sin instalar nada:
| Carpeta | Resultado | Workflow |
|---|---|---|
| `www/` + `android-res/` | **APK** para Android (`app-debug.apk`) | Compilar APK |
| `pc/` | **EXE** para Windows (`AnuncioFacil.exe`) | Compilar EXE (PC) |

## APK
App 100 % offline (sin internet). Mejora la calidad de la foto y quita fondos lisos. El botón **Compartir / Guardar** abre el menú de Android (WhatsApp, Drive, Archivos…). `appId`: `com.todoshop.anuncios`. Clave de datos: `todoshop.anuncios.v1`.

## PC (Windows)
Ver `pc/README.md`. Quita fondos con IA (descarga única del modelo, ~180 MB) y funciona sin internet después.

## Cómo subirlo (desde el navegador)
1. Descomprime el ZIP. **Copia tu `debug.keystore`** junto a `package.json` si ya tienes una (si no, ver nota abajo).
2. github.com → **+ → New repository** → nombre → **Private** → *Create repository*.
3. **uploading an existing file** → arrastra **el contenido** de la carpeta (no la carpeta contenedora) → **Commit changes**.
4. Verifica que exista la carpeta `.github`. Si no: *Add file → Create new file*, nombre `.github/workflows/build-apk.yml`, pega el contenido del archivo suelto y confirma (repite para `build-exe.yml`).
5. Pestaña **Actions**: espera 5–8 min (APK) y unos minutos (EXE). Si no inicia: *Compilar APK → Run workflow*.
6. Con el ✅ abre la ejecución → **Artifacts** → descarga `todoshop-anuncios-apk` o `AnuncioFacil-exe`.
7. APK al teléfono → acepta «origen desconocido» y, si aparece, *Play Protect → Instalar de todos modos*.

**Llave de firma:** sin `debug.keystore` el workflow crea una nueva y la deja en el artifact `debug-keystore-NUEVA-guardala`. Descárgala, guárdala fuera de GitHub y súbela al repo (privado) como `debug.keystore`: así las próximas versiones se instalan encima sin perder datos.

Actualizaciones: reemplaza `www/index.html` (*Add file → Upload files*) y se recompila solo.
