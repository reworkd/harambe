from harambe_core.observer.json_observer import JsonStdoutObserver


async def test_json_observer(capsys):
    observer = JsonStdoutObserver()

    await observer.on_save_data({"key": "value"})

    captured = capsys.readouterr()
    assert captured.out == '{"type": "on_save_data", "data": {"key": "value"}}\n'
    assert captured.err == ""

    await observer.on_queue_url("https://www.example.com", {"foo": "bar"}, {})

    captured = capsys.readouterr()
    assert (
        captured.out
        == '{"type": "on_queue_url", "data": {"url": "https://www.example.com", "context": {"foo": "bar"}, "options": {}}}\n'
    )
    assert captured.err == ""

    await observer.on_download(
        "https://www.example.com", "example.html", b"content", "path"
    )

    captured = capsys.readouterr()
    assert (
        captured.out
        == '{"type": "on_download", "data": {"download_url": "https://www.example.com", "filename": "example.html", "content": "base64:Y29udGVudA==", "path": "path"}}\n'
    )
    assert captured.err == ""

    await observer.on_save_cookies(
        [
            {
                "name": "name",
                "value": "value",
                "domain": "domain",
                "path": "path",
                "expires": 0,
                "size": 0,
                "httpOnly": True,
                "secure": True,
                "session": True,
                "sameSite": "strict",
            }
        ]
    )

    captured = capsys.readouterr()
    assert (
        captured.out
        == '{"type": "on_save_cookies", "data": [{"name": "name", "value": "value", "domain": "domain", "path": "path", "expires": 0, "size": 0, "httpOnly": true, "secure": true, "session": true, "sameSite": "strict"}]}\n'
    )
    assert captured.err == ""

    await observer.on_save_local_storage(
        [
            {
                "domain": "domain",
                "path": "path",
                "key": "key",
                "value": "value",
            }
        ]
    )

    captured = capsys.readouterr()
    assert (
        captured.out
        == '{"type": "on_save_local_storage", "data": [{"domain": "domain", "path": "path", "key": "key", "value": "value"}]}\n'
    )
    assert captured.err == ""


async def test_multiple_lines(capsys):
    observer = JsonStdoutObserver()

    await observer.on_save_data({"key": "value1"})
    await observer.on_queue_url("https://www.example.com", {"foo": "bar"}, {})
    await observer.on_save_data({"key": "value2"})

    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    assert len(lines) == 3

    assert lines[0] == '{"type": "on_save_data", "data": {"key": "value1"}}'
    assert (
        lines[1]
        == '{"type": "on_queue_url", "data": {"url": "https://www.example.com", "context": {"foo": "bar"}, "options": {}}}'
    )
    assert lines[2] == '{"type": "on_save_data", "data": {"key": "value2"}}'
