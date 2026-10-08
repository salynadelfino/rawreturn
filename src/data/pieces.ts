/**
 * The archive. Every piece Raw Return has made, in order. Numbers never reset.
 *
 * This file is the single source for the shop, the archive, product pages and
 * records. Sold pieces stay here permanently — they are the proof.
 *
 * PLACEHOLDER DATA: RR-011 → RR-015 come from the brand guideline. RR-001 →
 * RR-010 and RR-016, all prices, dates, wearer names and founder notes not in
 * the guideline are written to show the system working. Replace with the
 * founder's real records before launch.
 */

export type Status = 'available' | 'in-work' | 'returned';

export interface Piece {
  no: string; // RR-014
  slug: string; // rr-014
  name: string;
  type: string;
  status: Status;
  edition: { size: number; remaining: number }; // 1/1 → { size: 1, remaining: 1 }
  price: number | null; // GBP, whole pounds
  firstLife: string[]; // one garment per line, as listed on the care label
  garments: number; // count of first-life garments
  found: { place: string; date: string };
  panels: number | null;
  hours: number | null;
  attempts?: string;
  started: string; // DD.MM.YYYY
  finished?: string;
  returned?: { date: string; by: string };
  fit: string;
  material: string;
  description: string;
  note: string; // the founder, first person
  /** Image keys under src/assets/images (without extension). */
  images: { front: string; back?: string; detail?: string; returned?: string };
  alt: { front: string; back?: string; detail?: string; returned?: string };
}

