import os
import sys
import shutil
import traceback
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodR.settings")

# Handle SQLite on Vercel Serverless environment
tmp_db = Path("/tmp/db.sqlite3")
src_db = ROOT_DIR / "db.sqlite3"

if not tmp_db.exists() or tmp_db.stat().st_size == 0:
    if src_db.exists() and src_db.stat().st_size > 0:
        try:
            shutil.copy2(src_db, tmp_db)
        except Exception as e:
            print(f"Error copying db.sqlite3 to /tmp: {e}")

import django
django.setup()

from django.core.wsgi import get_wsgi_application

django_app = get_wsgi_application()

def application(environ, start_response):
    try:
        return django_app(environ, start_response)
    except Exception as e:
        tb = traceback.format_exc()
        print(f"WSGI Handler Error: {tb}")
        start_response('500 Internal Server Error', [('Content-Type', 'text/plain; charset=utf-8')])
        return [f"WSGI Internal Server Error:\n{tb}".encode('utf-8')]

app = application
handler = application
