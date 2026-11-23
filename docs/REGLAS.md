# Reglas — cómo decidimos (Tomás, 23-nov-2026)

El objetivo no es acumular reglas, sino tomar buenas decisiones con evidencia sin cegarnos. Este documento manda sobre
cualquier regla escrita en otro lado que lo contradiga (salvo *Seguridad* y *Publicación* de `proyecto/INSTRUCCIONES.md`,
que son parte de las reglas duras).

## 1. Dos niveles, no más

**Reglas duras** (pocas; no se rompen nunca):
1. **Verdad:** lo que se presenta como real es real, con 2 fuentes confiables e independientes.
2. **Publicar:** nada se publica ni se programa sin el OK de Tomás por post (archivo `studio/ok/<ep>-<red>.ok` que crea él con `tools/ok.sh`; el hook lo exige y lo gasta al usarlo).
3. **API keys:** nunca se escriben, piden, repiten ni suben. No se crean cuentas ni se inicia sesión por Tomás.
4. **No copiar un video ajeno entero** (mismo tema + misma secuencia + mismos visuales). Tomar una fórmula, una estructura o un tipo de gancho y usarlo con otro tema sí se puede.
5. **Nada con derechos:** ni assets, ni música comercial, ni personajes, ni voces de personas reales sin permiso. Los videos y textos de otros creadores no se suben al repo ni a GitHub. Assets con licencia restringida, sólo en el repo privado `nadieteexplica/assets`.
6. **Temas prohibidos** de `proyecto/INSTRUCCIONES.md` (retos peligrosos, tragedias recientes, política, lo imitable que hiere; salud sólo general).

**Criterios:** todo lo demás (estructuras de guion, duración, tipo de apertura, estilos visuales, CTA, ritmo, sonido). Son puntos de partida, no leyes: se pueden romper cuando el resultado le gana a los virales, dejando anotado por qué.

## 2. Cada criterio con su nivel de evidencia
- **[MEDIDA]** viene de nuestros números (YouTube, IG, `docs/PUBLICADOS.md`) o se ve objetivamente (texto ilegible en el celular, un render roto, una herramienta que falla).
- **[PROBABLE]** lo respalda un principio conocido (p. ej. la redundancia de Mayer, la brecha de curiosidad) o varios virales de `docs/referencias/virales/`.
- **[HIPÓTESIS]** una opinión, de Tomás o de Claude, sin probar. **Las hipótesis no bloquean nada:** se registran y se prueban con datos reales.

Dónde están marcadas: `docs/GUIONISTA.md`, `docs/LECCIONES.md`, las skills `guion`, `estilo-visual` y `qa-video`.

## 3. Qué decide si algo está bien, en este orden
1. **Métricas reales:** YouTube (visto vs. deslizado, % visto) e Instagram (envíos). Mandan sobre todo.
2. **El ojo de Tomás en el celular.**
3. **Jueces ciegos, como orientación.** Comparan en video (cuadros cada 0,25 s + audio descrito; no hojas quietas) y de forma relativa, contra el viral en el mismo tramo: ¿cuál se ve más profesional? ¿cuál deslizarías? Piso: ganar o empatar. **Si un juez deja a un viral de millones bajo 6, el juez está mal calibrado, no el viral.**

## 4. Aprender sin endurecerse
- Las notas de Tomás se guardan con `/aprender` **con su nivel de evidencia** (casi siempre [HIPÓTESIS] al principio), no como ley automática.
- Las hipótesis se prueban **alternando entre videos** (p. ej. apertura "raro" vs. "normal→escala"; `docs/ROTACION.md`) y se revisan con las métricas cada 4–6 videos.
- **Cada 5 videos, limpieza:** lo que los datos no confirmaron baja de nivel o se borra. Lo que confirmaron sube a [MEDIDA].

## 5. Qué le llega a Tomás
Sólo dos cosas: **elegir 1 de 10 ganchos** y **el OK final del video** (por post). Las decisiones chicas las toma Claude y las anota. Si algo grande cambia el plan, se le dice en 3 líneas con la recomendación.
