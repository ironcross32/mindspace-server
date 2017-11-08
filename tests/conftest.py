from server.server import server  # noqa
from server.db import Base

Base.metadata.create_all()
