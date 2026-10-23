# Biblioteca de assets — estilo realista

Pedido de Tomás (23-oct-2026, 18:24): "limar la edición realista" con una base de herramientas tipo Mixamo para poder editar cualquier tipo de video. Investigado el mismo día (extractos en la prerelease `assets-fuentes`, lista de páginas en `studio/caza/assets-realista.md`).

**Regla:** no se baja "todo" a ciegas. Se baja todo lo que sirve para el realista del Ep. 5 (`docs/ESTILO_REALISTA.md`), y nada entra al kit sin pasar por una hoja de contacto en Blender con la luz del Ep. 5 (sol bajo, materiales sucios). Los estilos rechazados (low-poly, monitos, fantasía) quedan fuera aunque sean gratis.

## 1. Lo que baja Claude solo (gratis, sin cuenta, con GitHub Actions)
| Fuente | Qué trae | Licencia (verificada 23-oct) | Cómo se usa |
|---|---|---|---|
| Poly Haven | Modelos, texturas y cielos HDRI | CC0. Su API ahora es libre para todos, incluso uso comercial; piden que quede claro que los assets son de Poly Haven | Catálogo en el repo; el render baja cada asset por nombre (no se guarda) |
| ambientCG | Materiales PBR | CC0 | Igual que Poly Haven |
| Smithsonian Open Access | Más de 2.000 escaneos 3D de objetos reales (OBJ/glTF) | CC0, sin atribución | Catálogo + descarga por nombre |
| Sketchfab / Objaverse | Escaneos de animales, objetos y vehículos, algunos ya animados (la rana del Ep. 5) | CC-BY (crédito en descripción y primer comentario) o CC0 | Catálogo filtrado por licencia y animación (`buscar-objaverse.yml`) |
| Quaternius Universal Animation Library 1 y 2 | La versión gratis trae **89 animaciones** (46 + 43; las completas de 120+ y 130+ son del Patreon) para un esqueleto universal | CC0 | Relleno de movimientos; calidad de juego, no de cine. Sirven: arreglar algo arrodillado, levantar de una mesa, empujar, manejar, hablar por teléfono, regar, cortar un árbol, caminar cargando, abrir un cofre, trepar 1 m, levantarse del suelo |
| Sonniss GDC Game Audio Bundle | Efectos de sonido de estudio (7,47 GB sólo el de 2026; los de años anteriores siguen disponibles) | Sin regalías, uso comercial, sin atribución; no se redistribuye suelto | Al repo privado `nadieteexplica/assets`; reemplaza los efectos sintetizados |

### Estado (23-oct-2026)
- **Listo:** catálogos en `studio/biblioteca/` (Poly Haven: 2.387 assets = 521 modelos, 997 cielos, 869 texturas; ambientCG: 2.926, de ellos 2.036 materiales y 434 cielos) y los 2 packs de Quaternius en la prerelease `biblioteca`. Buscar: `python3 tools/biblioteca.py buscar "concrete,rust" texture`; bajar en el render: `python3 tools/biblioteca.py bajar polyhaven <id> 2k`.
- **Pendiente:** Smithsonian (la API no respondió con la consulta de prueba; se depura con `extra=sonda`) y Sonniss (no se puede redistribuir: va al repo privado `nadieteexplica/assets`, y esta sesión no tiene acceso a ese repo: Tomás tiene que darle acceso a Claude en GitHub).

