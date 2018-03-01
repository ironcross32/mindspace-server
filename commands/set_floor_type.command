convertions = {
    None: 'Clear',
    False: 'Silent'
}
if a:
    name = a[0]
    if name is None:
        RoomFloorType.query(room_id=player.location_id, x=player.x, y=player.y, z=player.z).delete()
    else:
        floor = RoomFloorType.query(room_id=player.location_id, x=player.x, y=player.y, z=player.z).first()
        if floor is None:
            floor = RoomFloorType(x=player.x, y=player.y, z=player.z, room_id=player.location_id)
        if name is False:
            name = None
        floor.name = name
        s.add(floor)
    player.message('Done.')
else:
    items = [LabelItem('Select Floor Covering')]
    for name in [None, False] + sorted(os.listdir(os.path.join('sounds', 'Footsteps'))):
        items.append(Item(convertions.get(name, name), __name__, args=[name]))
    menu(con, Menu('Floor Covering', items, escapable=True))