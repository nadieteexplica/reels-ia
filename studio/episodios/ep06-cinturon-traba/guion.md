# Ep. 6 — El cinturón que se traba

**Versión 2.1 (23-oct-2026, ~20:05) — ganador del torneo de guiones (lección 95), esperando el OK de Tomás para la voz.** Sale de la ronda 2: el guion D ("Tira lento", ganador de la ronda 1 entre 4) mezclado con lo mejor de A (la mano a 5 cm de la bolsa), C (27° con inclinómetro y la gota en la máscara) y la revisión de producción (remate del doctor resuelto con el cuerpo, sin cara). v2.1 aplica lo que marcó la ronda 2: "jala" en vez de "tira" (público de YouTube sobre todo de México, Colombia y Perú), la bolsa cae atrás con la subida (así el doctor puede tenerla), píldora TAMBIÉN EN FRENADAS y DESDE 12° PUEDE. Torneo completo en `torneo/` (guiones, paquetes a ciegas y resultados) e investigación en `investigacion.md`.
**Voz:** Fernando Martínez · job pendiente (`jobs/voz/NNNN-ep06-cinturon-traba.json`), recién con el OK de Tomás.
**Línea:** datos · **Gancho:** "¿Cómo funciona por dentro?" dicho como regla que le pasa a todos ("jala rápido y te dice que no") · **Área:** tecnología cotidiana (auto) · **Formato:** comedia física + corte (entrar al pilar) + giro a mitad de video ("nadie tiró").
**Centro (en los primeros 2 s):** el cinturón mide qué tan rápido jalas: rápido se traba, lento te deja. El giro del medio: en la subida se traban los cuatro sin que nadie jale, porque una bolita de acero cree que te vas a volcar.
**Estilo:** realista (`estilo.json`), el del Ep. 5. Mundo abierto: camino de tierra y cerro de roca en el desierto de Atacama al atardecer, sol bajo de costado.
**Personajes (idea de Tomás: 4 lo más aleatorios posible, Mixamo With Skin del Release `Personajes`):** maneja un piloto de carreras (Racer) a paso de tortuga; de copiloto, un caballero con armadura (Castle Guard: revisar en la ficha que traiga texturas; si no, Astra o Gas Mask cambian de rol); atrás, el de la máscara antigás (Gas Mask) y un doctor (Chad). Mixamo no anima la cara: todo se actúa con cuerpo, objetos y cámara.
**Acción buscada:** enviar ("a ese que siempre pelea con el cinturón") y guardar el truco.
**Cuidado con el tema (Tomás):** nada que invite a no usar el cinturón, nada de choques ni heridas, nada de cómo manipular piezas, salud sólo general. Nadie se saca el cinturón en el video.

## Guion (109 palabras, ~40 s estimados a 2,9 palabras/s; se ajusta con `pausas.py`)
| # | Voz | Pantalla |
|---|---|---|
| 1 | Jala rápido y tu cinturón te dice que no. | Cuadro 0 con la acción en curso: camino de tierra plano, el caballero ya va lanzándose por la bolsa de papas del fondo del tablero; CLAC, el cinturón lo para y rebota contra el asiento (golpe de armadura) |
| 2 | Jala lento... y te deja. | Lo intenta despacio: la cinta sale suave; su mano queda a 5 cm de la bolsa |
| 3 | ¿Cómo sabe? La cinta vive en un carrete con dientes. | La cámara entra por la ranura del pilar, que se vuelve transparente: carrete con la cinta y rueda dentada. Píldora CARRETE |
| 4 | Si jalas de golpe, el carrete gira tan rápido... | 1 s afuera: el caballero jala de golpe. Adentro: el carrete gira veloz |
| 5 | ...que el giro empuja un pestillo hacia afuera, y se engancha. Clac. | Adentro: flecha FUERZA DEL GIRO empuja el pestillo hacia afuera y se engancha en los dientes. Afuera: el caballero rebota otra vez |
| 6 | Lento, el giro no alcanza. | Pantalla partida: adentro el carrete lento y el pestillo quieto; afuera el caballero se estira despacito |
| 7 | Pero el auto sube el cerro... y se traban los cuatro. | El 4x4 se empina; la bolsa se resbala hacia atrás y cae junto al doctor; CLAC ×4, los cuatro pegados al asiento. Inclinómetro chico subiendo. Nadie jaló |
| 8 | Nadie jaló. Fue una bolita de acero: rodó y trabó el carrete. | Adentro: la bolita de acero en su tacita; la tacita se inclina, la bolita rueda al borde, levanta una palanquita (flecha) y ésta muerde la rueda dentada. CLAC. Píldora TAMBIÉN EN FRENADAS |
| 9 | Pasado veintisiete grados, tiene que trabarse: cree que te vas a volcar. | Inclinómetro 27°, píldora DESDE 12° PUEDE · MÁS DE 27°: SE TRABA. El de la máscara mira el precipicio y le corre una gota por el vidrio de la máscara |
| 10 | Ya en plano: suéltalo un poquito... y jala lento. | Arriba, en plano: el de la máscara le hace la mímica lentísimo; el caballero suelta un poco la cinta y jala despacio: sale suave |
| 11 | Y ahí están, por fin, sus papas... | El caballero estira la mano despacio al tablero... la bolsa ya no está |
| 12 | ...si el doctor no se las comió antes. | Atrás, el doctor con la bolsa en la falda, una papa camino a la boca y migas naranjas en el delantal; lo pillan, se congela y se encoge de hombros. Corte al caballero lanzándose (loop al cuadro 0) |


