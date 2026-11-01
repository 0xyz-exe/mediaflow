from __future__ import annotations

import ipaddress
import json
import mimetypes
import os
import shutil
import socket
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
MAX_UPLOAD = 250 * 1024 * 1024
ALLOWED_OUTPUTS = {"mp3", "wav", "m4a", "ogg", "mp4", "webm"}


def checked_url(raw: str) -> tuple[str, str]:
    """Accept only public HTTP(S) destinations, resolving host before request."""
    try:
        parsed = urllib.parse.urlsplit(raw)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            raise ValueError("Use a valid HTTP or HTTPS media URL.")
        if parsed.username or parsed.password:
            raise ValueError("URLs containing credentials are not accepted.")
        host = parsed.hostname.rstrip(".").lower()
        if host == "localhost" or host.endswith(".localhost") or host.endswith(".local"):
            raise ValueError("Local and private network addresses are blocked.")
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        addresses = {item[4][0] for item in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)}
        if not addresses:
            raise ValueError("The media host did not resolve.")
        for address in addresses:
            ip = ipaddress.ip_address(address.split("%", 1)[0])
            if not ip.is_global:
                raise ValueError("Local and private network addresses are blocked.")
        return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path or "/", parsed.query, "")), host
    except (ValueError, UnicodeError, socket.gaierror, OSError) as exc:
        if isinstance(exc, ValueError) and str(exc).startswith(("Use ", "URLs ", "Local ", "The media")):
            raise
        raise ValueError("Invalid or unreachable media URL.") from exc


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Redirects are blocked for security. Use the final direct media URL.")


OPENER = urllib.request.build_opener(NoRedirect)


def inspect_url(raw: str) -> dict:
    safe_url, host = checked_url(raw)
    request = urllib.request.Request(safe_url, method="HEAD", headers={"User-Agent": "MediaFlow/0.1"})
    try:
        with OPENER.open(request, timeout=10) as response:
            content_type = response.headers.get_content_type()
            length = response.headers.get("Content-Length")
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise ValueError("Could not inspect this direct URL. Redirects and non-public hosts are unsupported.") from exc
    if not (content_type.startswith("video/") or content_type.startswith("audio/") or content_type == "image/*"):
        if content_type not in ("application/octet-stream", "image/jpeg", "image/png", "image/webp", "image/gif"):
            raise ValueError("URL did not identify itself as a supported direct media file.")
    return {"host": host, "type": content_type, "size": int(length) if length and length.isdigit() else None, "url": safe_url}


class Handler(BaseHTTPRequestHandler):
    server_version = "MediaFlow/0.1"

    def log_message(self, fmt, *args):
        # Avoid writing full request paths, which may contain sensitive query tokens.
        print(f"{self.client_address[0]} {self.command} {self.path.split('?')[0]} {args[1] if len(args) > 1 else ''}")

    def send_json(self, status: int, data: dict):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size > 16_384:
                raise ValueError("Request too large.")
            return json.loads(self.rfile.read(size))
        except (ValueError, json.JSONDecodeError) as exc:
            raise ValueError("Invalid request body.") from exc

    def do_GET(self):
        if self.path == "/api/health":
            return self.send_json(200, {"ok": True})
        if self.path == "/":
            path = WEB / "index.html"
        else:
            path = (WEB / self.path.lstrip("/")).resolve()
            if WEB.resolve() not in path.parents:
                return self.send_error(404)
        if not path.is_file():
            return self.send_error(404)
        content = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        try:
            if self.path == "/api/analyze":
                body = self.read_json()
                url = body.get("url") if isinstance(body, dict) else None
                if not isinstance(url, str) or len(url) > 4096:
                    raise ValueError("Enter a valid URL (up to 4096 characters).")
                return self.send_json(200, {"success": True, "data": inspect_url(url)})
            if self.path == "/api/convert":
                return self.convert_upload()
            return self.send_json(404, {"error": "Not found."})
        except ValueError as exc:
            return self.send_json(400, {"error": str(exc)})
        except Exception:
            return self.send_json(502, {"error": "Media request failed. Check the URL or file and try again."})

    def convert_upload(self):
        if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
            return self.send_json(503, {"error": "FFmpeg and FFprobe must be installed and available on PATH."})
        if not self.headers.get("Content-Type", "").startswith("multipart/form-data;"):
            raise ValueError("Upload a media file using the form.")
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > MAX_UPLOAD + 16_384:
            raise ValueError("Upload must be between 1 byte and 250 MiB.")
        # Parse MIME envelope with stdlib; raw upload bytes remain bounded by Content-Length.
        from email.parser import BytesParser
        from email.policy import default
        envelope = (f"Content-Type: {self.headers['Content-Type']}\r\nMIME-Version: 1.0\r\n\r\n").encode() + self.rfile.read(length)
        message = BytesParser(policy=default).parsebytes(envelope)
        file_part = next((part for part in message.iter_parts() if part.get_param("name", header="content-disposition") == "file"), None)
        format_part = next((part for part in message.iter_parts() if part.get_param("name", header="content-disposition") == "format"), None)
        if not file_part or not format_part:
            raise ValueError("Select a media file and output format.")
        output_format = (format_part.get_content() or "").strip().lower()
        if output_format not in ALLOWED_OUTPUTS:
            raise ValueError("Unsupported output format.")
        raw = file_part.get_payload(decode=True) or b""
        if not raw or len(raw) > MAX_UPLOAD:
            raise ValueError("File must be between 1 byte and 250 MiB.")
        with tempfile.TemporaryDirectory(prefix="mediaflow-") as directory:
            source = Path(directory) / "input.bin"
            target = Path(directory) / f"output.{output_format}"
            source.write_bytes(raw)
            probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(source)], capture_output=True, timeout=15, check=False)
            if probe.returncode != 0:
                raise ValueError("File is not a supported media file.")
            subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(source), "-t", "1800", str(target)], capture_output=True, timeout=180, check=True)
            output = target.read_bytes()
        filename = f"mediaflow-{uuid.uuid4().hex[:8]}.{output_format}"
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(filename)[0] or "application/octet-stream")
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(len(output)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(output)


def main():
    print("MediaFlow listening on http://127.0.0.1:8000 (loopback only)")
    ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()


if __name__ == "__main__":
    main()
