# Ideas — método, puntaje y banco

## 1. Dónde buscar (cada semana, en este orden)
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
5. **Objetos cotidianos:** mira alrededor (cocina, baño, celular, calle, metro) y pregúntate "¿cómo funciona esto por dentro?".

## 2. Puntaje (de 0 a 5 en cada criterio)
| Criterio | Pregunta | Peso |
|---|---|---|
| Curiosidad | ¿La gente se lo pregunta o lo busca? | ×1,5 |
| Universalidad | ¿Le pasa o le importa a cualquiera, en cualquier país? | ×1,2 |
| Sorpresa | ¿El dato contradice lo que uno cree? | ×1,5 |
| Visual 3D | ¿Se puede mostrar con imágenes, sin explicar con texto? | ×1,3 |
| Enseñanza | ¿Deja algo útil o algo que contarle a otro? | ×1,0 |
| Verificable | ¿Hay 2 fuentes sólidas? (si es 0, se descarta) | ×1,0 |
| Compartible | ¿Dan ganas de mandárselo a alguien? | ×1,5 |

- **Puntaje máximo:** 45. **Para producir hacen falta 32 o más.** Una idea con Verificable = 0 se descarta aunque sume.
- **Ajuste mensual:** los pesos se ajustan con los datos de `PUBLICADOS.md`. Por ejemplo, si los temas del cuerpo rinden el doble en envíos, sube su prioridad.
- **Variedad:** nunca 2 videos seguidos con el mismo gancho o la misma área (cuerpo, tecnología, planeta…).

## 3. Lista negra
- Retos o experimentos que alguien pueda imitar y salir herido.
- Tragedias recientes, política y religión.
- Salud que suene a indicación médica.
- Personajes, marcas o franquicias con derechos de autor como protagonistas.
- Temas ya publicados: se revisa `PUBLICADOS.md` antes de elegir.
- El pulpo, que a Tomás no le gustó como tema.

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
| pendiente | ¿Por qué Chile tiembla tanto? | La placa de Nazca se mete bajo Sudamérica varios cm por año | Placas chocando bajo Chile | Qué hacer en un temblor |
| pendiente | ¿Por qué el desierto de Atacama es el más seco del mundo? | Corriente de Humboldt + cordillera + alta presión | Nubes que no pasan | Por qué hay observatorios ahí |
| pendiente | ¿Por qué el cielo es azul y el atardecer naranjo? | La luz azul se dispersa más (dispersión de Rayleigh) | Rayos de luz rebotando | Por qué en Marte es al revés |
| pendiente | ¿Por qué el hielo flota? | El agua se expande al congelarse, y eso salva a los peces en invierno | Moléculas formando una red | Por qué revientan las botellas en el congelador |
| pendiente | Un rayo es más caliente que el Sol | Unos 30.000 °C contra ~5.500 °C de la superficie del Sol | Rayo en cámara lenta | Por qué suena el trueno |
| pendiente | Los plátanos son radiactivos | Tienen potasio-40, pero la dosis es mínima | Plátano con átomos brillando | Qué es la radiación de verdad |
| pendiente | Hay más árboles en la Tierra que estrellas en la Vía Láctea | ~3 billones de árboles (estudio de 2015) | Bosque vs galaxia | Escala |

## 5. Ideas de la comunidad
| Fecha | @usuario | Pregunta | Red | Puntaje | Estado |
|---|---|---|---|---|---|
