# Ideas — método, puntaje y banco

## 1. Dónde buscar (cada semana, en este orden)
El método completo para encontrar datos (pruebas, familias, métodos de caza, datos quemados y ángulos) está en `docs/CAZA_DATOS.md`. Hay un chat dedicado a eso; sus datos aprobados llegan a §4.

1. **Comentarios y DMs de nuestros videos.** Las preguntas de la gente son oro: si se produce, se acredita en pantalla con "Pregunta de @usuario".
2. **Outliers con vidIQ** (plan gratis, con pocos créditos):
   - Máximo **1 búsqueda de outliers por semana** (5 créditos), con términos como "qué pasaría si", "cómo funciona", "por qué no podemos", "what happens if" o "how does it work".
   - Antes de buscar, se revisa el saldo con `vidiq_balance`.
3. **Web:**
   - r/todayilearned y r/explainlikeimfive, lo top de la semana.
   - Noticias de ciencia: LiveScience, ScienceAlert, Popular Science, BBC Mundo Ciencia, National Geographic.
   - Google Trends Chile y Latam.
4. **Calendario:**
   - verano en Chile (dic–feb: calor, sol, playa, helado),
   - invierno (frío, resfrío, lluvia),
   - Fiestas Patrias (sept),
   - Halloween, Navidad y Año Nuevo,
   - eclipses y lluvias de estrellas,
   - temblores y volcanes (siempre con respeto).
5. **Objetos cotidianos:** mira alrededor (cocina, baño, celular, calle, metro) y pregúntate "¿cómo funciona esto por dentro?" o "¿por qué parece mal hecho?".
6. **Datos abiertos** para el formato "lo conté yo" (deportes, sismos, transporte). Se revisa la licencia de cada base antes de usarla.
7. **Referencias virales** que manda Tomás: fichas y conclusiones en `docs/REFERENCIAS.md`.

## 2. Puntaje (de 0 a 5 en cada criterio)
| Criterio | Pregunta | Peso |
|---|---|---|
| Curiosidad | ¿La gente se lo pregunta o lo busca? | ×1,5 |
| Universalidad | ¿Le pasa o le importa a cualquiera, en cualquier país? | ×1,2 |
| Sorpresa | ¿El dato contradice lo que uno cree? | ×1,5 |
| Visual 3D | ¿Se puede mostrar con imágenes, sin explicar con texto? | ×1,3 |
| Enseñanza | ¿Deja algo útil o algo que contarle a otro? | ×1,0 |
| Verificable | ¿Hay 2 fuentes sólidas? (si es 0, se descarta) | ×1,0 |
| Compartible o guardable | ¿Dan ganas de mandárselo a alguien, o de guardarlo para después? | ×1,5 |

- **Filtro previo:** antes de puntuar, responder *¿a quién se lo mandan?* o *¿por qué lo guardarían?*. Sin respuesta, no se puntúa.
- **Costo de producción (proceso v2, 21-oct-2026):** después del puntaje, a cada idea elegida se le anota una estimación de costo: ¿cabe en **25–40 s** (72–115 palabras; techo 45 s) con un dato central y 2–3 pasos? ¿cuántas escenas (máx. 6) y cuántas necesitan una plantilla que no existe todavía? **No es un descarte:** la idea pesa más que la técnica (REFERENCIAS §3) y cada idea se diseña para su viralidad (decisión de Tomás, 19-oct). Si una idea muy buena cuesta más que el tope, se le pregunta a Tomás con la estimación.
- **Línea datos:** puntaje máximo 45. **Para producir hacen falta 32 o más.** Una idea con Verificable = 0 se descarta aunque sume.
- **Línea historias:** se puntúa solo con Curiosidad (¿engancha el cuadro 0?), Universalidad, Sorpresa (¿sorprende el giro?), Visual 3D y Compartible. Máximo 35; **para producir hacen falta 25 o más.**
- **Salud (YouTube, 21-oct-2026):** YouTube no monetiza "personas de IA" que hablan de salud o finanzas (`docs/YOUTUBE.md` §5) y nuestra voz es sintética. Los datos curiosos del cuerpo siguen, pero con menos peso: Universalidad −1 si el tema es de salud, y nunca algo que suene a consejo.
- **Ajuste mensual:** los pesos se ajustan con los datos de `PUBLICADOS.md`. Por ejemplo, si los temas del cuerpo rinden el doble en envíos, sube su prioridad.
- **Variedad:** nunca 2 videos seguidos con el mismo gancho o la misma área (cuerpo, tecnología, planeta…).

## 3. Lista negra
- Retos o experimentos que alguien pueda imitar y salir herido.
- Tragedias recientes, política y religión.
- Salud que suene a indicación médica.
- Personajes, marcas o franquicias con derechos de autor como protagonistas.
- Temas ya publicados: se revisa `PUBLICADOS.md` antes de elegir.
- El pulpo, que a Tomás no le gustó como tema.
- Firmas de otras cuentas contadas igual: los megaproyectos narrados en imperativo de Zack D. Films, la casa con patio de `hiddenhome.3d`, las frutas humanizadas.

## 4. Banco de ideas
Todos los datos están por **verificar** al producir; acá solo van como pista.

**Estados:** `usada`, `siguiente`, `pendiente`.

