check_builder(player)
obj = s.query(Object).get(a[0])
if obj is None or obj.is_player or obj.is_exit:
    player.message('Invalid object.')
else:
    obj.mobile = Mobile()
    s.add(obj)
    player.message(f'{obj.get_name(True)} is now a mobile.')