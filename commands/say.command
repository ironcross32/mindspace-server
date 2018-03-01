text = ''.join(a)
if not text:
    player.message('Cancel.')
elif not player.name:
    player.message('You cannot speak until you have set your name.')
else:
    player.sound(get_sound(os.path.join('players', 'say.wav')))
    player.do_social('%1N say%1s: "{text}"', text=text, _channel='say')