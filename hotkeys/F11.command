player.monitor_transmitions = not player.monitor_transmitions
if player.monitor_transmitions:
    action = 'now'
else:
    action = 'no longer'
player.message('You will %s hear your own transmitions.' % action)