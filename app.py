import math
import mimetypes
import os
import sys
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlparse

from dotenv import dotenv_values
from flask import Flask, Response, abort, redirect, render_template, request

from config import ConfigError, load_config
from icons import icon, icon_paths

mimetypes.add_type("font/woff2", ".woff2")
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


def build_csp(analytics):
    scripts = ["'self'"] + ([analytics["script_origin"]] if analytics["enabled"] else [])
    connect = ["'self'"] + (analytics["connect_origins"] if analytics["enabled"] else [])
    return "; ".join([
        "default-src 'self'",
        f"script-src {' '.join(scripts)}",
        "style-src 'self'",
        "img-src 'self' data: https:",
        f"connect-src {' '.join(connect)}",
        "font-src 'self'",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'none'",
        "frame-ancestors 'none'",
    ])


def build_orbit(products):
    radii = (118, 168)
    count = len(products)
    nodes = []
    for i, p in enumerate(products):
        angle = math.radians(-38 + i * 360 / count + (24 if i % 2 else 0))
        r = radii[i % 2] if count > 1 else radii[0]
        nodes.append({"product": p, "x": round(r * math.cos(angle), 1), "y": round(r * math.sin(angle), 1)})
    return nodes


def create_app(env=None):
    env = {**dotenv_values(BASE_DIR / ".env"), **os.environ} if env is None else env
    config = load_config(env, STATIC_DIR)
    app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")
    app.config["HUB"] = config

    csp = build_csp(config["analytics"])
    orbit = build_orbit(config["products"])
    has_theme_css = any(p["accent"] for p in config["products"])

    @app.context_processor
    def inject():
        return {"c": config, "icon": icon, "icon_paths": icon_paths, "orbit": orbit,
                "has_theme_css": has_theme_css, "now_year": lambda: date.today().year}

    @app.template_filter("host")
    def host(href):
        return urlparse(href).netloc

    @app.after_request
    def secure(resp):
        resp.headers["Content-Security-Policy"] = csp
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        resp.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
        resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        resp.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        if config["app"]["is_production"]:
            resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        if request.path.endswith(".woff2"):
            resp.headers["Cache-Control"] = "public, max-age=604800"
        elif resp.mimetype == "text/html":
            resp.headers["Cache-Control"] = "no-cache" if resp.status_code == 200 else "no-store"
        return resp

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/about")
    def about():
        return render_template("pages/about.html")

    @app.get("/privacy")
    def privacy():
        return render_template("pages/privacy.html")

    @app.get("/terms")
    def terms():
        return render_template("pages/terms.html")

    @app.get("/contact")
    def contact():
        if not config["contact_email"]:
            abort(404)
        return render_template("pages/contact.html")

    @app.get("/healthz")
    def healthz():
        return Response("ok", mimetype="text/plain", headers={"Cache-Control": "no-store"})

    @app.get("/robots.txt")
    def robots():
        body = "User-agent: *\n" + ("Allow: /\n" if config["seo"]["indexable"] else "Disallow: /\n")
        return Response(body, mimetype="text/plain")

    @app.get("/theme.css")
    def theme_css():
        if not has_theme_css:
            abort(404)
        rules = "\n".join(f".product-{p['id']}{{--product-accent:{p['accent']}}}" for p in config["products"] if p["accent"])
        return Response(rules + "\n", mimetype="text/css")

    @app.get("/favicon.svg")
    def favicon_svg():
        if config["favicon"]:
            abort(404)
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#2d2a26"/>'
            f'<text x="32" y="44" text-anchor="middle" font-family="Georgia,serif" font-size="34" fill="#faf9f5">{escape(config["brand"]["mark"])}</text></svg>'
        )
        return Response(svg, mimetype="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})

    @app.get("/favicon.ico")
    def favicon_ico():
        return redirect(config["favicon"]["src"] if config["favicon"] else "/favicon.svg", 302)

    @app.errorhandler(404)
    def not_found(_):
        return render_template("message.html", code="404", label="Not Found", heading="Page not found",
                               text="The resource you are looking for has moved, been deleted, or never existed. Double-check the URL or head back to the platform."), 404

    @app.errorhandler(500)
    def server_error(_):
        return render_template("message.html", code="500", label="Server Error", heading="Something went wrong",
                               text="Something went wrong on our end. Please try again in a moment."), 500

    return app


try:
    app = create_app()
except ConfigError as err:
    print(err.format(), file=sys.stderr)
    sys.exit(1)

for warning in app.config["HUB"]["warnings"]:
    print(f"[config] {warning}", file=sys.stderr)

if __name__ == "__main__":
    hub = app.config["HUB"]["app"]
    app.run(host=hub["host"], port=hub["port"], debug=hub["debug"])
