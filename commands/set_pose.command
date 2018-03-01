if a:
    player.pose = a[0]
    player.message(f'Other people will now see {player.get_name()} {player.pose}.')
else:
    if player.pose is None:
        get_text(con, 'Enter your new pose', __name__)
    else:
        player.pose = None
        player.message('Pose cleared.')