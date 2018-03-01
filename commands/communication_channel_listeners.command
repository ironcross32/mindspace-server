id = a[0]
channel = CommunicationChannel.get(id)
if channel not in player.communication_channels:
    player.message('No such channel.')
    end()
items = [LabelItem(f'People listening to {channel.get_name(player.is_staff)}')]
for listener in channel.listeners:
    items.append(CopyItem(f'{"* " if listener.connected else ""}{listener.get_name(player.is_staff)}'))
menu(con, Menu('Channel Listeners', items, escapable=True))
