obj.beep()
z = obj.location.zone
if z.speed is None:
    player.message('Not moving.')
else:
    player.message(util.format_speed(z.speed))