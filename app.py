"""
Live Dispatch -- a local news dashboard + politics/history learning tool.

Run it with:   python app.py
Then open:     http://localhost:5050

A background scheduler refreshes the feeds every REFRESH_MINUTES, so you never
have to refresh by hand. Learn/Perspectives content lives in editable markdown
files under content/ -- edit those by hand any time; changes show on reload.
"""

import os
import re
import glob
from datetime import datetime, timezone

import markdown as md
from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler

import feeds as feeds_mod
import store
import fetcher

REFRESH_MINUTES = 45
ARTICLES_PER_REGION = 40      # "as much news as possible"
SCIENCE_LIMIT = 160           # bigger, because it's split across ~6 topics
BRIEFING_PER_SECTION = 3      # top stories per section in the digest
# Port 5000 is hijacked by macOS AirPlay Receiver, so we default to 5050.
# Override with the PORT env var (e.g. PORT=5051 python app.py) if needed.
PORT = int(os.environ.get("PORT", 5050))
CONTENT_DIR = os.path.join(os.path.dirname(__file__), "content")

# Outlets compared in the "top story across newsrooms" panel, and the topics
# we track. For each refresh we pick the topic with the widest coverage across
# these outlets and show one headline per outlet -- an automatic, keyword-
# anchored version of the Perspectives idea (no fragile story auto-matching).
PERSPECTIVE_SOURCES = ["Al Jazeera", "Haaretz", "Times of Israel",
                       "Al Mayadeen", "Reuters", "NYT Middle East"]
TRACK_TOPICS = [
    ("Gaza / Israel", ["gaza", "rafah", "yellow line", "hamas"]),
    ("Iran", ["iran", "tehran", "irgc", "hormuz", "khamenei"]),
    ("Lebanon / Hezbollah", ["lebanon", "hezbollah", "beirut"]),
    ("The West Bank", ["west bank", "nablus", "settler"]),
    ("Red Sea / Houthis", ["houthi", "red sea", "yemen"]),
]

app = Flask(__name__)
_md = md.Markdown(extensions=["extra", "sane_lists"])

# [[some-slug]] cross-links (Actors/Threads references) -> clean inline labels.
_WIKILINK = re.compile(r"\[\[([a-z0-9\-]+)\]\]")
_SMALL_WORDS = {"and", "of", "the", "to", "a"}


def _humanize_slug(slug):
    slug = re.sub(r"^\d+-", "", slug)              # drop the ordering prefix
    words = slug.replace("-", " ").split()
    return " ".join(w if (i and w in _SMALL_WORDS) else w.capitalize()
                    for i, w in enumerate(words))


