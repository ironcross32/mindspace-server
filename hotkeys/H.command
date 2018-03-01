z = obj.location.zone
obj.beep()
if z.direction is None:
    player.message('You have no course.')
else:
    player.message(f'Heading: {z.direction.name.title()}.')