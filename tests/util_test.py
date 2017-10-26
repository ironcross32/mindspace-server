from server.util import directions


def test_directions():
    c1 = (1, 1, 1)
    c2 = (1, 1, 1)
    assert directions(c1, c2) == 'here'
    c2 = (2, 1, 1)
    assert directions(c1, c2) == '1 east'
    c2 = (1, 2, 1)
    assert directions(c1, c2) == '1 north'
    c2 = (1, 1, 2)
    assert directions(c1, c2) == '1 up'
    c2 = (0, 0, 0)
    assert directions(c1, c2) == '1 west, 1 south, 1 down'
