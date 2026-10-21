# Auditor — revisión independiente por etapas (proceso v2)

**Para qué:** que ningún error que un espectador notaría llegue a Tomás ni a las redes, **sin** convertir cada video en 24 horas de rondas. Desde el Ep. 2, si Tomás encuentra un error que el auditor dejó pasar, es una falla del auditor y se corrige acá.

## Por qué cambió (21-oct-2026)
El Ep. 2 tomó más de 24 h y ~26 % del uso semanal de Claude de Tomás: **19 rondas** del auditor con hasta 6 revisores cada una; la puerta 6 marcó 76 → 66 → 58 cosas y nunca convergió (cada ronda traía revisores nuevos que encontraban detalles nuevos); la vara (las 28 notas ≥ 8) era casi imposible; el revisor veía 6 fotos por plano y decía "congelado"; y las reglas aparecían recién al final, así que el editor arreglaba a ciegas. El video que "reprobó" fue el que más le gustó a Tomás. **No se puede volver a repetir** (Tomás).

## Reglas v2 (decididas con Tomás el 21-oct-2026)
1. **El auditor es la receta, no el examen final.** Lo que va a exigir está escrito antes de animar: en la **ficha de plano** del storyboard y en el **chequeo automático por plano** que el editor corre en cada prueba (`tools/prueba.py`, `tools/auditor/chequeo_planos.py`).
2. **Bloqueantes: lista cerrada B1–B11** (`tools/auditor/prompts/comun.md`): sólo lo que un espectador notaría como error o lo que es falso. Todo lo demás es **sugerencia**, y el veredicto muestra sólo **las 5 más importantes**.
3. **Aprueba** sin bloqueantes, sin fallas automáticas, con **promedio ≥ 8 y ningún criterio bajo 7**. Las notas de los revisores se promedian (antes se tomaba la más baja).
4. **Máximo 2 rondas por puerta.** La 2.ª es de **verificación**: el revisor recibe lo que marcó la 1.ª (`anterior.json`), dice si quedó arreglado y sólo puede agregar bloqueantes nuevos. `preparar` no abre una 3.ª ronda (sólo con `--forzar 'motivo'`, que queda anotado y lo revisa la puerta P).
5. **Un plano que falla dos veces se simplifica o se cambia por una plantilla**: no se parcha otra vez. **Lo que ya pasó no se toca.**
6. **Máximo 2 revisores por ronda** (antes 6). El video se audita como **animatic** (baja resolución, antes del render final), con un revisor para todos los planos y uno global; el render final sólo pasa un chequeo de bloqueantes.
7. **El revisor ve 6–12 cuadros por plano (4 por segundo)** y las medidas de movimiento de cada plano, para no confundir movimiento chico con "congelado".
8. **Tomás tiene la última palabra.** A las 48 h de publicado se compara lo que dijo el auditor con las métricas (`PUBLICADOS.md`); si no calzan, se ajustan los criterios.
9. **Topes por video** (`tools/auditor/presupuesto.json` → `proceso_v2`): 8 h de trabajo, 2 rondas por puerta, 2 revisores por ronda, 2 animatics, 1 render final, 12 escenas, 3 escenas a medida. Si se va a pasar uno, se para y se le avisa a Tomás con opciones.

