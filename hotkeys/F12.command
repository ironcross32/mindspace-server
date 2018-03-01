if not player.holding:
    player.message('You are empty handed.')
    end()
items = [Item('Inventory', None)]
for obj in player.holding:
    items.append(Item(obj.get_name(player.is_staff), 'interact_object', args=[obj.id]))
menu(con, Menu('Inventory', items, escapable=True))