# Nadie te explica — contexto del proyecto

Leer esto entero antes de trabajar, junto con `proyecto/INSTRUCCIONES.md`: sus secciones *Seguridad* y *Publicación* mandan sobre todo. Es la fuente de verdad de lo decidido hasta ahora (18-oct-2026).

## La cuenta
- **Nombre:** Nadie te explica. Cuenta faceless de videos cortos hechos con Claude.
- **Redes:** Instagram `nadie_te_explica` · TikTok "Nadie te explica" · YouTube Shorts (canal `UCFvRAW_exW4MgXEwQqCD1Fw`).
- **Metricool:** brand id `7499838`, zona horaria America/Santiago. Ya están conectadas las tres redes.
- **Dueño:** Tomás (Santiago, Chile). Habla en español chileno casual y directo, y quiere respuestas cortas.
- **Meta: automatización total.** Claude investiga qué subir, escribe el guion, genera la voz, anima, deja todo listo, publica **3 veces por semana** (lun/mié/vie) vía Metricool con el OK de Tomás por post, y revisa los datos.

## Formato (brief vigente)
- **Temas de todo el mundo**, no solo animales. Los ganchos son:
  - "¿Qué pasaría si…?"
  - "¿Cómo funciona por dentro?"
  - "¿Por qué no podemos…?"
  - "¿Qué pasa dentro de…?"
  - "¿Sabías que…?"
- **Un dato impresionante** por video, de **62–75 s**, que **termina enseñando algo**. TikTok solo paga videos de más de 1 minuto, con 10 mil seguidores y 100 mil vistas en 30 días.
- **Cadencia:** se parte con **3 videos por semana** (lunes, miércoles y viernes) y se sube a 5 si la calidad se mantiene. Diario no cabe en los créditos de voz. Detalle en `docs/AUTOMATIZACION.md`.
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
  - **DECIDIDO (18-oct-2026):** semi-realista con Mixamo y **personaje propio de cuerpo normal**, hombre joven de ~18–20 años, con el look del niño de las muestras (polera coral con estrella, pelo café en mechones). Se descartó el cabezón: las animaciones de Mixamo son captura de movimiento real y en cabezones las manos atraviesan la cabeza. Las reacciones van en primer plano para que la cara se lea en vertical.
  - Base del personaje: MakeHuman (CC0), armado en Blender. Las muestras A/B/C quedan como referencia histórica.

## Voz
- **ElevenLabs**, plan Starter (pagado), con **40.000 créditos al mes**. Cada toma gasta unos 1.200 créditos (hay que presupuestar ~1,3 tomas por video), y el saldo se ve en `out/status.json`.
- La voz elegida es **Fernando Martínez**: `voice_id dlGxemPxFMTY7iXagmOj`. Habla a unas 2,97 palabras por segundo.
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
  - Una o dos líneas, con la caja dentro de **x 120–888 · y 1000–1250**. Fuente de 76–88 px, que baja hasta 60 px si una palabra larga no cabe. Nunca en el 35% inferior.
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

## Estado actual (18-oct-2026)
**Fase actual: 0, puesta a punto.** Ver la checklist en `docs/AUTOMATIZACION.md`.

- **Estilo decidido:** semi-realista con Mixamo y personaje propio (ver "Formato").
- **Protagonista (borrador 1, aprobado en dirección por Tomás):** `studio/personaje/` (ver su README).
  - Base MakeHuman CC0, hombre joven, 1,77 m, polera coral con estrella amarilla, jeans, zapatillas blancas, pelo café corto con jopo.
  - Riggeado por Claude con esqueleto `mixamorig:*`: las FBX de Mixamo se aplican directo (no hay que subir nada a Mixamo).
  - 34 shape keys de expresión (párpados, cejas, boca).
  - Cabeza y cuello de Mixamo suavizados un 30 % (la captura exagera; Tomás notó el cuello torcido).
  - Render de prueba en el workspace: ~9 s por cuadro a 405×720 con 12 muestras (2 núcleos). El render final va a Actions.
  - Pendiente: piel menos plástica, bordes de manga, mirada, sincronía de boca, contacto mano–cara (`Thinking` no llega al mentón).
