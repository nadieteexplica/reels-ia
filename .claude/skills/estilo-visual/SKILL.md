---
name: estilo-visual
description: Kit y criterios visuales de El viejo del dato para animar por código (fondo oscuro, un color de energía, objeto real con volumen, etiquetas con línea guía, subtítulos arriba con píldora, curvas de movimiento, loop; un solo estilo aprobado: laboratorio nocturno del beat v5), cada uno con su nivel de evidencia. Usar al hacer el storyboard y al animar.
---

# Estilo visual

Marco: `docs/REGLAS.md`. Aquí todo es **criterio** (punto de partida, se puede romper si el resultado le gana a los virales, anotando por qué), salvo lo marcado [DURA]. Niveles: **[MEDIDA]** nuestros números o algo que se ve objetivamente · **[PROBABLE]** principio conocido o varios virales · **[HIPÓTESIS]** opinión sin probar (no bloquea).

**Motor:** kit Python (`studio/plantilla/kit_explica.py`). Ganó a HyperFrames 2 a 1 en el duelo ciego del 23-nov-2026 [MEDIDA, una sola prueba]; HyperFrames queda de respaldo (`render-hyperframes.yml`). Render en el Mac (~1 min por 8 s con 6 procesos) o en Actions (`render-2d.yml`).

**Qué decide si se ve bien** (`docs/REGLAS.md` §3): métricas reales > el ojo de Tomás en el celular > jueces ciegos como orientación. La vara de los jueces es **relativa y en video**: el beat, con su sonido, contra un viral con /watch en el mismo tramo (`studio/duelo-visual/vara_relativa.py`, cuadros cada 0,25 s + audio descrito): ¿cuál se ve más profesional? ¿cuál deslizarías? Piso: ganar o empatar. Si el kit no llega en 3 vueltas, se prueba three.js en Actions.

## Base (todos los estilos)
- **[DURA]** Nada con derechos: objetos, fondos y tipografías propios o con licencia libre.
- **[MEDIDA] Texto legible en el celular o fuera:** subtítulos ~112 px; texto secundario ≥ 44 px bold con contorno o placa oscura; si no cabe, se saca (los jueces no pudieron leer etiquetas de 16–22 px).
- **[MEDIDA] Nada se corta ni queda bajo la interfaz:** subtítulos con la primera línea anclada en y≈300 y creciendo hacia abajo (el kit no deja pasar de y=250); nada importante bajo 1580 px ni en los 160 px de la derecha; márgenes de 60 px.
- **[MEDIDA] Lo que se dice y lo que se ve calzan:** el número en pantalla es el que dice la voz, completo en esa palabra (nada de medio dígito: `contador(..., rueda=False)` por defecto); la etiqueta dice lo del storyboard.
- **[PROBABLE] Subtítulos arriba**, palabra por palabra, 1–3 a la vez, MAYÚSCULAS, la palabra clave en una píldora rellena del color de energía (virales con /watch + jueces). Si hay un número gigante en pantalla, el subtítulo no lo repite (`subtitulos(..., ocultar=...)`) [PROBABLE: redundancia de Mayer].
- **[PROBABLE] Objeto real reconocible con volumen, sombra y brillo**, nunca un ícono plano (en corte, explotado o transparente si hay que ver adentro). Escala con referencias que se reconocen (persona legible, bus, edificio).
- **[PROBABLE] Una idea por imagen y el cambio cae en la palabra que la nombra** (inicio en `words.json`, ±2 cuadros); algo nuevo cada 2–3 s; nada quieto > 2 s mientras la voz habla.
- **[PROBABLE] Fondo oscuro + un solo color de energía** con brillo según el estado; rojo sólo para peligro.
- **[PROBABLE] Cuadro 0 ya compuesto** (nunca negro ni fundido) y **loop**: el último cuadro calza con el primero.
- **[PROBABLE] Ritmo: el cambio pasa DENTRO del plano** (aparece una etiqueta, corre un número, se mueve una pieza), donde el ojo ya está. Cortes y movimientos de cámara cuestan comprensión: sólo cuando cambia la idea, nunca para meter energía (lección 177: Tomás "no caché nada" con 4 cortes en 1,4 s y barridos bajo el texto). Guías:
  1. Sin barridos ni movimientos rápidos de cámara mientras hay texto en pantalla; el texto se lee quieto (≥ largo/17 s: ~17 caracteres por segundo, estándar de subtítulos).
  2. Ningún plano ni destello < ~0,3 s, salvo un impacto sin información.
  3. Un solo foco a la vez: lo nuevo aparece donde está el ojo o el movimiento lo lleva ahí.
  4. Ni frenético ni muerto: ni tramos > ~1,5 s sin ningún cambio, ni ráfagas de varios cambios en < 1 s.
  **Rango que funcionó [PROBABLE, 1 caso aprobado por Tomás: beat v5, `docs/referencias/virales/propio-beat-clavo-v5.md`]:** cámara rápida ≤ ~5 % del tiempo · ≤ ~0,3 s de cámara rápida o corte con texto encima · cambios dentro del plano ≥ ~1/s · cortes duros sólo al cambiar la idea (≤ 1 cada ~4 s) · tramo quieto ≤ ~1 s. La v4 (20 % de cámara rápida, 0,39 cambios/s) no le gustó.
  Se mide con `tools/ritmo.py` contra la banda de los virales de la biblioteca y con la prueba de primera vista (skill `qa-video`); decide el ojo de Tomás.
