from sqlalchemy import create_engine, text

from app.db.session import _build_sync_url

engine = create_engine(_build_sync_url())
with engine.connect() as c:
    exists = c.execute(text("SELECT to_regclass('public.organizations')")).scalar()
    print("organizations exists:", bool(exists))
