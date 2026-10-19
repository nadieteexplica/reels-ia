# Manual de producción — Nadie te explica

Este es el estándar de cada video. Si algo de acá no se cumple, el video no sale.

---

## 0. Estructura de archivos por episodio
Cada episodio tiene un **id único `epNN-slug`** (por ejemplo `ep02-dedos-arrugados`). El mismo id se usa en la carpeta, en el trabajo de voz (`jobs/voz/NNNN-epNN-slug.json` → `out/tts/epNN-slug.mp3`) y en el tag del release (`epNN`).
```
studio/episodios/epNN-slug/
  guion.md          guion final + fuentes + tiempos por frase
  storyboard.md     tabla plano por plano
  words.json        tiempos por palabra (salen de la alineación de ElevenLabs)
  escena/           código de la animación (three.js o Blender)
  audio/            sound.py y mezcla (los .wav no se suben al repo)
  entrega/caption.md   textos por red + comentario fijado + hashtags
```
- **Por qué dentro de `studio/`:** el servidor de render corre desde `studio/` y ahí está `node_modules`.
- **El MP4 final** va como asset de GitHub Release (tag `epNN`). No se commitean MP4 al repo. Solo si Metricool no acepta la URL del release (se prueba en la Fase 0), se usa `out/videos/` con `raw.githubusercontent.com`.
- **El slug** va en minúsculas, sin tildes, con guiones y sin el número.
- **Ep. 1:** es la excepción histórica. Su voz quedó como `out/tts/ep1-helado.*`.

---

## 1. Guion

### Duración y largo
- **62–75 s**, porque TikTok solo monetiza videos de más de 1 minuto.
- Fernando habla a unas **2,97 palabras por segundo**, así que el guion tiene **190–215 palabras** (185 palabras dan apenas ~62 s, sin margen).
- Mide siempre con los tiempos reales de la alineación, no con la estimación.

### Estructura (tiempos aproximados)
| Tramo | Qué pasa | Ejemplo (Ep. 1) |
|---|---|---|
| **0–3 s · Gancho** | Situación cotidiana o pregunta imposible, con una imagen fuerte desde el cuadro 0 | "Te comes un helado muy rápido… y de repente: ¡zas! Te duele la frente." |
| **3–8 s · Giro** | Contradice la intuición y abre la pregunta | "Pero el frío nunca tocó tu cerebro. Entonces, ¿qué pasó?" |
| **8–45 s · Mecanismo** | 4 a 6 pasos, cada uno con su imagen y su plano | Paladar → vasos → trigémino → confusión |
| **45–55 s · "Y lo más loco"** | Un segundo dato sorpresa | "Tu cerebro no siente dolor." |
| **55–68 s · Enseñanza** | Qué hacer, cómo usarlo o cómo explicárselo a alguien | "Aprieta la lengua contra el paladar…" |
| **Cierre en loop** | Frase que conecta con el inicio y deja ganas de verlo otra vez | "…nadie come helado lento." |

### Reglas de escritura
- **Persona y registro:** segunda persona ("tú") y español latino neutro y cercano. Nada de chilenismos fuertes, porque el público es toda Latam.
- **Frases:** cortas (14 palabras o menos), una idea por frase y números concretos.
- **Pausas:** los `...` marcan pausas dramáticas, y ElevenLabs las respeta. Úsalos 2 a 4 veces por guion, no más.
- **Prohibido en el guion:** "en este video", "sígueme", "dale like", "no vas a creer", promesas falsas o exageración sin respaldo.
- **Palabras difíciles:** si la voz pronuncia mal un nombre raro, escríbelo fonéticamente en el texto que va a ElevenLabs (no en los subtítulos).
- **Ciencia incierta:** si la ciencia no está segura, dilo: "los científicos creen que…".

---

## 2. Verificación (antes de generar la voz)
1. **El dato central** necesita 2 fuentes independientes y confiables:
   - instituciones (NASA, NIH, Cleveland Clinic, Mayo Clinic, servicios geológicos),
   - universidades,
   - papers,
   - medios de ciencia serios (LiveScience, Scientific American, Popular Science, BBC Science, National Geographic).
2. **Cada cifra** del guion necesita su fuente al lado en `guion.md`.
3. **Salud:** solo información general, nunca indicaciones médicas, y "si te pasa seguido, consulta" cuando aplique.
4. **Cifras contradictorias:** si las fuentes no coinciden, usa la más conservadora o un rango ("entre 30 segundos y 2 minutos").

---

