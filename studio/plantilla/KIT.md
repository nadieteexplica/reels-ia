# Kit de producción — lo que se reutiliza (proceso v2, 21-oct-2026)

**Para qué:** que un video nuevo no tome 24 h. El Ep. 2 armó ~45 escenas una por una (45 funciones `pNN` en `planos_ep02.py`, 2.322 líneas, con sólo ~5 escenarios) y las reglas del auditor aparecían recién al final.

**Dicho derecho (auditoría del 21-oct):** hoy este kit es un **catálogo de código del Ep. 2 para copiar**, no plantillas programadas. El ahorro **no está medido**: se mide en el Ep. 3 (horas por escena en la bitácora). El primer paso del Ep. 3 es convertir en funciones con parámetros las plantillas que ese video use (empezando por `detalle_lupa` con `graficos.lugar_libre`, que hoy existe pero ningún plano la usa).

**Regla de Tomás que sigue vigente:** cada idea se diseña para su viralidad (personajes, fondo, estilo). Reutilizar = reutilizar **código**, no repetir personajes ni escenarios. Un personaje nuevo se arma con las bases de `personajes.py` (mismas convenciones de pivotes y nombres de ojos), así la animación, el chequeo de ojos y el post sirven sin código nuevo.

## 1. Escena ≠ plano
- **Escena** = una actuación animada que se arma una vez (una función de animación) y se filma con una o varias cámaras. Es lo caro. **Máximo 12 por video, 3 a medida** (punto de partida; se ajusta con las horas medidas del Ep. 3).
- **Plano** = cada corte. Filmar la misma escena con otra cámara o un detalle es barato: en el Ep. 2, las piezas 15 y 16 reutilizan `p14` y la escena del cuadro 0 (`_c0`) se usó en 5 planos.
- Ritmo: **algo cambia cada 1–2 s, nunca más de 2 s sin cambio** (REFERENCIAS §3: cortes de 1,2 a 2,2 s, mediana ~1,65 s; R5 casi no corta, pero algo se transforma todo el rato).

## 2. Bases (copiar del Ep. 2 al crear `studio/episodios/epNN-slug/escena/`)
| Qué | Dónde (Ep. 2) | Para qué |
|---|---|---|
| Tiempos de la voz | `escena/ep02.py` → `epNN.py` (el workflow lo busca por el nombre del episodio) | `T`/`FR` por plano desde `words.json`, `t_palabra()`, `camara()`, `mirar()`, `empujar()` (push-in), `pantalla()` (punto → píxel), `oculto()` |
| Render por piezas | `escena/plano.py`, `escena/reparto.py` | Cada pieza arma su escena y renderiza sus cuadros; `reparto.py` las reparte en ≤ 16 máquinas; `plano.py` **guarda los ojos de cada personaje en el meta** (`studio/plantilla/caras.py`) |
| Personajes procedurales | `escena/personajes.py`, `escena/anim_pj.py` | Pájaro, ratón, rata, tupaya, ají con brazos: cuerpo, cabeza, ojos (`*_ojoL/R`), párpados, boca, orejas, cola. Parpadeo, mirar, masticar, tragar, caminar |
| Escenarios | `escena/desierto.py`, `set_c0.py`, `set_lengua.py`, `set_muelas.py`, `bosque.py` | Desierto al atardecer, interior de la lengua con sensores, ventana de muelas, bosque. `PROBE`/`RAYO_PIX` para ubicar utilería con rayos |
| Efectos | `escena/vfx.py` | Llama única, humo, vapor, burbujas, lágrimas |
| Post | `escena/post.py` | Subtítulos palabra por palabra, píldoras, lupa/recuadro con cuña, tarjetas ✓/✕, REC, whip, contador, bloom; **registra cada gráfico y cada movimiento de la imagen** (`studio/plantilla/graficos.py` → `graficos.json`). Hoy está escrito plano por plano (`if k == 23`): al copiarlo, cada gráfico nuevo se ubica con `lugar_libre` |
| Audio | `escena/audio.py` | Música y SFX sintetizados, ducking, −14 LUFS (escribe `<epNN>_mix.wav`) |
| Workflow | `.github/workflows/render-planos.yml` | Muestras, piezas, runs base, armado, chequeo automático por plano y borrador en la prerelease. Sirve para cualquier episodio si la escena tiene `epNN.py` y el post escribe `<epNN>_planos.json` |

