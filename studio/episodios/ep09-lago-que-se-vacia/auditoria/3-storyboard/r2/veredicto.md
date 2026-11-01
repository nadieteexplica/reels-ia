# 3-storyboard · ronda 2 · **NO APROBADO** · estilo realista

Promedio **7.5** (mínimo 8; ningún revisor bajo 7 en ningún criterio).

**2 rondas sin aprobar: no se abre otra.** Lo que sigue fallando son bloqueantes puntuales: esos planos se simplifican o se reemplazan por una plantilla del kit y la puerta 7 revisa bloqueantes en todo el render final. Si es guion o storyboard, se cambia la idea o se le pregunta a Tomás.

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| foco | 7.0 | 7 | cada frase tiene su plano y una idea por plano en 1-10 y 12-16, pero en el plano 11 (26.75) la voz dice 'Sale por el otro lado' y la ficha muestra directo la junta de los ríos: la salida del agua por el otro lado del glaciar no se ve. |
| ritmo | 8.0 | 8 | 16 planos en 45 s, con píldoras que entran en la palabra y un corte dentro del 6 (12.88-16.42); los planos largos (8, 11, 12, 16, de 3,7 a 4,6 s) se sostienen con un cambio continuo del nivel o del túnel, y la escala cambia G/M a tiempo. |
| viabilidad | 7.0 | 7 | 3 escenas con lago.py y 0 clips de Kling, pero el agua sigue de cerca en el plano 4 (a 1,6-2,2 m del agua, 80 m en 1,9 s), hay agua en corte en E2 y en E4 un río que sube y se devuelve, lo más difícil de hacer creíble en realista. |
| gancho_visual | 8.0 | 8 | en el cuadro 0 el trozo de hielo cae entre 0,1 y 0,7 s y el plano 16 termina en la cámara exacta del cuadro 0 (el loop cierra), pero 'aquí había un lago' todavía depende de la píldora porque no hay marca del nivel viejo. |

## Bloqueantes y fallas automáticas (impiden aprobar)

1. 🛑 [B14] La voz dice 'Sale por el otro lado' y se pasa del lago bajando (E1, plano 10) a la junta de dos ríos vista a 520 m (E4), un lugar nuevo que no tiene ni glaciar ni lago. Ningún plano muestra el agua saliendo bajo el hielo por el otro lado. Sin sonido, el agua café que entra al río turquesa no se conecta con el lago, así que E4 queda pegado sin un espacio que lo una (también es B13: lo que dice la voz no se ve). — plano 11 · 26.75 s. **Arreglo:** Mantener la misma escena E4 con un solo movimiento de cámara. Entre 26.75 y ~28.2, que el cuadro parta arriba con el frente del glaciar de E1 (de fondo, con neblina) y el agua café saliendo con fuerza de un arco en su base hacia el afluente. Después, la cámara baja siguiendo el afluente hasta la junta para 'se triplica'. El agua del túnel en los planos 9-10 tiene que ser del mismo café, así se lee como la misma agua.

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. [A1 sin arreglar] El cuadro 0 depende de la píldora para decir 'aquí había un lago'. La ficha sacó la marca del nivel del agua en las laderas que traía el paquete de gancho del guion. Además, lo único que se mueve es un dolly de 2,2 m (el témpano crece ~5 %), así que la acción no está en curso en el primer segundo (manual §4, Imagen). — plano 1 · 0.00 s. **Arreglo:** Poner la línea del nivel viejo en las dos laderas y en el frente del glaciar, a 31 m sobre el fondo: barro oscuro y mojado abajo, roca seca y clara arriba. Sin sonido se lee como 'aquí había agua'. Y que algo esté pasando desde el cuadro 0: agua que todavía chorrea del témpano y corre por un canal del barro hacia un charco (una textura animada sobre una malla delgada es barata).
2. [A2 sin arreglar] Estos son los dos planos con más riesgo de verse de juguete en realista. En el vaso (plano 4): un cubo perfecto, vidrio limpio y tres volúmenes que refractan (vidrio, agua, hielo) a 8 muestras dan ruido y negros en el vidrio. Además, si la cámara no queda a la altura del agua no se ve la parte hundida del cubo, que es lo que dice 'flota' en una foto. En el agua a ras (plano 3): la cámara va a 2 m del agua y avanza 80 m en 1,55 s (≈ 190 km/h), y el agua de cerca es lo más difícil de hacer creíble. — plano 4 · 7.25 s. **Arreglo:** Vaso: cubo con bordes derretidos y centro blanco con burbujas, vidrio con gotas de condensación y marcas, y menisco. Cámara a la altura de la línea del agua, para ver el ~90 % hundido a través del vidrio. Renderizar sólo este plano (66 cuadros) con 64 muestras y 12 rebotes de transmisión o más. Plano 3: subir la cámara a 6–8 m y acortar el avance a ~35 m, con desenfoque de movimiento y trozos de hielo en primer plano, para que se sienta la velocidad sin mostrar el agua tan de cerca.
3. [A3 sin arreglar] En 'levanta', el pie del hielo sube 4 m visto a ~230 m con 30 mm. En vertical 1080×1920 son unos 16–28 px (≤ 1,5 % del alto): en el teléfono el despegue no se ve y la mecánica queda sostenida sólo por la flecha y SE LEVANTA. Es riesgo de B13 justo en la frase que el guion marca como segundo punto de fuga. — plano 5 · 11.31 s. **Arreglo:** Corte seco en 'levanta' (11,31) a otra cámara de E2 (gratis, es la misma escena) a 80 m o menos del pie, encuadrando el contacto hielo-roca con el agua entrando en el hueco. Así los 4 m ocupan 80 px o más. El plano 5 queda en 9,45–11,31 (G: el lago sube y SE LLENA) y el corte nuevo va de 11,31 a 12,98, empalmando con la cámara del 6.
4. [A5 sin arreglar] La entrada al corte no tiene puente: se salta de un vaso a una tajada del valle sin un plano que muestre que es el mismo glaciar abierto (en el Ep. 4 la cortina se volvía transparente; en el Ep. 7 el corte se veía desde afuera). Además, con la cámara 85 m sobre el lago, ~25° hacia abajo y 30 mm, el borde de abajo del cuadro mira ~250 m bajo el nivel del lago. Si la roca cortada no llega tan hondo, abajo se ve vacío (B2/B3), sobre todo en el plano 8, donde la cámara se aleja. — plano 5 · 9.45 s. **Arreglo:** En los primeros ~0,6 s del plano 5, que la misma cámara muestre el glaciar entero y que la mitad de adelante baje o se desvanezca, dejando la cara cortada con un contorno blanco fino en el borde (eso la marca como capa de explicación). Hacer la roca del corte de 350 m o más bajo el lago y más ancha que el cuadro del plano 8.

## Verificación de la ronda anterior

| id | qué | arreglado |
|---|---|---|
| A1 | El cuadro 0 depende de la píldora para decir 'aquí había un lago'. La ficha sacó la marca  | **no** |
| A2 | Estos son los dos planos con más riesgo de verse de juguete en realista. En el vaso (plano | **no** |
| A3 | En 'levanta', el pie del hielo sube 4 m visto a ~230 m con 30 mm. En vertical 1080×1920 so | **no** |
| A4 | Como no hay personajes, la columna 'Cara (y)' queda en '—' y ninguna ficha dice a qué altu | sí |
| A5 | La entrada al corte no tiene puente: se salta de un vaso a una tajada del valle sin un pla | **no** |
