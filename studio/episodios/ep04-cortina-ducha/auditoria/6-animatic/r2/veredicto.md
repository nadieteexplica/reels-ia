# 6-animatic · ronda 2 · **NO APROBADO**

Promedio **7.88** (mínimo 8; ningún revisor bajo 7 en ningún criterio).

**2 rondas sin aprobar: no se abre otra.** Lo que sigue fallando se simplifica o se reemplaza por una plantilla del kit y el video sigue: en el animatic, la puerta 7 revisa bloqueantes en todo el render final (incluidos los planos simplificados). Si es guion o storyboard, se cambia la idea o se le pregunta a Tomás.

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| belleza | 8.0 | 8 | paleta turquesa/blanca coherente y luz suave en todos los planos (P1 0.04, P16 24.43, P21 33.99); la tela de la cortina se lee como material real; nada quemado ni lavado en zonas clave |
| animacion | 7.5 | 7 | P16 ya sostiene el perfil mientras la cortina se infla (24.43–26.30) y el susto de P21 se lee (34.28→34.57), pero en el remate de P21 la cortina casi no se mueve (33.99–36.01) y P17 resuelve la cortina con un salto de 1 cuadro (26.53) |
| claridad | 7.5 | 7 | la cadena se entiende hasta 'la presión baja' (16–21 s: remolino, anillo azul y 'BAJA PRESIÓN'), pero en 23 s 'AIRE DE AFUERA' sigue con flechas horizontales desde izquierda y derecha dentro del plano de la cortina y la cortina no se mueve en 22–24 s: el 'de afuera / hacia ti' recién se entiende al cortar en 24.4 s |
| ritmo | 8.0 | 8 | todos los planos del encargo cambian algo cada 1–2 s (quieto_max_s ≤ 0,2); el único tramo calmo es la cortina cerrada de P17 (26.68–27.88), sostenido por el subtítulo |
| gancho | 7.0 | 7 | el cuadro 0 y todo 0.00–1.00 s siguen siendo un hombre tranquilo con los ojos cerrados bajo la ducha (gancho.jpg); el personaje con la espuma en punta tiene gracia, pero la cortina recién actúa en el corte de 1.41 s y la cara de fantasma en 3.2 s |
| subtitulos | 9.0 | 9 | 97/97 palabras en pantalla, 0 desfases y 0 fuera de zona (checks.json); cajas entre y 1022–1214, siempre bajo la cara; tildes correctas en pantalla (ESTÁS, PRESIÓN, SOLUCIÓN, AHÍ SÍ, FRÍA, MÁS) y en etiquetas ('NO SOLO' sin tilde es correcto) |
| audio | 8.0 | 8 | no lo puedo escuchar: por cifras está en rango, −14.1 LUFS, true peak −1.4 dBTP y la voz 10.4 dB sobre música y efectos en las pausas (mínimo, con ducking) |
| precision | 8.0 | 8 | las etiquetas calzan con el guion y las fuentes (¿aire caliente? ✗ no solo; agua caliente más fuerte; agua fría igual pasa; flecha de aire hacia abajo; remolino de frente a través de la cortina, eje perpendicular a ella; baja presión en el centro; cortina pesada 'cuesta moverla'); lo único ambiguo son las flechas laterales de 23 s, que sugieren aire desde los costados de la ducha y no desde afuera |

## Bloqueantes y fallas automáticas (impiden aprobar)

1. 🛑 [B2] P17 abre con ~0,17 s (26.34–26.50, unos 5 cuadros) de Don Héctor de espaldas y en 26.53 (E21) la cortina pesada aparece entera en un solo cuadro con la cámara fija: el personaje desaparece de golpe y se lee como un flash entre P16 y la cortina, no como una cortina que cae (lo introdujo el arreglo de A3) — plano 17 · 26.38 s. **Arreglo:** empezar P17 con la cortina ya cerrada: sacar los cuadros 26.34–26.52 y sostener la cortina cerrada desde 26.34 (el arreglo que ya proponía A3); si la caída es buscada, animarla de arriba abajo en ≥ 6 cuadros

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. [A4 sin arreglar] el cuadro 0 (portada y lo que decide visto vs. deslizado) es un hombre duchándose tranquilo con los ojos cerrados; la acción del gancho (la cortina que se le viene encima) empieza recién a los 1.41 s y la cara de fantasma a los 3.2 s — plano 1 · 0.00 s. **Arreglo:** en el plano 1, adelantar la animación de la cortina para que desde el cuadro 0 ya venga inflada por detrás y le roce el hombro (que abra un ojo al contacto); y usar el cuadro de la cara de fantasma (~3.6 s) como portada (videoCoverMilliseconds) para la grilla
2. [A5 sin arreglar] las flechas naranjas de 'AIRE DE AFUERA' entran por la izquierda y la derecha, en el plano de la cortina: se lee como aire que viene de los costados dentro de la ducha, y en todo 22–24 s no se ve la cortina moverse hacia el centro, así que el 'mete la cortina hacia ti' recién se entiende al cortar a los 24.4 s — plano 15 · 23.00 s. **Arreglo:** cambiar las flechas laterales por flechas que vienen desde la cámara hacia el centro (en perspectiva, achicándose) y hacer que las rayas de la cortina se abomben hacia el anillo de baja presión en este mismo plano
3. [A8 sin arreglar] la cortina nueva que baja corta al personaje a la altura del cuello: por ~0.5 s se ve un torso sin cabeza, con espuma que parece estar en la espalda (la ficha la pone en el pecho); material insuficiente para verificar si es espalda o pecho — plano 17 · 26.40 s. **Arreglo:** empezar el plano con el borde de la cortina ya bajo los hombros, o cortar directo a la cortina pesada cerrada (27 s) y dejar al personaje fuera de este plano
4. [A6 sin arreglar] en 'FANTASMA' la cortina de la izquierda (x 0–500, y 250–1000) es una onda suave y desenfocada que casi no cambia entre 33.99 y 36.01: el remate prometido (la cortina pesada que igual se infla) no se ve, sólo la cara de susto — plano 21 · 34.86 s. **Arreglo:** en la misma cámara, justo en 'FANTASMA' (~34.9) que la cortina se infle hacia su hombro y aparezca la cara de fantasma marcada en la tela de los planos 3–4 (reusar ese desplazamiento), con un shake corto; cierra el chiste y el loop con el gancho

## Verificación de la ronda anterior

| id | qué | arreglado |
|---|---|---|
| A1 | aparecen manchas de espuma blanca sobre la cortina sin ninguna fuente (no hay personaje en | sí |
| A2 | Don Héctor pasa de perfil mirando a la derecha (25.77) a estar de frente a cámara con cara | sí |
| A3 | plano general de espaldas: el cuerpo de Don Héctor termina bajo la espuma, sin caderas ni  | sí |
| A4 | el cuadro 0 (portada y lo que decide visto vs. deslizado) es un hombre duchándose tranquil | **no** |
| A5 | las flechas naranjas de 'AIRE DE AFUERA' entran por la izquierda y la derecha, en el plano | **no** |
| A6 | en 'FANTASMA' la cortina de la izquierda (x 0–500, y 250–1000) es una onda suave y desenfo | **no** |
| A7 | el remolino celeste sobre baldosas celestes, visto a través de la cortina lechosa, tiene p | sí |
| A8 | la cortina nueva que baja corta al personaje a la altura del cuello: por ~0.5 s se ve un t | **no** |
