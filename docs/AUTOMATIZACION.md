# Automatización — cómo funciona la cuenta sola

## Cadencia
| Fase | Videos | Días | Créditos de voz al mes (aprox.) |
|---|---|---|---|
| **Piloto (primeras 4 semanas)** | 3 por semana | lunes, miércoles, viernes | ~20.000 de 40.000 |
| **Crecimiento** (si la calidad se mantiene y Tomás lo pide) | 5 por semana | lunes a viernes | ~34.000 de 40.000 (justo) |
| Diario | 7 por semana | todos | ~47.000: no cabe en Starter, así que **no** |

El cálculo supone ~1.200 créditos por toma y ~1,3 tomas por video.

Se parte con 3 a la semana a propósito. La calidad pesa más que la cantidad, y así hay datos para aprender antes de escalar.

## Fase 0 — Puesta a punto (una vez, en el chat del proyecto)
Antes de encender las tareas programadas, todo esto tiene que estar hecho y probado:
1. [ ] **Estilo elegido** por Tomás: monito animado (A, B o C) o semi-realista con Blender y Mixamo.
2. [ ] **Plantilla de producción del estilo**:
   - personaje protagonista fijo,
   - escenarios base,
   - biblioteca de expresiones y acciones,
   - sistema de subtítulos,
   - generador de SFX y música.

   Tiene que ser reutilizable: un episodio nuevo solo cambia el guion, el storyboard y los planos especiales.
3. [ ] **Render en GitHub Actions**: un workflow `render.yml` con matriz paralela que toma `studio/episodios/epNN-slug/` y devuelve el MP4 (si usa assets privados, clona `nadieteexplica/assets` con `ASSETS_TOKEN`). Hay que medir el tiempo por video.
4. [ ] **Hosting del MP4**: probar si Metricool acepta la URL de GitHub Release. Si no, usar `raw.githubusercontent.com` desde `out/videos/`.
5. [ ] **Script de QA automático**: `tools/qa.py` con los checks de la sección 9.1 del manual.
6. [ ] **Decisiones de Tomás** (ver "Decisiones pendientes" en `CONTEXTO.md`): `madeForKids`, y el repo privado `nadieteexplica/assets` con el secreto `ASSETS_TOKEN` si se usa Mixamo.
7. [ ] **Metricool:** revisar que el plan de Tomás permita ~39 posts al mes (3 videos × 3 redes × ~4,3 semanas) y la programación vía API. Si no, se le avisa.
8. [ ] **Ep. 1 de punta a punta**:
   - alargar el guion a 62 s o más (sumar un dato, por ejemplo el estudio de Harvard de 2012 o cuánto dura),
   - regenerar la voz,
   - animar, pasar el QA y la revisión independiente,
   - entregarlo y, con OK, programarlo.
9. [ ] **Crear las tareas programadas** de abajo, recién con todo lo anterior funcionando.

Ya hecho: el workflow de voz procesa solo los jobs nuevos de cada push, falla en rojo si hay error y hace rebase antes de guardar. `tools/words.py` arma `words.json`.

## Ciclo semanal (tareas programadas)

### A) Producción semanal — domingo ~09:50 (America/Santiago)
1. Actualizar el repo y leer los docs, primero `proyecto/INSTRUCCIONES.md` y después `CONTEXTO.md`, el manual, `IDEAS.md` y `PUBLICADOS.md`.
2. **Métricas:**
   - Bajar de Metricool los datos de los videos de las últimas semanas.
   - Actualizar `PUBLICADOS.md`.
   - Escribir 2–3 aprendizajes en `CONTEXTO.md`.
3. **Ideas:**
   - Buscar según `IDEAS.md` §1.
   - Puntuar y elegir **3 temas** con 32 puntos o más, variados (distinto gancho y distinta área).
   - Darle prioridad a las preguntas de la comunidad.
4. **Guiones:** verificar con 2 fuentes, escribir en 190–215 palabras y guardar en `studio/episodios/epNN-slug/guion.md`.
5. **Voces:** 3 jobs en un solo push. Esperar a Actions, revisar `out/status.json`, armar `words.json` con `tools/words.py` y controlar duraciones (62–75 s).
6. **Storyboards:** uno por episodio.
7. **Animación y render:** con la plantilla del estilo, en Actions.
8. **QA:** automático, visual y revisión independiente (8 o más en todo). Se corrige hasta 3 rondas; si no pasa, ese video se cambia o se entregan 2.
9. **Paquete:** MP4 con URL pública, `caption.md` y portada.
10. **Un solo mensaje a Tomás:**
    - los 3 videos (como archivos),
    - para cada uno: gancho, horario propuesto (mejor hora de Metricool por red) y texto del post,
    - la pregunta: "¿OK a los 3? (o dime cuál no)".
