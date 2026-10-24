# 6-animatic · ronda 1 · **APROBADO** · estilo realista

Promedio **8.0** (mínimo 8; ningún revisor bajo 7 en ningún criterio; realismo: ningún revisor bajo 8).

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| belleza | 8.0 | 8 | Contraluz azul con desenfoque real en la rana (P1 0.04), hora dorada en el salar con sombras largas (P3 4.21, P10 18.66) e interior rojo con negros de verdad (P6 9.70); lo único feo es el borrón oscuro sin sujeto de P2 2.86 a P3 3.18. |
| animacion | 7.0 | 7 | Cámara y capas muy bien animadas (flecha que nace y se achica en P6 9.70→10.87, flechitas que aparecen en cada molécula en P7 12.87), pero la rana es una estatua rígida en P1/P2/P4/P8 (misma pose en 14.09 y 16.96) y Pete sólo levanta la cabeza (P10, mov_mediana 0.75). |
| claridad | 8.0 | 8 | Cada frase tiene su imagen (revelado del imán P3 3.44→4.21, 'cada molécula' P7 12.64–14.01, IMÁN vs GRAVEDAD P8 15.66), salvo el remate del gancho: en 2.86 y 3.18 la rana no se ve mientras la voz dice 'sostiene'. |
| ritmo | 9.0 | 9 | Todos los planos tienen quieto_max_s ≤ 0,33 y algo nuevo cada 0,5–1 s (líneas 8.83, flecha 9.70, píldora 10.87; flechas en P8 14.61/14.87/15.66); los planos de 2,5–3,3 s (E13, E17, E20, E25) siguen cambiando. |
| realismo | 8.0 | 8 | Rana escaneada (P1, comparable a la foto real 1), fresa con semillas (P9 17.35), imán con óxido y cables (P3 4.47) y salar de costra hexagonal (P10) se ven 3D realista con DdC y sombras de contacto; delatan el 3D las células lisas y brillantes como gelatina (P5 6.50), el refri de bordes perfectos sin manilla ni junta y el pantalón brillante tipo látex de Pete (P10 18.66). |
| gancho | 7.0 | 7 | Cuadro 0 (0.00): rana real nítida al centro con las patas colgando, bonita y buena portada, pero el fondo azul del tubo se lee como acuario y 'flotando' en agua no sorprende; que está en el aire recién se insinúa con la píldora SIN HILOS en 2 s. |
| subtitulos | 8.0 | 8 | 119/119 palabras, desfase 0 y 0 fuera de zona; tildes correctas en todo lo visible (CÓMO, IMÁN, MOLÉCULA, QUÉ, DÉBIL, GASTARÍA, AHÍ SÍ, FLOTARÍAS); lo flojo: 'HACERTE FLOTAR A' sale más chico (25,27 s) y el texto pisa el cuerpo de Pete en 25 s y 27-28 s (la cara no). |
| audio | 8.0 | 8 | No lo puedo escuchar: -14,2 LUFS y -1,5 dBTP, ambos en rango; audio.json no trae la diferencia voz/música, así que el 15-20 dB del manual no se puede verificar. |
| precision | 9.0 | 9 | Las píldoras calzan con el guion y las fuentes (≈ 40 TESLAS, MÁS DEL DOBLE, MILES DE VECES / MÁS DÉBIL, ≈ 1 GIGAVATIO / 1 REACTOR NUCLEAR, fresa de Harvard Gazette) y SIMULACIÓN cubre toda la parte hipotética (24-38 s); único detalle: en 37 s Pete flota ~1,4 m sobre el imán y no en su boca 'donde quepas', como la rana. |

## Bloqueantes y fallas automáticas (impiden aprobar)

Ninguno.

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. Los pernos de la tapa del imán, desenfocados y encendidos por el sol cálido, se ven como un pedestal beige/oscuro justo bajo la rana (P1 0.93–1.07, E2) y como un dedo al lado de sus patas en todo P8 (14.09–16.96, también E21); contradice 'nadie la sostiene'. — plano 1 · 0.93 s. **Arreglo:** Sacar o correr los pernos que quedan en el eje de fondo de la cámara (o bajarles el brillo a gris oscuro) en los planos de la rana: P1, P2, P4 y P8.
2. el fondo azul parejo del tubo hace que la rana se lea como si nadara en un acuario: 'esta rana está flotando' no parece imposible en el segundo que decide visto vs. deslizado — plano 1 · 0.00 s. **Arreglo:** poner desde el cuadro 0 una píldora 'EN EL AIRE' (como la de SIN HILOS del final) y bajar la saturación del azul del fondo hacia el gris claro de laboratorio de la Foto real 1; si sobra tiempo, inclinar la cámara para que se vea el aire entre la rana y la boca oscura del imán
3. El armado del imán se ve como error de render: en 27.33 el tanque completo aparece de golpe flotando en el aire (E31, 1 cuadro), en 27.76 cae un cilindro negro puro sin luz ni material (E32) y la sombra en el suelo es la misma antes y después de que llegue el tanque (26.64 vs 28.88: misma área oscura, ~27 %), o sea la sombra del imán está antes que el imán. — plano 13 · 27.76 s. **Arreglo:** Que el tanque baje desde fuera del cuadro con desenfoque de movimiento (o suba desde el suelo) en vez de aparecer; darle al núcleo el mismo acero del tanque o dejarlo ya adentro; animar la visibilidad de sombras junto con la de cámara.
4. Los 5 cables aparecen enteros en 1 cuadro (E41, 33.07) y se ven como cuchillas planas azul oscuro con punta afilada que terminan en el borde del imán sin conectarse (E42 33.60); la punta asoma como una aleta detrás del imán en P16 (37.21). — plano 15 · 33.39 s. **Arreglo:** Cables redondos de goma negra con una caja de conexión en el imán; que crezcan desde el imán hacia las torres con el frente avanzando (no de golpe), dejando la línea naranja como capa de energía encima.
5. En 'ahí sí flotarías' Pete sale disparado del imán (36.64→36.92 sube casi su altura en 0,28 s, E46) y después flota tieso con los brazos pegados al cuerpo: se lee como salto, no como flotar. — plano 16 · 36.92 s. **Arreglo:** Subida con ease de ~0,8 s y una actuación de equilibrio: brazos un poco abiertos, mira sus pies y luego a cámara (sirve el clip de Mixamo de sorpresa).

## Avisos automáticos

- cara_al_borde · plano 10: Pete_ojoL en (319, 189) · 20.90–21.30 s
- cara_al_borde · plano 10: Pete_ojoR en (279, 190) · 20.90–21.20 s
