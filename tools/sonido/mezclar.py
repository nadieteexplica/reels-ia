"""Mezcla voz + efectos (SFX) + música según un sfx-plan.json y revisa que cada efecto importante se escuche.

Uso:
    .venv/bin/python tools/sonido/mezclar.py <sfx-plan.json> [--words words.json] [--salida mix.wav]
                     [--musica cama.wav | --sin-musica] [--guardar-ref] [--registrar ep16]

Formato del plan (adaptado del sfx-plan de hassancs91/claude-faceless-shorts-creator, licencia MIT):
    {
      "voz": "out/tts/ep16.mp3",            # cualquier formato que lea ffmpeg
      "musica": "cama.wav" | null,
      "catalogo": "tools/sonido/biblioteca/catalog.json",
      "salida": "mix.wav",
      "words": "studio/episodios/ep16/words_voz.json",   # opcional; --words manda
      "duracion_s": 45.0,                   # null = lo que dura la voz
      "ducking": true,
      "musica_gain_db": 0,                  # opcional: ganancia inicial de la música (normalizada a −20 LUFS)
      "eventos": [
        {"en_s": 4.9, "sfx": "thud-metal", "gain_db": -8, "cue": "el martillo golpea",
         "palabra": "golpe", "despues_de_s": 4.0, "desfase_s": -0.1, "alinear": "inicio", "opcional": false}
      ]
    }
Campos de cada evento:
    en_s          segundo del evento (si hay "palabra" y words, se reemplaza por el inicio de esa palabra).
    palabra       una o varias palabras seguidas ("el ruido"); se compara sin mayúsculas, tildes ni signos.
    despues_de_s  toma la primera aparición de la palabra que empieza en o después de este segundo.
    desfase_s     se suma al tiempo resuelto (ej. −0,12 para que el golpe caiga justo antes de la palabra).
    alinear       "inicio" (por defecto: el clip parte en en_s) o "fin" (el clip TERMINA en en_s: risers y
                  whoosh-reverso, para que el clímax caiga en el golpe).
    gain_db       relativo al clip, que viene a −20 LUFS.
    opcional      true = decorativo: no se exige que se escuche.

Cadena:
    1. voz a −16 LUFS (así el umbral del ducking se comporta igual en todos los episodios).
    2. bus de SFX (cada clip con su gain_db) y música (−20 LUFS + musica_gain_db, en loop).
    3. ducking: la curva de ganancia sale de ffmpeg `sidechaincompress=threshold=0.15:ratio=2:attack=5:
       release=200:makeup=2` con la voz de sidechain (se le pasa una señal constante y se lee la ganancia), y se
       aplica igual a la música y a los SFX. Como la ganancia depende sólo de la voz, es lo mismo que comprimir cada bus.
    4. regla del Ep. 16: la música queda ≥ 19 dB bajo la voz mientras habla (si no, se baja sola y se avisa).
    5. ganancia para −14 LUFS integrados y `alimiter` de ffmpeg (techo −1,5 dBFS); se mide con ffmpeg ebur128.
    6. revisión de audibilidad: en la ventana de 0,3 s desde cada evento (la que termina en en_s si alinear=fin),
       la mezcla tiene que quedar ≥ +4 dB RMS sobre la misma mezcla sin efectos (voz + música). Si un evento no
       opcional no se escucha → sale con código 1. También avisa eventos a menos de 0,25 s entre sí y golpes que
       tapan una palabra.
Deja al lado de la salida <salida>.reporte.json (lo usa ver.py para dibujar).
"""
import argparse
import os
import subprocess
import sys
import tempfile
import unicodedata

import numpy as np
from scipy.io import wavfile

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, AQUI)
import medir  # noqa: E402

SR = medir.SR
VOZ_LUFS = -16.0
OBJETIVO_LUFS = -14.0
LIMITE = 10 ** (-1.5 / 20)
MUSICA_BAJO_VOZ_DB = 19.0
DUCK = "sidechaincompress=threshold=0.15:ratio=2:attack=5:release=200:makeup=2"


def resolver(ruta, base_plan):
    if ruta is None or os.path.isabs(ruta):
        return ruta
    for base in (base_plan, os.getcwd(), RAIZ):
        p = os.path.join(base, ruta)
        if os.path.exists(p):
            return os.path.abspath(p)
    return os.path.abspath(os.path.join(RAIZ, ruta))


