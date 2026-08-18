import os
import sys
import shutil
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

# Auto-migrate if db still doesn't exist
if not tmp_db.exists() or tmp_db.stat().st_size == 0:
    try:
        from django.core.management import call_command
        call_command("migrate", "--noinput")
    except Exception as e:
        print(f"Migration error: {e}")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
app = application
handler = application