## Etapas
| # | Etapa | Cuándo | Chequeo automático | Revisor |
|---|---|---|---|---|
| 1 | **Guion** | antes de la voz | 182–190 palabras (62–65 s), frases ≤ 14 palabras, pausas, prohibidas, lista negra, 2 fuentes con URL (sin Wikipedia), tabla de verificación, cifras con fuente, puntaje ≥ mínimo | 1: precisión (abre las fuentes), gancho, claridad (¿sobra una frase?), compartible |
| 2 | **Voz** | antes del storyboard | duración 62–65 s (si queda corta: `tools/pausas.py`, 0 créditos), palabras > 1,2 s, pausas, conteo = guion, créditos, transcripción automática contra el guion | **sólo si** la transcripción encontró diferencias o hay ritmo raro |
| 3 | **Storyboard (fichas de plano)** | antes de animar | máx. 12 escenas y 3 a medida, columnas de la ficha completas (escena, plantilla, acción visible, cambio, cámara, cara, gráfico, origen), qué cambia en cada plano de más de 1,7 s, cara sobre y 1000, gráfico vs. cara, huecos, escala cada ≤ 12 s, Kling ≤ 3 | 1: foco, ritmo, viabilidad con el kit, gancho visual |
| 4 | **Cuadros de estilo** | sólo si hay escenario nuevo | resolución, % quemado, lavado, oscuro | 1 (todos los cuadros en un encargo) |
| 5 | **Clips de Kling** | si hay | resolución, palabras que activan el filtro, máx. 3 | 1 |
| 6 | **Animatic** | video completo en baja resolución (540×960, 8 muestras), antes del render final | QA técnico, detectores (pantalla vacía, apariciones, luz), **chequeo por plano** (ojos tapados, quemado, plano quieto, poco movimiento, fondo liso, cara bajo la interfaz), subtítulos contra `words.json`, audio | 2: **planos** (todos) y **global** (8 criterios) |
| 7 | **Final** | render final (720×1280, 16 muestras) | lo mismo que el animatic | 1: **sólo bloqueantes**, sin notas |
| 8 | **Paquete** | antes del mensaje a Tomás | título ≤ 60, hashtags, pregunta, fuentes, `madeForKids`, título de TikTok, etiquetas IA, URL pública | 1 |
| P | **Proceso** | al final | bitácora, horas prometidas, chequeos de 15 min, ≤ 16 máquinas, gasto, **rondas y revisores por puerta, horas del video** | — |

## Chequeo automático por plano (sin IA)
`tools/auditor/chequeo_planos.py` — corre en `tools/prueba.py` (cada plano, ~2–3 min), en el workflow de render (muestras y borrador) y en las puertas 6 y 7. Usa los **ojos** que `plano.py` guarda en el meta de cada cuadro (`studio/plantilla/caras.py`) y las **cajas de los gráficos** que registra el post (`studio/plantilla/graficos.py` → `graficos.json`).
- 🛑 ojo tapado por un gráfico o un subtítulo (≥ 0,2 s) · 🛑 quemado > 3 % sin subtítulos ni gráficos · 🛑 pantalla vacía
- ❌ ojos bajo y 1250 (interfaz de la app) · ❌ 1,5 s o más sin cambio visible
- ⚠️ ojos en la franja de subtítulos · ⚠️ poco movimiento (mediana < 0,5) · ⚠️ 1,0–1,5 s quieto · ⚠️ fondo liso > 70 % · ⚠️ cara al borde

**Calibración con el Ep. 2 (r3):** pilla la lupa que tapaba el ojo del pájaro en el plano 14 (el bloqueante que tumbó la r3), el suelo liso y quieto del 19 (2,1 s sin cambio, 76 % liso), el plano fijo del 13 y el interior quemado del 10 (3,5 %). El plano 14–16 que el revisor llamó "congelado" mide 0,8–1,0 de movimiento mediano y 0,6–0,7 s máximo quieto: se movía, poco.

## Formato de salida (fijo)
Cada ronda queda en `studio/episodios/<ep>/auditoria/<etapa>/rN/`:
- `checks.json` (automático), `<encargo>.json` (cada revisor), `materiales/anterior.json` (ronda 2).
- **`veredicto.md`** y `veredicto.json`: APROBADO / NO APROBADO, promedio, notas (promedio y la más baja), **bloqueantes y fallas automáticas**, **5 sugerencias**, verificación de la ronda anterior, planos que fallaron dos veces, avisos.
- `auditoria/ESTADO.md`: una línea por etapa y ronda.

