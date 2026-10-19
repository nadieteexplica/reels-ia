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

### Antes de escribir: ¿para qué acción?
Cada video se diseña para que lo **envíen** (tiene destinatario: humor, dato sorpresa, "esto es para ti") o para que lo **guarden** (sirve después: cómo se hace, algo que enseña). Si no se puede responder *¿a quién se lo mandan?* o *¿por qué lo guardarían?*, la idea no sale. Base: `docs/REFERENCIAS.md` §3.

### Estructura de la línea datos (tiempos aproximados)
| Tramo | Qué pasa | Ejemplo (Ep. 1) |
|---|---|---|
| **0–3 s · Gancho** | Situación cotidiana o pregunta imposible, con una imagen fuerte desde el cuadro 0 | "Te comes un helado muy rápido… y de repente: ¡zas! Te duele la frente." |
| **3–8 s · Giro** | Contradice la intuición y abre la pregunta | "Pero el frío nunca tocó tu cerebro. Entonces, ¿qué pasó?" |
| **8–45 s · Mecanismo** | 4 a 6 pasos, cada uno con su imagen y su plano | Paladar → vasos → trigémino → confusión |
| **45–55 s · "Y lo más loco"** | Un segundo dato sorpresa | "Tu cerebro no siente dolor." |
| **55–68 s · Enseñanza** | Qué hacer, cómo usarlo o cómo explicárselo a alguien | "Aprieta la lengua contra el paladar…" |
| **Cierre en loop** | Frase que conecta con el inicio y deja ganas de verlo otra vez | "…nadie come helado lento." |

- **Con cifras:** dejar adivinar antes de revelar (opciones o pregunta en pantalla y después la respuesta).

### Estructura de la línea historias (ficción)
| Tramo | Qué pasa |
|---|---|
| **0–3 s · Cuadro absurdo** | Una imagen que todavía no tiene sentido, o la frase que abre el conflicto |
| **3–15 s · Conflicto** | Quién es, qué quiere y qué sale mal |
| **15–55 s · Escalada** | Cada 5–10 s algo empeora o sorprende; un símbolo que se repite amarra la historia |
| **55–70 s · Giro o remate** | El chiste, la revelación o la moraleja que apunta al que mira ("esto es para ti") |
| **Cierre en loop** | Conecta con el cuadro 0 |

- Una sola voz (Fernando), en primera persona o como narrador.
- Un set principal por historia, con muchos ángulos de cámara.
- No se copian fábulas, premisas ni firmas de otras cuentas.

### Reglas de escritura
- **Persona y registro:** segunda persona ("tú") y español latino neutro y cercano. Nada de chilenismos fuertes, porque el público es toda Latam.
- **Frases:** cortas (14 palabras o menos), una idea por frase y números concretos.
- **Pausas:** los `...` marcan pausas dramáticas, y ElevenLabs las respeta. Úsalos 2 a 4 veces por guion, no más.
- **Prohibido en el guion:** "en este video", "sígueme", "dale like", "no vas a creer", promesas falsas o exageración sin respaldo.
- **Cierre con envío (en prueba):** en algunos videos, la última frase pide el envío con un destinatario concreto ("mándaselo a ese amigo que siempre…"). Se marca en `PUBLICADOS.md` para comparar.
- **Palabras difíciles:** si la voz pronuncia mal un nombre raro, escríbelo fonéticamente en el texto que va a ElevenLabs (no en los subtítulos).
- **Ciencia incierta:** si la ciencia no está segura, dilo: "los científicos creen que…".

---

## 2. Verificación (antes de generar la voz)
Aplica a todo lo que el video presenta como real, en las dos líneas. En la línea historias, solo a los datos reales que aparezcan.

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

| # | Tiempo | Frase de la voz | Plano (tipo) | Acción / actuación | Cámara | SFX | Llamado en pantalla | Origen |
|---|---|---|---|---|---|---|---|---|

- **Origen** (obligatorio, lo revisa el auditor): `render` (Blender), `kling` (máx. 3 por video: manos con objetos o en la cara) o `biblioteca` (reacción ya hecha). Una mano con objeto marcada `render` no pasa la puerta 3.
- **Plano (tipo)** empieza con la escala: G, M, P, D o I (interior).

### Ritmo
- Cada plano dura 1,2–2,5 s (25–50 planos por minuto).
- **Nunca pasan más de 2 s sin un cambio en pantalla:** un corte, o algo que aparece, se transforma o se arma dentro del cuadro. Con transformación continua un plano puede durar más (R5: 13 s sin cortar).
- Los cortes son secos, justo en el inicio de una frase o palabra clave.
- Cambia la escala cada 8–12 s (general → medio → detalle → interior del cuerpo u objeto).

