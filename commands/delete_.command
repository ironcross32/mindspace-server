player = con.get_player()
a = list(a)
if not player.is_admin:
    end()
elif len(a) == 1:
    a.extend([None, None])
elif len(a) == 2:
    a.append(None)
elif len(a) == 3:
    pass  # Perfect.
else:
    raise RuntimeError('Invalid arguments: %r.' % a)
type, id, response = a
if type == 'hotkey':
    cls = Hotkey
elif type == 'command':
    cls = Command
else:
    raise RuntimeError('Invalid type %r.' % type)
if id is None:
    items = []
    for obj in s.query(cls):
        items.append(Item(obj.get_name(True), __name__, args=[type, obj.id]))
    m = Menu('Select Object', items, escapable=True)
    menu(con, m)
    end()
obj = s.query(cls).get(id)
if obj is None:
    player.message('Invalid object.')
    end()
if response is None:
    m = Menu(
        f'Are you sure you want to delete {type} {obj.get_name(True)}?', [
            Item('Yes', __name__, args=[type, obj.id, True]),
            Item('No', __name__, args=[type, obj.id, False])
        ]
    )
    menu(con, m)
elif response:
    s.delete(obj)
    player.message('Deleted.')
else:
    player.message('Not deleting.')
