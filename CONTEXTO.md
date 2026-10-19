# Nadie te explica — contexto del proyecto

Leer esto entero antes de trabajar, junto con `proyecto/INSTRUCCIONES.md`: sus secciones *Seguridad* y *Publicación* mandan sobre todo. Es la fuente de verdad de lo decidido hasta ahora (18-oct-2026).

## La cuenta
- **Nombre:** Nadie te explica. Cuenta faceless de videos cortos hechos con Claude.
- **Redes:** Instagram `nadie_te_explica` · TikTok "Nadie te explica" · YouTube Shorts (canal `UCFvRAW_exW4MgXEwQqCD1Fw`).
- **Metricool:** brand id `7499838`, zona horaria America/Santiago. Ya están conectadas las tres redes.
- **Dueño:** Tomás (Santiago, Chile). Habla en español chileno casual y directo, y quiere respuestas cortas.
- **Meta: automatización total.** Claude investiga qué subir, escribe el guion, genera la voz, anima, deja todo listo, publica **3 veces por semana** (lun/mié/vie) vía Metricool con el OK de Tomás por post, y revisa los datos.

## Formato (brief vigente)
- **Dos líneas de contenido (decidido por Tomás, 18-oct-2026):**
  - **Datos:** un dato impresionante por video, que termina enseñando algo, con fuentes. Usa los ganchos de abajo.
  - **Historias:** ficción (inventadas, absurdas o sin sentido: fábulas, story time). Si sale un híbrido historia + dato de forma natural, bien, pero no es requisito.
  - La proporción entre líneas está pendiente (ver "Decisiones pendientes").
- **Temas de todo el mundo**, no solo animales. Los ganchos de la línea datos son:
  - "¿Qué pasaría si…?"
  - "¿Cómo funciona por dentro?"
  - "¿Por qué no podemos…?"
  - "¿Qué pasa dentro de…?"
  - "¿Sabías que…?"
- **Formatos candidatos** (del estudio de referencias, sin probar todavía; fichas en `docs/REFERENCIAS.md` §5): corte que se transforma, objeto cotidiano "parece un error, pero es a propósito", "lo conté yo" con datos propios, concepto armado frente a ti, megaproyecto absurdo + "lo calculé", fábula absurda y story time.
- **Duración: 62–75 s** en las dos líneas. TikTok solo paga videos de más de 1 minuto, con 10 mil seguidores y 100 mil vistas en 30 días.
- **Cadencia:** se parte con **3 videos por semana** (lunes, miércoles y viernes) y se sube a 5 si la calidad se mantiene. Diario no cabe en los créditos de voz. Detalle en `docs/AUTOMATIZACION.md`.
- **Lo que se presenta como real es real y verificado**, con fuentes. Nada de desinformar. La ficción de la línea historias puede ser todo lo loca que se quiera, pero no se disfraza de dato.
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
- **Referencias de look** (fichas en `docs/REFERENCIAS.md`; son referencias de calidad, nunca de marca):
  - **R4** (el clavo, Zack D. Films): escenas con personajes. Paredes celestes, luz suave de estudio y ropa en pastel saturado.
  - **R3** (la caverna): momentos dramáticos. Una sola fuente de luz fuerte y cálida, sombras profundas y contraluz.
  - **R8** (gancho del metro): objetos en primer plano. Render tipo producto, fondo oscuro cálido con partículas desenfocadas.

## Voz
- **ElevenLabs**, plan Starter (pagado), con **40.000 créditos al mes**. Cada toma gasta unos 1.200 créditos (hay que presupuestar ~1,3 tomas por video), y el saldo se ve en `out/status.json`.
- La voz elegida es **Fernando Martínez**: `voice_id dlGxemPxFMTY7iXagmOj`. Habla a unas 2,97 palabras por segundo.
- Modelo `eleven_multilingual_v2`.
- Settings: stability 0.4, similarity 0.8, style 0.32, speaker boost activado.
- Se genera **con timestamps por carácter** para armar subtítulos palabra por palabra.

## Reglas de edición (del estudio de formatos virales y de `docs/REFERENCIAS.md`)
- **Gancho** en los primeros 0–2 s. El cuadro 0 es una imagen absurda o una pregunta: algo que todavía no tiene sentido.
- **Planos:**
  - Una idea por plano, de 1,2–2,5 s cada uno.
  - **Nunca más de 2 s sin un cambio en pantalla:** un corte, o algo que aparece o se transforma dentro del cuadro. Con transformación continua un plano puede durar más.
  - Cortes secos sincronizados con la voz.
  - La cámara siempre se mueve (acercamientos lentos u órbitas).
  - Cambio de escala cada 8–12 s.
