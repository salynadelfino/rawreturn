// @ts-check
import { defineConfig } from 'astro/config';

export default defineConfig({
  // PLACEHOLDER: set to the live domain before launch (used for canonical URLs and OG tags).
  site: 'https://rawreturn.co.uk',
  trailingSlash: 'ignore',
  prefetch: { prefetchAll: true, defaultStrategy: 'hover' },
  image: { responsiveStyles: false },
  // class strategy lets page styles reach the `class` prop forwarded by components
  scopedStyleStrategy: 'class',
});