## 2. Lo que baja Tomás (piden cuenta)
### Mixamo (licencia: gratis, uso comercial sí; lo único prohibido es redistribuir los archivos sueltos o entrenar IA)
- **Personajes: todos los de la grilla sirven** (Tomás, 23-oct 19:05: "el algoritmo no tiene reglas, así que no pongas reglas"). Caricaturas, monstruos, zombies, armaduras, robots, soldados o uniformados, todo vale para videos más locos. Se bajan en **With Skin**, FBX Binary, T-pose. Lo único que se mantiene es la regla de las instrucciones del proyecto: lo que se presenta como real es real, y la ficción no se disfraza de dato.
- **Prioridad para el realista (23-oct, 18:55):** Remy y Lewis (hombres jóvenes), Megan y Sophie (mujeres jóvenes), Brian (hombre adulto), Martha (mujer adulta), Joe y Louise (oficina), Chad (doctor o laboratorio) y Pete (ya está). Para lo loco: Mannequin y Dummy (maniquí de prueba), Racer, Astra, Gas Mask y Castle Guard 01. En Mixamo no hay viejos ni niños realistas (The Boss, Abe, Sporty Granny, Timmy, Ty y Aj son caricatura). Cada uno pasa una ficha con la luz del episodio antes de usarlo.
- **Tomás encontró que los movimientos son demasiados (18:52):** ahora se baja sólo una base de ~25 y el resto a pedido, 3–5 por video según el guion.
- **Movimientos: sí, esta lista** (Without Skin, FBX Binary, 30 fps, keyframe reduction none, "In Place" marcado cuando exista). Se busca la palabra en Mixamo y se baja la versión que se vea más natural; si una no existe, se salta. ★ = primero. Ya están: Drinking, Focus, Thinking, Shrugging, Arm Gesture, Pointing, Talking, Surprised, Head Nod Yes, Relieved Sigh, Shaking Head No, Laughing, Happy Idle, Terrified, Excited.
  - **Vida (estar quieto sin estar tieso):** ★ Breathing Idle · ★ Standing Idle · ★ Looking Around · Bored · Weight Shift · Sad Idle · Nervously Look Around
  - **Moverse:** ★ Walking · ★ Start Walking · ★ Stop Walking · Walking Backwards · ★ Left Turn · ★ Right Turn · Jogging · ★ Running · Stop Running · Crouch Walk · Ascending Stairs · Descending Stairs · ★ Climbing Ladder
  - **Manos y objetos:** ★ Picking Up · ★ Lifting · ★ Carrying · ★ Pushing · ★ Pulling · Throwing · Catching · ★ Typing · ★ Texting · Talking On Phone · ★ Pressing Button · Opening · Knocking · Wiping · Hammering · Digging · Shoveling
  - **Agacharse y sentarse:** ★ Kneeling · Kneel To Stand · ★ Crouching · Looking Down · ★ Sitting Idle · ★ Stand To Sit · ★ Sit To Stand · Sitting Talking · Sitting Typing · Driving
  - **Reacciones de cuerpo (Mixamo no anima la cara):** ★ Clapping · ★ Cheering · ★ Waving · ★ Shocked · Disappointed · Angry · Defeated · Thumbs Up · Facepalm · Shivering · Wiping Sweat · Covering Ears · Yawn · Sneezing
  - **Física (caer, flotar, perder el equilibrio):** ★ Floating · ★ Falling Idle · ★ Falling · Hard Landing · ★ Jumping · Stumble · Slipping · ★ Getting Up · Hanging Idle · Treading Water · Swimming
  - **Esfuerzo:** Stretching · Push Up · Jumping Jacks · Out Of Breath
- Van al Release privado `Personajes` de `nadieteexplica/assets` (como Pete), **personajes y movimientos juntos** (Tomás, 23-oct 19:15). Nunca al repo público. En `assets.txt`, `privados <patrón>` baja cualquiera de los dos y `pose <patrón>` busca primero en la carpeta `mixamo/` del repo privado y después en ese Release.
- **Script para bajar todo Mixamo de una** (`gnuton/mixamo_anims_downloader`): existe y corre en el Chrome de Tomás con su sesión de Adobe. Es uso automatizado de su cuenta; los autores no se hacen responsables. Recomendación: no usarlo, lista a mano.

### Inventario del Release `Personajes` (revisado con `revisar-privados.yml`, 23-oct 19:20: 41 archivos, todos completos)
- **Personajes (20):** Astra, Brian, Castle Guard (pesa 5 MB contra 30–140 MB del resto: puede venir sin texturas; se ve en la ficha), Chad, David, Dummy, Gas Mask, Joe, Lewis, Louise, Mannequin, Marta, Megan, Ortiz, Pete, Racer, Remy, Sophie, Steve, Suzie.
- **Movimientos (20 + 1 pack):** Box Turn, Capoeira (+ Capoeira Pack.zip), Dancing Running Man, Defeated, Drunk Run Forward, Dying, Female Crouch Pose, Goalkeeper Body Block, Great Sword Walk, Jumping Down (3 variantes), Male Action Pose, Old Man Idle, Reaction (2 copias iguales), Right Block, Shoved Reaction With Spin, Sitting Laughing, Taunt. Más los 14 del Ep. 1 en la carpeta `mixamo/` del repo privado.
- **Falta la base de uso diario** (caminar, quieto respirando, tomar, empujar, sentarse, caer, flotar…): se pide a Tomás cuando un guion la necesite.

