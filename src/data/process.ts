/**
 * The method, in the order it happens. Founder commentary is first person.
 * PLACEHOLDER copy written to the guideline's voice — the founder should read
 * every line and replace anything that isn't exactly how they work.
 */
export interface Stage {
  n: string;
  name: string;
  image: string;
  alt: string;
  note: string; // founder, first person
  facts: Array<[string, string]>;
  caption: string;
}

const stages: Stage[] = [
  {
    n: '01',
    name: 'Find',
    image: 'process/01-find',
    alt: 'A pile of used jeans and jackets on a concrete floor, different washes and weights.',
    note: 'I go through the pile one pair at a time. Two hundred pairs, eleven kept. I look for honest fading, heavy weight, and wear I couldn’t fake if I tried.',
    facts: [
      ['Sourced', 'Around London'],
      ['Kept', '≈ 1 in 18'],
      ['Looking for', 'Weight, fade, repairs'],
    ],
    caption: 'The pile, Walthamstow E17',
  },
  {
    n: '02',
    name: 'Unpick',
    image: 'process/02-unpick',
    alt: 'Denim panels from one pair of jeans, unpicked along every seam, stitch holes visible.',
    note: 'Every seam comes apart by hand. It’s slower than cutting, but cutting throws away the seam allowance, and the seam allowance is where the darkest indigo is.',
    facts: [
      ['Tool', 'Seam ripper, no blade'],
      ['One pair', '≈ 3 hrs'],
      ['Panels', '14–18 per pair'],
    ],
    caption: 'Unpicked: 1 × Levi’s 501',
  },
  {
    n: '03',
    name: 'Study',
    image: 'process/03-study',
    alt: 'Unpicked denim panels laid out on concrete in a grid, each with a numbered paper tag.',
    note: 'Everything gets laid out and numbered before anything is cut. I want to know where the fades are and which way they run before I decide what they become.',
    facts: [
      ['Each panel', 'Tagged & numbered'],
      ['Recorded', 'Wash, weight, wear'],
      ['Washed', '30°, inside out'],
    ],
    caption: 'Panels 01.01 → 01.11',
  },
  {
    n: '04',
    name: 'Cut',
    image: 'process/04-cut',
    alt: 'Tailor’s chalk lines and notches on raw indigo denim beside a steel ruler and shears.',
    note: 'Pattern pieces go down so the wear lands where I want it — the knee fade on a shoulder, a phone outline on a hip. Measure twice, chalk, cut once.',
    facts: [
      ['Marked', 'Tailor’s chalk'],
      ['Seam allowance', '1 cm, felled'],
      ['Waste', 'Kept for offcut pieces'],
    ],
    caption: 'Chalk on raw indigo',
  },
  {
    n: '05',
    name: 'Rebuild',
    image: 'process/05-rebuild',
    alt: 'A jacket in progress on the cutting table: pinned denim panels, pattern paper, shears, tape measure.',
    note: 'Panels are pinned, tried, unpinned, tried again. Most of the hours go here. When a part doesn’t work it comes off and goes on the wall.',
    facts: [
      ['Seams', 'Flat-felled, 2 rows'],
      ['Thread', 'Cotton-wrapped poly, gold'],
      ['Attempts', 'Logged on the record'],
    ],
    caption: 'RR-014 on the bench',
  },
  {
    n: '06',
    name: 'Record',
    image: 'process/06-record',
    alt: 'A printed record card for RR-014 listing first life and second life, laid on raw denim with an offcut swatch.',
    note: 'Every piece gets a number that never repeats, and a record of exactly how it was made. The record goes in the box and on the archive, permanently.',
    facts: [
      ['Number', 'RR-001 onwards'],
      ['Record', 'First life / Second life'],
      ['In the box', 'Record, offcut card'],
    ],
    caption: 'Record of making, RR-014',
  },
  {
    n: '07',
    name: 'Return',
    image: 'process/07-return',
    alt: 'The back of a panelled denim jacket worn at night, lit by direct flash, street lights behind.',
    note: 'A piece is finished when somebody wears it outside. If it ever wears out, it can come back, and it gets rebuilt again.',
    facts: [
      ['Leaves', 'Grey board, tan tape'],
      ['Comes back', 'Any time'],
      ['Then', 'A new number'],
    ],
    caption: 'Returned — RR-014',
  },
];
export default stages;
