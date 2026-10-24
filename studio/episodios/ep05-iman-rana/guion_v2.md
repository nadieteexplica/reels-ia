# Ep. 5 — El imán que hace flotar a una rana

**Versión 2.1 (23-oct-2026, 00:45; puerta 1 APROBADO 8,25 con la v2).** v2.1 aplica sugerencias de la puerta 1: "fresa" en vez de "frutilla" (se entiende en toda Latam; el público de YouTube es sobre todo de México), 4 pausas en vez de 5, y el cierre "sin hilos" en vez de "tranquila" (Geim cuenta que la rana se desorientaba). No se aplicó: cambiar "casi cuarenta" por un rango (son los números de Geim que eligió Tomás; Leicester queda en los matices) ni sacar "Ahí sí flotarías" (es el remate que pidió Tomás).
**Versión 2 (23-oct-2026, 00:30).** v2: la parte de la persona cuenta paso a paso cómo podría llegar a pasar (pedido de Tomás, 00:25), siempre en condicional; "miles de veces" con 2 fuentes; todo a escala real. Idea y forma decididas por Tomás (ficha en `docs/IDEAS.md` → "Ficha — El imán que hace flotar seres vivos", decisión del 22-oct 23:12 y pedido de las 23:16).
**Voz:** Fernando Martínez · job `jobs/voz/0010-ep05-iman-rana.json` → `out/tts/ep05-iman-rana.mp3`.
**Línea:** datos · **Gancho:** "¿Sabías que…?" (una rana flotando, real) + "¿Qué pasa si…?" (el imán para una persona) · **Área:** física / naturaleza · **Formato:** imagen imposible + mecánica por dentro (como el Ep. 4: la cámara entra a la rana hasta el agua) + megaproyecto hipotético con números reales.
**Estilo:** **realista** (`estilo.json`): "realista pero en un mundo animado", referencia de calidad Zack D. Films (Tomás, 22-oct 23:26). Nada de fotorrealismo de IA.
**Tono (decisión de Tomás):** directo, sin contar el estudio (nada de quién, cuándo, "científicos" ni premios: va en la descripción, el primer comentario y, la anécdota del Ig Nobel + Nobel, en el texto del post).
**Acción buscada:** enviar. ¿A quién? A cualquiera: "mira, una rana flotando" se entiende sin sonido y el remate ("hacerte flotar a ti") tiene destinatario. Se guarda por el "por qué no" del imán del refri.
**Puntaje de la idea:** 42,5 de 45 (IDEAS.md §2; mínimo 32 en datos). Curiosidad 5 (×1,5 = 7,5) · Universalidad 5 (×1,2 = 6: todos tienen un imán en el refri y todos tenemos agua) · Sorpresa 5 (×1,5 = 7,5) · Visual 3D 5 (×1,3 = 6,5) · Enseñanza 4 (×1 = 4) · Verificable 5 (×1 = 5) · Compartible 4 (×1,5 = 6).
**Costo estimado:** ~40 s; 5 escenas (laboratorio con la rana, interior de la rana hasta el agua, refri, construcción del imán gigante, persona flotando dentro), 3 a medida; 0 clips de Kling (todo render 3D con el mismo look).
**Duración estimada:** 119 palabras a ~2,9 palabras/s ≈ 41,0 s.

## Guion (119 palabras, ~41,0 s)
Esta rana está flotando... y nadie la sostiene.
La levanta un imán gigante.
¿Cómo? La rana es, en gran parte, agua.
Y al agua, un imán la empuja... un poquito.
Ese empujoncito lo recibe cada molécula.
Y con un imán bien fuerte, le gana a la gravedad.
Le pasa a una fresa... y a ti.
¿Por qué no flotas junto al refri?
Porque ese imán es miles de veces más débil.
¿Y si quisiéramos hacerte flotar a ti?
Haría falta un imán gigante donde quepas.
Casi cuarenta teslas: más del doble que el de la rana.
Y gastaría cerca de un gigavatio: un reactor nuclear entero.
Ahí sí flotarías.
Todo eso... para lo que esta rana hace sin hilos.

