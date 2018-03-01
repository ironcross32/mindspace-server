id = a[0]
obj = Object.query(id=id, holder_id=player.id).first()
valid_object(player, obj)
obj.location_id = player.location_id
obj.holder_id = None
obj.coordinates = player.coordinates
s.add(obj)
s.commit()
obj.update_neighbours()
player.do_social(obj.drop_msg, _others=[obj])
if obj.drop_sound is not None:
    obj.sound(get_sound(obj.drop_sound))