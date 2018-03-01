check_admin(player)
items = [Item(f'Connections ({len(server.connections)})', None)]
for connection in server.connections:
    obj = connection.get_player(s)
    if obj is None:
        name = 'Anonymous connection'
    else:
        name = obj.get_name(True)
    items.append(
        Item(
            f'{name} ({connection.host}:{connection.port})',
            'connection_menu', args=[connection.host, connection.port]
        )
    )
q = BannedIP.query()
items.append(Item(f'Banned IP Addresses ({q.count()})', None))
for addr in q:
    items.append(Item(f'{addr.ip} ({addr.owner.get_name(True) if addr.owner is not None else "Anonymous"})', 'unban', args=[addr.ip]))
menu(con, Menu('Manage Connections', items, escapable=True))