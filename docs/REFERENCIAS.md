# Referencias virales — estudio

Documento vivo. Acá se analizan videos virales que manda Tomás (o que encuentra Claude): por qué funcionan, qué se puede tomar, qué no y qué tan alcanzable es con nuestro pipeline. Las conclusiones que se consolidan pasan al manual, a `IDEAS.md` y a `CONTEXTO.md` (ver la última sección).

**Método por video:** grabación de pantalla → hoja de contacto de 45 cuadros, detección de cortes (diferencia entre cuadros a 10 fps), cuadros de detalle y métricas visibles en la app.

**Ojo con las métricas:** Instagram no muestra el alcance, así que los ratios se calculan **contra likes** como aproximación (envíos/likes y guardados/likes). Las grabaciones a veces son un fragmento del video, así que las duraciones no se comparan.

---

## 1. Resumen de métricas

| # | Video (cuenta) | Tipo | Likes | Envíos | Guardados | Envíos/likes | Guardados/likes | Seg. por plano |
|---|---|---|---|---|---|---|---|---|
| R1 | Frutas humanizadas, "Parte 1" (`@blickyweshh`, resubido por `el.miguel.83`) | Teleserie de humor, IA de video | 25,6 mil | 11,9 mil | 4.810 | **46 %** | 19 % | ~2,2 (fundidos) |
| R2 | "Intenté salvar a mi papá" (`hisytstoryespanol`) | Story time ficticio, 3D | 313 mil | 24,9 mil | 9.641 | 8 % | 3 % | ~1,7 |
| R3 | La caverna de Platón (`zackdfilms`) | Concepto armado frente a ti, 3D | 618 mil | 86,2 mil | 66,6 mil | 14 % | 11 % | ~1,6 |
| R4 | El clavo en la cabeza (`zackdfilms`) | Fábula absurda con moraleja, 3D | 243 mil | 48,1 mil | 35,7 mil | 20 % | 15 % | **~1,2** |
| R5 | Hoyo en el patio → estanque (`hiddenhome.3d`) | Corte del terreno que se transforma, 3D | 382 mil | 39,2 mil | **75,3 mil** | 10 % | 20 % | casi plano fijo |
| R6 | Por qué las ventanas de avión son redondas (cuenta 2D, nombre no legible) | "¿Sabías que…?" con dato histórico, 2D | 25,6 mil | 7.951 | 5.280 | **31 %** | **21 %** | 4 cortes en 44 s |
| R7 | Cómo ganarle al arquero en un mano a mano (`admir_footy`) | Análisis de datos propio, visualización 2D | 62,6 mil | 25,7 mil | 12 mil | **41 %** | 19 % | 0 cortes |
| R8 | ¿Por qué el gancho del metro está suelto? (`resultaaquee`) | Objeto cotidiano en primer plano, 3D, con etiqueta de IA | 290 mil | 50,3 mil | 29,7 mil | 17 % | 10 % | ~1,8 |
| R9 | Hacer girar el monte Fuji como un trompo (`zackdfilms`) | Megaproyecto absurdo paso a paso, 3D | **5,8 mill.** | **1,4 mill.** | 243 mil | 24 % | 4 % | ~1,4 |

---

## 2. Fichas

### R1 · Frutas humanizadas (teleserie)
- **Qué es:** personajes que son frutas humanizadas en una teleserie por partes. Humor de doble sentido (los "cm" en la frente, "Elver Galarga"). Hecho con IA de video (tipo Kling o Veo).
- **Por qué funciona:** el chiste se entiende en 1 s y es para mandárselo a un amigo. Por eso tiene el ratio de envíos más alto.
- **Tomar:**
  - look semi-realista tipo Pixar, luz cálida de tarde, fondo real desenfocado, saturado sin quemar;
  - cada personaje se reconoce por color y textura en medio segundo;
  - la actuación está en la cara (primeros planos con expresión exagerada);
  - un detalle fijo que se entiende sin texto (la etiqueta en la frente);
  - serie por partes ("Parte 1").
- **No tomar:** doble sentido; fundidos entre planos; subtítulos chicos en minúscula; frutas humanizadas (trend ajeno).
- **Alcanzable:** **no** a ese nivel de cara. Sale de IA de video, que está fuera de presupuesto.

