# Chrome Web Store Preparation

This folder contains release-readiness material for the Chrome Web Store. It does not publish or submit the extension.

- `listing.md`: Dashboard-ready listing copy, privacy declarations, permission justifications, reviewer notes, and update guidance.
- `permission-audit.md`: requested permissions, removed permissions, remaining access, and justification.
- `release-checklist.md`: packaging, dashboard, asset, CORS, and final QA checklist.
- `assets/`: final Store screenshots and promotional tile.
- `source/`: deterministic HTML used to render the final raster assets.

The public privacy policy source is `../PRIVACY.md`. Host it at a stable public HTTPS URL before submission and enter that URL in the Developer Dashboard Privacy practices tab.

The optional product landing page lives in `../site/`. If it is published through GitHub Pages or another HTTPS host, use that URL as the Chrome Web Store homepage.
