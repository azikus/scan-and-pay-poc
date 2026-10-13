# Scan & Pay showcase and Webflow handoff

A content-only showcase for `azikus.com/scan-and-pay-poc`: actual application UI, synthetic/demo data, scoped styles and lightweight JavaScript. It supplies the page content, not navigation or a replacement site footer. Building it does not upload or publish anything. This README owns build, integration and screenshot attribution.

## Build and preview

Requires Python 3 only, with no packages to install. From the repository root, or the root of the extracted handoff ZIP:

```sh
python3 website/scripts/build.py
python3 -m http.server 8778 --bind 127.0.0.1 --directory website/dist
```

Open `http://127.0.0.1:8778`. Edit `website/content.html`, `styles.css` and `site.js`, then rebuild. Do not preview `content.html` alone: it is unstyled markup.

| Generated file | Use |
| --- | --- |
| `dist/Scan-and-Pay.html` | Self-contained visual reference with embedded screenshots/fonts/CSS/JS; opens offline |
| `dist/index.html` + `dist/assets/` | Standard static preview |
| `dist/webflow-embed.html` | Scoped Code Embed fragment; map asset URLs before use |
| `dist/asset-urls.json` | Filename-to-hosted-URL template |
| `dist/Scan-and-Pay-Webflow.zip` | Preview, embed, used assets/licence and editable source; this README becomes START-HERE.md |

Build output and QA captures are ignored. The ZIP is a developer handoff, not a Webflow project-import file. The source HTML/CSS/JS, screenshots, licences and provenance stay in Git. `assets/provenance.json` is excluded from the public package.

## Install in Webflow

1. Create/open the page slug `scan-and-pay-poc`. Keep the existing Azikus navigation/footer. Add a full-width wrapper without extra padding or max-width; the embed owns its spacing and supplies the page H1.
2. Upload images from the packaged `assets/` to Webflow Assets. Host fonts through a permitted host, retaining `OFL.txt`, or use the site's existing licensed ABC Monument Grotesk.
3. Copy the generated `asset-urls.json` outside `website/dist/`, then replace every placeholder with that asset's actual HTTPS URL. Keep all gallery filenames, including initially hidden screenshots and the bundled fonts.
4. From the repository/extracted ZIP root, run:

   ```sh
   python3 website/scripts/build.py --asset-map asset-urls.json
   ```

   A map stored elsewhere can use an absolute path. Mapping rewrites CSS fonts, initial screenshots and interactive gallery URLs together.
5. Paste the resulting **`website/dist/webflow-embed.html`** into the page's Code Embed. Do not paste the standalone document or unstyled content source.
6. To use an existing licensed site font, remove the three fallback `@font-face` declarations and add `#az-scan-pay { --sp-font: "YOUR WEBFLOW FONT FAMILY", sans-serif; }` after the embed's styles. The mapping workflow still expects valid HTTPS URLs for every supplied key.
7. Set title to **Scan & Pay | Azikus** and description to **From a paper invoice to a reviewed payment draft. Explore Azikus native mobile, AI and spatial banking proofs of concept.** Use the site's canonical domain/redirects; the display QR targets the `www` form.
8. Verify on Webflow staging: desktop/mobile layouts, all mobile dark/light and spatial tabs, screenshot enlargement/Escape/focus restoration, extraction disclosure, repository/contact links and reduced motion. Designer view may not execute scripts; inspect staging before normal publication.

If all assets share one HTTPS directory, build with:

```sh
python3 website/scripts/build.py --asset-base https://YOUR-HOST/scan-and-pay/assets/
```

Without Python, update `webflow-embed.html` directly, including the JavaScript `assetBase`/`asset` mapping for every gallery image. Updating only visible `<img>` URLs is insufficient.

## Integration behavior

The fragment has no document shell or global CSS reset. Styles/script queries are scoped to `#az-scan-pay`, and initialization runs once. No framework, backend connection, provider key, payment action, analytics or third-party JavaScript is needed. Inline CSS/JS must be permitted by the host's CSP, or moved to approved external files/nonces. Contact opens a draft in the visitor's mail app.

Keyboard tabs, visible focus, native disclosures and an Escape/focus-restoring screenshot modal are retained. Mobile layouts collapse; galleries have no autoplay. Explanatory content remains visible without JavaScript; switching/enlargement needs it. Motion is limited and respects Reduced Motion. Final host typography/layout needs staging verification.

## Screenshot attribution and licences

| Group | Source and meaning |
| --- | --- |
| Dark mobile walkthrough | Actual native iOS UI-test captures; synthetic invoice/account values |
| Light mobile walkthrough | Supplied original native iPhone captures; synthetic values |
| Spatial gallery | Supplied native UI renderer previews of a separate app; demo accounts/receipts, not headset or passthrough captures |
| Live display journey | Real companion webpage rendered with an isolated QA session; not a fresh live provider/latency study |
| Admin context | Production renderer with an isolated synthetic UK fixture |
| Admin selector | Authenticated admin cropped to method/model controls; no private scan list/document/token |

`assets/provenance.json` retains source filenames/descriptions, treatment and hashes. Resized/compressed delivery copies preserve screenshot content. Full local source paths and readable source invoices/corpus galleries are excluded. Physical user acceptance of the mobile/backend/display journey is distinct from screenshot attribution or measured accuracy/latency.

Use original Azikus artwork and near-black/white/ice-blue styling. Bundled Hanken Grotesk is the disclosed fallback for ABC Monument Grotesk; retain its SIL OFL when redistributing. Product screenshots retain their actual appearance. Event mention does not imply sponsorship or partnership, and project assets are not a grant for unrelated reuse/publication.

The showcase describes working capture/review/configurable extraction and potential payment-service integration. It promises neither Android delivery nor a further presentation. Confirmation remains simulated; no money moves or production quality guarantee is claimed. The repository's main README owns the product explanation, and `docs/EVALUATION.md` owns measurements/limits.
