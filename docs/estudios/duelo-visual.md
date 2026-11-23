# Duelo visual a ciegas (23-nov-2026): kit Python vs HyperFrames

**Pedido de Tomás:** "lo visual no se decide por supuesto": el mismo beat en los dos motores, comparado a ciegas, y se queda el que gane.

**Cómo se hizo**
- Beat de prueba de 7,6 s tipo martinete (estructura A, texto propio, no se publica): `studio/duelo-visual/storyboard.json`, voz del narrador `out/voz-libre/duelo-visual/`.
- Dos agentes distintos, mismo storyboard, misma voz, mismo estilo ("laboratorio nocturno"), cada uno con autorrevisión de cuadros:
  - **Kit Python** (`studio/plantilla/kit_explica.py` + `studio/duelo-visual/python/render.py`): 39 s de render en el Mac (6 procesos).
  - **HyperFrames 0.9.84** (`studio/duelo-visual/hyperframes/`, `.github/workflows/render-hyperframes.yml`): 22 s en Actions (ubuntu, 4 vCPU, Chrome por software).
- `studio/duelo-visual/comparar.py` armó las mismas hojas a tamaño celular (gancho, beats, golpe cada 0,1 s, todo a 2 cps) con letras al azar; la clave quedó aparte. 3 jueces ciegos (sólo lectura), con miradas distintas (espectador exigente, espectador de 25 años con elección instintiva, diseñador de movimiento).

**Resultado: gana el kit Python, 2 a 1** (los tres "leve"; nota global promedio 7,7 contra 7,0).
- Python: se ve más terminado (bloque de madera con volumen, viñeta y grano, anillo de impacto, polvo, la cámara que se aleja en "Pero" vende la escala). Fallas: contador con medio dígito al congelar, recuadro de la frase clave más grande que la palabra, una etiqueta que no era la del storyboard, subtítulos en minúscula, el martillo final como ícono, sin loop real.
- HyperFrames: más fiel al storyboard y subtítulos más legibles (mayúsculas), sin fallas; pero fondo plano y pesado, objetos más planos, corte seco sin movimiento de cámara, sin loop real.

**Decisión:** el render visual sigue en Python (en el Mac o en Actions con `render-2d.yml`). HyperFrames queda como respaldo probado (el workflow funciona).

**Arreglado en el kit después del duelo:** contador sin medio dígito por defecto (`rueda=False`), subtítulos en MAYÚSCULAS sin puntuación final, el recuadro crece con las palabras ya dichas (también en dos líneas).

**Reglas que quedan (skill `estilo-visual`):** la etiqueta dice exactamente lo del storyboard; el último cuadro tiene que calzar de verdad con el primero; el objeto del remate es un objeto real, nunca un ícono en un círculo; las revelaciones de escala con movimiento de cámara, no con corte seco.
