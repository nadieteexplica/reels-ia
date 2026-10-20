# Ep. 2 — para retomar (21-oct-2026)

> **20-oct 10:40 — lo lleva la sesión de chat con Tomás** (eligió rediseñar el bosque). Cualquier otra sesión: no tocar el repo ni lanzar runs del Ep. 2 hasta que este aviso se borre.

Estado: guion, voz y storyboard **APROBADOS** (puertas 1–3). **Puerta 4 (cuadros de estilo): NO APROBADO en la 3.ª ronda** (r1: 2 bloqueantes · r2: 0 bloqueantes, 6 arreglos · r3: 0 bloqueantes, 5 arreglos; belleza 7 por el bosque). Por la regla de 3 rondas no se siguió corrigiendo y **no se le mandaron los cuadros a Tomás**: se le pidió decidir el reemplazo.

## Dónde están los cuadros (r3)
- HD en la prerelease **`ep02-estilos`** (los sube `estilos.yml`, run 39429531804; los 4 en paralelo, ~3–10 min). El de muelas lleva el inserto 2D: `python3 escena/marco_ysi.py estilo_muelas_HD.jpg salida.jpg x izq mascara`.
- Veredictos: `auditoria/4-cuadros/r1..r3/veredicto.md`.
- Pasan sin problemas mayores: **desierto (C0)**, **lengua (campana)** y **muelas (inserto)**. Lo que impide el APROBADO es el **bosque** (belleza 7: luz plana, fondo verde lavado, hojas de papel, hojas flotando, mancha de la tupaya en el cuello).

## Adelantado el 21-oct (sirve con las dos opciones; sin auditar todavía)
- Muelas: cámara un 7 % más lejos y cabeza más arriba y a la izquierda → la oreja tiene aire dentro del recuadro y la ventanita baja hasta y≈980 (< 1000).
- Lengua: molécula más chica y más acostada → la punta queda bajo y≈200; campana menos brillante (rough 0.32) → 0,08 % quemado.
- Falta: render HD de los 4 (`estilos.yml`) y la puerta 4 nueva, cuando Tomás elija el bosque.

## Lo que espera de Tomás
Elegir el reemplazo del bosque (propuesta de Claude primero):
1. **Rediseñar el set del bosque** (luz cálida filtrada entre hojas + contorno en la tupaya, follaje oscuro en capas con helechos y musgo, hojas con grosor, sin hojas sueltas, mancha de la tupaya en el hombro) y pasarlo solo por una puerta 4 nueva junto con los arreglos chicos de r3 en muelas (oreja y ventanita) y lengua (punta de la molécula, reflejo).
2. Sacar el escenario: plano 30 como recuadro sobre el desierto (la tupaya en una "postal" de China) sin set de bosque.
Con su OK a una opción: se hace, puerta 4 (rondas nuevas), y recién con APROBADO se le mandan los 4 cuadros + `ficha.jpg` para el OK antes de animar.

## Después
Animación por plano (storyboard v3.1, tabla de utilería actualizada: lentes y medalla en el escalón de la roca), render en GPU (RunPod) o Actions, puertas 6, 7 y P.

## Cambios de código de hoy (valen para todo el episodio)
- `personajes.tupaya` volvió al modelo de la ficha (el que se usaba se había alejado: patas gruesas, sin mancha). No cambiar sin volver a renderizar `ficha.jpg`.
- `lengua.campana`: campana de verdad (labio, pie, badajo); papilas rosadas; `vfx.llamarada`: fuego amarillo-naranjo (antes salmón); chispas naranjas; medalla dorada sin espejo; mordisco del ají con pulpa clara (`props_ep02.morder`).
- `marco_ysi.py`: opciones `izq` (✕ a la izquierda) y `mascara` (fuera del recuadro oscuro y desenfocado).
