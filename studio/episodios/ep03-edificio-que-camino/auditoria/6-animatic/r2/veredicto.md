# 6-animatic · ronda 2 · **APROBADO**

Promedio **8.38** (mínimo 8; ningún revisor bajo 7 en ningún criterio).

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| belleza | 8.0 | 8 | Ladrillo, cielo y patas amarillo/celeste se ven limpios y bien iluminados (P02 1.33, P21 32.15, P23 35.69); lo más pobre es la vista cenital de P25-P26 (39.51-42.24), con textura de tierra a manchas y el edificio como una T gris plana, y el suelo liso que llena la mitad baja en P10 y P24. |
| animacion | 8.0 | 8 | Las patas se alternan con pies levantados (P02 1.62-2.77, P21 32.49-33.00), la bola de demolición entra columpiándose (P11 17.20-17.40), las torres crecen piso a piso (P09 12.94-13.14) y la muleta da un paso con 'camine' (P24 38.59-38.87); P25 casi no tiene acción (mov_mediana 0,64), sólo entran los rieles. |
| claridad | 8.3 | 8 | Cada imagen muestra lo que dice la voz: torres nuevas con 'estorbaba' (P09), bola con ✕ DEMOLER (P11), cambio de grupo con flechas en 'luego cambian' (P21), muletas en 'muletas' (P23-P24) y rieles con ✕ RIELES (P25-P26); el cuadro 0 sigue leyéndose más 'edificio' que 'edificio con patas' (A7 abierto). |
| ritmo | 8.7 | 8 | ningún plano pasa 0,6 s sin cambio (quieto_max_s 0–0,6) y los contadores cambian cada ~0,3 s en P27, P29 y P33; el más lento es P32 (52.30–54.00, sólo acercamiento y subtítulos) |
| gancho | 7.0 | 7 | la frase 'este edificio de cinco pisos se fue caminando' más el corte a las patas en paso a 1,29 s (gancho.jpg 1.40 s) sujetan, y en 0–1,29 s las patas ya se mueven (mov_mediana 4,32); pero la portada (cuadro0) sigue mostrando las patas como una franja de ~90 px (y≈840–930, ~5 % del alto) con la mitad de abajo de tierra lisa, y el grupo amarillo sube apenas ~30 px: en el teléfono se lee 'edificio sobre gatas', no 'edificio con patas dando un paso' |
| subtitulos | 9.0 | 9 | 181/181 palabras, desfase 0, todas las cajas dentro de x 139–866 · y 1022–1217, tildes bien (SHANGHÁI, CAMINÓ, DEMORÓ, DÍAS, PRÁCTICA, APRENDIÓ, ROBÓTICAS, TÉCNICO), sin caras que tapar; la puntuación (incluido ¿?) se omite de forma pareja como estilo, y el tamaño baja en algunos bloques (19–20 s, 15 s) sin perder legibilidad |
| audio | 9.0 | 9 | no lo puedo escuchar: por cifras, −14,0 LUFS y −1,5 dBTP dentro de rango, y la voz queda 12,8 dB sobre música y efectos medidos en las pausas (mínimo, por el ducking) |
| precision | 9.0 | 9 | 5 hileras de ventanas = 5 pisos, Escuela Lagena, 1935, Shanghái, 7.600 t con 'más de' en la voz, 198 patas, dos grupos, 21°, 62 m, 18 días, 85 años y la sala de 2003 movida sin patas, todo coincide con guion y fuentes; 'CÁMARA RÁPIDA' marca el paso acelerado (1,9–4,5 s). No alcanzo a ver el valor final del contador de metros de la sala (55,5 s marca 61 m): por China Daily debe detenerse en 66 m, no en 62 |

## Bloqueantes y fallas automáticas (impiden aprobar)

Ninguno.

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. [A3 sin arreglar] el cuadro 0, que además es la portada, no vende 'patas': la fila de patas es una franja chica a media altura, ningún grupo está levantado y la mitad de abajo es tierra lisa; recién en el plano 2 se ve el edificio entero sobre patas, y desde lejos — plano 1 · 0.00 s. **Arreglo:** bajar y acercar la cámara del plano 1 para que las patas queden más grandes, justo sobre los subtítulos (y≈850–1000), y partir el ciclo de paso con el grupo A (amarillo) en el aire en el cuadro 0; el plano 36 usa la misma toma para que el loop siga calzando
2. [A7 sin arreglar] En el cuadro 0 (portada), las patas, que son lo imposible, son una franja delgada (y≈820-940, ~7 % del alto) bajo un edificio grande. En el teléfono se lee 'edificio sobre algo' más que 'edificio con patas'. — plano 1 · 0.04 s. **Arreglo:** Bajar y acercar la cámara para que las patas ocupen 20-25 % del alto, con un grupo levantado justo en el cuadro 0.
3. [A5 sin arreglar] la sala ocupa la mitad del ancho con la base en y≈1000 y la mitad inferior es pavimento gris vacío (fondo_liso 0.40); de 52.30 a 54.00 sólo hay un push lento, casi no cambia nada — plano 32 · 52.30 s. **Arreglo:** cámara más baja y más cerca (sala en ~70% del ancho, base en y≈950, rieles visibles a la derecha) y que la sala empiece a deslizarse sobre los rieles en 'práctica' (53.43)
4. [A6 sin arreglar] el remate de la historia de 2003 no muestra la causa: la autopista aparece delante de la sala, pero no se ve que pase por donde estaba la sala; además la sala queda cortada por el borde derecho (x≈720–1080) todo el plano — plano 34 · 57.36 s. **Arreglo:** panear o abrir un poco la cámara a la izquierda para que la sala entre entera (x≈600–1000) y dejar en el piso una huella marcada del tamaño de la sala al inicio de los rieles, justo donde aterriza la autopista en 57.08

## Verificación de la ronda anterior

| id | qué | arreglado |
|---|---|---|
| A1 | la bola de demolicion aparece de la nada en el aire (E15) y cuelga de 3 eslabones separado | sí |
| A2 | Cuando el edificio se alza, las muletas suben con él: en 36.91 la punta de goma toca el su | sí |
| A3 | el cuadro 0, que además es la portada, no vende 'patas': la fila de patas es una franja ch | **no** |
| A4 | En 'se fue caminando' la cámara va alta y acompaña al edificio: las patas son una franja o | sí |
| A5 | la sala ocupa la mitad del ancho con la base en y≈1000 y la mitad inferior es pavimento gr | **no** |
| A6 | el remate de la historia de 2003 no muestra la causa: la autopista aparece delante de la s | **no** |
| A7 | En el cuadro 0 (portada), las patas, que son lo imposible, son una franja delgada (y≈820-9 | **no** |

## Avisos automáticos

- sin datos de ojos en el meta: no se pudo comprobar 'cara tapada' (plano.py + studio/plantilla/caras.py)
