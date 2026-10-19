# Etapa 5 — Clips de Kling

**Criterios:** `manos`, `objeto`, `personaje`, `estabilidad`.
**Materiales:** por clip, una grilla de **8 cuadros** en orden de tiempo (`<clip>.jpg`) y su **cuadro de partida** (`<clip>_inicio.jpg`); `clips.json` (duración, resolución y la instrucción en inglés que se le dio a Kling); la ficha de los personajes del episodio.

Cada clip reemplaza un plano del video. Un clip con un defecto visible en cualquiera de sus cuadros **no sirve** (salvo que el defecto quede fuera del tramo usado, y eso no lo sabes: juzga el clip entero y di desde qué segundo es usable).

## Revisa cada clip, cuadro por cuadro
1. **Manos:** dedos que rodean el objeto o se apoyan en la cara de verdad; ninguno atraviesa, ninguno flota; cantidad de dedos correcta; la mano no se deforma.
2. **Objeto:** pegado a la mano mientras se mueve; no cambia de forma, tamaño, **color ni material** entre cuadros; no aparecen objetos nuevos ni desaparecen los que estaban.
3. **Personaje:** la cara, la forma, los colores (y el pelo o la ropa, si tiene) son los del cuadro de partida y de la ficha en los 8 cuadros (Kling tiende a "derretir" caras y cambiar ropa al final).
4. **Estabilidad:** cámara fija como se pidió, fondo que no se deforma, sin texto, sin cortes, sin cambios de luz bruscos.
5. **Acción:** ¿hace lo que pide la instrucción y lo que necesita el plano? ¿Se ve natural (sin cámara lenta rara ni movimientos de goma)?

Por clip, en `problemas` pon `"plano": "<nombre del clip>"` y en `segundo` el cuadro (por ejemplo "3,2 s").

**Tramo usable.** Del clip se usa un tramo (normalmente 1,5–3 s). Para cada clip define el tramo más largo **sin ningún bloqueante** y agrégalo en un campo extra de tu JSON:
`"clips": [{"clip": "p9_cono_a", "usable": [0.0, 2.1], "sirve": true, "por_que": "…"}]`
- `sirve` = true sólo si ese tramo dura **1,5 s o más** y dentro de él la mano, el objeto y el personaje están bien en todos los cuadros.
- Un defecto **fuera** del tramo usable no es bloqueante: anótalo con prioridad 2 y di que queda fuera del tramo.
- Un defecto **dentro** del tramo usable es bloqueante (ese tramo no sirve; busca otro o `sirve` = false).

`veredicto` del encargo: APROBADO sólo si **todos** sus clips sirven.
