# Etapa 4 — Cuadros de estilo y cuadros de partida para Kling

**Criterios:** `belleza`, `personaje`, `manos`, `anatomia` (null si ningún cuadro muestra el interior del cuerpo; `manos` null si no se ven manos) y, **sólo si el estilo es realista**, `realismo` (obligatorio, con número: escala en `estilos.md`).
**Materiales:** cada cuadro en 720x1280, `ficha_personaje.jpg` (los personajes de este episodio), `cuadros.json` (resolución, % quemado, brillo, saturación, negros) y, en realista, `ref_*.jpg` (fotos reales del tema, sólo para comparar). El encargo puede traer `notas_de_uso` (para qué es cada cuadro) y trae `estilo` (animado o realista).

Hay dos tipos de cuadro y se juzgan distinto:
- **De estilo** (escenario nuevo): define el look de todo el video. Se le muestra a Tomás después de ti.
- **De partida para Kling:** Kling **copia** lo que ve en este cuadro durante todo el clip. Un agarre malo, un objeto con el color equivocado o una cara rara se repiten en el clip entero.

## Revisa cada cuadro
1. **Manos.** En cuadros de partida, la mano tiene que estar **libre** (sin objeto) o con el objeto **apoyado** (en una mesa, en el carrito); nunca un agarre a medias. Si hay agarre: cada dedo toca el objeto, ninguno lo atraviesa, el objeto no flota entre los dedos. Mano deforme o con dedos de más/menos = bloqueante.
2. **Objetos** tal como deben verse en el video (material, color, transparencia, tamaño). Si un objeto se ve distinto de lo que dice la voz o de lo que es en la vida real, Kling lo va a "corregir" a mitad del clip.
3. **Personaje** igual a la ficha **de este episodio** (`ficha_personaje.jpg`): forma, colores, proporciones, ojos, pelo y ropa. Cara bien encuadrada (tercio superior, y≈350–900 de 1920, aire sobre la cabeza). No lo compares con personajes de otros videos.
4. **Anatomía** (si hay interior): cabeza de vidrio de perfil, fondo azul noche, anatomía real y limpia, un solo foco brillando, nada inventado, nada cortado, sin cráneo, sin ojos de caricatura. Lo importante queda sobre la franja de subtítulos (y < 1000).
5. **Belleza según el estilo** (`estilos.md`). **Animado:** luz suave de estudio o una fuente fuerte cálida, colores saturados sin quemar, fondo vivo. **Realista:** luz con sombras reales, materiales con textura e imperfecciones, color natural con contraste, lente real. En los dos: nada lavado, sin artefactos de render (ruido, piezas atravesadas, texturas estiradas).
6. **Realismo** (sólo realista): nota con la escala de `estilos.md`, diciendo qué se ve real y qué delata el 3D (plano y detalle). Si hay `ref_*.jpg`, compara materiales, luz y escala contra esas fotos. Un cuadro de estilo realista define el look de todo el video: si no llega a 8, di exactamente qué cambiar (material, luz, lente, personaje) para que llegue.
