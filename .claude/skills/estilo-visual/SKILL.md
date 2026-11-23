---
name: estilo-visual
description: Kit y reglas visuales de El viejo del dato para animar por código: fondo oscuro, un color de energía con brillo, etiquetas con línea guía, objeto real, subtítulos palabra por palabra con recuadro, curvas de movimiento con números, loop, y 5 estilos que rotan entre videos. Usar al hacer el storyboard y al animar.
---

# Estilo visual

**Motor: kit Python** (`studio/plantilla/kit_explica.py`), ganador del duelo visual a ciegas del 23-nov-2026 contra HyperFrames, 2 a 1 (`docs/estudios/duelo-visual.md`). Render en el Mac (~40 s por 8 s de video con 6 procesos) o en Actions (`render-2d.yml`). HyperFrames queda de respaldo (`render-hyperframes.yml`). **La vara no es el otro motor sino los virales:** un beat nuevo del kit tiene que sacar ≥ 8 contra cuadros de virales con /watch (`studio/duelo-visual/vara_viral.py`, jueces ciegos); el kit tiene 3 vueltas para llegar, si no, se prueba three.js en Actions (Tomás, 23-nov-2026).

**Lo que dejó el duelo (no repetir):** la etiqueta dice exactamente lo del storyboard · el último cuadro calza de verdad con el primero (loop) · el objeto del remate es real, nunca un ícono en un círculo · las revelaciones de escala van con movimiento de cámara (alejarse), no con corte seco · volumen leve en los objetos (cara superior, sombra) y viñeta + grano ganan · contadores sin medio dígito (`contador(..., rueda=False)`, por defecto).

## La base (todos los estilos)
- **Fondo oscuro** (#0B101D–#16181F, con grano leve) y **un solo color de energía** que significa algo (lo activo, lo que lleva la energía o el dato). Brillo (glow) sólo en ese color y según el estado, no decorativo. Rojo sólo para peligro o error.
- **Objeto real reconocible**: la máquina, la pieza o el lugar como es (proporciones, partes que la gente conoce), nunca un ícono genérico. En corte, explotado o con la carcasa transparente cuando hay que ver adentro.
- **Una idea por imagen.** Un foco por cuadro.
- **El cambio cae en la palabra que lo nombra** (inicio de la palabra en `words.json`, ±2 cuadros). Nada quieto > 2 s; nada que se mueva sin que la voz lo nombre.
- **Etiquetas:** MAYÚSCULAS, cortas (≤ 3 palabras), con **línea guía** al punto exacto; números que cambian en vivo (contador, ×10, 100 → 0 %).
- **Subtítulos ARRIBA** (vara viral, 23-nov-2026: los virales y los jueces ciegos los piden en la zona superior): palabra por palabra, 1–3 palabras a la vez, Inter Black ~112 px en MAYÚSCULAS con contorno oscuro y sombra suave, centrados en y≈290–420 (bajo la barra de la plataforma), la palabra clave en una **píldora rellena** del color de energía con texto oscuro (`subtitulos(...)` por defecto; `estilo_clave="recuadro"` para el recuadro con manillas). Nunca tapan el foco: el sujeto se corre o la columna de texto se mueve. Lo demás importante (píldoras de gancho, avisos) va a y ≥ 430 para no chocar.
- **Texto secundario** (etiquetas, unidades, avisos) mínimo **44 px**, bold, con contorno de 4 px o placa oscura; si no cabe, se saca. Números protagonistas enormes (14–18 % del alto) y completos en la palabra que los dice.
- **Zona segura:** nada importante bajo 1580 px ni en los 160 px de la derecha; márgenes de 60 px.
- **Cuadro 0** ya muestra el gancho completo (nunca negro ni fundido). **Último cuadro empalma con el primero** (loop).

## Movimiento (reglas de claude-motion, MIT, con sus números)
- Todo es función del tiempo: `t` en segundos → cuadro. Nada al azar sin semilla.
- Curvas: **entradas** `bezier(0.16, 1, 0.3, 1)` · **salidas** `bezier(0.6, 0, 0.9, 0.35)` · **de un estado a otro** `bezier(0.65, 0, 0.35, 1)` · **algo que "aterriza"** con rebote `bezier(0.55, 0, 0.2, 1.12)` · lineal sólo para movimiento continuo (engranajes, flujo). Están en `kit_explica.ease_*`.
- Escalonado: palabras 0,09 s · ítems de lista 0,2–0,25 s. Una aparición de texto dura ~0,8 s.
- Salidas en la mitad del tiempo de la entrada (0,35–0,55 s contra 0,7–1,25 s). Las escenas se traslapan: nunca un corte a vacío.
- Tiempo de lectura: ≥ 1 s por frase corta + 0,25 s por palabra sobre 3; ≥ 2 s en el remate. **El texto no se mueve mientras se lee.**
- Un solo rebote elástico por video (el momento más fuerte).

## Los 5 estilos (propios; rotan, `docs/ROTACION.md`)
Escritos por nosotros. La idea de tener un menú de estilos viene de lemo-opuscar, pero sus textos no se copian: tienen licencia no comercial para compartir.
1. **Plano técnico:** líneas blancas finas sobre azul de Prusia profundo, el objeto se dibuja en orden de dibujante (contorno → piezas → cotas); energía: amarillo tiza. Para máquinas y "cómo se hace".
2. **Rayos X:** fondo negro, el objeto como radiografía translúcida (bordes claros, interior por densidad); energía: cian. Para "qué hay adentro de".
3. **Laboratorio nocturno:** fondo carbón, objetos planos con sombra corta, etiquetas HUD; energía: oro. Para mecanismos cotidianos (el estilo base).
4. **Pizarra:** fondo verde pizarra oscuro, trazos de tiza que se escriben; el mito se escribe y se borra de una pasada, la verdad se escribe en el mismo lugar; energía: naranja. Para mito + analogía.
5. **Escala:** fondo azul noche, zoom continuo entre escalas con contador (×1 → ×1.000.000) y regla que se estira; energía: verde menta. Para tamaños, distancias y números imposibles.

Cada estilo define: fondo, color de energía, trazo, tipografía de etiquetas, cómo entra un objeto y su efecto de sonido de firma. Están en `kit_explica.ESTILOS`.
