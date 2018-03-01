check_admin(player)

def parse_args(type_name, id=None, type_id=None):
    return (type_name, id, type_id)

type_name, id, type_id = parse_args(*a)

other = type_name.lower() + 's'
cls = Base._decl_class_registry[type_name]

if id is None:
    items = [Item('Select Object Type', None)]
    for type in ObjectType.query():
        items.append(Item(type.get_name(True), __name__, args=[type_name, type.id]))
    menu(con, Menu(f'{__name__.title()} {type_name}', items, escapable=True))
    end()

type = ObjectType.get(id)
valid_object(player, type)

if type_id is None:
    kwargs = {}
    if cls == Hotkey:
        kwargs['reusable'] = True
    objects = cls.query(**kwargs)
    items = [Item(f'Select {type_name}', None)]
    for obj in objects:
        if obj not in getattr(type, other):
            name = obj.get_name(True)
            if callable(getattr(obj, 'get_description')):
                name = f'{name} {obj.get_description()}'
            items.append(Item(name, __name__, args=[type_name, type.id, obj.id]))
    menu(con, Menu(f'{__name__.title()} {type_name}', items, escapable=True))
    end()

obj = cls.get(type_id)
valid_object(player, obj)
getattr(type, other).append(obj)
s.add(type)
player.message(f'Added {obj.get_name(True)} to {type.get_name(True)}.')