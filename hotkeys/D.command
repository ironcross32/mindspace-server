zone = player.location.zone
ship = zone.starship
if ship is None or ship.sensors is None:
    player.message('No sensors found.')
    end()
obj = ship.last_scanned
if obj is None or obj not in zone.visible_objects():
    player.message('Nothing scanned.')
    end()
ship.play_object_sound(obj, player)
directions = util.directions(zone.coordinates, obj.coordinates, format=util.format_distance_simple)
player.message(f'{obj.get_name(player.is_staff)} ({obj.get_type()}): {directions}.')