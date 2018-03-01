items = []
number = 0
for connection in server.connections:
    obj = connection.get_player(s)
    if obj is not None:
        items.append(Item(obj.get_name(player.is_staff), 'compose_mail', args=[obj.id]))
        number += 1
items.insert(0, Item(f'Connected Players ({number})', None))
menu(con, Menu('Who', items, escapable=True))