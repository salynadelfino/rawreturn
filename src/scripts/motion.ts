/**
 * Motion. Considered, never decorative: things arrive in reading order,
 * photographs open like a shutter, process sequences scroll as a contact sheet.
 * Everything here is skipped or flattened under prefers-reduced-motion.
 */
import Lenis from 'lenis';

const reduced = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const desktop = () => window.matchMedia('(min-width: 900px) and (pointer: fine)').matches;

let lenis: Lenis | null = null;
let teardown: Array<() => void> = [];

function onScroll(fn: () => void) {
  let ticking = false;
  const handler = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      ticking = false;
      fn();
    });
  };
  window.addEventListener('scroll', handler, { passive: true });
  window.addEventListener('resize', handler);
  teardown.push(() => {
    window.removeEventListener('scroll', handler);
    window.removeEventListener('resize', handler);
  });
  fn();
}

/* ───────────────────────── smooth scroll (once per session) */
function initLenis() {
  if (lenis || reduced() || !desktop()) return;
  lenis = new Lenis({ lerp: 0.12, smoothWheel: true });
  const raf = (t: number) => {
    lenis?.raf(t);
    requestAnimationFrame(raf);
  };
  requestAnimationFrame(raf);
}

/* ───────────────────────── reveals */
function initReveals() {
  const els = document.querySelectorAll<HTMLElement>('[data-reveal], [data-lines]');
  if (reduced() || !('IntersectionObserver' in window)) {
    els.forEach((el) => el.classList.add('is-in'));
    return;
  }
  // A masked element is fully clipped until revealed, and Chrome counts the
  // target's own clip-path — so watch its (unclipped) parent instead.
  const targets = new Map<Element, HTMLElement[]>();
  const io = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (!e.isIntersecting) continue;
        targets.get(e.target)?.forEach((el) => el.classList.add('is-in'));
        io.unobserve(e.target);
      }
    },
    { rootMargin: '0px 0px -6% 0px', threshold: 0.01 },
  );
  els.forEach((el) => {
    // anything already on the first screen arrives on load, in order
    const r = el.getBoundingClientRect();
    if (r.top < window.innerHeight && r.bottom > 0) {
      requestAnimationFrame(() => el.classList.add('is-in'));
      return;
    }
    const watch = el.dataset.reveal?.startsWith('mask') && el.parentElement ? el.parentElement : el;
    if (!targets.has(watch)) {
      targets.set(watch, []);
      io.observe(watch);
    }
    targets.get(watch)!.push(el);
  });
  teardown.push(() => io.disconnect());
}

/* ───────────────────────── parallax: [data-parallax="0.12"] */
function initParallax() {
  if (reduced() || !desktop()) return;
  const els = [...document.querySelectorAll<HTMLElement>('[data-parallax]')];
  if (!els.length) return;
  onScroll(() => {
    const vh = window.innerHeight;
    for (const el of els) {
      const r = el.parentElement!.getBoundingClientRect();
      if (r.bottom < -200 || r.top > vh + 200) continue;
      const f = parseFloat(el.dataset.parallax || '0.1');
      const off = (r.top + r.height / 2 - vh / 2) * -f;
      el.style.transform = `translate3d(0, ${off.toFixed(1)}px, 0) scale(${1 + f})`;
    }
  });
}

/* ───────────────────────── pinned horizontal sequence: [data-hscroll] */
function initHScroll() {
  const blocks = [...document.querySelectorAll<HTMLElement>('[data-hscroll]')];
  if (!blocks.length) return;
  const enabled = !reduced() && window.matchMedia('(min-width: 900px)').matches;
  for (const b of blocks) b.toggleAttribute('data-pinned', enabled);
  if (!enabled) return;
  const measure = () => {
    for (const b of blocks) {
      const track = b.querySelector<HTMLElement>('[data-hscroll-track]')!;
      const dist = Math.max(0, track.scrollWidth - window.innerWidth);
      b.style.height = `${window.innerHeight + dist}px`;
      b.dataset.dist = String(dist);
    }
  };
  measure();
  window.addEventListener('resize', measure);
  teardown.push(() => window.removeEventListener('resize', measure));
  onScroll(() => {
    for (const b of blocks) {
      const r = b.getBoundingClientRect();
      const dist = Number(b.dataset.dist || 0);
      const p = Math.min(1, Math.max(0, -r.top / Math.max(1, dist)));
      const track = b.querySelector<HTMLElement>('[data-hscroll-track]')!;
      track.style.transform = `translate3d(${(-p * dist).toFixed(1)}px, 0, 0)`;
      const bar = b.querySelector<HTMLElement>('[data-hscroll-progress]');
      if (bar) bar.style.transform = `scaleX(${p})`;
      const count = b.querySelector<HTMLElement>('[data-hscroll-count]');
      if (count) {
        const n = Number(count.dataset.total || 1);
        count.textContent = String(Math.min(n, Math.floor(p * n) + 1)).padStart(2, '0');
      }
    }
  });
}

/* ───────────────────────── header: hide on the way down, tone over dark sections, seam grows */
function initHeader() {
  const header = document.querySelector<HTMLElement>('[data-header]');
  if (!header) return;
  let last = window.scrollY;
  onScroll(() => {
    const y = window.scrollY;
    const menuOpen = header.hasAttribute('data-menu-open');
    if (!menuOpen) header.toggleAttribute('data-hidden', y > 160 && y > last + 2 && !reduced());
    if (y < last - 2 || y < 160) header.removeAttribute('data-hidden');
    last = y;
    const probe = 28;
    let dark = false;
    document.querySelectorAll<HTMLElement>('[data-tone="dark"]').forEach((s) => {
      const r = s.getBoundingClientRect();
      if (r.top <= probe && r.bottom >= probe) dark = true;
    });
    header.dataset.tone = dark ? 'dark' : 'light';
    const max = document.documentElement.scrollHeight - window.innerHeight;
    header.style.setProperty('--seam', String(0.35 + 0.65 * Math.min(1, y / Math.max(1, max))));
  });
}

