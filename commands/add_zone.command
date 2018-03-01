check_admin(player)
if a:
    name = a[0]
    if name:
        z = Zone(name=name, owner_id=player.id)
        r = Room(name='The First Room', zone=z)
        s.add_all([z, r])
        player.message(f'Created zone {name}.')
    else:
        player.message('Your zone must have a name.')
else:
    get_text(con, 'Enter the name of your new zone', __name__)