## Predicción de la simulación (para calibrar con YouTube Studio)
Panel de 10 espectadores simulados (hombres y mujeres de 16 a 35, de México, Argentina, Colombia, Perú y Chile; 3 sin sonido), subagentes que no escribieron los guiones, con los videos en orden aleatorio y a ciegas.
- **Ronda 1 (4 guiones):** D "Tira lento" pasa los 3 s 100 % · llega al final 40 % · se rió 90 % · lo manda 20 % · nota 6,1 (A 100/30 · B 100/20 · C 80/20).
- **Ronda 2 (D contra esta mezcla):** **esta versión pasa los 3 s 100 % · llega al final 80 %** · se rió 100 % · lo manda 80 % · nota 7,3 (D en la misma ronda: 100/10).
- **Ojo al comparar:** la simulación no está calibrada todavía y en un mano a mano exagera la distancia (D bajó de 40 % a 10 % de final sin cambiar nada). Referencia real: en YouTube los Ep. 1–4 tuvieron 73–78 % de "visto" contra "deslizado". Se anota para comparar a las 48 h con visto/deslizado y % visto de YouTube Studio.

## Verificación por afirmación
| Afirmación del guion | Fuente(s) |
|---|---|
| Si jalas rápido el cinturón se traba; si jalas lento, te deja | Manual del Nissan Juke 2025 (el retractor se traba en una frenada brusca; tirar lento deja moverse) · Autoliv (el sensor de la cinta traba si se tira demasiado rápido) · manual Mazda CX-5 |
| La cinta vive enrollada en un carrete con una rueda dentada | Indiana Public Media, A Moment of Science (carrete con resorte y rueda dentada unida al carrete) · Gobierno de Montana, "How Seat Belts Work" (carrete y resorte) |
| Si jalas de golpe, el giro rápido del carrete empuja un pestillo hacia afuera y se engancha en los dientes | Indiana Public Media (la fuerza centrífuga de un tirón brusco saca hacia afuera una palanca unida al carrete, que engancha la rueda dentada) · patente US5451009 (la masa de inercia se queda atrás cuando el carrete acelera y bloquea el giro) · Safe Ride News (traba cuando la cinta sale rápido) |
| Lento, el giro no alcanza para trabarlo | Las mismas: el bloqueo de la cinta sólo actúa sobre cierta aceleración (US5451009: "above a first predetermined rate"); el Reglamento 16 prohíbe que se trabe con tirones de menos de 0,8 g |
| En la subida se traban sin que nadie jale: una bolita de acero rueda y traba el carrete | Safe Ride News (bola de acero en el anillo de un platillo: un cambio de velocidad o de orientación del auto la saca de su lugar y levanta la palanca hacia la rueda dentada) · artículo PMC3274245 en PubMed Central (copa en el pilar, bola de acero y uña que traba el cinturón cuando el auto se inclina) · Autoliv (el sensor del auto traba con aceleración, frenada o inclinación) |
| También en frenadas (píldora) | Indiana Public Media (en una frenada el peso se va adelante y traba) · Safe Ride News · Autoliv |
| Pasado 27° tiene que trabarse (desde 12° ya puede) | Reglamento 16 de la ONU §6.2.5.3.1.3–4 (no debe trabarse con 12° o menos; debe trabarse con más de 27° en los cinturones tipo 4) · PMC3274245 (traba cuando la carrocería pasa el ángulo permitido, 12–27°) |
| Cree que te vas a volcar (para eso es) | PMC3274245 (en un vuelco el bloqueo pasa a la fase que traba según el ángulo permitido) · Safe Ride News (cambio de orientación del vehículo) |
| Si se trabó: déjalo recoger un poquito y jala lento | Manual Mazda CX-5 y CX-3 (si está trabado, recogerlo una vez y sacarlo lento) · manual Nissan Juke (tirar firme, soltar y sacarlo suave) |

