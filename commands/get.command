id = a[0]
obj = Object.query(anchored=False, id=id, location_id=player.location_id).first()
if obj.coordinates != player.coordinates:
    player.message(f'You must walk to {obj.get_name(player.is_staff)} first.')
    end()
valid_object(player, obj)
if obj.followers:
    for follower in obj.followers:
        follower.message(f'You stop following {obj.get_name(follower.is_staff)}.')
    obj.followers.clear()
if obj.get_sound is not None:
    obj.sound(get_sound(obj.get_sound))
player.do_social(obj.get_msg, _others=[obj])
obj.holder_id = player.id
obj.location.broadcast_command(delete, obj.id)
obj.location_id = None
s.add(obj)