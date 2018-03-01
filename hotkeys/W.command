directions = Direction.query(z=0.0)
items = [LabelItem('Directions')]
x1, y1, z1 = player.coordinates
xs, ys, zs = player.location.size
for direction in directions:
    if (
        (
            direction.x > 0 and x1 >= xs
        ) or (
            direction.x < 0 and not x1
        )
    ) or (
        (
            direction.y > 0 and y1 >= xs
        ) or (
            direction.y < 0 and not y1
        )
    ):
        continue
    x2, y2, z2 = player.get_corner_coordinates(direction)
    if [x2, y2, z2] != [x1, y1, z1]:
        items.append(Item(direction.get_name(player.is_staff), 'autostroll', args=[dict(x=x2, y=y2)]))
if len(items) > 1:
    menu(con, Menu('Autostroll', items, escapable=True))
else:
    player.message('There is nowhere to go.')