**Matices (para no exagerar):**
- "Tiene que trabarse" pasado 27° es lo que exige el Reglamento 16 de la ONU a los cinturones tipo 4 (autos); entre 12° y 27° la norma deja que cada fabricante elija (por eso la píldora DESDE 12° PUEDE). La norma de EE. UU. (FMVSS 209) usa otros ángulos: la voz no dice "por ley" ni "en todos los autos".
- La bolita puede ser un péndulo en otros modelos (US4166592A: "pendulum mounted weight or rolling ball"); se muestra la bolita porque es la más común en las explicaciones (Safe Ride News) y la del paper.
- La inclinación del cerro (~30°) es fuerte pero real para un 4x4; no se presenta como una calle común.
- El truco sólo sirve para el sensor de la cinta: por eso el guion lo usa "ya en plano" (con el auto inclinado la bolita lo sigue trabando).
- Nada imitable ni peligroso: nadie se saca el cinturón, el auto no choca ni se vuelca, no se abren ni se tocan piezas.
- Sin nombres, años ni quién lo inventó en la voz (regla de Tomás).

## Fuentes
- Autoliv — Seatbelts: https://www.autoliv.com/seatbelt
- Safe Ride News — Does your seat belt have a retractor? (PDF): https://www.saferidenews.com/wp-content/uploads/2018/11/Retractor-Type-Flyer-by-Safe-Ride-News.pdf
- Indiana Public Media, A Moment of Science — How seatbelts work: https://indianapublicmedia.org/amomentofscience/seatbelts/
- Development of an Emergency Locking Unit for a Belt-In-Seat System Using a MEMS Acceleration Sensor (PubMed Central): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3274245/
- Reglamento 16 de la ONU (CEPE), copia del texto: https://euroamerica-llc.com/wp-content/uploads/2021/01/ECE-R-16-Regulation.pdf
- Reglamento 16 de la ONU, original (MLIT Japón): https://www.mlit.go.jp/jidosha/un/UN_R016.pdf
- Manual Mazda CX-5 — Emergency Locking Mode: https://owners-manual.mazda.com/gen/en/cx-5/cx-5_8hy2ee19l/contents/03020102.html
- Manual Nissan Juke 2025 — Fastening the seat belts: https://www.nissan.ie/ownership/car-owner-manual/manuals/iom/juke/0f16/e0/2025/fastening-the-seat-belts-1.shtml
- Gobierno de Montana — 2.1 How Seat Belts Work (PDF): https://opifiles.mt.gov/portals/182/Page%20Files/Driver%20Education/Curriculum/Module%202%20all%20files/2.1-How-Seat-Belts-Work.pdf
- Patente US5451009 (retractor con sensor de la cinta): https://patents.google.com/patent/US5451009
- Patente US4166592A (péndulo o bola): https://patents.google.com/patent/US4166592A/en

## Plan de Kling
**0 clips** (todo render 3D realista). Las manos que agarran (la bolsa, la papa del doctor) se resuelven con el objeto apoyado y planos donde no se ven los dedos de cerca, o se piden 1–2 clips si la puerta 3 lo exige.
