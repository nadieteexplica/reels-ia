# Touchscreen: por qué el lápiz no funciona y el dedo sí

estado: **con /watch** (23-nov-2026, `tools/watch/watch.py`; la grabación corta en el s 70 de ~84: el cierre no se vio)

## Datos
- @speedy_devv (Keyframes), Instagram Reels, hecho 100 % con código y Claude Code · **13,6 M vistas** · duración ~84 s · **visto promedio 30,6 s** (dato del propio dueño, `-automatizacion.md` §2).
- En la grabación (23-nov): 765 mil me gusta · 2.745 comentarios · 17,4 mil reposts · **188 mil envíos** · 143 mil guardados. Envíos = 25 % de los me gusta (el más alto de los cuatro: es un video "para mandar").
- Idioma: inglés. Fecha de publicación: s/d.
- Grabación de Tomás: el reel empieza en el s 0 de la grabación (entra en la primera palabra). En el s ~70 el video se congela (rueda de carga) y la voz se corta a media frase: **se vieron 70 de ~84 s**; los últimos ~14 s (cierre y CTA) quedan por ver.

## Estructura
**B · Mecanismo con contradicción.** Confirmado: la contradicción (roce leve sí, presión fuerte no) va en la primera frase y en el cuadro 0; el mecanismo la resuelve y después la reusa en casos que el espectador conoce (guantes, lluvia, guantes táctiles).

## Beats (con segundos)
- 0–5,6 s HOOK: la contradicción dicha y mostrada: el dedo apenas roza y la carga dorada se junta bajo la yema; el lápiz aprieta y no pasa nada.
- 5,6–7,7 s QUIZ: la pregunta directa (¿qué está sintiendo entonces?).
- 7,7–12 s REVEAL corto: no mide presión, mide la electricidad de tu cuerpo (adelanta la respuesta y abre el "¿cómo?").
- 12–15,5 s SETUP con dolor: invierno, contestar con guantes (mano enguantada, llamada entrante que no se puede aceptar).
- 15,5–29,4 s Mecánica 1: bajo el vidrio hay una grilla de cables (filas y columnas), cada cruce guarda una carga y el teléfono los revisa una y otra vez (contador de barridos por segundo 115 → 120).
- 29,4–44 s Mecánica 2 / REVEAL: el cuerpo es agua salada y conduce; la yema roba carga a los cruces de abajo, los números bajan de 100 a ~62 y el teléfono "lo cuenta como toque" (s 44 = **52 %** de 84 s).
- 44–50,5 s Bonus: como mide cada cruce por separado, sigue dos dedos (pellizcar para hacer zoom).
- 50,5–58,6 s TWIST que paga el setup: el guante de lana no conduce, el dedo está ahí pero la carga no se mueve. Frase clave: "For the phone, nobody touched it." (s 57–58, **68 %**).
- 58,6–65 s Caso 2: la lluvia; cada gota conduce y parece un dedo.
- 65–70 s Caso 3: guantes táctiles con hilo conductor en la yema (aquí corta la grabación).
- 70–84 s: por ver (la investigación dice frase poética que cierra en loop + CTA de envío ligado al caso).

## Gancho
- **Cuadro 0:** fondo casi negro; corte lateral del vidrio con una fila de arcos de carga dorados y una franja de píxeles de colores; a la izquierda un dedo, arriba a la derecha la punta dorada de un lápiz. Etiquetas chicas en mayúscula con línea guía (vidrio, cables). Se entiende en mudo: dedo y lápiz frente a la misma pantalla.
- **0–3 s:** el dedo roza y los arcos se concentran bajo la yema (aparece la etiqueta de carga en 1,5 s); en 3 s el foco pasa al lápiz, que aprieta sin efecto.
- **Texto en pantalla:** sólo subtítulos, arriba al centro, 1–4 palabras por vez; cambian cada ~0,5 s. La palabra clave va en un recuadro azul con manillas (estilo selección de Figma): teléfono (0 s), "más leve" (1,5 s), dedo (2,5 s), ignora (3,5 s). Emoji en línea al lado de algunas palabras (teléfono, rayo, gota, guante, lluvia).
- **Voz 0–3 s:** arranca en el s 0, sin respiro: tu pantalla reacciona al roce más leve de tu dedo… (y en 3–5 s: e ignora un lápiz apretado con toda tu fuerza).

