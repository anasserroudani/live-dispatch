#!/bin/zsh
# Fetch fresh news, rebuild the shareable snapshot, and push it to GitHub so the
# public site (https://anasserroudani.github.io/live-dispatch/) updates itself.
# Run automatically twice a day by the launchd job com.livedispatch.autopublish.

cd "$HOME/Desktop/live-dispatch" || exit 1
source venv/bin/activate

echo "===== auto-publish $(date '+%Y-%m-%d %H:%M') ====="

# 1. pull the latest news into the cache
python -c "import store, fetcher; store.init_db(); fetcher.refresh_all()"

# 2. rebuild the single-file snapshot (also refreshes docs/ for GitHub Pages)
python build_static.py

# 3. publish: commit + push (harmless if nothing changed)
git add -A
git commit -m "auto refresh $(date '+%Y-%m-%d %H:%M')" || echo "(nothing new to commit)"
git push origin main && echo "pushed OK" || echo "push failed"
