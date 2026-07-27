# Live Dispatch

A **local** news dashboard + politics/history learning tool. It pulls RSS feeds
from a fixed set of outlets, groups the stories by region, refreshes itself
automatically in the background, and pairs the news with editable "Learn"
essays, timelines, a glossary, and a "Perspectives" media-literacy section.

Everything runs on your own Mac. Nothing is published anywhere. It fetches only
**headlines + short snippets + source + link** — never full paywalled article
text.

---

## First-time setup (do this once)

You need Python 3 (you already have 3.13). Open the **Terminal** app, then copy
these commands in one at a time.

**1. Go into the project folder:**
```bash
cd ~/Desktop/live-dispatch
```

**2. Create an isolated environment** (keeps this project's libraries separate
from the rest of your Mac):
```bash
python3 -m venv venv
```

**3. Turn that environment on:**
```bash
source venv/bin/activate
```
You'll now see `(venv)` at the start of your Terminal line. That means it worked.

**4. Install the libraries it needs:**
```bash
pip install -r requirements.txt
```

*(If you set the project up with me already, the `venv` folder exists and steps
2–4 are done — you can skip straight to "Running it".)*

---

## Running it (every time)

```bash
cd ~/Desktop/live-dispatch
source venv/bin/activate
python app.py
```

Then open your browser to:

**http://localhost:5050**

The first launch fetches all the feeds (takes ~10–20 seconds), then the page
loads. After that it **refreshes itself every 45 minutes** — you never have to
refresh by hand. The page also quietly reloads every 20 minutes so new stories
appear on their own.

To stop it: go back to the Terminal and press **Ctrl + C**.

---

## What each tab is

- **Iran War & Middle East / Morocco / Africa / US & Europe** — live headlines,
  grouped by region. "US & Europe" only shows stories that connect back to your
  other beats (Iran, Gaza, Morocco, Africa, trade, oil).
- **Science & Tech** — deliberately styled differently (blue/gold) so it never
  blurs into the politics sections.
- **Perspectives** — starts with **"Today's lead story across newsrooms"**: the
  app automatically finds the Middle East topic with the widest coverage right
  now and shows one headline per outlet (Al Jazeera, Haaretz, Times of Israel,
  Al Mayadeen, Reuters, NYT) so you can see the framing gap at a glance. Below
  that is the fixed guide to who funds each outlet.
- **Learn** — goes *deep* on one conflict at a time: Explainers, year-by-year
  Timelines, a Glossary, and "How we got here" recaps. Now covers Iran, Gaza,
  Western Sahara, Sudan, the Sahel, **Ukraine, Yemen, Syria, and DR Congo**.
- **Connect** — the *horizontal* layer that ties it all together:
  - **The Map** — the great-power hubs (Iran, Russia, US, China) and the
    conflicts/proxies each one connects.
  - **The Threads** — the ~7 cross-cutting forces (energy, minerals, proxy
    warfare, great-power rivalry, colonial legacy, displacement, religion) that
    run through many conflicts at once. This is where "everything connects."
  - **The Actors** — the ~15 recurring players and what each one *wants*.
  - **The Analyst's Toolkit** — a repeatable method for reading *any* new story
    and slotting it into the map.
  Add your own actors/threads by dropping a `.md` file into
  `content/actors/` or `content/threads/`.
- **Search** (box under the masthead) — searches every headline and snippet
  currently cached, across all regions.

A few touches: stories about de-escalation, aid, ceasefires or releases get a
small green **"glimmer"** tag — a bit of deliberate optimism in a heavy feed.
The **☀ / ☾ button** (top-right) switches between the light and dark themes and
remembers your choice.

---

## Sending it to a friend (one shareable file)

Run this and it bundles the **whole app into a single HTML file** — every tab,
all the Learn/Connect content, and a snapshot of the current news:

```bash
cd ~/Desktop/live-dispatch && source venv/bin/activate && python build_static.py
```

It creates **`share/index.html`**. That one file is self-contained (the styling
and logo are baked in), so:

- **To send it as a file:** AirDrop / WhatsApp / email `share/index.html`. Your
  friend just double-clicks it — no Python, no Terminal, no server. Article links
  still open in their browser.
- **For a free public link (no card, no account):** go to
  **app.netlify.com/drop** and drag the whole **`share` folder** onto the page.
  In ~10 seconds you get a web address like `https://sunny-cat-123.netlify.app`
  to send. To keep it permanently, click "Sign up to claim your site" — the free
  Netlify account does **not** ask for a card. (The page only contains public
  news snippets and links, nothing private.)

