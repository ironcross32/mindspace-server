zone = player.location.zone
ship = zone.starship
if not ship.sensors:
    player.message('No sensors found.')
    end()
objects = zone.visible_objects()
if not objects:
    ship.last_scanned = None
    player.message('Nothing on scan.')
    end()
if ship.last_scanned is None or ship.last_scanned not in objects:
    ship.last_scanned = objects[0]
else:
    i = objects.index(ship.last_scanned)
    if 'shift' in modifiers:
        i -= 1
    else:
        i += 1
    if i >= len(objects):
        obj = objects[0]
    else:
        obj = objects[i]
    ship.last_scanned = obj
obj = ship.last_scanned
ship.play_object_sound(obj, player)
distance = util.format_distance_simple(util.distance_between(zone.coordinates, obj.coordinates))
direction = util.direction_between(zone.coordinates, obj.coordinates)
if direction is None:
    direction = ''
else:
    direction = ' ' + direction.name
player.message(f'{obj.get_name(player.is_staff)} ({obj.get_type()}): {distance}{direction}.')