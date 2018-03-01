check_admin(player)
obj_id, type_id = a
obj = Object.get(obj_id)
type = ObjectType.get(type_id)
for thing in (obj, type):
    valid_object(player, thing)

obj.types.remove(type)
s.add(obj)
player.message(f'Removed type {type.get_name(True)} from {obj.get_name(True)}.')