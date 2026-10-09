# Admin frontend

`admin/` contains the inspector's HTML, JavaScript, CSS, artwork and licensed fonts. Edit these files here. No separate frontend build, package manager or web server is required.

FastAPI serves the shell at `/admin` and the allowlisted assets at `/admin/assets/{name}`. The shell contains no private scan data; every data endpoint requires the existing bearer token. The collapsible **Connection** section reads authenticated `/v1/admin/connection` to display current phone URLs, warnings and automatic-update state. The managed Mac launcher follows network changes; see [connection setup](../docs/CONNECTION_SETUP.md).

In a source checkout or editable Python install, `backend/api.py` reads `frontend/admin/`. Hatch's wheel configuration maps that directory to `backend/admin_assets/` inside the installed package. This internal wheel path is intentional: an installed deployment does not need the repository or a sibling frontend directory. The font license is included in the wheel.

From the repository root:

```sh
node --check frontend/admin/admin.js
.venv/bin/python -m hatchling build
```

Before changing packaging, verify an installed wheel from outside the checkout, including `/admin`, every allowed asset and rejection of unlisted assets. See [reorganization verification](../docs/REPOSITORY_REORGANIZATION_HANDOFF.md) for the recorded check. Backend startup and private configuration remain in the [root README](../README.md) and [operations](../docs/OPERATIONS.md).
