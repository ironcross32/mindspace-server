z = player.location.zone
check_in_space(player)
now = time()
diff = now - z.last_turn
if z.speed is None:
    player.message('You are not moving.')
elif diff > z.speed:
    obj.beep()
    z.last_turn = now
    z.accelerating = not z.accelerating
    player.message(f'Starship {"accelerating" if z.accelerating else "decelerating"}.')
else:
    player.message('You must wait %.2f seconds before changing direction.' % diff)