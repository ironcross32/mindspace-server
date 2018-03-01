check_builder(player)

footsteps = os.listdir('sounds/Footsteps')
here = player.location

if a:
    data = a[0]
    x1 = max(0, data['start_x'])
    x2 = min(here.size_x, data['end_x'])
    y1 = max(0, data['start_y'])
    y2 = min(here.size_y, data['end_y'])
    name = data['name']
    assert name in footsteps
    z = player.z
    done = 0
    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            RoomFloorType.query(x=x, y=y, z=z, room_id=here.id).delete()
            s.add(RoomFloorType(name=name, x=x, y=y, z=z, room_id=here.id))
            done += 1
    player.message(f'Floor coverings added: {done}.')
else:
    fields = [
        Field('start_x', 0, type=list(range(0, int(here.size_x) + 1))),
        Field('end_x', 0, type=list(range(0, int(here.size_x) + 1))),
        Field('start_y', 0, type=list(range(0, int(here.size_y) + 1))),
        Field('end_y', 0, type=list(range(0, int(here.size_y) + 1))),
        Field('name', footsteps[0], type=footsteps)
    ]
    form(con, Form('Create Bulk Floor Coverings', fields, __name__, cancel='Cancel'))