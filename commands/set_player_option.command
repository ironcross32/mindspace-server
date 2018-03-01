name, diff = a
obj = player.player
value = getattr(obj, name)
value += diff
if name.endswith('_volume'):
    if value > 1.0:
        value = 1.0
    elif value < 0.0:
        value = 0.0
setattr(obj, name, value)
player.message(
    '%s set to %g.' % (name.replace('_', ' ').title(), value)
)
obj.send_options(con)
