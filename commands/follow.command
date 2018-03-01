if player.followers:
    player.message('You must ditch your followers first.')
    end()
id = a[0]
obj = s.query(Object).get(id)
if obj is None:
    player.message('Invalid object.')
elif obj is player.following:
    player.message(f'You are already following {obj.get_name(player.is_staff)}.')
elif obj.location is not player.location or obj.coordinates != player.coordinates:
    player.message(f'You are not close enough to {obj.get_name(player.is_staff)} to follow.')
else:
    player.following = obj
    player.do_social(player.follow_msg, _others=[obj])