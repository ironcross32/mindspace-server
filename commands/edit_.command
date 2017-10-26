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
    raise RuntimeError('Incorrect number of arguments: %r.' % a)
type, id, data = a
if type == 'command':
    cls = Command
elif type == 'hotkey':
    cls = Hotkey
else:
    raise RuntimeError('Invalid type: %r.' % type)
if id is None:
    items = []
    for thing in s.query(cls):
        items.append(Item(thing.get_name(True), __name__, args=[type, thing.id]))
    m = Menu('Choose a %s' % cls.__name__.lower(), items, escapable=True)
    menu(con, m)
    end()
obj = s.query(cls).get(id)
if obj is None:
    player.message('Invalid object.')
    end()
if data:
    if all(data.values()):
        for name, value in data.items():
            setattr(obj, name, value)
        try:
            obj.set_code(obj.code)
            s.add(obj)
            s.commit()
            player.message('Edits saved.')
            end()
        except OK:
            end()
        except Exception as e:
            player.message(repr(e))
    else:
        player.message('All fields are required.')
form(con, ObjectForm(obj, __name__, args=[type, obj.id], cancel='Cancel'))
