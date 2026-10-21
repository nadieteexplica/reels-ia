"""Detectores automáticos sobre el video final (sin IA). Marcan eventos para que el revisor los mire; no aprueban ni rechazan solos,
salvo la pantalla vacía, que es bloqueante.

- vacios: cuadros sin contenido fuera de la franja de subtítulos (fondo liso) → "pantalla vacía".
- apariciones: algo aparece o desaparece de golpe dentro de un plano (sin corte) → cono que aparece en la mano, domo que se apaga.
- luz: el brillo de un plano cambia mucho entre su inicio y su fin sin corte → luces que se apagan durante el plano.
- cortes: cambios bruscos de todo el cuadro (si no hay lista de planos).
"""
import numpy as np

FPS_D = 15          # cuadros por segundo para detectar
DW, DH = 216, 384   # resolución de trabajo (1080x1920 / 5)
ESC = 1080 / DW


def mascara_subs(subs_log, n, fps_video=30):
    """Para cada cuadro de detección, una máscara (DH, DW) True donde hay subtítulos (con margen)."""
    m = np.zeros((n, DH, DW), bool)
    if not subs_log:
        m[:, int(990 / ESC):int(1265 / ESC), :] = True   # franja fija si no hay registro
        return m
    for f, _tok, x0, y0, x1, y1, *_ in subs_log:
        i = int(round((f - 1) / fps_video * FPS_D))
        if 0 <= i < n:
            for j in (i - 1, i, i + 1):
                if 0 <= j < n:
                    m[j, max(0, int(y0 / ESC) - 3):int(y1 / ESC) + 3, max(0, int(x0 / ESC) - 3):int(x1 / ESC) + 3] = True
    return m


def detalle(G, mask_band=None):
    """Fracción de píxeles con borde (gradiente > 10) fuera de la franja de subtítulos, por cuadro."""
    gx = np.abs(np.diff(G, axis=2))
    gy = np.abs(np.diff(G, axis=1))
    e = np.pad(gx, ((0, 0), (0, 0), (0, 1))) + np.pad(gy, ((0, 0), (0, 1), (0, 0)))
    band = np.ones((DH, DW), bool)
    band[int(980 / ESC):int(1270 / ESC)] = False
    return ((e > 10) & band).mean(axis=(1, 2))


def vacios(G, min_s=0.2, umbral=0.008):
    d = detalle(G.astype(np.float32))
    bajos = d < umbral
    out, i = [], 0
    while i < len(bajos):
        if bajos[i]:
            j = i
            while j + 1 < len(bajos) and bajos[j + 1]:
                j += 1
            if (j - i + 1) / FPS_D >= min_s:
                out.append({"tipo": "pantalla_vacia", "t0": round(i / FPS_D, 2), "t1": round((j + 1) / FPS_D, 2),
                            "detalle": round(float(d[i:j + 1].mean()), 4), "bloqueante": True,
                            "que": "fondo liso sin contenido fuera de los subtítulos"})
            i = j + 1
        else:
            i += 1
    return out


def cortes(G, umbral=25):
    """Tiempos de corte detectados (cambio de casi todo el cuadro). G: gris (N, DH, DW)."""
    d = np.abs(np.diff(G.astype(np.float32), axis=0)).mean(axis=(1, 2))
    return [round((i + 1) / FPS_D, 2) for i in np.where(d > umbral)[0]]


