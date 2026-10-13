# Azikus Scan & Pay — Webflow handoff

13 October 2026 · Target page: https://azikus.com/scan-and-pay-poc

## Preview first

Open **Scan-and-Pay.html** in a browser. It includes all CSS, JavaScript, images and fonts and works without a server. This is the complete visual reference. Do not preview `website/content.html` on its own: it is unstyled source markup.

## Package contents

- `Scan-and-Pay.html`: self-contained visual reference.
- `webflow-embed.html`: content, CSS and JavaScript for a Webflow Code Embed; asset URLs must be replaced before use.
- `assets/`: only the images and fonts used by the page, plus the font licence.
- `asset-urls.json`: filename-to-hosted-URL mapping template.
- `index.html`: alternative preview using the adjacent assets folder.
- `website/`: editable source and Python build script, including its own assets.

## Install in Webflow

1. Create or open the page with slug `scan-and-pay-poc`. Keep the existing Azikus navigation and footer. Insert a full-width wrapper without extra padding or a max-width; this content manages its own spacing. The embed supplies the page H1.
2. Upload the images from `assets/` to Webflow Assets. Host the bundled fonts through your permitted font/asset host, or use the site's existing licensed ABC Monument Grotesk. The bundled Hanken Grotesk is a fallback; retain `OFL.txt` with redistributed fonts.
3. Edit the root `asset-urls.json`: replace every placeholder with that file's actual HTTPS URL. Keep all filenames as keys, including gallery images that are not initially visible.
4. From the extracted ZIP folder, run this command (Python 3 only; no packages to install):

   ```sh
   python3 website/scripts/build.py --asset-map asset-urls.json
   ```

5. Copy the complete contents of the newly generated **`website/dist/webflow-embed.html`** into the page's Code Embed. This updates CSS fonts, initial screenshots and interactive gallery URLs together. Do not paste the standalone HTML or the unstyled source fragment.
6. If using the site's licensed font, remove the three fallback `@font-face` rules from the embed and add `#az-scan-pay { --sp-font: "YOUR WEBFLOW FONT FAMILY", sans-serif; }` after its other styles. The mapping script still expects every key in the supplied map; leave valid HTTPS URLs for the bundled fonts if using this build workflow.
7. Set page title to **Scan & Pay | Azikus** and description to **From a paper invoice to a reviewed payment draft. Explore Azikus native mobile, AI and spatial banking proofs of concept.** Use the site's normal canonical domain and redirects.
8. Check on Webflow staging before publication: desktop and mobile layouts; all five mobile steps in dark and light; all five spatial tabs; screenshot enlargement and Escape; extraction disclosure; GitHub button and contact email link. Designer view may not run the embedded JavaScript; verify on staging.

Alternatively, host all files in `assets/` under one HTTPS directory, then build with:

```sh
python3 website/scripts/build.py --asset-base https://YOUR-HOST/scan-and-pay/assets/
```

If Python is unavailable, update asset references in `webflow-embed.html` directly. For separately hosted files, replace the JavaScript `assetBase`/`asset` declarations with a filename-to-URL map covering all gallery screenshots; replacing only the visible `<img>` URLs is insufficient.

## Integration notes

Content only: no added navigation, side rails or replacement site footer. Styles are scoped to `#az-scan-pay`; script queries are scoped to the same root. No framework, backend connection, credentials or payment action is required. The page contains synthetic demonstration screenshots. Inline styles/scripts must be permitted by the host's content security policy.

The latest requested version uses mobile phone / companion display wording, a UK admin example and a prominent GitHub button. The “Proof beyond the interface” section has been removed.

Nothing has been uploaded or published. This ZIP is a developer handoff, not a Webflow project-import file.
