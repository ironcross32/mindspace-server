check_admin(player)
host, port = a
for connection in server.connections:
    if connection.host == host and connection.port == port:
        if connection.last_active:
            duration = time() - connection.last_active
            last_active = f'Last active: {util.format_timedelta(datetime.timedelta(seconds=duration))} ago at {ctime(connection.last_active)}'
        else:
            last_active = 'Never active'
        items = [
            Item('Manage Connection', None),
            Item(f'IP Address: {host}', 'copy', args=[host]),
            Item(f'Port: {port}', 'copy', args=[str(port)]),
            Item(last_active, 'copy', args=[last_active]),
            Item('Disconnect', 'disconnect', args=[f'{host}:{port}']),
            Item('Ban IP', 'ban', args=[host])
        ]
        items.append(
            Item(
                f'{"Unlock" if connection.locked else "Lock"} Connection',
                'lock_connection', args=[f'{host}:{port}', not connection.locked]
            )
        )
        if connection.player_id is not None:
            account = connection.get_player(s).player
            items.append(
                Item(
                    f'{"Unlock" if account.locked else "Lock"} Account',
                    'lock_account', args=[account.id, not account.locked]
                )
            )
        menu(con, Menu('Connection', items, escapable=True))
        break
else:
    player.message('No such connection.')