## 3. Plantillas (recetas; las que use el Ep. 3 se programan como funciones)
| Plantilla | Escala | Ejemplo Ep. 2 | Reglas que tiene que traer | Qué falló en el Ep. 2 |
|---|---|---|---|---|
| **reaccion** | P | 4, 5, 12 | Cara de 3/4 entre y 350–800, lente ≥ 45 mm, una acción que se lee en una foto, push-in 6–12 %, una acción secundaria cada ~1 s | 12: el ratón casi no se movía (r3) |
| **detalle_lupa** | D + gráfico | 14–16, 23–24, 31 | La lupa se ubica con `lugar_libre` y los ojos del meta (nunca con números fijos), cuña al detalle, fondo animado | 14–16: la lupa fija tapó el ojo (bloqueante de la r3) |
| **interior** | I | 7–11 | Una sola cámara para todo el interior con push-in, un solo foco | 10: interior quemado (3,5 %) |
| **tarjetas** | M | 23–24 | Tarjeta con marco, ✓ o ✕ que entra con la palabra, fondo desenfocado | 24: fondo liso 73 % (aviso) |
| **cifra** | M | 35 | Número grande que sube con la voz (y 280–490), algo 3D detrás que cambia | — |
| **recorrido** | G/M | 29 | Personaje que camina con la luz que lo sigue, cámara de costado | — |
| **loop** | P | 40 → 1 | Termina exacto en el encuadre del cuadro 0 | — |
| **whip** | — | 28 | Transición rápida; máximo 2 por video | — |

Formatos de las referencias que **no tienen plantilla todavía** (corte que se transforma R5, datos propios R7, megaproyecto R9): una idea así no se descarta; se estima su costo y se le pregunta a Tomás si pasa el tope.

## 4. El ciclo del editor (cada plano, antes del auditor)
1. Armar el plano desde su ficha (y su plantilla, si existe).
2. `python3 tools/prueba.py <ep> --planos N` → render chico + post + **chequeo automático** + `hoja.jpg` (ojos en verde si están libres y en rojo si algo los tapa; gráficos en azul). Medido: 94 s (plano 14) y 124 s (plano 23) con 2 cuadros por pieza.
3. Arreglar hasta **0 fallas** y mirar la hoja. La prueba usa cuadros sueltos: **no** mide si el plano está quieto; eso lo mide el animatic.
4. Con todos los planos listos: **animatic** (`render-planos.yml`, `res=540x960`, `samples=8`) → el workflow corre el chequeo con el video corrido (ahí sí: plano quieto, poco movimiento) → si hay fallas automáticas se arreglan **antes** de abrir la puerta 6.
5. Puerta 6 → se arreglan los bloqueantes y, si es barato, las 5 sugerencias; se re-renderiza sólo eso. **Lo que ya pasó no se toca.** Un plano que falla dos veces se simplifica o se cambia.
6. Render final de una vez (720×1280, 16 muestras) → **puerta 7** (chequeo + 1 revisor, sólo bloqueantes).

## 5. Qué mide el chequeo automático (`tools/auditor/chequeo_planos.py`)
- 🛑 ojo tapado por un gráfico o un subtítulo (lupa, recuadro y marca como círculos; píldoras y subtítulos como cajas; ojos movidos igual que la imagen en el post) · 🛑 quemado > 3 % · 🛑 pantalla vacía
- ❌ cara bajo la interfaz (y > 1250) · ❌ 2 s o más sin cambio visible (sólo con video corrido)
- ⚠️ cara en la franja de subtítulos · ⚠️ poco movimiento · ⚠️ 1,2–2 s quieto · ⚠️ fondo liso > 70 % · ⚠️ cara pegada al borde

**Lo que pilla y lo que no (probado con la versión publicada del Ep. 2):** de los 3 bloqueantes que dejó el revisor en la r3, pilla 1 (la lupa sobre el ojo del 14); **no** ve las hojas que flotaban en el 25 ni el brazo que se veía a través del vaso en el 34: eso sigue siendo del revisor. Además marca el quemado del 10 y el suelo quieto del 19 (sólo con el video corrido), y deja como aviso el plano fijo del 13.
