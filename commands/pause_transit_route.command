check_builder(player)
id, state = a
route = TransitRoute.get(id)
valid_object(player, route)
route.paused = state
player.message(f'{route.get_name(True)} {"paused" if state else "resumed"}.')