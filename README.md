# Raw Return

Website for Raw Return, a reconstruction denim house in London. An archive with a
shop in it, not a shop with a blog.

Built with [Astro](https://astro.build) as a static site. No framework runtime: the
interactive parts (bag, motion, archive filters) are small vanilla TypeScript modules.

```bash
npm install
npm run dev       # http://localhost:4321
npm run build     # static output in dist/
npm run check     # type-check .astro and .ts files
```

## Structure

```
src/
  data/
    pieces.ts      every piece RR-001 →, the single source for shop, archive, records
    process.ts     the seven stages, founder commentary, technical facts
    notes.ts       journal entries, organised by series
    images.ts      image registry: 'products/rr-014-front' → src/assets/images/…
  components/      design-system components (see below)
  layouts/Base.astro
  pages/           / · /shop · /archive · /archive/[rr-0xx] · /the-house · /process
                   /notes · /notes/[slug] · /checkout · 404
  scripts/
    cart.ts        the bag: localStorage state, drawer, focus trap, edition limits
    motion.ts      reveals, parallax, pinned contact sheet, header, cursor label
  styles/
    tokens.css     brand tokens — colour, type, grid, motion (from the guideline)
    global.css     reset, type roles, layout, reveal system, view transitions
  assets/images/   placeholder photography — see the README in that folder
tools/photo/       the placeholder photography renderer (Python)
```

### Components

`Header` · `Footer` · `Wordmark` · `PieceCard` (product card) · `ArchiveRecord`
(two-half first life / second life record) · `ArchiveTable` · `SpecBlock` (technical
record) · `FounderQuote` · `EditorialImage` (masked reveal, parallax, caption) ·
`ContactSheet` (pinned horizontal process sequence) · `Gallery` · `PurchaseModule` ·
`Status` · `CartDrawer` · `Button` · `NewsletterForm` · `SectionLabel` · `Lines`
(line-by-line headline reveal) · `Img`.

## Adding a piece

Add an entry to `src/data/pieces.ts` with the next RR number (numbers never reset),
drop its photographs into `src/assets/images/products/` and `street/` using the same
key, and rebuild. The shop, archive, record, product page, footer counts and bag
pick it up automatically. When a piece sells, set `status: 'returned'` and add
`returned: { date, by }` — it stays in the archive permanently.

## Before launch — placeholders to replace

Search the codebase for `PLACEHOLDER` to find every one.

- **Photography:** every image is a rendered placeholder. Shot list:
  `src/assets/images/README.md`.
- **Records:** RR-001 → RR-010, RR-016, all prices, dates, wearer names and most founder
  notes were written to show the system working. RR-011 → RR-015 follow the brand
  guideline. The founder should check every line.
- **The founder's story** on `/the-house` must be written by the founder.
- **Payment:** `/checkout` validates details but no payment provider is connected.
  Wire it to Shopify Checkout or Stripe Checkout; bag lines are on `window.rrBag.lines()`.
- **Newsletter:** the form confirms locally; connect it to the email provider.
- **Domain, Instagram handle, contact address, shipping and returns terms.**

## Accessibility & performance

Semantic landmarks, skip link, visible focus, keyboard-operable menu and bag (focus
trap, Esc, `inert` background), live-region announcements, alt text on every image,
`prefers-reduced-motion` respected throughout (no smooth scroll, no pinning, no
reveals). Images are served as responsive WebP via `astro:assets` with lazy loading
below the fold. Every page passes an axe-core audit with zero violations.
