# Etapa 4 — Cuadros de estilo y cuadros de partida para Kling

**Criterios:** `belleza`, `personaje`, `manos`, `anatomia` (null si ningún cuadro muestra el interior del cuerpo; `manos` null si no se ven manos).
**Materiales:** cada cuadro en 720x1280, `ficha_personaje.jpg` (el protagonista aprobado) y `cuadros.json` (resolución, % quemado, brillo, saturación). El encargo puede traer `notas_de_uso` (para qué es cada cuadro).

Hay dos tipos de cuadro y se juzgan distinto:
- **De estilo** (escenario nuevo): define el look de todo el video. Se le muestra a Tomás después de ti.
- **De partida para Kling:** Kling **copia** lo que ve en este cuadro durante todo el clip. Un agarre malo, un objeto con el color equivocado o una cara rara se repiten en el clip entero.

## Revisa cada cuadro
1. **Manos.** En cuadros de partida, la mano tiene que estar **libre** (sin objeto) o con el objeto **apoyado** (en una mesa, en el carrito); nunca un agarre a medias. Si hay agarre: cada dedo toca el objeto, ninguno lo atraviesa, el objeto no flota entre los dedos. Mano deforme o con dedos de más/menos = bloqueante.
2. **Objetos** tal como deben verse en el video (material, color, transparencia, tamaño). Si un objeto se ve distinto de lo que dice la voz o de lo que es en la vida real, Kling lo va a "corregir" a mitad del clip.
3. **Personaje** igual a la ficha: pelo, polera coral con estrella, colores, proporciones de cara. Cara bien encuadrada (tercio superior, y≈350–900 de 1920, aire sobre el pelo).
4. **Anatomía** (si hay interior): cabeza de vidrio de perfil, fondo azul noche, anatomía real y limpia, un solo foco brillando, nada inventado, nada cortado, sin cráneo, sin ojos de caricatura. Lo importante queda sobre la franja de subtítulos (y < 1000).
5. **Belleza:** luz suave de estudio o una fuente fuerte cálida para lo dramático, colores saturados sin quemar, fondo vivo, nada lavado ni plástico, sin artefactos de render (ruido, piezas atravesadas, texturas estiradas).
