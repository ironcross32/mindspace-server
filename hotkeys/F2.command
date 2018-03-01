if player.is_builder:
    loc = player.location
    f = ObjectForm(
        loc, 'configure_room', args=[loc.id],
        cancel='Cancel'
    )
    form(con, f)