### Imagen
- **Cuadro 0:** tiene que ser una imagen fuerte, absurda o con pregunta, porque es la portada en la grilla de Instagram. Nada de fade desde negro.
- **Símbolo recurrente:** un objeto o detalle que vuelve durante el video y sirve de portada (el clavo de R4, la ventana de R6).
- **Construir frente al espectador:** cuando se pueda, la escena se arma o se transforma paso a paso, para que quieran ver cómo termina (R3, R5, R6).
- **Escala con repetición:** para cifras grandes, un objeto por caso (1.945 pelotas, miles de aviones) con instancias (R7, R9).
- **Cada afirmación del guion tiene su imagen.** Si algo es invisible (nervios, ondas, átomos), se muestra con una metáfora visual clara en 3D: un corte del objeto, un zoom hacia adentro o flechas de flujo.
- **Personaje recurrente:** es la cara de la cuenta y aparece en el gancho, en la reacción y en la enseñanza. Los formatos de objeto o corte (R5, R8) pueden ir sin él.
- **Final:** conecta visualmente con el cuadro 0 para que el loop se sienta continuo.

---

## 5. Look y animación
El estilo vigente está en `CONTEXTO.md`, y estas reglas valen para cualquier estilo.

### Luz y color
- **Fondo:** cielo o degradado celeste/turquesa, o escenario simple y saturado. Para objetos en primer plano, fondo oscuro cálido con partículas desenfocadas (R8).
- **Referencias de look** (`docs/REFERENCIAS.md`): R4 para personajes (paredes celestes, ropa pastel saturada), R3 para momentos dramáticos (una sola fuente fuerte y cálida, contraluz) y R8 para objetos.
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
- **Código de color fijo:** un color por idea u opción (correcto/incorrecto, opción A/B/C), igual en objetos, gráficos y subtítulos (R6, R7, R8).
- **Lo invisible se muestra:** planos translúcidos, flechas y números grandes que cuentan hacia arriba (R6, R8).
- **Nunca:** logos, marcas de agua, marcas de terceros, ni texto que tape la cara.

---

## 6. Subtítulos
- **Agrupación:** palabra por palabra en grupos de 1 a 3 palabras, que se cortan en la puntuación.
- **Tipografía:** Inter 900, en mayúsculas, a 76–88 px, blanca con borde negro de unos 5 px y sombra suave.
- **Palabra activa:** amarilla `#FFD23F`, con un pop de escala de 1,12 que dura 0,12 s.
- **Palabra clave:** 1–3 por video (la cifra, el objeto, el giro), en el color de su idea según el código de color y un 10 % más grande. Cuando se dice, hace el mismo pop.
- **Posición:** una o dos líneas, con la caja completa dentro de **x 120–888 · y 1000–1250**. Si una palabra no cabe (por ejemplo, GANGLIONEURALGIA), la fuente baja hasta 60 px. Nunca encima de la cara del personaje ni en el 35% inferior.
- **Excepción de posición:** si el protagonista del plano es un objeto centrado (formato objeto, R8), los subtítulos pueden ir arriba, en y 280–480, bajo la barra de Instagram.
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
2. **Hoja de contacto propia:** 1 cuadro por plano a baja resolución, revisada por Claude (encuadre, manos, objetos, caras) antes de mandar el render. Los cuadros de estilo y los de partida para Kling pasan además la **puerta 4 del auditor** (`docs/AUDITOR.md`).
3. **Render completo**, dos caminos (720×1280 con eliminación de ruido, se amplía a 1080×1920 al armar):
   - **GPU arrendada (RunPod, preferido):** `render-gpu.yml`. El pod arma la escena, renderiza con OptiX (~1,4 s por cuadro en una RTX A5000), mete los clips de Kling, hace post/audio/video y sube el MP4 a la prerelease `gpu-<run>` y a `epNN-borrador`. ~1 h por video, ~USD 0,3–0,5. El pod se borra solo y el workflow lo borra igual. Saldo cargado por Tomás, sin Auto-Pay.
   - **GitHub Actions (gratis, de respaldo):** `render.yml`, 16 partes (deja 4 máquinas libres para Kling y RunPod; con 20 se bloquea todo lo demás). ~1,5–2 h.
