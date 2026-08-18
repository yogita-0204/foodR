import os
import sys
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodR.settings")

# Copy existing SQLite db to writable /tmp on Vercel Serverless if needed
src_db = ROOT_DIR / "db.sqlite3"
tmp_db = Path("/tmp/db.sqlite3")

if src_db.exists() and not tmp_db.exists():
    try:
        shutil.copy2(src_db, tmp_db)
    except Exception as e:
        print(f"Could not copy db.sqlite3 to /tmp: {e}")

import django
django.setup()

# Ensure migrations are applied if database is freshly created in /tmp
if not tmp_db.exists():
    try:
        from django.core.management import call_command
        call_command("migrate", "--noinput")
    except Exception as e:
        print(f"Auto-migrate warning: {e}")

from django.core.wsgi import get_wsgi_application  # noqa: E402

app = get_wsgi_application()