## Verificación por afirmación
| Afirmación del guion | Fuente(s) |
|---|---|
| Una rana viva puede flotar en el aire, sin nada que la sostenga, dentro de un imán | Geim y Berry, *European Journal of Physics* 1997 (rana viva levitando dentro de un imán de ~16 T); Geim, *Physics Today* 1998 ("Everyone's magnetism"); Harvard Gazette 2024 |
| La levanta un imán gigante | Las mismas: un electroimán de laboratorio de campos altos (Nijmegen), del orden de 16 teslas; el aparato es enorme aunque el hueco donde flota es chico |
| La rana es, en gran parte, agua | Harvard Gazette 2024 (Geim: el diamagnetismo que usa está en el agua, la comida y las moléculas orgánicas; primero vio flotar agua y después frutas y la rana); MIT Technology Review 2009 (lo que hace flotar a los ratones es el efecto del campo sobre las moléculas de agua). Geim no lo dice con esas palabras: es la explicación común de las dos fuentes |
| Al agua, un imán la empuja apenas un poquito (diamagnetismo) | Geim y Berry 1997; Geim 1998 (el agua es diamagnética: un campo magnético la repele débilmente) |
| Ese empujoncito lo recibe cada molécula; y con un imán bien fuerte, le gana a la gravedad | Geim y Berry 1997 (la fuerza diamagnética actúa sobre cada parte del cuerpo, por eso el objeto flota sin tensiones internas; con campo y gradiente suficientes iguala al peso) |
| Le pasa a una fresa y también a ti (a todo lo que tiene agua) | Harvard Gazette 2024 (el diamagnetismo está en el agua, la comida y las moléculas orgánicas; después del agua hizo flotar frutillas y tomates cherry); Geim 1998 (todos somos diamagnéticos: "Everyone's magnetism") |
| No flotas junto al refri porque ese imán es miles de veces más débil (el del refri también te empuja, muchísimo menos) | Harvard Gazette 2024 (el propio Geim: para hacer flotar una rana hace falta un campo "1,000 to 10,000 times stronger than a refrigerator magnet"); MIT Technology Review 2009 (17 T, "ten thousand times as strong as a typical fridge magnet"). Dos fuentes independientes coinciden en "miles"; no se da un número exacto |
| ¿Y si quisiéramos hacerte flotar a ti? Haría falta un imán gigante con un hueco donde quepas, de casi 40 T, que gastaría cerca de un gigavatio; ahí sí flotarías | Geim 1998 (hacer flotar a una persona "requeriría un imán especial de casi 40 T y alrededor de un gigavatio" de consumo continuo). Son los números de la ficha (decisión de Tomás). Ojo: el cálculo de estudiantes de Leicester da 70,6 T con otros supuestos; por eso la voz dice "casi cuarenta" (el piso de Geim) y no "exactamente" |
| Cerca de un gigavatio: un reactor nuclear entero (lo que produce un reactor típico) | Departamento de Energía de EE. UU. (un reactor típico produce ~1 gigavatio) |
| Casi cuarenta teslas es más del doble que el imán de la rana | Geim y Berry 1997 (la rana flotó en ~16 T: 40/16 = 2,5) y Harvard Gazette (10 T: 4 veces). Con cualquiera de los dos, "más del doble" es cierto |
| La rana flota sin hilos y no le pasa nada (cierre) | Geim 1998 y Harvard Gazette (la rana no sufrió efectos, salvo desorientarse por la falta de peso) |

**Matices (para no exagerar):**
- **No se dice que se haya hecho flotar a una persona.** La parte del humano es hipotética ("¿Y si quisiéramos…?", "haría falta", "gastaría") y en pantalla lleva una píldora fija de SIMULACIÓN mientras dura.
- "Miles de veces más débil": Harvard Gazette (Geim en 2024: 1.000–10.000 veces) y MIT Technology Review (~10.000 para 17 T) coinciden en miles. Geim en 1998 había comparado 10 T con ~100 imanes de refri (depende del imán de refri que se tome): no se pone un número exacto.
- Teslas para un humano: Geim (1998) dice casi 40 T; el trabajo de estudiantes de Leicester calcula 70,6 T. La voz usa el número de Geim (la ficha) y el texto del post no promete precisión.
- "Le gana a la gravedad" simplifica: no basta con un campo fuerte, el campo también tiene que cambiar rápido con la altura (el empujón depende de los dos). El dibujo del imán muestra las líneas apretándose bajo la rana.
- **Escala real (Tomás, 00:25):** la rana del experimento cabía en el hueco del imán, de ~3 cm: en la animación la rana es chica (~3 cm) y flota dentro de un tubo transparente en la boca del imán, que es grande (el aparato pesa toneladas aunque el hueco sea angosto). Pete mide 1,79 m, el refri es de tamaño normal y las torres de la central nuclear (~150 m) están lejos en el horizonte.
- "Ahí sí flotarías": es lo que se deduce de Geim (1998), que da esos números como lo que haría falta para hacer flotar a una persona. Siempre en condicional ("haría falta", "gastaría", "flotarías") y con la píldora SIMULACIÓN.
- Seguridad: nada imitable. Nadie acerca imanes a personas ni a animales en la animación; los animales se ven bien y tranquilos.
- El estudio (Geim y Berry, Nijmegen, 1997; Ig Nobel 2000 y Nobel de Física 2010 por el grafeno) no se cuenta en la voz (decisión de Tomás): va en la descripción, el primer comentario y el texto del post.

## Fuentes
- Geim y Berry, European Journal of Physics (1997) — Of flying frogs and levitrons: https://obelix.physik.uni-bielefeld.de/~schnack/Herbstakademie/CD-2008/frog-ejp.pdf
- Andre Geim, Physics Today (1998) — Everyone's magnetism: https://www.physics.umd.edu/grt/taj/411c/EveryonesMagnetism.pdf
- Harvard Gazette (2024) — How did you get that frog to float?: https://news.harvard.edu/gazette/story/2024/04/how-did-you-get-that-frog-to-float
- U.S. Department of Energy — How much power does a nuclear reactor produce?: https://www.energy.gov/ne/articles/infographic-how-much-power-does-nuclear-reactor-produce
- MIT Technology Review (2009) — Magnetically levitating mice: https://www.technologyreview.com/2009/09/11/93412/magnetically-levitating-mice/
- Journal of Physics Special Topics, U. de Leicester — cálculo de levitación diamagnética de un humano: https://journals.le.ac.uk/index.php/pst/article/view/2049

## Plan de Kling
**0 clips.** Tomás rechazó el fotorrealismo de IA (22-oct 23:26): todo es render 3D con el mismo look, así la rana y el laboratorio son siempre los mismos.