> **Note:** truly *live* hosting (always-fresh news at a URL) now requires a
> credit card on every major host (Render, Railway, Fly…), even on their free
> tiers. The snapshot approach avoids that entirely. See `DEPLOY.md`
> for the live-hosting route if you ever want it.

### The public link (GitHub Pages — free, no card)

The site is already published, for free, at:

**https://anasserroudani.github.io/live-dispatch/**

It's a snapshot hosted from the `docs/` folder of the GitHub repo. To **update
the live site** with fresh news later, run three commands:

```bash
cd ~/Desktop/live-dispatch && source venv/bin/activate && python build_static.py
```
```bash
cd ~/Desktop/live-dispatch && git add -A && git commit -m "refresh news" && git push
```

GitHub rebuilds the page automatically about a minute after you push.

The **news is a snapshot** from the moment you build it; the Learn, Connect,
Timelines and Perspectives sections are evergreen. Re-run the command any time
for a fresh snapshot. (The live search and "refresh" button are hidden in the
shareable file, since those need the running app.)

---

## Viewing it on your iPhone (optional)

The app has a full mobile layout. To open it on your phone, your phone must be
on the **same Wi-Fi** as your Mac:

1. Find your Mac's local IP: **System Settings → Wi-Fi → Details → IP address**
   (looks like `192.168.1.x`).
2. On your iPhone, open Safari to `http://YOUR-MAC-IP:5050` (e.g.
   `http://192.168.1.23:5050`).
3. Tap **Share → Add to Home Screen** to get an app icon (the sunrise logo) that
   opens full-screen, like a real app.

Your Mac has to be on and running the app for the phone to reach it — it's still
your Mac doing the work, the phone is just the screen.

---

## Editing the Learn content yourself

All the essays, timelines, glossary, and perspectives are plain text files in
the `content/` folder — **not** buried in code. Edit them in any text editor:

```
content/
  explainers/   ← one .md file per background essay
  timelines/    ← one .md file per timeline
  glossary.md   ← add your own terms here
  recaps.md     ← the "how we got here" catch-up
  perspectives.md
```

They're written in **Markdown** (`#` = heading, `**bold**`, `-` = bullet).
Save the file, reload the page, and your change is live. To add a new explainer,
just drop a new `.md` file into `content/explainers/`.

---

## Where the news comes from

Direct RSS feeds: Al Jazeera, BBC World, CNN World, NYT (World + Middle East),
Times of Israel, Haaretz, Hespress, Africanews, The Africa Report, ScienceDaily.

Via **Google News RSS** (a legitimate free aggregator that links back to the
original outlet — used because these block their own RSS or discontinued it):
**Morocco World News**, **Al Mayadeen**, and **Reuters**.

To change the source list, edit `feeds.py`. To change how often it refreshes,
change `REFRESH_MINUTES` at the top of `app.py`. To drop noise (sports, gossip),
add words to the `_DENY_KW` list in `feeds.py`.

---

## Optional: make it start automatically at login

By default you start the app by hand in Terminal. If you'd rather have it
**always running in the background** — so it's just there whenever you open
`http://localhost:5050`, even after a restart — set up the included login item.

**Turn it ON** (run each line once in Terminal):

```bash
# 1. Stop the manual copy first if one is running (Ctrl+C in its window)
# 2. Install and start the login item:
cp ~/Desktop/live-dispatch/com.livedispatch.app.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.livedispatch.app.plist
```

From then on it runs on its own — **don't also run `python app.py` by hand**, or
you'll get the "Address already in use" error (two copies fighting over the port).

**Turn it OFF:**

```bash
launchctl unload ~/Library/LaunchAgents/com.livedispatch.app.plist
rm ~/Library/LaunchAgents/com.livedispatch.app.plist
```

While it's running as a login item, its output goes to `server.log` in the
project folder if you ever want to check on it.

---

## Honest limitations

- **Region sorting is keyword-based**, not AI. It's ~90% right; an occasional
  story lands in the "wrong" section (e.g. a Spanish-news item from a Moroccan
  outlet showing under Morocco). Easy to tune in `feeds.py`.
- **The "top story across newsrooms" is keyword-anchored, not true story
  matching.** It groups outlets by a shared topic (Iran, Gaza, Lebanon…), not by
  proving they're about the identical event — a deliberate trade-off, since full
  auto-matching is fragile. The hand-written funding guide below it is fixed.
- **Some outlets (FT, NYT, Haaretz premium) only expose headlines via RSS**, not
  full text — which is exactly what we want anyway (headline + link only).
- It runs while the Terminal window is open. Close the Terminal (or Ctrl+C) and
  it stops. This is a personal tool, not a hosted website.
