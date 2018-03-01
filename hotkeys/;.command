items = [LabelItem(f'Communication Channels ({len(player.communication_channels)})')]
for channel in player.communication_channels:
    items.append(Item(channel.get_name(player.is_staff), 'communication_channel_listeners', args=[channel.id]))
menu(con, Menu('Communication Channel Listeners', items, escapable=True))