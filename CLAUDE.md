# CLAUDE.md

Source for **https://www.psycopg.org** — a [Lektor](https://www.getlektor.com/)
static site. Built by CI and deployed to the `psycopg/psycopg.github.io` GitHub
Pages repo.

## Build & serve

Requires the venv in `env/` (created by `make setup`; `make` uses `env/bin/lektor`).

- `make setup` — create `env/` venv, install `requirements.txt` (includes lektor).
- `make serve` — Lektor dev server on http://localhost:5000/.
- `make` / `make build` — full build: generate psycopg2 docs (`docs`), psycopg3
  docs (`docs3`), then `lektor build -O build`. Output goes to `build/`, which is
  itself a git clone of `psycopg/psycopg.github.io`.
- `make publish` — commit & push `build/` (the Pages repo).

`docs`/`docs3` clone the `psycopg2` and `psycopg` (into `psycopg3/`) repos and
build their Sphinx docs, injecting `templates/docs-layout.html` /
`databags/analytics.json` as the docs layout. These subdirs are external checkouts,
not part of this repo's source — don't edit them here.

### Deploy

- `.github/workflows/build.yml` — on push to `master` (and on `repository_dispatch`
  from psycopg2/psycopg3 commits): runs `codespell`, `make setup`, `make`, then
  deploys `build/` to `psycopg/psycopg.github.io`.
- `codespell` runs in CI (config in `pyproject.toml`) — keep spelling clean or the
  build fails.
- Preview: `tools/upload-preview` builds and deploys to Cloudflare Pages (needs
  `CLOUDFLARE_ACCOUNT` / `CLOUDFLARE_API_TOKEN`).

## Layout of the source

- `psycopg.lektorproject` — Lektor project config + plugins (rst, tags, atom).
- `content/` — page sources: each dir has a `contents.lr` (`_model:` + fields,
  `---`-separated). Body is reStructuredText.
- `templates/` — Jinja2 (`htmldjango`) templates. `layout.html` is the base;
  normal pages `{% extends "layout.html" %}`.
- `models/` — content model field definitions (`page`, `raw`, `blog`, etc.).
- `configs/` — Lektor plugin configs (atom feed, tags, blog archive).
- `databags/` — `analytics.json`, `website.json`: data exposed to templates.
- `assets/` — copied verbatim to the site root (`css/`, `js/`, `img/`, `CNAME`,
  `robots.txt`, `manifest.json`). Main stylesheet: `assets/css/style.css`; design
  tokens (colors, etc.) live in the `:root` block at the top.
- `build/` — build output (a git clone of the Pages repo); not source.
- `homepage.bak/` — stale backup, ignore.

### Homepage is a special case

`content/contents.lr` uses `_model: raw` with `body_file: homepage.html`, and
`templates/raw.html` just `{% include %}`s it. So **`templates/homepage.html` is a
full standalone HTML document** (its own `<!doctype>`, nav, footer) and does **not**
extend `layout.html`. Nav/footer markup is therefore duplicated: a change to the
shared chrome must be made in **both** `layout.html` and `homepage.html`.

## Sponsors pipeline

`sponsors.yaml` is the **single source of truth** for both the homepage carousel and
the `/sponsors/` page. After editing it, run:

```
python tools/update_sponsors.py            # --redownload to force re-fetch avatars
```

This regenerates the marker-delimited blocks in place — do **not** hand-edit between
the markers, regenerate instead:

- `templates/homepage.html` — `<!-- SPONSORS-START -->` … `<!-- SPONSORS-END -->`
  (current platinum/gold/silver/bronze sponsors only, per `CAROUSEL_TIERS`; backers
  are on `/sponsors/` only; carousel is duplicated for a seamless loop).
- `templates/sponsors.html` — `<!-- SPONSOR-WALL-START -->` … `<!-- SPONSOR-WALL-END -->`
  (all current sponsors, grouped by tier).

Avatars are downloaded to `assets/img/sponsors/{key}.ext` on first run; a leading-`/`
`avatar:` is treated as an already-committed local path. Unused images are pruned.
Names are HTML-escaped in the generated markup.

`sponsors.yaml` entry fields:

- `key` — id + local avatar filename.
- `name` — display name.
- `url` — sponsor site (falls back to `github`).
- `github` — profile URL (avatar source / lookup).
- `avatar` — image URL to download (or a local `/img/...` path). May be omitted for
  a `backer` with no logo: they are then kept off the homepage carousel.
- `style` — `round` (default) | `square` (org/product logos).
- `tier` — `gold` | `silver` | `bronze` (shown with a logo, sized down by tier via
  CSS) | `backer` (name only). A `supporter` tier, if present, is intentionally not
  rendered (GitHub badge only).
- `past` — `true` for former sponsors: kept in `sponsors.yaml` for the record, but
  not displayed anywhere (their avatars are pruned).

Sponsor styling lives in `assets/css/style.css` (`.sponsor-item*` for the homepage
carousel, `.sponsor-wall__*` for the `/sponsors/` page). `square` sponsors get the
`--square` modifier class. The pale strip/tile background is the `--bg-strip` token.
