check_builder(player)
if a:
    data = a[0]
else:
    data = None
id = kw.get('id', None)
if id is None:
    items = [Item('Select an object', None)]
    for obj in player.location.objects:
        name = obj.get_name(True)
        where = util.directions(player.coordinates, obj.coordinates)
        items.append(
            Item(
                f'{name} ({where})', 'configure_object',
                kwargs=dict(id=obj.id)
            )
        )
    m = Menu('Select an object', items, escapable=True)
    menu(con, m)
    end()
obj = Object.query(
    location_id=player.location_id, id=id
).first()
if obj is None:
    player.message('Invalid object.')
    end()
con.handle_command('edit_', 'Object', id)