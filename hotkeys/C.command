items = [Item('Select Object', None)]
for obj in player.location.objects:
    items.append(Item(f'{obj.get_name(True)}: {util.directions(player.coordinates, obj.coordinates)}', 'edit_', args=[obj.__class__.__name__, obj.id]))
menu(con, Menu('Configure Object', items, escapable=True))