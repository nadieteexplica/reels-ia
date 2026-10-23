# Auditor — revisión independiente por etapas (proceso v2)

**Para qué:** que ningún error que un espectador notaría llegue a Tomás ni a las redes, **sin** convertir cada video en 24 horas de rondas. Si Tomás encuentra un error que el auditor dejó pasar, es una falla del auditor y se corrige acá.

## Por qué cambió (21-oct-2026)
El Ep. 2 tomó más de 24 h y ~26 % del uso semanal de Claude de Tomás. Medido en su bitácora: **22,7 h activas, 20 rondas** del auditor (una cancelada), **35 revisores** y **337 imágenes** revisadas. La puerta 6 marcó 76 → 66 → 58 cosas y nunca convergió (revisores nuevos en cada ronda encontraban detalles nuevos); la vara (las 28 notas ≥ 8) era casi imposible; el revisor veía 6 fotos por plano y decía "congelado"; y las reglas aparecían recién al final, así que el editor arreglaba a ciegas. El video que "reprobó" fue el que más le gustó a Tomás. **No se puede volver a repetir** (Tomás).

## Reglas v2 (con Tomás, 21-oct-2026; corregidas el mismo día tras una auditoría independiente)
1. **El auditor es la receta, no el examen final.** Lo que va a exigir está escrito antes de animar: en la **ficha de plano** del storyboard y en el **chequeo automático** que el editor corre en cada prueba (`tools/prueba.py`) y el workflow en cada animatic.
2. **Lo medible se arregla antes de gastar revisores:** si el chequeo automático de una puerta falla, `preparar` **no abre la ronda ni crea encargos** (queda en `<etapa>/_pre/checks.json`). Una ronda sólo se gasta en lo que necesita ojos.
3. **Bloqueantes: lista cerrada B1–B11** (`tools/auditor/prompts/comun.md`): sólo lo que un espectador notaría como error o lo que es falso. Todo lo demás es **sugerencia**, y el veredicto muestra sólo **las 5 más importantes**.
4. **Aprueba** sin bloqueantes, sin fallas automáticas, con **promedio ≥ 8** (promedio de los revisores por criterio) y **ninguna nota de ningún revisor bajo 7** (el promedio no esconde al revisor que sí miró). En un episodio realista, `realismo` pide **ningún revisor bajo 8**.
5. **Máximo 2 rondas por puerta.** La 2.ª es de **verificación**: cada cosa que marcó la 1.ª la verifica **un solo revisor** (el que tiene ese plano, o el global si la marcó el global), que también puede agregar bloqueantes nuevos; nada de sugerencias nuevas. `preparar` no abre una 3.ª ronda (sólo con `--forzar 'motivo'`, que queda anotado y lo revisa la puerta P).
6. **Salida después de 2 rondas:** si lo que no llega es el `realismo` de un episodio realista, **se para y se le pregunta a Tomás** (el kit es animado y la puerta 7 no mide realismo; el veredicto lo dice y marca `parar_y_preguntar`). Si no, en el animatic, los planos que siguen fallando se simplifican o se cambian por una plantilla y el video sigue: la **puerta 7** revisa bloqueantes en todo el render final, incluidos esos planos. En guion o storyboard, se cambia la idea o se le pregunta a Tomás.
7. **Un plano con un bloqueante que falla dos veces se simplifica o se reemplaza**, no se parcha otra vez. Una sugerencia que el editor decidió no hacer no cuenta como falla. **Lo que ya pasó no se toca.**
8. **Revisores:** en el animatic, **1 por cada 10 planos + 1 global** (un solo revisor no alcanza a mirar 40 tiras con sus eventos); en la r2, sólo los planos que tenían algo que verificar o que se re-renderizaron (`--cambiados`). El render final lo revisa uno solo, por bloqueantes.
9. **El revisor ve 6–12 cuadros por plano (4 por segundo)** y las medidas de movimiento de cada plano, para no confundir movimiento chico con "congelado".
10. **Tomás tiene la última palabra.** A las 48 h de publicado se compara lo que dijo el auditor con las métricas (`PUBLICADOS.md`); si no calzan, se ajustan los criterios.
11. **Topes por video** en `tools/auditor/presupuesto.json` → `proceso_v2` (el código los lee de ahí; los cambia Tomás): 4 h activas (meta 2,5 h), 2 rondas por puerta, 10 planos por revisor, 2 animatics, 1 render final, 6 escenas, 3 a medida, 2 s máximo sin cambio, 70–128 palabras, 25–45,5 s (meta 25–40 s; YouTube primero, 21-oct-2026). Se ajustan con lo medido en el Ep. 4. **El % de uso de Claude no se puede medir desde la sesión:** la puerta P anota revisores lanzados e imágenes revisadas, que es lo que más lo mueve.

