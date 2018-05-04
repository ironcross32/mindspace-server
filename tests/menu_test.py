from server.menus import DeleteMenu, Item, LabelItem


def test_delete_menu():
    m = DeleteMenu('test', 'test')
    assert len(m.items) == 3
    assert m.items[0] == LabelItem('test')
    assert m.items[1] == Item('Yes', 'test', args=[True])
    assert m.items[2] == Item('No', 'test', args=[False])
