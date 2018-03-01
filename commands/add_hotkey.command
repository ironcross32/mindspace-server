check_admin(player)

def parse_args(id, hotkey_id=None):
    return (id, hotkey_id)

id, hotkey_id = parse_args(*a)
obj = Object.get(id)
valid_object(player, obj)
if hotkey_id is None:
    items = [Item('Select Hotkey', None)]
    for h in Hotkey.query(reusable=True).order_by(Hotkey.name):
        items.append(Item(f'{h.get_name(True)}: {h.description}', __name__, args=[id, h.id]))
    menu(con, Menu('Add Hotkey', items, escapable=True))
else:
    h = Hotkey.query(id=hotkey_id, reusable=True).first()
    valid_object(player, h)
    obj.hotkeys.append(h)
    s.add(obj)
    player.message(f'Added {h.get_name(True)} to {obj.get_name(True)}.')