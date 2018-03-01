check_in_space(player)
z = player.location.zone
key, modifiers = a
if key == 'K':
    if 'shift' in modifiers:
        name = 'up'
    elif 'ctrl' in modifiers:
        name = 'down'
    else:
        player.message('You must add shift for up, or control for down.')
        end()
elif key == 'R':
    pass  # Handled below.
else:
    name = Direction.key_to_name(key)
    if 'shift' in modifiers:
        name += ' and up'
    elif 'ctrl' in modifiers:
        name += ' and down'
if key == 'R':
    direction = choice(Direction.query().all())
else:
    direction = Direction.query(name=name).first()
if direction is z.direction:
    player.message('Heading unchanged.')
    end()
now = time()
diff = now - z.last_turn
if z.speed is None or diff > z.speed:
    z.last_turn = now
    z.direction = direction
    player.beep()
    player.message(f'New heading: {direction.get_name(player.is_staff)}.')
else:
    player.message('You must wait %.2f seconds before turning again.' % diff)