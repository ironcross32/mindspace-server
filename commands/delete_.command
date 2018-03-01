check_admin(player)

def parse_args(t, id=None, res=None):
    return (t, id, res)

type, id, response = parse_args(*a)
cls = Base._decl_class_registry[type]
if id is None:
    items = [Item(f'Select {cls.__name__}', None)]
    for obj in s.query(cls).order_by(cls.name):
        items.append(Item(obj.get_name(True), __name__, args=[type, obj.id]))
    m = Menu(f'Delete {cls.__name__}', items, escapable=True)
    menu(con, m)
    end()
obj = s.query(cls).get(id)
if obj is None:
    player.message('Invalid object.')
    end()
if response is None:
    m = Menu(
        f'Are you sure you want to delete {obj.get_name(True) if hasattr(obj, "get_name") else "this " + type}?', [
            Item('Yes', __name__, args=[type, obj.id, True]),
            Item('No', __name__, args=[type, obj.id, False])
        ]
    )
    menu(con, m)
elif response:
    if isinstance(obj, Object):
        if obj.is_player:
            player.message('You cannot delete players.')
            end()
        elif obj.is_exit:
            s.delete(obj.exit)
    s.delete(obj)
    player.message('Deleted.')
else:
    player.message('Not deleting.')