# Scan & Pay: Webflow content

Prepared for `azikus.com/scan-and-pay-poc`, 13 October 2026. This is a content-only product showcase, without site navigation, side rails or a replacement site footer. It uses actual product UI, not generated screens. Nothing is published by this build.

## Deliverables

- `dist/Scan-and-Pay.html`: portable standalone HTML with images, fonts, styles and scripts embedded. Open directly; no server or internet required. Best for review and forwarding, not pasting into Webflow.
- `dist/index.html` + `dist/assets/`: standard static preview.
- `dist/webflow-embed.html`: scoped content fragment with inline CSS/JS and external assets. Paste into a Webflow Code Embed after mapping the asset URLs.
- `dist/Scan-and-Pay-Webflow.zip`: packaged handoff including all the above, asset URL template and these notes.

## Webflow integration

1. Keep the existing site shell. Add a full-width content wrapper on the page with slug `scan-and-pay-poc`, with no extra max-width or padding; the fragment manages its own responsive content width. Use one page H1: the embed already contains it.
2. Upload the screenshots and fonts from `dist/assets/` to your permitted asset host. `OFL.txt` must accompany redistributed Hanken fonts. If Webflow already serves a licensed ABC Monument Grotesk family, use it through `#az-scan-pay { --sp-font: "YOUR EXISTING FAMILY", sans-serif; }` and omit the three fallback `@font-face` rules.
3. For individual Webflow CDN URLs, copy `dist/asset-urls.json` to a file outside `dist/`, replace every placeholder with its uploaded HTTPS URL, then run `python3 website/scripts/build.py --asset-map /absolute/path/to/asset-urls.json`. The builder rewrites initial images, CSS fonts and all interactive gallery images. The default relative `assets/` paths are for local preview and must be mapped for Webflow.
4. If serving all assets from one directory, use `python3 website/scripts/build.py --asset-base https://YOUR-HOST/scan-and-pay/assets/` instead.
5. Paste the resulting `dist/webflow-embed.html` into the page’s Code Embed. Preview on staging to check the site's existing styles, then publish through your normal Webflow process. No Webflow login or publication was performed here.

The fragment contains no `<html>`, `<head>` or `<body>`. CSS selectors are scoped to `#az-scan-pay`; script queries are scoped to the same root and initialise once. It does not fetch invoice data or use any backend credentials. There is no framework, third-party JavaScript, analytics, external font request or payment action. An existing host content security policy must permit the embed’s inline styles/scripts, or move those into approved external files/nonces. Contact opens a draft in the visitor’s email app.

Set the Webflow page title to **Scan & Pay | Azikus** and description to **From a paper invoice to a reviewed payment draft. Explore Azikus native mobile, AI and spatial banking proofs of concept.** Set the canonical URL to the site's chosen `www` or non-`www` form of `/scan-and-pay-poc`. The existing SUNMI QR targets the `www` form; preserve the site's normal domain redirect.

## Edit and preview

Edit `content.html`, `styles.css` and `site.js`. Build with Python 3 (standard library only):

```sh
python3 website/scripts/build.py
python3 -m http.server 8778 --bind 127.0.0.1 --directory website/dist
```

Open `http://127.0.0.1:8778`. Build output and local QA captures are ignored by Git. `assets/provenance.json` is an authoring record; its local source paths are deliberately excluded from the distributable package. Source screenshots remain unchanged; WebP delivery copies are resized/compressed only.

Typography uses bundled **Hanken Grotesk**, the disclosed fallback for the brand's **ABC Monument Grotesk**. The visual language follows the Azikus brand kit and the public site's current content. Direct rendering of azikus.com was blocked by its certificate/connection error during preparation, so exact host-page typography and shell integration require the final Webflow staging check.

## Design and verification

Near-black canvas, ice-blue emphasis, large left-aligned type and real native UI. Native CSS and lightweight JavaScript suit the requested Webflow fragment. Motion is limited to entry, section reveals and screenshot changes, with Reduced Motion support. No scroll hijacking or endless animation. Product screenshots retain their real appearance.

Keyboard-accessible tab groups, visible focus, native disclosure elements, and a modal screenshot viewer with Escape/focus restoration. Mobile layouts collapse explicitly; the screenshot gallery remains navigable without autoplay. All core explanatory content remains visible without JavaScript; gallery switching and enlargement require JavaScript.

See `EVIDENCE.md` for factual sources and limitations. This page is the existing showcase of current work. Markus skipped Android and the final presentation on 13 October; those are not promised next deliverables. Real payment integration remains outside the PoC.

Verified in the browser at 320, 390, 768, 1024 and 1440 px: no document/body horizontal overflow. Mobile dark/light switching, keyboard tab navigation, spatial portrait/landscape switching, disclosure tables, modal Escape and focus restoration passed. The standalone HTML uses embedded data images successfully for both galleries. No browser console warnings/errors were observed. JavaScript syntax and package asset checks passed. Reduced-motion rules were inspected; no Lighthouse score or device performance measurement is claimed.
