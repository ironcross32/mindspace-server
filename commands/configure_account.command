if a:
    data = a[0]
    account = player.player
    account.email = data.get('email', account.email) or None
    name = data.get('name', '')
    if name and name != player.name:
        if player.last_name_change is not None:
            elapsed = util.now() - player.last_name_change
            i = server_options().name_change_interval
            if elapsed < i:
                player.message(f'You cannot change your name for another {util.format_timedelta(i - elapsed)}.')
                end()
        old = player.name
        player.set_name(name)
        s.add(player)
        if old is not None:
            for connection in server.connections:
                message(connection, f'{old} is now known as {name}.')
        else:
            player.message(f'You are now known as {name}.')
    password = data.get('password', '')
    confirm = data.get('password_confirm', '')
    if password:
        if password == confirm:
            account.set_password(password)
            s.add(account)
            player.message('Password updated.')
        else:
            player.message('Passwords do not match.')
    s.commit()
    end()
name = player.get_name() or ''
items = [
    Field('name', name, title='The name of your player'),
    Field('email', player.player.email, title='Email Address'),
    Field('password', '', title='Account Password'),
    Field('password_confirm', '', title='Password (Confirm)')
]
f = Form(
    'Account information. Leave fields blank or unchanged to avoid '
    'changing them.', items, __name__, cancel='Cancel'
)
form(con, f)