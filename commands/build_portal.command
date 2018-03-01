check_builder(player)

def parse_args(zone_id=None, room_id=None, name=None):
    return (zone_id, room_id, name)

zone_id, room_id, name = parse_args(*a)
if zone_id is None:
    items = [Item('Select Zone', None)]
    for z in s.query(Zone).order_by(Zone.name):
        items.append(Item(z.get_name(True), __name__, args=[z.id]))
    menu(con, Menu('Build Portal', items, escapable=True))
    end()
z = s.query(Zone).get(zone_id)
if z is None:
    player.message('Invalid zone.')
    end()
if room_id is None:
    items = [Item('Select Rom', None)]
    for r in s.query(Room).filter_by(zone_id=z.id).order_by(Room.name):
        items.append(Item(r.get_name(True), __name__, args=[z.id, r.id]))
    menu(con, Menu('Build Portal', items, escapable=True))
    end()
r = s.query(Room).filter_by(id=room_id, zone_id=z.id).first()
if r is None:
    player.message('Invalid room.')
    end()
if name is None:
    get_text(con, 'Enter the name for your new portal', __name__, args=[z.id, r.id])
    end()
con.handle_command('build_exit', name, r.id)