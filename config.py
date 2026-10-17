import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from icons import ICON_NAMES

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}
APP_ENVS = ("development", "production", "test")
THEMES = {
    "sunset": "Sunset",
    "paper": "Paper",
    "dark": "Dark",
    "midnight": "Midnight",
    "emerald": "Emerald",
}
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EMAIL_RE = re.compile(r"^[^\s@<>\"',;:]+@[^\s@<>\"',;:]+\.[^\s@<>\"',;:]{2,}$")
ASSET_PATH_RE = re.compile(r"^/[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*$")
ASSET_EXTENSIONS = {".svg", ".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif", ".ico", ".mp4", ".webm"}
PRODUCT_FIELDS = (
    "NAME", "DESCRIPTION", "URL", "FALLBACK_URL", "ICON", "LOGO_PATH",
    "CATEGORY", "CTA_LABEL", "ACCENT", "VISIBLE", "ORDER",
)
MAX_LINKS = 12


class ConfigError(Exception):
    def __init__(self, problems, warnings=()):
        super().__init__(f"Invalid configuration: {len(problems)} problem(s) found.")
        self.problems = list(problems)
        self.warnings = list(warnings)

    def format(self):
        lines = ["", "The product hub cannot start because its configuration is invalid:", ""]
        lines += [f"  - {p}" for p in self.problems]
        lines += ["", "Fix the variables above in .env (local) or in your host's environment settings.", ""]
        return "\n".join(lines)


def parse_web_url(value, is_prod):
    try:
        u = urlparse(value)
        host = u.hostname
        u.port
    except ValueError:
        return None, "is not a valid absolute URL (expected something like https://example.com)"
    if u.scheme and u.scheme not in ("http", "https"):
        return None, f'uses the unsupported scheme "{u.scheme}:" (only https is allowed)'
    if not u.scheme or not host:
        return None, "is not a valid absolute URL (expected something like https://example.com)"
    if u.username or u.password:
        return None, "must not contain a username or password"
    local = host in LOCAL_HOSTS
    if u.scheme == "http" and (is_prod or not local):
        return None, "must use https (plain http is only allowed for localhost outside production)"
    if is_prod and local:
        return None, "points to localhost, which is not valid in production"
    return u._replace(path=u.path or "/", netloc=u.netloc.lower()).geturl(), None


def resolve_target(value, is_prod):
    if re.match(r"^#[A-Za-z][\w-]*$", value):
        return {"href": value, "external": False}, None
    if value.lower().startswith("mailto:"):
        addr = value[7:]
        if not EMAIL_RE.match(addr):
            return None, "has an invalid mailto: address"
        return {"href": f"mailto:{addr}", "external": False}, None
    href, err = parse_web_url(value, is_prod)
    if err:
        return None, err
    return {"href": href, "external": True}, None