## Ritmo
- **Cortes:** ffmpeg marca 0 (la UI de Instagram fija y las transiciones de cámara continua lo engañan; recortando la UI marca 4). Contando en las hojas: **~26 cambios de plano en 70 s ≈ 22/min, uno cada ~2,7 s**, casi todos por movimiento de cámara o zoom a través del objeto (al vidrio, a la grilla, a la yema), no por corte seco.
- **Voz:** 231 palabras en 68 s de voz ≈ **204 palabras/min** (210 hablando; 3,4 palabras/s). Habla el 88 % del tiempo; un solo silencio real (0,7 s en el s 67,8).
- **Cada cuánto cambia algo:** subtítulo cada ~0,5 s, palabra en recuadro cada ~1,5–2 s, etiqueta o número nuevo cada ~3 s, plano nuevo cada ~2,7 s. Nunca hay más de ~3 s con la misma imagen quieta.

## Recursos visuales
- 3D/2,5D limpio por código, fondo oscuro (#0B101D–#16181F) + **un solo color de energía (dorado)** para la carga; los píxeles RGB como textura de pantalla.
- Etiquetas en mayúscula blanca, chicas, con línea guía al objeto (vidrio, cables, carga, fila, columna, cruce, lana, hilo conductor).
- Avisos honestos en letra mínima abajo a la izquierda: ilustración aumentada, valores ilustrativos, cables transparentes en un teléfono real, carga invisible al ojo.
- **Números en vivo** como prueba: la grilla de "100" que baja a 81/62/84 bajo el dedo, con corchete que los agrupa; contador de barridos con la fuente en letra chica (modelo de iPhone).
- Objetos cotidianos reconocibles: mano con guante gris, pantalla de bloqueo con hora, llamada entrante, pantalla de inicio con íconos, gotas sobre el vidrio.
- Subtítulos: blancos, sans, palabras por decir en gris, la que suena en blanco, y la clave en recuadro con manillas.

## Sonido
- −15,3 LUFS integrado, LRA 3,4 LU (voz muy pareja), pico 0,4 dBTP.
- Voz en inglés, rápida y continua (humana o IA: por ver). Música y foley: por ver (la investigación dice foley en cada acción: clic, whoosh, ping).

## Cierre y CTA
- No se vio (la grabación corta en el s 70). Según la investigación: frase poética que empalma con la primera (loop) + CTA de envío ligado al caso (mandárselo a quien no le funciona el celular con las manos mojadas). Por ver con una grabación completa.

## Qué copiamos
- **La contradicción en el cuadro 0 y en la primera frase a la vez** (dos cosas lado a lado, una funciona y la otra no), sin explicar todavía.
- **Adelantar la respuesta corta en el s ~8** ("no es presión, es electricidad") y dejar abierto el cómo: la gente se queda por el mecanismo, no por la sorpresa.
- **Un dolor cotidiano antes del mecanismo** (guantes en invierno) que se paga a los 2/3 del video: el setup vuelve como twist.
- **Números en vivo que cambian bajo la acción** (100 → 62): el reveal se ve, no sólo se dice.
- Recuadro en la palabra clave, cambio de subtítulo cada ~0,5 s, un color de energía sobre fondo oscuro, avisos de "ilustrativo" en letra chica.
- 2–3 casos extra que el espectador reconoce (lluvia, guantes táctiles) en vez de un dato suelto.

## Qué no
- 84 s: nuestro techo en YouTube es ~45–50 s; la gente mira ~31 s. Si copiamos la forma, cortamos al primer caso extra.
- El tema: nuestro Ep. 13 (pantalla táctil) se descartó por muy visto.
- Inglés técnico en la voz ("capacitive", nombres de modelos): la fuente va en letra chica en pantalla, no en la voz.

---
Fuentes de esta ficha: /watch del 23-nov-2026 sobre la grabación de Tomás `referencias/ScreenRecording_11-23-2026 12-51-28_1.MP4` (salida en el scratchpad, no en el repo), más `docs/estudios/investigacion-2026-11-23-formatos.md` (§1–4), `-automatizacion.md` (§2) y la consulta de vidIQ del 23-nov (`studio/caza/ronda08-demanda/`).
