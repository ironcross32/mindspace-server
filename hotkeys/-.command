z = player.location.zone
ship = z.starship
check_in_space(player)
if ship.engine is None:
    player.message('No engines found.')
elif z.direction is None:
    player.message('You must first set a course.')
elif z.ambience_rate <= 0.0:
    player.message('The ship is not accelerating.')
else:
    obj.beep()
    z.ambience_rate = max(0.0, z.ambience_rate - 0.1)
    z.acceleration = ship.engine.max_acceleration * z.ambience_rate
    if not z.acceleration:
        z.acceleration = None
    z.update_occupants()
    s.add(z)