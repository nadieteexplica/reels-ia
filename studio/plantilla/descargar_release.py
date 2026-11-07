"""Baja assets de una release de GitHub con la API REST (sin gh): lo usa el pod de RunPod (runpod_planos.sh).

  python descargar_release.py <owner/repo> <tag> <carpeta> <patrón> [patrón ...]
El token sale de la variable GH_DL_TOKEN (nunca se imprime). Los patrones son tipo glob (fnmatch).
"""
import fnmatch, json, os, sys, urllib.request

repo, tag, dst, pats = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
tok = os.environ.get("GH_DL_TOKEN", "")
h = {"Authorization": f"Bearer {tok}", "User-Agent": "reels-ia-pod", "Accept": "application/vnd.github+json"}
r = urllib.request.urlopen(urllib.request.Request(f"https://api.github.com/repos/{repo}/releases/tags/{tag}", headers=h), timeout=60)
assets = json.load(r)["assets"]
os.makedirs(dst, exist_ok=True)
n = 0
for a in assets:
    if not any(fnmatch.fnmatch(a["name"], p) for p in pats):
        continue
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases/assets/{a['id']}",
                                 headers=dict(h, Accept="application/octet-stream"))
    with urllib.request.urlopen(req, timeout=600) as resp, open(os.path.join(dst, a["name"]), "wb") as f:
        while True:
            b = resp.read(1 << 20)
            if not b:
                break
            f.write(b)
    n += 1
print(f"{repo}@{tag}: {n} archivos → {dst}")
