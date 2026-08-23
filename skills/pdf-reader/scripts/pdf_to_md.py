#!/usr/bin/env python3
"""Convert a PDF to Markdown via the MinerU cloud API (v4 batch flow).

Flow: request an upload URL -> PUT the file -> poll the batch -> download the
result zip -> extract the .md file.

Token resolution order:
  1. --token argument
  2. MINERU_API_KEY environment variable
  3. ~/.mineru/token file (first line)

Prints the extracted .md path as the last stdout line; progress goes to stderr.
Uses only the Python standard library.
"""

import argparse
import http.client
import io
import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
import zipfile
from pathlib import Path

API_BASE = "https://mineru.net/api/v4"
RETRYABLE_HTTP_STATUSES = {408, 429, 500, 502, 503, 504}
RETRY_DELAY_SECONDS = 2


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def retry_once(msg):
    log(f"      {msg}; retrying once in {RETRY_DELAY_SECONDS}s ...")
    time.sleep(RETRY_DELAY_SECONDS)


def get_token(args_token):
    if args_token:
        return args_token.strip()
    env = os.environ.get("MINERU_API_KEY", "").strip()
    if env:
        return env
    token_file = Path.home() / ".mineru" / "token"
    if token_file.exists():
        lines = token_file.read_text(encoding="utf-8").splitlines()
        if lines and lines[0].strip():
            return lines[0].strip()
    sys.exit(
        "No MinerU API token found. Set MINERU_API_KEY, pass --token, "
        "or write the token to ~/.mineru/token (get one at https://mineru.net)"
    )


def http_request(method, url, token=None, payload=None, data=None,
                 extra_headers=None, timeout=120):
    headers = dict(extra_headers or {})
    body = data
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    for attempt in range(2):
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")[:500]
            if attempt == 0 and e.code in RETRYABLE_HTTP_STATUSES:
                retry_once(f"HTTP {e.code} from MinerU API")
                continue
            sys.exit(f"HTTP {e.code} from MinerU API: {detail}")
        except (urllib.error.URLError, TimeoutError, OSError,
                http.client.HTTPException) as e:
            if attempt == 0:
                retry_once(f"Network error contacting MinerU API: {e}")
                continue
            sys.exit(f"Network error contacting MinerU API after retry: {e}")


def put_presigned(url, data, timeout=600):
    """PUT to a pre-signed OSS URL with NO Content-Type header.

    MinerU signs the URL without Content-Type, so any Content-Type header
    (including urllib's injected default) breaks the signature. http.client
    gives exact control over which headers are sent.
    """
    u = urllib.parse.urlsplit(url)
    path = u.path + ("?" + u.query if u.query else "")
    for attempt in range(2):
        conn = None
        try:
            conn = http.client.HTTPSConnection(u.netloc, timeout=timeout)
            conn.putrequest("PUT", path, skip_accept_encoding=True)
            conn.putheader("Content-Length", str(len(data)))
            conn.endheaders(data)
            resp = conn.getresponse()
            body = resp.read()
            status = resp.status
            if status < 400:
                return
            detail = body.decode("utf-8", errors="replace")[:500]
            if attempt == 0 and status in RETRYABLE_HTTP_STATUSES:
                retry_once(f"HTTP {status} while uploading to MinerU")
                continue
            sys.exit(f"HTTP {status} from MinerU API: {detail}")
        except (TimeoutError, OSError, http.client.HTTPException) as e:
            if attempt == 0:
                retry_once(f"Network error uploading to MinerU: {e}")
                continue
            sys.exit(f"Network error uploading to MinerU after retry: {e}")
        finally:
            if conn is not None:
                conn.close()


def api_call(method, url, token, **kwargs):
    resp = json.loads(http_request(method, url, token=token, **kwargs))
    if resp.get("code") != 0:
        sys.exit(f"MinerU API error: {json.dumps(resp, ensure_ascii=False)[:500]}")
    return resp["data"]


def main():
    ap = argparse.ArgumentParser(description="Convert PDF to Markdown via MinerU API")
    ap.add_argument("pdf", help="Path to the PDF file")
    ap.add_argument("--out", default=None,
                    help="Output directory (default: <pdf_dir>/<pdf_stem>_mineru/)")
    ap.add_argument("--token", default=None)
    ap.add_argument("--language", default="ch",
                    help="Document language hint, e.g. ch / en (default: ch)")
    ap.add_argument("--no-ocr", action="store_true",
                    help="Disable OCR (for PDFs with a reliable text layer)")
    ap.add_argument("--no-formula", action="store_true")
    ap.add_argument("--no-table", action="store_true")
    ap.add_argument("--timeout", type=int, default=900,
                    help="Max seconds to wait for conversion (default: 900)")
    ap.add_argument("--poll", type=int, default=5,
                    help="Polling interval in seconds (default: 5)")
    args = ap.parse_args()

    pdf = Path(args.pdf).expanduser().resolve()
    if not pdf.is_file():
        sys.exit(f"PDF not found: {pdf}")
    token = get_token(args.token)

    out_dir = (Path(args.out).expanduser().resolve() if args.out
               else pdf.parent / (pdf.stem + "_mineru"))
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Request an upload URL
    log(f"[1/4] Requesting upload URL for {pdf.name} ...")
    data = api_call("POST", f"{API_BASE}/file-urls/batch", token, payload={
        "enable_formula": not args.no_formula,
        "enable_table": not args.no_table,
        "language": args.language,
        "files": [{"name": pdf.name, "is_ocr": not args.no_ocr}],
    })
    batch_id = data["batch_id"]
    upload_url = data["file_urls"][0]
    log(f"      batch_id: {batch_id}")

    # 2. Upload the file (pre-signed URL, no auth/content-type headers)
    log(f"[2/4] Uploading {pdf.stat().st_size / 1024:.0f} KB ...")
    put_presigned(upload_url, pdf.read_bytes())

    # 3. Poll until done
    log("[3/4] Converting (polling) ...")
    deadline = time.time() + args.timeout
    zip_url = None
    while True:
        data = api_call("GET", f"{API_BASE}/extract-results/batch/{batch_id}", token)
        results = data.get("extract_result") or []
        state = results[0]["state"] if results else "pending"
        log(f"      state: {state}")
        if state == "done":
            zip_url = results[0]["full_zip_url"]
            break
        if state == "failed":
            sys.exit(f"MinerU conversion failed: {results[0].get('err_msg', '(no message)')}")
        if time.time() > deadline:
            sys.exit(f"Timed out after {args.timeout}s (batch_id={batch_id}). "
                     "Retry with a larger --timeout.")
        time.sleep(args.poll)

    # 4. Download the zip and extract
    log("[4/4] Downloading and extracting result ...")
    zip_bytes = http_request("GET", zip_url, timeout=600)
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        zf.extractall(out_dir)

    md_files = sorted(out_dir.rglob("*.md"),
                      key=lambda p: (p.name != "full.md", len(p.parts)))
    if not md_files:
        sys.exit(f"No .md file found in extracted result under {out_dir}")

    md_path = md_files[0]
    log(f"Done. Markdown: {md_path}")
    print(str(md_path))


if __name__ == "__main__":
    main()
