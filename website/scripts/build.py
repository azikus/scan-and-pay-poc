"""Build local preview, portable HTML and a Webflow content fragment. No network."""
import argparse
import base64
import json
import mimetypes
from pathlib import Path
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--asset-base', default='assets/', help='Public HTTPS asset directory; include trailing slash')
parser.add_argument('--asset-map', type=Path, help='JSON mapping asset filenames to individual Webflow CDN URLs')
args = parser.parse_args()
dist = ROOT / 'dist'
dist.mkdir(exist_ok=True)
assets = ROOT / 'assets'
content = (ROOT / 'content.html').read_text()
css = (ROOT / 'styles.css').read_text()
js = (ROOT / 'site.js').read_text()
used = set(re.findall(r'assets/([\w.-]+)', content + css))
used.update(f'{p}-{n:02}.webp' for p in ('dark','mobile','spatial') for n in range(1,6))
asset_map = json.loads(args.asset_map.read_text()) if args.asset_map else {}
if asset_map:
    missing = used - asset_map.keys()
    if missing:
        raise SystemExit('Missing asset URLs: ' + ', '.join(sorted(missing)))
    if any(not v.startswith('https://') for v in asset_map.values()):
        raise SystemExit('Asset URLs must use HTTPS')

def wrap(body):
    return '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Scan &amp; Pay | Azikus</title><meta name="description" content="From a paper invoice to a reviewed payment draft. Explore Azikus native mobile, AI and spatial banking proofs of concept."><style>body{margin:0;background:#0a0a0a}</style></head><body>' + body + '</body></html>\n'

def fragment(markup, style, script):
    return '<!-- Azikus Scan & Pay: content only. No site navigation or global CSS reset. -->\n<style>\n' + style + '\n</style>\n' + markup + '\n<script>\n' + script + '\n</script>\n'

local = fragment(content, css, js)
(dist / 'index.html').write_text(wrap(local))
# Recreate the generated asset directory; source assets and provenance stay intact.
delivery_assets = dist / 'assets'
if delivery_assets.exists():
    shutil.rmtree(delivery_assets)
delivery_assets.mkdir()
for name in sorted(used | {'OFL.txt'}):
    shutil.copy2(assets / name, delivery_assets / name)

urls = {name: asset_map.get(name, args.asset_base.rstrip('/') + '/' + name) for name in used}
embed_content, embed_css = content, css
for name, url in urls.items():
    embed_content = embed_content.replace('assets/' + name, url)
    embed_css = embed_css.replace('assets/' + name, url)
embed_js = js
if asset_map:
    embed_js = re.sub(r"  const assetBase = .*\n  const asset = name => assetBase \+ name;", '  const assetURLs = ' + json.dumps(urls) + ';\n  const asset = name => assetURLs[name];', js)
embed = fragment(embed_content, embed_css, embed_js)
(dist / 'webflow-embed.html').write_text(embed)

data = {name: 'data:' + (mimetypes.guess_type(name)[0] or 'application/octet-stream') + ';base64,' + base64.b64encode((assets/name).read_bytes()).decode() for name in used}
inline_content, inline_css = content, css
for name, url in data.items():
    inline_content = inline_content.replace('assets/' + name, url)
    inline_css = inline_css.replace('assets/' + name, url)
inline_js = re.sub(r"  const assetBase = .*\n  const asset = name => assetBase \+ name;", '  const embeddedAssets = ' + json.dumps(data) + ';\n  const asset = name => embeddedAssets[name];', js)
license_note = '<!-- Hanken Grotesk font licence\n' + (assets/'OFL.txt').read_text().replace('--','- -') + '\n-->\n'
(dist / 'Scan-and-Pay.html').write_text(wrap(license_note + fragment(inline_content,inline_css,inline_js)))
(dist / 'asset-urls.json').write_text(json.dumps({name: 'https://YOUR-ASSET-HOST/' + name for name in sorted(used)}, indent=2))
shutil.copy2(ROOT/'README.md', dist/'README.md')
# Remove superseded documentation left by an older local build.
for name in ['EVIDENCE.md', 'HANDOFF.md']:
    (dist/name).unlink(missing_ok=True)
with zipfile.ZipFile(dist/'Scan-and-Pay-Webflow.zip','w',zipfile.ZIP_DEFLATED) as z:
    # Explicit allowlist: keep authoring evidence, private paths and stale assets out.
    for name in ['Scan-and-Pay.html', 'index.html', 'webflow-embed.html', 'asset-urls.json']:
        z.write(dist/name, name)
    z.write(ROOT/'README.md', 'START-HERE.md')
    for name in ['content.html', 'styles.css', 'site.js', 'scripts/build.py', 'README.md']:
        z.write(ROOT/name, 'website/' + name)
    for name in sorted(used | {'OFL.txt'}):
        z.write(assets/name, 'assets/' + name)
        z.write(assets/name, 'website/assets/' + name)
print(f'Built preview, standalone HTML and Webflow package. Embed: {len(embed):,} characters.')
