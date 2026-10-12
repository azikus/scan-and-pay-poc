import { cp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, extname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

export const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
export const mime = { '.css': 'text/css', '.js': 'text/javascript', '.mjs': 'text/javascript', '.html': 'text/html', '.png': 'image/png', '.svg': 'image/svg+xml', '.ttf': 'font/ttf', '.json': 'application/json', '.txt': 'text/plain' };
const privateEdition = process.argv.includes('--private');
const out = resolve(root, privateEdition ? 'dist-private' : 'dist');
const manifest = JSON.parse(await readFile(resolve(root, 'assets/manifest.json'), 'utf8'));
const dependency = JSON.parse(await readFile(resolve(root, 'node_modules/reveal.js/package.json'), 'utf8'));
if (dependency.version !== '6.0.2') throw new Error('Install the pinned dependencies with npm ci.');
let html = await readFile(resolve(root, 'index.html'), 'utf8');
// Opt-in only. Never discover private files while building the repository edition.
if (privateEdition) {
  await readFile(resolve(root, 'private-assets/corpus-gallery.png'));
  html = html.replace(/<!-- PRIVATE_CORPUS_START -->[\s\S]*?<!-- PRIVATE_CORPUS_END -->/, '<img class="gallery" src="assets/corpus-gallery.png" alt="All 17 inputs in the reviewed comparison">');
}
await rm(out, { recursive: true, force: true });
await mkdir(resolve(out, 'assets'), { recursive: true });
await mkdir(resolve(out, 'vendor'), { recursive: true });
for (const { file } of manifest.assets) {
  if (!/^[\w.-]+$/.test(file)) throw new Error('Asset names must be plain filenames.');
  await cp(resolve(root, 'assets', file), resolve(out, 'assets', file));
}
if (privateEdition) await cp(resolve(root, 'private-assets/corpus-gallery.png'), resolve(out, 'assets/corpus-gallery.png'));
for (const file of ['deck.css', 'deck.js']) await cp(resolve(root, file), resolve(out, file));
for (const [from, to] of [['dist/reveal.css', 'reveal.css'], ['dist/reveal.js', 'reveal.js'], ['dist/plugin/notes.js', 'notes.js'], ['LICENSE', 'LICENSE']]) {
  await cp(resolve(root, 'node_modules/reveal.js', from), resolve(out, 'vendor', to));
}
await writeFile(resolve(out, 'index.html'), html);
const dataUrl = async (path) => `data:${mime[extname(path)] ?? 'application/octet-stream'};base64,${(await readFile(resolve(out, path))).toString('base64')}`;
let audience = html.replace(/<aside class="notes"[\s\S]*?<\/aside>/g, '').replace('<html lang="en">', '<html lang="en" data-audience="true">').replace('<button id="notes">', '<button id="notes" hidden>');
for (const file of ['vendor/reveal.css', 'deck.css']) {
  let css = await readFile(resolve(out, file), 'utf8');
  for (const match of [...css.matchAll(/url\((['"]?)(assets\/[^)'"\s]+)\1\)/g)]) css = css.replace(match[0], `url(${await dataUrl(match[2])})`);
  audience = audience.replace(`<link rel="stylesheet" href="${file}">`, `<style>${css}</style>`);
}
audience = audience.replace('<script src="vendor/notes.js"></script>', '');
for (const file of ['vendor/reveal.js', 'deck.js']) {
  const js = (await readFile(resolve(out, file), 'utf8')).replace(/<\/script/gi, '<\\/script');
  audience = audience.replace(`<script src="${file}"></script>`, `<script>${js}</script>`);
}
for (const match of [...audience.matchAll(/src="(assets\/[^"]+)"/g)]) audience = audience.replace(match[0], `src="${await dataUrl(match[1])}"`);
const licenses = await Promise.all(['vendor/LICENSE', 'assets/OFL.txt'].map(file => readFile(resolve(out, file), 'utf8')));
audience = audience.replace('</head>', `<!-- Bundled dependency and font licenses\n${licenses.join('\n\n').replace(/--/g, '—')}\n-->\n</head>`);
await writeFile(resolve(out, 'Audience.html'), audience);
await writeFile(resolve(out, 'BUILD.json'), JSON.stringify({ edition: privateEdition ? 'private-invoice-gallery' : 'repository', revealVersion: dependency.version, slides: (html.match(/<section\b/g) ?? []).length }, null, 2) + '\n');
console.log(`Built ${privateEdition ? 'private' : 'repository'} presenter deck and standalone audience HTML in ${out}`);