11. **Programar:** con OK, crear los posts programados en Metricool (lun, mié y vie, en las 3 redes) y anotarlos en `PUBLICADOS.md`.
    - **El OK se da en esta misma sesión. Sin OK no se programa nada.**
    - Si Tomás responde tarde, los videos se programan desde el siguiente día hábil, manteniendo la separación de 1 día entre posts.
    - Si no responde, la revisión del jueves se lo recuerda en una línea. Los videos sin publicar quedan para la semana siguiente y esa semana se producen menos videos nuevos.
12. Hacer commit y push de todo.

### B) Revisión de mitad de semana — jueves ~18:50
- Métricas tempranas de los videos de lunes y miércoles.
- Leer los comentarios y pasar las preguntas buenas a `IDEAS.md` §5.
- Si un video rompió el promedio (2× o más), anotar qué tuvo de distinto.
- Si hay videos de la semana esperando su OK, recordárselo en una línea.
- Mensaje corto a Tomás solo si hay algo relevante. Si no hay nada, no se manda nada.

### C) Reporte mensual — primer domingo del mes (dentro de la tarea A)
Cinco líneas para Tomás:
- crecimiento de seguidores,
- top 3 videos y por qué,
- qué se ajusta en el puntaje de ideas,
- créditos de voz usados,
- recomendación (seguir igual, subir a 5 por semana o cambiar algo).

## Prompts listos para crear las tareas programadas
(Se crean al final de la Fase 0. Cada ejecución parte en una sesión nueva, por eso cada prompt es autosuficiente.)

**Tarea A — "Nadie te explica · producción semanal"** (domingo 09:52, CRON_TZ=America/Santiago)
```
Eres el productor de la cuenta "Nadie te explica". Clona github.com/nadieteexplica/reels-ia. Lee primero proyecto/INSTRUCCIONES.md: sus secciones Seguridad y Publicación mandan sobre todo. Después lee CONTEXTO.md, docs/MANUAL_PRODUCCION.md, docs/AUTOMATIZACION.md, docs/IDEAS.md y docs/PUBLICADOS.md. Ejecuta el "Ciclo semanal A) Producción semanal" de AUTOMATIZACION.md completo: métricas → 3 ideas → guiones verificados → voces → storyboards → animación y render → QA con revisión independiente → paquete. Mándale a Tomás un solo mensaje con los 3 videos y los textos, y pídele OK. Solo con su OK explícito programa los posts en Metricool. Nunca programes un post sin el OK explícito de Tomás en esta sesión. Al final actualiza CONTEXTO.md, IDEAS.md y PUBLICADOS.md y haz push. Háblale en español chileno, corto y directo.
```

**Tarea B — "Nadie te explica · revisión jueves"** (jueves 18:52, CRON_TZ=America/Santiago)
```
Clona github.com/nadieteexplica/reels-ia. Lee primero proyecto/INSTRUCCIONES.md (Seguridad y Publicación mandan), después CONTEXTO.md y docs/AUTOMATIZACION.md. Ejecuta "B) Revisión de mitad de semana": métricas tempranas en Metricool, comentarios con preguntas → docs/IDEAS.md §5, y anota los outliers en docs/PUBLICADOS.md. Haz push. Escríbele a Tomás solo si hay algo relevante, en 3 líneas como máximo.
```

## Manejo de fallas
| Falla | Qué hacer |
|---|---|
| Actions falla (voz o render): workflow en rojo o `error` en `out/status.json` | Reintentar 2 veces (con `workflow_dispatch`, sin crear jobs nuevos). Si sigue, avisar en 1 línea con la causa y la propuesta |
| Créditos de ElevenLabs bajo 8.000 | Avisar a Tomás y bajar a 2 videos esa semana |
| Un video no pasa el QA en 3 rondas | Entregar 2 videos y explicar. Nunca mandar uno malo |
| Metricool rechaza la URL o el post | Probar el hosting alternativo y avisar |
| vidIQ sin créditos | Seguir con la web y los comentarios. vidIQ no es imprescindible |
| Duda sobre un dato | El tema no sale hasta tener 2 fuentes. Se cambia por otro del banco |