## 3. Voz
Se crea `jobs/voz/NNNN-epNN-slug.json` (NNNN es correlativo, mira el último en la carpeta) con este contenido:
```json
{"mode":"tts","id":"epNN-slug","voice_id":"dlGxemPxFMTY7iXagmOj","model_id":"eleven_multilingual_v2",
 "voice_settings":{"stability":0.4,"similarity_boost":0.8,"style":0.32,"use_speaker_boost":true},
 "text":"<guion>"}
```
- **Generación:** al hacer push se dispara Actions. Espera con `git fetch` hasta que cambie `origin/main` y después haz pull.
- **Revisar el resultado:** en `out/status.json["NNNN-epNN-slug.json"]`. Si dice `error`, es falla aunque el commit haya llegado. Además, el workflow queda en rojo.
- **Archivos que salen:** `out/tts/epNN-slug.mp3` y `epNN-slug.json`, con la alineación por carácter.
- **`words.json`:** se arma con `python3 tools/words.py out/tts/epNN-slug.json studio/episodios/epNN-slug/words.json [pantalla.txt]`.
  - Usa `alignment`, no `normalized_alignment`.
  - Si escribiste palabras fonéticamente para la voz, pasa `pantalla.txt` con el guion tal como debe verse. Debe tener el mismo número de palabras.
- **Control:**
  - La duración total debe quedar entre 62 y 75 s.
  - Ninguna palabra puede durar más de 1,2 s (salvo pausas).
  - El conteo de palabras tiene que coincidir con el guion.
  - Si algo falla, se regenera solo esa versión, porque cada intento cuesta créditos.
- **Varios episodios:** van varios JSON en un solo push, y Actions procesa solo los JSON nuevos o modificados de ese push. Nunca edites jobs viejos, porque se volverían a correr y gastarían créditos.

---

## 4. Storyboard (antes de animar)
Se arma una tabla en `storyboard.md`:

| # | Tiempo | Frase de la voz | Plano (tipo) | Acción / actuación | Cámara | SFX | Llamado en pantalla |
|---|---|---|---|---|---|---|---|

### Ritmo
- Cada plano dura 2–3 s, con 20–25 planos por minuto.
- Los cortes son secos, justo en el inicio de una frase o palabra clave.
- Cambia la escala cada 8–12 s (general → medio → detalle → interior del cuerpo u objeto).

### Imagen
- **Cuadro 0:** tiene que ser una imagen fuerte, porque es la portada en la grilla de Instagram. Nada de fade desde negro.
- **Cada afirmación del guion tiene su imagen.** Si algo es invisible (nervios, ondas, átomos), se muestra con una metáfora visual clara en 3D: un corte del objeto, un zoom hacia adentro o flechas de flujo.
- **Personaje recurrente:** es la cara de la cuenta y aparece en el gancho, en la reacción y en la enseñanza.
- **Final:** conecta visualmente con el cuadro 0 para que el loop se sienta continuo.

---

## 5. Look y animación
El estilo vigente está en `CONTEXTO.md`, y estas reglas valen para cualquier estilo.

### Luz y color
- **Fondo:** cielo o degradado celeste/turquesa, o escenario simple y saturado.
- **Luz:** suave de estudio, con luz principal, de relleno y de contorno.
- **Exposición:** nunca sobreexpuesto.
  - Control automático: menos del 3% de píxeles por sobre 250 en cada cuadro de muestra, **medido sin subtítulos ni gráficos**. Se renderiza el cuadro con `?nocap=1` o se excluye la zona de subtítulos.
  - Tone mapping: Neutral o AgX, no ACES fuerte.

### Encuadre vertical 1080×1920
- La cara del personaje va en el tercio superior, entre y≈350 y y≈900.
- Hay que dejar aire sobre el pelo.
- Nada importante debajo de y=1250.

### Cámara y animación
- **Cámara:** siempre en movimiento (acercamiento lento, órbita o paneo). En los golpes van zoom-punch y un shake corto.
- **Actuación con los principios de animación:**
  - anticipación,
  - aplastar y estirar,
  - exageración,
  - acción secundaria,
  - poses sostenidas de 6–10 cuadros en el énfasis.
- **Expresiones grandes** en la cara: ojos, cejas y boca.

### Transiciones y estética
- **Transiciones:** corte seco por defecto. Máximo 2 transiciones especiales por video (whip o zoom).
- **Gráficos:** limpios y amigables. Flechas finas y etiquetas tipo píldora (texto oscuro sobre blanco, o blanco sobre color), con un máximo de 4 palabras.
- **Nunca:** logos, marcas de agua, marcas de terceros, ni texto que tape la cara.

