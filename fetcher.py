"""
Fetch + parse all feeds, classify each article, store the new ones.

Called on startup and then every REFRESH_MINUTES by the scheduler in app.py.
Network/parse errors are swallowed per-feed so one dead source never breaks
the whole refresh -- the cached copy just stays until the feed recovers.
"""

import socket
import re
import html
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

import feedparser

import feeds as feeds_mod
import store

socket.setdefaulttimeout(20)

USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36")

_TAG_RE = re.compile(r"<[^>]+>")


def _clean(text, limit=280):
    """Strip HTML tags/entities from a summary and trim to a short snippet."""
    if not text:
        return ""
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0] + "…"
    return text


def _published_iso(entry):
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc).isoformat()
            except (ValueError, TypeError):
                pass
    return None


def _fetch_one(feed):
    rows = []
    try:
        parsed = feedparser.parse(feed["url"], agent=USER_AGENT)
    except Exception as e:
        print(f"  ! {feed['name']}: fetch error ({e})")
        return rows

    if not parsed.entries:
        status = getattr(parsed, "status", "??")
        print(f"  ! {feed['name']}: 0 entries [status {status}]")
        return rows

    for entry in parsed.entries:
        title = _clean(entry.get("title", ""), limit=200)
        # Skip junk: empty, too short, or section/landing pages that some
        # site: searches return (e.g. "- dvprogram (.gov)", "Region - World").
        if not title or len(title) < 18 or title.lstrip().startswith("-") \
                or title.count(" ") < 2 or "(.gov)" in title:
            continue
        summary = _clean(entry.get("summary", entry.get("description", "")))
        link = entry.get("link", "")
        region = feeds_mod.classify(title, summary, feed.get("default_region"))
        if region is None:
            continue
        rows.append({
            "title": title,
            "snippet": summary,
            "source": feed["name"],
            "note": feed.get("note"),
            "link": link,
            "region": region,
            "published": _published_iso(entry),
        })
    print(f"  ✓ {feed['name']}: {len(rows)} kept / {len(parsed.entries)} fetched")
    return rows


def refresh_all():
    """Fetch every feed (in parallel), store new articles, prune old ones."""
    start = datetime.now(timezone.utc)
    print(f"[refresh] starting {start.isoformat(timespec='seconds')}")
    all_rows = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for rows in ex.map(_fetch_one, feeds_mod.FEEDS):
            all_rows.extend(rows)

    new_count = store.upsert_articles(all_rows)
    store.prune(keep_days=14)
    store.set_meta("last_refresh", datetime.now(timezone.utc).isoformat())
    store.set_meta("last_new_count", new_count)
    print(f"[refresh] done: {new_count} new, {len(all_rows)} seen this pass")
    return new_count


if __name__ == "__main__":
    store.init_db()
    refresh_all()
