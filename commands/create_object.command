check_builder(player)

def parse_args(type=None, name=None):
    return (type, name)

type, name = parse_args(*a)
if type is None:
    items = [
        Item('Select Type', None),
        Item('Standard Object', __name__, args=[0])
    ]
    for type in ObjectType.query():
        items.append(Item(type.get_name(True), __name__, args=[type.id]))
    menu(con, Menu('Create Object', items, escapable=True))
elif not name:
    get_text(con, 'Enter a name for your new object', __name__, args=[type])
else:
    if type:
        type = ObjectType.get(type)
        valid_object(player, type)
    else:
        type = None
    obj = Object(name=name, location_id = player.location_id, owner_id=player.id)
    obj.coordinates = player.coordinates
    if type is not None:
        obj.types.append(type)
    s.add(obj)
    s.commit()
    player.message(f'Created {"object" if type is None else type.get_name(True).lower()} {obj.get_name(True)}.')