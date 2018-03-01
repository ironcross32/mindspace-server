id, state = a
window = Window.get(id)
valid_object(player, window)
obj = window.object
if state == window.open:
    player.message(f'{obj.get_name(player.is_staff).title()} is already {"open" if state else "closed"}.')
else:
    if state:
        msg = window.open_msg
        sound = window.open_sound
    else:
        msg = window.close_msg
        sound = window.close_sound
    if sound is not None:
        obj.sound(get_sound(sound))
    player.do_social(msg, _others=[obj])
    window.opened = state