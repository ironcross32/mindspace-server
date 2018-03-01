check_staff(player)
exit = Entrance.get(*a)
valid_object(player, exit)
obj = exit.object
password = random_password()
exit.set_password(password)
s.add(exit)
copy(con, password)
player.message(f'Set the password for {obj.get_name(True)}.')