### R2 · "Intenté salvar a mi papá" (story time)
- **Qué es:** historia dramática ficticia en primera persona, con niño, papá y policía. 3D tipo motor de juego.
- **Por qué funciona:** tensión y curiosidad por el final. Muchísimo alcance, pero pocos envíos y guardados: se mira, no se comparte.
- **Tomar:**
  - **un solo set** (el auto) del que salen ~28 planos solo moviendo la cámara: ideal para automatizar;
  - cámara expresiva: gran angular, ángulos bajos, muy cerca de la cara;
  - una sola voz narrando en primera persona (cabe en nuestros créditos de voz).
- **No tomar:** errores técnicos (el cinturón atraviesa el cuerpo, el niño va de pie dentro del auto, luz plana, cielo morado); tema de policía y bolsa blanca.
- **Lección:** la historia pesa más que la técnica. Igual llegó a 313 mil con errores visibles.
- **Alcanzable:** **sí**, y mejor terminado.

### R3 · La caverna de Platón (Zack D. Films)
- **Qué es:** una idea abstracta explicada armando la escena paso a paso (los prisioneros, el muro, el fuego, la pasarela).
- **Por qué funciona:** la escena se construye frente a ti, así que quieres ver cómo termina. Es aprendizaje, por eso tiene muchos guardados.
- **Tomar:**
  - luz de **una sola fuente fuerte y cálida** (fuego, rayo de luz), sombras profundas y contraluz;
  - alternar primerísimos planos de la cara (fondo desenfocado) con planos abiertos de escala;
  - llamados mínimos (dos flechitas en los ojos);
  - el personaje es **simple** (pelado, piel lisa): la calidad está en la luz y la cámara, no en el detalle.
- **No tomar:** la narración en imperativo ("ahora pon un fuego… después construye…"), que es su firma; el tema mismo.
- **Alcanzable:** **sí**. Es casi lo que sale de MakeHuman.
- **Abre temas:** experimentos mentales, filosofía, historia.

### R4 · El clavo en la cabeza (Zack D. Films)
- **Qué es:** fábula absurda. Un tipo con un clavo en la cabeza se queja de migraña y no quiere sacárselo. Después se da vuelta: "tú no tienes un clavo, pero te quejas de no tener tiempo y pasas 4 horas en el celular". Termina vendiendo su curso.
- **Por qué funciona:** lo absurdo engancha en el cuadro 0 y la moraleja apunta al que mira ("esto es para ti"), así que se comparte.
- **Tomar:**
  - **el look de nuestro manual casi exacto:** paredes celestes, luz suave de estudio, ropa en pastel saturado (morado, rosado, verde). **Referencia de look n.º 1;**
  - burbuja de pensamiento con forma de nube;
  - **un símbolo que se repite** (el clavo, después en neón sobre cada persona);
  - utilería con chiste (la cuenta del hospital por $98.450);
  - ángulos extremos (desde el suelo, cenital, como si miraras por el celular);
  - ritmo de ~1,2 s por plano.
- **No tomar:** la venta del curso; copiar la fábula.
- **Alcanzable:** **sí**, pero con trabajo: tiene 5 o más personajes y 4 sets. Pelo y barba son nuestro punto débil.

### R5 · Hoyo en el patio → estanque (`hiddenhome.3d`)
- **Qué es:** corte del terreno frente a una casa. La cámara casi no se mueve; el hoyo se transforma (agua, lona, agua verde, plantas, grava, agua limpia). No hay personajes.
- **Por qué funciona:** transformación con final ("¿cómo queda?") y "cómo se hace", que se guarda para después. Los guardados duplican los envíos.
- **Tomar:**
  - **el corte** como lenguaje visual (calza con "¿Cómo funciona por dentro?");
  - hasta 13 s sin cortar y no aburre, porque **algo cambia en el cuadro cada 1–2 s**.
- **No tomar:** su set de casa con patio, que es su sello.
- **Alcanzable:** **sí, y es lo más fácil**: geometría, agua y texturas CC0, sin caras ni pelo.

### R6 · Ventanas de avión redondas (2D)
- **Qué es:** "¿Sabías por qué las ventanas de los aviones no pueden ser cuadradas?". El Comet en 1954, la prueba en un tanque de agua y la grieta en la esquina. 2D minimalista: gris y negro con un solo naranjo, y un monito como mascota.
- **Por qué funciona:** pregunta cotidiana + dato sorpresa + explicación visual simple. Tiene el segundo mejor ratio de envíos y el mejor de guardados, con una producción mínima.
- **Tomar:**
  - **palabra clave en color** dentro del subtítulo ("cuadradas", "piscina gigante", "esquinas");
  - números grandes que cuentan hacia arriba (2.274 → 3.000);
  - metáforas visuales (el avión que se infla como globo, flechas de fuerza que se juntan en las esquinas);
  - **un solo color de marca**;
  - pocos cortes, pero algo cambia todo el rato.
