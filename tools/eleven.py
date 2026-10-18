"""Corre los trabajos de voz de ElevenLabs que están en jobs/voz/*.json.

Modos:
  voices -> busca voces en la Voice Library y descarga sus previews (out/voces/)
  tts    -> genera la locución con timestamps por carácter (out/tts/<id>.mp3 + .json)

La clave se lee de la variable de entorno ELEVENLABS_API_KEY (secreto de GitHub Actions).
"""
import base64, json, os, sys, pathlib, urllib.request, urllib.parse, urllib.error

API = "https://api.elevenlabs.io/v1"
KEY = os.environ.get("ELEVENLABS_API_KEY", "").strip()
ROOT = pathlib.Path(__file__).resolve().parents[1]
STATUS = ROOT / "out" / "status.json"


def req(method, path, params=None, body=None):
    url = API + path + ("?" + urllib.parse.urlencode(params, doseq=True) if params else "")
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method,
                               headers={"xi-api-key": KEY, "Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(r, timeout=120) as resp:
        return json.loads(resp.read().decode())


def write_status(obj):
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    old = json.loads(STATUS.read_text()) if STATUS.exists() else {}
    old.update(obj)
    STATUS.write_text(json.dumps(old, ensure_ascii=False, indent=1))


def job_voices(job):
    out = ROOT / "out" / "voces"; out.mkdir(parents=True, exist_ok=True)
    seen, found = set(), []
    for q in job["queries"]:
        try:
            res = req("GET", "/shared-voices", {"page_size": 30, **q})
        except urllib.error.HTTPError as e:
            found.append({"query": q, "error": f"{e.code} {e.read().decode()[:300]}"}); continue
        for v in res.get("voices", []):
            if v.get("voice_id") in seen: continue
            seen.add(v.get("voice_id"))
            found.append({k: v.get(k) for k in ("voice_id", "public_owner_id", "name", "accent", "gender", "age", "language", "locale",
                                                "use_case", "descriptive", "category", "description", "preview_url",
                                                "usage_character_count_1y", "cloned_by_count")})
    found = [f for f in found if "voice_id" in f]
    found.sort(key=lambda v: -(v.get("usage_character_count_1y") or 0))
    top = found[: job.get("top", 8)]
    for i, v in enumerate(top, 1):
        if v.get("preview_url"):
            try:
                urllib.request.urlretrieve(v["preview_url"], out / f"{i:02d}_{(v['name'] or 'voz').replace(' ', '_')[:30]}.mp3")
            except Exception as e:  # noqa
                v["preview_error"] = str(e)
    (out / "voces.json").write_text(json.dumps({"top": top, "total_encontradas": len(found)}, ensure_ascii=False, indent=1))
    return {"voces_encontradas": len(found), "previews": len(top)}


def job_tts(job):
    out = ROOT / "out" / "tts"; out.mkdir(parents=True, exist_ok=True)
    res = req("POST", f"/text-to-speech/{job['voice_id']}/with-timestamps",
              {"output_format": job.get("output_format", "mp3_44100_128")},
              {"text": job["text"], "model_id": job.get("model_id", "eleven_multilingual_v2"),
               "voice_settings": job.get("voice_settings", {"stability": 0.45, "similarity_boost": 0.8, "style": 0.25, "use_speaker_boost": True})})
    (out / f"{job['id']}.mp3").write_bytes(base64.b64decode(res["audio_base64"]))
    (out / f"{job['id']}.json").write_text(json.dumps({"alignment": res.get("alignment"), "normalized_alignment": res.get("normalized_alignment")}, ensure_ascii=False))
    return {"tts": job["id"]}


def main(files):
    if not KEY:
        write_status({"elevenlabs": "FALTA EL SECRETO ELEVENLABS_API_KEY"}); print("sin clave"); return
    try:
        me = req("GET", "/user/subscription")
        write_status({"elevenlabs": "OK", "plan": me.get("tier"), "creditos_usados": me.get("character_count"), "creditos_limite": me.get("character_limit")})
    except urllib.error.HTTPError as e:
        write_status({"elevenlabs": f"clave rechazada o sin permiso de User: {e.code}"})
    for f in files:
        job = json.loads(pathlib.Path(f).read_text())
        try:
            r = job_voices(job) if job["mode"] == "voices" else job_tts(job)
            write_status({pathlib.Path(f).name: r})
        except urllib.error.HTTPError as e:
            write_status({pathlib.Path(f).name: f"error {e.code}: {e.read().decode()[:400]}"})
        except Exception as e:  # noqa
            write_status({pathlib.Path(f).name: f"error: {e}"})


if __name__ == "__main__":
    main(sys.argv[1:])
