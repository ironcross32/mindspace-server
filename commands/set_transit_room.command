check_builder(player)

def parse_args(route_id, room_id=None):
    return (route_id, room_id)

route_id, room_id = parse_args(*a)
route = TransitRoute.get(route_id)
valid_object(player, route)
if room_id is None:
    items = [Item('Select Room', None)]
    for room in player.location.zone.rooms:
        items.append(Item(room.get_name(True), __name__, args=[route.id, room.id]))
    menu(con, Menu('Add Room', items, escapable=True))
else:
    room = Room.get(room_id)
    valid_object(player, room)
    if route.room is not None:
        player.message(f'{obj.get_name(True)} is already accessible via {obj.transit_route.room.get_name(True)}.')
    else:
        route.room = room
        s.add(route)
        s.commit()
        player.message(f'Attached {room.get_name(True)} to {route.get_name(True)}.')