- **No tomar:** el 2D (lo nuestro es 3D sí o sí).
- **Alcanzable:** **sí** en 3D. El tema es historia conocida y va al banco contado a nuestra manera.

### R7 · Mano a mano con el arquero (`admir_footy`)
- **Qué es:** "Encontré 1.945 mano a mano": cada tiro es un punto en pantalla, un contador sube hasta 1.945, revela que el arquero gana 2 de cada 3 y después pregunta: ¿picarla, colocarla o reventarla? Con barras por opción. Fondo oscuro, 2D, en inglés.
- **Por qué funciona:**
  - contradice lo que uno cree ("la oportunidad más fácil del fútbol"… no lo es);
  - **datos propios**: "yo los conté" da autoridad y es 100 % original;
  - deja adivinar antes de revelar, lo que invita a comentar y discutir;
  - tiene un destinatario clarísimo: el amigo futbolero. Por eso el ratio de envíos es el segundo más alto.
- **Tomar:**
  - **"lo conté yo"**: análisis propio con datos abiertos, verificable por construcción;
  - **un punto = un caso**: los números grandes se vuelven tangibles;
  - contador que sube + revelación + opciones para adivinar;
  - **código de color fijo** por opción (celeste, amarillo, rojo), repetido en texto y gráficos;
  - palabra clave en color en el subtítulo (igual que R6);
  - cero cortes, pero algo cambia todo el rato.
- **No tomar:** el 2D; su tema (definiciones de fútbol) contado igual.
- **Alcanzable:** **sí**. En 3D, los puntos pueden ser objetos reales (1.945 pelotas, 1.000 temblores sobre un mapa de Chile), con instancias en Blender y sin personajes. Tomás sabe Python y R: el análisis de datos es terreno propio.

### R8 · El gancho del metro (`resultaaquee`)
- **Qué es:** "¿Por qué el gancho del metro está suelto? No, no está roto." Se mueve justo lo que mide su grosor, así que el cero queda bien si lo enganchas en una tabla o si lo empujas contra una pared. Si lo aprietas, la medida te sale siempre mal. Cierra con "Sí, está suelto, pero a propósito. Envíaselo a ese amigo", con un celular animado mostrando cómo se comparte. En español y con la etiqueta "Contenido de IA".
- **Por qué funciona:**
  - todos tienen un metro en la casa y todos pensaron que estaba malo: **parece un defecto, pero es a propósito**;
  - la respuesta se entiende en 20 s y te deja con algo que contar;
  - pide el envío explícitamente y con destinatario.
- **Tomar:**
  - **un solo objeto en primer plano**, render limpio tipo comercial de producto, fondo oscuro cálido con partículas desenfocadas;
  - **colores con significado:** gris normal, rojo/rosado cuando está mal, celeste para la línea del cero;
  - planos translúcidos y flechas para mostrar lo invisible (dónde queda el cero);
  - utilería para el "error" (el alicate que aprieta el gancho);
  - **subtítulos arriba** cuando el objeto ocupa el centro: texto gris con la palabra activa en blanco dentro de un recuadro;
  - **llamado a enviar al final, con destinatario** ("envíaselo a ese amigo"). Es distinto de un "sígueme": empuja nuestra métrica principal.
- **No tomar:** el gráfico del celular con la interfaz de Instagram (es de la app); el tema contado igual.
- **Alcanzable:** **sí, es de lo más fácil**: un objeto, un par de materiales, una tabla y una pared. Sin personajes.
- **Dato extra:** la etiqueta "Contenido de IA" no le impidió llegar a 290 mil.

### R9 · El monte Fuji girando como trompo (Zack D. Films)
- **Qué es:** un megaproyecto absurdo explicado paso a paso: amarrar un cable a la base del Fuji, perforar miles de pozos, anclarlo, envolverlo en malla de acero, darlo vuelta con cohetes, montarlo sobre un rodamiento gigante y tirar del cable con miles de aviones de combate hasta que gira. Tiene 5,8 millones de likes, 1,4 millones de envíos y 85 mil comentarios.
- **Por qué funciona:**
  - premisa absurda y gigante, que se entiende en el título;
  - la ingeniería suena seria (anclas, lechada, rodamiento), lo que lo hace "creíble" y divertido a la vez;
  - **escala épica:** miles de anclas, cohetes y aviones;
  - invita a discutir ("eso no funcionaría"), por eso los comentarios son muchísimos (1,5 % de los likes, 10 veces más que el resto).
