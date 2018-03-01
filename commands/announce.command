check_admin(player)
if a:
    text = a[0]
    if not text.strip():
        message(con, 'You must enter some text.')
    else:
        for connection in server.connections:
            message(
                connection,
                f'Announcement from {player.get_name()}: {text}',
                channel='Announcements'
            )
            interface_sound(
                con, get_sound(
                    os.path.join('notifications', 'announcement.wav')
                )
            )
else:
    get_text(con, 'Enter the text of your announcement:', 'announce')