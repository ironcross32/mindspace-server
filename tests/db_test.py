from server.db import Object


def test_system():
    assert Object.get(0) is not None
