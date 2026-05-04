#!/usr/bin/env python3
"""
Regenerate the sponsors carousel in templates/homepage.html from sponsors.yaml.
Downloads avatars into assets/img/sponsors/ on first run; skips existing files.

Usage:
    python tools/update_homepage_sponsors.py            # skip already-downloaded
    python tools/update_homepage_sponsors.py --redownload  # force re-fetch all
"""

import re
import sys
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SPONSORS_FILE = ROOT / "sponsors.yaml"
HOMEPAGE = ROOT / "templates" / "homepage.html"
IMG_DIR = ROOT / "assets" / "img" / "sponsors"

START = "<!-- SPONSORS-START -->"
END = "<!-- SPONSORS-END -->"

INDENT = "            "

MIME_EXT = {
    "image/jpeg": ".jpeg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
}


def download_avatar(key: str, url: str, *, redownload: bool = False) -> str:
    """Fetch avatar URL, save to assets/img/sponsors/{key}.ext, return web path."""
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    if not redownload:
        existing = next(IMG_DIR.glob(f"{key}.*"), None)
        if existing:
            return f"/img/sponsors/{existing.name}"

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        content_type = resp.headers.get_content_type()
        ext = MIME_EXT.get(content_type, ".png")
        data = resp.read()

    filename = f"{key}{ext}"
    (IMG_DIR / filename).write_bytes(data)
    print(f"  {filename}  ({len(data):,} bytes)  [{content_type}]")
    return f"/img/sponsors/{filename}"


def sponsor_item(s: dict, *, hidden: bool = False) -> str:
    extra_attrs = ' aria-hidden="true" tabindex="-1"' if hidden else ""
    alt = "" if hidden else s["name"]
    cls = "sponsor-item"
    if s.get("style") == "square":
        cls += " sponsor-item--square"
    name_span = (
        ""
        if hidden
        else f'\n{INDENT}  <span class="sponsor-item__name">{s["name"]}</span>'
    )
    return (
        f'{INDENT}<a class="{cls}"{extra_attrs}'
        f' href="{s["url"]}" target="_blank" rel="noopener">'
        f'\n{INDENT}  <img src="{s["local"]}" alt="{alt}" width="80" height="80" />'
        f"{name_span}"
        f"\n{INDENT}</a>"
    )


def build_block(sponsors: list) -> str:
    lines = [""]
    for s in sponsors:
        lines.append(sponsor_item(s))
    lines.append(
        f"{INDENT}<!-- Duplicate set for seamless loop (hidden from assistive tech) -->"
    )
    for s in sponsors:
        lines.append(sponsor_item(s, hidden=True))
    lines.append(f"{INDENT}")
    return "\n".join(lines)


def main() -> None:
    redownload = "--redownload" in sys.argv

    sponsors = yaml.safe_load(SPONSORS_FILE.read_text())

    print(f"Downloading avatars into {IMG_DIR.relative_to(ROOT)} ...")
    for s in sponsors:
        s["local"] = download_avatar(s["key"], s["avatar"], redownload=redownload)

    # Remove images whose key is no longer in the sponsors list.
    # Only touches flat files; leaves subdirectories (e.g. top/) alone.
    active_keys = {s["key"] for s in sponsors}
    for path in IMG_DIR.iterdir():
        if path.is_file() and path.stem not in active_keys:
            path.unlink()
            print(f"  removed {path.name}")

    html = HOMEPAGE.read_text()
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)

    replacement = START + build_block(sponsors) + END
    new_html, n = pattern.subn(replacement, html)

    if n == 0:
        print(
            f"ERROR: markers {START!r} / {END!r} not found in {HOMEPAGE}",
            file=sys.stderr,
        )
        sys.exit(1)

    HOMEPAGE.write_text(new_html)
    print(f"Updated {len(sponsors)} sponsors in {HOMEPAGE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
