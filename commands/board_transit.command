route = TransitRoute.get(*a)
valid_object(player, route)
obj = route.object
check_location(player, obj)
room = route.room
if room is None:
    player.message('No boarding allowed.')
else:
    util.migrate(player, obj, room, route.coordinates, route.board_msg, route.board_sound, route.board_other_msg, route.board_other_sound, route.board_follow_msg)