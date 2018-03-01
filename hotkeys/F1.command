items = [LabelItem('Hotkeys')]
for key in Hotkey.query(reusable=False).order_by(Hotkey.name):
    if key.objects:
        continue
    modifiers = []
    args=[key.name, []]
    for name in ('ctrl', 'shift', 'alt'):
        value = getattr(key, name)
        if value is None:
            modifiers.append(f'[{name}]')
        elif value is True:
            args[-1].append(name)
            modifiers.append(name.upper())
    items.append(Item(f'{" ".join(modifiers)}{" " if modifiers else ""}{key.get_name(player.is_staff)}: {key.get_description()}', 'key', args=args))
menu(con, Menu('Hotkeys', items, escapable=True))