# Etapa 3 — Storyboard (fichas de plano)

**Criterios:** `foco`, `ritmo`, `viabilidad`, `gancho_visual`.
**Materiales:** `storyboard.md` (una ficha por plano, en tabla), `guion.md`, `ficha.jpg` si el episodio tiene personajes propios. **Contexto:** manual §4, §5 y §8; el **estilo del episodio** (`estilo` del encargo, reglas en `estilos.md`); `studio/plantilla/KIT.md` (lo que ya existe y se puede reutilizar).

**Si el estilo es realista**, en **viabilidad** mira además cómo llega cada escena a verse real: materiales con textura (assets CC0, escaneos), luz y lente reales, render con las muestras suficientes (GPU) o Kling partiendo de un cuadro 3D nuestro (mantiene el look; nada de video fotorrealista de IA, que Tomás rechazó) para lo que en render se vería de juguete (personas, animales). Una escena que depende de un personaje estilizado (el protagonista de MakeHuman de los episodios anteriores, un muñeco) o de un plano que en render va a verse de plástico es **sugerencia de prioridad 1**, con la alternativa (de espalda, fuera de foco, manos con guantes, Kling). Desde el Ep. 5 el realista es la línea de la cuenta (`docs/ESTILO_REALISTA.md`): cada ficha realista debe decir **dónde está el sol** respecto de la cámara (nunca de frente), **qué hay detrás de lo que flota** (fondo lejano o cielo, nunca el suelo lejano), el **micro-movimiento de lo vivo** (nada quieto más de 1 s) y, si la cámara panea hacia algo que nombra la voz, que **nada lo tapa**. Si falta, es sugerencia de prioridad 1 (en el Ep. 5 esos cuatro puntos costaron un animatic entero).

El storyboard es **la receta del editor**: cada ficha ya trae lo que después vas a exigir en el animatic. Se audita **antes de gastar** render: acá cambiar es gratis. Sé duro con lo que el pipeline no logra y con los planos que no se van a poder leer.

## Cada ficha tiene (columnas obligatorias; el chequeo automático ya verificó que no estén vacías)
`# · Tiempo · Frase · Escena · Plano (escala) · Plantilla · Acción visible · Se entiende sin sonido · Cambio (≤ 2 s) · Cámara · Cara (y) · Gráfico (dónde) · SFX · Origen`

**Escena ≠ plano:** una escena es una actuación animada que se arma una vez y se filma con una o varias cámaras (lo caro: el Ep. 2 armó ~45); un plano es cada corte (otra cámara de la misma escena, un detalle) y es barato. Máximo 12 escenas; cortes, los que hagan falta.

## Revisa
0. **Lectura en orden, sin sonido (Ep. 6, vergüenza máxima):** lee **sólo** la columna "Se entiende sin sonido" de arriba abajo, como si fuera el video. ¿Cuenta la historia completa? ¿El primer plano (0–3 s) es de situación: quién, dónde y la acción del gancho? ¿Cada personaje del relato aparece reconocible al menos una vez, y los que comparten escena se ven juntos en un plano abierto? ¿Hay detalles o primeros planos sin un plano antes que diga de dónde salen? ¿Cada línea de la voz que dice que algo pasa tiene un plano donde **eso se ve**? Si no, es **bloqueante B13/B14** ya en el storyboard: acá cambiarlo es gratis. Un set donde la cámara no cabe (interior chico, personajes que no se pueden ver al armar) sin plano abierto posible es sugerencia de prioridad 1: cambiar el set.
1. **Foco:** una idea por plano y cada frase de la voz con su imagen. Interior del cuerpo: un solo foco. Lo invisible con una metáfora clara.
2. **Acción visible:** ¿la acción se entiende en **una foto**? "El ratón parpadea" no se lee en una foto; "el ratón escupe una llamarada" sí. Una acción que no se lee en una foto es sugerencia de prioridad 1.
3. **Ritmo:** algo cambia cada 1–2 s y nunca más de 2 s sin cambio (en 50 s, unos 25–50 cambios: cortes dentro de las escenas, acciones, gráficos, transformaciones); la columna "Cambio" dice cuál en cada plano largo; cambio de escala cada 8–12 s; máximo 2 transiciones especiales. Si el ritmo se apoya en armar escenas nuevas en vez de cortar dentro de las que hay, es sugerencia de prioridad 1.
4. **Encuadre y gráficos:** la cara del personaje entre y≈300 y 950; ningún gráfico (lupa, píldora, recuadro) encima de la cara. Si la ficha pone el gráfico en la misma zona x **y** y que la cara, es **bloqueante B5** desde ya; si sólo comparten la franja vertical, es aviso (la prueba lo mide).
5. **Viabilidad:** ¿cada escena usa una plantilla del kit o una variación chica (máx. 6 escenas, 3 a medida)? Un plano "a medida" muy complejo (multitudes, agua, pelo largo, contacto de manos con objetos en render) es sugerencia de prioridad 1: proponer cómo simplificarlo. Manos agarrando objetos en render = bloqueante B1 (salen de Kling o se rehacen sin objeto).
6. **Gancho visual:** cuadro 0 fuerte (absurdo o pregunta, sin fundido), símbolo que se repite, final que empalma con el cuadro 0.

En `problemas`, `plano` es el número del storyboard y `segundo` el tiempo de ese plano.
