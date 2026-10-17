<div align="center">

<img src="static/favicon.png" alt="Sarvadwar" width="72" height="72">

# Sarvadwar

**One gateway to every product.**

A configuration-driven product hub that lists your software products and opens each one in a click.
Built with Flask. Every name, link, theme and footer detail comes from a single `.env` file.

</div>

---

## Highlights

- **Editorial landing page** with an animated hero, an ecosystem orbit graphic and a distinct showcase panel per product.
- **Five themes** — Sunset, Paper, Dark, Midnight and Emerald — with a circular-wipe theme switch. The choice is remembered in the browser.
- **Fully `.env` driven.** Add, hide, reorder or rename a product by editing configuration; no template or code change.
- **Logo and favicon from files.** Use an image or a looping `.mp4` logo.
- **Mobile first**, keyboard accessible, and reduced-motion aware.
- **Secure by default:** strict Content-Security-Policy with no inline scripts or styles, HTTPS-only product links in production, and HTML-escaped content.
- **No database, no accounts, no tracking.** Analytics (Plausible or GA4) stays off unless you enable it.

## Quick start

Requires Python 3.11+.

```bash
git clone https://github.com/Jainarayan-Singh/sarvadwar.git
cd sarvadwar
python -m venv .venv
.venv\Scripts\activate          # macOS / Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://localhost:3000.

If a value in `.env` is invalid, the app refuses to start and prints every problem with the variable name.

## Add a product

1. Add an id to `PRODUCT_IDS` (the order is the display order):

   ```ini
   PRODUCT_IDS=smart-ai-exam,penny-wise,my-new-app
   ```

2. Add its settings. The prefix is `PRODUCT_<ID>_` with the id upper-cased and hyphens turned into underscores:

   ```ini
   PRODUCT_MY_NEW_APP_NAME=My New App
   PRODUCT_MY_NEW_APP_DESCRIPTION=One factual sentence about the product.
   PRODUCT_MY_NEW_APP_URL=https://my-new-app.example.com
   PRODUCT_MY_NEW_APP_ICON=chart
   PRODUCT_MY_NEW_APP_CATEGORY=Productivity
   PRODUCT_MY_NEW_APP_ACCENT="#b45309"
   ```

3. Restart. The new showcase panel and its orbit node appear automatically.

| Variable (`PRODUCT_<ID>_…`) | Required | Notes |
| --- | --- | --- |
| `NAME`, `DESCRIPTION`, `URL` | yes | `URL` must be `https` (`http://localhost` only outside production) |
| `FALLBACK_URL` | no | Adds a secondary "Backup site" button |
| `ICON` | no | `box`, `graduation-cap`, `wallet`, `book`, `chart`, `calendar`, `chat`, `code`, `shield`, `mail`, `globe`, `layers`, `sparkles`, `check-circle`, `pencil`, `home` |
| `LOGO_PATH` | no | `/assets/…` image or `https` URL; replaces the icon |
| `CATEGORY`, `CTA_LABEL` | no | Label above the name, and the button text |
| `ACCENT` | no | Quoted `"#rrggbb"`; gives the product its own colour identity |
| `VISIBLE`, `ORDER` | no | Hide a product without deleting it; override the sort order |

## Configuration

| Area | Variables |
| --- | --- |
| App | `APP_ENV`, `DEBUG`, `PORT`, `HOST`, `APP_BASE_URL`, `APP_NAME`, `APP_TAGLINE`, `APP_DESCRIPTION` |
| Brand | `BRAND_LOGO_PATH`, `BRAND_LOGO_DARK_PATH`, `BRAND_LOGO_HIDE_NAME`, `BRAND_MARK_TEXT`, `FAVICON_PATH` |
| Hero | `HERO_HEADLINE`, `HERO_DESCRIPTION`, `HERO_PRIMARY_CTA_LABEL`, `HERO_SECONDARY_CTA_LABEL`, `HERO_SECONDARY_CTA_URL` |
| Products | `PRODUCT_IDS`, `PRODUCTS_TITLE`, `PRODUCTS_OPEN_IN_NEW_TAB`, `PRODUCTS_DEFAULT_CTA_LABEL`, `PRODUCTS_FALLBACK_LABEL` |
| Navigation | `NAV_LINKS_JSON`, `HEADER_CTA_LABEL`, `HEADER_CTA_URL` |
| Footer | `CONTACT_EMAIL`, `SUPPORT_URL`, `DOCS_URL`, `PRIVACY_URL`, `TERMS_URL`, `SOCIAL_LINKS_JSON`, `FOOTER_LINKS_JSON`, `COPYRIGHT_OWNER`, `COPYRIGHT_START_YEAR` |
| Theme | `SUPPORTED_THEMES`, `DEFAULT_THEME`, `ANIMATIONS_ENABLED` |
| SEO | `SEO_TITLE`, `SEO_DESCRIPTION`, `SEO_IMAGE_PATH`, `SEO_IMAGE_ALT`, `SEO_INDEX` |
| Analytics | `ANALYTICS_ENABLED`, `ANALYTICS_PROVIDER`, `ANALYTICS_ID`, `ANALYTICS_SCRIPT_URL` |

Optional pieces that are not configured (contact, social and legal links, header button, secondary hero button, analytics) are left out of the page entirely. Real environment variables always override `.env`, and values containing `#` must be quoted.

Search engines are told `noindex` unless `APP_ENV=production`. A canonical URL is emitted only when `APP_BASE_URL` is set.

## Deploy

Sarvadwar is a plain Flask app, so it runs on Render, Railway, Fly.io or any host with Python.

| Setting | Value |
| --- | --- |
| Build command | `pip install -r requirements.txt` |
| Start command | `gunicorn app:app` |
| Health check | `/healthz` |
| Environment | `APP_ENV=production`, `APP_BASE_URL=https://your-domain`, plus your product variables |

On a host, set the variables in its dashboard instead of relying on the committed `.env`; real environment variables take precedence.

## Project structure

```
app.py            Flask app, routes, security headers
config.py         .env parsing and validation
icons.py          built-in icon set
templates/        base, index and error pages (Jinja)
static/           css, js, fonts, logo.mp4, favicon.png
requirements.txt
.env              all configuration
```

## Credits

Typography: [Newsreader](https://fonts.google.com/specimen/Newsreader) and [DM Sans](https://fonts.google.com/specimen/DM+Sans), self-hosted under the SIL Open Font License.
Theme palettes follow the Smart AI Exam Portal.

## License

See [LICENSE](LICENSE).