const pieces: Piece[] = [
  {
    no: 'RR-001',
    slug: 'rr-001',
    name: 'Hem Belt',
    type: 'Belt',
    status: 'returned',
    edition: { size: 1, remaining: 0 },
    price: null,
    firstLife: ["2 × Levi's 505 hems"],
    garments: 2,
    found: { place: 'Leyton, E10', date: '03.2025' },
    panels: 8,
    hours: 6,
    started: '02.04.2025',
    finished: '05.04.2025',
    returned: { date: '04.2025', by: 'Dan, Leyton' },
    fit: '84–96 cm',
    material: '100% cotton denim, steel buckle',
    description:
      'Eight hems cut from two pairs of 505s, joined end to end with their original chain-stitch left on. The buckle came off a market stall on the same street as the jeans.',
    note: 'The first one. Two hems, one buckle. Six hours, most of them unpicking.',
    images: { front: 'products/rr-001-front', returned: 'street/rr-001-returned' },
    alt: {
      front: 'RR-001 Hem Belt laid flat on concrete: eight hem sections in different washes joined end to end.',
      returned: 'RR-001 Hem Belt photographed at night on a London kerb with direct flash.',
    },
  },
  {
    no: 'RR-002',
    slug: 'rr-002',
    name: 'Inside-Out Five Pocket',
    type: 'Trouser',
    status: 'returned',
    edition: { size: 1, remaining: 0 },
    price: null,
    firstLife: ["1 × Levi's 501", "1 × Levi's 550"],
    garments: 2,
    found: { place: 'Walthamstow, E17', date: '04.2025' },
    panels: 11,
    hours: 19,
    started: '28.04.2025',
    finished: '09.05.2025',
    returned: { date: '05.2025', by: 'Ruth, Deptford' },
    fit: 'W31 L30',
    material: '100% cotton denim',
    description:
      'Two pairs opened along every seam and rebuilt with the reverse of the cloth facing out. The pocket bags, darns and a previous owner’s hem are all visible from the outside.',
    note: 'You can see every repair the last owner made. That was the point.',
    images: { front: 'products/rr-002-front', returned: 'street/rr-002-returned' },
    alt: {
      front: 'RR-002 trousers hung on a plaster wall, panels from two pairs of jeans in two washes.',
      returned: 'RR-002 trousers on a London stock-brick wall at night, lit by direct flash.',
    },
  },
  {
    no: 'RR-003',
    slug: 'rr-003',
    name: 'Waistband Bag',
    type: 'Bag',
    status: 'returned',
    edition: { size: 1, remaining: 0 },
    price: null,
    firstLife: ['7 × waistbands, assorted'],
    garments: 7,
    found: { place: 'The pile, E17', date: '05.2025' },
    panels: 7,
    hours: 11,
    started: '20.05.2025',
    finished: '24.05.2025',
    returned: { date: '06.2025', by: 'Mira, Kentish Town' },
    fit: '34 × 29 cm',
    material: '100% cotton denim, steel shank buttons',
    description:
      'Seven waistbands stacked and joined edge to edge. Every button and belt loop is left in place, which is why no two rows line up.',
    note: 'Seven waistbands, seven buttons, none of them the same.',
    images: { front: 'products/rr-003-front', returned: 'street/rr-003-returned' },
    alt: {
      front: 'RR-003 Waistband Bag: seven denim waistbands stacked into a bag, buttons still attached.',
      returned: 'RR-003 bag on a wet London kerb at night beside double yellow lines.',
    },
  },
  {
    no: 'RR-004',
    slug: 'rr-004',
    name: 'Patch Chore Coat',
    type: 'Coat',
    status: 'returned',
    edition: { size: 1, remaining: 0 },
    price: null,
    firstLife: ['3 × Lee 200', '1 × Wrangler 124MJ'],
    garments: 4,
    found: { place: 'Hackney Wick, E9', date: '06.2025' },
    panels: 24,
    hours: 41,
    attempts: '2 (collar)',
    started: '01.07.2025',
    finished: '30.07.2025',
    returned: { date: '08.2025', by: 'Kwame, Tottenham' },
    fit: 'L',
    material: '100% cotton denim',
    description:
      'A long chore coat from three pairs of Lee 200s and a Wrangler jacket. The jacket’s chest pockets moved down to the hip.',
    note: 'The pockets are from the Wrangler. I moved them down to where hands actually go.',
    images: { front: 'products/rr-004-front', returned: 'street/rr-004-returned' },
    alt: {
      front: 'RR-004 Patch Chore Coat hung on a plaster wall, twenty-four panels in four washes.',
      returned: 'The back of RR-004 at night, direct flash, street lights out of focus behind.',
    },
  },
  {
    no: 'RR-005',
    slug: 'rr-005',
    name: 'Yoke Skirt',
    type: 'Skirt',
    status: 'returned',
    edition: { size: 1, remaining: 0 },
    price: null,
    firstLife: ["2 × Levi's 517"],
    garments: 2,
    found: { place: 'Brick Lane, E1', date: '07.2025' },
    panels: 10,
    hours: 14,
    started: '11.08.2025',
    finished: '19.08.2025',
    returned: { date: '08.2025', by: 'Ines, Bermondsey' },
    fit: 'W28',
    material: '100% cotton denim',
    description: 'Two pairs of bootcut 517s split at the yoke and re-cut as an A-line skirt. The original back yoke stays at the waist.',
    note: 'The flare went. The yoke stayed.',
    images: { front: 'products/rr-005-front', returned: 'street/rr-005-returned' },
    alt: {
      front: 'RR-005 Yoke Skirt laid flat on concrete under direct flash.',
      returned: 'RR-005 skirt on a brick wall at night.',
    },
  },
  {
    no: 'RR-006',
    slug: 'rr-006',
    name: 'Back Pocket Gilet',
    type: 'Gilet',
    status: 'returned',
    edition: { size: 1, remaining: 0 },
    price: null,
    firstLife: ["3 × Levi's 501", '9 × back pockets'],
    garments: 3,
    found: { place: 'Walthamstow, E17', date: '08.2025' },
    panels: 14,
    hours: 27,
    started: '01.09.2025',
    finished: '22.09.2025',
    returned: { date: '10.2025', by: 'Theo, Walthamstow' },
    fit: 'M',
    material: '100% cotton denim',
    description: 'A sleeveless trucker shape with nine back pockets set into the body. Three still carry the outline of a wallet.',
    note: 'Nine back pockets. You can still see the wallet on three of them.',
    images: { front: 'products/rr-006-front', returned: 'street/rr-006-returned' },
    alt: {
      front: 'RR-006 Back Pocket Gilet hung on a plaster wall.',
      returned: 'The back of RR-006 in a crowd at night, direct flash.',
    },
  },
  {
    no: 'RR-007',
    slug: 'rr-007',
    name: 'Selvedge Edge Shirt',
    type: 'Shirt',
    status: 'available',
    edition: { size: 1, remaining: 1 },
    price: 520, // PLACEHOLDER price
    firstLife: ['2 × selvedge jeans, maker unknown'],
    garments: 2,
    found: { place: 'Camden, NW1', date: '10.2025' },
    panels: 14,
    hours: 24,
    started: '03.11.2025',
    finished: '28.11.2025',
    fit: 'M–L',
    material: '100% cotton selvedge denim, 13 oz',
    description:
      'A long shirt from two pairs of Japanese selvedge jeans with the labels cut out years before they reached the pile. The selvedge ID runs down the placket and both cuffs. Square body, dropped shoulder.',
    note: 'Two pairs gave me just enough selvedge for both cuffs, with nothing left over. I measured it four times before cutting.',
    images: {
      front: 'products/rr-007-front',
      back: 'products/rr-007-back',
      detail: 'products/rr-007-detail',
      returned: 'street/rr-007-returned',
    },
    alt: {
      front: 'RR-007 Selvedge Edge Shirt laid flat on concrete, direct flash.',
      back: 'RR-007 from the back, showing the yoke and patch.',
      detail: 'Close-up of RR-007: two washes joined at a flat-felled seam with gold topstitch.',
      returned: 'RR-007 worn at night, photographed from behind with direct flash.',
    },
  },
  {
    no: 'RR-008',
    slug: 'rr-008',
    name: 'Carpenter, Two Washes',
    type: 'Trouser',
    status: 'available',
    edition: { size: 1, remaining: 1 },
    price: 640, // PLACEHOLDER price
    firstLife: ['1 × Carhartt carpenter jean', "1 × Levi's 501"],
    garments: 2,
    found: { place: 'Leyton, E10', date: '11.2025' },
    panels: 12,
    hours: 31,
    attempts: '2 (tool pocket)',
    started: '06.12.2025',
    finished: '14.01.2026',
    fit: 'W32 L31',
    material: '100% cotton denim',
    description:
      'One leg is a carpenter jean in a deep rinse, the other a 501 worn almost white at the thigh. The hammer loop and tool pocket stay where the first owner used them.',
    note: 'I left the hammer loop exactly where it was. Somebody used it for years.',
    images: {
      front: 'products/rr-008-front',
      back: 'products/rr-008-back',
      detail: 'products/rr-008-detail',
      returned: 'street/rr-008-returned',
    },
    alt: {
      front: 'RR-008 carpenter trousers hung on a plaster wall, one leg dark, one leg light.',
      back: 'RR-008 from the back, laid flat on concrete.',
      detail: 'Close-up of RR-008 where the two washes meet.',
      returned: 'RR-008 on a London brick wall at night, direct flash.',
    },
  },
  {
    no: 'RR-009',
    slug: 'rr-009',
    name: 'Panel Overshirt',
    type: 'Overshirt',
    status: 'returned',
    edition: { size: 1, remaining: 0 },
    price: null,
    firstLife: ["4 × Levi's 505"],
    garments: 4,
    found: { place: 'Walthamstow, E17', date: '10.2025' },
    panels: 20,
    hours: 33,
    started: '19.01.2026',
    finished: '16.02.2026',
    returned: { date: '03.2026', by: 'Sol, Hackney Wick' },
    fit: 'L',
    material: '100% cotton denim',
    description: 'Four pairs of 505s that left the factory in the same wash and came back in four different ones.',
    note: 'All the same wash once. All different now.',
    images: { front: 'products/rr-009-front', returned: 'street/rr-009-returned' },
    alt: {
      front: 'RR-009 Panel Overshirt laid flat on concrete under direct flash.',
      returned: 'The back of RR-009 at night in a crowd.',
    },
  },
  {
    no: 'RR-010',
    slug: 'rr-010',
    name: 'Reversed Wide Leg',
    type: 'Trouser',
    status: 'available',
    edition: { size: 1, remaining: 1 },
    price: 560, // PLACEHOLDER price
    firstLife: ["2 × Levi's 501", "1 × Levi's 517"],
    garments: 3,
    found: { place: 'Deptford, SE8', date: '12.2025' },
    panels: 9,
    hours: 26,
    started: '23.02.2026',
    finished: '17.03.2026',
    fit: 'W30 L32, wide',
    material: '100% cotton denim',
    description:
      'Cut wide and straight from three pairs, with the face of the cloth turned to the inside. The original wash only shows at the seams and the turn-up.',
    note: 'Cut inside out. The wash shows through at the seams, which is the only place I wanted it.',
    images: {
      front: 'products/rr-010-front',
      back: 'products/rr-010-back',
      detail: 'products/rr-010-detail',
      returned: 'street/rr-010-returned',
    },
    alt: {
      front: 'RR-010 Reversed Wide Leg hung on a plaster wall.',
      back: 'RR-010 from the back on concrete.',
      detail: 'Close-up of a seam on RR-010.',
      returned: 'RR-010 on a London brick wall at night.',
    },
  },
  {
    no: 'RR-011',
    slug: 'rr-011',
    name: 'Twelve Pocket Jacket',
    type: 'Jacket',
    status: 'returned',
    edition: { size: 1, remaining: 0 },
    price: null,
    firstLife: ['6 × unknown 1990s jeans'],
    garments: 6,
    found: { place: 'Walthamstow, E17', date: '11.2025' },
    panels: 31,
    hours: 51,
    attempts: '2 (back)',
    started: '05.01.2026',
    finished: '23.02.2026',
    returned: { date: '03.2026', by: 'Priya, Brixton' },
    fit: 'M',
    material: '100% cotton denim',
    description: 'Six pairs with no labels left between them. Twelve pockets kept whole, four of them still working.',
    note: 'No labels left in any of them. I kept every back pocket I could, which is where the twelve came from.',
    images: {
      front: 'products/rr-011-front',
      back: 'products/rr-011-back',
      detail: 'products/rr-011-detail',
      returned: 'street/rr-011-returned',
    },
    alt: {
      front: 'RR-011 Twelve Pocket Jacket laid flat on concrete.',
      back: 'The back of RR-011.',
      detail: 'Close-up of a pocket ghost on RR-011.',
      returned: 'RR-011 worn at night, direct flash.',
    },
  },
  {
    no: 'RR-012',
    slug: 'rr-012',
    name: 'Offcut Tote',
    type: 'Bag',
    status: 'returned',
    edition: { size: 1, remaining: 0 },
    price: null,
    firstLife: ['RR-009 – RR-011 offcuts'],
    garments: 3,
    found: { place: 'The bench', date: '02.2026' },
    panels: 9,
    hours: 9,
    started: '26.02.2026',
    finished: '01.03.2026',
    returned: { date: '03.2026', by: 'Joe, E8' },
    fit: '44 × 44 cm',
    material: '100% cotton denim',
    description: 'Made from what was left on the floor after RR-009 to RR-011. Nine panels, every one smaller than a hand.',
    note: 'Offcuts from three pieces. Nothing in it is bigger than my hand.',
    images: { front: 'products/rr-012-front', returned: 'street/rr-012-returned' },
    alt: {
      front: 'RR-012 Offcut Tote hung on a plaster wall.',
      returned: 'RR-012 on a London kerb at night.',
    },
  },
  {
    no: 'RR-013',
    slug: 'rr-013',
    name: 'Reversed Yoke Shirt',
    type: 'Shirt',
    status: 'returned',
    edition: { size: 1, remaining: 0 },
    price: null,
    firstLife: ["2 × Levi's 506"],
    garments: 2,
    found: { place: 'Peckham, SE15', date: '01.2026' },
    panels: 12,
    hours: 22,
    started: '02.03.2026',
    finished: '25.03.2026',
    returned: { date: '04.2026', by: 'Ama, Peckham' },
    fit: 'S–M',
    material: '100% cotton denim',
    description: 'Two 506 jackets taken apart and rebuilt as a shirt with the back yoke turned upside down.',
    note: 'Both jackets had the same repair on the yoke, done by different people. I turned the yoke over so you can see both.',
    images: {
      front: 'products/rr-013-front',
      back: 'products/rr-013-back',
      detail: 'products/rr-013-detail',
      returned: 'street/rr-013-returned',
    },
    alt: {
      front: 'RR-013 Reversed Yoke Shirt laid flat on concrete.',
      back: 'The back of RR-013 showing the reversed yoke.',
      detail: 'Close-up of the yoke seam on RR-013.',
      returned: 'RR-013 worn by Ama in Peckham, photographed from behind at night with flash.',
    },
  },
  {
    no: 'RR-014',
    slug: 'rr-014',
    name: 'Panel Trucker',
    type: 'Jacket',
    status: 'available',
    edition: { size: 1, remaining: 1 },
    price: 1150, // PLACEHOLDER price
    firstLife: ["4 × Levi's 501", '1 × Lee 101J'],
    garments: 5,
    found: { place: 'Walthamstow, E17', date: '03.2026' },
    panels: 23,
    hours: 38,
    attempts: '3 (L. sleeve)',
    started: '11.03.2026',
    finished: '19.04.2026',
    fit: 'M–L',
    material: '100% cotton denim',
    description:
      'Built from five garments, the oldest a pair of 501s faded almost white at the knee. The body is cut so each panel keeps its original wear: a phone outline on the left hip, a hand-darned back pocket on the right shoulder. The original selvedge runs inside the front placket. Boxy, cropped at the hip.',
    note: 'The left sleeve took three attempts. The first two are still hanging on the wall.',
    images: {
      front: 'products/rr-014-front',
      back: 'products/rr-014-back',
      detail: 'products/rr-014-detail',
      returned: 'street/rr-014-returned',
    },
    alt: {
      front: 'RR-014 Panel Trucker hung on a plaster wall: twenty-three panels from five garments, gold topstitch.',
      back: 'RR-014 from the back, laid flat on concrete, tan leather patch at the hem.',
      detail: 'Close-up of RR-014: two first-life garments meeting at a flat-felled seam.',
      returned: 'RR-014 worn at night, photographed from behind with direct flash, street lights out of focus.',
    },
  },
  {
    no: 'RR-015',
    slug: 'rr-015',
    name: 'Split Leg Trouser',
    type: 'Trouser',
    status: 'in-work',
    edition: { size: 1, remaining: 0 },
    price: null,
    firstLife: ['3 × Wrangler 13MWZ'],
    garments: 3,
    found: { place: 'Tottenham, N17', date: '08.2026' },
    panels: 14,
    hours: null,
    started: '22.09.2026',
    fit: 'W32 L32',
    material: '100% cotton denim',
    description:
      'Three pairs of Wranglers, split down the outseam and rejoined so each leg carries two washes: deep at the front, nearly bleached behind. Wide, straight, with the original rivets moved to the side seam where they now hold the join.',
    note: 'The rivets are going on the side seam, where they hold the join. Day nine.',
    images: { front: 'products/rr-015-front', back: 'products/rr-015-back', detail: 'products/rr-015-detail' },
    alt: {
      front: 'RR-015 Split Leg Trouser, unfinished, hung on a plaster wall.',
      back: 'RR-015 from the back on concrete.',
      detail: 'Close-up of a seam on RR-015.',
    },
  },
  {
    no: 'RR-016',
    slug: 'rr-016',
    name: 'Waistband Belt',
    type: 'Belt',
    status: 'available',
    edition: { size: 8, remaining: 5 },
    price: 95, // PLACEHOLDER price
    firstLife: ["8 × Levi's 501 waistbands"],
    garments: 8,
    found: { place: 'The pile, E17', date: '2025–2026' },
    panels: 8,
    hours: 4,
    started: '03.08.2026',
    finished: '21.08.2026',
    fit: 'One size, 80–100 cm',
    material: '100% cotton denim, original shank button',
    description:
      'An edition of eight. Each belt is one 501 waistband, closed with its own original button. Every one is a different wash, so the record card tells you which pair yours came from.',
    note: 'Eight waistbands from the pile that were too good to throw out. The buttons don’t match. They aren’t meant to.',
    images: {
      front: 'products/rr-016-front',
      back: 'products/rr-016-back',
      detail: 'products/rr-016-detail',
      returned: 'street/rr-016-returned',
    },
    alt: {
      front: 'RR-016 Waistband Belt hung on a plaster wall.',
      back: 'RR-016 laid flat on concrete, tan patch at one end.',
      detail: 'Close-up of RR-016 showing the topstitch.',
      returned: 'RR-016 on a London kerb at night.',
    },
  },
];

export default pieces;

export const bySlug = (slug: string) => pieces.find((p) => p.slug === slug);

/** Newest first — the order the archive is read in. */
export const archiveOrder = () => [...pieces].reverse();

export const available = () => archiveOrder().filter((p) => p.status === 'available');

export const inWork = () => pieces.find((p) => p.status === 'in-work');

export const totals = () => ({
  pieces: pieces.length,
  hours: pieces.reduce((n, p) => n + (p.hours ?? 0), 0),
  garments: pieces.reduce((n, p) => n + p.garments, 0),
  returned: pieces.filter((p) => p.status === 'returned').length,
});

export const statusLabel: Record<Status, string> = {
  available: 'Available',
  'in-work': 'In work',
  returned: 'Returned',
};

export const formatPrice = (n: number | null) =>
  n === null ? '—' : new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', maximumFractionDigits: 0 }).format(n);

export const editionLabel = (p: Piece) => (p.edition.size === 1 ? '1/1' : `ED. ${p.edition.size}`);

export const garmentsLabel = (p: Piece) => `${p.garments} ${p.garments === 1 ? 'garment' : 'garments'} → 1 object`;
