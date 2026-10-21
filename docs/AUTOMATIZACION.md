# Automatización — cómo funciona la cuenta sola

## Cadencia
| Fase | Videos | Días | Créditos de voz al mes (aprox.) |
|---|---|---|---|
| **Meta de Tomás (19-oct-2026)** | **2 cada 3 días** (~20 al mes) | cada 3 días, en tandas | ~31.000 de 40.000 |
| **Piloto (primeras 4 semanas)** | 3 por semana | lunes, miércoles, viernes | ~20.000 de 40.000 |
| **Crecimiento** (si la calidad se mantiene y Tomás lo pide) | 5 por semana | lunes a viernes | ~34.000 de 40.000 (justo) |
| Diario | 7 por semana | todos | ~47.000: no cabe en Starter, así que **no** |

El cálculo supone ~1.200 créditos por toma y ~1,3 tomas por video.

Se parte con 3 a la semana a propósito. La calidad pesa más que la cantidad, y así hay datos para aprender antes de escalar.

## Fase 0 — Puesta a punto (una vez, en el chat del proyecto)
Antes de trabajar en serie, todo esto tiene que estar hecho y probado:
1. [ ] **Estilo elegido** por Tomás: monito animado (A, B o C) o semi-realista con Blender y Mixamo.
2. [ ] **Plantilla de producción del estilo**:
   - personaje protagonista fijo,
   - escenarios base,
   - biblioteca de expresiones y acciones,
   - sistema de subtítulos,
   - generador de SFX y música.

   Tiene que ser reutilizable: un episodio nuevo solo cambia el guion, el storyboard y los planos especiales.
3. [ ] **Render en GitHub Actions**: un workflow `render.yml` con matriz paralela que toma `studio/episodios/epNN-slug/` y devuelve el MP4 (si usa assets privados, clona `nadieteexplica/assets` con el secreto `TOKEN`). Hay que medir el tiempo por video.
4. [ ] **Hosting del MP4**: probar si Metricool acepta la URL de GitHub Release. Si no, usar `raw.githubusercontent.com` desde `out/videos/`.
5. [x] **Script de QA automático**: `tools/qa.py` con los checks de la sección 9.1 del manual.
5b. [x] **Auditor por etapas** (`docs/AUDITOR.md`, `tools/auditor/`), calibrado a ciegas con las versiones del Ep. 1 (`docs/AUDITOR_CALIBRACION.md`). Listo el 19-oct-2026.
6. [ ] **Decisiones de Tomás** (ver "Decisiones pendientes" en `CONTEXTO.md`): `madeForKids`, (el repo privado `nadieteexplica/assets` con el secreto `TOKEN` ya está listo).
7. [ ] **Metricool:** revisar que el plan de Tomás permita ~39 posts al mes (3 videos × 3 redes × ~4,3 semanas) y la programación vía API. Si no, se le avisa.
8. [ ] **Ep. 1 de punta a punta**:
   - alargar el guion a 62 s o más (sumar un dato, por ejemplo el estudio de Harvard de 2012 o cuánto dura),
   - regenerar la voz,
   - animar, pasar el QA y la revisión independiente,
   - entregarlo y, con OK, programarlo.
9. [x] ~~Tarea programada de producción~~: **eliminada por Tomás el 21-oct-2026**: "yo cuando quiera crear un video lo hago hablando con el chat". La producción es siempre a pedido, en el chat, un video a la vez. (La revisión del jueves, B, sigue siendo opcional: sólo si Tomás la pide.)

Ya hecho: el workflow de voz procesa solo los jobs nuevos de cada push, falla en rojo si hay error y hace rebase antes de guardar. `tools/words.py` arma `words.json`.

## Topes por video (proceso v2, 21-oct-2026 — "NO SE PUEDE VOLVER A REPETIR", Tomás)
El Ep. 2 tomó más de 24 h y ~26 % del uso semanal de Claude de Tomás. Desde el Ep. 3, cada video tiene estos topes (`tools/auditor/presupuesto.json` → `proceso_v2`; la puerta P los revisa):
- **62–65 s** y **máximo 12 escenas** (una escena = una actuación animada que se arma una vez y se filma con varias cámaras; el Ep. 2 armó ~45), **3 a medida como máximo**. Los cortes dentro de una escena son baratos: algo cambia cada 1–2 s y nunca más de 2 s sin cambio. El 12 es un punto de partida: se ajusta con las horas medidas del Ep. 3.
- **2 rondas por puerta** (la 2.ª sólo verifica; con fallas automáticas no se abre ronda), 1 revisor por cada 10 planos + 1 global (en la r2 sólo los planos marcados), **2 animatics** y **1 render final**. **8 h activas** (la puerta P lo mide con la bitácora: huecos de más de 1 h no cuentan). El % de uso de Claude no se puede medir desde la sesión: la puerta P anota revisores lanzados e imágenes revisadas, que es lo que más lo mueve; Tomás puede contar el % real.
- Cada plano pasa `tools/prueba.py` con 0 fallas **antes** del auditor. Lo aprobado no se toca. Un plano que falla dos veces se simplifica o se cambia por una plantilla.
- Si se ve venir que un tope se pasa, se para y se le avisa a Tomás en 2 líneas con opciones (simplificar, cambiar la idea, seguir).

