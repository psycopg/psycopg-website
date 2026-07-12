#!/usr/bin/env python3
"""
Regenerate the sponsor listings from sponsors.yaml:

  * the scrolling carousel in templates/homepage.html (current sponsors only),
  * the tiered sponsor wall in templates/sponsors.html (all sponsors, grouped
    by tier; past sponsors are merged in as a thank-you).

Avatars are downloaded into assets/img/sponsors/ on first run; existing files
are skipped.

Usage:
    python tools/update_sponsors.py             # skip already-downloaded
    python tools/update_sponsors.py --redownload  # force re-fetch all
"""

import html
import re
import sys
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SPONSORS_FILE = ROOT / "sponsors.yaml"
HOMEPAGE = ROOT / "templates" / "homepage.html"
SPONSORS_PAGE = ROOT / "templates" / "sponsors.html"
IMG_DIR = ROOT / "assets" / "img" / "sponsors"

# Carousel markers (homepage)
START = "<!-- SPONSORS-START -->"
END = "<!-- SPONSORS-END -->"

# Sponsor wall markers (sponsors page)
WALL_START = "<!-- SPONSOR-WALL-START -->"
WALL_END = "<!-- SPONSOR-WALL-END -->"

INDENT = "            "
WALL_INDENT = "      "

# Tiers shown on the sponsor wall, in display order. `logo` tiers show the
# avatar (sized down gold -> bronze via CSS); backers are listed by name only.
# The `supporter` tier is intentionally absent: those get the GitHub badge only.
TIERS = [
    {"key": "gold", "label": "Gold sponsors", "logo": True, "size": 176},
    {"key": "silver", "label": "Silver sponsors", "logo": True, "size": 112},
    {"key": "bronze", "label": "Bronze sponsors", "logo": True, "size": 72},
    {"key": "backer", "label": "Backers", "logo": False, "size": 0},
]

# Tiers whose sponsors are shown with a logo/avatar on the sponsors page.
LOGO_TIERS = {t["key"] for t in TIERS if t["logo"]}


def needs_avatar(s: dict) -> bool:
    """An avatar is only used if the sponsor is shown with a logo somewhere:
    in a logo tier on the sponsors page, or in the homepage carousel (which
    lists current sponsors only). Name-only past backers need no image."""
    return s.get("tier") in LOGO_TIERS or not s.get("past")

MIME_EXT = {
    "image/jpeg": ".jpeg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
}


def download_avatar(key: str, url: str, *, redownload: bool = False) -> str:
    """Fetch avatar URL, save to assets/img/sponsors/{key}.ext, return web path."""
    # A local path (e.g. a committed logo whose GitHub user no longer exists)
    # is used as-is - nothing to download.
    if url.startswith("/"):
        return url

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


# ── Homepage carousel ───────────────────────────────────────────────────


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


# ── Sponsor wall (sponsors page) ────────────────────────────────────────


def wall_item(s: dict, tier: dict) -> str:
    href = s.get("url") or s.get("github")
    name = html.escape(s["name"])
    indent = WALL_INDENT + "    "
    if tier["logo"]:
        cls = "sponsor-wall__item"
        if s.get("style") == "square":
            cls += " sponsor-wall__item--square"
        size = tier["size"]
        return (
            f'{indent}<a class="{cls}" href="{href}" target="_blank" rel="noopener" title="{name}">\n'
            f'{indent}  <img src="{s["local"]}" alt="{name}" width="{size}" height="{size}" />\n'
            f'{indent}  <span class="sponsor-wall__name">{name}</span>\n'
            f"{indent}</a>"
        )
    return (
        f'{indent}<a class="sponsor-wall__item sponsor-wall__item--name"'
        f' href="{href}" target="_blank" rel="noopener">{name}</a>'
    )


def build_wall(sponsors: list) -> str:
    lines = [""]
    for tier in TIERS:
        group = [s for s in sponsors if s.get("tier") == tier["key"]]
        if not group:
            continue
        lines.append(
            f'{WALL_INDENT}<section class="sponsor-wall__group sponsor-wall__group--{tier["key"]}">'
        )
        lines.append(f'{WALL_INDENT}  <h2 class="sponsor-wall__tier">{tier["label"]}</h2>')
        lines.append(f'{WALL_INDENT}  <div class="sponsor-wall__items">')
        for s in group:
            lines.append(wall_item(s, tier))
        lines.append(f"{WALL_INDENT}  </div>")
        lines.append(f"{WALL_INDENT}</section>")
    lines.append(WALL_INDENT)
    return "\n".join(lines)


# ── Shared ──────────────────────────────────────────────────────────────


def replace_between(path: Path, start: str, end: str, block: str) -> None:
    text = path.read_text()
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    new_text, n = pattern.subn(start + block + end, text)
    if n == 0:
        print(
            f"ERROR: markers {start!r} / {end!r} not found in {path}",
            file=sys.stderr,
        )
        sys.exit(1)
    path.write_text(new_text)


def main() -> None:
    redownload = "--redownload" in sys.argv

    sponsors = yaml.safe_load(SPONSORS_FILE.read_text())

    print(f"Downloading avatars into {IMG_DIR.relative_to(ROOT)} ...")
    for s in sponsors:
        if needs_avatar(s):
            s["local"] = download_avatar(s["key"], s["avatar"], redownload=redownload)

    # Remove images no longer needed (dropped sponsors, or name-only backers).
    # Only touches flat files; leaves subdirectories (e.g. top/) alone.
    active_keys = {s["key"] for s in sponsors if needs_avatar(s)}
    for path in IMG_DIR.iterdir():
        if path.is_file() and path.stem not in active_keys:
            path.unlink()
            print(f"  removed {path.name}")

    # Homepage carousel: current sponsors only (past ones are kept off it).
    current = [s for s in sponsors if not s.get("past")]
    replace_between(HOMEPAGE, START, END, build_block(current))
    print(f"Updated {len(current)} sponsors in {HOMEPAGE.relative_to(ROOT)}")

    # Sponsor wall: everyone, grouped by tier.
    replace_between(SPONSORS_PAGE, WALL_START, WALL_END, build_wall(sponsors))
    print(f"Updated {len(sponsors)} sponsors in {SPONSORS_PAGE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
