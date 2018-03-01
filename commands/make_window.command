check_builder(player)

def parse_args(id, overlooking_id=None):
    return (id, overlooking_id)

id, overlooking_id = parse_args(*a)
obj = Object.get(id)
valid_object(player, obj)
if overlooking_id is None:
    items = [Item('Select Room', None)]
    for room in obj.location.zone.rooms:
        if room is not obj.location:
            items.append(Item(room.get_name(True), __name__, args=[obj.id, room.id]))
    menu(con, Menu('Select a room to overlook', items, escapable=True))
else:
    overlooking = Room.get(overlooking_id)
    valid_object(player, overlooking)
    w = Window(overlooking_id=overlooking_id)
    obj.window = w
    s.add(w)
    s.commit()
    player.message('Done.')