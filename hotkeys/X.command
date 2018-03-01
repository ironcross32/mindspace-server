zone = player.location.zone
ship = zone.starship
if ship is None or ship.sensors is None:
    player.message('No sensors found.')
    end()
obj = ship.last_scanned
if obj is None or obj not in zone.visible_objects():
    player.message('Nothing scanned.')
    end()
player.message(obj.get_name(player.is_staff))
player.message(f'Type: {obj.get_type()}')
player.message(f'Speed: {"not moving" if obj.speed is None else util.format_speed(obj.speed)}')
player.message('Coordinates: (%.2f, %.2f, %.2f)' % obj.coordinates)
player.message(f'Orbiting: {"nothing" if obj.orbit is None else obj.orbit.orbiting.get_name(player.is_staff)}')