check_admin(player)

if a:
    entry = ChangelogEntry(owner_id=player.id, text=a[0].strip())
    s.add(entry)
    sound = get_sound('notifications/changelog')
    for who in Object.join(Object.player).filter(Player.changelog_notifications.is_(True), Object.connected.is_(True)):
        connection = who.get_connection()
        if connection is not None:
            message(connection, f'Game change from {player.get_name(who.is_staff)}: {entry.text}')
            interface_sound(connection, sound)
else:
    get_text(con, 'Enter the text of your change', __name__, escapable=True)