from server.db import Player, Room, Session as s


def test_default():
    p = Player(username=__name__)
    s.add(p)
    s.commit()
    assert p.home is None


def test_squatters():
    r = Room(name='Test Room')
    s.add(r)
    s.commit()
    assert r.squatters == []
