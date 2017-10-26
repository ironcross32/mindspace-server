from pytest import raises
from server.server import server  # noqa
from server.program import PermissionError, check_perms


class DummyPlayer:
    """Looks like a db.Object instance."""

    is_admin = False
    is_builder = False

    def get_name(self, *args, **kwargs):
        return 'Dummy Player'


def test_check_perms():
    p = DummyPlayer()
    assert check_perms(p) is None
    with raises(PermissionError):
        check_perms(p, builder=True)
    with raises(PermissionError):
        check_perms(p, admin=True)
    p.is_builder = True
    p.is_admin = True
    with raises(PermissionError):
        check_perms(p, builder=False)
    with raises(PermissionError):
        check_perms(p, admin=False)
