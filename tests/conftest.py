from server import db_engine

db_engine.engine_args = ('sqlite:///:memory:',)

from server.db import (
    Base, Currency, Object, CreditCard, session, Room, finalise_db
)  # noqa E402
from server.server import server  # noqa E402
assert server is not None  # Stop pytest from moaning.
Base.metadata.create_all()


class Message(Exception):
    """A message was received."""


class CustomPlayer:
    def message(self, *args, **kwargs):
        raise Message(*args, **kwargs)


Base.metadata.create_all()
finalise_db()
with session() as s:
    s.add(Currency(value=1.0))
    s.commit()
    c = CreditCard(value=5)
    s.add(c)
    s.commit()
    r = Room(name='Test Room')
    s.add(r)
    s.commit()
    p = Object(name='Test Player', location_id=r.id)
    o = Object(name='Credit Card', holder=p, credit_card_id=c.id)
    s.add_all([p, o])