## Estilo del episodio: animado o realista (Tomás, 22-oct-2026)
Hasta el Ep. 4 el auditor tenía metido el look animado: belleza pedía colores saturados y fondo celeste, el personaje se comparaba con el protagonista viejo, y no había forma de exigir realismo. Tomás pidió realismo de verdad, así que ahora **cada episodio declara su estilo** y el auditor se ajusta a ese estilo.

**`studio/episodios/<ep>/estilo.json`** (obligatorio desde el Ep. 5; sin él, `preparar` falla en las puertas 3–8):
```json
{"estilo": "realista", "referencias": ["referencias/*.jpg"], "nota": "rana flotando en el laboratorio y el imán gigante"}
```
- `estilo`: `animado` o `realista`. Las reglas de cada uno están en **`tools/auditor/prompts/estilos.md`**, y cada revisor lee la sección de su estilo.
- `referencias` (opcional, recomendado en realista): hasta 4 fotos reales del tema para comparar (lista de rutas en la carpeta del episodio; se aceptan comodines). Van como `ref_N.jpg` a los materiales de las puertas 4, 6 y 7. Son de otros y sólo para comparar: **no van al video ni al repo público** (`.gitignore` ignora `referencias/` y `ref_*.jpg`). Si todavía no están, es aviso, no falla.
- Los episodios de antes (Ep. 1–4 y Rhein, `LEGADO` en `comun.py`) siguen como animados sin el archivo.

| | Animado | Realista |
|---|---|---|
| **Qué es** | el look de los Ep. 1–4 | "realista pero en un mundo animado" (Tomás; referencia de calidad: Zack D. Films). **No** es fotorrealismo de IA |
| **Belleza** | luz suave de estudio, colores saturados, fondo vivo | luz con sombras reales, materiales con textura e imperfecciones, color natural con contraste, lente real |
| **Criterio `realismo`** | no existe | obligatorio en cuadros (4) y animatic (6), con número; **ningún revisor bajo 8** (`presupuesto.json` → `realismo_min`). "No aplica" cuenta como falta |
| **Lavado (automático, puerta 4)** | brillo > 175 y saturación < 70 | brillo > 175 y **sin negros** (percentil 5 > 120, como neblina); entre 90 y 120, o poco color con sombras reales, es aviso y lo decide el revisor |
| **B9** | estilo rechazado o imagen rota | lo mismo, más un plano o personaje **claramente** de dibujo animado (≤ 5 en la escala); las capas de explicación nunca, y lo "de plástico" va en la nota |
| **Paquete** | etiqueta IA en IG y TikTok | además `isAiGeneratedContent: true` en YouTube (falla si falta) |
| **Personajes** | los de la ficha del episodio | los de la ficha del episodio; el protagonista de MakeHuman ya no se usa |

**Ficha:** un episodio nuevo se compara **sólo con su propia `ficha.jpg`**: el protagonista viejo ya no sirve de respaldo. Sin ficha, las puertas 4–7 fallan, salvo `--sin-personajes`.

**Capas de explicación:** en realista, las líneas, flechas, cortes y etiquetas pueden ir estilizadas encima del mundo real (lo del Ep. 4) y no bajan el realismo.