class Reader:
    def __init__(self, env, is_prod, static_dir):
        self.env = env
        self.is_prod = is_prod
        self.static_dir = Path(static_dir)
        self.problems = []
        self.warnings = []

    def raw(self, name):
        v = self.env.get(name)
        if v is None:
            return None
        v = str(v).strip()
        return v or None

    def bad(self, name, msg):
        self.problems.append(f"{name} {msg}")

    def str(self, name, default=None, max=200, required=False, example=None):
        v = self.raw(name)
        if v is None:
            if required:
                self.bad(name, f"is required{f' (example: {name}={example})' if example else ''}.")
            return default
        if len(v) > max:
            self.bad(name, f"is too long ({len(v)} characters, maximum {max}).")
            return default
        return v

    def bool(self, name, default):
        v = self.raw(name)
        if v is None:
            return default
        t = v.lower()
        if t in ("true", "1", "yes", "on"):
            return True
        if t in ("false", "0", "no", "off"):
            return False
        self.bad(name, f'must be true or false (got "{v}").')
        return default

    def one_of(self, name, allowed, default):
        v = self.raw(name)
        if v is None:
            return default
        t = v.lower()
        if t in allowed:
            return t
        self.bad(name, f'must be one of: {", ".join(allowed)} (got "{v}").')
        return default

    def int(self, name, default=None, min=-(10**9), max=10**9):
        v = self.raw(name)
        if v is None:
            return default
        try:
            n = int(v)
        except ValueError:
            n = None
        if n is None or n < min or n > max:
            self.bad(name, f'must be a whole number between {min} and {max} (got "{v}").')
            return default
        return n

    def list(self, name):
        v = self.raw(name)
        return [] if v is None else [s.strip() for s in v.split(",") if s.strip()]

    def hex(self, name):
        v = self.raw(name)
        if v is None:
            return None
        if not HEX_RE.match(v):
            self.bad(name, f'must be a 6-digit hex colour such as #3b4cca (got "{v}").')
            return None
        return v.lower()

    def email(self, name):
        v = self.raw(name)
        if v is None:
            return None
        if not EMAIL_RE.match(v) or len(v) > 254:
            self.bad(name, f'is not a valid email address (got "{v}").')
            return None
        return v

    def url(self, name, required=False):
        v = self.raw(name)
        if v is None:
            if required:
                self.bad(name, "is required (an absolute https:// URL).")
            return None
        href, err = parse_web_url(v, self.is_prod)
        if err:
            self.bad(name, f'{err} (got "{v}").')
            return None
        return href

    def asset(self, name):
        v = self.raw(name)
        if v is None:
            return None
        if v.startswith("/"):
            if not ASSET_PATH_RE.match(v) or ".." in v.split("/") or "//" in v:
                self.bad(name, f'must look like /logo.mp4 or /assets/your-file.svg (letters, digits, . _ - / only) or be an https URL (got "{v}").')
                return None
            if Path(v).suffix.lower() not in ASSET_EXTENSIONS:
                self.bad(name, f'must be an image or video file ({", ".join(sorted(ASSET_EXTENSIONS))}) (got "{v}").')
                return None
            if not (self.static_dir / v.lstrip("/")).is_file():
                self.bad(name, f'refers to "{v}" but no such file exists in the static/ folder.')
                return None
            return {"src": v, "local": True}
        href, err = parse_web_url(v, self.is_prod)
        if err:
            self.bad(name, f'{err} (got "{v}").')
            return None
        return {"src": href, "local": False}

    def links(self, name):
        v = self.raw(name)
        if v is None:
            return []
        try:
            data = json.loads(v)
        except json.JSONDecodeError as e:
            self.bad(name, f'is not valid JSON ({e.msg}). Expected e.g. [{{"label":"Docs","url":"https://example.com/docs"}}].')
            return []
        if not isinstance(data, list):
            self.bad(name, 'must be a JSON array of {"label": "...", "url": "..."} objects.')
            return []
        if len(data) > MAX_LINKS:
            self.bad(name, f"has too many entries ({len(data)}, maximum {MAX_LINKS}).")
        out = []
        for i, item in enumerate(data[:MAX_LINKS]):
            where = f"{name}[{i}]"
            if not isinstance(item, dict) or not isinstance(item.get("label"), str) or not isinstance(item.get("url"), str):
                self.bad(where, 'must be an object with string "label" and "url" properties.')
                continue
            label = item["label"].strip()
            if not label or len(label) > 40:
                self.bad(where, "has an empty or too long label (maximum 40 characters).")
                continue
            target, err = resolve_target(item["url"].strip(), self.is_prod)
            if err:
                self.bad(where, f"url {err}.")
                continue
            out.append({"label": label, **target})
        return out

    def link(self, name, label):
        v = self.raw(name)
        if v is None:
            return None
        target, err = resolve_target(v, self.is_prod)
        if err:
            self.bad(name, f'{err} (got "{v}").')
            return None
        return {"label": label, **target}


