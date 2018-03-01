obj = Object.get(*a)
valid_object(player, obj)
exit = obj.exit
valid_object(player, exit)
items = [
    Item(obj.get_name(player.is_staff), None),
    Item('Knock', 'knock', args=[obj.id])
]
if exit.lockable:
    items.append(
        Item(
            'Unlock' if exit.locked else 'Lock', 'lock_exit',
            args=[obj.id, not exit.locked]
        )
    )
    if exit.password is not None:
        items.append(
            Item('Set Code', 'set_exit_code', args=[obj.id])
        )
if exit.has_chime:
    items.append(Item('Chime', 'chime', args=[obj.id]))
if player.is_staff:
    items.append(
        Item('Configure', 'edit_', args=['Entrance', exit.id])
    )
    other_side = obj.exit.get_other_side()
    if other_side is not None:
        items.append(Item('Configure (Other Side)', 'edit_', args=['Object', other_side.id]))
    if exit.password is None:
        items.append(Item('Add Code', 'add_exit_code', args=[exit.id]))
    else:
        items.extend(
            [
                Item('Clear Code', 'clear_exit_code', args=[exit.id]),
                Item('Remove Code', 'remove_exit_code', args=[exit.id])
            ]
        )
if len(items) == 1:
    player.message(f'{obj.get_name(player.is_staff)} is not a door.')
else:
    menu(con, Menu('Door Menu', items, escapable=True))