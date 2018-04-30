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
    valid_names = (
        'Chris Norman',
        'Gemma-Louise Goulston',
        'Craig D\'Andrea',
        'Philip Bottomly-Smithe',
        'Freddy'
    )
    invalid_names = (
        'C\'raig-Philip Danger-Widget'
        'Arsebucket',
        'Clammon Jerkoff'
        'B00b Smile',
        'Test\nthis'
    )
    for name in valid_names:
        assert server.valid_name(name), 'Should be a valid name: %r.' % name
    for name in invalid_names:
        assert not server.valid_name(name), \
            'Should not be a valid name: %r.' % name