---

## 6. Subtítulos
- **Agrupación:** palabra por palabra en grupos de 1 a 3 palabras, que se cortan en la puntuación.
- **Tipografía:** Inter 900, en mayúsculas, a 76–88 px, blanca con borde negro de unos 5 px y sombra suave.
- **Palabra activa:** amarilla `#FFD23F`, con un pop de escala de 1,12 que dura 0,12 s.
- **Posición:** una o dos líneas, con la caja completa dentro de **x 120–888 · y 1000–1250**. Si una palabra no cabe (por ejemplo, GANGLIONEURALGIA), la fuente baja hasta 60 px. Nunca encima de la cara del personaje ni en el 35% inferior.
- **Limpieza:** sin puntos suspensivos ni signos de puntuación en pantalla, y con tildes correctas.
- **Silencio del título:** los subtítulos se ocultan cuando aparece un texto grande en pantalla, como un nombre científico.

---

## 7. Audio
- **Voz:** es la protagonista y no lleva efectos encima.
- **Música:** queda 15–20 dB por debajo de la voz, con ducking automático según la envolvente de la voz.
  - Fuente: sintetizada en numpy, o una pista de licencia libre (Pixabay Music o la librería de audio de YouTube) que Tomás descargue.
  - Nunca música comercial.
- **SFX:** un efecto por cada evento visual, como un golpe, un pop, un whoosh en un cambio de escala o un cristal. En un momento clave, cortar la música en seco es un recurso cómico que funciona.
- **Master:** loudnorm a **−14 LUFS integrado**, con **true peak ≤ −1 dBTP** y AAC 192 kbps a 48 kHz.

---

## 8. Render (con dos OK de Tomás antes de gastar horas)
Regla nacida del Ep. 1 (19-oct-2026): **nunca se renderiza el video completo sin que Tomás haya aprobado el look.**
1. **Cuadros de estilo (≈30 min):** un cuadro HD por escenario nuevo (plaza, interior del cuerpo, etc.). Tomás los aprueba o pide cambios. Cambiar acá es barato.
2. **Hoja de contacto propia:** 1 cuadro por plano a baja resolución, revisada por Claude (encuadre, manos, objetos, caras) antes de mandar el render.
3. **Render completo** en GitHub Actions: **720×1280, 12 muestras con eliminación de ruido**, se amplía a 1080×1920 al armar (en el celular se ve igual; ~4× más rápido que HD). 40 partes en paralelo: ~1–1,5 h.
4. **Revisión independiente + OK de Tomás** sobre el MP4. Si algo se corrige, se re-renderizan **sólo esos planos** (`lista` con rangos + `base_run`) y se rearma.
5. **Encode:** H.264 High, yuv420p, CRF 18 y `+faststart`.
- **EEVEE** (motor en tiempo real) sólo sirve con tarjeta gráfica; en los servidores gratis es 3× más lento que Cycles (probado el 19-oct).

### Objetos en la mano (obligatorio)
- Todo lo que el personaje sostiene va **dentro del puño** (entre pulgar y dedos, `cup_matrix`), nunca flotando ni pegado a la palma.
- Lo que va a la boca (taza, vaso, bombilla, cono) **llega a los labios**: con IK hacia una meta en la boca durante el sorbo o la mordida.
- Se revisa en la hoja de contacto con un cuadro **en el momento del contacto** de cada objeto.

### Interior del cuerpo (obligatorio)
- Nada de órganos inventados con formas simples: se usa el **kit de anatomía real** (`studio/plantilla/anatomia_kit.py` → Z-Anatomy, CC BY-SA 4.0) montado en la cabeza del personaje (`anatomia_real.py`).
- Las explicaciones se **animan con activaciones**: pulsos de luz que viajan por los nervios, zonas que se encienden, vasos que laten.
- Crédito obligatorio en descripción y primer comentario (ver `studio/plantilla/LICENCIAS_ANATOMIA.md`).

---

## 9. Control de calidad (QA)

### 9.1 Automático (script)
- [ ] Dura 62–75 s, a 1080×1920 y 30 fps, en H.264 yuv420p y pesa menos de 100 MB.
- [ ] El volumen integrado está en −14 ±1 LUFS y el true peak en ≤ −1 dBTP (`ffmpeg -af ebur128`).
- [ ] No hay negros ni congelados (`blackdetect`, `freezedetect` > 0,5 s).
- [ ] Menos del 3% de píxeles quemados (>250) en cada cuadro de muestra, medido sin subtítulos.
- [ ] Los subtítulos coinciden palabra por palabra con `words.json`, y sus cajas quedan dentro de la zona segura (se miden en el DOM durante el render).

