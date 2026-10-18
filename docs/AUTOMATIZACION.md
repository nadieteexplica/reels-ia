# Automatización — cómo funciona la cuenta sola

## Cadencia
| Fase | Videos | Días | Créditos de voz al mes (aprox.) |
|---|---|---|---|
| **Piloto (primeras 4 semanas)** | 3 por semana | lunes, miércoles, viernes | ~16.000 de 40.000 |
| **Crecimiento** (si la calidad se mantiene y Tomás lo pide) | 5 por semana | lunes a viernes | ~27.000 de 40.000 |
| Diario | 7 por semana | todos | ~38.000+: no deja margen en Starter, así que **no** |

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
3. [ ] **Render en GitHub Actions**: un workflow `render.yml` con matriz paralela que toma `episodios/<slug>/` y devuelve el MP4. Hay que medir el tiempo por video.
4. [ ] **Hosting del MP4**: probar si Metricool acepta la URL de GitHub Release. Si no, usar `raw.githubusercontent.com` desde `out/videos/`.
5. [ ] **Script de QA automático**: `tools/qa.py` con los checks de la sección 9.1 del manual.
6. [ ] **Ep. 1 de punta a punta**:
   - alargar el guion a 62 s o más (sumar un dato, por ejemplo el estudio de Harvard de 2012 o cuánto dura),
   - regenerar la voz,
   - animar, pasar el QA y la revisión independiente,
   - entregarlo y, con OK, programarlo.
7. [ ] **Crear las tareas programadas** de abajo, recién con todo lo anterior funcionando.

## Ciclo semanal (tareas programadas)

### A) Producción semanal — domingo 10:00 (America/Santiago)
1. Actualizar el repo y leer los docs (`CONTEXTO.md`, el manual, `IDEAS.md` y `PUBLICADOS.md`).
2. **Métricas:**
   - Bajar de Metricool los datos de los videos de las últimas semanas.
   - Actualizar `PUBLICADOS.md`.
   - Escribir 2–3 aprendizajes en `CONTEXTO.md`.
3. **Ideas:**
   - Buscar según `IDEAS.md` §1.
   - Puntuar y elegir **3 temas** con 32 puntos o más, variados (distinto gancho y distinta área).
   - Darle prioridad a las preguntas de la comunidad.
4. **Guiones:** verificar con 2 fuentes, escribir en 185–215 palabras y guardar en `episodios/<NN>-<slug>/guion.md`.
5. **Voces:** 3 jobs en un solo commit. Esperar a Actions y controlar duraciones (62–75 s).
6. **Storyboards:** uno por episodio.
7. **Animación y render:** con la plantilla del estilo, en Actions.
8. **QA:** automático, visual y revisión independiente (8 o más en todo). Se corrige hasta que pase.
9. **Paquete:** MP4 con URL pública, `caption.md` y portada.
10. **Un solo mensaje a Tomás:**
    - los 3 videos (como archivos),
    - para cada uno: gancho, horario propuesto (mejor hora de Metricool por red) y texto del post,
    - la pregunta: "¿OK a los 3? (o dime cuál no)".
11. **Programar:** con OK, crear los posts programados en Metricool (lun, mié y vie, en las 3 redes) y anotarlos en `PUBLICADOS.md`.
    - **Sin OK no se publica nada.**
    - Si el lunes a las 9:00 no hay respuesta, enviar un recordatorio y correr el lunes y el miércoles al día siguiente.
12. Hacer commit y push de todo.

### B) Revisión de mitad de semana — jueves 19:00
- Métricas tempranas de los videos de lunes y miércoles.
- Leer los comentarios y pasar las preguntas buenas a `IDEAS.md` §5.
- Si un video rompió el promedio (2× o más), anotar qué tuvo de distinto.
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
Eres el productor de la cuenta "Nadie te explica". Clona github.com/nadieteexplica/reels-ia y lee CONTEXTO.md, docs/MANUAL_PRODUCCION.md, docs/AUTOMATIZACION.md, docs/IDEAS.md y docs/PUBLICADOS.md. Ejecuta el "Ciclo semanal A) Producción semanal" de AUTOMATIZACION.md completo: métricas → 3 ideas → guiones verificados → voces → storyboards → animación y render → QA con revisión independiente → paquete. Mándale a Tomás un solo mensaje con los 3 videos y los textos, y pídele OK. Solo con su OK explícito programa los posts en Metricool. Respeta todas las reglas de seguridad de CONTEXTO.md. Al final actualiza CONTEXTO.md, IDEAS.md y PUBLICADOS.md y haz push. Háblale en español chileno, corto y directo.
```

**Tarea B — "Nadie te explica · revisión jueves"** (jueves 18:52, CRON_TZ=America/Santiago)
```
Clona github.com/nadieteexplica/reels-ia y lee CONTEXTO.md y docs/AUTOMATIZACION.md. Ejecuta "B) Revisión de mitad de semana": métricas tempranas en Metricool, comentarios con preguntas → docs/IDEAS.md §5, y anota los outliers en docs/PUBLICADOS.md. Haz push. Escríbele a Tomás solo si hay algo relevante, en 3 líneas como máximo.
```

## Manejo de fallas
| Falla | Qué hacer |
|---|---|
| Actions falla (voz o render) | Reintentar 2 veces. Si sigue, avisar en 1 línea con la causa y la propuesta |
| Créditos de ElevenLabs bajo 8.000 | Avisar a Tomás y bajar a 2 videos esa semana |
| Un video no pasa el QA en 3 rondas | Entregar 2 videos y explicar. Nunca mandar uno malo |
| Metricool rechaza la URL o el post | Probar el hosting alternativo y avisar |
| vidIQ sin créditos | Seguir con la web y los comentarios. vidIQ no es imprescindible |
| Duda sobre un dato | El tema no sale hasta tener 2 fuentes. Se cambia por otro del banco |
