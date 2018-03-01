zone = player.location.zone
ship = zone.starship
if ship is None or ship.sensors is None:
    player.message('No sensors found.')
else:
    objects = 0
    for obj in zone.visible_objects():
        objects += 1
        ship.play_object_sound(obj, player)
    player.message(f'{objects} sensor {util.pluralise(objects, "contact")}.')