## Cómo se hace un video

### A) Producción de un video — cuando Tomás lo pide en el chat (decisión de Tomás, 21-oct-2026)
No hay tarea programada de producción: Tomás abre el chat y pide el video. Se hace **un video por sesión**.
1. Actualizar el repo y leer los docs, primero `proyecto/INSTRUCCIONES.md` y después `CONTEXTO.md`, **`docs/LECCIONES.md`**, el manual, `IDEAS.md` y `PUBLICADOS.md`.
2. **Métricas:**
   - Bajar de Metricool los datos de los videos de las últimas semanas.
   - Actualizar `PUBLICADOS.md`.
   - Escribir 2–3 aprendizajes en `CONTEXTO.md`.
3. **Ideas:**
   - Buscar según `IDEAS.md` §1.
   - Si Tomás no trae la idea: proponerle 3 con su puntaje (`IDEAS.md` §2: 32 en datos, 25 en historias) y su costo estimado, variadas (distinto gancho, área y formato); él elige.
   - Darle prioridad a las preguntas de la comunidad.
4. **Guiones:** verificar con 2 fuentes, escribir en 181–188 palabras (62–65 s) y guardar en `studio/episodios/epNN-slug/guion.md` (con el puntaje de la idea y para qué acción es). → **Puerta 1 del auditor** (`auditar.py preparar <ep> guion` → `lanzar` → `cerrar`). Sin APROBADO no se genera la voz.
5. **Voz:** un job. Esperar a Actions, revisar `out/status.json`, armar `words.json` con `tools/words.py` y controlar duraciones (62–65 s; si queda corta, `tools/pausas.py`). `asr.yml` transcribe cada voz sola al terminar `voz.yml`. → **Puerta 2** (voz: automática; revisor sólo si la transcripción encuentra diferencias).
6. **Storyboard = fichas de plano** (`studio/plantilla/storyboard.md`): máx. 12 escenas con su plantilla del kit y los cortes que hagan falta dentro de cada una; por plano: acción visible, qué cambia (nunca más de 2 s sin cambio), cámara, dónde va la cara y dónde el gráfico, y `Origen` (render / kling / biblioteca; máx. 3 de Kling). → **Puerta 3**, antes de gastar en cuadros, Kling o render.
7. **Cuadros de estilo** sólo si hay escenario nuevo (si se reutiliza un set del kit, no hay) → **Puerta 4** → recién aprobados se le muestran a Tomás (es el único mensaje intermedio).
8. **Kling:** cuadros de partida con la mano libre → **Puerta 4** (`--nota` con el plano y la acción) → `kling.yml` → **Puerta 5** (8 cuadros por clip) → `kling/planos.json` sólo con clips aprobados.
9. **Animación por plano:** cada plano desde su plantilla → `tools/prueba.py <ep> --planos N` hasta 0 fallas y la hoja mirada. Nada pasa al animatic con fallas del chequeo.
10. **Animatic** (`render-planos.yml`, `res=540x960`, `samples=8`) → el workflow corre el chequeo por plano y sube `chequeo.txt` → **Puerta 6** (`--video`, `--planos`, `--subs`, `--meta`, `--graficos` de la prerelease `epNN-borrador`; 1 revisor por cada 10 planos + 1 global). Se arreglan los bloqueantes y, si es barato, las 5 sugerencias; se re-renderizan sólo esos planos → r2 de verificación (`--cambiados` con esos planos). Máximo 2 rondas; lo que siga fallando se simplifica y lo revisa la puerta 7.
11. **Render final, una sola vez** (720×1280, 16 muestras; GPU de RunPod o Actions) → **Puerta 7** (chequeo + 1 revisor, sólo bloqueantes). Mientras corre cualquier render, **revisar el avance cada 15 min** y dar horas sólo con datos medidos. Todo va a la **bitácora** (`tools/auditor/bitacora.py`).
12. **Paquete:** versión liviana de 720p para el mensaje, `caption.md` (con `madeForKids` no y título de TikTok) y portada → **Puerta 8** (paquete) y **Puerta P** (proceso: bitácora, horas, chequeos, máquinas, gasto, rondas y topes).
13. **Mensaje a Tomás** (sólo con las puertas en APROBADO; la puerta 6 puede quedar cerrada por tope si la 7 aprobó el render final):
    - el video (como archivo),
    - una línea del auditor: rondas que necesitó y qué se arregló (el `veredicto.md` queda en el repo),
    - gancho, horario propuesto por red (`docs/HORARIOS.md` y Metricool) y texto de cada post,
    - la pregunta: "¿OK para programarlo?".
