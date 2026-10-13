import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const html = await readFile(resolve(root, 'index.html'), 'utf8');
const plain = text => text.replace(/<!--[\s\S]*?-->/g, '').replace(/<[^>]*>/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#x27;|&#39;/g, "'").replace(/\s+/g, ' ').trim();
const output = ['# Scan and Pay 2.0 — presentation content', 'Source: `presentation/index.html`. Generated with `npm run content` in `presentation/`; edit the HTML source, then regenerate this companion.', '25 slides. English slides and Croatian speaker notes; approximately 19–20 minutes including the live demo. Content retains the approved 9 October 2026 revision and its dated evidence. The repository edition uses a numbered corpus overview; original invoice previews are optional local assets.'];
for (const [index, match] of [...html.matchAll(/<section\b[\s\S]*?<\/section>/g)].entries()) {
  const section = match[0];
  const title = section.match(/data-name="([^"]*)"/)?.[1] || (index === 0 ? 'Cover' : 'More to build together');
  const body = section.match(/<main>([\s\S]*?)<\/main>/)?.[1] ?? '';
  const notes = section.match(/<aside class="notes"[^>]*>([\s\S]*?)<\/aside>/)?.[1] ?? '';
  output.push(`## ${index + 1}. ${plain(title)}`, '### On slide', plain(body), '### Speaker notes — Croatian', plain(notes));
}
await writeFile(resolve(root, 'CONTENT.md'), output.join('\n\n') + '\n');
console.log('Updated presentation/CONTENT.md from the deck source.');
