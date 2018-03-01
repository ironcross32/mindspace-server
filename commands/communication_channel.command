action, id = a
c = CommunicationChannel.get(id)
valid_object(player, c)
name = c.get_name(player.is_builder or player.is_admin)
msg = None
if action == 'add':
    if c in player.communication_channels:
        player.message(f'You are already listening to {name}.')
    elif (c.builder and not player.is_builder) or (c.admin and not player.is_admin):
        player.message(f'You do not have sufficient permissions to listen to {name}.')
    else:
        player.communication_channels.append(c)
        msg = 'joins the channel'
elif action == 'remove':
    if c in player.communication_channels:
        player.communication_channels.remove(c)
        player.message(f'You mute {name}.')
        msg = 'leaves the channel'
    else:
        player.message(f'{name} is already muted.')
if msg is not None:
 c.transmit(player, msg, format='[{}] {} {}.', strict=False)