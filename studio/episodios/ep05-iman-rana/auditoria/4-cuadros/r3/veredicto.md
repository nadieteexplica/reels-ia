# 4-cuadros · ronda 3 · **NO APROBADO** · estilo realista

Promedio **8.0** (mínimo 8; ningún revisor bajo 7 en ningún criterio; realismo: ningún revisor bajo 8).

**2 rondas sin aprobar: no se abre otra.** Lo que sigue fallando se simplifica o se reemplaza por una plantilla del kit y el video sigue: en el animatic, la puerta 7 revisa bloqueantes en todo el render final (incluidos los planos simplificados). Si es guion o storyboard, se cambia la idea o se le pregunta a Tomás.

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| belleza | 8.0 | 8 | B: luz baja cálida con dirección (cerros, torres y casco iluminados desde la derecha), bruma de distancia y metal del imán con óxido, rayas y pernos; A: tubo con profundidad de campo, burbujas y bordes de vidrio oscuros; C: un foco claro (molécula central con flecha). Lo único flojo: las plumas de B son blancas parejas sin lado en sombra ni tinte cálido. |
| personaje | 8.0 | 8 | B: Pete igual a la ficha (casco blanco, barba, chaleco naranjo con cintas amarillas, polera oscura de manga larga, pantalón embarrado, botas cafés), cara en y≈230/1280 (≈345/1920) con aire de cielo encima; A: rana igual al escaneo de la ficha. |
| manos | 8.0 | 8 | B: las dos manos libres y relajadas junto a los muslos (una semicerrada, otra abierta), sin agarre ni objeto, cinco dedos legibles; sirve como cuadro de partida. |
| anatomia | 8.0 | 8 | C: interior a nivel de células con vasos, un solo foco (la molécula central bajo la flecha, y≈460/1280, sobre la franja de subtítulos), nada cortado ni inventado; moléculas y líneas de campo son capa de explicación permitida. |
| realismo | 8.0 | 8 | Real: en B los cerros ahora tienen falda y llegan al salar en todo el ancho con bruma de distancia, el imán es metal gastado con óxido y pernos, Pete con proporciones reales y ropa con barro; A es un escaneo real con DOF y vidrio que refracta. Delata el 3D: las plumas de B (x≈395-640, y≈215-475) son tarjetas blancas planas con bordes cortados recto (base de la izquierda en y≈464, techo de ambas), sin volumen ni sombra; el domo y el bloque de la derecha (x≈605-720, y≈540-595) con bordes perfectos. Para subir a 9: plumas volumétricas con lado en sombra azulado y lado al sol cálido, que se deshilachen arriba en vez de terminar en un borde. |

## Bloqueantes y fallas automáticas (impiden aprobar)

1. 🛑 [B1] La pluma de vapor de la torre izquierda flota: su base es un corte recto horizontal en y≈464 (x≈426-452 a 720x1280; y≈696, x≈639-678 a 1080x1920) y entre ella y el labio de la torre (y≈479; ≈718 a 1080) hay una franja de cielo de ~14 px (~21 px a 1080). La pluma derecha sí nace del labio (blanco hasta y≈474, labio en 477). Lo rompió el rehacer de las plumas en r3, queda justo al lado de las botas de Pete y Kling lo va a copiar en todo el clip. — plano B · cuadro s. **Arreglo:** Bajar el emisor/volumen de la pluma izquierda hasta dentro de la boca de la torre (como la derecha) y agrandar el dominio del volumen para que la base no quede cortada recta; volver a mirar sólo la franja x 385-470, y 455-485 (a 720).

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

Ninguna.

## Verificación de la ronda anterior

| id | qué | arreglado |
|---|---|---|
| A1 | Los cerros nuevos flotan: en x 0-230, y≈560-595 (a 720x1280; x 0-345, y 840-893 a 1080) se | sí |

## Avisos automáticos

- ronda 3 abierta con --forzar: Tomás pidió seguir el 23-oct 06:24 ('sí, sigue con todo') después de ver los cuadros; el fondo de B (único motivo del 7 en r2) ya está rehecho
