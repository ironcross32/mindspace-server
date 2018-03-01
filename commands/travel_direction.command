if time() - player.last_walked < player.speed:
    end()
key, modifiers = a

name = Direction.key_to_name(key)
direction = Direction.query(name=name, z=0.0).first()
if con.walk_task is not None:
    con.walk_task.stop()
    con.walk_task = None
if 'shift' in modifiers:
    x, y, z = player.get_corner_coordinates(direction)
    if (x, y, z) == player.coordinates:
        player.message(f'You are already as far {direction.get_name()} as you can go.')
    else:
        con.handle_command('autostroll', dict(x=x, y=y))
else:
    util.walk(player, x=direction.x, y=direction.y)