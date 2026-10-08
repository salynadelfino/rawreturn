# Photography — placeholder set and shot list

Every image in this folder is a **placeholder**, rendered by `tools/photo/render.py`
so that the whole site sits in one photographic world (same denim, same concrete,
same two lights, same film grade). None of it is real photography, and none of it
shows real garments or people.

**To replace an image:** export the real photograph as JPEG, give it the exact same
path and filename, overwrite the file, and rebuild (`npm run build`). Any aspect ratio
works — the site crops with `object-fit: cover`. Alt text lives in
`src/data/pieces.ts`, `src/data/process.ts` and `src/data/notes.ts`; update it to
describe the real photograph.

## The two lights (brand guideline §13)

- **Available light, inside** — workshop, process, founder, piece. Quiet, slow, exact.
- **Direct flash, outside** — the return. Fast, social, night, London.

The switch in light marks the moment a piece leaves the bench. Grade: cool, slightly
lifted blacks, denim true to colour, never orange-teal, tan must read as tan.
35mm or medium format. Tight on hands and seams; wide on rooms and streets.

## Shot list

| File | Replace with | Light |
| --- | --- | --- |
| `hero/hero-bench-night.jpg` | The cutting table at night, one lamp, RR-014 half-built: pinned panels, pattern paper, shears, the unsewn tan patch. Wide, 3:2 or wider. | Available (lamp) |
| `workshop/bench-day.jpg` | The workshop in daylight, the bench mid-job. | Available |
| `workshop/the-pile.jpg` | The pile on a concrete floor — every wash. Wide. | Available |
| `workshop/the-pile-flash.jpg` | A closer, harder frame of the pile: waistbands, pockets, folded legs. | On-camera flash |
| `workshop/chalk-on-indigo.jpg` | Chalk lines, notches and a ruler on raw indigo, the moment before a cut. | Available |
| `workshop/topstitch-macro.jpg` | Macro: two first-life garments meeting at a felled seam, gold topstitch. | Available |
| `workshop/selvedge-macro.jpg` | Macro: selvedge ID inside a placket or cuff. | Available |
| `workshop/ghost-pocket-macro.jpg` | Macro: the unfaded ghost of a removed back pocket. | Available |
| `workshop/patch-macro.jpg` | The debossed tan leather patch on denim. | Available |
| `process/01-find.jpg` … `07-return.jpg` | One frame per stage: the pile; a garment unpicked; panels laid out and tagged; marking and cutting; pinned on the bench; the record card; the piece on the street. | 01–06 available, 07 flash |
| `process/failed-sleeves.jpg` | The failed attempts hanging on the workshop wall, tagged. | Available |
| `founder/founder-bench.jpg` | The founder at the bench — from behind or side-on, hands working. Never a posed portrait. | Available |
| `founder/founder-hands-chalk.jpg` | Hands marking up denim with chalk and a ruler. | Available |
| `archive/rr-014-record.jpg` | The printed record of making on its board, with the offcut card. | Flash or available |
| `products/rr-0XX-front.jpg` | The piece hung on a plaster wall or laid flat on concrete, one hard light. Portrait 4:5. | One hard light |
| `products/rr-0XX-back.jpg` | Same set-up, back view. | One hard light |
| `products/rr-0XX-detail.jpg` | A construction close-up — every seam joining two garments deserves a frame. Square. | Available |
| `street/rr-0XX-returned.jpg` | The piece worn by its real wearer on a London street at night. Direct flash, movement, imperfect framing. Cast friends and customers, not agency models. Portrait 4:5. | Direct flash |
| `street/night-kerb.jpg`, `street/brick-flash.jpg` | Spare street frames for future pages. | Direct flash |

## Never

White-sweep e-commerce, ghost mannequins, lifestyle cafés, staged "artisan" props,
fake handwriting, recycling or eco imagery, graffiti, all-black streetwear styling.
If a real image is supplied for a piece, the garment must never be altered:
proportions, construction, colours, patches, stitching, labels, wear and hardware
stay exactly as they are. The photography can change. The garment cannot.

## Re-rendering the placeholders

```bash
pip install -r tools/photo/requirements.txt
npm run images            # everything (≈ 4 min on 4 cores)
npm run images -- rr-014  # only files whose path contains "rr-014"
```
