def parse_args(id, target_id=None):
    return (id, target_id)

id, target_id = parse_args(*a)
obj = Object.query(holder_id=player.id, id=id).first()
valid_object(player, obj)
if target_id is None:
    targets = Object.query(Object.id != player.id, Object.player_id.isnot(None), *player.same_coordinates(), location_id=player.location_id)
    if not targets.count():
        player.message(f'There is nobody here to give {obj.get_name(player.is_staff)} to.')
        end()
    items = [Item('Players', None)]
    for target in targets:
        items.append(Item(target.get_name(player.is_staff), __name__, args=[obj.id, target.id]))
    menu(con, Menu('Give', items, escapable=True))
    end()
target = Object.query(*player.same_coordinates(), id=target_id, location_id=player.location_id).first()
valid_object(player, target)
player.do_social(obj.give_msg, _others=[obj, target])
if obj.give_sound is not None:
    player.sound(get_sound(obj.give_sound))
obj.holder_id = target.id
s.add(obj)