Administration menu.
player = con.get_player()
if player.is_admin:
    menu(con, AdminMenu())