4. **Puerta 6 del auditor + OK de Tomás** sobre el MP4. Las correcciones se re-renderizan en la GPU (rápido) o, en Actions, sólo esos planos (`lista` + `base_run`).
5. **Encode:** H.264 High, yuv420p, CRF 18 y `+faststart`.
- **EEVEE** (motor en tiempo real) sólo sirve con tarjeta gráfica; en los servidores gratis es 3× más lento que Cycles (probado el 19-oct).
- Los logs de Actions no se pueden leer desde el espacio de trabajo: todo lo que haya que revisar (errores, log del pod) se sube a la prerelease del run.

### Objetos en la mano y reacciones (obligatorio) → Kling
- Desde el 19-oct, los planos donde alguien **agarra algo** (cono, taza, vasos) o **reacciona con las manos en la cara** se hacen con **Kling** (API oficial image-to-video 3.0, 1080p, 5 s, sin audio) partiendo de un cuadro nuestro. En Blender los dedos flotaban o atravesaban los objetos (Tomás lo rechazó dos veces).
- **Cuadro de partida con la mano libre** (o el objeto apoyado) y que Kling traiga el objeto: si el cuadro trae un agarre malo, Kling lo copia.
- Prompt en inglés: mismo estilo/personaje/fondo, cámara fija, acción exacta, "fingers wrapped around…", "never floats, never passes through…", sin texto ni objetos nuevos.
- Se revisa cada clip en 8 cuadros: dedos, objeto pegado a la mano, cara/personaje igual, nada que cambie de forma o color. Si no pasa, se repite (máx. 2) o el plano se rehace sin objeto en la mano.
- `kling/planos.json` dice qué clip reemplaza qué plano (`desde`, `velocidad`); el armado lo aplica antes del post. Para el loop, el último plano usa `last_frame` = cuadro 1.
- **Nunca** para anatomía ni para inventar datos visuales. Costo: 4 unidades por clip de 5 s (paquete de 100).

### Interior del cuerpo (obligatorio) — "cabeza de vidrio", aprobado por Tomás el 19-oct
- **Anatomía real** (`studio/plantilla/anatomia_kit.py` → Z-Anatomy, CC BY-SA 4.0) montada en la cabeza del personaje (`anatomia_real.py`). Nada de órganos inventados.
- **Siempre de perfil** (misma cámara lateral con leve 3/4 y push-in lento), fondo azul noche, piel de vidrio. Sin cráneo, sin cortes, sin ojos de caricatura.
- **Se ve y brilla sólo lo que la voz nombra en ese momento** (paladar azul hielo/naranjo, nervio amarillo con pulso, arterias rojas que laten, corteza que se enciende, frente roja); lo demás apagado u oculto. Nervios y arterias sólo del lado que mira a la cámara.
- Lo importante queda **sobre la franja de subtítulos**; la etiqueta (píldora) apunta con flecha calculada desde Blender (`flechas` en `*_planos.json`). Resplandor (bloom) en el post.
- Entrada a la cabeza: la cámara parte de frente y gira a perfil mientras se ve el interior.
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
- [ ] Nunca pasan más de 2 s sin un cambio en pantalla (corte o transformación).
- [ ] El final empalma con el inicio.

### 9.3 Revisión independiente (obligatoria) → el auditor
Desde el 19-oct-2026 la revisión independiente la hace el **auditor por etapas** (`docs/AUDITOR.md`, `tools/auditor/`): revisa guion, voz, storyboard, cuadros, clips de Kling, video final, paquete y proceso, cada uno como puerta. Lo de abajo es lo que mira en el video final (puerta 6).
- **Quién revisa:** subagentes que no participaron del video: uno por tramo de ≤9 planos y uno global.
- **Cómo se lanza:** como subagente, con los materiales y sin tu opinión ni tu autoevaluación.
- **Qué recibe:**
  - el guion con sus fuentes,
  - la hoja de contacto (1 cuadro por segundo),
  - una **tira de 6 cuadros por plano**, para juzgar movimiento y actuación,
  - la tabla de subtítulos contra `words.json` (palabra, inicio, fin, posición de la caja),
  - los eventos de los detectores automáticos (pantalla vacía, algo que aparece o desaparece de golpe, cambios de luz dentro del plano), con su "antes | después",
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
  - Todas las notas ≥8 y **ningún bloqueante** (dedos u objetos que flotan o atraviesan, algo que aparece de golpe, pantalla vacía, personaje distinto, cara tapada, dato sin respaldo, interior confuso, lista negra, estilo rechazado, faltas de ortografía).
  - Si no pasa, se corrige en el orden de la lista de arreglos y se revisa otra vez, hasta 3 rondas.
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
