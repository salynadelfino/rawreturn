/**
 * Image registry. Every photograph on the site is looked up by key, e.g.
 * 'products/rr-014-front' → src/assets/images/products/rr-014-front.jpg
 *
 * To replace placeholder photography: drop the real file in at the same path
 * (same name, .jpg) and rebuild. Astro generates responsive WebP sizes.
 * See src/assets/images/README.md for the full shot list.
 */
import type { ImageMetadata } from 'astro';

const files = import.meta.glob<{ default: ImageMetadata }>('/src/assets/images/**/*.{jpg,jpeg,png,webp}', {
  eager: true,
});

const registry = new Map<string, ImageMetadata>();
for (const [path, mod] of Object.entries(files)) {
  const key = path.replace('/src/assets/images/', '').replace(/\.(jpe?g|png|webp)$/, '');
  registry.set(key, mod.default);
}

export const getImage = (key: string | undefined) => (key ? registry.get(key) : undefined);
export const hasImage = (key: string | undefined) => !!key && registry.has(key);
