id, data = a
check_builder(player)
loc = Room.get(id)
valid_object(player, loc)
for name, value in data.items():
    if name in ('floor_type', 'ambience', 'music'):
        assert value in getattr(loc, f'{name}_choices')()
    setattr(loc, name, value)
s.add(loc)
s.commit()
for obj in loc.objects:
    obj.identify_location()