string = a[0]
if string:
    string = '%1N ' + string
    try:
        util.emote(player, string)
    except SocialsError as e:
        player.message(str(e))
else:
    player.message('You must emote something.')