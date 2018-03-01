z = player.location.zone
ship = z.starship
check_in_space(player)
if ship.engine is None:
    player.message('No engines found.')
elif z.direction is None:
    player.message('You must first set a course.')
elif z.ambience_rate >= 1.0:
    player.message('The ship is at full thrust.')
else:
    obj.beep()
    z.ambience_rate = min(1.0, z.ambience_rate + 0.1)
    z.acceleration = ship.engine.max_acceleration * z.ambience_rate
    z.update_occupants()
    s.add(z)