items = [
    LabelItem('Game Options'),
    Item('Disconnect', 'quit'),
    CopyItem('No connection metrics available' if player.player.connected_time is None else f'Total time connected: {util.format_timedelta(player.player.connected_time)}'),
    Item(f'{"set" if player.pose is None else "Clear"} pose', 'set_pose'),
    Item('Mail', 'mail'),
    Item('Rules', 'rules'),
    Item('Ideas', 'ideas'),
    Item('Changelog', 'changelog'),
    Item('Donate', 'show_url', args=['Visit Donator Page', 'https://www.patreon.com/chris_norman']),
    LabelItem('Options'),
    Item('Set Player Options', 'configure_account')
]
for x in dir(player.player):
    if x.endswith('_notifications'):
        state = getattr(player.player, x)
        items.append(Item(f'{"disable" if state else "enable"} {x.replace("_", " ").title()}', 'set_player_option', args=[x, -1 if state else 1]))
m = Menu('Game', items, escapable=True)
menu(con, m)