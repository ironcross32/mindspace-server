check_admin(player)
if not a:
    items = [Item('Select Player', None)]
    for obj in Object.query(
        Object.player_id.isnot(None),
        Object.id.isnot(player.id),
        Object.location_id.isnot(player.location_id)
    ).order_by(Object.name):
        items.append(Item(obj.get_name(True), __name__, args=[obj.id]))
    m = Menu('Join Player', items, escapable=True)
    menu(con, m)
    end()
obj = Object.query(id=a[0]).first()
if obj is None:
    player.message('Invalid object.')
    end()
old = obj.location
if old is player.location:
    player.message(f'You are already with {obj.get_name()}.')
    end()
player.teleport(obj.location, obj.coordinates)
assert player.coordinates == obj.coordinates
s.add(player)