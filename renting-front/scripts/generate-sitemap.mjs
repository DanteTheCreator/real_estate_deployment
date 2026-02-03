import { writeFileSync, existsSync } from 'fs';
import { resolve } from 'path';

// Basic static routes; dynamic property pages could be augmented by fetching an API in future
const baseUrl = 'https://comfyrent.homes';
const staticRoutes = [
  '/',
  '/privacy-policy',
  '/terms-of-service',
  '/cookie-policy'
];

// Generate XML
const now = new Date().toISOString();
const urlSet = staticRoutes.map(r => `  <url>\n    <loc>${baseUrl}${r}</loc>\n    <lastmod>${now}</lastmod>\n    <changefreq>${r === '/' ? 'daily' : 'monthly'}</changefreq>\n    <priority>${r === '/' ? '1.0' : '0.5'}</priority>\n  </url>`).join('\n');

const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urlSet}\n</urlset>\n`;

const publicOut = resolve(process.cwd(), 'public', 'sitemap.xml');
writeFileSync(publicOut, xml, 'utf8');
let distOut;
// Also write into dist if it exists (when running in postbuild after Vite build)
const potentialDist = resolve(process.cwd(), 'dist');
if (existsSync(potentialDist)) {
  distOut = resolve(potentialDist, 'sitemap.xml');
  writeFileSync(distOut, xml, 'utf8');
}
console.log('Sitemap generated at', publicOut, distOut ? 'and ' + distOut : '');
