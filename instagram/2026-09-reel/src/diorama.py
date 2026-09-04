"""Generate the miniature travel-poster diorama series with Nano Banana Pro.

The user supplied a Rio de Janeiro prompt as the art direction. Nara Abroad is a
study-abroad platform, so the same treatment is applied to the destinations the
brand actually sends students to - the Rio original is kept as the reference.
"""
import base64, sys, time
from gem import call

MODELS = ["gemini-3-pro-image", "gemini-3.1-flash-image", "gemini-2.5-flash-image"]

STYLE = """Create a highly detailed, photorealistic miniature travel-poster diorama inspired by {CITY}, arranged as a handcrafted 3D paper scene on a warm ivory, slightly textured background.

In the foreground, a realistic human hand holds a vintage {COUNTRY} travel ticket or {CITY}-themed transit card vertically on the left side. Give the card aged paper texture, subtle printing imperfections, elegant typography, and authentic-looking travel details. From behind the card, a miniature {CITY} landscape physically rises outward like an intricate pop-up diorama.

Make {LANDMARK} the dominant central landmark, positioned high above a miniature cityscape with {SURROUND}. Below, build a tiny realistic {CITY} street featuring {STREET}. Add {DISTANCE} in the distance. Layer the architecture and terrain so everything appears physically constructed from paper, wood, plaster, and miniature materials, with convincing depth, cast shadows, overlapping surfaces, and a slight three-quarter perspective.

Around the main 3D scene, incorporate delicate black, charcoal, and muted sepia hand-drawn travel illustrations on the cream paper. Include {SKETCHES}. Add subtle handwritten travel notes, tiny map markings, architectural outlines, compass symbols, postage-stamp details, and understated travel annotations.

Keep the composition refined rather than crowded. Blend realistic miniature photography with vintage travel-journal design, tactile paper fibers, faint ink bleed, imperfect hand-drawn lines, warm natural studio lighting, gentle shadows, subtle film grain, and a sophisticated cream, charcoal, {PALETTE} palette.

The final image should feel like a premium collectible {CITY} travel postcard transformed into a physical miniature world, with the central diorama sharply detailed and the surrounding illustrations slightly softer. Highly realistic human hand and fingers, believable miniature materials, cinematic product photography, editorial travel-magazine aesthetic, shallow depth of field, ultra-fine textures, photorealistic 3D details, vertical 4:5 composition, 8K quality.

Leave the upper right area comparatively calm and uncluttered so a small logo can sit there later. Do not render any text in Arabic. Any lettering on the ticket or sketches must be plausible Latin travel typography."""

CITIES = {
 "london": dict(CITY="London", COUNTRY="British", LANDMARK="Big Ben and the Houses of Parliament",
   SURROUND="Westminster rooftops and plane trees around it",
   STREET="a classic red double-decker bus, a black cab, Georgian townhouses, red phone box, "
          "pedestrians with umbrellas, cyclists, cast-iron street lamps, and wet paving stones",
   DISTANCE="a glimpse of Tower Bridge and the Thames with tiny boats",
   SKETCHES="a small Tower Bridge sketch in the upper left, an artistic London Eye illustration in the "
            "upper right, a detailed Underground roundel and terrace-house study along the right side, "
            "and a small St Paul's dome drawing near the bottom",
   PALETTE="muted green, deep Westminster blue, and London bus red"),
 "berlin": dict(CITY="Berlin", COUNTRY="German", LANDMARK="the Brandenburg Gate",
   SURROUND="linden trees and Mitte rooftops around it",
   STREET="a yellow BVG tram, cream Altbau facades, bicycles leaning on railings, a currywurst kiosk, "
          "students with tote bags, street lamps, and cobblestones",
   DISTANCE="a glimpse of the Fernsehturm television tower and the Spree river",
   SKETCHES="a small Fernsehturm sketch in the upper left, an artistic Museum Island illustration in the "
            "upper right, a detailed East Side Gallery wall study along the right side, and a small "
            "Reichstag dome drawing near the bottom",
   PALETTE="muted green, slate blue, and mustard yellow"),
 "amsterdam": dict(CITY="Amsterdam", COUNTRY="Dutch", LANDMARK="a tall canal-house row with stepped gables",
   SURROUND="elm trees and a curving canal around it",
   STREET="a white-and-blue tram, hundreds of parked bicycles, an arched bridge over the canal, "
          "a houseboat, tulip stall, students cycling, and iron street lamps",
   DISTANCE="a glimpse of the Rijksmuseum and windmills on the horizon",
   SKETCHES="a small windmill sketch in the upper left, an artistic canal-bridge illustration in the "
            "upper right, a detailed gable-facade study along the right side, and a small bicycle "
            "drawing near the bottom",
   PALETTE="muted green, canal blue, and warm brick orange"),
 "rio": dict(CITY="Rio de Janeiro", COUNTRY="Brazilian", LANDMARK="Christ the Redeemer",
   SURROUND="lush green mountains surrounding it",
   STREET="a classic yellow taxi, colorful buildings, palm trees, pedestrians, cyclists, street lamps, "
          "tiled sidewalks, and small Brazilian urban details",
   DISTANCE="Copacabana beach elements with tiny umbrellas, beachgoers, and a glimpse of the Atlantic Ocean",
   SKETCHES="a small Sugarloaf Mountain sketch in the upper left, an artistic Copacabana promenade "
            "illustration in the upper right, a detailed Selaron Steps sketch along the right side, "
            "and a small Ipanema beachfront skyline drawing near the bottom",
   PALETTE="muted green, ocean blue, and Brazilian yellow"),
}


def generate(key, out):
    prompt = STYLE
    for k, v in CITIES[key].items():
        prompt = prompt.replace("{" + k + "}", v)
    for attempt in range(14):
      for model in MODELS:
        st, d = call(f"models/{model}:generateContent", {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["IMAGE"],
                                 "imageConfig": {"aspectRatio": "4:5"}},
        })
        if st == 429:
            wait = 32
            for det in d.get("error", {}).get("details", []):
                if det.get("@type", "").endswith("RetryInfo"):
                    wait = int(str(det.get("retryDelay", "32s")).rstrip("s") or 32) + 5
            print(f"  {key}: {model} rate-limited, waiting {wait}s (try {attempt+1}/14)", flush=True)
            time.sleep(wait); continue
        if st != 200:
            print(f"  {key}: {model} -> HTTP {st} {str(d)[:110]}", flush=True)
            time.sleep(3); continue
        try:
            parts = d["candidates"][0]["content"]["parts"]
            blob = next(p["inlineData"]["data"] for p in parts if "inlineData" in p)
        except (KeyError, IndexError, StopIteration):
            print(f"  {key}: {model} -> no image in response {str(d)[:110]}")
            continue
        raw = base64.b64decode(blob)
        open(out, "wb").write(raw)
        print(f"  {key}: OK via {model}  ({len(raw)//1024} KB)", flush=True)
        return True
    return False


if __name__ == "__main__":
    for key in (sys.argv[1:] or ["london", "berlin", "amsterdam", "rio"]):
        generate(key, f"dio-{key}.png")
