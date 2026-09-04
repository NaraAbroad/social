# Diorama series — image prompts

Art direction supplied by the client (originally written for Rio de Janeiro),
re-pointed at the destinations Nara Abroad actually sends students to. The
wording of the style is kept intact so every image in the series matches.

Two lines were added to every prompt:

- *"Leave the upper right area comparatively calm and uncluttered"* — that is
  where the Nara wordmark sits once the image becomes a post.
- *"Do not render any text in Arabic"* — image models mangle Arabic letterforms.
  Arabic is added afterwards, as live text, in the post layout.

Output is 4:5 (1080×1350), the same ratio as the existing post set.

---

## 1 — London

Create a highly detailed, photorealistic miniature travel-poster diorama inspired by London, arranged as a handcrafted 3D paper scene on a warm ivory, slightly textured background.

In the foreground, a realistic human hand holds a vintage British travel ticket or London-themed transit card vertically on the left side. Give the card aged paper texture, subtle printing imperfections, elegant typography, and authentic-looking travel details. From behind the card, a miniature London landscape physically rises outward like an intricate pop-up diorama.

Make Big Ben and the Houses of Parliament the dominant central landmark, positioned high above a miniature cityscape with Westminster rooftops and plane trees around it. Below, build a tiny realistic London street featuring a classic red double-decker bus, a black cab, Georgian townhouses, red phone box, pedestrians with umbrellas, cyclists, cast-iron street lamps, and wet paving stones. Add a glimpse of Tower Bridge and the Thames with tiny boats in the distance. Layer the architecture and terrain so everything appears physically constructed from paper, wood, plaster, and miniature materials, with convincing depth, cast shadows, overlapping surfaces, and a slight three-quarter perspective.

Around the main 3D scene, incorporate delicate black, charcoal, and muted sepia hand-drawn travel illustrations on the cream paper. Include a small Tower Bridge sketch in the upper left, an artistic London Eye illustration in the upper right, a detailed Underground roundel and terrace-house study along the right side, and a small St Paul's dome drawing near the bottom. Add subtle handwritten travel notes, tiny map markings, architectural outlines, compass symbols, postage-stamp details, and understated travel annotations.

Keep the composition refined rather than crowded. Blend realistic miniature photography with vintage travel-journal design, tactile paper fibers, faint ink bleed, imperfect hand-drawn lines, warm natural studio lighting, gentle shadows, subtle film grain, and a sophisticated cream, charcoal, muted green, deep Westminster blue, and London bus red palette.

The final image should feel like a premium collectible London travel postcard transformed into a physical miniature world, with the central diorama sharply detailed and the surrounding illustrations slightly softer. Highly realistic human hand and fingers, believable miniature materials, cinematic product photography, editorial travel-magazine aesthetic, shallow depth of field, ultra-fine textures, photorealistic 3D details, vertical 4:5 composition, 8K quality.

Leave the upper right area comparatively calm and uncluttered so a small logo can sit there later. Do not render any text in Arabic. Any lettering on the ticket or sketches must be plausible Latin travel typography.

---

## 2 — Berlin

Same opening paragraph, with Berlin / German in place of London / British.

- **Central landmark:** the Brandenburg Gate, above linden trees and Mitte rooftops
- **Street level:** a yellow BVG tram, cream Altbau facades, bicycles leaning on railings, a currywurst kiosk, students with tote bags, street lamps, cobblestones
- **Distance:** the Fernsehturm television tower and the Spree river
- **Marginal sketches:** Fernsehturm upper left, Museum Island upper right, East Side Gallery wall study along the right, Reichstag dome near the bottom
- **Palette:** cream, charcoal, muted green, slate blue, mustard yellow

---

## 3 — Amsterdam

- **Central landmark:** a tall canal-house row with stepped gables, above elm trees and a curving canal
- **Street level:** a white-and-blue tram, hundreds of parked bicycles, an arched bridge, a houseboat, tulip stall, students cycling, iron street lamps
- **Distance:** the Rijksmuseum and windmills on the horizon
- **Marginal sketches:** windmill upper left, canal bridge upper right, gable-facade study along the right, bicycle near the bottom
- **Palette:** cream, charcoal, muted green, canal blue, warm brick orange

---

## 4 — Rio de Janeiro (the original brief, unchanged)

Kept as the reference image for the series, and as the template any further
city inherits from.

- **Central landmark:** Christ the Redeemer above lush green mountains
- **Street level:** yellow taxi, colorful buildings, palm trees, pedestrians, cyclists, street lamps, tiled sidewalks
- **Distance:** Copacabana beach, tiny umbrellas, beachgoers, the Atlantic
- **Marginal sketches:** Sugarloaf upper left, Copacabana promenade upper right, Selarón Steps along the right, Ipanema skyline near the bottom
- **Palette:** cream, charcoal, muted green, ocean blue, Brazilian yellow

---

## Turning an image into a post

Each finished diorama becomes a 1080×1350 post the same way:

1. Image fills the frame.
2. Nara wordmark, small, upper right — the area the prompt keeps clear.
3. A short Levantine headline over the lower third, on a soft dark scrim so it
   stays readable against the ivory paper.
4. `nara-abroad.co.uk` on the bottom edge.

Suggested headlines, one per city:

| City | Headline | Sub |
|---|---|---|
| London | لندن مش بس حلم. | شوف برامجها وتكلفتها الحقيقية |
| Berlin | ألمانيا: رسوم شبه مجانية. | بس في شروط لازم تعرفها |
| Amsterdam | هولندا بتدرّس بالإنجليزي. | أكتر مما بتتخيّل |
| Rio | وين شايف حالك؟ | ٣٥ دولة، وكل وحدة إلها قصة |

`src/diorama.py` in the reel folder generates the series once quota allows —
`python3 diorama.py london berlin amsterdam rio`.
