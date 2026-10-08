/**
 * The bag. Client-side state in localStorage; prices and limits come from the
 * catalogue the drawer ships (only AVAILABLE pieces can be added).
 *
 * PLACEHOLDER: checkout is a local summary page. Connect a payment provider
 * (Shopify Storefront cart, Stripe Checkout…) in /checkout before launch.
 */
type Item = { slug: string; no: string; name: string; price: number; max: number; edition: string; thumb: string };
type Line = { slug: string; qty: number };

const KEY = 'rr-bag-v1';
const fmt = new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', maximumFractionDigits: 0 });

let catalogue: Record<string, Item> = {};
let lastFocus: HTMLElement | null = null;

function loadCatalogue() {
  const el = document.querySelector('[data-bag-catalogue]');
  if (!el) return;
  try {
    const list = JSON.parse(el.textContent || '[]') as Item[];
    catalogue = Object.fromEntries(list.map((i) => [i.slug, i]));
  } catch {
    catalogue = {};
  }
}

function read(): Line[] {
  try {
    const raw = JSON.parse(localStorage.getItem(KEY) || '[]') as Line[];
    return raw.filter((l) => catalogue[l.slug]).map((l) => ({ ...l, qty: Math.min(l.qty, catalogue[l.slug].max) }));
  } catch {
    return [];
  }
}
function write(lines: Line[]) {
  try {
    localStorage.setItem(KEY, JSON.stringify(lines));
  } catch {
    /* private mode: the bag lasts for this page view */
  }
  memory = lines;
  render();
}
let memory: Line[] = [];
const lines = () => (memory.length ? memory : (memory = read()));

export const bag = {
  add(slug: string, qty = 1) {
    const item = catalogue[slug];
    if (!item) return;
    const ls = [...lines()];
    const ex = ls.find((l) => l.slug === slug);
    if (ex) ex.qty = Math.min(item.max, ex.qty + qty);
    else ls.push({ slug, qty: Math.min(item.max, qty) });
    write(ls);
    announce(`${item.no} ${item.name} added to the bag.`);
  },
  set(slug: string, qty: number) {
    const item = catalogue[slug];
    if (!item) return;
    write(lines().map((l) => (l.slug === slug ? { ...l, qty: Math.max(1, Math.min(item.max, qty)) } : l)));
  },
  remove(slug: string) {
    const item = catalogue[slug];
    write(lines().filter((l) => l.slug !== slug));
    if (item) announce(`${item.no} removed.`);
  },
  count: () => lines().reduce((n, l) => n + l.qty, 0),
  subtotal: () => lines().reduce((n, l) => n + l.qty * (catalogue[l.slug]?.price ?? 0), 0),
  lines,
  catalogue: () => catalogue,
};
(window as unknown as { rrBag: typeof bag }).rrBag = bag;

function announce(msg: string) {
  const el = document.querySelector<HTMLElement>('[data-bag-announce]');
  if (el) el.textContent = msg;
}

function render() {
  const n = bag.count();
  document.querySelectorAll('[data-bag-count]').forEach((el) => (el.textContent = String(n)));
  document.querySelectorAll('[data-bag-count-label]').forEach((el) => (el.textContent = `(${n})`));
  const root = document.querySelector<HTMLElement>('[data-bag-root]');
  root?.toggleAttribute('data-empty', n === 0);
  const sub = document.querySelector('[data-bag-subtotal]');
  if (sub) sub.textContent = fmt.format(bag.subtotal());

  const list = document.querySelector<HTMLElement>('[data-bag-lines]');
  const tpl = document.querySelector<HTMLTemplateElement>('[data-bag-line-tpl]');
  if (list && tpl) {
    list.replaceChildren(
      ...lines().map((l) => {
        const item = catalogue[l.slug];
        const li = tpl.content.firstElementChild!.cloneNode(true) as HTMLElement;
        li.dataset.slug = l.slug;
        const q = <T extends Element = HTMLElement>(s: string) => li.querySelector(s) as T;
        q<HTMLAnchorElement>('[data-l-link]').href = `/archive/${l.slug}`;
        const img = q<HTMLImageElement>('[data-l-img]');
        img.src = item.thumb;
        img.alt = `${item.no} ${item.name}`;
        q('[data-l-no]').textContent = item.no;
        q('[data-l-ed]').textContent = item.edition;
        q('[data-l-name]').textContent = item.name;
        q('[data-l-price]').textContent = fmt.format(item.price * l.qty);
        q('[data-l-count]').textContent = String(l.qty);
        const qty = q('[data-l-qty]');
        if (item.max <= 1) qty.toggleAttribute('data-fixed', true);
        q<HTMLButtonElement>('[data-l-dec]').disabled = l.qty <= 1;
        q<HTMLButtonElement>('[data-l-inc]').disabled = l.qty >= item.max;
        q<HTMLButtonElement>('[data-l-remove]').setAttribute('aria-label', `Remove ${item.no} ${item.name}`);
        return li;
      }),
    );
  }

  // purchase modules on the page reflect what is already in the bag
  document.querySelectorAll<HTMLElement>('[data-purchase]').forEach((mod) => {
    const slug = mod.dataset.purchase!;
    const line = lines().find((l) => l.slug === slug);
    const item = catalogue[slug];
    const full = !!line && !!item && line.qty >= item.max;
    mod.toggleAttribute('data-in-bag', !!line);
    const btn = mod.querySelector<HTMLButtonElement>('[data-add]');
    const label = btn?.querySelector('.btn-label');
    if (btn && label) {
      btn.disabled = full;
      label.textContent = full ? (item.max === 1 ? 'In your bag' : 'Edition limit in bag') : 'Add to bag';
    }
  });
}