14. **Programar:** con OK, `release.yml` copia el MP4 al Release `epNN`; `auditar.py preparar <ep> paquete --url <URL>` comprueba que la URL responde; recién ahí se crean los posts programados en Metricool (en las 3 redes; TikTok exige `tiktokData.title`) y anotarlos en `PUBLICADOS.md`. Después de la hora, confirmar en Metricool que quedaron "Published".
    - **El OK se da en esta misma sesión. Sin OK no se programa nada.**
    - Si Tomás responde tarde, el video se programa desde el siguiente horario bueno, con al menos 1 día de separación con el video anterior.
15. Anotar en `docs/LECCIONES.md` cualquier error nuevo con su regla; si fue un error que el auditor dejó pasar, ajustar su prompt o chequeo y volver a calibrar (`docs/AUDITOR.md` → Mantenimiento). Hacer commit y push de todo (incluidos los `veredicto.*` de cada puerta).

### B) Revisión de métricas (opcional, sólo si Tomás la pide) — jueves ~18:50
- Métricas tempranas de los videos de lunes y miércoles.
- Leer los comentarios y pasar las preguntas buenas a `IDEAS.md` §5.
- Si un video rompió el promedio (2× o más), anotar qué tuvo de distinto.
- Si hay videos de la semana esperando su OK, recordárselo en una línea.
- Mensaje corto a Tomás solo si hay algo relevante. Si no hay nada, no se manda nada.

### C) Reporte mensual — cuando Tomás lo pida
Cinco líneas para Tomás:
- crecimiento de seguidores,
- top 3 videos y por qué,
- qué se ajusta en el puntaje de ideas,
- créditos de voz usados,
- recomendación (seguir igual, subir a 5 por semana o cambiar algo).

## Prompt de la revisión de métricas (si Tomás la pide como tarea programada)
(La producción no es tarea programada: la pide Tomás en el chat.)

**Tarea B — "Nadie te explica · revisión jueves"** (jueves 18:52, CRON_TZ=America/Santiago)
```
Clona github.com/nadieteexplica/reels-ia. Lee primero proyecto/INSTRUCCIONES.md (Seguridad y Publicación mandan), después CONTEXTO.md y docs/AUTOMATIZACION.md. Ejecuta "B) Revisión de mitad de semana": métricas tempranas en Metricool, comentarios con preguntas → docs/IDEAS.md §5, y anota los outliers en docs/PUBLICADOS.md. Haz push. Escríbele a Tomás solo si hay algo relevante, en 3 líneas como máximo.
```

## Manejo de fallas
| Falla | Qué hacer |
|---|---|
| Actions falla (voz o render): workflow en rojo o `error` en `out/status.json` | Reintentar 2 veces (con `workflow_dispatch`, sin crear jobs nuevos). Si sigue, avisar en 1 línea con la causa y la propuesta |
| Créditos de ElevenLabs bajo 8.000 | Avisar a Tomás y bajar a 2 videos esa semana |
| Un video no pasa una puerta en 2 rondas | Lo que sigue fallando se simplifica o se cambia por una plantilla (sin otra ronda); si igual no llega, entregar 2 videos y explicar. Nunca mandar uno malo |
| Un video va a pasar el tope de 8 h activas | Parar y avisar a Tomás en 2 líneas con opciones (simplificar, cambiar la idea, seguir) |
| Un revisor del auditor se corta (Tomás escribió a mitad de turno, error) | `auditar.py estado` muestra qué encargo falta; `lanzar` da el texto para relanzarlo. No se pierde nada: cada encargo escribe su resultado una sola vez al final |
| Se cree que el auditor se equivocó | Nunca se edita un veredicto. Se corrige el prompt o el chequeo, se anota en `LECCIONES.md` y se corre una ronda nueva |
| Metricool rechaza la URL o el post | Probar el hosting alternativo y avisar |
| vidIQ sin créditos | Seguir con la web y los comentarios. vidIQ no es imprescindible |
| Duda sobre un dato | El tema no sale hasta tener 2 fuentes. Se cambia por otro del banco |
| Un trabajo en paralelo se cae o no avanza | Se detecta en la revisión de cada 15 min; se relanza en Actions/RunPod (no en subagentes) y se avisa a Tomás en 1 línea |
| Kling rechaza un clip ("risk control") o el clip deforma algo | Reescribir la instrucción sin palabras de dolor/violencia o cambiar el cuadro de partida; máx. 2 intentos, si no el plano se hace sin objeto en la mano |
| RunPod sin stock o error al crear el pod | El workflow prueba secure y otras GPU; si igual falla, render en Actions (16 partes) |
| Unidades de Kling bajo 15 | Avisar a Tomás: usar solo la biblioteca de reacciones hasta que decida si compra más |