## Etapas
| # | Etapa | Cuándo | Chequeo automático | Revisor |
|---|---|---|---|---|
| 1 | **Guion** | antes de la voz | 70–128 palabras (25–45 s; meta 25–40), frases ≤ 14 palabras, pausas, prohibidas, lista negra, 2 fuentes con URL (sin Wikipedia), tabla de verificación, cifras con fuente, puntaje ≥ mínimo | 1: precisión (abre las fuentes), gancho, claridad (¿sobra una frase?), compartible |
| 2 | **Voz** | antes del storyboard | duración 25–45,5 s (si se pasa: recortar el guion; pausas con `tools/pausas.py`, 0 créditos), palabras > 1,2 s, pausas, conteo = guion, créditos, transcripción automática contra el guion | **sólo si** la transcripción encontró diferencias o hay ritmo raro |
| 3 | **Storyboard (fichas de plano)** | antes de animar | columnas de la ficha (escena, plantilla, acción visible, cambio, cámara, cara, gráfico, origen), máx. 6 escenas (el id "E1" cuenta igual aunque diga "E1 patio") y 3 a medida, qué cambia en cada plano de más de 2 s, cara sobre y 1000, gráfico vs. cara, huecos, escala cada ≤ 12 s, Kling ≤ 3 | 1: foco, ritmo, viabilidad, gancho visual |
| 4 | **Cuadros de estilo** | sólo si hay escenario nuevo | resolución, % quemado, lavado (según el estilo), oscuro, `estilo.json`, ficha del episodio | 1 (todos los cuadros en un encargo); en realista suma `realismo` |
| 5 | **Clips de Kling** | si hay | resolución, palabras que activan el filtro, máx. 3 | 1 |
| 6 | **Animatic** | video completo en baja resolución (540×960, 8 muestras), antes del render final | QA técnico, detectores (pantalla vacía, apariciones, luz), **chequeo por plano** (ojos tapados, quemado, plano quieto, poco movimiento, fondo liso, cara bajo la interfaz), **sin datos de ojos = falla** (salvo `--sin-personajes`), subtítulos contra `words.json`, audio | 1 por cada 10 planos + 1 global |
| 7 | **Final** | render final (720×1280, 16 muestras) | lo mismo que el animatic | 1: **sólo bloqueantes**, sin notas |
| 8 | **Paquete** | antes del mensaje a Tomás | título ≤ 60, hashtags, pregunta, fuentes, `madeForKids`, título de TikTok, etiquetas IA | 1. La comprobación de la URL pública después del OK (`--url`) **no es una ronda** (queda en `8-paquete/url.json`) |
| P | **Proceso** | al final | bitácora, horas prometidas, chequeos de 15 min, ≤ 16 máquinas, gasto, **todas las rondas por puerta** (las de carpetas archivadas o canceladas también cuentan), **horas activas** (huecos de más de 1 h sin anotar no cuentan; pasarse es falla), revisores e imágenes | — (es un informe: no tiene tope de rondas) |

## Chequeo automático por plano (sin IA)
`tools/auditor/chequeo_planos.py` — corre en `tools/prueba.py` (cada plano; medido 94–124 s), en el workflow de render (muestras y borrador) y en las puertas 6 y 7. Usa los **ojos** que `plano.py` guarda en el meta de cada cuadro (`studio/plantilla/caras.py`: reconoce `*_ojoL/R` y `Ojo.L/R`) y lo que registra el post (`studio/plantilla/graficos.py` → `graficos.json`): las cajas de los gráficos y cada movimiento de la imagen (espejo, acercamientos), que mueve también los ojos.
- 🛑 al menos medio radio de un ojo bajo un gráfico (lupa, recuadro y marca como círculos; píldoras, contador y subtítulos como cajas), ≥ 0,2 s · 🛑 quemado > 3 % sin subtítulos ni gráficos · 🛑 pantalla vacía
- ❌ ojos bajo y 1250 (interfaz de la app) · ❌ 2 s o más sin cambio visible (sólo con video corrido)
- ⚠️ ojos en la franja de subtítulos · ⚠️ poco movimiento (mediana < 0,5) · ⚠️ 1,2–2 s quieto · ⚠️ fondo liso > 70 % · ⚠️ cara al borde

**Calibración con el Ep. 2 (versión publicada):** pilla la lupa que tapaba el ojo del pájaro en el plano 14 (el único de los 3 bloqueantes de la r3 que se puede medir; las hojas que flotaban en el 25 y el brazo visto a través del vaso en el 34 siguen siendo del revisor), el suelo quieto del 19 (2,1 s sin cambio, 76 % liso), el interior quemado del 10 (3,5 %) y avisa del plano fijo del 13. Probado también en el plano 23, que va en espejo: los ojos quedan donde corresponde. El 14–16 que el revisor llamó "congelado" mide 0,8–1,0 de movimiento mediano y 0,6–0,7 s máximo quieto: se movía, poco. Los umbrales de movimiento se calibraron con el render final (16 muestras): el ruido del animatic (8 muestras) puede cambiarlos y se recalibran con el primer animatic del Ep. 3.

