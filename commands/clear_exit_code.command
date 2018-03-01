check_staff(player)
exit = Entrance.get(*a)
obj = exit.object
exit.set_password('')
s.add(exit)
player.message(f'Cleared the code for {obj.get_name(True)}.')