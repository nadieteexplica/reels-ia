# 4-cuadros · ronda 1 · **NO APROBADO**

Promedio **7.5** (mínimo 8; ningún revisor bajo 7 en ningún criterio).

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| belleza | 7.0 | 7 | 00022 y 01075 se ven bien (rayas turquesa saturadas, barra cromada, azulejos, luz suave, 0,13-0,14 % quemado), pero el chorro sale rosado en esos dos cuadros, el 00560 es azul sobre azul con la tina pálida y plana abajo, y la cara de fantasma del 00121 queda menta sobre menta, con poco contraste. |
| personaje | 8.0 | 8 | Don Héctor en 00022 y 01075 calza con la ficha (gorro de espuma con punta, costados rapados, cejas gruesas, bigote gris, espuma en el pecho), con los ojos en y≈490 de 1280 (≈735 de 1920) y aire sobre la espuma; la piel sale más naranja y brillante que en la ficha y el susto del 01075 es moderado. |
| manos | — | — | no aplica |
| anatomia | — | — | no aplica |

## Bloqueantes y fallas automáticas (impiden aprobar)

1. 🛑 [B2] El agua del chorro y las salpicaduras sale rosada o salmón en estilo_00022 (plano 0) y estilo_01075 (plano 21), con un RGB medio de ≈178,143,121 sobre la cortina a la izquierda de la cabeza, mientras que en estilo_00121 (plano 4) y estilo_00560 (plano 12) es blanca (≈206-220 neutro). El mismo chorro cambia de color entre planos y el agua rosada no es como se ve en la vida real. — 0.73 s. **Arreglo:** Usar en los planos 0 y 21 el mismo material de gotas de los planos 4 y 12 (blanco o transparente, sin tinte) y volver a renderizar estos dos cuadros.

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. En el cuadro 0 (portada) la cortina detrás de él cuelga casi plana: no se lee que 'se le viene por detrás'. Sin esa amenaza visible, la portada es un señor duchándose y no plantea pregunta. — 0.73 s. **Arreglo:** Inflar la cortina en el cuadro 0 con un bulto redondo grande a la altura del hombro izquierdo (x≈60-330, y≈300-700 de 1280) casi tocándole la espalda, con sombra de contacto, como en 01075 pero más marcado.
2. El remolino es azul claro sobre azulejo azul y se pierde. La parte baja del anillo (y≈667-820 de 1280, es decir 1000-1230 de 1920) cae justo en la franja de subtítulos, y el borde izquierdo del anillo toca o se corta en x=0. — plano 12 · 18.67 s. **Arreglo:** Subir el remolino unos 80 px (de 1280) y achicarlo un 10-15 % o alejar la cámara para que quede entero y sobre y 1000 (de 1920). Darle contraste con bordes más blancos o un centro más oscuro, o bajar la saturación y desenfocar los azulejos detrás.
3. En el cierre, la cortina 'inflada' se lee como pliegues (bultos suaves en x≈100-330, y≈300-650) y el susto es moderado (cejas apenas arriba, ojos poco abiertos), así que el remate pierde fuerza. — plano 21 · 35.83 s. **Arreglo:** Hacer la cortina un globo claro que le empuje el hombro, y para el susto subir más las cejas, abrir más los ojos y echar la cabeza hacia atrás, en una pose sostenida.
4. La cara de fantasma del gancho se lee a medias: tiene poco contraste (menta sobre menta) y los ojos no coinciden: el izquierdo es un hueco oscuro y el derecho un anillo brillante convexo (x≈380-460, y≈320-420). — plano 4 · 4.03 s. **Arreglo:** Poner una luz rasante lateral (desde arriba a la izquierda) para hundir las sombras, hacer los dos ojos iguales (dos huecos oscuros) y oscurecer la boca en O.
5. En el borde izquierdo hay una pieza blanca sin identificar (x≈0-20, y≈380-540, con una barra horizontal en y≈515) cortada por el borde y detrás del remolino. El material no alcanza para saber si es una llave o utilería técnica. — plano 12 · 18.67 s. **Arreglo:** Si es la llave, encuadrarla para que se reconozca; si no, sacarla del cuadro.
