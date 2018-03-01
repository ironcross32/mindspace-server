check_builder(player)
items = [Item('Select Object', None)]
for obj in player.location.objects:
    if obj.is_player:
        continue
    items.append(Item(f'{obj.get_name(True)} ({util.directions(player.coordinates, obj.coordinates)})', 'delete_', args=['Object', obj.id]))
menu(con, Menu('Delete Object', items, escapable=True))