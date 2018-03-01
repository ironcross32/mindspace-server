check_builder(player)

def parse_args(zone=None, room=None):
    return (zone, room)

zone, room = parse_args(*a)
if zone is None:
    items = [Item('Select Zone', None)]
    for z in s.query(Zone).order_by(Zone.name):
        items.append(Item(z.get_name(True), __name__, args=[z.id]))
    menu(con, Menu('Teleport', items, escapable=True))
elif room is None:
    zone = s.query(Zone).get(zone)
    if zone is None:
        player.message('Invalid zone.')
        end()
    items = [Item('Select Room', None)]
    for r in s.query(Room).filter_by(zone=zone).order_by(Room.name):
        items.append(Item(r.get_name(True), __name__, [zone.id, r.id]))
    menu(con, Menu('Teleport', items, escapable=True))
else:
    room = s.query(Room).get(room)
    if room is None:
        player.message('Invalid room.')
        end()
    player.teleport(room, (0.0, 0.0, 0.0))