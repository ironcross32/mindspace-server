id = a[0]
check_admin(player)
if isinstance(id, int):
    obj = s.query(Object).get(id)
    if obj is None:
        player.message('Invalid id %r.' % id)
        end()
    obj_con = obj.get_connection()
    if obj_con is None:
        player.message(f'{obj.get_name(True)} is not connected.')
        end()
elif isinstance(id, str):
    for obj_con in server.connections:
        if f'{obj_con.host}:{obj_con.port}' == id:
            break
    else:
        player.message('No such connection.')
        end()
player.message('Disconnecting.')
obj_con.disconnect(f'You have been booted off the server by {player.get_name()}.')