### Otros
- **Renderpeople (gratis):** 4 personas escaneadas de verdad, con esqueleto, uso comercial, con versión Blender (dato de 2017: confirmar que siguen gratis).
- **Fab (Epic):** cada cierto tiempo regala packs por tiempo limitado que quedan en la cuenta para siempre. La licencia estándar de Fab permite usarlos en cualquier herramienta (Blender incluido) y en proyectos comerciales, sin dar crédito. Megascans ya no es gratis desde 2025.
- **Rokoko Video:** de video a animación (se graba con el iPhone a alguien haciendo la acción exacta del guion y sale el movimiento para Blender). Para lo que Mixamo no tiene. Confirmar el plan gratis y su licencia antes de usarlo.

## 3. Para después: MetaHuman (personas con cara animable)
- Lo mejor gratis en personas realistas, y resuelve las caras (Mixamo no anima la cara).
- **Licencia, fuentes que chocan:** CG Channel (jun-2025 y jul-2026) dice que Epic cambió la licencia para usarlos en cualquier motor o programa, también comercial, y que el add-on Character DNA para Blender (4.5+) es gratis desde jul-2026. Un blog de StraySpark (2026) dice lo contrario. **Antes de instalar nada se lee el contrato de MetaHuman.**
- Costo para Tomás: instalar Unreal Engine 5.6+ en su computador y crear los personajes ahí (la app web cierra el 5-nov-2026). Hay que probar que se rendericen bien en Blender y en Actions (pelo y peso).
- Se prueba con **un cuadro** antes de adoptarlo (lección 75: un look nuevo se confirma con un cuadro de prueba propio).

## 4. Descartado
- ActorCore (Reallusion): sólo ~32 movimientos y 4 personajes gratis, de poca resolución.
- Human Base Meshes de Blender Studio (CC0): son bases para esculpir, no personajes listos.
- Kenney, Quaternius (modelos) y packs low-poly: estilo rechazado.
- CMU (base de captura de movimiento): miles de clips en bruto que hay que limpiar a mano; sólo si falta algo muy puntual.

## Fuentes
- https://community.adobe.com/t5/mixamo-discussions/mixamo-faq-licensing-royalties-ownership-eula-and-tos/m-p/13234775
- https://github.com/gnuton/mixamo_anims_downloader
- https://www.cgchannel.com/2025/06/you-can-now-sell-metahumans-or-use-them-in-unity-or-godot/
- https://www.cgchannel.com/2026/07/the-character-dna-metahuman-add-on-for-blender-is-now-free/
- https://www.strayspark.studio/blog/metahuman-2026-web-app-shutdown-migration-guide
- https://quaternius.com/packs/universalanimationlibrary.html
- https://digitalproduction.com/2026/02/10/130-animations-one-rig-zero-drama/
- https://www.rokoko.com/insights/rokoko-video-launch
- https://www.cgchannel.com/2017/11/download-four-free-renderpeople-rigged-3d-characters
- https://www.fab.com/eula
- https://80.lv/articles/megascans-no-longer-free-after-2024
- https://www.cgchannel.com/2026/04/get-650-free-3d-assets-for-building-dungeons-in-blender-unity-and-unreal-engine/
- https://www.cgchannel.com/2020/03/get-2000-free-3d-models-from-the-smithsonian-collection/
- https://polyhaven.com/our-api
- https://docs.ambientcg.com/license/
- https://rekkerd.org/sonniss-releases-gdc-2026-game-audio-bundle/
- https://www.cgchannel.com/?p=121885
- https://www.cgchannel.com/2023/06/download-blender-studios-free-human-base-meshes