- **Mixamo:** 14 FBX en los archivos del proyecto de Claude (no en el repo). `Talking` bajó la versión **sentado**: falta "General Conversation" (de pie). `Drinking` está repetida.
- **Muestras de estilo A/B/C** (`studio/muestras/`): históricas, ya no se usan.
- **Ep. 1 — Congelamiento cerebral (helado):**
  - Guion, voz (`out/tts/ep1-helado.mp3`, id antiguo `ep1-helado`) y tiempos (`studio/episodios/ep01-congelamiento-cerebral/words.json`) listos. Guion y fuentes en `studio/episodios/ep01-congelamiento-cerebral/guion.md`.
  - **Dura 55 s:** hay que alargarlo a 62 s o más (sumar un dato) y regenerar la voz.
  - Falta animarlo en el estilo elegido.
- **Mixamo (referencia):**
  - **Dónde van las FBX:** al repo **privado** `nadieteexplica/assets`, que crea Tomás en la Fase 0. El render los clona con el secreto `ASSETS_TOKEN`. Nunca van al repo público.
  - Configuración: FBX Binary, 30 fps, keyframe reduction none, y "In Place" marcado cuando exista.
  - **Animaciones en Without Skin** (elegidas mirando el catálogo el 18-oct; nombre de búsqueda → descripción en Mixamo):
    - Ep. 1 y base de la biblioteca:
      - `Drinking` → "Male Drinking" (se lleva el helado a la boca; también "toma algo tibio"),
      - `Focus` → "Shake Off Head Pain And Focus" (manos a la cabeza: el "¡zas!"),
      - `Thinking` → "Thinking While Standing",
      - `Shrugging` → "Shoulder Shrug",
      - `Arm Gesture` → "Gesturing With Arm To The Side" (presenta el corte de la cabeza),
      - `Pointing` → "Pointing With Arm Bent",
      - `Talking` → "General Conversation" y "Asking A Question With Two Hands",
      - `Surprised` → "Finding Something And Wiggling Fingers" ("y lo más loco"),
      - `Head Nod Yes` → "Nodding Head Yes" ("sí, en serio"),
      - `Relieved Sigh` → "Sighing In Relief" (cuando se pasa el dolor),
      - `Shaking Head No` → "Shaking Head No Dismissively",
      - `Laughing` → "Laughing Standing" (cierre),
      - `Happy Idle` → "Happy Idle Variation 1" (entre planos).
    - Para otros episodios: `Terrified` ("Being Terrified While Standing") y `Excited` ("Super Excited").
    - Descartadas: `Agony` (demasiado dramática).
- **Próximos pasos:**
  1. Pulir el protagonista (piel, mangas, mirada, boca).
  2. Plantilla de producción (escenarios, biblioteca de acciones y expresiones, subtítulos, SFX y música).
  3. Render en Actions (necesita el repo privado de assets para las FBX).
  4. Hosting y prueba con Metricool.
  5. Ep. 1 de punta a punta (alargar a 62 s o más y regenerar la voz).
  6. Tareas programadas (A: domingo de producción; B: jueves de revisión).

## Decisiones pendientes de Tomás
1. ~~Estilo~~: decidido el 18-oct (semi-realista con Mixamo, personaje propio de cuerpo normal, ~18–20 años).
2. **Audiencia de YouTube (`madeForKids`):** se recomienda **no**, porque el contenido es de curiosidades para público general, aunque el protagonista sea un niño. La decisión es de Tomás.
3. Si va Mixamo: crear el repo **privado** `nadieteexplica/assets` y un token de solo lectura como secreto `ASSETS_TOKEN` en `reels-ia`. Claude le da los pasos.

## Aprendizajes
(Se llenan con los datos de cada semana. Ver `docs/PUBLICADOS.md`.)

## Documentos
- `proyecto/INSTRUCCIONES.md`: instrucciones del proyecto en Claude.
- `docs/MANUAL_PRODUCCION.md`: estándar de cada video (guion, verificación, voz, storyboard, look, subtítulos, audio, render, QA, entrega, publicación).
- `docs/AUTOMATIZACION.md`: cadencia, fases, ciclo semanal, prompts de las tareas programadas y manejo de fallas.
- `docs/IDEAS.md`: dónde buscar, puntaje, lista negra y banco de unas 40 ideas.
- `docs/PUBLICADOS.md`: registro de videos y métricas.
- `docs/REFERENCIAS.md`: estudio de videos virales de referencia (por qué funcionan, qué tomar, qué tan alcanzable). Documento vivo.
- `docs/investigacion-formatos-virales.md`: investigación de formatos virales. **Es histórica**: sus datos de plataformas sirven, pero sus propuestas (noticiero low-poly, publicar diario) **no están vigentes**.
- `docs/banco-ideas-antiguo.md`: banco viejo, de la época low-poly.
