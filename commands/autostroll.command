if con.walk_task is not None:
    if con.walk_task.running:
        con.walk_task.stop()
    con.walk_task = None
    player.message('You stop walking.')
elif not a:
    obj = player.scanned
    if obj is None:
        obj = player
    items = [Label('Enter coordinates to walk to')]
    for name in ('x', 'y'):
        items.append(Field(name, int(getattr(obj, name)), type=int))
    f = Form('Autostroll', items, __name__, cancel='Cancel')
    form(con, f)
else:
    data = a[0]
    x = data['x']
    y = data['y']
    z = player.z
    if (x, y, z) == player.coordinates:
        player.message('You are already there.')
        end()
    con.walk_task = util.WalkTask(player.id, x, y, z)
    obj = Object.query(location_id=player.location_id, x=x, y=y, z=z).first()
    if obj:
        player.message(f'You begin walking towards {obj.get_name(player.is_staff)}.')
    else:
        player.message('You begin walking.')
    con.walk_task.start()