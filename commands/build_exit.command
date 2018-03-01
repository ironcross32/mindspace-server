check_builder(player)

def parse_args(name=None, id=None):
    return (name, id)


exit_name, id = parse_args(*a)
loc = player.location
z = loc.zone
if not exit_name:
    get_text(
        con, 'Enter the name for the new exit', 'build_exit'
    )
    end()
elif id is None:
    rooms = [Item(f'Zone: {z.get_name(True)}', None)]
    for room in reversed(z.rooms):
        if room is loc:
            continue
        rooms.append(
            Item(
                room.get_name(True), 'build_exit',
                args=[exit_name, room.id]
            )
        )
    m = Menu('Choose Destination Room', rooms, escapable=True)
    menu(con, m)
    end()
dest = s.query(Room).filter_by(id=id).first()
if dest is None:
    player.message('Invalid room.')
    end()
player.message(f'Building an exit to {dest.get_name(True)}.')
exit = Object(
    location=loc, name=exit_name,
    exit=Entrance(location=dest)
)
exit.coordinates = player.coordinates
entrance = Object(
    name=exit_name, location=dest,
    exit=Entrance(location=loc)
)
entrance.exit.coordinates = player.coordinates
s.add_all([exit, entrance])
player.message(f'Created exit {exit.get_name(True)}.')
player.message(f'Created entrance {entrance.get_name(True)}.')