- **Tomar:**
  - **premisa absurda a escala gigante** con un lugar real y conocido;
  - **repetición masiva** (miles de objetos iguales) para dar escala;
  - planos aéreos amplios alternados con detalles de máquinas;
  - ritmo de ~1,4 s por plano.
- **No tomar:** es **el formato insignia de Zack** (megaproyecto + narración en imperativo). Hacerlo igual es imitarlo. La referencia a Beyblade (una marca) tampoco.
- **Cómo hacerlo nuestro:** la premisa absurda, pero **con el cálculo real** de si funcionaría ("¿Cuántos aviones harían falta para hacer girar el Aconcagua? Lo calculé"). Cruza la escala de R9 con los datos propios de R7, y es algo que Zack no hace.
- **Alcanzable:** **sí, con trabajo**. El terreno sale de datos de elevación abiertos y los miles de objetos son instancias en Blender. Faltan modelos semi-realistas de máquinas (cohetes, aviones, grúas), y el render de paisajes es pesado.

---

## 3. Conclusiones (al 18-oct-2026, con 9 referencias)

1. **Cada video se diseña para una acción: enviar o guardar.**
   - Se **envía** lo que tiene un destinatario: humor (R1, 46 %), dato sorpresa (R6, 31 %) o moraleja "esto es para ti" (R4, 20 %).
   - Se **guarda** lo que sirve después: cómo se hace (R5), dato que enseña (R6) o concepto (R3).
   - El drama puro (R2) junta likes, pero casi no se envía ni se guarda.
   - Al elegir una idea, hay que responder: *¿a quién se lo mandan?* o *¿por qué lo guardarían?* Si no hay respuesta, no sale.
2. **Algo cambia en pantalla cada 1–2 s.** Puede ser un corte (R4: 1,2 s; R2: 1,7 s) o una transformación dentro del cuadro (R5, R6). La regla "plano de 2–3 s" se queda corta.
3. **Cuadro 0 absurdo o con pregunta.** Un clavo en la cabeza, cm en la frente, un hoyo en el patio o una pregunta escrita: una imagen que todavía no tiene sentido obliga a quedarse.
4. **Un símbolo que se repite amarra el video** y sirve de portada: el clavo, la etiqueta, la ventana, el hoyo.
5. **Construir o transformar frente al espectador retiene.** Se quiere ver el resultado final (R3, R5, R6).
6. **La idea pesa más que la técnica.** R2 explotó con errores visibles y R6 con 2D mínimo. La calidad multiplica una buena idea, pero no la reemplaza.
7. **Subtítulos:** todos van al medio, con 1–3 palabras. Confirma nuestra regla. Se suma **la palabra clave en color o más grande** (R6).
8. **El personaje no necesita ser detallado** (R3): luz, cámara y expresión hacen el trabajo. El look de R4 es nuestro objetivo.
9. **Las series por partes** (R1) generan seguidores: la Parte 2 la ve gente que nunca vio la 1 (coincide con `investigacion-formatos-virales.md`).
10. **Los datos propios son originalidad y autoridad a la vez** (R7). "Conté 1.945 casos" no se puede copiar y se verifica solo.
11. **Dejar adivinar antes de revelar** (R7) genera comentarios y retención.
12. **Código de color fijo** (R6, R7, R8): un color por idea u opción, repetido en subtítulos y gráficos. Se lee sin pensar.
13. **"Parece un error, pero es a propósito"** (R8, R6) es una familia de temas muy compartible: objetos que todos tienen y todos creen que están malos o mal diseñados.
14. **Pedir el envío con destinatario al final** ("envíaselo a ese amigo que…") puede subir la métrica principal (R8). Se prueba en algunos videos y se compara.
15. **La etiqueta de IA no frena el alcance** (R8: 290 mil con "Contenido de IA").
16. **El subtítulo puede ir arriba** cuando el objeto ocupa el centro (R8). La zona fija al medio sirve para personajes, no para todo.
17. **El mayor alcance lo da lo absurdo a escala gigante** (R9: 5,8 millones). Una premisa imposible con un lugar real.
18. **Los comentarios explotan cuando la premisa invita a discutir** (R9: "eso no funcionaría"). Para comentarios: dejar algo que la gente quiera corregir o completar.

---

## 4. Qué podemos lograr con nuestro pipeline

