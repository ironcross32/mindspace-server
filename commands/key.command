possible_modifiers = ('ctrl', 'shift', 'alt')

def parse_args(name, modifiers=None):
    if modifiers is None:
        modifiers = []
    return (name, modifiers)

def check_hotkey(hotkey, modifiers):
    global possible_modifiers
    for mod in possible_modifiers:
        value = getattr(hotkey, mod)
        if value not in (None, mod in modifiers):
            return False
    return True

name, modifiers = parse_args(*a)

if getattr(con, 'debug', False):
    player.message(f'{modifiers}: {name}.')

if con.object_id is None:
    obj = None
else:
    obj = Object.get(con.object_id)
    if obj is None:
        con.object_id = None

kwargs = dict(modifiers=modifiers)
if obj is None:
    query_args = [Hotkey.name == name]
    if not player.is_builder:
        query_args.append(Hotkey.builder.is_(False))
    if not player.is_admin:
        query_args.append(Hotkey.admin.is_(False))
    for mod in possible_modifiers:
        column = getattr(Hotkey, mod)
        query_args.append(
            sqlalchemy.or_(
                column.is_(None),
                column.is_(mod in modifiers)
            )
        )
    keys = Hotkey.query(*query_args, reusable=False)
elif name == 'ESCAPE':
    con.object_id = None
    player.do_social(obj.stop_use_msg, _others=[obj])
    end()
elif name == 'F1':
    obj = Object.get(con.object_id)
    items = [LabelItem('Hotkeys')]
    for key in obj.get_hotkeys():
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
    end()
else:
    kwargs['obj'] = obj
    keys = []
    for hotkey in obj.get_hotkeys():
        if hotkey.name == name and check_hotkey(hotkey, modifiers):
            keys.append(hotkey)
for key in keys:
    run_program(con, s, key, **kwargs)
