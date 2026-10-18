"""Frame capture for code-generated reels.
Usage: python3 capture.py <page_path> <out_dir> <start_frame> <end_frame> [fps] [rs]
       python3 capture.py <page_path> <out_dir> --times 0,7.5,20 [rs]
"""
import sys, os, time
from playwright.sync_api import sync_playwright

page_path, out_dir = sys.argv[1], sys.argv[2]
os.makedirs(out_dir, exist_ok=True)
args = ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]

def run(frames, rs):
    with sync_playwright() as p:
        b = p.chromium.launch(args=args)
        pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        pg.on("console", lambda m: print("console:", m.text) if m.type in ("error", "warning") else None)
        pg.on("pageerror", lambda e: print("pageerror:", e))
        pg.goto(f"http://127.0.0.1:8765/{page_path}?rs={rs}")
        pg.wait_for_function("window.READY===true", timeout=180000)
        t0 = time.time()
        for name, t in frames:
            pg.evaluate(f"renderAt({t})")
            pg.screenshot(path=os.path.join(out_dir, name), type="jpeg", quality=93)
        print(f"{len(frames)} frames in {time.time()-t0:.1f}s")
        b.close()

if sys.argv[3] == "--times":
    times = [float(x) for x in sys.argv[4].split(",")]
    rs = sys.argv[5] if len(sys.argv) > 5 else "1"
    run([(f"t{t:05.2f}.jpg", t) for t in times], rs)
else:
    s, e = int(sys.argv[3]), int(sys.argv[4])
    fps = int(sys.argv[5]) if len(sys.argv) > 5 else 30
    rs = sys.argv[6] if len(sys.argv) > 6 else "1"
    run([(f"f{f:05d}.jpg", f / fps) for f in range(s, e)], rs)
