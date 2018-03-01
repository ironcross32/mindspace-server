check_builder(player)
zone = player.location.zone

if a:
    for name, value in a[0].items():
        setattr(zone, name, value)
    s.add(zone)
    try:
        s.commit()
        zone.update_occupants()
        player.message('Done.')
    except Exception as e:
        f = ObjectForm(zone, __name__, cancel='Cancel')
        form(con, f)
        player.message(str(e))
else:
    f = ObjectForm(zone, __name__, cancel='Cancel')
    form(con, f)