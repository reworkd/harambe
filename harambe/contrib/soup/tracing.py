import hashlib
import json
import zipfile
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from curl_cffi import requests

from harambe.utils import swallow_exceptions


def write_json_lines(file_path: Path, data: list[Any]) -> None:
    with file_path.open("w") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")


class Tracer:
    def __init__(self) -> None:
        self._is_tracing = False
        self._network_traces: list[Any] = []
        self._resources: list[tuple[str, bytes]] = []

    def start(self) -> None:
        self._is_tracing = True

    def stop(self, *, path: str | Path) -> None:
        self._is_tracing = False
        self._create_zip(path)

    def _create_zip(self, path: str | Path) -> None:
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            resources_path = temp_path / "resources"
            resources_path.mkdir(parents=True, exist_ok=True)

            # Create dummy trace files for demonstration
            trace_network_file = temp_path / "trace.network"
            trace_trace_file = temp_path / "trace.trace"
            trace_stacks_file = temp_path / "trace.stacks"

            write_json_lines(trace_network_file, self._network_traces)
            trace_trace_file.touch()
            trace_stacks_file.touch()

            # Write resources
            for file_name, content in self._resources:
                with (resources_path / file_name).open("wb") as f:
                    f.write(content)

            # Create the zip file
            with zipfile.ZipFile(path, "w") as zipf:
                for file_path in temp_path.rglob("*"):
                    zipf.write(file_path, file_path.relative_to(temp_path))

    @swallow_exceptions
    def log_request(self, response: requests.Response) -> None:
        if not self._is_tracing or not response.request:
            return

        started_date_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        sha1 = hashlib.sha1(response.content).hexdigest()
        file_name = f"{sha1}.html"  # todo FILE types

        self._resources.append((file_name, response.content))
        self._network_traces.append(
            {
                "type": "resource-snapshot",
                "snapshot": {
                    "_frameref": "frame@7e64af4e3ffc9880713f6353fe66e81d",
                    "_monotonicTime": 0,  # TODO: calculate this
                    "startedDateTime": started_date_time,
                    "time": response.elapsed,
                    "request": {
                        "method": response.request.method,
                        "url": response.url,
                        "httpVersion": "HTTP/1.1",
                        "cookies": response.request.headers.get("Cookie", ""),
                        "headers": [
                            {"name": k, "value": v}
                            for k, v in response.request.headers.items()
                        ],
                        "queryString": [],
                        "headersSize": sum(
                            len(k) + len(v) for k, v in response.request.headers.items()
                        ),
                        "bodySize": 0,
                    },
                    "response": {
                        "status": response.status_code,
                        "statusText": response.reason,
                        "httpVersion": "HTTP/1.1",
                        "cookies": response.cookies.get_dict(),
                        "headers": [
                            {"name": k, "value": v} for k, v in response.headers.items()
                        ],
                        "content": {
                            "size": len(response.content),
                            "mimeType": response.headers.get("Content-Type", ""),
                            "compression": 0,
                            "_sha1": file_name,
                        },
                        "headersSize": sum(
                            len(k) + len(v) for k, v in response.headers.items()
                        ),
                        "bodySize": len(response.content),
                        "redirectURL": response.headers.get("Location", ""),
                        "_transferSize": len(response.content)
                        + sum(len(k) + len(v) for k, v in response.headers.items()),
                    },
                    "cache": {},
                    "timings": {
                        "dns": 0,  # Detailed timing info requires more complex instrumentation
                        "connect": 0,
                        "ssl": 0,
                        "send": 0,
                        "wait": response.elapsed,
                        "receive": 0,
                    },
                    "pageref": "page@cdd43826a397303886e152d3ad9548b3",
                    "serverIPAddress": response.primary_ip,
                    "_serverPort": 8081,
                    "_securityDetails": {},
                },
            }
        )
