check_builder(player)
if a:
    name = a[0]
else:
    name = ''
if not name:
    get_text(
        con, 'Enter a name for your new room', 'create_room'
    )
elif player is not player.location.zone.owner and not player.is_admin:
    player.message('You cannot build here.')
else:
    r = Room(name=name, zone=player.location.zone)
    s.add(r)
    s.commit()
    player.message(f'Created room {r.get_name(True)}.')