### Cuerpo humano
| Estado | Gancho | Dato central (verificar) | Imagen 3D clave | Enseñanza |
|---|---|---|---|---|
| usada (Ep. 1) | ¿Por qué te duele la frente con el helado? | Vasos del paladar + trigémino → dolor referido | Corte de la cabeza, vasos que se cierran y se abren | Lengua contra el paladar |
| pendiente | ¿Por qué se te arrugan los dedos en el agua? | No es el agua que entra: es el sistema nervioso; con un nervio cortado no se arrugan | Dedo por dentro, vasos que se contraen | Teoría del "agarre en mojado" |
| pendiente | ¿Qué suena cuando te tronas los dedos? | Una burbuja que se forma en el líquido de la articulación (resonancia magnética en 2015); no hay evidencia de que cause artritis | Articulación por dentro, la burbuja que aparece | Por qué hay que esperar ~20 min para volver a tronarlos |
| pendiente | ¿Por qué no te puedes hacer cosquillas a ti mismo? | El cerebelo predice tu propio movimiento y "apaga" la sorpresa | Cerebro anticipando la mano | Con un intermediario (un robot) sí funciona |
| pendiente | ¿Por qué se te duerme la pierna? | Presión sobre nervios y vasos → señales cortadas → hormigueo al volver | Nervio aplastado como manguera | Cómo despertarla rápido |
| pendiente | ¿Por qué estornudas al mirar el sol? | Reflejo fótico, que tiene una parte importante de la población | Cables del ojo y de la nariz que se cruzan | Si te pasa, es genético |
| pendiente | ¿Por qué te suena el estómago con hambre? | Borborigmos: el intestino "barre" cada cierto tiempo aunque esté vacío | Intestino haciendo ola | Ese ruido es limpieza, no hambre |
| pendiente | ¿Por qué ves estrellitas al pararte rápido? | Baja la presión al cerebro por unos segundos | Sangre que "se cae" a las piernas | Párate en 2 tiempos |
| pendiente | ¿Por qué se te pone la piel de gallina? | Músculos diminutos que paran cada pelo: un vestigio de cuando teníamos pelaje | Pelos que se paran | Por qué pasa también con música |
| pendiente | ¿Cuánta energía gasta tu cerebro? | Cerca del 20% de tu energía, siendo ~2% de tu peso | Cerebro como ampolleta gigante | Por qué pensar cansa |
| pendiente | ¿Por qué una canción se te pega? | "Gusanos auditivos"; un estudio vio que mascar chicle ayuda | Canción en loop dentro de la cabeza | Truco del chicle |
| pendiente | ¿Por qué la cebolla te hace llorar? | Gas irritante que se forma al cortar | Célula de cebolla que explota en gas | Cebolla fría + cuchillo afilado |
| pendiente | ¿Por qué no puedes estornudar con los ojos abiertos? | Es un reflejo, y es mito que se te salgan los ojos | Cara en cámara lenta | Mito derribado |

### Tecnología cotidiana: cómo funciona por dentro
| Estado | Gancho | Dato central (verificar) | Imagen 3D clave | Enseñanza |
|---|---|---|---|---|
| pendiente | La tarjeta del metro no tiene batería… ¿cómo funciona? | El lector genera un campo que alimenta el chip por inducción (NFC/RFID) | Ondas que encienden el chip | Por qué hay que acercarla |
| pendiente | ¿Cómo sabe el semáforo que llegaste? | Una espira enterrada en el pavimento detecta el metal del auto | Corte del asfalto con la bobina | Por qué a veces no detecta las bicis |
| pendiente | ¿Por qué el microondas calienta disparejo? | Ondas estacionarias con puntos calientes y fríos | Ondas rebotando dentro | Revolver o dejar reposar |
| pendiente | ¿Cómo sabe tu celular hacia dónde lo giras? | Un chip con una masa microscópica que se mueve (MEMS) | Zoom al chip, la masa que oscila | Por qué se calibra la brújula |
| pendiente | Un QR roto igual funciona… ¿por qué? | Corrección de errores: puede perder hasta ~30% | QR al que le sacan pedazos | Por qué tienen esos 3 cuadrados |
| pendiente | ¿Cómo enfría el refrigerador si el frío no se fabrica? | Se *saca* el calor con un gas que se evapora | Gas que absorbe calor y sale por atrás | Por qué la parte de atrás está caliente |
| pendiente | ¿Por qué la olla a presión cocina más rápido? | El agua hierve sobre 100 °C con presión | Burbujas a presión | Cómo abrirla segura |
| pendiente | ¿Por qué los aviones dejan rayas blancas? | Estelas: el vapor del motor se congela | Escape que se convierte en cristales | Qué te dicen del clima |

### ¿Qué pasaría si…?
| Estado | Gancho | Dato central (verificar) | Imagen 3D clave | Enseñanza |
|---|---|---|---|---|
| pendiente | ¿Qué pasaría si la Tierra dejara de girar? | La atmósfera y los océanos seguirían moviéndose a cientos de km/h en el ecuador | Planeta que frena, vientos | Por qué no sentimos que gira |
| pendiente | ¿Y si cavaras un túnel que atraviese la Tierra y saltaras? | Unos 42 minutos al otro lado ("tren gravitatorio") | Caída por el túnel | Cómo funciona la gravedad adentro |
| pendiente | ¿Y si el Sol se apagara? | No lo notarías por unos 8 minutos | Luz viajando del Sol | La luz que ves es del pasado |
| pendiente | ¿Y si la Luna desapareciera? | Las mareas bajarían a cerca de 1/3, las noches serían más oscuras y el eje se volvería inestable a largo plazo | Mar que baja | Para qué sirve la Luna |
| pendiente | ¿Y si gritaras en el espacio? | No se escucha nada: el sonido necesita aire | Onda de sonido que no avanza | Por qué en las películas sí suena |
| pendiente | ¿Y si todo el mundo saltara al mismo tiempo? | Prácticamente nada: la Tierra es muchísimo más pesada | 8.000 millones saltando | Escala de las cosas |

### ¿Por qué no podemos…?
| Estado | Gancho | Dato central (verificar) | Imagen 3D clave | Enseñanza |
|---|---|---|---|---|
| pendiente | ¿Por qué no podemos tomar agua de mar? | El riñón necesita más agua para sacar esa sal: te deshidrata | Riñón saturado de sal | Cómo se potabiliza (desaladoras) |
| pendiente | ¿Por qué no podemos respirar bajo el agua si el agua tiene oxígeno? | Hay muchísimo menos oxígeno disuelto que en el aire | Branquia vs pulmón | Cómo lo hacen los peces |
| pendiente | ¿Por qué no podemos ver en la oscuridad como los gatos? | Capa reflectante detrás del ojo y más bastones | Ojo de gato por dentro | Por qué les brillan los ojos |
| pendiente | ¿Por qué no recuerdas cuando eras bebé? | Amnesia infantil: el hipocampo todavía se está formando | Recuerdos que no se "guardan" | Tu recuerdo más antiguo puede ser inventado |
| pendiente | ¿Por qué no podemos cavar hasta el centro de la Tierra? | El pozo más profundo (Kola) llegó a ~12 km y a unos 180 °C | Corte de la Tierra con el pozo | Qué tan profundo es "profundo" |

