items = [
    Item('Building Menu', None),
    Item('Set floor Type', 'set_floor_type'),
    Item('Bulk Set Floor Types', 'set_floor_type_range'),
    Item('Create Room', 'create_room'),
    Item('Create Object', 'create_object'),
    Item('Build Exit', 'build_exit'),
    Item('Build Portal', 'build_portal'),
    Item('Configure Room Objects', 'configure_object'),
    Item('Random Sounds', None),
    Item('Add Random Sound', 'add_random_sound', args=['Room', player.location.id]),
    Item('Edit Random Sound', 'edit_random_sound', args=['Room', player.location.id]),
    Item('Delete Random Sound', 'delete_random_sound', args=['Room', player.location.id]),
    Item('Configuration', None),
    Item('Configure Room', 'key', args=['F2']),
    Item('Configure Zone', 'configure_zone'),
    Item('Delete Room Object', 'delete_object'),
    Item('Reset Flooring', 'reset_floor_types'),
    Item('Add Zone', 'add_zone'),
    Item('Preview Sounds', 'preview_sounds'),
    Item('Add Transit Stop', 'add_transit_stop')
]
obj = player.location
items.append(LabelItem('Room Flags'))
if obj.airlock_id is None:
    items.append(Item('Add Airlock', 'create_airlock'))
else:
    for name in ('edit', 'delete'):
        items.append(Item(f'{name.title()} Airlock', f'{name}_', args=['RoomAirlock', obj.airlock_id]))
if obj.airlock is not None:
    items.append(Item('Configure Airlock', 'edit_', args=['RoomAirlock', obj.airlock_id]))
if obj.transit_route is not None:
    route = obj.transit_route
    items.append(LabelItem(route.get_name(True)))
    items.append(Item('Resume' if route.paused else 'Pause', 'pause_transit_route', args=[route.id, not route.paused]))
    for name in ('edit', 'delete'):
        items.append(Item(f'{name.title()} Transit Route', f'{name}_', args=['TransitRoute', route.id]))
    items.append(Item(f'Stops ({len(route.stops)})', None))
    for stop in route.stops:
        for name in ('edit', 'delete'):
            items.append(Item(f'{name.title()} {stop.location.get_name(True)} stop', f'{name}_', args=['TransitStop', stop.id]))
menu(con, Menu('Building Commands', items, escapable=True))