/* ───────────────────────── drawer */
function drawer() {
  return {
    root: document.querySelector<HTMLElement>('[data-bag-root]'),
    el: document.querySelector<HTMLElement>('[data-bag]'),
  };
}
function open() {
  const { root, el } = drawer();
  if (!root || !el) return;
  lastFocus = document.activeElement as HTMLElement;
  el.hidden = false;
  requestAnimationFrame(() => {
    root.classList.add('is-open');
    el.focus();
  });
  document.querySelectorAll<HTMLElement>('main, footer.site-footer, [data-header]').forEach((m) => (m.inert = true));
  document.documentElement.style.overflow = 'hidden';
}
function close() {
  const { root, el } = drawer();
  if (!root || !el || !root.classList.contains('is-open')) return;
  root.classList.remove('is-open');
  document.querySelectorAll<HTMLElement>('main, footer.site-footer, [data-header]').forEach((m) => (m.inert = false));
  document.documentElement.style.overflow = '';
  setTimeout(() => {
    if (!root.classList.contains('is-open')) el.hidden = true;
  }, 600);
  lastFocus?.focus?.();
}

document.addEventListener('click', (e) => {
  const t = e.target as HTMLElement;
  if (t.closest('[data-bag-open]')) {
    e.preventDefault();
    open();
    return;
  }
  if (t.closest('[data-bag-close]')) {
    close();
    return;
  }
  const add = t.closest<HTMLElement>('[data-add]');
  if (add) {
    const mod = add.closest<HTMLElement>('[data-purchase]');
    const slug = mod?.dataset.purchase;
    if (!slug) return;
    const qtyInput = mod!.querySelector<HTMLSelectElement>('[data-qty]');
    bag.add(slug, qtyInput ? Number(qtyInput.value) : 1);
    open();
    return;
  }
  const line = t.closest<HTMLElement>('[data-bag-lines] li');
  if (line) {
    const slug = line.dataset.slug!;
    const cur = lines().find((l) => l.slug === slug)?.qty ?? 1;
    if (t.closest('[data-l-inc]')) bag.set(slug, cur + 1);
    else if (t.closest('[data-l-dec]')) bag.set(slug, cur - 1);
    else if (t.closest('[data-l-remove]')) bag.remove(slug);
  }
  if (t.closest('[data-bag-checkout]')) close();
});

document.addEventListener('keydown', (e) => {
  const { root, el } = drawer();
  if (!root?.classList.contains('is-open') || !el) return;
  if (e.key === 'Escape') {
    close();
    return;
  }
  if (e.key === 'Tab') {
    const f = [...el.querySelectorAll<HTMLElement>('a[href], button:not([disabled]), input, select')].filter(
      (x) => x.offsetParent !== null,
    );
    if (!f.length) return;
    const first = f[0],
      last = f[f.length - 1];
    if (e.shiftKey && (document.activeElement === first || document.activeElement === el)) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }
});

window.addEventListener('storage', (e) => {
  if (e.key === KEY) {
    memory = read();
    render();
  }
});

document.addEventListener('astro:page-load', () => {
  loadCatalogue();
  memory = read();
  render();
  document.dispatchEvent(new CustomEvent('rr:bag-ready'));
});
document.addEventListener('astro:before-swap', close);
