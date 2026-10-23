# Etapa 6 — Animatic, revisión plano por plano

El animatic es el video **completo** con la voz, los subtítulos y los gráficos, renderizado más chico y con menos muestras (un poco de ruido es normal: no lo cuentes). Se revisa **antes** del render final: acá arreglar es barato. Otro revisor mira el video completo (gancho, ritmo general, subtítulos, audio); tú vas plano por plano.

**Criterios (para todos los planos):** `belleza`, `animacion`, `claridad`, `ritmo` y, **sólo si el estilo del encargo es realista**, `realismo` (escala en `estilos.md`; di qué plano delata el 3D y por qué). Belleza se juzga según el estilo (`estilos.md`).
**En realista** (`estilos.md`): recorre las **señales de maqueta** en tus planos y anota todas en `delatores` (plano, segundo, zona). Revisa la **vida**: lo vivo nunca quieto más de 1 s (una rana que respira, una persona que flota y busca el equilibrio). En realista la puerta 6 puede correr **sobre el render final** (no un animatic de baja resolución): juzga igual, pero el ruido de pocas muestras ya no es excusa.
**Materiales:**
- `planos/PNN.jpg`: 6–12 cuadros por plano (4 por segundo), en orden de tiempo (izquierda→derecha, arriba→abajo), con el segundo de cada uno.
- `planos.json`: inicio, fin y origen de cada plano, y las **medidas automáticas**: `mov_mediana`, `quieto_max_s`, `fondo_liso` (ver comun.md, "Movimiento").
- `contacto.jpg`: 1 cuadro por segundo del video entero (para ubicarte).
- `eventos/E*.jpg` y `eventos.json`: lo que marcaron los detectores (antes | después).
- `ficha.jpg`: los personajes de este episodio.
- Contexto: `guion.md` (qué dice la voz), el manual. En `checks.json` están los chequeos automáticos por plano (ojos tapados, quemado, plano quieto, fondo liso): no los repitas, sólo di si ves algo que se les pasó.

## Por cada plano
1. **Bloqueantes** (lista cerrada de comun.md): piezas que se atraviesan o flotan (B1), cambios de golpe o utilería técnica a la vista (B2), personaje distinto a la ficha (B4: compara la cara con `ficha.jpg`), cara tapada (B5), algo clave cortado (B11).
2. **Imagen ↔ voz:** ¿la imagen muestra lo que la voz dice en ese momento? Si no ayuda a entender, es sugerencia de claridad.
3. **Encuadre:** caras entre y≈300 y 950; nada importante bajo y 1000 (subtítulos) ni bajo y 1250 (interfaz de la app).
4. **Animación:** ¿el personaje actúa (una acción que se lee en una foto, anticipación, expresión) o está tieso? Usa las medidas antes de decir "congelado".
5. **Belleza:** luz, color, materiales, composición. El ruido de las pocas muestras del animatic no cuenta.
6. **Ritmo del plano:** ¿cambia algo en pantalla al menos cada 2 s? (`quieto_max_s` lo mide)
7. **Cada evento:** ¿defecto o buscado? Respóndelo en `eventos`.

Al final, ordena tus sugerencias por impacto (máximo 8). En `problemas`, `plano` es el número del plano y `segundo` el tiempo exacto del cuadro donde se ve (el rótulo de la imagen).
