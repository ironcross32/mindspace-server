from server import db
for x in dir(db):
    if not x.startswith('_'):
        locals()[x] = getattr(db, x)
load_db()  # noqa f821
