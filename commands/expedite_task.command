check_admin(player)
id = a[0]
task = Task.get(id)
task.next_run = None
s.add(task)
player.message('Done.')