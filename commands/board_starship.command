starship_id, room_id = a
starship = Starship.get(starship_id)
room = Room.query(Room.airlock_id.isnot(None), id=room_id).first()
for obj in (room, starship):
    valid_object(player, obj)
obj = starship.object
check_location(player, obj)
if room not in starship.zone.rooms:
    player.message('No such airlock.')
else:
    airlock = room.airlock
    util.migrate(player, obj, room, airlock.coordinates, airlock.board_msg, airlock.board_sound, airlock.board_other_msg, airlock.board_other_sound, airlock.board_follow_msg)