# Asset provenance and dependencies

Imported from the locally delivered 9 October 2026 Scan and Pay deck. The approved design and all included image/font bytes are preserved. `assets/manifest.json` records SHA-256 hashes so later replacements are deliberate.

| Asset | Source and treatment |
| --- | --- |
| `logo-white.svg`, `logo-dark.svg`, `logomark-white.svg` | Supplied Azikus artwork, unchanged |
| `aircash-logo.png` | Supplied Aircash logo from the approved reference deck, unchanged |
| `HankenGrotesk-*.ttf`, `OFL.txt` | Hanken Grotesk under the bundled SIL Open Font License; disclosed fallback for ABC Monument Grotesk |
| `current-3855.png` | User-supplied production scanner screen, without invoice/payment values |
| `current-3860.png`, `current-3861.png` | User-supplied production scanner reading a test barcode, without banking data |
| `current-payment.png` | Previously flattened screenshot with payment values masked; no original unmasked screenshot imported |
| `review.png` | PoC synthetic preview, explicitly labelled in the image |
| `admin-selector.png` | Method/model selector, without credentials or payment values |
| `admin-inspector.png` | Inspector navigation/header, without the invoice, JSON values or raw provider content |

The real invoice montage `corpus-gallery.png` is excluded from version control and from the default build. It can be included only through the explicit local private build. Original source invoices, labels, raw responses and credentials remain outside the presentation source.

reveal.js **6.0.2** is an exact dependency in `package.json` / `package-lock.json`, under its MIT license. Each build copies that license into `vendor/LICENSE`. The font license is included in both distributable folders. Both licenses are also embedded as a comment in each standalone audience HTML. Azikus/Aircash logos and user-supplied product screenshots are project assets, not a grant for unrelated reuse or public publication.
