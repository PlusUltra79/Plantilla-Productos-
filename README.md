# AnuncioFácil · todoshop
Programa de escritorio (Windows) para crear anuncios con tu logo en 3 formatos: cuadrado 1080×1080, vertical 1080×1350 y horizontal 1920×1080: foto, nombre, precio/oferta, características y botón. Variantes: Producto nuevo, Oferta y Catálogo. **Funciona sin internet**, salvo la descarga única del modelo de recorte (ver abajo).

## Opción A — Con Python (rápido)
1. Instala Python desde python.org (marca **Add Python to PATH**).
2. Doble clic en `1-Instalar.bat` (solo la primera vez; instala Pillow).
3. Doble clic en `2-Abrir-AnuncioFacil.bat`.

## Opción B — Un solo `.exe` (sin instalar Python)
Sube esta carpeta a un repositorio privado de GitHub; en **Actions → Compilar EXE** descarga el artifact `AnuncioFacil-exe`.

## Uso
Elige el tipo, la foto y completa los textos; la vista previa se actualiza sola. Pulsa **Guardar PNG**. Tus textos se recuerdan (`~/.anuncio_facil.json`).

## Pruebas manuales
1. Abrir sin foto: aparece el aviso al guardar. 2. Elegir foto JPG/PNG. 3. Nombre muy largo: se reduce a 2 líneas. 4. Oferta: aparecen precio tachado y etiqueta. 5. Catálogo: aparece «Pág. X de Y». 6. Sin características: el precio ocupa todo el ancho.

## Tipografía
Usa Arial Black/Bold de Windows. Para Montserrat, copia los .ttf a la carpeta `fonts/`.

## Quitar fondo del producto
Elige la foto y pulsa **Quitar fondo del producto**. El producto queda solo sobre fondo blanco en el anuncio. Puedes guardar el recorte en PNG transparente.
- **Primera vez:** descarga un modelo de IA (~180 MB) y lo guarda en tu usuario (`.anuncio_facil_models`). Después funciona 100 % sin internet.
- **Sin internet nunca:** copia `isnet-general-use.onnx` a la carpeta `models/` de este programa.
- Funciona mejor con fotos nítidas y buen contraste entre producto y fondo. Productos blancos sobre fondo blanco, transparentes o con sombras fuertes pueden requerir revisión: usa «Usar foto sin fondo» para comparar con el original.
- Si Windows indica que falta una DLL de onnxruntime, instala «Microsoft Visual C++ Redistributable».

## Mejorar calidad y resolución
Casilla activada por defecto: amplía la foto (hasta ~2000 px), reduce el ruido, afina los detalles y avivar el color y el contraste. Funciona sin internet y tarda menos de un segundo. Es una mejora clásica (no inventa detalles como una IA): una foto muy borrosa o diminuta mejora, pero no se vuelve nítida. Si el resultado no te gusta, desmarca la casilla.

## Estilo
- **Con detalles** (por defecto): fondo degradado amarillo suave, círculo, anillos, puntos, destellos, sombra bajo el producto recortado, subrayado en el nombre y línea punteada en el encabezado.
- **Minimalista**: el diseño limpio de antes.
