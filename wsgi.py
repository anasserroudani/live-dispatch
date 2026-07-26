"""
Production entry point (used when the app is hosted online, e.g. on Render).

Local use still runs `python app.py`. A production server like gunicorn imports
this file instead of running app.py directly, so we call bootstrap() here to
create the database, fetch the first batch of news, and start the background
refresh scheduler.

    gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
"""

from app import app, bootstrap

bootstrap()
