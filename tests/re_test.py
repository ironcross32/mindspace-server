from pytest import raises
from server.program import OK, get_coordinates


class DummyPlayer:
    def message(self, *args, **kwargs):
        pass


player = DummyPlayer()


def test_get_coordinates():
    coords = (1.0, 1.0, 1.0)
    assert get_coordinates(player, '1,1,1') == coords
    assert get_coordinates(player, '(1.0, 1.0, 1.0)') == coords
    assert get_coordinates(player, '[1.5, 1.5,1.5]') == (1.5, 1.5, 1.5)
    with raises(OK):
        get_coordinates(player, 'a s d')
    assert get_coordinates(player, '1 1 1') == coords
