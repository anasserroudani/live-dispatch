# Putting Live Dispatch online (a real, always-live link)

This makes a proper website your friend can visit any time and always see
**fresh** news — not a frozen snapshot. It runs on **Render**, which has a free
plan.

> ⚠️ **Card warning:** Render (and Railway, Fly.io, etc.) now ask for a **credit
> card** to verify your account *even for the free plan*. They shouldn't charge
> it on the free tier, but the card must be valid/accepted. If you don't want to
> add a card, **use the free Netlify Drop snapshot instead** (see the "Sending
> it to a friend" section of `README.md`) — that needs no card and no server.

You'll do this **once**, and it takes about 20 minutes. No coding — but you do
need to create two free accounts (I can't create accounts for you).

**Honest heads-up about the free plan:**
- After ~15 minutes with no visitors, the site "goes to sleep." The next visit
  takes ~30–50 seconds to wake up and load, then it's fast again. (Paid plans
  stay awake, but free is fine for sharing with a friend.)
- On each wake-up it re-fetches the news fresh, so it's always current.

---

## What you need

1. A free **GitHub** account → https://github.com/signup
2. A free **Render** account → https://render.com (sign up with your GitHub — one click)
3. **GitHub Desktop** (a simple app, no command line) → https://desktop.github.com

---

## Step 1 — Put the project on GitHub

Think of GitHub as a cloud folder for the code. Render reads the code from there.

1. Install and open **GitHub Desktop**, sign in with your GitHub account.
2. Menu: **File → Add Local Repository…**
3. Choose the folder `~/Desktop/live-dispatch` (your project).
4. It'll say "this isn't a Git repository — create one?" → click **Create a
   Repository**, then **Create Repository** again on the next screen.
5. Click **Publish repository** (top right).
   - **Uncheck** "Keep this code private" if you want (either works).
   - Click **Publish Repository**.

Done — your code is now on GitHub. (The big `venv` folder and the database are
automatically skipped, thanks to the `.gitignore` file already in the project.)

---

## Step 2 — Deploy on Render

1. Go to **https://dashboard.render.com** and sign in.
2. Click **New +** (top right) → **Blueprint**.
3. Connect your GitHub and pick the **live-dispatch** repository.
4. Render finds the `render.yaml` file automatically and shows a plan called
   **live-dispatch**. Click **Apply** / **Create Services**.
5. Wait a few minutes while it builds (you'll see logs scroll). When it says
   **Live**, it's done.

---

## Step 3 — Get your link and share it

At the top of your Render service page there's a URL like:

**`https://live-dispatch.onrender.com`**

That's your website. **Send that link to your friend** — it works on any phone
or computer, anywhere. (First load after a quiet spell takes ~30–50 s to wake up.)

---

## Updating it later

Whenever you change something (edit a Learn file, add a conflict, tweak the
design):

1. Open **GitHub Desktop** — it shows your changes.
2. Type a short note in the "Summary" box, click **Commit to main**.
3. Click **Push origin**.

Render notices the change and **redeploys automatically** in a couple of minutes.
No need to touch Render again.

---

## If something goes wrong

- **Build failed** — open the Render logs (the "Logs" tab) and read the last red
  lines. Usually it's a typo in a file you edited; undo it and push again.
- **Page is blank / "Application error"** — give it a minute (it may still be
  waking up), then refresh. If it persists, check the Logs tab.
- **News looks empty on first load** — the very first fetch runs as the site
  boots; refresh after ~30 seconds and it'll be populated.
- **Want it to never sleep** — that needs Render's paid "Starter" plan (a few
  dollars a month). Not necessary for sharing with a friend.

---

## How this differs from the shareable file

| | Single file (`build_static.py`) | Hosted site (this guide) |
|---|---|---|
| News | frozen snapshot | always fresh |
| Setup | one command | ~20 min, two accounts |
| Cost | free | free (sleeps when idle) |
| How you send it | send the file | send a link |

Both are good — the file is instant and offline; the hosted site is always live.
