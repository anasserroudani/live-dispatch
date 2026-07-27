"""
Build a single, self-contained HTML file you can send to a friend.

    python build_static.py

It fetches the latest news (if the cache is empty/stale), renders the whole
app as ONE file with the CSS and icon inlined, and writes it to:

    share/live-dispatch.html

Your friend just double-clicks that file — no Python, no server, no internet
needed for the app itself (article links still open in their browser). The
news is a snapshot from the moment you run this; the Learn/Connect sections are
always current. Re-run it any time for a fresh snapshot.
"""

import os
import re
import base64
from datetime import datetime

import app as app_module
import store
import fetcher

HERE = os.path.dirname(__file__)
SHARE_DIR = os.path.join(HERE, "share")
# Named index.html so web hosts (Netlify Drop, GitHub Pages) serve it at the
# clean root URL automatically. It's also the file you send to a friend.
OUT_FILE = os.path.join(SHARE_DIR, "index.html")


def _inline_css(html):
    css_path = os.path.join(HERE, "static", "style.css")
    with open(css_path, encoding="utf-8") as f:
        css = f.read()
    # Replace the <link rel="stylesheet" ...style.css"> tag with an inline block.
    link_re = re.compile(r'<link[^>]+href="[^"]*style\.css"[^>]*>')
    return link_re.sub(f"<style>\n{css}\n</style>", html)


def _inline_icon(html):
    icon_path = os.path.join(HERE, "static", "icon.svg")
    with open(icon_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    data_uri = f"data:image/svg+xml;base64,{data}"
    # Point every /static/icon.svg reference (favicon, apple-touch-icon) at the data URI.
    return re.sub(r'href="[^"]*icon\.svg"', f'href="{data_uri}"', html)


def build():
    store.init_db()
    if store.get_meta("last_refresh") is None:
        print("[build] empty cache -> fetching news first…")
        fetcher.refresh_all()
    # keep classification current with the latest rules
    store.reclassify_all()

    # test_request_context (not just app_context) so url_for('static', ...) works.
    with app_module.app.test_request_context():
        from flask import render_template
        html = render_template(
            "index.html",
            **app_module.build_index_context(static_build=True),
        )

    html = _inline_css(html)
    html = _inline_icon(html)

    os.makedirs(SHARE_DIR, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(OUT_FILE) / 1024
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\n  ✓ Built {OUT_FILE}")
    print(f"    {size_kb:.0f} KB · snapshot {stamp} · a single self-contained file")
    print(f"    Send it to a friend — they just double-click to open it.\n")


if __name__ == "__main__":
    build()