/* ───────────────────────── mobile menu */
function initMenu() {
  const header = document.querySelector<HTMLElement>('[data-header]');
  const btn = header?.querySelector<HTMLButtonElement>('[data-menu-toggle]');
  const menu = header?.querySelector<HTMLElement>('[data-menu]');
  if (!header || !btn || !menu || btn.dataset.bound) return;
  btn.dataset.bound = '1';
  const main = () => document.querySelectorAll<HTMLElement>('main, footer.site-footer');
  const set = (open: boolean) => {
    btn.setAttribute('aria-expanded', String(open));
    header.toggleAttribute('data-menu-open', open);
    if (open) {
      menu.hidden = false;
      requestAnimationFrame(() => menu.classList.add('is-open'));
      main().forEach((m) => (m.inert = true));
      lenis?.stop();
      document.documentElement.style.overflow = 'hidden';
    } else {
      menu.classList.remove('is-open');
      main().forEach((m) => (m.inert = false));
      lenis?.start();
      document.documentElement.style.overflow = '';
      setTimeout(() => {
        if (!menu.classList.contains('is-open')) menu.hidden = true;
      }, 700);
    }
  };
  btn.addEventListener('click', () => set(btn.getAttribute('aria-expanded') !== 'true'));
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && btn.getAttribute('aria-expanded') === 'true') {
      set(false);
      btn.focus();
    }
  });
  document.addEventListener('astro:before-swap', () => set(false));
}

/* ───────────────────────── cursor label: [data-cursor="RR-014 →"] */
function initCursor() {
  const label = document.querySelector<HTMLElement>('[data-cursor-label]');
  if (!label || !desktop() || reduced()) return;
  let x = -100,
    y = -100,
    tx = -100,
    ty = -100,
    running = false;
  const loop = () => {
    x += (tx - x) * 0.25;
    y += (ty - y) * 0.25;
    label.style.transform = `translate3d(${x + 16}px, ${y + 18}px, 0)`;
    if (Math.abs(tx - x) + Math.abs(ty - y) > 0.5) requestAnimationFrame(loop);
    else running = false;
  };
  const move = (e: PointerEvent) => {
    tx = e.clientX;
    ty = e.clientY;
    if (!running) {
      running = true;
      requestAnimationFrame(loop);
    }
  };
  document.querySelectorAll<HTMLElement>('[data-cursor]').forEach((el) => {
    el.addEventListener('pointerenter', (e) => {
      label.textContent = el.dataset.cursor || '';
      x = tx = e.clientX;
      y = ty = e.clientY;
      label.classList.add('is-on');
    });
    el.addEventListener('pointerleave', () => label.classList.remove('is-on'));
    el.addEventListener('pointermove', move);
  });
  teardown.push(() => label.classList.remove('is-on'));
}

/* ───────────────────────── IN WORK: day count from the start date (a fact, not a fake ticker) */
function initInWork() {
  document.querySelectorAll<HTMLElement>('[data-day-since]').forEach((el) => {
    const [d, m, y] = (el.dataset.daySince || '').split('.').map(Number);
    if (!y) return;
    const start = new Date(y, m - 1, d);
    const days = Math.max(1, Math.floor((Date.now() - start.getTime()) / 86400000) + 1);
    el.textContent = `Day ${days}`;
  });
}

/* ───────────────────────── product gallery counter (mobile swipe) */
function initGalleries() {
  document.querySelectorAll<HTMLElement>('[data-gallery]').forEach((g) => {
    const track = g.querySelector<HTMLElement>('[data-gallery-track]');
    const count = g.querySelector<HTMLElement>('[data-gallery-count]');
    if (!track || !count) return;
    const update = () => {
      const i = Math.round(track.scrollLeft / Math.max(1, track.clientWidth));
      count.textContent = String(i + 1).padStart(2, '0');
    };
    track.addEventListener('scroll', update, { passive: true });
  });
}

/* ───────────────────────── newsletter (local confirmation until a provider is connected) */
function initNewsletter() {
  document.querySelectorAll<HTMLFormElement>('[data-newsletter]').forEach((f) => {
    if (f.dataset.bound) return;
    f.dataset.bound = '1';
    f.addEventListener('submit', (e) => {
      e.preventDefault();
      const input = f.querySelector('input')!;
      const msg = f.querySelector<HTMLElement>('[aria-live]')!;
      if (!input.checkValidity() || !input.value) {
        f.dataset.state = 'error';
        input.setAttribute('aria-invalid', 'true');
        msg.textContent = 'That address doesn’t look right.';
        input.focus();
        return;
      }
      f.dataset.state = 'ok';
      input.removeAttribute('aria-invalid');
      msg.textContent = 'Noted. The next one comes from the bench.';
      f.reset();
    });
  });
}

function init() {
  teardown.forEach((fn) => fn());
  teardown = [];
  initLenis();
  initReveals();
  initParallax();
  initHScroll();
  initHeader();
  initMenu();
  initCursor();
  initInWork();
  initGalleries();
  initNewsletter();
}

document.addEventListener('astro:page-load', init);
document.addEventListener('astro:after-swap', () => {
  lenis?.scrollTo(0, { immediate: true });
});
