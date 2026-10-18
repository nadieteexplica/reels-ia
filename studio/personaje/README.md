# Protagonista — pipeline del personaje

Personaje propio de **Nadie te explica**: hombre joven (~18–20 años), cuerpo de proporciones normales, polera coral con estrella amarilla (`#FFD23F`, el amarillo de los subtítulos), jeans y zapatillas blancas, pelo café en mechones.

Todo se genera con scripts (Blender como módulo de Python, `pip install bpy==5.2.0`). No hay `.blend` en el repo: el personaje se rearma en ~30 s.

## Licencias
- **Cuerpo base:** MakeHuman (malla y targets **CC0**, `github.com/makehumancommunity/makehuman`, carpeta `makehuman/data`). Se puede usar y redistribuir.
- **Animaciones:** Mixamo (FBX *Without Skin*). **No se suben a este repo público**: viven en el repo privado `nadieteexplica/assets` (o en los archivos del proyecto de Claude). El esqueleto propio usa los mismos nombres (`mixamorig:*`), así que las FBX se aplican directo, sin subir el personaje a Mixamo.

## Pasos
| Script | Qué hace | Sale |
|---|---|---|
| `build_body.py` | Cuerpo MakeHuman (hombre, 21 años de slider ≈ 18–20 de aspecto, 1,77 m, rasgos mezclados) + ajustes de cara | `out/body.blend`, `joints.json`, `expr_units.npz` |
| `rig.py` | Esqueleto `mixamorig:*` en las articulaciones, pesos automáticos, cabeza rígida, cuello suavizado, 34 shape keys de expresión (FACS de MakeHuman), pose T alineada a Mixamo | `out/rigged.blend` |
| `dress.py` | Polera, jeans y zapatillas generadas desde el cuerpo (heredan los pesos), piel pintada en UV (cejas, labios, base del pelo), ojos | `out/dressed.blend` |
| `hair.py` | Pelo con curvas (26 mil hebras agrupadas en mechones), pegado al hueso de la cabeza | `out/personaje.blend` |
| `anim.py` | Carga una FBX de Mixamo, escala la cadera y suaviza un 30 % cabeza y cuello | — |
| `look.py` / `clip.py` | Hojas de revisión y clips de prueba | `out/*.png` |

```bash
export MH_DATA=/ruta/a/makehuman/data MIXAMO_DIR=/ruta/a/fbx
python3 build_body.py && python3 rig.py && python3 dress.py && python3 hair.py
FBX=Thinking FRAME=70 python3 look.py
```

## Expresiones (shape keys en `Cuerpo`)
`eye-left/right-closure` (parpadeo), `eye-*-opened-up` (sorpresa), `eyebrows-*-up / -down / -inner-up`, `mouth-open`, `mouth-corner-puller` (sonrisa), `mouth-depression-retraction` (mueca de dolor), `mouth-pursing`, `nose-*-elevation`, entre otras. Se animan por clave igual que en `clip.py`.

## Pendiente
- Piel menos plástica (poros/variación más fina) y bordes de manga.
- Mirada (huesos de ojos) y sincronía de boca con la voz.
- Contacto mano–cara (las proporciones difieren de Y Bot: `Thinking` no llega al mentón): corrección con IK por plano.