def normal(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return "".join(c for c in s if c.isalnum())


def buscar_palabra(words, frase, despues_de=0.0):
    obj = [normal(p) for p in frase.split() if normal(p)]
    claves = [normal(w["w"]) for w in words]
    for i in range(len(words) - len(obj) + 1):
        if words[i]["s"] + 1e-6 >= despues_de and claves[i:i + len(obj)] == obj:
            return words[i]
    return None


def curva_ducking(voz, dur_n):
    """Ganancia (n,) que aplica sidechaincompress con la voz de sidechain (incluye el makeup)."""
    with tempfile.TemporaryDirectory() as tmp:
        pv = os.path.join(tmp, "voz.wav")
        wavfile.write(pv, SR, voz.astype(np.float32))
        cmd = ["ffmpeg", "-v", "error", "-f", "lavfi", "-i", f"aevalsrc=0.5:s={SR}:d={dur_n / SR:.6f}", "-i", pv,
               "-filter_complex", f"[0][1]{DUCK}", "-ac", "1", "-f", "f32le", "-"]
        out = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)
    g = np.ones(dur_n) * 2.0
    g[:min(dur_n, len(out))] = out[:dur_n] / 0.5
    return g.astype(np.float64)


def limitar_ffmpeg(x, ruta_salida=None):
    """alimiter de ffmpeg (techo −1,5 dBFS, sin auto-nivel). Devuelve la señal limitada (n, 2)."""
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "pre.wav")
        wavfile.write(p, SR, x.astype(np.float32))
        # limitador a 192 kHz (4×) para atajar también los picos entre muestras; latency=1 compensa el retardo
        af = f"aresample=192000,alimiter=limit={LIMITE:.4f}:attack=5:release=50:level=false:latency=1,aresample={SR}"
        out = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-af", af, "-f", "f32le", "-"],
                                           capture_output=True, check=True).stdout, np.float32)
    y = out.astype(np.float64).reshape(-1, 2)
    if len(y) < len(x):
        y = np.concatenate([y, np.zeros((len(x) - len(y), 2))])
    return y[:len(x)]


def escribir_pcm16(ruta, x):
    rng = np.random.default_rng(7)
    d = (rng.random(x.shape) - rng.random(x.shape)) / 32768.0
    wavfile.write(ruta, SR, np.clip(np.round((x + d) * 32767), -32768, 32767).astype(np.int16))


