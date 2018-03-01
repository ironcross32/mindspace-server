id = a[0]
obj = Object.get(id)
valid_object(player, obj)
check_location(player, obj)
if obj.coordinates != player.coordinates:
    player.message(f'{obj.get_name(player.is_staff).capitalize()} is just too far away.')
    end()
if obj.is_exit:
    # Let's leave through the exit:
    if player.last_name_change is None and player.location.zone_id != 1:
        player.message(
            'You must set your name before you can leave this room. You do this from the game menu (press the scape key).'
        )
    elif obj.exit.locked:
        exit = obj.exit
        player.do_social(exit.locked_msg, _others=[obj])
        if exit.locked_sound is not None:
            sound = get_sound(exit.locked_sound)
            obj.sound(sound)
        other_side = exit.get_other_side()
        if other_side is not None:
            other_side.do_social(exit.other_locked_msg)
            if exit.other_locked_sound is not None:
                sound = get_sound(exit.other_locked_sound)
                other_side.sound(sound)
    else:
        player.clear_following()
        obj.use_exit(player)
    end()
name = f'{obj.get_name(player.is_admin)} ({obj.get_type()})'
description = obj.get_description()
items = [
    Item(name, 'copy', args=[name]),
    Item(description, 'copy', args=[description])
]
if obj is player.following:
    items.append(Item('Stop Following', 'stop_following'))
elif obj.is_mobile or obj.is_player:
    items.append(Item('Follow', 'follow', args=[obj.id]))
if obj.hotkeys:
    items.append(Item('Start using', 'use', args=[obj.id]))
items.append(Item('Knock', 'knock', args=[obj.id]))
for action in obj.get_actions():
    if action.name is None or (action.admin and not player.is_admin) or (action.builder and not player.is_builder):
        continue
    items.append(
        Item(
            f'{action.get_name(player.is_staff)}: {action.get_description()}', 'action',
            args=[obj.id, action.id]
        )
    )
if obj.starship_id is not None:
    for room in obj.starship.zone.rooms:
        if room.airlock:
            items.append(Item(f'Board via {room.get_name(player.is_staff)}', 'board_starship', args=[obj.starship_id, room.id]))
if obj.transit_route is None:
    if player.is_staff:
        items.append(Item('Add Transit Route', 'add_transit_route', args=[obj.id]))
else:
    route = obj.transit_route
    if route.next_move is not None:
        seconds = int(route.next_move - time())
        eta = datetime.timedelta(seconds=seconds)
        items.append(CopyItem(f'Departing in {util.format_timedelta(eta)}.'))
    if route.room is not None:
        items.append(Item('Board', 'board_transit', args=[route.id]))
    if player.is_staff:
        if route.room is None:
            items.append(Item('Set Room', 'set_transit_room', args=[route.id]))
        else:
            items.append(Item('Clear Room', 'clear_transit_room', args=[route.id]))
        for name in ('edit', 'delete'):
            items.append(Item(f'{name.title()} Transit Route', f'{name}_', args=['TransitRoute', route.id]))
        for stop in route.stops:
            for name in ('edit', 'delete'):
                items.append(Item(f'{name.title()} {stop.location.get_name(True)} stop', f'{name}_', args=['TransitStop', stop.id]))
if obj.is_window:
    items.append(Item('Window', None))
    w = obj.window
    items.append(Item('Look Through', 'show_message', args=['You see:', w.overlooking.get_name(player.is_staff), w.overlooking.get_description()]))
    items.append(Item(f'{"Close" if w.open else "Open"} Window', 'set_window_state', args=[w.id, not w.open]))
if not obj.anchored and obj.location is player.location:
    items.append(Item('Get', 'get', args=[obj.id]))
elif obj.holder_id == player.id:
    items.extend(
        [
            Item('Give', 'give', args=[obj.id]),
            Item('Drop', 'drop', args=[obj.id])
        ]
    )
if player.is_staff:
    items.append(
        Item(
            f'#{obj.id}', 'copy', args=[str(obj.id)]
        )
    )
    if not obj.is_player:
        if player.is_admin:
            items.extend(
                [
                    Item('Object Types', None),
                    Item('Add Type', 'add_type', args=[obj.id]),
                ]
            )
            for type in obj.types:
                items.append(Item(f'Remove Type {type.get_name(True)}', 'remove_type', args=[obj.id, type.id]))
            items.append(Item('Add Action', 'add_action', args=[obj.id]))
            if obj.actions:
                items.append(Item('Delete Action', 'delete_action', args=[obj.id]))
            items.append(Item('Add Hotkey', 'add_hotkey', args=[obj.id]))
            if obj.hotkeys:
                items.append(Item('Delete Hotkey', 'remove_hotkey', args=[obj.id]))
        if player.is_builder:
            items.append(Item('Add Random Sound', 'add_random_sound', args=['Object', obj.id]))
            if obj.random_sounds:
                for name in ('edit', 'delete'):
                    items.append(Item(f'{name.title()} Random Sound', f'{name}_random_sound', args=['Object', obj.id]))
            if obj.is_window:
                for name in ('edit', 'delete'):
                    items.append(Item(f'{name.title()} Window', f'{name}_', args=['Window', obj.window_id]))
            else:
                items.append(Item('Make Window', 'make_window', args=[obj.id]))
            if obj.is_mobile:
                if obj.mobile.next_move:
                    items.append(
                        Item(
                            'Next move: %.2f seconds.' % (obj.mobile.next_move - time()), None
                        )
                    )
                items.extend(
                    [
                        Item('Configure Mobile', 'edit_', args=['Mobile', obj.mobile.id]),
                        Item('Remove Mobile', 'delete_', args=['Mobile', obj.mobile.id])
                    ]
                )
            else:
                items.append(Item('Make Mobile', 'make_mobile', args=[obj.id]))
if obj.is_player:
    if player.is_admin:
        items.append(LabelItem('Admin'))
        if obj.player.last_connected is None:
            items.append(CopyItem('Never connected.'))
        else:
            when = util.format_timedelta(datetime.datetime.utcnow() - obj.player.last_connected)
            items.append(CopyItem(f'Last connected {when} ago from {obj.player.last_host}.'))
        for name in ('builder', 'admin', 'transmition_banned'):
            value = getattr(obj.player, name)
            items.append(
                Item(
                    f'{"unset" if value else "set"} {name}',
                    'set_attribute', args=[
                        'player', obj.player.id, name, not value
                    ]
                )
            )
        if obj.connected:
            connection = obj.get_connection()
            items.append(Item('Manage Connection', 'connection_menu', args=[connection.host, connection.port]))
        else:
            a = obj.player
            items.append(
                Item(
                    f'{"Unlock" if a.locked else "Lock"} Account',
                    'lock_account', args=[a.id, not a.locked]
                )
            )
if not items:
    items.append(Item('No commands available.', None))
m = Menu(obj.get_name(player.is_admin), items, escapable=True)
menu(con, m)