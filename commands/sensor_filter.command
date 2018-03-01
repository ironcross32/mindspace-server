zone, ship = valid_sensors(player)
obj = Object.get(con.object_id)
valid_object(player, obj)
index = a[0]
if not index:
    index = 9
else:
    index -= 1
names = [x for x in dir(ship) if x.startswith('filter_')]
try:
    name = names[index]
    string = name.replace('_', ' ')
    value = not getattr(ship, name)
    if value:
        msg = string.capitalize()
    else:
        msg = "Don't " + string
    setattr(ship, name, value)
    obj.beep()
    player.message(msg)
except IndexError:
    player.message('There is no filter at that position.')