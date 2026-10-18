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
  - Tomás aún no elige.

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

- **Muestras de estilo A/B/C** (`studio/muestras/`):
  - Renderizadas y entregadas a Tomás. Él todavía no elige.
  - Tiempos de render en el workspace (2 procesos en paralelo):
    - A: ~9 s por cuadro.
    - B: ~3 s por cuadro.
    - C (a 12 fps): ~8 s por cuadro.
  - Todas tienen el mismo personaje: niño con polera coral y estrella, pelo café en mechones, ojos grandes, cara pintada (boca, mejillas) y efecto de congelamiento azul.
- **Ep. 1 — Congelamiento cerebral (helado):**
  - Guion, voz (`out/tts/ep1-helado.mp3`, id antiguo `ep1-helado`) y tiempos (`studio/episodios/ep01-congelamiento-cerebral/words.json`) listos. Guion y fuentes en `studio/episodios/ep01-congelamiento-cerebral/guion.md`.
  - **Dura 55 s:** hay que alargarlo a 62 s o más (sumar un dato) y regenerar la voz.
  - Falta animarlo en el estilo elegido.
- **Mixamo:** cuenta creada. Falta que Tomás baje el personaje y las animaciones, y las adjunte en el chat.
  - **Dónde van:** al repo **privado** `nadieteexplica/assets`, que crea Tomás en la Fase 0. El render los clona con el secreto `ASSETS_TOKEN`. Nunca van al repo público.
  - Configuración: FBX Binary, 30 fps, keyframe reduction none, y "In Place" marcado cuando exista.
  - **Personaje:** joven o niño con ropa casual, con la animación `Breathing Idle` en **With Skin**.
  - **Animaciones en Without Skin:**
    - `Talking` (2–3),
    - `Surprised`,
    - `Terrified`,
    - `Thinking`,
    - `Pointing`,
    - `Drinking` (sirve para llevarse algo a la boca),
    - `Shaking Head No`,
    - `Head Nod Yes`,
    - `Excited`,
    - `Shrugging`,
    - alguna con las manos en la cabeza (buscar `head`),
    - `Happy Idle`.
- **Próximos pasos:**
  1. Que Tomás elija el estilo.
  2. Plantilla de producción.
  3. Render en Actions.
  4. Hosting y prueba con Metricool.
  5. Ep. 1 de punta a punta.
  6. Tareas programadas (A: domingo de producción; B: jueves de revisión).

## Decisiones pendientes de Tomás
1. **Estilo:** A, B o C del monito, o semi-realista con Mixamo.
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
- `docs/investigacion-formatos-virales.md`: investigación de formatos virales. **Es histórica**: sus datos de plataformas sirven, pero sus propuestas (noticiero low-poly, publicar diario) **no están vigentes**.
- `docs/banco-ideas-antiguo.md`: banco viejo, de la época low-poly.