def load_config(env, static_dir):
    r = Reader(env, True, static_dir)
    app_env = r.one_of("APP_ENV", APP_ENVS, "production")
    is_prod = app_env == "production"
    r.is_prod = is_prod
    name = r.str("APP_NAME", "Product Hub", 60)
    tagline = r.str("APP_TAGLINE", max=120)
    description = r.str("APP_DESCRIPTION", max=300)
    port = r.int("PORT", 3000, 1, 65535)
    host = r.str("HOST", "0.0.0.0" if is_prod else "127.0.0.1", 100)

    base_url = None
    base_raw = r.url("APP_BASE_URL")
    if base_raw:
        u = urlparse(base_raw)
        if u.path not in ("", "/") or u.query or u.fragment:
            r.bad("APP_BASE_URL", f'must be an origin only, without a path, query or fragment (got "{base_raw}").')
        else:
            base_url = f"{u.scheme}://{u.netloc}"

    logo = r.asset("BRAND_LOGO_PATH")
    logo_dark = r.asset("BRAND_LOGO_DARK_PATH")
    if logo_dark and not logo:
        r.bad("BRAND_LOGO_DARK_PATH", "requires BRAND_LOGO_PATH to be set as well.")
    mark = r.str("BRAND_MARK_TEXT", max=3) or (name.strip()[:1].upper() or "?")
    brand = {
        "logo": logo,
        "logo_dark": logo_dark if logo else None,
        "hide_name": r.bool("BRAND_LOGO_HIDE_NAME", False) and bool(logo),
        "mark": mark,
    }
    favicon = r.asset("FAVICON_PATH")

    hero_description = r.str("HERO_DESCRIPTION", max=200)
    secondary_label = r.str("HERO_SECONDARY_CTA_LABEL", max=30)
    secondary = r.link("HERO_SECONDARY_CTA_URL", secondary_label)
    if bool(secondary_label) != bool(secondary):
        r.warnings.append("HERO_SECONDARY_CTA_LABEL and HERO_SECONDARY_CTA_URL must both be set to show the secondary button; it is hidden.")
    hero = {
        "headline": r.str("HERO_HEADLINE", "Our products, in one place", 90),
        "description": hero_description,
        "primary_label": r.str("HERO_PRIMARY_CTA_LABEL", "View products", 30),
        "secondary": secondary if secondary_label and secondary else None,
    }

    section = {
        "title": r.str("PRODUCTS_TITLE", "Products", 60),
        "fallback_label": r.str("PRODUCTS_FALLBACK_LABEL", "Backup site", 30),
        "new_tab": r.bool("PRODUCTS_OPEN_IN_NEW_TAB", True),
        "default_cta": r.str("PRODUCTS_DEFAULT_CTA_LABEL", "Open product", 30),
    }

    ids = [i.lower() for i in r.list("PRODUCT_IDS")]
    products = []
    if not ids:
        r.bad("PRODUCT_IDS", "is required: a comma-separated list of product ids, e.g. PRODUCT_IDS=my-app,other-app. Each id then needs PRODUCT_<ID>_NAME, _DESCRIPTION and _URL.")
    seen = set()
    for index, pid in enumerate(ids):
        if not ID_RE.match(pid):
            r.bad("PRODUCT_IDS", f'contains the invalid id "{pid}" (use lowercase letters, digits and single hyphens).')
            continue
        if pid in seen:
            r.bad("PRODUCT_IDS", f'lists "{pid}" more than once.')
            continue
        seen.add(pid)
        p = f"PRODUCT_{pid.upper().replace('-', '_')}_"
        url = r.url(f"{p}URL", required=True)
        fallback = r.url(f"{p}FALLBACK_URL")
        if url and fallback and url == fallback:
            r.bad(f"{p}FALLBACK_URL", "must differ from the primary URL.")
        products.append({
            "id": pid,
            "name": r.str(f"{p}NAME", required=True, max=60, example="My App"),
            "description": r.str(f"{p}DESCRIPTION", required=True, max=300, example="What the product does."),
            "url": url,
            "fallback_url": fallback,
            "icon": r.one_of(f"{p}ICON", ICON_NAMES, "box"),
            "logo": r.asset(f"{p}LOGO_PATH"),
            "category": r.str(f"{p}CATEGORY", max=40),
            "cta_label": r.str(f"{p}CTA_LABEL", section["default_cta"], 30),
            "accent": r.hex(f"{p}ACCENT"),
            "visible": r.bool(f"{p}VISIBLE", True),
            "order": r.int(f"{p}ORDER", (index + 1) * 10, -100000, 100000),
            "index": index,
        })

    known = {i.upper().replace("-", "_") for i in ids if ID_RE.match(i)}
    orphan_re = re.compile(rf"^PRODUCT_([A-Z0-9_]+?)_(?:{'|'.join(PRODUCT_FIELDS)})$")
    orphans = {m.group(1) for k in env if (m := orphan_re.match(k)) and m.group(1) not in known and r.raw(k)}
    for key in sorted(orphans):
        r.warnings.append(f'Variables starting with PRODUCT_{key}_ were found but "{key.lower().replace("_", "-")}" is not listed in PRODUCT_IDS, so they are ignored.')

    visible = sorted((p for p in products if p["visible"]), key=lambda p: (p["order"], p["index"]))
    if ids and not visible and not r.problems:
        r.bad("PRODUCT_IDS", "has no visible products; set at least one PRODUCT_<ID>_VISIBLE to true.")

    contact_email = r.email("CONTACT_EMAIL")
    support_url = r.url("SUPPORT_URL")
    support = {"label": r.str("SUPPORT_LABEL", "Support", 30), "href": support_url, "external": True} if support_url else None
    contact = {"label": r.str("CONTACT_LABEL", "Contact", 30), "href": f"mailto:{contact_email}", "external": False} if contact_email else None
    docs_url = r.url("DOCS_URL")
    docs = {"label": r.str("DOCS_LABEL", "Documentation", 30), "href": docs_url, "external": True} if docs_url else None

    nav = r.links("NAV_LINKS_JSON")
    extra = support or contact
    if extra:
        nav.append(extra)

    cta_label = r.str("HEADER_CTA_LABEL", max=30)
    cta = r.link("HEADER_CTA_URL", cta_label)
    if bool(cta_label) != bool(cta):
        r.warnings.append("HEADER_CTA_LABEL and HEADER_CTA_URL must both be set to show the header button; it is hidden.")

    start_year = r.int("COPYRIGHT_START_YEAR", None, 1970, 9999)
    if start_year and start_year > date.today().year:
        r.bad("COPYRIGHT_START_YEAR", f"is in the future ({start_year}).")
    footer_links = r.links("FOOTER_LINKS_JSON")
    if docs:
        footer_links.insert(0, docs)
    footer = {
        "links": footer_links + ([support] if support else []) + r.links("SOCIAL_LINKS_JSON"),
        "owner": r.str("COPYRIGHT_OWNER", name, 80),
        "start_year": start_year,
    }

    chosen = list(dict.fromkeys(t.lower() for t in r.list("SUPPORTED_THEMES"))) or list(THEMES)
    invalid = [t for t in chosen if t not in THEMES]
    if invalid:
        r.bad("SUPPORTED_THEMES", f'contains unsupported values: {", ".join(invalid)} (supported: {", ".join(THEMES)}).')
        chosen = list(THEMES)
    theme = {
        "options": [{"id": t, "label": THEMES[t]} for t in chosen],
        "default": r.one_of("DEFAULT_THEME", chosen, "sunset" if "sunset" in chosen else chosen[0]),
        "selector": len(chosen) > 1,
    }
    motion = r.bool("ANIMATIONS_ENABLED", True)

    seo_image = r.asset("SEO_IMAGE_PATH")
    image_url = None
    if seo_image:
        if not seo_image["local"]:
            image_url = seo_image["src"]
        elif base_url:
            image_url = base_url + seo_image["src"]
        else:
            r.warnings.append("SEO_IMAGE_PATH is a local file but APP_BASE_URL is not set, so the social-sharing image is omitted (it needs an absolute URL).")
    seo_index = r.bool("SEO_INDEX", True)
    seo = {
        "title": r.str("SEO_TITLE", f"{name} – {tagline}" if tagline else name, 90),
        "description": r.str("SEO_DESCRIPTION", description or hero_description, 300),
        "canonical": f"{base_url}/" if base_url else None,
        "image": image_url,
        "image_alt": r.str("SEO_IMAGE_ALT", max=200) if image_url else None,
        "indexable": seo_index and is_prod,
    }
    if seo_index and not is_prod:
        r.warnings.append(f'APP_ENV is "{app_env}", so search engines are told not to index this instance (noindex).')

    analytics = {"enabled": False, "provider": None, "id": None, "script_url": None, "script_origin": None, "connect_origins": []}
    if r.bool("ANALYTICS_ENABLED", False):
        provider = r.one_of("ANALYTICS_PROVIDER", ("plausible", "ga4"), None)
        aid = r.str("ANALYTICS_ID", max=100)
        if not provider or not aid:
            r.warnings.append("ANALYTICS_ENABLED is true but ANALYTICS_PROVIDER or ANALYTICS_ID is missing, so analytics stays disabled.")
        elif not is_prod:
            r.warnings.append("Analytics is only loaded when APP_ENV=production; it stays disabled here.")
        elif provider == "ga4" and not re.match(r"^G-[A-Z0-9]{4,}$", aid):
            r.bad("ANALYTICS_ID", f'must look like G-XXXXXXXXXX for ga4 (got "{aid}").')
        elif provider == "plausible" and not re.match(r"^[a-z0-9.-]+$", aid, re.I):
            r.bad("ANALYTICS_ID", f'must be the site domain, e.g. example.com, for plausible (got "{aid}").')
        else:
            script_url = r.url("ANALYTICS_SCRIPT_URL") or (
                "https://plausible.io/js/script.js" if provider == "plausible" else "https://www.googletagmanager.com/gtag/js"
            )
            su = urlparse(script_url)
            origin = f"{su.scheme}://{su.netloc}"
            analytics.update(
                enabled=True, provider=provider, id=aid, script_url=script_url, script_origin=origin,
                connect_origins=[origin, "https://www.google-analytics.com", "https://*.google-analytics.com", "https://*.analytics.google.com"]
                if provider == "ga4" else [origin],
            )

    if r.problems:
        raise ConfigError(r.problems, r.warnings)

    return {
        "warnings": r.warnings,
        "app": {"name": name, "tagline": tagline, "description": description, "base_url": base_url,
                "env": app_env, "is_production": is_prod, "debug": r.bool("DEBUG", False), "port": port, "host": host},
        "brand": brand,
        "favicon": favicon,
        "hero": hero,
        "section": section,
        "products": visible,
        "nav": nav,
        "header_cta": cta if cta_label and cta else None,
        "contact_email": contact_email,
        "footer": footer,
        "theme": theme,
        "motion": motion,
        "seo": seo,
        "analytics": analytics,
    }