### ¿Sabías que…? (planeta, naturaleza, espacio, Chile)
| Estado | Gancho | Dato central (verificar) | Imagen 3D clave | Enseñanza |
|---|---|---|---|---|
| en producción (Ep. 2, ficha abajo) | Los pájaros no sienten el picante | El receptor que nos hace arder con la capsaicina no reacciona en las aves; el ají "eligió" a quién quemar | Pájaro tranquilo comiendo ají al lado del protagonista que llora con el mismo ají | Si te pica: leche (aunque sea descremada); las bebidas con gas, peor |
| pendiente | ¿Por qué Chile tiembla tanto? | La placa de Nazca se mete bajo Sudamérica varios cm por año | Placas chocando bajo Chile | Qué hacer en un temblor |
| pendiente | ¿Por qué el desierto de Atacama es el más seco del mundo? | Corriente de Humboldt + cordillera + alta presión | Nubes que no pasan | Por qué hay observatorios ahí |
| pendiente | ¿Por qué el cielo es azul y el atardecer naranjo? | La luz azul se dispersa más (dispersión de Rayleigh) | Rayos de luz rebotando | Por qué en Marte es al revés |
| pendiente | ¿Por qué el hielo flota? | El agua se expande al congelarse, y eso salva a los peces en invierno | Moléculas formando una red | Por qué revientan las botellas en el congelador |
| pendiente | Un rayo es más caliente que el Sol | Unos 30.000 °C contra ~5.500 °C de la superficie del Sol | Rayo en cámara lenta | Por qué suena el trueno |
| pendiente (quemado: solo con ángulo nuevo) | Los plátanos son radiactivos | Tienen potasio-40, pero la dosis es mínima | Plátano con átomos brillando | Qué es la radiación de verdad |
| pendiente (quemado: solo con ángulo nuevo) | Hay más árboles en la Tierra que estrellas en la Vía Láctea | ~3 billones de árboles (estudio de 2015) | Bosque vs galaxia | Escala |

