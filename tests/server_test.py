"""Test server curses. Note that this file contains strong language, as does
curses.txt. Read both at your own risk."""

from server.server import server


def test_curses():
    assert server.curses
    curse = server.curses[0]
    assert '\n' not in curse
    assert '\r' not in curse
    assert '\r\n' not in curse


def test_valid_name():
    assert server.valid_name('test')
    assert not server.valid_name('arse bag')
    assert not server.valid_name('Bob Fuckteeth')
    assert not server.valid_name('arseflannel')
    assert server.valid_name('Tom Scunthorpe')
    assert not server.valid_name('test\ning')
    assert not server.valid_name('hello\r\nworld')
    assert not server.valid_name('test\rthis')
