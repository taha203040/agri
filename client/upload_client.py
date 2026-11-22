"""
Small CLI client for the Agri RAG API — uploads documents for ingestion.

Usage:
    python client/upload_client.py --topic soil path/to/guide.pdf
    python client/upload_client.py --topic water data/raw/water/

Environment (optional):
    AGRI_API_URL   default http://localhost:8000
    AGRI_API_KEY   sent as the X-API-Key header (used once the gateway step adds auth)
"""

import argparse
import os
import sys
from pathlib import Path

import httpx

SUPPORTED = {".txt", ".md", ".pdf", ".docx", ".html", ".htm"}
TOPICS = ["soil", "disease", "water", "crop_health", "yield"]


def collect_files(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for p in map(Path, paths):
        if p.is_dir():
            files += sorted(
                f for f in p.rglob("*")
                if f.is_file() and f.suffix.lower() in SUPPORTED
            )
        elif p.is_file():
            files.append(p)
        else:
            print(f"skip (not found): {p}", file=sys.stderr)
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload documents to the Agri RAG API.")
    parser.add_argument("paths", nargs="+", help="files or folders")
    parser.add_argument("--topic", required=True, choices=TOPICS)
    parser.add_argument("--url", default=os.getenv("AGRI_API_URL", "http://localhost:8000"))
    args = parser.parse_args()

    headers = {}
    api_key = os.getenv("AGRI_API_KEY")
    if api_key:
        headers["X-API-Key"] = api_key

    files = collect_files(args.paths)
    if not files:
        sys.exit("No supported files found.")

    failed = 0
    with httpx.Client(base_url=args.url, headers=headers, timeout=120) as client:
        for f in files:
            try:
                with f.open("rb") as fh:
                    r = client.post(
                        "/ingest",
                        data={"topic": args.topic},
                        files={"file": (f.name, fh)},
                    )
            except httpx.HTTPError as e:
                failed += 1
                print(f"FAIL {f.name}  {e}")
                continue

            if r.status_code == 200:
                d = r.json()
                tag = "duplicate" if d["duplicate"] else d["status"]
                print(f"OK   {f.name}  id={d['doc_id']}  [{tag}]")
            else:
                failed += 1
                print(f"FAIL {f.name}  {r.status_code} {r.text}")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
