# Frontends

Two static frontends are served by the same FastAPI process. Neither needs a separate build, package manager or service.

| Source | Route | Wheel path | Use |
| --- | --- | --- | --- |
| `admin/` | `/admin` | `backend/admin_assets/` | Private inspection, method selection and connection status |
| `demo/` | `/demo` | `backend/demo_assets/` | Sanitized live companion views |

Source/editable installs read these directories directly. Shells contain no private record data; data endpoints require the existing bearer token. Assets are allowlisted and self-hosted, including font licences. User/provider metadata is rendered as text, never executed as HTML.

Admin reads original JSON, retained outputs, exact mobile images and separate confirmed reviews. The Next scan form updates the shared exact profile selection without dispatching inference. Connection shows bound Mac addresses; [setup](../docs/SETUP.md) covers hotspot operation.

[Live display behavior](demo/README.md) describes projection/streaming and [SUNMI setup](../sunmi/companion/README.md) covers the native host. [Development checks](../docs/DEVELOPMENT.md) cover syntax/tests and installed-wheel asset verification.