def apariciones(G, limites, mask, top=15):
    """Algo que aparece o desaparece de golpe dentro de un plano (cono que aparece en la mano, domo que se apaga).
    Compensa el movimiento de cámara y de personajes con flujo óptico: lo que el movimiento no explica es una aparición.
    Sólo compara cuadros del mismo plano. G: cuadros en gris uint8 (N, DH, DW). limites: tiempos de corte (s). mask: subtítulos."""
    import cv2
    n = len(G)
    plano = np.zeros(n, int)
    g = np.abs(np.diff(G.astype(np.float32), axis=0)).mean(axis=(1, 2))
    bordes = {int(round(t * FPS_D)) for t in limites} | {i + 1 for i in np.where(g > 25)[0]}   # cortes listados + detectados
    for k in sorted(bordes):
        plano[k:] += 1
    C = 6
    hc, wc = DH // C, DW // C
    yy, xx = np.mgrid[0:DH, 0:DW].astype(np.float32)

    def celdas(a):
        return a[: hc * C, : wc * C].reshape(hc, C, wc, C).mean(axis=(1, 3))

    R = np.zeros((n - 1, hc, wc), np.float32)
    for i in range(n - 1):
        if plano[i] != plano[i + 1]:
            continue
        fl = cv2.calcOpticalFlowFarneback(G[i + 1], G[i], None, 0.5, 3, 15, 3, 5, 1.2, 0)
        w = cv2.remap(G[i], xx + fl[..., 0], yy + fl[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        r = celdas(np.abs(w.astype(np.float32) - G[i + 1].astype(np.float32)))
        r[:, :1] = r[:, -1:] = r[:1] = r[-1:] = 0          # bordes: el flujo inventa ahí
        r[celdas(mask[i].astype(float) + mask[i + 1].astype(float)) > 0.05] = 0
        R[i] = r
    ev = []
    for i in range(n - 1):
        if plano[i] != plano[i + 1]:
            continue
        vec = [R[j] for j in (i - 2, i - 1, i + 1, i + 2) if 0 <= j < n - 1 and plano[j] == plano[i] and plano[j + 1] == plano[i]]
        if not vec:
            continue
        vecino = np.max(np.stack(vec), axis=0)
        cand = (R[i] > 35) & (R[i] > 2.5 * (vecino + 4))
        k = int(cand.sum())
        if k == 0 or k > 0.2 * hc * wc:
            continue
        ys, xs = np.where(cand)
        ev.append({"tipo": "aparece_o_desaparece", "t": round((i + 1) / FPS_D, 2),
                   "caja": [int(xs.min() * C * ESC), int(ys.min() * C * ESC), int((xs.max() + 1) * C * ESC), int((ys.max() + 1) * C * ESC)],
                   "celdas": k, "score": round(float(np.median(R[i][cand] / (vecino[cand] + 4)) * np.sqrt(k)), 2),
                   "bloqueante": False, "que": "algo cambia de golpe en 1 cuadro dentro del plano y el movimiento no lo explica"})
        c = ev[-1]["caja"]
        if c[3] - c[1] <= 200 and 230 <= c[1] and c[3] <= 480:
            ev[-1]["que"] += " (zona de etiquetas: puede ser una píldora que entra a propósito)"
    ev.sort(key=lambda e: -e["score"])
    elegidos = []
    for e in ev:
        if all(abs(e["t"] - o["t"]) > 0.4 for o in elegidos):
            elegidos.append(e)
    return sorted(elegidos[:top], key=lambda e: e["t"])


def luz(G, planos, umbral=0.30):
    """Planos cuyo brillo cambia más de un 30 % entre el primer y el último tercio, sin corte. G: gris (N, DH, DW)."""
    G = G.astype(np.float32)
    out = []
    for p in planos:
        a, b = int(round(p["a"] * FPS_D)) + 1, int(round(p["b"] * FPS_D)) - 1
        if b - a < 6:
            continue
        L = G[a:b].mean(axis=(1, 2))
        k = max(2, (b - a) // 3)
        l0, l1 = float(L[:k].mean()), float(L[-k:].mean())
        rel = (l1 - l0) / max(l0, 8)
        if abs(rel) > umbral:
            out.append({"tipo": "cambio_de_luz", "plano": p["plano"], "t0": p["a"], "t1": p["b"], "cambio": round(rel * 100),
                        "bloqueante": False, "que": f"el brillo {'sube' if rel > 0 else 'baja'} {abs(round(rel * 100))} % dentro del plano"})
    return out


def sin_cambio(planos, max_s=2.5):
    """Planos más largos que lo permitido: el revisor confirma si hay transformación dentro del cuadro."""
    return [{"tipo": "plano_largo", "plano": p["plano"], "t0": p["a"], "t1": p["b"], "dur": round(p["b"] - p["a"], 2),
             "bloqueante": False, "que": f"plano de {p['b'] - p['a']:.1f} s: confirmar que algo cambia cada 1,5 s"}
            for p in planos if p["b"] - p["a"] > max_s]
