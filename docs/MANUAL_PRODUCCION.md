# Manual de producción — Nadie te explica

Este es el estándar de cada video. Si algo de acá no se cumple, el video no sale.

---

## 0. Estructura de archivos por episodio
```
episodios/<NN>-<slug>/
  guion.md          guion final + fuentes + tiempos por frase
  storyboard.md     tabla plano por plano
  words.json        tiempos por palabra (salen de la alineación de ElevenLabs)
  escena/           código de la animación (three.js o Blender)
  audio/            sound.py y mezcla (los .wav no se suben al repo)
  entrega/caption.md   textos por red + comentario fijado + hashtags
```
- **El MP4 final** va como asset de GitHub Release (tag `epNN`) o en `out/videos/` si Metricool no acepta la URL del release. Esto se prueba en la Fase 0.
- **El slug** va en minúsculas, sin tildes y con guiones, por ejemplo `01-congelamiento-cerebral`.

---

## 1. Guion

### Duración y largo
- **62–75 s**, porque TikTok solo monetiza videos de más de 1 minuto.
- Fernando habla a unas **2,97 palabras por segundo**, así que el guion tiene **185–215 palabras**.
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
Se crea `jobs/voz/NNNN-<slug>.json` con este contenido:
```json
{"mode":"tts","id":"<slug>","voice_id":"dlGxemPxFMTY7iXagmOj","model_id":"eleven_multilingual_v2",
 "voice_settings":{"stability":0.4,"similarity_boost":0.8,"style":0.32,"use_speaker_boost":true},
 "text":"<guion>"}
```
- **Generación:** al hacer push se dispara Actions. Espera con `git fetch` hasta que cambie `origin/main` y después haz pull.
- **Archivos que salen:** `out/tts/<slug>.mp3` y `<slug>.json`, con la alineación por carácter. De ahí se arma `words.json`, una lista de `{w, s, e}` partida por espacios.
- **Control:**
  - La duración total debe quedar entre 62 y 75 s.
  - Ninguna palabra puede durar más de 1,2 s (salvo pausas).
  - El conteo de palabras tiene que coincidir con el guion.
  - Si algo falla, se regenera solo esa versión, porque cada intento cuesta créditos.
- **Varios episodios:** van varios JSON en un solo commit, y Actions los procesa todos.

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
  - Control automático: menos del 3% de píxeles por sobre 250 en cada hoja de contacto.
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
- **Tipografía:** Inter 900, en mayúsculas, a 84–90 px, blanca con borde negro de unos 5 px y sombra suave.
- **Palabra activa:** amarilla `#FFD23F`, con un pop de escala de 1,12 que dura 0,12 s.
- **Posición:** la parte de arriba del bloque va en y≈1100–1180, dentro de x 100–980. Nunca encima de la cara del personaje ni en el 35% inferior.
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

## 8. Render
1. **Prueba primero:** 1 cuadro por plano y una hoja de contacto, que se revisa *antes* del render completo.
2. **Render completo a 30 fps.** Si el workspace es lento (unos 4–8 s por cuadro), va a GitHub Actions en una matriz paralela de 10–20 jobs.
3. **Encode:** H.264 High, yuv420p, CRF 18 y `+faststart`.

---

## 9. Control de calidad (QA)

### 9.1 Automático (script)
- [ ] Dura 62–75 s, a 1080×1920 y 30 fps, en H.264 yuv420p y pesa menos de 100 MB.
- [ ] El volumen integrado está en −14 ±1 LUFS y el true peak en ≤ −1 dBTP (`ffmpeg -af ebur128`).
- [ ] No hay negros ni congelados (`blackdetect`, `freezedetect` > 0,5 s).
- [ ] Menos del 3% de píxeles quemados (>250) en cada cuadro de muestra.
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
- **Qué recibe:**
  - el guion,
  - las fuentes,
  - la hoja de contacto,
  - las estadísticas de audio,
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
- **Comentario fijado:**
  - "Fuentes: …",
  - "¿Qué quieres que te explique la próxima?".
- **Portada:** el cuadro 0, o el más fuerte, en `portada.jpg`.
- **Etiqueta IA:** se marca si el estilo es realista o donde la plataforma lo exija.
- **Palabras clave:** en el texto, lo que la gente buscaría ("dolor de cabeza helado"). En TikTok, 1 de cada 4 usuarios busca algo en los primeros 30 s de un video.

---

## 11. Publicación (solo con OK de Tomás)
- **Herramienta:** Metricool `createScheduledPost`, que necesita una URL pública del MP4. Se publica en las 3 redes, cada una con su texto.
- **Horario:** según `getBestTimeToPostByNetwork`, con zona America/Santiago.
- **Registro:** después de publicar, se agrega una fila en `docs/PUBLICADOS.md`.
