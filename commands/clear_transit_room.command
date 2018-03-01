check_builder(player)
route = TransitRoute.get(*a)
valid_object(player, route)
if route.room is None:
    player.message('Room already cleared.')
else:
    route.room = None
    player.message('ROom cleared.')