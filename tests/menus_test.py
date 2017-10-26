from server.menus import Menu, Item


def test_item():
    i = Item('test', 'test')
    assert i.title == 'test'
    assert i.command == 'test'
    assert i.args == []
    assert i.kwargs == {}


def test_menu():
    m = Menu('test', [Item('test', 'test')])
    assert m.title == 'test'
    assert m.items == [Item('test', 'test')]
    assert m.escapable is False
    assert m.dump() == [m.title, [['test', 'test', [], {}]], False]
