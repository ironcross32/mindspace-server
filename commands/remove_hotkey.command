check_admin(player)

def parse_args(id, hotkey_id=None):
    return (id, hotkey_id)

id, hotkey_id = parse_args(*a)
obj = Object.get(id)
valid_object(player, obj)
if hotkey_id is None:
    items = [Item('Select Hotkey', None)]
    for hotkey in obj.hotkeys:
        items.append(Item(f'{hotkey.get_name(True)}: {hotkey.get_description()}', __name__, args=[id, hotkey.id]))
    menu(con, Menu('Remove Hotkey', items, escapable=True))
else:
    hotkey = Hotkey.get(hotkey_id)
    if hotkey not in obj.hotkeys:
        hotkey = None
    valid_object(player, hotkey)
    obj.hotkeys.remove(hotkey)
    s.add(obj)
    player.message(f'Deleted hotkey {hotkey.get_name(True)} from {obj.get_name(True)}.')