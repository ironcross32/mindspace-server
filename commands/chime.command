obj = Object.get(*a)
assert obj.is_exit, '%r is not an exit.' % obj
exit = obj.exit
if not exit.has_chime:
    player.message(f'{obj.get_name(player.is_staff).capitalize()} has not chime.')
    end()
sound = get_sound(exit.chime_sound)
player.do_social(exit.chime_msg, _others=[obj])
obj.sound(sound)
exit.location.broadcast_command(random_sound, sound, *exit.coordinates, 1.0)