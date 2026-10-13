# Scan and Pay presentation

The approved 25-slide, 1600 × 900 reveal.js deck now lives beside the application. It retains the 9 October 2026 narrative, measured comparisons, English slides, Croatian speaker notes, animations and approximately 19–20 minute timing. The original external export is preserved.

## Run locally

Requires Node.js 22 or newer and npm. From this directory:

```sh
npm ci --ignore-scripts
npm run build
npm run check
npm start
```

Open <http://127.0.0.1:8766>. Arrow keys or the on-screen controls advance slides and fragments. `S` / **Notes** opens the presenter view in a separate window (allow popups); `F` or **Fullscreen** uses fullscreen. `?review` displays all fragments for layout inspection. Use `npm start -- --port 8767` if the default port is occupied. The static server binds only loopback and serves only the built deck, independently of the backend on port 8000. It never submits a scan.

Only dependency installation needs network access. reveal.js is pinned to **6.0.2**, matching the previous deck, with a lockfile. Fonts, logos, screenshots, scripts and styles are local. No CDN is required while presenting.

## Edit and export

- `index.html` is the slide and speaker-note source of truth. Edit it directly.
- `deck.css` and `deck.js` preserve the approved visual design and interaction.
- `assets/manifest.json` records the reviewed asset hashes. Original logos and the existing masked/synthetic screenshots are retained byte-for-byte.
- `npm run content` regenerates [the text companion](../docs/PRESENTATION_CONTENT.md). Do this after changing slide text or notes, then rebuild and check.
- `dist/index.html` is the presenter version with notes. `dist/Audience.html` is a standalone file containing its own scripts, fonts and images, with speaker notes and the notes plugin removed. It opens without a server.
- For PDF, open <http://127.0.0.1:8766/?print-pdf> in Chrome/Chromium, choose Print → Save as PDF, landscape, no margins, and enable background graphics. Fragments print together. PDF and generated HTML exports are ignored by Git.

Build output is regenerated, not committed. After `npm ci`, run `npm run build` from a fresh checkout. No backend or iOS build is required. Historical evaluation values remain dated facts; do not replace them with the current operational allowance or selection.

## Invoice gallery

The repository edition shows a numbered overview of the **17 evaluation inputs**, preserving the study counts without including invoice pixels. Other screenshots were inspected before import: review is synthetic, payment values are already masked, and the admin/production screenshots contain no personal or banking values. See [asset provenance](ASSETS.md).

The full invoice gallery remains an optional **local-only** asset. On the existing Mac it is already copied, unchanged, into ignored `private-assets/corpus-gallery.png`. On another machine, obtain that file from the private original export; do not add it to Git. Then:

```sh
npm run build:private
npm run start:private
```

This writes only `dist-private/`, including its own presenter deck and audience export. These outputs contain readable invoice previews and remain private. The regular build never reads private assets, and the local server cannot serve source files, credentials or the private-assets directory. Building either edition does not publish it.

## Evidence and next work

[Authoring evidence](../docs/PRESENTATION_EVIDENCE.md) keeps metric sources and revision history separate from slides. [Current status](../docs/CURRENT_STATUS.md) records the application, allowance and delivery state. The initial deck is retained. Markus skipped Android and the comprehensive final presentation on 13 October; no new deck is pending. The separate existing [Webflow showcase](../website/README.md) is preserved and unpublished.
