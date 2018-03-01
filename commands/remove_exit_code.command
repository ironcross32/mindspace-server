check_staff(player)
exit = Entrance.get(*a)
obj = exit.object
exit.clear_password()
s.add(exit)
player.message(f'Removed the code for {obj.get_name(True)}.')