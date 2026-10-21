# Kit de producción — lo que se reutiliza (proceso v2, 21-oct-2026)

**Para qué:** que un video nuevo se arme en **una jornada**, no en 24 h. El Ep. 2 tomó más de 24 h y ~26 % del uso semanal de Claude de Tomás porque cada uno de sus 40 planos se hizo a mano y las reglas del auditor aparecían recién al final. Desde el Ep. 3, cada plano parte de una **plantilla** de esta lista y de las **bases** que ya existen.

**Regla de Tomás que sigue vigente:** cada idea se diseña para su viralidad (personajes, fondo, estilo). Reutilizar = reutilizar **código y plantillas**, no repetir personajes. Un personaje nuevo se arma con las bases de `personajes.py` (mismas convenciones de pivotes y nombres), así la animación, el chequeo de ojos y el post funcionan sin escribir código nuevo.

## 1. Bases (copiar del Ep. 2 al crear `studio/episodios/epNN-slug/escena/`)
| Qué | Dónde (Ep. 2) | Para qué |
|---|---|---|
| Tiempos de la voz | `escena/ep02.py` → `epNN.py` | `T`/`FR` por plano desde `words.json`, `t_palabra()`, `camara()`, `mirar()`, `empujar()` (push-in), `pantalla()` (punto → píxel), `oculto()` |
| Render por piezas | `escena/plano.py`, `escena/reparto.py` | Cada pieza arma su escena y renderiza sus cuadros; `reparto.py` las reparte en ≤16 máquinas; **escribe los ojos de cada personaje en el meta** (`studio/plantilla/caras.py`) |
| Personajes procedurales | `escena/personajes.py`, `escena/anim_pj.py` | Pájaro, ratón, rata, tupaya, ají con brazos: cuerpo, cabeza, ojos (`*_ojoL/R`), párpados, boca, orejas, cola. Parpadeo, mirar, masticar, tragar, caminar. Un animal nuevo = otra llamada con otras proporciones y colores |
| Sets | `escena/desierto.py`, `set_c0.py`, `set_lengua.py`, `set_muelas.py`, `bosque.py` | Desierto al atardecer (roca, matas, saguaros, cielo), interior de la lengua con sensores, ventana de muelas, bosque. `PROBE`/`RAYO_PIX` para ubicar utilería con rayos |
| Efectos | `escena/vfx.py` | Llama única, humo, vapor, burbujas, lágrimas |
| Post | `escena/post.py` | Subtítulos palabra por palabra (zona x 120–888 · y 1000–1250), píldoras, lupa/recuadro con cuña, tarjetas ✓/✕, REC, whip, contador, bloom; **registra cada gráfico** (`studio/plantilla/graficos.py` → `graficos.json`) |
| Audio | `escena/audio.py` | Música y SFX sintetizados, ducking, −14 LUFS |
| Workflow | `.github/workflows/render-planos.yml` | Muestras, piezas, runs base, armado, **chequeo automático por plano** y borrador en la prerelease. Al copiar para otro episodio: cambiar `ep02_planos.json` y `import ep02` por los del episodio |

## 2. Plantillas de plano (cada una ya cumple las reglas del auditor)
**Escena ≠ plano.** Una escena es lo caro: una función que arma el set, los personajes y su actuación (en el Ep. 2, `_c0()` arma la roca con el pájaro y el ratón). Un plano es un corte dentro de una escena: otra pieza que llama a la misma función con otra cámara o un detalle (el Ep. 2 usó `_c0()` en los planos 1, 2, 14, 17 y 40). **Máximo 12 escenas por video, 3 a medida**; cortes, los que hagan falta para que algo cambie cada 1,5 s (~40 cambios en 62 s, el ritmo de las referencias que retienen). Cada ficha del storyboard dice su escena y su plantilla.

| Plantilla | Escala | Ejemplo Ep. 2 | Reglas que trae puestas |
|---|---|---|---|
| **reaccion** | P | 4, 5, 12 | Cara de 3/4 entre y 350–800, lente ≥ 45 mm, una acción que se lee en una foto (llamarada, ojos enormes, salto), push-in 6–12 %, parpadeo y una acción secundaria cada ~1 s |
| **detalle_lupa** | D + gráfico | 14–16, 23–24, 31 | La lupa/recuadro se ubica con `graficos.lugar_libre(ancho, alto, ojos)` usando los ojos del meta (nunca con números fijos: lección 47), cuña que apunta al detalle, fondo animado (nunca un cuadro fijo) |
| **interior** | I | 7–11 | Una sola cámara para todo el interior con push-in, un solo foco que brilla con la palabra |
| **tarjetas** | M | 23–24 | Tarjeta con marco, ✓ o ✕ que entra con la palabra, fondo del set desenfocado y oscuro afuera |
| **cifra** | M | 35 | Número grande que sube con la voz (y 280–490), algo 3D detrás que cambia |
| **recorrido** | G/M | 29 | Personaje que camina con la luz que lo sigue, cámara de costado, se detiene y mira |
| **loop** | P | 40 → 1 | Termina exacto en el encuadre del cuadro 0 |
| **whip** | — | 28 | Transición rápida; máximo 2 por video |

## 3. El ciclo del editor (cada plano, antes del auditor)
1. Armar el plano desde su plantilla, con lo que dice su ficha.
2. `python3 tools/prueba.py <ep> --planos N` → render chico + post + **chequeo automático** + `hoja.jpg` (ojos marcados en verde si están libres y en rojo si algo los tapa; cajas de los gráficos en azul). En ~1,5 min por plano (medido: 94 s en el plano 14 del Ep. 2, 2 piezas × 2 cuadros).
3. Arreglar hasta **0 fallas** del chequeo y mirar la hoja (30 s por plano). Recién ahí el plano está listo.
4. Con todos los planos listos: **animatic** completo (`render-planos.yml` con `res=540x960`, `samples=8`) → el workflow corre el chequeo → **puerta 6** (2 revisores).
5. Sólo se arreglan los bloqueantes y las 5 sugerencias de arriba, re-renderizando sólo esos planos (`piezas` + `base_run`). **Lo que ya pasó no se toca.** Un plano que falla dos veces se simplifica o se cambia por una plantilla.
6. Render final de una vez (720×1280, 16 muestras) → **puerta 7** (chequeo + 1 revisor, sólo bloqueantes).

## 4. Qué mide el chequeo automático (`tools/auditor/chequeo_planos.py`)
Calibrado con el Ep. 2: en la r3 habría pillado la lupa sobre el ojo del plano 14 (bloqueante), el suelo liso y quieto del 19, el plano fijo del 13 y el interior quemado del 10.
- 🛑 ojo tapado por un gráfico o un subtítulo · 🛑 quemado > 3 % · 🛑 pantalla vacía
- ❌ cara bajo la interfaz (y > 1250) · ❌ 1,5 s o más sin cambio visible
- ⚠️ cara en la franja de subtítulos · ⚠️ poco movimiento · ⚠️ fondo liso > 70 % · ⚠️ cara pegada al borde
