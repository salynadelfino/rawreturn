/**
 * Notes — ongoing documentation of the house, organised as the series in the
 * brand guideline (§14). Not blog categories: each series is a habit.
 *
 * PLACEHOLDER entries written in the founder's voice to show the format.
 * Replace with real entries; keep them specific, dated and short.
 */
export type Series = 'Bench Notes' | 'Failed' | 'The Pile' | 'Unpicked' | 'In Work' | 'Returned';

export const series: Record<Series, string> = {
  'The Pile': 'Sourcing. What was found, what was kept and why.',
  Unpicked: 'One garment taken apart, flat-laid as panels. The raw material, catalogued.',
  'In Work': 'The current piece on the bench, day by day.',
  Failed: 'An attempt that didn’t work, and what it taught.',
  'Bench Notes': 'Pattern pieces, sketchbook pages, decisions.',
  Returned: 'The finished piece on its wearer, on the street.',
};

export interface Note {
  slug: string;
  series: Series;
  title: string;
  date: string; // DD.MM.YYYY
  piece?: string; // RR number
  image: string;
  alt: string;
  dek: string;
  body: string[];
}

const notes: Note[] = [
  {
    slug: 'split-leg-day-nine',
    series: 'In Work',
    title: 'Day nine on the split leg',
    date: '30.09.2026',
    piece: 'RR-015',
    image: 'process/05-rebuild',
    alt: 'Pinned denim panels on the cutting table beside shears and a cloth tape measure.',
    dek: 'Three pairs of Wranglers, two washes per leg. The rivets are moving to the side seam.',
    body: [
      'Both legs are cut. Each one is two halves from different pairs: the front from the darkest of the three, the back from one that has been washed so many times it is closer to grey than blue.',
      'The problem is the outseam. A 13MWZ has rivets at the pocket corners, and I didn’t want to lose them. So they are going on the side seam, where the two halves meet. They’ll do the job a rivet was made for: hold a join that takes strain.',
      'Hours so far are on the record. I’ll post the total when it is finished.',
    ],
  },
  {
    slug: 'the-left-sleeve',
    series: 'Failed',
    title: 'The left sleeve, three times',
    date: '02.04.2026',
    piece: 'RR-014',
    image: 'process/failed-sleeves',
    alt: 'Three denim sleeves hanging from bulldog clips on a plaster wall, each with a paper tag: attempt 1, 2 and 3.',
    dek: 'The first was too short. The second had the pitch wrong. The third is on the jacket.',
    body: [
      'The first attempt came out two centimetres short because I lost length in the felled seam I hadn’t allowed for. That is the kind of mistake you only make once, and then make again on the next piece.',
      'The second was the right length but set at the wrong pitch, so the sleeve twisted forward when the arm hung down. On a hanger you couldn’t see it. On a person you couldn’t miss it.',
      'The third is on RR-014. The first two are still hanging on the wall. I’m keeping them, partly as a reminder and partly because there is enough denim in them for something else.',
    ],
  },
  {
    slug: 'two-hundred-pairs',
    series: 'The Pile',
    title: 'Two hundred pairs. Eleven kept.',
    date: '14.03.2026',
    image: 'workshop/the-pile',
    alt: 'A pile of used denim on a concrete floor.',
    dek: 'Walthamstow, a Saturday morning. What made the cut and why.',
    body: [
      'Most of what is in a pile like this is fine and nothing more: modern stretch denim, thin, faded by a machine rather than a person. It goes back.',
      'What I keep is heavy, 100% cotton, and worn by somebody. Honest fading at the knee and the thigh. Repairs done by hand. A phone outline on a back pocket. Wear I couldn’t fake if I tried — and wouldn’t want to.',
      'Eleven out of two hundred. Four of them became RR-014.',
    ],
  },
  {
    slug: 'one-506-eighteen-panels',
    series: 'Unpicked',
    title: 'One 506, eighteen panels',
    date: '20.02.2026',
    piece: 'RR-013',
    image: 'process/03-study',
    alt: 'Panels from an unpicked jacket laid on concrete, each tagged with a number.',
    dek: 'Eighteen panels, two rivets, one pocket somebody repaired by hand years ago.',
    body: [
      'A 506 comes apart into eighteen pieces if you are patient with it. Eighteen panels, two rivets, and one repaired pocket somebody did by hand a long time ago, in a thread that doesn’t match anything.',
      'Keeping that pocket. It went into RR-013, upside down, next to a repair somebody else made on the other jacket.',
    ],
  },
  {
    slug: 'notches',
    series: 'Bench Notes',
    title: 'Notches, and why the pattern says CUT 3',
    date: '18.03.2026',
    piece: 'RR-014',
    image: 'workshop/chalk-on-indigo',
    alt: 'Chalk lines, notches and a cross marked on raw indigo denim next to a steel ruler.',
    dek: 'Every pattern piece carries its piece number and how many times it has been cut.',
    body: [
      'Each pattern piece is stamped with the piece number, the part and a cut count. The count goes up every time I cut from it. When it gets to three, I stop and ask whether the pattern is wrong rather than the cloth.',
      'The notches on the edge are where two pieces must meet. On a reconstruction they matter more than usual, because the two pieces were never meant to be together.',
    ],
  },
  {
    slug: 'ama-peckham',
    series: 'Returned',
    title: 'RR-013, Peckham',
    date: '11.04.2026',
    piece: 'RR-013',
    image: 'street/rr-013-returned',
    alt: 'The back of a denim shirt at night, lit by direct flash, street lights out of focus.',
    dek: 'Out of the workshop, back on the street. Ama, Peckham, Saturday night.',
    body: [
      'Out of the workshop and back on the street, about a mile from where one of the two 506s was found.',
      'Ama says the reversed yoke gets more questions than anything else in the wardrobe. That is the repair doing its job.',
    ],
  },
];

export default notes;
export const noteBySlug = (s: string) => notes.find((n) => n.slug === s);
