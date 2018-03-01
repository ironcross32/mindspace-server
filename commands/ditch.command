id = a[0]
obj = Object.get(id)
valid_object(player, obj)
if obj not in player.followers:
    player.message(f'{obj.get_name(player.is_staff)} is not following you.')
else:
    player.followers.remove(obj)
    player.do_social(player.ditch_msg, _others=[obj])