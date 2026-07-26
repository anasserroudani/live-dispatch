"""
SQLite cache layer.

One table: articles. We keep whatever we fetch so the page loads instantly
and survives a feed being temporarily down. We store headline + snippet +
source + link + region only -- never full article text (hard requirement).
"""

import sqlite3
import os
import hashlib
from datetime import datetime, timezone

# DISPATCH_DB env var lets you point at a different cache file (used for testing
# without touching your live dispatch.db). Defaults to dispatch.db next to this.
DB_PATH = os.environ.get(
    "DISPATCH_DB", os.path.join(os.path.dirname(__file__), "dispatch.db"))


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id          TEXT PRIMARY KEY,   -- hash of link (dedupe key)
                title       TEXT NOT NULL,
                snippet     TEXT,
                source      TEXT NOT NULL,
                note        TEXT,               -- e.g. "via Google News"
                link        TEXT NOT NULL,
                region      TEXT NOT NULL,
                published   TEXT,               -- ISO8601, best effort
                fetched_at  TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_region ON articles(region)")
        conn.execute("""CREATE TABLE IF NOT EXISTS meta
                        (key TEXT PRIMARY KEY, value TEXT)""")


def _make_id(link, title):
    key = (link or title or "").strip().lower()
    return hashlib.sha1(key.encode("utf-8")).hexdigest()


def upsert_articles(rows):
    """rows: list of dicts. Returns number of NEW articles inserted."""
    inserted = 0
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        for r in rows:
            aid = _make_id(r["link"], r["title"])
            exists = conn.execute("SELECT 1 FROM articles WHERE id=?", (aid,)).fetchone()
            if exists:
                continue
            conn.execute("""
                INSERT INTO articles
                    (id, title, snippet, source, note, link, region, published, fetched_at)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (aid, r["title"], r.get("snippet", ""), r["source"],
                  r.get("note"), r["link"], r["region"], r.get("published"), now))
            inserted += 1
    return inserted


def get_by_region(region, limit=25):
    with _connect() as conn:
        cur = conn.execute("""
            SELECT title, snippet, source, note, link, published
            FROM articles WHERE region=?
            ORDER BY COALESCE(published, fetched_at) DESC
            LIMIT ?
        """, (region, limit))
        return [dict(r) for r in cur.fetchall()]


def search(query, limit=80):
    """Full-text-ish search across cached headlines + snippets."""
    like = f"%{query}%"
    with _connect() as conn:
        cur = conn.execute("""
            SELECT title, snippet, source, note, link, region, published
            FROM articles
            WHERE title LIKE ? OR snippet LIKE ?
            ORDER BY COALESCE(published, fetched_at) DESC
            LIMIT ?
        """, (like, like, limit))
        return [dict(r) for r in cur.fetchall()]


def get_recent_by_sources(sources, limit=150):
    """Recent articles from a specific set of outlets (for the top-story panel)."""
    if not sources:
        return []
    placeholders = ",".join("?" * len(sources))
    with _connect() as conn:
        cur = conn.execute(f"""
            SELECT title, snippet, source, note, link, published
            FROM articles WHERE source IN ({placeholders})
            ORDER BY COALESCE(published, fetched_at) DESC
            LIMIT ?
        """, (*sources, limit))
        return [dict(r) for r in cur.fetchall()]


def reclassify_all():
    """Re-run classification over every cached article using the current rules
    in feeds.py. Applies keyword/deny-list tuning to already-cached rows on
    startup (and drops anything the rules now reject), so edits take effect
    immediately without waiting for the cache to cycle. Returns (updated, dropped)."""
    import feeds as feeds_mod  # local import avoids a circular import at module load
    defaults = {f["name"]: f.get("default_region") for f in feeds_mod.FEEDS}
    updated = dropped = 0
    with _connect() as conn:
        rows = conn.execute("SELECT id, title, snippet, source, region FROM articles").fetchall()
        for r in rows:
            region = feeds_mod.classify(r["title"], r["snippet"] or "",
                                        defaults.get(r["source"]))
            if region is None:
                conn.execute("DELETE FROM articles WHERE id=?", (r["id"],))
                dropped += 1
            elif region != r["region"]:
                conn.execute("UPDATE articles SET region=? WHERE id=?", (region, r["id"]))
                updated += 1
    return updated, dropped


def prune(keep_days=14):
    """Drop articles older than keep_days to stop the DB growing forever."""
    cutoff = datetime.now(timezone.utc).timestamp() - keep_days * 86400
    with _connect() as conn:
        rows = conn.execute("SELECT id, published, fetched_at FROM articles").fetchall()
        for row in rows:
            stamp = row["published"] or row["fetched_at"]
            try:
                ts = datetime.fromisoformat(stamp).timestamp()
            except (ValueError, TypeError):
                continue
            if ts < cutoff:
                conn.execute("DELETE FROM articles WHERE id=?", (row["id"],))


def set_meta(key, value):
    with _connect() as conn:
        conn.execute("INSERT INTO meta(key,value) VALUES(?,?) "
                     "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                     (key, str(value)))


def get_meta(key, default=None):
    with _connect() as conn:
        row = conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default
