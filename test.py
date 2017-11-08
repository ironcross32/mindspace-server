from server.server import server
from server.db import *
load_db()
for field in Entrance.first().get_all_fields():
    print(field)
