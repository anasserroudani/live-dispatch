"""
Feed definitions + article classification.

Each feed is a dict:
  name          -> short label shown to you (the source name)
  url           -> the RSS/Atom URL we actually fetch
  default_region-> region to fall back to if keyword matching finds nothing
                   (used for outlets that only ever cover one beat)
  note          -> optional attribution note (e.g. "via Google News")

REGIONS is the ordered list of sections shown on the dashboard.
Classification is keyword-first (so an Al Jazeera Sudan story lands in AFRICA),
then falls back to the feed's default_region, then the article is dropped.
"""

import urllib.parse

# ---- Region identifiers (order = display order on the page) -----------------
MIDEAST = "mideast"
MOROCCO = "morocco"
AFRICA = "africa"
GLOBAL = "global"
SCIENCE = "science"

REGIONS = [
    {"id": MIDEAST, "title": "Iran War & Middle East",
     "tag": "incl. Gaza / Israel / Lebanon"},
    {"id": MOROCCO, "title": "Morocco",
     "tag": "incl. Western Sahara"},
    {"id": AFRICA, "title": "Africa",
     "tag": "politics & security"},
    {"id": GLOBAL, "title": "Great Powers & Global",
     "tag": "US · Europe · Russia · Ukraine · China"},
    {"id": SCIENCE, "title": "Science & Tech",
     "tag": "AI · quantum · physics · space"},
]


def _gnews(query):
    """Build a Google News RSS search URL (legitimate free aggregator).
    Used only for outlets whose own RSS is blocked or discontinued.
    Results link back to the original outlet -- no scraping of article text."""
    q = urllib.parse.quote(query)
    return f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"


# ---- The feed list ----------------------------------------------------------
FEEDS = [
    # -- Middle East beat --
    {"name": "Al Jazeera",        "url": "https://www.aljazeera.com/xml/rss/all.xml",
     "default_region": None},
    {"name": "NYT Middle East",   "url": "https://rss.nytimes.com/services/xml/rss/nyt/MiddleEast.xml",
     "default_region": MIDEAST},
    {"name": "Times of Israel",   "url": "https://www.timesofisrael.com/feed/",
     "default_region": MIDEAST},
    {"name": "Haaretz",           "url": "https://www.haaretz.com/cmlink/1.4605102",
     "default_region": MIDEAST},
    {"name": "Al Mayadeen",       "url": _gnews("site:english.almayadeen.net"),
     "default_region": MIDEAST, "note": "via Google News"},

    # -- Morocco beat --
    {"name": "Hespress",          "url": "https://en.hespress.com/feed/",
     "default_region": MOROCCO},
    {"name": "Morocco World News", "url": _gnews("site:moroccoworldnews.com"),
     "default_region": MOROCCO, "note": "via Google News"},

    # -- Africa beat --
    {"name": "Africanews",        "url": "https://www.africanews.com/feed/",
     "default_region": AFRICA},
    {"name": "The Africa Report", "url": "https://www.theafricareport.com/feed/",
     "default_region": AFRICA},

    # -- General wires (keyword-classified; unmatched items are dropped) --
    {"name": "BBC World",         "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
     "default_region": None},
    {"name": "CNN World",         "url": "http://rss.cnn.com/rss/cnn_world.rss",
     "default_region": None},
    {"name": "NYT World",         "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
     "default_region": None},
    {"name": "Reuters",           "url": _gnews("site:reuters.com Middle East OR Africa OR Iran"),
     "default_region": None, "note": "via Google News"},

    # -- Great powers & other connective conflicts --
    {"name": "Ukraine wire",      "url": _gnews("Ukraine Russia war when:3d"),
     "default_region": GLOBAL, "note": "via Google News"},
    {"name": "DR Congo wire",     "url": _gnews("DR Congo M23 conflict when:4d"),
     "default_region": AFRICA, "note": "via Google News"},

    # -- Science & tech --
    {"name": "ScienceDaily",      "url": "https://www.sciencedaily.com/rss/all.xml",
     "default_region": SCIENCE},
]


