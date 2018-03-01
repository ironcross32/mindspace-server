def parse_args(id, state, code=None):
    return (id, state, code)

id, state, code = parse_args(*a)
obj = Object.get(id)
valid_object(player, obj)
exit = obj.exit
valid_object(player, exit)

if exit.locked is state:
    player.message(f'{obj.get_name(player.is_staff)} is already {"locked" if state else "unlocked"}.')
elif not state and exit.password is not None and code is None:
    exit.enter_code(player)
    get_text(con, 'Enter code', __name__, args=[obj.id, state])
elif not state and exit.password is not None and not exit.check_password(code):
    exit.incorrect_code(player)
else:
    if not state and exit.password is not None:
        exit.correct_code(player)
    exit.locked = state
    s.add(exit)
    if state:
        msg = exit.lock_msg
        other_msg = exit.other_lock_msg
        sound = exit.lock_sound
        other_sound = exit.other_lock_sound
    else:
        msg = exit.unlock_msg
        other_msg = exit.other_unlock_msg
        sound = exit.unlock_sound
        other_sound = exit.other_unlock_sound
    player.do_social(msg, _others=[obj])
    other_side = exit.get_other_side()
    if other_side is not None:
        other_side.exit.lockable=True  # Fix any dodgy exits.
        other_side.exit.locked = state
        s.add(other_side.exit)
        other_side.do_social(other_msg)
        if other_sound is not None:
            other_sound = get_sound(other_sound)
            other_side.sound(other_sound)
    if sound is not None:
        sound = get_sound(sound)
        obj.sound(sound)