## Cómo se corre (lo hace Claude, no Tomás)
```bash
python3 tools/prueba.py <ep> --planos 3,4                                   # editor: cada plano, antes del auditor
python3 tools/auditor/auditar.py preparar <ep> guion [--fuentes fuentes.md]
python3 tools/auditor/auditar.py preparar <ep> voz                          # necesita out/asr/<ep>.json
python3 tools/auditor/auditar.py preparar <ep> storyboard
python3 tools/auditor/auditar.py preparar <ep> cuadros --imagenes 'ruta/*.jpg' --nota "para qué es cada cuadro"
python3 tools/auditor/auditar.py preparar <ep> animatic --video borrador.mp4 --planos planos.json --subs subs_log.json \
        --meta meta/ --graficos graficos.json --kling-planos ninguno           # todo sale de la prerelease epNN-borrador
python3 tools/auditor/auditar.py preparar <ep> final    --video final.mp4 (mismas opciones)
python3 tools/auditor/auditar.py preparar <ep> paquete --url <URL pública del MP4>
python3 tools/auditor/auditar.py preparar <ep> proceso
python3 tools/auditor/auditar.py lanzar <ep> <etapa>     # texto exacto de cada subagente → Agent, en segundo plano
python3 tools/auditor/auditar.py estado <ep> <etapa>
python3 tools/auditor/auditar.py cerrar <ep> <etapa>     # veredicto.md (sale 0 si APROBADO) → commit y push
```
- **Prohibido** escribir o editar a mano un `<encargo>.json` o un `veredicto.*`. Si el auditor se equivoca, se corrige el prompt o el chequeo.
- Con NO APROBADO en la r1: se arreglan los bloqueantes y, si es barato, las 5 sugerencias; se re-renderiza **sólo** lo que cambió; `preparar` abre la r2 (verificación). Con NO APROBADO en la r2: lo que sigue fallando se simplifica o se reemplaza por una plantilla, sin otra ronda; si es guion o storyboard, se cambia la idea o se le pregunta a Tomás.

## Bitácora del proceso (obligatoria)
Cada hecho se anota con `tools/auditor/bitacora.py` en `auditoria/proceso.jsonl`:
```bash
python3 tools/auditor/bitacora.py <ep> promesa --hora 18:40 --que "animatic" --dato "muestras: 40 planos en 9 min"
python3 tools/auditor/bitacora.py <ep> aviso   --que "se atrasa a 19:10: ..."          # cada aviso a Tomás, ANTES de la hora
python3 tools/auditor/bitacora.py <ep> cumplida --id <n de la promesa>
python3 tools/auditor/bitacora.py <ep> trabajo --id "pod a5000-1" --estado inicio|fin|caido
python3 tools/auditor/bitacora.py <ep> chequeo --id "render-planos 39290639291" --estado "vivo, 812/2160"   # cada 15 min
python3 tools/auditor/bitacora.py <ep> gasto   --servicio kling --monto 4 --nota "p3"
```

## Límites (dichos derecho)
- **El revisor no escucha el audio:** la pronunciación se juzga con la transcripción automática y el volumen con mediciones.
- **Los detectores marcan, no deciden** (salvo pantalla vacía, quemado y ojo tapado). Hay falsos positivos (etiquetas que entran a propósito, acciones rápidas).
- **El chequeo de ojos es geométrico:** sabe si un gráfico o un subtítulo queda sobre el ojo, no si una pata o una hoja lo tapa en 3D.
- **Independencia:** el revisor conoce las reglas, no sabe qué se hizo ni qué opina quien lo hizo (salvo, en la r2, la lista de lo que debía arreglarse).

## Calibración y mantenimiento
`docs/AUDITOR_CALIBRACION.md`. Cada error nuevo que llegue a Tomás o a las redes se anota en `LECCIONES.md` y se agrega al chequeo automático si se puede medir; si no, a la lista de bloqueantes o al prompt de la etapa.
