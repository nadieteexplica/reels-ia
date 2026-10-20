# Ep. 2 — para retomar (20-oct-2026, 13:30)

> **Lo lleva la sesión de chat con Tomás** (desde el 20-oct 10:40). Cualquier otra sesión: no tocar el repo ni lanzar runs del Ep. 2 hasta que este aviso se borre.

Estado: guion, voz y storyboard **APROBADOS** (puertas 1–3). **Puerta 4, ciclo 2** (con el bosque rediseñado que eligió Tomás): r1 NO APROBADO (1 bloqueante, 16 arreglos), r2 NO APROBADO (0 bloqueantes, 11 arreglos). Los 11 arreglos de r2 están hechos; **r3 es la última ronda del ciclo**.

## Dónde están los cuadros
- HD en la prerelease **`ep02-estilos`** (los sube `estilos.yml` con `escenas=desierto,lengua,muelas2,bosque`; `muelas2` arma el inserto completo: ratón + lupa + recuadro + ✕).
- Veredictos: `auditoria/4-cuadros/r1..r2/veredicto.md` (el ciclo 1 está archivado en `auditoria/4-cuadros-ciclo1/`).

## Arreglos de r2 (hechos el 20-oct)
- Desierto (C0): cabeza del pájaro de 3/4 con el pico abierto apretando el ají; pájaro más arriba (pico sobre y 950); duna a la izquierda (sin franja azul en el horizonte); pistas en dos repisas escalonadas a la derecha del ratón (ají mordido en el borde, medalla colgando con cinta azul, lentes en la repisa alta). Herramientas: `PROBE`, `RAYO_PIX`, `PERFIL`, `SOLO_POS` en `estilo_desierto.py`.
- Muelas: ratón entero sentado de perfil (como la ficha), pata de la cámara como tubo doblado con la palma frente al pecho, oreja girada hacia la cámara; lupa arriba a la izquierda; ✕ abajo al centro de la lupa; semillas = discos planos amarillo pálido con borde oscuro (~1/3 de corona), migas del mismo amarillo.
- Lengua: lengua corrida a la izquierda (se ve el borde derecho), surco central marcado, papilas sueltas de tamaños distintos (mate); campana apoyada en la superficie; ondas de la izquierda cortadas bajo la cadena; molécula de rojo más profundo.
- Bosque: remate del tallo de Piper (nudo + hoja nueva); luz menos cálida (RAYO 40, contorno 60) → tupaya café oliva; tupaya girada a 55° y guata más clara → se ve la garganta.
- Medalla: cinta azul y relieve central en `personajes.medalla` → `ficha.jpg` re-renderizada.

## Lo que sigue
1. Revisión propia de los 4 HD con zoom → `auditar.py preparar ep02-pajaros-picante 4-cuadros --imagenes ... --nota "$(cat nota)"` → `lanzar` (subagente) → `cerrar`.
2. Con APROBADO: mandarle a Tomás los 4 cuadros + `ficha.jpg` y esperar su OK antes de animar. Si r3 no aprueba: explicarle y proponer opciones (no seguir corrigiendo sin su decisión).
3. Después: animación por plano (storyboard v3.1), render, puertas 6, 7 y P.
