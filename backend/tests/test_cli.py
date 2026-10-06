import json
import sys

import httpx
import pytest

from backend import cli


def test_cli_upload_poll_saves_private_result_without_payment_logs(
    uk, png, tmp_path, monkeypatch, capsys
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SCANPAY_TOKEN", "test-token")
    image = tmp_path / "synthetic.png"
    image.write_bytes(png)
    uk.scan_id = "scan-" + "0" * 32
    result = uk.model_dump(mode="json")
    seen = []

    def handler(request):
        seen.append(request)
        if request.method == "POST":
            assert request.headers["idempotency-key"] == "fixed-key"
            return httpx.Response(202, json={"scan_id": uk.scan_id, "state": "queued"})
        return httpx.Response(200, json=result)

    actual_client = httpx.Client
    monkeypatch.setattr(
        cli.httpx,
        "Client",
        lambda **kwargs: actual_client(**kwargs, transport=httpx.MockTransport(handler)),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["scanpay", "upload", str(image), "--profiles", "openai-luna-vision", "--key", "fixed-key"],
    )
    cli.main()
    text = capsys.readouterr().out
    assert "ready_for_review" in text
    assert "Example Utilities" not in text and "00000000" not in text.replace(uk.scan_id, "")
    saved = tmp_path / ".local/client" / (uk.scan_id + ".json")
    assert json.loads(saved.read_text()) == result
    assert saved.stat().st_mode & 0o777 == 0o600
    assert len(seen) == 2


@pytest.mark.parametrize("command", ["health", "profiles", "delete", "get"])
def test_cli_commands(uk, tmp_path, monkeypatch, capsys, command):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SCANPAY_TOKEN", "test-token")
    uk.scan_id = "scan-" + "1" * 32
    result = uk.model_dump(mode="json")
    actual_client = httpx.Client

    def handler(request):
        return (
            httpx.Response(204)
            if command == "delete"
            else httpx.Response(200, json=result if command == "get" else {"status": "ok"})
        )

    monkeypatch.setattr(
        cli.httpx,
        "Client",
        lambda **kwargs: actual_client(**kwargs, transport=httpx.MockTransport(handler)),
    )
    monkeypatch.setattr(
        sys, "argv", ["scanpay", command] + ([uk.scan_id] if command in {"delete", "get"} else [])
    )
    cli.main()
    assert capsys.readouterr().out


def test_poll_deadline_and_cli_http_failure(monkeypatch, capsys):
    with httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json={"state": "running"})
        ),
        base_url="http://localhost",
    ) as client:
        monkeypatch.setattr(cli.time, "sleep", lambda _: None)
        with pytest.raises(TimeoutError):
            cli.poll(client, "scan-test", 0.001)
    actual_client = httpx.Client
    monkeypatch.setattr(
        cli.httpx,
        "Client",
        lambda **kwargs: actual_client(
            **kwargs,
            transport=httpx.MockTransport(lambda request: httpx.Response(500, text="SECRET")),
        ),
    )
    monkeypatch.setattr(sys, "argv", ["scanpay", "health"])
    with pytest.raises(SystemExit):
        cli.main()
    assert "SECRET" not in capsys.readouterr().err
