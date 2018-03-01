check_admin(player)

def parse_args(obj_id, type_id=None):
    return (obj_id, type_id)

obj_id, type_id = parse_args(*a)

obj = Object.get(obj_id)
valid_object(player, obj)
if type_id is None:
    items = [Item('Select Type', None)]
    for type in ObjectType.query():
        if type not in obj.types:
            items.append(Item(type.get_name(True), __name__, args=[obj.id, type.id]))
    menu(con, Menu('Add Object Type', items, escapable=True))
    end()
type = ObjectType.get(type_id)
valid_object(player, type)
obj.types.append(type)
s.add(obj)
player.message(f'Added {type.get_name(True)} to {obj.get_name(True)}.')