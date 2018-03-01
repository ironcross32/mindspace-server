if player.following is None:
    player.message('You are not currently following anyone.')
else:
    player.do_social(player.unfollow_msg, _others=[player.following])
    player.following = None