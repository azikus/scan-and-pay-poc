"""Isolated observation rehearsal. No provider adapters, credentials or live data."""

import argparse
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import uvicorn
from pydantic import SecretStr

from backend.api import create_app
from backend.config import Settings

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--host", default="127.0.0.1")
parser.add_argument("--port", type=int, default=8769)
args = parser.parse_args()
with tempfile.TemporaryDirectory(prefix="scanpay-display-rehearsal-") as data:
    app = create_app(
        Settings(data_dir=Path(data), token=SecretStr("synthetic-demo-access-no-private-data")),
        definitions={},
        adapters={},
    )
    print(f"Synthetic-only rehearsal: http://{args.host}:{args.port}/demo", flush=True)
    uvicorn.run(app, host=args.host, port=args.port, access_log=False)