#### Ficha Ep. 2 — Los pájaros no sienten el picante (caza del 19-oct-2026)
- **Dato central (verificado, 2 fuentes independientes):**
  - El receptor de la capsaicina (vanilloide/TRPV1) de las aves no responde a la capsaicina; sí responde al calor real. Jordt y Julius, *Cell* 108(3), 2002 ([Duke Scholars](https://scholars.duke.edu/publication/1003152)).
  - En el chiltepín (ají silvestre de México/Arizona) solo comían los frutos los cuitlacoches (*curve-billed thrasher*); ratas de campo y ratones del cactus los evitaban. Las semillas salen enteras del pájaro y germinan; las que mastica el roedor no. Tewksbury y Nabhan, *Nature* 2001 ([U. of Florida](https://archive.news.ufl.edu/articles/2001/07/for-peppers-hot-quite-literally-the-spice-of-life-uf-research-shows.html) · [Harvard SITN](https://sites.harvard.edu/sitn/2012/11/29/issue131b)).
  - Decirlo como "los científicos creen que" el picante evolucionó para alejar a los mamíferos (hipótesis de la disuasión dirigida).
- **"Y lo más loco" (verificado):** hay un mamífero que tampoco lo siente: la tupaya china (*Tupaia belangeri chinensis*, pariente lejano de los primates) come una planta picante (*Piper boehmeriaefolium*) porque una mutación en su TRPV1 le quita un aminoácido. Han et al., *PLOS Biology* 2018 ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6042686) · [Smithsonian](https://www.smithsonianmag.com/smart-news/tree-shrews-peppers-feel-the-burn-180969702/)).
- **Enseñanza (verificada, con matiz):** en un estudio con 72 personas, la leche (entera o descremada) fue lo que más bajó el ardor; las bebidas con gas rindieron peor y el alcohol lo empeora. No decir "el agua no sirve": todas las bebidas bajaron algo el ardor. Nolden, Lenart y Hayes, *Physiology & Behavior* 2019 ([Penn State](https://www.psu.edu/news/research/story/milk-best-drink-reduce-burn-chili-peppers) · [ScienceDaily](https://www.sciencedaily.com/releases/2019/06/190625133526.htm)).
- **Por qué esta idea (simulación del chat de caza, 19-oct):** salió #1 de 10 (34 % de probabilidad de ser la más vista). Lo que la empuja:
  - nadie ha contado el dato en español (revisión en vidIQ, IG + TikTok desde 2023);
  - la imagen "pájaro + ají" ya está probada: una animación de humor con pájaros comiendo ají hizo 2,1 M en español, y los videos 3D de pájaros andan bien (1,6 M). **No copiarla:** en esa los pájaros sufren; lo nuestro es justo lo contrario y con personaje propio;
  - tiene destinatario clarísimo: "mándaselo al que se cree inmune al picante". Sin ese destinatario, la ventaja sobre la #2 (plantas) desaparece.
- **No perder:** pájaro + ají en el cuadro 0; cierre con envío a ese amigo (marcarlo en `PUBLICADOS.md`); la enseñanza de la leche.
- **Producción:** el pájaro es el protagonista visual y no hay anatomía de aves en Z-Anatomy → modelo CC0 con licencia revisada. El interior de la lengua y el nervio del humano puede usar la "cabeza de vidrio" (§8 del manual). Máximo 2–3 planos con Kling (morder el ají, reacción, tomar leche).

### Parece un error, pero es a propósito (objeto en primer plano)
| Estado | Gancho | Dato central (verificar) | Imagen 3D clave | Enseñanza |
|---|---|---|---|---|
| pendiente | ¿Por qué la tapa del lápiz tiene un agujero? | Para que pase aire si alguien se la traga | Tapa en corte con el flujo de aire | Por qué no hay que morder tapas |
| pendiente | ¿Por qué la ventana del avión tiene un agujerito? | Iguala la presión entre los vidrios para que la carga la tome el vidrio exterior | Ventana en corte con las capas | Qué pasa si se tapa |
| pendiente | ¿Para qué es el bolsillo chico de los jeans? | Nació para guardar el reloj de bolsillo | Jeans con el reloj entrando | De dónde vienen los diseños de la ropa |
| pendiente | ¿Por qué la F y la J del teclado tienen una rayita? | Para ubicar los índices sin mirar | Manos llegando al teclado a ciegas | Cómo escribir sin mirar |

### Lo conté yo (datos propios)
| Estado | Gancho | Fuente de datos (confirmar acceso y licencia) | Imagen 3D clave | Acción buscada |
|---|---|---|---|---|
| pendiente | ¿Cuántas veces tembló en Chile este año? Los conté | Catálogo del Centro Sismológico Nacional | Cada sismo es una esfera que cae sobre el mapa de Chile | Enviar |
| pendiente | ¿Cuál es la estación de metro más usada de Santiago? | Datos de afluencia de Metro | Una persona por cada mil pasajeros, apilándose en cada estación | Enviar |
| pendiente | ¿De qué minuto salen más goles? | Base abierta de partidos (por definir) | Cada gol es una pelota que cae en su minuto | Enviar y comentar |

### Historia e ingeniería · experimentos mentales
| Estado | Gancho | Dato central (verificar) | Imagen 3D clave | Enseñanza |
|---|---|---|---|---|
| pendiente | ¿Por qué las ventanas de los aviones son redondas? | El Comet (1954): las esquinas cuadradas concentraban la tensión y se agrietaban | Avión en un tanque de agua, grieta en la esquina | Por qué las esquinas redondas aguantan más |
| pendiente | Con 23 personas en una pieza, hay 50 % de que dos estén de cumpleaños el mismo día | La paradoja del cumpleaños | Pieza que se llena y parejas que se conectan | Por qué la intuición falla con las probabilidades |
| usada (Ep. 3, sale el 22-oct 10:00) | Un edificio de 7.600 toneladas se fue caminando | Shanghái, 2020: una escuela de 1935 "caminó" 62 m sobre 198 patas robóticas para dejarle el sitio a un centro comercial | El edificio de cinco pisos con patitas, dando pasos por la ciudad | La reacción la pone la gente ("¿no era más fácil hacer el mall en otro lado?"); el video no la explica |

#### Ficha — El edificio que caminó (caza del 21-oct-2026, verificado)
- **Qué pasó:** en octubre de 2020 movieron la Escuela Primaria Lagena (Shanghái, construida en 1935, cinco pisos, en forma de T, más de 7.600 toneladas) para dejar el terreno a un complejo de oficinas y comercio. No la demolieron: era patrimonio.
- **Cómo:** 198 patas robóticas hidráulicas debajo del edificio, en **dos grupos que se turnan** para levantar y avanzar, imitando pasos humanos. Rieles no servían porque el camino era curvo y había que girarlo.
- **Cifras:** 62 m (203 pies) en **18 días**, girándolo ~21° de paso; llegó el 15-oct-2020. Lo hizo la empresa Shanghai Evolution Shift, con un sistema creado en 2018. Después quedó como centro cultural.
- **Fuentes (2, coinciden en peso, patas, distancia, días y giro):** [The Drive](https://www.thedrive.com/news/37679/watch-a-giant-walking-machine-relocate-an-entire-five-story-school-building) (cita a CNN) · [Oddity Central](https://www.odditycentral.com/architecture/robot-legs-help-7600-tonne-building-walk-to-new-location.html) (cita al South China Morning Post). Giro: una dice "unos 20°" y la otra 21° → decir "unos 20 grados".
- **Ojo al guion:** el video muestra el absurdo y no cierra con moraleja ni con "¿para qué sirvió?" narrado (gusto de Tomás, `CAZA_DATOS.md` §9).
- **Estilo (decisión de Tomás, 21-oct):** semi-realista, un solo estilo; no se le muestran opciones. Antes de producir, el chat del video hace un estudio corto (algoritmo de las 3 redes, nuestras métricas, videos parecidos) y guarda las conclusiones en `docs/estudios/ep03.md`.

### Procesos: cómo se hace, cómo se genera, qué pasa si (ronda 5, 21-oct-2026, 👍 de Tomás, verificadas)
| Estado | Gancho | Dato central (verificado) | Imagen 3D clave | Enseñanza |
|---|---|---|---|---|
| **usada: Ep. 4** (22-oct-2026) | La cortina de la ducha te persigue (y no es un fantasma) | El chorro arma un remolino acostado dentro de la ducha; su centro tiene baja presión y chupa la cortina. Pasa también con agua fría | La ducha en corte con el remolino girando como una rueda y la cortina que se mete | El agua caliente lo empeora |
| pendiente (ficha abajo) | El vidrio de tu ventana se hizo flotando sobre metal derretido | Vidrio a 1.100 °C se vierte sobre una piscina de estaño fundido, flota y se aplana solo; sale a 600 °C | La cinta de vidrio naranja deslizándose sobre el espejo de estaño | Con luz ultravioleta se ve cuál lado tocó el estaño |
| usada: Ep. 5 (sale el 24-oct) | Con un imán gigante puedes hacer flotar a un ser vivo | El agua del cuerpo es repelida un poquito por los imanes: con ~16 T flotó una rana viva; la NASA hizo flotar ratones por horas | La rana flotando dentro del tubo del imán | Todo lo que tiene agua (tú también) es levemente "antimagnético" |

#### Ficha — La cortina de la ducha (verificada)
- **Por qué le gustó a Tomás:** una vez pensó que le estaban penando porque la cortina se movía sola. Gancho natural: "no es un fantasma".
- **Escalera:** (1) la teoría vieja: el aire caliente sube y entra aire frío por abajo (Popular Science, 1938); (2) pero pasa igual con agua fría; (3) otra teoría: Bernoulli, el chorro arrastra aire; (4) en 2001 David Schmidt (U. de Massachusetts Amherst) simuló una ducha en su PC: 50.000 celdas, 1,5 billones de cálculos, dos semanas corriendo de noche porque en la mañana su señora le hacía reiniciar el computador; (5) resultado: el chorro arma un **remolino acostado**, como una rueda de agua, y su centro de baja presión chupa la cortina. Ganó el Ig Nobel 2001.
- **Matiz obligatorio:** en 2007 otro investigador mostró que el agua caliente sí produce un efecto más fuerte que la fría: el calor ayuda, pero no es la causa principal. Decir "pasa hasta con agua fría", no "el calor no tiene nada que ver".
- **Fuentes (independientes):** [Popular Science](https://www.popsci.com/why-do-shower-curtains-billow-inward-0/) · [The Straight Dope (carta del propio Schmidt)](https://www.straightdope.com/21343421/why-does-the-shower-curtain-blow-in-despite-the-water-pushing-it-out-revisited) · [NASW, ScienceWriters 2001-02](https://nasw.org/sites/default/files/sciencewriters/html/win0102tex/shower.htm) · [Mental Floss](https://www.mentalfloss.com/science/physics/why-does-shower-curtain-always-try-get-me).
- **Producción:** un solo set (baño), tela de la cortina y el remolino visible con partículas o vapor. Barata.
- **Producida como Ep. 4 (22-oct-2026):** `studio/episodios/ep04-cortina-ducha/`. Ojo: el eje del remolino es **perpendicular a la cortina** (Schmidt en Scientific American, fuente sumada); "de costado" no alcanza para dibujarlo.
- **Decisión de Tomás (21-oct, 23:27):** el video **no cuenta el estudio** (nada de "en 2001 un científico simuló…", ni el Ig Nobel ni el computador reiniciado: aburre). Se explica directo cómo pasa: no es el aire caliente (pasa hasta con agua fría) → es un remolino → su centro chupa la cortina. Las fuentes van en la descripción y el primer comentario. Personaje nuevo, no el del helado.

#### Ficha — El vidrio flotado (verificada)
- **Cómo se hace de verdad (Pilkington y Guardian Glass coinciden):** el horno funde arena, soda y caliza a ~1.500–1.600 °C; el vidrio entra a ~1.100 °C a un baño de **estaño fundido**, flota encima y se extiende solo hasta quedar plano y liso; sale sólido a ~600 °C; después se templa en un horno largo (lehr), se inspecciona y se corta con ruedas de diamante. La línea mide casi medio kilómetro. El grosor "natural" que toma solo era de 6,8 mm; hoy con otros ajustes va de menos de 1 mm a 25 mm.
- **Historia:** Alastair Pilkington empezó a experimentar en diciembre de 1952; 7 años y £28 millones después lo anunciaron, el 20-ene-1959. Lo de que se le ocurrió lavando platos es un mito que él mismo negaba (Pilkington).
- **Giro 1:** el lado que tocó el estaño queda con una capa finísima de estaño y **brilla con luz ultravioleta**; las vidrierías usan una lámpara para saber qué lado es (Nakajima Glass, Bohle).
- **Giro 2 (mito al revés):** los vitrales viejos más gruesos abajo **no** son vidrio que "se chorreó": el vidrio tardaría miles de millones de años en deformarse algo visible (Penn State 2018, Scientific American). Eran hechos a mano, disparejos. Antes del flotado, el vidrio plano se pulía a mano o con máquinas.
- **Fuentes:** [Pilkington, el paso a paso](https://www.pilkington.com/en/global/knowledge-base/glass-technology/the-float-process/the-float-process-step-by-step) · [Guardian Glass (PDF)](https://www.guardianglass.com/content/dam/guardianindustriesholdings/collateral/usca/brochure_expert_series_EN_doc5_mfg_process_float_glass_2020.pdf) · [Pilkington, la invención](https://www.pilkington.com/en/gbl/about-us/pilkington-history/invention-of-float-glass) · [Nakajima Glass, lado estaño con UV](https://www.ngci.co.jp/en/tech/tech_kn1/) · [Penn State](https://www.psu.edu/news/research/story/researcher-uses-westminster-abbey-windows-shine-light-glass-myth) · [Scientific American](https://www.scientificamerican.com/article/fact-fiction-glass-liquid/).
- **Producción:** 3–4 escenas (horno, baño de estaño, horno de templado y corte, ventana con UV). Render tipo producto (R8).

#### Ficha — El imán que hace flotar seres vivos (verificada)
- **Qué pasó:** Andre Geim, en el Laboratorio de Campos Magnéticos Altos de Nijmegen (Países Bajos), hizo flotar una rana viva dentro de un imán de ~16 teslas (Geim y Berry, *European Journal of Physics* 1997). Empezó como un experimento de viernes en la noche. Ganó el Ig Nobel por eso y en 2010 el **Nobel de Física** de verdad, por el grafeno: es el único con los dos.
- **Cómo funciona:** el agua es diamagnética: un campo muy fuerte la repele un poquito. Como los seres vivos son casi pura agua, con suficiente campo esa fuerza le gana a la gravedad.
- **"Y lo más loco":** en 2009 la NASA (JPL) hizo flotar ratones de 10 g por horas en un imán superconductor de 17 T, con comida y agua, para estudiar cómo afecta la falta de gravedad a los huesos. El primero se veía agitado y desorientado.
- **Ojo:** no decir que se ha hecho flotar a una persona ni que "se podría" sin una fuente que lo diga.
- **Fuentes:** [Geim y Berry, EJP 1997 (PDF)](https://obelix.physik.uni-bielefeld.de/~schnack/Herbstakademie/CD-2008/frog-ejp.pdf) · [Harvard Gazette](https://news.harvard.edu/gazette/story/2024/04/how-did-you-get-that-frog-to-float) · [NobelPrize.org](https://www.nobelprize.org/prizes/physics/2010/geim/facts/) · [MIT Technology Review](https://www.technologyreview.com/2009/09/11/93412/magnetically-levitating-mice/) · [NBC/Space.com](https://www.nbcnews.com/news/amp/wbna32760311).
- **Producción:** rana y ratón animados (seres vivos: más costo); el tubo del imán y el laboratorio.
- **Decisión de Tomás (22-oct, 23:12) — así es el video:** "¿Sabías que…?" + "¿qué pasa si…?". **Parte real:** una rana flota dentro de un imán gigante (sin narrar quién, cuándo ni ningún estudio: se cuenta directo lo que pasa; fuentes abajo). **Parte fantasía:** "¿y si quisiéramos hacer flotar a una persona?": la escena donde **se construye ese imán** y cómo tendría que ser, con números reales. **Realismo de verdad**, no el look animado de los episodios anteriores ni el personaje de MakeHuman (ya no le gusta).
- **Números para la fantasía (Geim, *Physics Today* 1998, "Everyone's magnetism" — [PDF](https://www.physics.umd.edu/grt/taj/411c/EveryonesMagnetism.pdf)):** hacer flotar a un humano "requeriría un imán especial de casi 40 T y alrededor de **un gigavatio** de consumo continuo"; con la tecnología de entonces los imanes aceptaban objetos de hasta ~15 cm. 1 GW ≈ lo que produce un reactor nuclear típico ([Departamento de Energía de EE. UU.](https://www.energy.gov/ne/articles/infographic-how-much-power-does-nuclear-reactor-produce)). Segunda fuente para el cálculo del humano: [Journal of Physics Special Topics, U. de Leicester](https://journals.le.ac.uk/index.php/pst/article/view/2049) (trabajo de estudiantes: usarla para cruzar, no sola). El mismo artículo de Geim: la rana no sufrió efectos, salvo desorientarse por la falta de peso; voluntarios pasaron hasta 40 h en un imán de 4 T sin efectos.
- **Ojo con el imán del refri:** las fuentes no calzan (Geim: 10 T ≈ 100 veces un imán de refri; MIT Technology Review: 17 T ≈ 10.000 veces). No usar un "X veces" sin resolverlo; si no se resuelve, decir "cientos de veces más fuerte".

### Mecánicas: cómo se hizo, cómo funciona, cómo se hace (ronda 6, 23-oct-2026, esperando 👍/👎 de Tomás)
Pedido de Tomás (23-oct, 18:58): el Ep. 3 (edificio) fue el que más rindió "por lejos" y él cree que fue por **mostrar la mecánica** (el hoyo, cómo ponían las patas): ideas de "cómo funciona la mecánica" / "el arte de crear algo", abiertas a todo. ADN buscado: imagen "qué weá" que se entiende sola en el cuadro 0 + mecánica real paso a paso + un giro ingenioso a mitad de video.
**Ojo:** las fuentes están **ubicadas** (la página existe y trata el tema), no leídas: las cifras van **por verificar** y se verifican a fondo sólo las 👍 (regla de §9 de `CAZA_DATOS.md`). Lo de "quemado" es estimado (vidIQ sin créditos hasta el 18-nov).

| # | Estado | Gancho | Mecánica (escalera) | Giro | Puntaje | Quemado | Costo |
|---|---|---|---|---|---|---|---|
| 1 | pendiente | En Corea tocaban el celular con salchichas. ¿Por qué funcionaba? | Grilla invisible de electrodos bajo el vidrio → el chip la barre muchas veces por segundo → el dedo (agua con sal) "roba" carga en un cruce → el guante aísla | La salchicha conduce como un dedo (Corea, invierno 2010). **No decir** que subieron las ventas: no hay cifra | 40,2 | medio el touch; poco la salchicha | 4 escenas, bajo |
| 2 | pendiente | ¿Cómo sabe la pistola de bencina que el estanque se llenó? | Agujerito en la punta con un tubo hasta una membrana → el chorro chupa aire por ahí (Venturi) → el líquido tapa el agujero → vacío → la membrana suelta el pestillo: clic | No tiene sensor, chip ni electricidad: es un agujero y aire | 39,0 | poco | 4 escenas, 1 asset a medida (pistola en corte) |
| 3 | **siguiente: datos verificados (24-oct), ficha abajo** | Este rascacielos se achicó piso por piso, sin explosión | El último piso se vuelve un "sombrero" sobre gatas → abajo desarman el piso → las gatas bajan el sombrero → se repite (Tecorep de Taisei, Tokio) | Las grúas de adentro generan electricidad al bajar los escombros. Variante: Kajima corta el piso 1 y baja el edificio entero | 37,8 | medio (viral en inglés en 2013) | 4–5 escenas, medio |
| 4 | pendiente | Este túnel de ~73.000 t llegó flotando por el mar | Tramos de concreto hechos en tierra → tapas de acero y flota → remolque → lastre y se hunde en una zanja → gatas lo tiran contra el anterior (Fehmarnbelt, 2026) | Bombean el agua entre las dos tapas y **el mar mismo lo aprieta** contra la junta de goma y lo sella | 37,8 | poco | 5 escenas, medio |
| 5 | pendiente | Giraron este edificio 90° con 600 personas trabajando adentro | Central telefónica de ~11.000 t que no se podía apagar → sobre rodillos → gatas a mano, ~38 cm por hora → luz, agua, gas y teléfono por conexiones que se estiraban (Indiana Bell, 1930) | Nadie dejó de trabajar ni un día | 36,8 | poco | 4 escenas, bajo–medio. Pariente directo del Ep. 3: diferenciarlo con la gente adentro |
| 6 | **usada (Ep. 6, 24-oct)** | ¿Por qué el cinturón se traba si lo tiras rápido? | Carrete con resorte y rueda dentada → un peso se va hacia adelante al frenar y muerde la rueda → pesitos centrífugos traban si la cinta sale rápido | Tirón suave pasa, tirón brusco se traba. Volvo liberó la patente de 1959 | 35,7 | poco | 4 escenas, medio |
| 7 | pendiente | El vidrio de tu celular se endurece en sal derretida | El vidrio se baña en sal de potasio derretida (~400 °C, horas) → los iones de potasio, más grandes, toman el lugar de los de sodio → la superficie queda apretada | No es una lámina encima: es el mismo vidrio con átomos metidos a presión (analogía: una micro llena). Sin nombrar la marca | 34,7 | poco | 4–5 escenas, bajo |
| 8 | pendiente | Este espejo de 8 m se hace en un horno que gira | ~17–20 t de vidrio sobre un molde de panal → horno a ~1.165 °C girando ~5 vueltas por minuto → la fuerza centrífuga curva el vidrio líquido → 3 meses enfriando, años puliendo (Telescopio Gigante de Magallanes, va a Las Campanas, Chile) | La curva no se talla: la hace el giro, como el agua en un balde que da vueltas | 34,6 | no visto | 5 escenas, medio |
| 9 | pendiente | Arrastraron por el mar una torre más alta que el Empire State | Se construye parada en un fiordo, hundiéndola con lastre → le pasan la cubierta por encima → sacan lastre y sube → remolque ~200 km → se hunde a ~300 m (Troll A, Noruega, 1995) | Todo se hace subiendo y bajando con agua; ~472 m de torre, casi toda bajo el agua (récord Guinness) | 34,1 | poco | 5 escenas, medio–alto (agua y escala) |
| 10 | pendiente | En los Andes, el sol convierte la nieve en cuchillas | Aire seco y sol fuerte → la nieve pasa directo a vapor sin derretirse → cada hoyito atrapa más luz y se hunde más → bosque de cuchillas de 1 a varios metros, inclinadas al sol (penitentes) | No los talla el viento: los talla el sol | 33,6 | no visto | 4 escenas, barato |
| 11 | pendiente | Hace un segundo, esta lata era un disco plano | Disco de ~0,27 mm → vaso → 3 anillos de planchado lo estiran al triple → pared de ~0,1 mm → domo en el fondo para la presión | La bebida nunca toca el aluminio: adentro va barniz rociado | 33,0 | medio | 5 escenas, bajo–medio |
| 12 | pendiente | Este alambre se vuelve tornillo sin perder ni una viruta | Alambre cortado → la cabeza se forma a golpes en frío → rueda entre dos placas con surcos y la rosca aparece de una pasada | La rosca no se talla, se aplasta: el tornillo sale más ancho que el alambre | 32,2 | no visto | 4 escenas, bajo |

**Reserva (buenas, con un problema cada una):** encendedor de cocina sin pila (piezo; falta 2.ª fuente fuerte) · camiones de ALMA (antena de 100+ t a 5.000 m; Chile, menos universal) · Chicago levantó la ciudad con tornillos (1860, hotel con huéspedes adentro) · escalera mecánica (¿dónde se van los escalones?; medio quemada) · bombón que se derrite solo con una enzima (poco común en Latam, 31,3) · cristales de Naica (México) · moáis que "caminaban" (ADN del Ep. 3, pero quemado en español, hipótesis discutida y 18 personajes) · elástico = rebanada de manguera · gomitas moldeadas en maicena · rayas de la pasta de dientes (confirmar qué método se usa hoy).
**Descartados:** máquina de peluches (quemada: viral de TikTok 2022) · Palm Jumeirah y grúa autotrepante (quemadas) · canal de Panamá y tuneladora (muy explicados en español) · El Teniente (accidentes recientes: lista negra; para más adelante) · cajones de Brooklyn (tono oscuro) · reloj de cuarzo, espejo adaptativo del ELT y nieve artificial (física de nerd) · torre de perdigones (plomo fundido).

**Fuentes ubicadas (2 por idea; leer antes del guion):**
1. Touch: [TED-Ed, salchicha vs. guante](https://www.ted.com/talks/charles_wallace_and_sajan_saini_why_a_sausage_can_do_what_your_gloves_cannot) · [Engadget 2010](https://www.engadget.com/2010-02-11-south-korean-iphone-users-turn-to-sausages-as-a-cold-weather-me.html)
2. Pistola de bencina: [Hagerty](https://www.hagerty.com/media/maintenance-and-tech/how-the-venturi-effect-enables-gas-pump-shutoffs-and-carburetors/) · [Mental Floss](https://www.mentalfloss.com/article/28113/how-gas-pump-knows-when-shut) · patente US4098306A (membrana y pestillo por verificar)
3. Rascacielos que se encoge: [Japan Times 2013](https://www.japantimes.co.jp/news/2013/01/08/national/razing-skyscrapers-from-the-inside/) · [Popular Science](https://www.popsci.com/technology/article/2013-01/demolition-goes-eco-friendly-japan/) · [Web Japan (los dos métodos)](https://web-japan.org/trends/11_tech-life/tec130325.html)
4. Túnel flotante: [Femern (tramos ya hundidos)](https://femern.com/press/news/first-tunnel-element-of-the-fehmarnbelt-tunnel-to-be-immersed/) · [Trelleborg (junta Gina)](https://www.trelleborg.com/media/products-and-solutions-news/tailor-made-sealing-systems-for-the-fehmarnbelt-immersed-tunnel) · [Tunnels and Tunnelling](https://www.tunnelsandtunnelling.com/analysis/ensuring-the-seals-on-immersed-tunnels-281222-10500091/) (217 m, 73.000 t y 89 tramos por verificar)
5. Indiana Bell: [Logically Facts](https://logicallyfacts.com/en/fact-check/true-in-1930-the-indiana-bell-building-was-rotated-90-and-over-a-month-the-structure-was-moved-15-inch-hr-all-while-600-employees-still-worked-there) · [Indiana Historical Society](https://indianahistory.org/blog/instead-of-moving-mountains-they-moved-a-building/)
6. Cinturón: [Gobierno de Montana (PDF)](https://opifiles.mt.gov/) "2.1 How Seat Belts Work" · [Indiana Public Media](https://indianapublicmedia.org/amomentofscience/seatbelts/) · [Volvo](https://www.volvogroup.com/en/about-us/heritage/three-point-safety-belt.html) ("un millón de vidas" es cifra de Volvo: no usar sin fuente independiente)
7. Vidrio del celular: [Corning](https://www.corning.com/worldwide/en/innovation/the-glass-age/science-of-glass/how-it-works-strengthening-glass.html) · [C&EN](https://cen.acs.org/content/cen/articles/96/i3/Chemically-strengthened-glass-finds-new.html)
8. Espejo en horno que gira: [Giant Magellan Telescope](https://giantmagellan.org/2021/03/05/engineering-marvel-sixth-mirror-cast-for-giant-magellan-telescope) · [U. de Arizona](https://news.arizona.edu/news/sixth-mirror-casting-brings-giant-magellan-telescope-closer-completion)
9. Troll A: [Guinness](https://www.guinnessworldrecords.com/world-records/86725-tallest-object-manmade-moved) · [Equinor](https://equinor.industriminne.no/en/troll-a-giant-move-from-fjord-to-field/) (peso: 656.000 vs 683.000 t, no calzan)
10. Penitentes: Warren, *Annals of Glaciology* 2023 (Cambridge) · [APS Physics](https://link.aps.org/doi/10.1103/Physics.8.92)
11. Lata: [CanCentral](https://www.cancentral.com/canresources/how-cans-are-made/) · [Penn State](https://courses.ems.psu.edu/matse81/book/export/html/2216)
12. Tornillo: [CJ Winter](https://www.cjwinter.com/what-is-thread-rolling/) · [Virtual Labs (académico)](https://msvs2-dei.vlabs.ac.in/exp/thread-rolling/theory.html)

#### Ficha — El rascacielos que se encoge (verificada el 24-oct-2026; Tomás pidió sólo los datos, el video lo hace otro chat)
Extractos completos en la prerelease `caza06-fuentes` → `fuentes_caza06-rascacielos.md` (fuentes en `studio/caza/ronda06b-rascacielos.md`). Ojo: IOL, eHotelier y TheJournal son **el mismo cable de AFP** (cuentan como 1 fuente).

**El edificio:** Grand Prince Hotel Akasaka, Tokio: **~140 m y 40 pisos** (sitio oficial de Prince Hotels + AFP), construido en los años 80 (AFP). Al demolerlo era el edificio más alto derribado en Japón (Popular Science, 2013).
**Por qué no lo volaron:** en pleno Tokio, rodeado de vecinos: la explosión, los escombros y la nube de polvo eran inaceptables (Core77).

**La mecánica, paso a paso (método Tecorep de Taisei):**
1. Usan **el último piso como tapa**: lo refuerzan con vigas de acero y lo dejan como un "sombrero" que se puede bajar (AFP; Prince Hotels; Spoon & Tamago).
2. La tapa queda sobre **columnas provisorias con gatas hidráulicas** (Newswitch/Nikkan Kogyo; Spoon & Tamago; 99% Invisible). AFP: **15 gatas** (cifra de una sola fuente).
3. Cierran los pisos de arriba con **paneles contra el ruido**: queda una "fábrica de desarmar" cerrada arriba del edificio (Prince Hotels; 99% Invisible; Taisei en Spoon & Tamago: "es como poner un sombrero grande y el edificio se achica desde arriba").
4. Adentro, **una grúa colgada del techo** desarma el piso de abajo pieza por pieza; todo se separa y se recicla (99% Invisible; AFP).
5. Cuando el piso queda vacío, **las gatas bajan la tapa un piso** y se repite hacia abajo, "como rebobinar la construcción" (Prince Hotels: 新築工事を巻き戻すかのように; PopSci; NBC).
6. **Ritmo:** ~**2 pisos (6,4 m) cada 10 días** (AFP, que cita a Taisei; NBC lo repite). En la nota de AFP ya iba en **la mitad de su altura**. Desde afuera se ve igual, sólo cada vez más bajo: "el edificio se encoge y desaparece sin que lo notes" (Hideki Ichihara, Taisei, en AFP y NBC).

**El giro (4 fuentes):** los escombros bajan por **un pozo central** con un montacargas de **frenado regenerativo, como un auto eléctrico**: el peso que baja genera electricidad, **más de la que se necesita para volver a subir el gancho vacío**; el sobrante va a baterías que prenden **las luces y los ventiladores** de la obra (Core77; AFP; Popular Science; 99% Invisible). Popular Science: mientras más alto el edificio, más electricidad.

**Números del resultado:** **más de 90 % menos polvo** (AFP citando a Taisei; Inhabitat; Spoon & Tamago); ruido **más de 25 % menos** (Spoon & Tamago, una fuente); **85 % menos CO₂** (dato de la empresa, PopSci e Inhabitat: decirlo como "según la empresa" o no usarlo). Ganó el máximo premio de Japón a la tecnología de construcción (14.º Premio de Desarrollo Tecnológico de Infraestructura, Prince Hotels). Lo cubrieron 15 medios extranjeros (President).

**Variante "al revés" (Kajima, daruma otoshi):** cortan las columnas **del primer piso**, las cambian por **gatas controladas por computador**, desarman ese piso y **bajan el edificio entero**; se repite piso por piso desde abajo (Pink Tentacle; 99% Invisible; Aproplan). Lo usaron en sus propias oficinas: una torre de 75 m y 20 pisos y otra de 65 m y 17 (Pink Tentacle). Se llama así por el juguete japonés de bloques que se sacan a martillazos desde abajo sin botar la muñeca. 20 % más rápido (Pink Tentacle, cifra de la empresa).

**Extras (una fuente, por verificar si se usan):**
- En la misma obra, el edificio antiguo del hotel (patrimonio histórico, la ex residencia de la familia real coreana Yi en Tokio) se **trasladó 44 m** con técnica de "hikiya" para protegerlo y después se renovó como Akasaka Prince Classic House (President). Primo directo del Ep. 3.
- Nueva versión "Tecorep-light": en vez del techo del edificio arman un techo provisorio de acero más liviano, con la mitad de las gatas (Newswitch). También se usó en el ex Akasaka Twin Tower East (Newswitch).
- En su lugar hoy está el complejo Tokyo Garden Terrace Kioicho (President).
- Cálculo propio (no es dato de fuente): 140 m a 6,4 m cada 10 días ≈ 220 días, unos 7 meses.

**No decir:** fechas exactas de inicio/fin, el arquitecto ni "1982" (sólo Wikipedia); "15 gatas" como cifra segura; que "no hace nada de ruido" (es menos, no cero).
**Fuentes (las que respondieron):** [Prince Hotels, oficial (FIGURE 004)](https://www.princehotels.co.jp/kioicho/figure/detail/004.html) · [AFP en IOL](https://www.iol.co.za/travel/tokyo-hotels-vanishing-act-1478642) · [NBC News](https://www.nbcnews.com/news/amp/wbna50992992) · [Popular Science](https://www.popsci.com/technology/article/2013-01/demolition-goes-eco-friendly-japan/) · [Core77](https://www.core77.com/posts/55976/Japans-Silent-Dust-Free-Building-Demolition-System-Uses-the-Buildings-Weight-to-Generate-Electricity) · [99% Invisible](https://99percentinvisible.org/article/reverse-architecture-deconstruction-crews-erase-buildings-floor-floor/) · [Newswitch / Nikkan Kogyo](https://newswitch.jp/p/10143) · [President Online](https://president.jp/articles/-/20590) · [Spoon & Tamago](https://spoon-tamago.com/watch-a-skyscraper-slowly-vanish-as-it-gets-demolished-from-the-top-down/) · [Inhabitat](https://inhabitat.com/new-skyscraper-deconstruction-technique-harvests-energy-from-demolition-process/) · Kajima: [Pink Tentacle](https://pinktentacle.com/?p=666) · [Aproplan](https://www.aproplan.com/blog/skyscraper-demolition-techniques).

### Megaproyecto absurdo + "lo calculé"
| Estado | Gancho | Cálculo (supuestos explícitos en `guion.md`) | Imagen 3D clave | Acción buscada |
|---|---|---|---|---|
| pendiente | ¿Cuántos aviones harían falta para hacer girar el Aconcagua? | Momento de inercia del cerro vs empuje de un avión | El cerro con un cable y una nube de aviones | Enviar y comentar |
| pendiente | ¿Cuántos globos de helio harían falta para levantar un auto? | Empuje por globo vs peso del auto | Auto que se despega del suelo | Enviar |

### Historias (ficción)
| Estado | Premisa (cuadro 0) | Giro o remate | Set principal | Acción buscada |
|---|---|---|---|---|
| pendiente (borrador) | Un tipo pone 12 alarmas para despertarse | Aprende a apagarlas todas dormido | Pieza | Enviar |
| pendiente (borrador) | Un niño entrena 10 años para el récord de no pestañear | El día del récord estornuda | Pieza y estadio | Enviar |
| pendiente (borrador) | Un genio le concede a alguien no volver a elegir la fila lenta del súper | Ahora el súper entero tiene una sola fila | Supermercado | Enviar |

## 5. Ideas de la comunidad
| Fecha | @usuario | Pregunta | Red | Puntaje | Estado |
|---|---|---|---|---|---|
