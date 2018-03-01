id = a[0]
obj = s.query(Object).get(id)
valid_object(player, obj)
con.object_id = obj.id
player.do_social(obj.start_use_msg, _others=[obj])