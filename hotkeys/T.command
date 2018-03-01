check_admin(player)
tasks = Task.query().all()
items = [LabelItem(f'Tasks ({len(tasks)})')]
now = time()
for t in tasks:
    name = t.get_name(True)
    description = t.get_description()
    if t.next_run is None:
        next_run = 'Not scheduled'
    elif now > t.next_run:
        next_run = 'Recently Run'
    else:
        next_run = t.next_run - now
        next_run = datetime.timedelta(seconds=next_run)
        next_run = util.format_timedelta(next_run)
    paused = 'Paused' if t.paused else 'Running'
    items.append(Item(f'{name} [{paused}] ({next_run}): {description}', 'expedite_task', args=[t.id]))
menu(con, Menu('Server Tasks', items, escapable=True))