- **Look:** fondos vivos (celeste/turquesa), luz suave de estudio, colores saturados. Nunca sobreexpuesto. Con encuadre vertical se deja aire: la cara del personaje va en el tercio superior.
- **Subtítulos:**
  - Palabra por palabra, de 1 a 3 palabras a la vez, en mayúsculas gruesas.
  - Blancos con borde negro, y la palabra activa en amarillo (#FFD23F).
  - Una o dos líneas, con la caja dentro de **x 120–888 · y 1000–1250**. Fuente de 76–88 px, que baja hasta 60 px si una palabra larga no cabe. Nunca en el 35% inferior.
  - **Palabra clave** (1–3 por video: la cifra, el objeto, el giro) en el color de su idea y un poco más grande.
  - **Excepción:** si el protagonista del plano es un objeto centrado, los subtítulos pueden ir arriba (y 280–480).
- **Llamados en pantalla:** mínimos (flechas finas, etiquetas tipo píldora). Sin logo encima.
- **Código de color fijo:** un color por idea u opción (correcto/incorrecto, opción A/B/C), igual en objetos, gráficos y subtítulos.
- **Símbolo que se repite:** un objeto o detalle que vuelve durante el video y sirve de portada.
- **Audio:**
  - Música 15–20 dB bajo la voz, con ducking.
  - Un efecto de sonido en cada evento visual.
  - −14 LUFS, true peak ≤ −1 dBTP.
- **Final en loop.** Nada de "sígueme" en el video: eso va en el texto del post o en un comentario fijado.
- **En prueba:** cierre que pide el envío con destinatario concreto ("mándaselo a ese amigo que…"). Se usa en algunos videos y se compara en `PUBLICADOS.md`.

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
- **Tope: 10.000 CLP al mes.** ElevenLabs Starter ya está pagado.
- **Octubre 2026 (excepción aprobada por Tomás el 19-oct):** compró el paquete Trial de la **API de Kling** (USD 9,80 = 100 unidades, vence a los 30 días) y cargó **USD 10 en RunPod** (sin Auto-Pay). ~19.400 CLP extra este mes.
  - Kling: 4 unidades por clip de 5 s a 1080p. Después del Trial, el paquete oficial más barato cuesta USD 700: si se sigue usando, hay que evaluar un intermediario con pago por clip (decisión de Tomás).
  - RunPod: ~USD 0,22–0,30 la hora (RTX A5000/A4000, community/secure); un video completo ~USD 0,3–0,5.
- Gratis primero: Blender, Actions, assets CC0, Mixamo. Toda compra nueva se pregunta antes con el monto en CLP.

## Seguridad (obligatorio)
- La API key de ElevenLabs vive **solo** en el secreto del repo. Nunca escribirla, repetirla ni commitearla.
- No crear cuentas ni usar contraseñas por Tomás.
- **Publicar en redes solo con su OK explícito, post por post.**

## Estado actual (19-oct-2026, noche)
**Fase actual: 0, puesta a punto.** Ver la checklist en `docs/AUTOMATIZACION.md`.

- **Estilo decidido:** semi-realista con Mixamo y personaje propio (ver "Formato").
- **Auditor por etapas listo (19-oct):** `docs/AUDITOR.md` + `tools/auditor/`. Corre como subagentes (gratis), umbral 8 + bloqueantes, máx. 3 rondas, y a Tomás le llegan sólo los cuadros de estilo nuevos y el video final ya aprobados. Calibrado a ciegas con las versiones viejas del Ep. 1: detecta 20 de 22 errores conocidos (`docs/AUDITOR_CALIBRACION.md`). Desde el Ep. 2 es obligatorio, junto con la bitácora del proceso.
- **Interior del cuerpo ("cabeza de vidrio"), aprobado por Tomás el 19-oct:** perfil fijo, fondo azul noche, anatomía real de Z-Anatomy; se ve y brilla sólo lo que nombra la voz. Reglas en el manual §8.
- **Manos con objetos y reacciones → Kling** (API oficial, secreto `KILING_SECRET`, workflow `kling.yml`). En Blender los dedos flotaban; Tomás lo rechazó dos veces. Kling parte de cuadros nuestros y no se usa para anatomía.
- **Render en GPU → RunPod** (secreto `RUNPOD_API_KEY`, workflow `render-gpu.yml`). Probado el 19-oct: RTX A5000, ~1,4 s por cuadro a 720p/16 muestras, el pod se borra solo.
- **Proceso (desde el 19-oct):** cada etapa pasa una puerta del **auditor** (`docs/AUDITOR.md`) antes de avanzar: guion → voz → storyboard → cuadros (los de estilo nuevos van a Tomás ya aprobados) → Kling → render → video final → paquete, más el proceso (bitácora). A Tomás le llegan sólo los cuadros de estilo de escenarios nuevos y el video final, los dos con APROBADO. Claude revisa su trabajo antes de mostrarlo y vigila cada 15 min lo que corre en paralelo (el 19-oct dos trabajos en paralelo murieron una hora sin que nadie lo notara).
- **Estudio de referencias virales:** `docs/REFERENCIAS.md` (Tomás sigue mandando videos).
- **Protagonista:** `studio/personaje/` (MakeHuman CC0 + esqueleto `mixamorig:*`, 34 shape keys de expresión).
- **Ep. 1 — Congelamiento cerebral (helado):** guion v2 con fuentes, voz de 71,7 s, escena `escena/build_ep01.py`, post `escena/post.py`, audio `escena/audio.py`, clips de Kling en `kling/`, textos en `entrega/caption.md`. Estado de la entrega: ver el final de esta sección.
- **Mixamo (referencia):**
  - **Dónde van las FBX:** repo **privado** `nadieteexplica/assets`, carpeta `mixamo/`. El render los clona con el secreto `TOKEN` (token fino "render" de la organización, solo lectura de ese repo, vence el 17-nov-2026: hay que renovarlo). Nunca van al repo público.
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
- **Ep. 1 publicado** el 19-oct-2026 a las 16:35 en Instagram, TikTok y YouTube (links en `docs/PUBLICADOS.md`). Métricas a las 48 h (21-oct) y a los 7 días (26-oct).
- **Próximos pasos:**
  1. ~~Auditor por etapas~~: listo el 19-oct (`docs/AUDITOR.md`, `tools/auditor/`, calibración en `docs/AUDITOR_CALIBRACION.md`).
  2. Biblioteca de reacciones del protagonista con Kling (una vez; después se reusa sin gastar unidades).
  3. RunPod con 2–3 pods en paralelo (video completo en ~20–30 min).
  4. Ep. 2 con el proceso nuevo: guion pensado para 2–3 planos de Kling como máximo, storyboard con columna `Origen`, cuadros de estilo, render en GPU y las 8 puertas del auditor con bitácora desde el primer minuto.
  5. Tareas programadas (A: producción; B: revisión del jueves) cuando el Ep. 2 salga sin intervención.

## Decisiones pendientes de Tomás
1. ~~Estilo~~: decidido el 18-oct (semi-realista con Mixamo, personaje propio de cuerpo normal, ~18–20 años).
2. ~~Audiencia de YouTube (`madeForKids`)~~: decidido el 19-oct → **no es para niños**.
3. ~~Repo privado de assets y token~~: listo el 18-oct (`nadieteexplica/assets` + secreto `TOKEN`). **Renovar el token antes del 17-nov-2026.**
4. **Proporción datos/historias.** Propuesta de Claude: ~2 de datos por cada historia en el piloto; a las 4 semanas se ajusta según envíos/alcance de cada línea.

## Aprendizajes
(Se llenan con los datos de cada semana. Ver `docs/PUBLICADOS.md`.)
- Antes de publicar, los aprendizajes vienen de videos ajenos: `docs/REFERENCIAS.md` §3. Se confirman o se descartan con nuestros datos.
- **Errores de producción y sus reglas: `docs/LECCIONES.md`** (se lee antes de cada video). Del Ep. 1: interior "cabeza de vidrio" con un solo foco; manos con objetos → Kling partiendo con la mano libre; nunca mostrarle nada a Tomás sin revisión propia; horas solo con datos medidos; revisar cada 15 min lo que corre en paralelo.

## Documentos
- `proyecto/INSTRUCCIONES.md`: instrucciones del proyecto en Claude.
- `docs/LECCIONES.md`: errores de producción, cómo se solucionaron y la regla que queda (leer antes de cada video).
- `docs/AUDITOR.md`: el auditor independiente por etapas (puertas, chequeos, bloqueantes, formato del veredicto, bitácora del proceso). Código y prompts en `tools/auditor/`.
- `docs/AUDITOR_CALIBRACION.md`: el auditor corrido a ciegas sobre las versiones del Ep. 1 y qué errores detectó.
- `docs/MANUAL_PRODUCCION.md`: estándar de cada video (guion, verificación, voz, storyboard, look, subtítulos, audio, render, QA, entrega, publicación).
- `docs/AUTOMATIZACION.md`: cadencia, fases, ciclo semanal, prompts de las tareas programadas y manejo de fallas.
- `docs/IDEAS.md`: dónde buscar, puntaje, lista negra y banco de ideas.
- `docs/CAZA_DATOS.md`: método del chat de caza de datos (qué buscamos, familias, métodos, dónde verificar, datos quemados, ángulos y gustos de Tomás).
- `docs/PUBLICADOS.md`: registro de videos y métricas.
- `docs/REFERENCIAS.md`: estudio de videos virales de referencia (por qué funcionan, qué tomar, qué tan alcanzable). Documento vivo.
- `docs/investigacion-formatos-virales.md`: investigación de formatos virales. **Es histórica**: sus datos de plataformas sirven, pero sus propuestas (noticiero low-poly, publicar diario) **no están vigentes**.
- `docs/banco-ideas-antiguo.md`: banco viejo, de la época low-poly.
