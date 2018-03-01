check_admin(player)
if not a:
    items = [Item('Select Player', None)]
    for obj in s.query(Object).filter(
        Object.player_id.isnot(None),
        Object.id.isnot(player.id),
        Object.location_id.isnot(player.location_id)
    ).order_by(Object.name):
        items.append(Item(obj.get_name(True), __name__, args=[obj.id]))
    m = Menu('Bring Player', items, escapable=True)
    menu(con, m)
    end()
obj = s.query(Object).get(a[0])
if obj is None:
    player.message('Invalid object.')
    end()
old = obj.location
if old is player.location:
    player.message(f'{obj.get_name(True)} is already here.')
    end()
obj.teleport(player.location, player.coordinates)
s.add(obj)