### 9.2 Visual (hoja de contacto con 1 cuadro por segundo y cuadros de cada plano)
- [ ] El cuadro 0 sirve como portada.
- [ ] No hay cabezas, manos ni objetos clave cortados por el borde.
- [ ] La cara del personaje nunca queda tapada por subtítulos ni gráficos.
- [ ] El personaje se ve igual en todo el video (pelo, ropa, colores).
- [ ] Cada frase del guion tiene su imagen.
- [ ] Hay un cambio de escala cada 8–12 s.
- [ ] Ningún plano estático dura más de 3 s.
- [ ] El final empalma con el inicio.

### 9.3 Revisión independiente (obligatoria)
- **Quién revisa:** un subagente que no participó del video.
- **Cómo se lanza:** como subagente, con los materiales y sin tu opinión ni tu autoevaluación.
- **Qué recibe:**
  - el guion con sus fuentes,
  - la hoja de contacto (1 cuadro por segundo),
  - una **tira de 6 cuadros por plano**, para juzgar movimiento y actuación,
  - la tabla de subtítulos contra `words.json` (palabra, inicio, fin, posición de la caja),
  - las estadísticas de audio: LUFS, true peak y dB de diferencia entre voz y música,
  - este manual.
- **Cómo puntúa:** de 1 a 10, cada uno con un comentario concreto, en:
  1. **Gancho:** ¿alguien deja de hacer scroll en 1 s?
  2. **Claridad:** ¿un niño de 12 años lo entiende?
  3. **Ritmo:** ¿hay tiempos muertos?
  4. **Belleza:** ¿se ve profesional y atractivo?
  5. **Animación:** ¿el personaje actúa o está tieso?
  6. **Subtítulos:** ¿se leen, sincronizan y no tapan?
  7. **Audio:** ¿la mezcla y el volumen están bien?
  8. **Precisión:** ¿cada dato está respaldado?
- **Regla de aprobación:**
  - Si algún criterio queda bajo 8, se corrige y se revisa otra vez, hasta 3 rondas.
  - Si sigue sin llegar, se descarta y se explica por qué.

---

## 10. Entrega por video (`entrega/caption.md`)
- **Instagram / TikTok:**
  - gancho (1 línea),
  - el dato en 1 línea,
  - pregunta abierta ("¿Qué otra cosa te pasa y nadie te explica por qué?"),
  - 3 a 5 hashtags (1 amplio + 2–3 del tema + `#nadieteexplica`).
- **YouTube Shorts:**
  - título de 60 caracteres o menos, con la palabra clave al inicio (p. ej. "Por qué te duele la cabeza con el helado 🍦"),
  - descripción de 2 líneas con las fuentes.
- **Primer comentario** (`firstCommentText` de Metricool):
  - "Fuentes: …",
  - "¿Qué quieres que te explique la próxima?".

  Metricool no lo fija; Tomás puede fijarlo a mano. En YouTube, las fuentes van también en la descripción.
- **Portada:** el cuadro 0, o el más fuerte, en `portada.jpg`.
- **Etiqueta IA:** siempre en Instagram (`isAiGenerated`) y TikTok (`isAigc`), porque la voz es sintética. En YouTube (`isAiGeneratedContent`), solo si el estilo es realista.
- **Palabras clave:** en el texto, lo que la gente buscaría ("dolor de cabeza helado"). En TikTok, 1 de cada 4 usuarios busca algo en los primeros 30 s de un video.

---

## 11. Publicación (solo con OK de Tomás)
- **Herramienta:** Metricool `createScheduledPost`, con `blogId` 7499838 y `publicationDate` en America/Santiago.
- **Un post por red** (3 por video), porque cada post lleva un solo texto. Cada uno lleva:
  - `media:[URL pública del MP4]`,
  - `autoPublish:true`,
  - `firstCommentText` y `videoCoverMilliseconds` (el cuadro de portada).
- **Instagram:** `instagramData:{type:"REEL", isAiGenerated:true}`.
- **TikTok:** `tiktokData:{isAigc:true}`.
- **YouTube:** `youtubeData:{type:"short", title, madeForKids:<decisión de Tomás en CONTEXTO>, category:"EDUCATION", isAiGeneratedContent:<true solo si es realista>}`.
- **Horario:** según `getBestTimeToPostByNetwork`, con zona America/Santiago.
- **Registro:** después de publicar, se agrega una fila en `docs/PUBLICADOS.md`.
