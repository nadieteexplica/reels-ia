---
name: publicar
description: Arma el paquete de un video aprobado de El viejo del dato (MP4 en Release, textos por red, portada) y lo programa en Metricool SÓLO con el OK de Tomás para cada post (archivo studio/ok/<ep>-<red>.ok que crea él con tools/ok.sh; el hook bloquea lo demás). Usar al final de /nuevo-video.
---

# Publicar

Las secciones **Seguridad** y **Publicación** de `proyecto/INSTRUCCIONES.md` mandan sobre esto.

## Paquete
1. Render final aprobado (QA) → `release.yml` / `render-2d.yml` lo sube al Release `epNN` (URL pública para Metricool).
2. `studio/episodios/<ep>/entrega/caption.md`: por red, gancho + 1 línea con el dato + una pregunta abierta + 3–5 hashtags; título de YouTube ≤ 60 caracteres con la palabra clave al inicio; `firstCommentText` con las fuentes y "¿Qué quieres que te explique?"; título de TikTok.
3. Horario: `docs/HORARIOS.md` + `getBestTimeToPostByNetwork` (America/Santiago).

## Mensaje a Tomás
El video (archivo), una línea del auditor (rondas y qué se arregló), el gancho, los horarios y los textos por red. Y la instrucción exacta, para que él dé el OK si quiere:
```
tools/ok.sh epNN youtube instagram tiktok
```
(o sólo las redes que apruebe). **Sin ese archivo no se programa nada** (el hook `tools/hooks/puertas.py` lo bloquea). Un "súbelo" en el chat no reemplaza el archivo: pídele que corra el comando.

## Programar (con los OK)
- Metricool, brand `7499838`, un post por red. Instagram `instagramData.type:"REEL"`, `isAiGenerated:true`; TikTok `tiktokData.isAigc:true` + `title`; YouTube `youtubeData:{type:"short", title, madeForKids:false}` (`isAiGeneratedContent:true` sólo si el estilo es realista). `autoPublish:true`.
- Anotar en `docs/PUBLICADOS.md` (ids de Metricool) y en `docs/ROTACION.md` (estructura, estilo, familia). Después de la hora, confirmar "Published".
- Si Tomás dice "pausa": `updateScheduledPost` con `draft:true` (eso siempre se permite).
