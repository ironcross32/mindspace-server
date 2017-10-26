Allow administrators to enter Python.
player = con.get_player(s)
if player.is_admin:
    get_text(con, 'Enter some code', 'python')
