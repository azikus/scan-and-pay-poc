import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, access } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const source = await readFile(resolve(root, 'index.html'), 'utf8');
const built = await readFile(resolve(root, 'dist/index.html'), 'utf8');
const audience = await readFile(resolve(root, 'dist/Audience.html'), 'utf8');
assert.equal((source.match(/<section\b/g) ?? []).length, 25);
assert.equal((source.match(/<aside class="notes"/g) ?? []).length, 25);
assert.equal((audience.match(/<section\b/g) ?? []).length, 25);
assert(!audience.includes('<aside class="notes"'));
assert(!audience.includes('<script src='));
assert(!audience.includes('<link rel="stylesheet"'));
assert(!/src="(?!data:)/.test(audience));
assert(audience.includes('SIL OPEN FONT LICENSE'));
assert(audience.includes('MIT'));
assert(built.includes('class="corpus-index"'));
assert(!built.includes('corpus-gallery.png'));
assert(!/data:image|\/Users\/|file:\/\//.test(source));
await assert.rejects(access(resolve(root, 'dist/assets/corpus-gallery.png')));
const ids = [...source.matchAll(/<section[^>]+id="([^"]+)"/g)].map(m => m[1]);
assert.equal(new Set(ids).size, 25);
const manifest = JSON.parse(await readFile(resolve(root, 'assets/manifest.json'), 'utf8'));
for (const asset of manifest.assets) {
  const bytes = await readFile(resolve(root, 'assets', asset.file));
  assert.equal(createHash('sha256').update(bytes).digest('hex'), asset.sha256, `Update the reviewed asset manifest for ${asset.file}`);
}
for (const match of built.matchAll(/(?:src|href)="([^"]+)"/g)) {
  if (match[1].startsWith('#')) continue;
  assert(!/^(?:https?:|file:|\/)/.test(match[1]), `Unexpected remote or absolute resource: ${match[1]}`);
  await access(resolve(root, 'dist', match[1]));
}
assert((await readFile(resolve(root, 'dist/vendor/LICENSE'), 'utf8')).includes('MIT'));
assert((await readFile(resolve(root, 'assets/OFL.txt'), 'utf8')).includes('SIL OPEN FONT LICENSE'));
console.log('25 slides; notes and assets intact; audience export self-contained; private gallery excluded.');
