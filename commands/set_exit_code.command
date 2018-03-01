def parse_args(id, old=None, new=None):
    return (id, old, new)

id, old, new = parse_args(*a)
obj = Object.get(id)
valid_object(player, obj)
assert obj.is_exit, '%r is not an exit.' % obj
exit = obj.exit
if old is None:
    get_text(con, 'Enter the old code', __name__, args=[obj.id])
elif new is None:
    get_text(con, 'Enter the new code', __name__, args=[obj.id, old])
elif not exit.check_password(old):
    exit.incorrect_code(player)
else:
    exit.correct_code(player)
    exit.set_password(new)
    copy(con, new)
    player.message('New code set.')