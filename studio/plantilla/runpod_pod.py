"""Crea, vigila y borra el pod de RunPod que renderiza un episodio en GPU (lo usa .github/workflows/render-gpu.yml).

  python runpod_pod.py crear      → imprime el id del pod (env: RUNPOD_API_KEY y las variables que necesita runpod_render.sh)
  python runpod_pod.py esperar ID → espera el estado.txt en la prerelease del run; borra el pod si se pasa del tiempo
  python runpod_pod.py borrar ID  → borra el pod (si ya no existe, no pasa nada)
La clave sólo se lee del entorno y nunca se imprime.
"""
import json, os, sys, time, urllib.request, urllib.error

API = "https://rest.runpod.io/v1"


def req(method, path, body=None):
    r = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                               headers={"Authorization": f"Bearer {os.environ['RUNPOD_API_KEY']}", "Content-Type": "application/json",
                                        "User-Agent": "reels-ia-render/1.0"})  # Cloudflare bloquea el agente por defecto de urllib (error 1010)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            t = resp.read().decode()
            return resp.status, (json.loads(t) if t.strip() else {})
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode(errors="replace")[:500]}


def crear():
    e = os.environ
    sh = (f"https://raw.githubusercontent.com/{e['REPO']}/{e['SHA']}/studio/plantilla/runpod_render.sh")
    cmd = ("apt-get update -qq && apt-get install -y -qq curl ca-certificates > /dev/null && "
           f"curl -fsSL {sh} -o /r.sh && bash /r.sh; "
           # si algo falla antes de que el script tome el control, el pod igual se borra
           "curl -s -X DELETE https://rest.runpod.io/v1/pods/$RUNPOD_POD_ID -H \"Authorization: Bearer $RUNPOD_API_KEY\"; sleep 600")
    env = {k: e[k] for k in ("REPO", "SHA", "EP", "RES", "SAMPLES", "UPLOAD_URL", "GH_TOKEN", "ASSETS_TOKEN", "RUNPOD_API_KEY")}
    env["CUADROS"] = e.get("CUADROS", "")
    gpus = [g.strip() for g in e.get("GPUS", "NVIDIA GeForce RTX 4090").split(",") if g.strip()]
    body = {"name": f"reels-{e['EP'][:20]}-{e.get('GITHUB_RUN_ID', '')}", "imageName": "nvidia/cuda:12.4.1-base-ubuntu22.04",
            "cloudType": e.get("NUBE", "COMMUNITY"), "computeType": "GPU", "gpuTypeIds": gpus, "gpuTypePriority": "custom",
            "gpuCount": 1, "containerDiskInGb": 40, "volumeInGb": 0, "minVCPUPerGPU": 8, "minRAMPerGPU": 24,
            "ports": [], "env": env, "dockerStartCmd": ["bash", "-c", cmd], "interruptible": False}
    for intento in range(3):
        st, r = req("POST", "/pods", body)
        if st in (200, 201) and r.get("id"):
            print(r["id"])
            print(f"pod {r['id']} · {r.get('machine', {}).get('gpuDisplayName', '') or r.get('gpu', {})} · USD {r.get('costPerHr', '?')}/h",
                  file=sys.stderr)
            return 0
        print(f"no se pudo crear el pod ({st}): {r}", file=sys.stderr)
        if body["cloudType"] == "COMMUNITY":
            body["cloudType"] = "SECURE"   # sin stock en community: probar secure
        time.sleep(10)
    return 1


def borrar(pid):
    st, r = req("DELETE", f"/pods/{pid}")
    print(f"borrar {pid}: {st}")
    return 0


def esperar(pid, tag, repo, limite_min=110):
    import subprocess
    t0 = time.time()
    while time.time() - t0 < limite_min * 60:
        time.sleep(30)
        a = subprocess.run(["gh", "api", f"repos/{repo}/releases/tags/{tag}", "--jq", "[.assets[].name]"], capture_output=True, text=True).stdout
        if "estado.txt" in a:
            print(f"terminó a los {int((time.time() - t0) / 60)} min")
            return 0
        st, r = req("GET", f"/pods/{pid}")
        if st == 404:
            print("el pod ya no existe y no dejó estado")
            return 1
        mins = int((time.time() - t0) / 60)
        if mins % 5 == 0:
            print(f"{mins} min · pod {r.get('desiredStatus', '?')} · USD {r.get('costPerHr', '?')}/h · subido: {a.strip()}", flush=True)
    print("se pasó del tiempo: se borra el pod")
    borrar(pid)
    return 1


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "crear":
        sys.exit(crear())
    if c == "borrar":
        sys.exit(borrar(sys.argv[2]))
    if c == "esperar":
        sys.exit(esperar(sys.argv[2], sys.argv[3], sys.argv[4]))
    sys.exit(__doc__)
