q = Object.query(Object.id != player.id, *player.same_coordinates(), location_id=player.location_id)
objects = []
items = [Item('Select Object', None)]
for obj in q:
    if obj.get_hotkeys():
        objects.append(obj)
        items.append(Item(obj.get_name(player.is_staff), 'use', args=[obj.id]))
if not objects:
    player.message('There is nothing to use.')
elif len(objects) == 1:
    con.handle_command('use', objects[0].id)
else:
    menu(con, Menu('Use Object', items, escapable=True))