## Formato de salida (fijo)
Cada ronda queda en `studio/episodios/<ep>/auditoria/<etapa>/rN/`:
- `checks.json` (automático), `<encargo>.json` (cada revisor), `materiales/anterior.json` y `anterior_<encargo>.json` (ronda 2).
- **`veredicto.md`** y `veredicto.json`: APROBADO / NO APROBADO, promedio, notas (promedio y la más baja), **bloqueantes y fallas automáticas**, **5 sugerencias**, verificación de la ronda anterior, planos que fallaron dos veces, avisos.
- `auditoria/ESTADO.md`: una línea por etapa y ronda.

## Cómo se corre (lo hace Claude, no Tomás)
```bash
python3 tools/prueba.py <ep> --planos 3,4                                   # editor: cada plano, antes del auditor
echo '{"estilo": "realista"}' > studio/episodios/<ep>/estilo.json   # una vez, al empezar ("referencias" se agrega cuando estén las fotos)
python3 tools/auditor/auditar.py preparar <ep> guion [--fuentes fuentes.md]
python3 tools/auditor/auditar.py preparar <ep> voz                          # necesita out/asr/<ep>.json
python3 tools/auditor/auditar.py preparar <ep> storyboard
python3 tools/auditor/auditar.py preparar <ep> cuadros --imagenes 'ruta/*.jpg' --nota "para qué es cada cuadro"
python3 tools/auditor/auditar.py preparar <ep> animatic --video borrador.mp4 --planos planos.json --subs subs_log.json \
        --meta meta/ --graficos graficos.json --kling-planos ninguno [--cambiados 14,25]   # todo sale de la prerelease epNN-borrador
python3 tools/auditor/auditar.py preparar <ep> final    --video final.mp4 (mismas opciones)
python3 tools/auditor/auditar.py preparar <ep> paquete [--url <URL pública del MP4>]
python3 tools/auditor/auditar.py preparar <ep> proceso
python3 tools/auditor/auditar.py lanzar <ep> <etapa>     # texto exacto de cada subagente → Agent, en segundo plano
python3 tools/auditor/auditar.py estado <ep> <etapa>
python3 tools/auditor/auditar.py cerrar <ep> <etapa>     # veredicto.md (sale 0 si APROBADO) → commit y push
```
- Si `preparar` sale con fallas automáticas, se arreglan y se vuelve a correr: no se gastó ninguna ronda.
- **Prohibido** escribir o editar a mano un `<encargo>.json` o un `veredicto.*`. Si el auditor se equivoca, se corrige el prompt o el chequeo.

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
- **El chequeo de ojos es geométrico:** sabe si un gráfico o un subtítulo queda sobre el ojo, no si una pata o una hoja lo tapa en 3D; y depende de que el post registre cada gráfico y cada movimiento de la imagen.
- **Independencia:** el revisor conoce las reglas, no sabe qué se hizo ni qué opina quien lo hizo (salvo, en la r2, la lista de lo que debía arreglarse).
- **Modo realista sin calibrar:** las notas de realismo y el lavado realista (percentil 5) se probaron con simulaciones, no con un video realista de verdad; se ajustan con el Ep. 5. El chequeo automático de pantalla vacía es igual para los dos estilos: un plano realista muy oscuro y sin bordes puede saltarlo.
- **Sin recalibrar:** la calibración "20 de 22" (`AUDITOR_CALIBRACION.md`) es del auditor v1; el v2 (lista cerrada, un revisor por cada 10 planos) no se ha recalibrado.

## Calibración y mantenimiento
`docs/AUDITOR_CALIBRACION.md`. Cada error nuevo que llegue a Tomás o a las redes se anota en `LECCIONES.md` y se agrega al chequeo automático si se puede medir; si no, a la lista de bloqueantes o al prompt de la etapa. **Todo cambio al proceso pasa una auditoría independiente y una simulación de las rondas antes de darlo por listo** (lección 50).