def mascara_habla(voz, ventana=0.05):
    """Ventanas de 50 ms donde la voz está a menos de 25 dB de su nivel integrado."""
    w = int(ventana * SR)
    n = len(voz) // w
    r = np.sqrt(np.mean(voz[:n * w].reshape(n, w) ** 2, axis=1) + 1e-12)
    ref = 10 ** ((medir.lufs(voz) - 25) / 20)
    return np.repeat(r > ref, w), w


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("--words")
    ap.add_argument("--salida")
    ap.add_argument("--musica")
    ap.add_argument("--sin-musica", action="store_true")
    ap.add_argument("--ventana", type=float, default=0.3)
    ap.add_argument("--umbral", type=float, default=4.0, help="dB mínimos sobre voz+música (por defecto 4)")
    ap.add_argument("--guardar-ref", action="store_true", help="guarda también <salida>.ref.wav (sin efectos)")
    ap.add_argument("--registrar", help="agrega este episodio a usado_en de los clips usados en el catálogo")
    a = ap.parse_args()

    ruta_plan = os.path.abspath(a.plan)
    base = os.path.dirname(ruta_plan)
    plan = medir.leer_json(ruta_plan)
    voz_p = resolver(plan["voz"], base)
    mus_p = None if a.sin_musica else resolver(a.musica or plan.get("musica"), base)
    cat_p = resolver(plan.get("catalogo", "tools/sonido/biblioteca/catalog.json"), base)
    salida = os.path.abspath(a.salida) if a.salida else resolver(plan["salida"], base)
    words_p = os.path.abspath(a.words) if a.words else resolver(plan.get("words"), base)
    os.makedirs(os.path.dirname(salida), exist_ok=True)

    cat = medir.leer_json(cat_p)
    clips = {c["id"]: c for c in cat["clips"]}
    words = medir.leer_json(words_p) if words_p else []

    voz = medir.leer_audio(voz_p, 1)
    dur = plan.get("duracion_s") or len(voz) / SR
    n = int(round(dur * SR))
    recortada = len(voz) > n + int(0.05 * SR)
    voz = np.concatenate([voz, np.zeros(max(0, n - len(voz)))])[:n]
    voz *= 10 ** ((VOZ_LUFS - medir.lufs(voz)) / 20)

    # ---------------------------------------------------------------- eventos
    eventos, errores = [], []
    for k, ev in enumerate(plan.get("eventos", []), 1):
        e = dict(ev, n=k)
        if ev["sfx"] not in clips:
            errores.append(f"evento {k}: el sfx '{ev['sfx']}' no está en el catálogo")
            continue
        t = ev.get("en_s")
        if ev.get("palabra"):
            if words:
                w = buscar_palabra(words, ev["palabra"], ev.get("despues_de_s", 0.0))
                if w is None:
                    msg = f"evento {k}: no encontré la palabra '{ev['palabra']}' después de {ev.get('despues_de_s', 0)} s"
                    (print("aviso:", msg, "(opcional, se omite)") if ev.get("opcional") else errores.append(msg))
                    continue
                t = w["s"]
                e["palabra_s"] = w["s"]
            elif t is None:
                errores.append(f"evento {k}: tiene 'palabra' pero no hay words.json ni en_s")
                continue
        t = float(t) + float(ev.get("desfase_s", 0.0))
        e["t"] = round(t, 3)
        clip = medir.leer_audio(os.path.join(os.path.dirname(cat_p), clips[ev["sfx"]]["archivo"]), 2)
        e["clip"] = clip * 10 ** (ev.get("gain_db", 0.0) / 20)
        e["ini"] = t - len(clip) / SR if ev.get("alinear") == "fin" else t
        e["win"] = (t - a.ventana, t) if ev.get("alinear") == "fin" else (t, t + a.ventana)
        eventos.append(e)
    if errores:
        print("\n".join("ERROR: " + x for x in errores))
        sys.exit(2)

    def bus_de(evs):
        b = np.zeros((n, 2))
        for e in evs:
            i = int(round(e["ini"] * SR))
            c = e["clip"]
            if i < 0:
                c, i = c[-i:], 0
            j = min(n, i + len(c))
            if j > i:
                b[i:j] += c[:j - i]
        return b

    sfx = bus_de(eventos)

    # ---------------------------------------------------------------- música
    musica = np.zeros((n, 2))
    if mus_p:
        m = medir.leer_audio(mus_p, 2)
        m = np.tile(m, (int(np.ceil(n / len(m))), 1))[:n]
        musica = m * 10 ** ((-20 - medir.lufs(m) + plan.get("musica_gain_db", 0.0)) / 20)

    g = curva_ducking(voz, n) if plan.get("ducking", True) else np.ones(n)
    voz_st = np.repeat(voz[:, None], 2, axis=1)
    habla, _ = mascara_habla(voz)

    musica_bajo = None
    if mus_p:
        def bajo_voz(mu):
            pv = np.mean(voz[habla] ** 2)
            pm = np.mean(np.mean((mu * g[:, None])[habla] ** 2, axis=1))
            return 10 * np.log10(pv / (pm + 1e-20))
        musica_bajo = bajo_voz(musica)
        if musica_bajo < MUSICA_BAJO_VOZ_DB:
            baja = MUSICA_BAJO_VOZ_DB + 0.5 - musica_bajo
            print(f"aviso: la música quedaba {musica_bajo:.1f} dB bajo la voz; la bajo {baja:.1f} dB (regla ≥ 19 dB)")
            musica *= 10 ** (-baja / 20)
            musica_bajo = bajo_voz(musica)

    mix = voz_st + g[:, None] * (musica + sfx)
    ref = voz_st + g[:, None] * musica
    if recortada:
        f = int(0.3 * SR)
        rampa = np.linspace(1, 0, f)[:, None]
        mix[-f:] *= rampa
        ref[-f:] *= rampa

    # ---------------------------------------------------------------- loudness y limitador
    gan = 10 ** ((OBJETIVO_LUFS - medir.lufs(mix)) / 20)
    for _ in range(3):
        final = limitar_ffmpeg(mix * gan)
        escribir_pcm16(salida, final)
        i_lufs, tp = medir.ebur128_ffmpeg(salida)
        if abs(i_lufs - OBJETIVO_LUFS) <= 0.3:
            break
        gan *= 10 ** ((OBJETIVO_LUFS - i_lufs) / 20)
    ref_final = limitar_ffmpeg(ref * gan)
    if a.guardar_ref:
        escribir_pcm16(salida[:-4] + ".ref.wav", ref_final)

    # ---------------------------------------------------------------- audibilidad
    fallas = 0
    filas = []
    orden = sorted(eventos, key=lambda e: e["t"])
    for e in orden:
        i0, i1 = (max(0, int(round(x * SR))) for x in e["win"])
        i1 = min(n, max(i1, i0 + 1))
        d = medir.rms_db(final[i0:i1]) - medir.rms_db(ref_final[i0:i1])
        avisos = []
        for o in orden:
            if o is e or abs(o["t"] - e["t"]) >= 0.25:
                continue
            if abs(o["t"] - e["t"]) < 0.05 and "fin" in (o.get("alinear"), e.get("alinear")):
                avisos.append(f"capa con #{o['n']}")          # riser/whoosh-reverso que remata en un golpe: buscado
            else:
                avisos.append(f"a {abs(o['t'] - e['t']):.2f} s del #{o['n']}")
        # ¿tapa una palabra? golpe que cae dentro de una palabra y suena más fuerte que la voz en esos 0,15 s
        j0, j1 = int(e["t"] * SR), min(n, int((e["t"] + 0.15) * SR))
        for w in words:
            if w["s"] - 0.02 <= e["t"] <= w["e"] - 0.05 and j1 > j0:
                solo = bus_de([e])[j0:j1] * g[j0:j1, None]
                if medir.rms_db(solo) > medir.rms_db(voz_st[j0:j1]):
                    avisos.append(f"tapa '{w['w']}'")
                break
        ok = d >= a.umbral
        estado = "ok" if ok else ("opcional" if e.get("opcional") else "NO SE OYE")
        if not ok and not e.get("opcional"):
            fallas += 1
        filas.append(dict(n=e["n"], t=e["t"], sfx=e["sfx"], palabra=e.get("palabra"), gain_db=e.get("gain_db", 0.0),
                          opcional=bool(e.get("opcional")), delta_db=round(d, 1), estado=estado, avisos=avisos,
                          ventana=[round(x, 3) for x in e["win"]], cue=e.get("cue", "")))

    print(f"\nmezcla: {salida}")
    print(f"loudness integrado {i_lufs:.1f} LUFS (objetivo {OBJETIVO_LUFS:.0f}) · true peak {tp:.1f} dBTP · {dur:.2f} s")
    if musica_bajo is not None:
        print(f"música bajo la voz mientras habla: {musica_bajo:.1f} dB (regla ≥ {MUSICA_BAJO_VOZ_DB:.0f})")
    print(f"\naudibilidad (ventana {a.ventana} s, umbral +{a.umbral} dB sobre voz+música):")
    print(f"{'#':>3} {'t (s)':>6}  {'sfx':16s} {'palabra':12s} {'gain':>5} {'Δ dB':>6}  estado      avisos")
    for f in filas:
        print(f"{f['n']:>3} {f['t']:6.2f}  {f['sfx']:16s} {str(f['palabra'] or '—')[:12]:12s} {f['gain_db']:5.1f} "
              f"{f['delta_db']:6.1f}  {f['estado']:11s} {'; '.join(f['avisos'])}")
    criticos = [f for f in filas if not f["opcional"]]
    print(f"\n{len(criticos) - fallas}/{len(criticos)} eventos importantes se oyen · {len(filas) - len(criticos)} opcionales")

    medir.escribir_json(salida[:-4] + ".reporte.json", {
        "plan": ruta_plan, "salida": salida, "ref": salida[:-4] + ".ref.wav" if a.guardar_ref else None,
        "words": words_p, "duracion_s": round(dur, 3), "loudness_lufs": round(i_lufs, 2), "true_peak_dbtp": round(tp, 2),
        "musica_bajo_voz_db": None if musica_bajo is None else round(musica_bajo, 1),
        "umbral_db": a.umbral, "ventana_s": a.ventana, "eventos": filas, "fallas": fallas,
    })

    if a.registrar:
        usados = {e["sfx"] for e in eventos}
        for c in cat["clips"]:
            if c["id"] in usados and a.registrar not in c["usado_en"]:
                c["usado_en"].append(a.registrar)
        medir.escribir_json(cat_p, cat)
        print(f"registrado '{a.registrar}' en usado_en de {len(usados)} clips")

    if fallas:
        print(f"FALLA: {fallas} evento(s) importante(s) no se oyen: súbeles gain_db o muévelos a un hueco de la voz.")
        sys.exit(1)


if __name__ == "__main__":
    main()