# ---- Markdown content loading ----------------------------------------------
def _render_md(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    _md.reset()
    html = _md.convert(text)
    return _WIKILINK.sub(
        lambda m: f'<span class="xlink">{_humanize_slug(m.group(1))}</span>', html)


def _title_from(path):
    """Use the first '# Heading' line as the card title, else the filename."""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("# "):
                return line[2:].strip()
    return os.path.splitext(os.path.basename(path))[0].replace("-", " ").title()


def load_docs(subdir):
    """Load every .md file in content/<subdir> as {title, html}, sorted."""
    folder = os.path.join(CONTENT_DIR, subdir)
    docs = []
    for path in sorted(glob.glob(os.path.join(folder, "*.md"))):
        docs.append({"title": _title_from(path), "html": _render_md(path)})
    return docs


def load_single(filename):
    path = os.path.join(CONTENT_DIR, filename)
    return _render_md(path) if os.path.exists(path) else ""


# ---- Time formatting --------------------------------------------------------
def _humanize(iso):
    if not iso:
        return ""
    try:
        dt = datetime.fromisoformat(iso)
    except ValueError:
        return ""
    delta = datetime.now(timezone.utc) - dt
    secs = delta.total_seconds()
    if secs < 3600:
        return f"{int(secs // 60)} min ago"
    if secs < 86400:
        return f"{int(secs // 3600)}h ago"
    return f"{int(secs // 86400)}d ago"


def compute_top_story():
    """Pick the Middle East topic with the widest coverage across the
    Perspectives outlets right now, and return one headline per outlet."""
    recent = store.get_recent_by_sources(PERSPECTIVE_SOURCES, limit=150)
    best_label, best_items = None, {}
    for label, kws in TRACK_TOPICS:
        by_source = {}
        for a in recent:
            text = f"{a['title']} {a.get('snippet', '')}".lower()
            if any(k in text for k in kws) and a["source"] not in by_source:
                by_source[a["source"]] = a  # first = most recent for that outlet
        if len(by_source) > len(best_items):
            best_label, best_items = label, by_source
    if len(best_items) < 2:  # need at least two outlets to be a "comparison"
        return None
    stories = []
    for src in PERSPECTIVE_SOURCES:  # stable, meaningful ordering
        if src in best_items:
            a = best_items[src]
            stories.append({**a, "ago": _humanize(a.get("published")),
                            "hopeful": feeds_mod.is_hopeful(a["title"], a.get("snippet", ""))})
    return {"label": best_label, "stories": stories}


def build_index_context(static_build=False):
    """Assemble everything the main page needs. Shared by the live route and
    the static-site exporter (build_static.py). static_build=True hides the
    server-only controls (search, refresh) for a self-contained snapshot."""
    regions = []
    science_topics = None
    for r in feeds_mod.REGIONS:
        limit = SCIENCE_LIMIT if r["id"] == feeds_mod.SCIENCE else ARTICLES_PER_REGION
        articles = store.get_by_region(r["id"], limit=limit)
        for a in articles:
            a["ago"] = _humanize(a.get("published"))
            a["hopeful"] = feeds_mod.is_hopeful(a["title"], a.get("snippet", ""))
        if r["id"] == feeds_mod.SCIENCE:
            # split Science into its topic "places"
            buckets = {t["id"]: [] for t in feeds_mod.SCIENCE_TOPICS}
            for a in articles:
                buckets[feeds_mod.sci_topic(a["title"], a.get("snippet", ""))].append(a)
            science_topics = [{**t, "articles": buckets[t["id"]]}
                              for t in feeds_mod.SCIENCE_TOPICS]
        regions.append({**r, "articles": articles})

    # Briefing: a scannable digest of the top few stories per section.
    briefing = []
    for r in regions:
        top = r["articles"][:BRIEFING_PER_SECTION]
        if top:
            briefing.append({"title": r["title"], "id": r["id"], "stories": top})

    return dict(
        regions=regions,
        science_topics=science_topics,
        briefing=briefing,
        top_story=compute_top_story(),
        explainers=load_docs("explainers"),
        timelines=load_docs("timelines"),
        glossary_html=load_single("glossary.md"),
        recaps_html=load_single("recaps.md"),
        perspectives_html=load_single("perspectives.md"),
        connections_html=load_single("connections.md"),
        threads=load_docs("threads"),
        actors=load_docs("actors"),
        toolkit_html=load_single("toolkit.md"),
        last_refresh=_humanize(store.get_meta("last_refresh")),
        today=datetime.now().strftime("%B %-d, %Y").upper(),
        refresh_minutes=REFRESH_MINUTES,
        habiba_day=datetime.now().strftime("%m-%d") == "07-28",
        static_build=static_build,
    )


# ---- Routes -----------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", **build_index_context())


@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    results = store.search(q) if q else []
    for a in results:
        a["ago"] = _humanize(a.get("published"))
        a["hopeful"] = feeds_mod.is_hopeful(a["title"], a.get("snippet", ""))
    region_titles = {r["id"]: r["title"] for r in feeds_mod.REGIONS}
    return render_template(
        "search.html",
        q=q,
        results=results,
        region_titles=region_titles,
        today=datetime.now().strftime("%B %-d, %Y").upper(),
    )


@app.route("/read")
@app.route("/read/")
def read():
    """A birthday surprise page — plain URL so nothing gives it away. 🌸"""
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), "docs", "read"), "index.html")


@app.route("/refresh", methods=["POST"])
def refresh_now():
    fetcher.refresh_all()
    return redirect(url_for("index"))


# ---- Startup ----------------------------------------------------------------
def bootstrap():
    store.init_db()
    # Fetch immediately if the cache is empty or older than the refresh window.
    last = store.get_meta("last_refresh")
    stale = True
    if last:
        try:
            age = (datetime.now(timezone.utc) - datetime.fromisoformat(last)).total_seconds()
            stale = age > REFRESH_MINUTES * 60
        except ValueError:
            stale = True
    if stale:
        fetcher.refresh_all()
    # Re-sort every cached article with the current rules so any tweaks to the
    # classifier in feeds.py take effect immediately (and newly-denied junk is
    # dropped), whether or not we just fetched.
    updated, dropped = store.reclassify_all()
    if updated or dropped:
        print(f"[reclassify] {updated} re-sorted, {dropped} dropped")

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(fetcher.refresh_all, "interval", minutes=REFRESH_MINUTES,
                      id="refresh", max_instances=1, coalesce=True)
    scheduler.start()
    print(f"[scheduler] auto-refresh every {REFRESH_MINUTES} min")


if __name__ == "__main__":
    bootstrap()
    print(f"\n  Live Dispatch running -> http://localhost:{PORT}\n")
    # use_reloader=False so the scheduler/bootstrap doesn't run twice
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)
