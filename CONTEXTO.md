# Nadie te explica — contexto del proyecto

Leer esto entero antes de trabajar. Es la fuente de verdad de lo decidido hasta ahora (18-oct-2026).

## La cuenta
- **Nombre:** Nadie te explica. Cuenta faceless de videos cortos hechos con Claude.
- **Redes:** Instagram `nadie_te_explica` · TikTok "Nadie te explica" · YouTube Shorts (canal `UCFvRAW_exW4MgXEwQqCD1Fw`).
- **Metricool:** brand id `7499838`, zona horaria America/Santiago. Ya están conectadas las tres redes.
- **Dueño:** Tomás (Santiago, Chile). Habla en español chileno casual y directo, y quiere respuestas cortas.
- **Meta: automatización total.** Claude investiga qué subir, escribe el guion, genera la voz, anima, publica a diario (vía Metricool) y revisa los datos.

## Formato (brief vigente)
- **Temas de todo el mundo**, no solo animales. Los ganchos son:
  - "¿Qué pasaría si…?"
  - "¿Cómo funciona por dentro?"
  - "¿Por qué no podemos…?"
  - "¿Qué pasa dentro de…?"
  - "¿Sabías que…?"
- **Un dato impresionante** por video, de unos 60 s, que **termina enseñando algo**.
- **Solo información real y verificada**, con fuentes. Nada de desinformar.
- **Animación 3D "sí o sí".**
- **Edición:** limpia, amigable, llamativa, entretenida y bonita de ver.
- **Rechazado:**
  - Low-poly (el video del oxígeno).
  - Rayos X / neón 2D.
  - Look lavado o sobreexpuesto con cámara pegada (primer intento del helado).
  - Copiar formatos de otras cuentas tal cual.
  - El pulpo como tema (no engancha).
- **Estilo en evaluación:**
  - **Monito animado 3D.** Muestras de 5 s en tres estilos: A · Pixar suave, B · caricatura con contorno, C · plastilina.
  - **Semi-realista tipo Zack D. Films.** Él lo mostró como referencia. Usarlo como referencia de *calidad*, pero con personaje, colores y escenario propios. Nunca su marca.
  - Tomás aún no elige.

## Voz
- **ElevenLabs**, plan Starter (pagado). La voz elegida es **Fernando Martínez**: `voice_id dlGxemPxFMTY7iXagmOj`.
- Modelo `eleven_multilingual_v2`.
- Settings: stability 0.4, similarity 0.8, style 0.32, speaker boost activado.
- Se genera **con timestamps por carácter** para armar subtítulos palabra por palabra.

## Reglas de edición (del estudio de formatos virales)
- **Gancho** en los primeros 0–2 s.
- **Planos:**
  - Una idea por plano, de unos 2–3 s cada uno (20–25 por minuto).
  - Cortes secos sincronizados con la voz.
  - La cámara siempre se mueve (acercamientos lentos u órbitas).
  - Cambio de escala cada 8–12 s.
- **Look:** fondos vivos (celeste/turquesa), luz suave de estudio, colores saturados. Nunca sobreexpuesto. Con encuadre vertical se deja aire: la cara del personaje va en el tercio superior.
- **Subtítulos:**
  - Palabra por palabra, de 1 a 3 palabras a la vez, en mayúsculas gruesas.
  - Blancos con borde negro, y la palabra activa en amarillo (#FFD23F).
  - Ubicados en y≈1000–1250 dentro de la zona segura x 120–888. Nunca en el 35% inferior.
- **Llamados en pantalla:** mínimos (flechas finas, etiquetas tipo píldora). Sin logo encima.
- **Audio:**
  - Música 15–20 dB bajo la voz, con ducking.
  - Un efecto de sonido en cada evento visual.
  - −14 LUFS, true peak ≤ −1 dBTP.
- **Final en loop.** Nada de "sígueme" en el video: eso va en el texto del post o en un comentario fijado.

## Pipeline técnico
- **Repo** público `nadieteexplica/reels-ia`:
  - Para generar voz se sube un JSON a `jobs/voz/`. GitHub Actions (`.github/workflows/voz.yml`) corre `tools/eleven.py` con el secreto `ELEVENLABS_API_KEY` y guarda en `out/`.
  - Modos del JSON: `voices` (buscar voces), `compare` (mismo texto con varias voces) y `tts` (locución final con alineación → `out/tts/<id>.mp3` + `<id>.json`).
  - Se espera el resultado con `git fetch` hasta que cambie `origin/main`.
- **Por qué Actions:** ElevenLabs está bloqueado desde el espacio de trabajo de Claude (la red tiene allowlist). GitHub y PyPI/npm sí funcionan.
- **Render actual (`studio/`):**
  - Cada video es una página three.js que expone `window.renderAt(t)` y `window.READY`.
  - `capture.py` (Playwright + SwiftShader) saca los cuadros a 30 fps.
  - `mux.sh` codifica H.264 + AAC con loudnorm −14 LUFS.
  - El audio (efectos y música) se sintetiza en numpy.
  - Instrucciones en `studio/README.md`.
- **Plan para subir calidad:**
  - Pasar a **Blender** (`pip install bpy`, la versión 5.2 está disponible) y renderizar en **GitHub Actions** (gratis en repo público, en paralelo).
  - Assets CC0: Poly Haven, ambientCG, Quaternius.
  - **Mixamo:** Tomás ya tiene la cuenta creada. Va a bajar un personaje (With Skin, con Breathing Idle) y unas 12 animaciones (Without Skin, FBX Binary, 30 fps, keyframe reduction none). Las adjunta en el chat. **No subirlas al repo público:** la licencia no permite redistribuir los archivos sueltos.
- **Publicación:**
  - Metricool `createScheduledPost` necesita una URL pública del video. El plan es hostearlo en el repo.
  - `createScheduledPostForReview` requiere plan de equipo. Con `autoPublish:false` llega una notificación para publicar a mano.
- **vidIQ (plan gratis):** pocos créditos. Ver un video cuesta 10 y una búsqueda de outliers cuesta 5.

## Presupuesto
- **Máximo 10.000 CLP al mes** en total. ElevenLabs Starter ya está pagado.
- La calidad se sube con cosas gratis (Blender, Actions, assets CC0, Mixamo).
- Si se gasta algo: una compra única de un buen personaje protagonista, después de elegir el estilo.
- No gastar en planes de video con IA ni en suscripciones de música.

## Seguridad (obligatorio)
- La API key de ElevenLabs vive **solo** en el secreto del repo. Nunca escribirla, repetirla ni commitearla.
- No crear cuentas ni usar contraseñas por Tomás.
- **Publicar en redes solo con su OK explícito, post por post.**

## Estado actual
- **Ep. 1 — Congelamiento cerebral (helado):**
  - Guion final, voz generada (`out/tts/ep1-helado.mp3`, 55 s) y tiempos por palabra (`studio/ep1-helado/words.json`). Guion y fuentes en `studio/ep1-helado/guion.md`.
  - **Falta animarlo** en el estilo que elija Tomás.
- **Muestras de estilo A/B/C:** renderizadas el 18-oct, en espera de que Tomás elija.
- **Mixamo:** cuenta creada. Falta que baje el personaje y las animaciones.
- **Después:**
  1. Pipeline Blender + Actions.
  2. Hostear el MP4 y programar con Metricool (con su OK).
  3. Tarea programada diaria y skill de producción.

## Documentos
- `docs/investigacion-formatos-virales.md`: investigación de formatos virales originales (qué funciona y por qué).
- `docs/banco-ideas-antiguo.md`: banco de ideas viejo, de la época low-poly. Sirve como lista de temas.
