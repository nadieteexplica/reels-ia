# Ep. 2 — para retomar (19-oct-2026, 21:30)

Estado: guion, voz y storyboard **APROBADOS** (puertas 1–3). Personajes propios en `ficha.jpg` (código en `escena/personajes.py`).

## Cuadros de estilo (escenarios nuevos) — falta la puerta 4 y mandárselos a Tomás
- Desierto / cuadro 0: `estilos/estilo_desierto_HD.jpg` (render local, 1080x1920). Script: `escena/estilo_desierto.py` (+ `post_estilo.py`).
- Lengua con alarmas (cámara S), ventanita de muelas (plano 23) y bosque con tupaya: HD en la prerelease **`ep02-estilos`** (`estilo_lengua_HD.jpg`, `estilo_muelas_HD.jpg`, `estilo_bosque_HD.jpg`), renderizados por `estilos.yml` (runs 39347261475 y 39347387369). Borradores chicos en `estilos/`.
  - A la ventanita de muelas le falta el recuadro punteado 2D: `python3 escena/marco_ysi.py estilo_muelas_HD.jpg salida.jpg x`.
- Para volver a renderizar en la nube: workflow `estilos.yml` (input `escenas`: desierto,lengua,muelas,bosque).

## Pasos siguientes
1. Bajar los 4 HD (prerelease `ep02-estilos` y `estilos/`), revisarlos uno por uno (manos, contactos, caras, encuadre: caras sobre y 1000).
2. Puerta 4: `python3 tools/auditor/auditar.py preparar ep02-pajaros-picante cuadros --imagenes '<los 4 jpg>' --nota "cuadros de estilo de escenarios nuevos: desierto (= cuadro 0, planos 1 y 40), lengua por dentro (cámara S, plano 11), ventanita de muelas (plano 23, recuadro 2D), bosque de China (plano 30). Estilo del episodio: dibujo animado 3D, ficha en ficha.jpg"` → `lanzar` (subagente) → `cerrar`. Máx. 3 rondas.
3. Con APROBADO: mandarle a Tomás los 4 cuadros + la ficha en un mensaje corto y esperar su OK antes de animar.
4. Después: animación por plano (storyboard v3.1, tabla de utilería), render en GPU (RunPod) o Actions, puertas 6, 7 y P.

## Reglas que salieron hoy (ya están en CONTEXTO y LECCIONES)
- Cada idea con su propio estilo y personajes (no el protagonista de siempre).
- Consultas web en un solo workflow; WebFetch máx. 1–2.
- Los mensajes de Tomás cortan a los subagentes: esperar 2–3 min y mirar `auditar.py estado` antes de relanzar.
