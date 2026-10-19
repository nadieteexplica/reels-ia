# Etapa 6 — Video final, revisión por tramo

Revisas un **tramo de planos** del video final. Otro revisor mira el video completo (gancho, ritmo general, subtítulos, audio); tú vas plano por plano con lupa.

**Criterios (sólo para tu tramo):** `belleza`, `animacion`, `claridad`, `ritmo`.
**Materiales:**
- `planos/PNN.jpg`: 6 cuadros por plano, en orden de tiempo (izquierda→derecha, arriba→abajo), con el segundo de cada uno.
- `contacto.jpg`: 1 cuadro por segundo del video entero (para ubicarte).
- `eventos/E*.jpg` y `eventos.json`: lo que marcaron los detectores automáticos en tu tramo (antes | después).
- `planos.json`: inicio, fin y origen de cada plano (render o kling).
- `ficha.jpg`: el protagonista aprobado (cara, pelo, ropa).
- Contexto: `guion.md` (qué dice la voz) y el manual.

## Por cada plano de tu tramo
1. **Bloqueantes** (ver reglas comunes): dedos y objetos, cosas que aparecen o cambian de golpe entre dos de los 6 cuadros, pantalla vacía, personaje distinto, cara tapada, interior confuso, texto con faltas.
   - **Personaje:** compara la cara de cada plano con `ficha.jpg`. Si en un plano tiene **otra cara** (ojos más grandes o redondos, cejas más gruesas, otra nariz, otra forma de cara, más "caricatura" o más "realista", otro pelo), es el **bloqueante 4**, aunque parezca "el mismo personaje en otro estilo". El espectador lo nota como otra persona. Mira con lupa los planos de origen `kling` (`planos.json`): Kling tiende a cambiarle la cara a mitad del clip.
   - **Objetos que cambian:** un objeto que cambia de material, color o forma entre dos cuadros del mismo plano (material, color, transparencia o forma; por ejemplo, una pelota que cambia de color) es el **bloqueante 2**.
2. **Imagen ↔ voz:** con el guion y los segundos, ¿la imagen muestra lo que la voz dice en ese momento? Un plano que no ayuda a entender = problema de claridad.
3. **Encuadre:** cabezas, manos u objetos clave cortados por el borde; cara en el tercio superior; nada importante bajo y=1250 (la franja de subtítulos y la interfaz de la app).
4. **Animación:** ¿el personaje actúa (anticipación, expresión, poses claras) o está tieso? ¿Movimientos de goma, deslizamientos de pies, brazos que atraviesan el cuerpo?
5. **Belleza:** luz, color, materiales, ruido de render, piezas que se atraviesan, bordes raros, look plástico o lavado.
6. **Ritmo del plano:** ¿cambia algo en pantalla al menos cada 2 s? ¿La cámara se mueve?
7. **Cada evento** de tu tramo: ¿defecto o buscado? Respóndelo en `eventos`.

En `problemas`, `plano` es el número del plano y `segundo` el tiempo exacto del cuadro donde se ve (el rótulo de la imagen).
