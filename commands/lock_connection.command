spec, value = a
check_perms(player, admin=True)
for obj_con in server.connections:
    if f'{obj_con.host}:{obj_con.port}' == spec:
        obj_con.set_locked(value)
        message(
            con,
            f'Connection {"locked" if value else "unlocked"}.'
        )
        break
else:
    message(con, 'Invalid connection.')