| Nivel | Qué | Referencias | Estado |
|---|---|---|---|
| **Ya alcanzable** | Corte o transformación sin personaje; objeto cotidiano en primer plano; objetos con metáforas visuales; números animados; datos propios con objetos 3D | R5, R6, R7, R8 | Solo falta la plantilla |
| **Con trabajo** | Megaproyectos absurdos con paisajes reales y miles de objetos | R9 | Terreno con datos de elevación abiertos; faltan modelos de máquinas |
| **Con trabajo** | Fábulas y story time con personajes semi-realistas y look pastel | R2, R3, R4 | Protagonista borrador 1 en `studio/personaje/`. Faltan piel, mirada, boca y personajes secundarios (variaciones de MakeHuman) |
| **Fuera de alcance** | Caras tipo Pixar con esa expresividad | R1 | Requiere IA de video: fuera de presupuesto |

---

## 5. Formatos posibles para la cuenta

| Formato | Línea | Referencia | Acción buscada |
|---|---|---|---|
| **Corte que se transforma** ("¿qué pasa si…?", "¿cómo se hace…?") | Datos | R5 | Guardar |
| **Dato histórico con metáfora visual** | Datos | R6 | Enviar y guardar |
| **Concepto armado frente a ti** (filosofía, experimentos mentales) | Datos | R3 | Guardar |
| **"Lo conté yo"** (análisis propio con datos abiertos: fútbol, temblores, metro…) | Datos | R7 | Enviar y comentar |
| **"Parece un error, pero es a propósito"** (objeto cotidiano en primer plano) | Datos | R8 | Enviar |
| **Megaproyecto absurdo + "lo calculé"** (¿cuántos aviones para girar el Aconcagua?) | Ambas | R9 + R7 | Enviar y comentar |
| **Fábula absurda con moraleja** | Historias | R4 | Enviar |
| **Story time ficticio en primera persona** | Historias | R2 | Retención (alcance) |
| **Serie por partes** (cualquiera de los anteriores) | Ambas | R1 | Seguir |

**Firmas ajenas que no se copian:** la narración en imperativo de Zack D. Films y sus megaproyectos contados igual; la casa con patio de `hiddenhome.3d`; las frutas humanizadas.

---

## 6. Decisiones de Tomás en este estudio (18-oct-2026)

- **La cuenta no es solo informar.** Hay dos líneas: **datos** (con fuentes) e **historias** (inventadas, absurdas o sin sentido; híbridas solo si salen solas).
- **Regla que se mantiene:** si un video presenta algo como dato real, es real. La ficción puede ser todo lo loca que se quiera.
- **Propuesta de arranque (sin confirmar):** 2 de datos + 1 historia por semana; la proporción se ajusta a las 4 semanas según envíos.

---

## 7. Cambios propuestos a otros documentos (se aplican al cerrar el estudio)

- **`MANUAL_PRODUCCION.md`:**
  - §4: reemplazar "plano de 2–3 s" y "ningún plano estático de más de 3 s" por "**nunca más de 2 s sin un cambio en pantalla**" (corte o transformación). Planos de 1,2–2,5 s.
  - §6: sumar **palabra clave** destacada además de la palabra activa; permitir **subtítulos arriba** cuando el protagonista es un objeto centrado.
  - §1 y §10: probar un cierre con **llamado a enviar con destinatario** ("envíaselo a…") en algunos videos, sin romper el loop.
  - §1: estructura de guion para la línea historias.
  - §2: la verificación aplica a todo lo que se presenta como real.
  - §5: look de referencia R4 (pastel saturado) y luz de una sola fuente para momentos dramáticos (R3).
  - §5: código de color fijo por idea u opción (R6, R7).
- **`CONTEXTO.md`:** dos líneas de contenido; referencias de look; color de marca por definir.
- **`IDEAS.md`:**
  - criterio nuevo **Guardable** junto a Compartible, y la pregunta "¿a quién se lo mandan / por qué lo guardarían?";
  - banco de historias;
  - temas nuevos: experimentos mentales, filosofía, historia de la ingeniería (ventanas del Comet), **fútbol y deportes**, **datos propios** (temblores en Chile, metro de Santiago, etc.).
  - fuentes de datos abiertos para la línea "lo conté yo" (la licencia de cada base se revisa antes de usarla).
  - familia "parece un error, pero es a propósito" en el banco de objetos cotidianos.
- **`PUBLICADOS.md`:** columna **Línea** (datos / historias) y **Formato**.