- **[HIPÓTESIS]** Revelaciones de escala con un movimiento de cámara lento (no crash zoom ni barrido); viñeta + grano quieto (el grano animado pesa 6 veces más: [MEDIDA]).

## Movimiento (claude-motion, MIT) [PROBABLE]
- Todo en función del tiempo; nada al azar sin semilla.
- Curvas: entradas `bezier(0.16,1,0.3,1)` · salidas `bezier(0.6,0,0.9,0.35)` · cambio de estado `bezier(0.65,0,0.35,1)` · aterrizaje con rebote `bezier(0.55,0,0.2,1.12)` · lineal sólo para movimiento continuo (`kit_explica.ease_*`).
- Salidas en la mitad del tiempo de las entradas; escenas que se traslapan (nunca corte a vacío); el texto no se mueve mientras se lee (≥ 1 s por frase corta + 0,25 s por palabra sobre 3; ≥ 2 s en el remate). Un solo rebote elástico por video.

## Estilo: uno solo aprobado (Tomás, 23-nov-2026) — la rotación está APAGADA
**Se usa sólo laboratorio nocturno, el del beat v5 aprobado** (`docs/referencias/virales/propio-beat-clavo-v5.md`): carbón, objetos con volumen, luz y sombra corta, etiquetas HUD, energía oro. Los otros 4 de `kit_explica.ESTILOS` quedan en pausa: no se usan sin un OK nuevo de Tomás. (La prueba con Plano técnico del 23-nov perdió contra un viral 3D en el gancho: "plano, de bajo presupuesto".)

Referencia de los 4 en pausa (no usar):
1. **Plano técnico:** líneas blancas sobre azul de Prusia; se dibuja en orden de dibujante; energía amarillo tiza. Máquinas y "cómo se hace".
2. **Rayos X:** fondo negro, objeto translúcido; energía cian. "Qué hay adentro de".
3. **Laboratorio nocturno:** carbón, objetos con volumen y sombra corta, etiquetas HUD; energía oro. Mecanismos cotidianos (base).
4. **Pizarra:** verde pizarra, tiza; el mito se escribe y se borra, la verdad en el mismo lugar; energía naranja. Mito + analogía.
5. **Escala:** azul noche, zoom continuo entre escalas con contador; energía verde menta. Tamaños y números imposibles.
