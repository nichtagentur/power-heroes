#!/usr/bin/env python3
"""Generate 8 hero portraits via OpenRouter -> Gemini 2.5 Flash Image (Nano Banana)."""
import os, json, base64, urllib.request, sys, concurrent.futures
from pathlib import Path

OUT = Path(__file__).parent / 'heroes'
OUT.mkdir(exist_ok=True)
KEY = os.environ['OPENROUTER_API_KEY']
URL = 'https://openrouter.ai/api/v1/chat/completions'
MODEL = 'google/gemini-2.5-flash-image'

# Shared style anchor — every hero shares this so the set looks like one comic.
STYLE = (
    "Vintage 1960s Silver-Age comic-book superhero portrait, square 1:1 frame, "
    "Roy Lichtenstein pop-art aesthetic, prominent halftone Ben-Day dot pattern background, "
    "bold thick black ink outlines, flat saturated color fills, dynamic motion lines, "
    "no text, no logos, no signatures, no watermarks, no speech bubbles, no captions. "
    "3/4 hero bust portrait, confident heroic pose, masked face like classic superhero. "
    "Cream pulp-paper border. Reads like one panel from a printed comic."
)

HEROES = [
    ("solara",   "SOLARA, the Sun Champion. Female superhero with golden mask, sun-ray halo headpiece, glowing yellow costume. Sun-disc emblem on chest. Background: saturated comic yellow #ffd60a with halftone dots. Hair flowing like solar flares."),
    ("aerial",   "AERIAL, the Gale Sentinel. Female superhero with sleek goggles, swept-back hair as if standing in a gale, teal-green flight cape. Wind-turbine emblem on chest. Background: teal #3aafa9 with halftone dots. Wind streak lines around her."),
    ("cascada",  "CASCADA, the Pumped Storm. Female superhero with deep-blue mask, water-droplet emblem on chest, costume that looks like flowing water, splashing water motifs around her. Background: cobalt blue #0466c8 with halftone dots."),
    ("neutra",   "NEUTRA, the Fission Phoenix. Female superhero with sleek magenta mask, atom emblem on chest with three elliptical orbital rings around a glowing nucleus, magenta-pink costume. Background: hot pink #d62898 with halftone dots. Energy aura."),
    ("vulcana",  "VULCANA, Daughter of the Deep. Female superhero with orange mask, volcano emblem on chest with magma plume, orange-red costume with lava-line trim. Background: hot orange-red #ef5b2a with halftone dots. Spark particles around her."),
    ("verda",    "VERDA, the Forest Forge. Female superhero with green mask, leaf emblem on chest with subtle circuit-like veins, deep-green costume with subtle bark-pattern texture. Background: forest green #3a915b with halftone dots. Floating leaf motifs."),
    ("marea",    "MAREA, the Tidal Rookie. Young female superhero with cyan mask, cresting-wave emblem on chest, cyan-blue costume, ocean-spray motifs around her. Background: cyan #00b4d8 with halftone dots. Wave-curl lines."),
    ("hydra",    "HYDRA, the Quantum Carrier. Female superhero with violet mask, H2-molecule emblem on chest (two connected circles), electric purple costume with crackling lightning-spark trim. Background: violet #7b4eff with halftone dots. Energy sparks around her."),
]


def gen_one(handle, hero_prompt):
    out_path = OUT / f"{handle}.png"
    if out_path.exists() and out_path.stat().st_size > 5000:
        print(f"[skip] {handle} already exists ({out_path.stat().st_size} bytes)")
        return out_path

    full_prompt = f"{hero_prompt}\n\n{STYLE}"
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": full_prompt}],
        "modalities": ["image", "text"],
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://nichtagentur.github.io/power-heroes/",
            "X-Title": "Europe's Power Heroes",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())

    # Gemini image responses on OpenRouter live in choices[0].message.images
    choice = data["choices"][0]["message"]
    images = choice.get("images") or []
    if not images:
        # Sometimes content has data: url
        content = choice.get("content") or ""
        raise RuntimeError(f"No image returned for {handle}. Response: {json.dumps(data)[:500]}")

    img = images[0]
    url = img.get("image_url", {}).get("url") if isinstance(img, dict) else None
    if not url:
        raise RuntimeError(f"Unexpected image shape for {handle}: {json.dumps(img)[:300]}")

    # data:image/png;base64,...
    if url.startswith("data:"):
        b64 = url.split(",", 1)[1]
        out_path.write_bytes(base64.b64decode(b64))
    else:
        # Remote URL — download
        with urllib.request.urlopen(url) as r:
            out_path.write_bytes(r.read())
    print(f"[ok] {handle} -> {out_path} ({out_path.stat().st_size} bytes)")
    return out_path


def main():
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(gen_one, h, p): h for h, p in HEROES}
        for f in concurrent.futures.as_completed(futs):
            h = futs[f]
            try:
                f.result()
            except Exception as e:
                print(f"[FAIL] {h}: {e}", file=sys.stderr)
                failures.append(h)
    if failures:
        sys.exit(f"failed: {failures}")
    print("All 8 heroes generated.")


if __name__ == "__main__":
    main()