# ---- Classification keywords ------------------------------------------------
# Keyword hit -> region. Checked in this order; first match wins.
_SCIENCE_KW = [
    "quantum", "qubit", "artificial intelligence", " ai ", "machine learning",
    "physics", "particle", "telescope", "galaxy", "nasa", "rocket", "spacecraft",
    "satellite", "astronom", "space station", "tectonic", "fusion", "semiconductor",
    "neural network", "genome", "climate model", "supercomput", "black hole",
]
_MOROCCO_KW = [
    "morocco", "moroccan", "rabat", "casablanca", "marrakech", "tangier",
    "western sahara", "sahrawi", "polisario", "dakhla", "laayoune", "el aaiun",
    "nador", "dirham", "autonomy plan",
]
_MIDEAST_KW = [
    "iran", "iranian", "tehran", "khamenei", "irgc", "revolutionary guard",
    "israel", "israeli", "gaza", "palestin", "hamas", "hezbollah", "lebanon",
    "beirut", "houthi", "yemen", "hormuz", "netanyahu", "west bank", "idf",
    "tel aviv", "strait of hormuz", "ceasefire", "al-hayya", "rafah",
    "saudi", "qatar", "uae", "emirates", "bahrain", "kuwait", "oman",
    "jordan", "red sea", "gulf state",
    "syria", "syrian", "damascus", "assad", "aleppo", "kurdish", "kurds",
    "bab el-mandeb", "sanaa",
]
_AFRICA_KW = [
    "africa", "african", "sudan", "sudanese", "rsf", "khartoum", "mali", "malian",
    "sahel", "burkina", "niger", "nigeria", "ghana", "congo", "drc", "kinshasa",
    "ethiopia", "kenya", "somalia", "wagner", "ebola", "sahelian", "senegal",
    "ivory coast", "côte d", "cote d", "cameroon", "chad", "zimbabwe",
    "uganda", "rwanda", "tanzania", "mozambique", "madagascar", "libya",
    "tunisia", "sahara desert", "m23", "goma", "great lakes", "coltan",
]
# Great-power stories route straight to GLOBAL (Ukraine/Russia/China/Taiwan).
_GREATPOWER_KW = [
    "ukraine", "ukrainian", "russia", "russian", "moscow", "putin", "kyiv",
    "kremlin", "china", "chinese", "beijing", "xi jinping", "taiwan", "nato",
    "zelensky", "wagner", "crimea", "donbas",
]
# For GLOBAL (connective): a "US/Europe" anchor AND a topical hook that ties back.
_WEST_KW = [
    "united states", "u.s.", " us ", "washington", "white house", "trump",
    "congress", "pentagon", "state department", "europe", "european union",
    " eu ", "france", "french", "britain", "uk ", "germany", "brussels", "nato",
]
_HOOK_KW = _MIDEAST_KW + _MOROCCO_KW + _AFRICA_KW + [
    "oil", "energy", "china", "chinese", "trade", "sanction", "tariff", "market",
]


# Force-drop obvious non-news noise even if it comes from a regional outlet
# (e.g. Morocco World News' football coverage inheriting the Morocco beat).
_DENY_KW = [
    "messi", "ronaldo", "premier league", "la liga", "champions league",
    "soccer", "football match", "afcon", "world cup qualif", "tennis",
    "wimbledon", "grand prix", "box office", "celebrity", "horoscope",
    "recipe", "grammy", "oscars", "red carpet", "transfer window",
    "goalkeeper", "midfielder", "top scorer", "kick-off",
]


def _has(text, keywords):
    return any(kw in text for kw in keywords)


def classify(title, summary, default_region):
    """Return a region id, or None if the article should be dropped."""
    text = f" {title} {summary} ".lower()

    # Junk filter first: drop sports/entertainment regardless of source.
    if _has(text, _DENY_KW):
        return None

    # A story with a clear geopolitics signal is never "science", even if it
    # happens to mention satellites, drones or AI (e.g. "satellite images show
    # US bases evacuated"). This keeps war reporting out of the Science tab.
    has_geo = _has(text, _MIDEAST_KW) or _has(text, _MOROCCO_KW) or _has(text, _AFRICA_KW)

    # Route to Science only when the feed's own beat is Science, or it's a
    # general wire (no home beat) with no geopolitics signal in the text.
    if _has(text, _SCIENCE_KW) and (
            default_region == SCIENCE or (default_region is None and not has_geo)):
        return SCIENCE
    if _has(text, _MOROCCO_KW):
        return MOROCCO
    if _has(text, _MIDEAST_KW):
        return MIDEAST
    if _has(text, _AFRICA_KW):
        return AFRICA
    if _has(text, _GREATPOWER_KW):
        return GLOBAL
    if _has(text, _WEST_KW) and _has(text, _HOOK_KW):
        return GLOBAL

    # No keyword matched -> fall back to the feed's home beat (if it has one).
    return default_region


# Words that suggest a hopeful / de-escalation angle. Stories matching these get
# a soft green "glimmer" marker -- a small deliberate note of optimism in an
# otherwise heavy feed. Kept conservative to avoid false cheer on tragic news.
_HOPE_KW = [
    "ceasefire", "truce", "peace deal", "peace talks", "de-escalat", "diplomacy",
    "aid convoy", "humanitarian aid", "released", "freed", "reunited", "rebuild",
    "reopen", "reconstruction", "agreement reached", "breakthrough", "recovery",
    "vaccine", "cure", "rescued", "prisoner exchange", "reconciliation",
    "returns home", "aid reaches", "restored", "milestone",
]


# Negations that flip a hopeful-sounding headline back to bad news
# ("ceasefire rejected", "de-escalation uncertain", "talks collapse").
_HOPE_NEG = [
    "reject", "collaps", "fail", "uncertain", "breaks down", "broke down",
    "off the table", "denies", "denied", "refuse", "stall", "no ceasefire",
    "no deal", "not hold", "in doubt", "delayed", "threaten",
]


def is_hopeful(title, summary):
    """True if a headline reads as a genuine de-escalation / hope story."""
    text = f" {title} {summary} ".lower()
    return _has(text, _HOPE_KW) and not _has(text, _HOPE_NEG)
