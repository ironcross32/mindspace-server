from server.server import server
from server.db import *
load_db()
for field in Hotkey.first().get_all_fields():
    print(field)
