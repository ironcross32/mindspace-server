names = ('Command', 'Hotkey', 'Action', 'Task', 'StarshipEngine', 'ObjectType', 'Gender')
items = [Item('Search', None)]
for name in names:
    items.append(Item(f'Search {name}s', 'search_', args=[name, 'menu_']))
items.extend(
    [
        Item('Find Object', 'find_object'),
        Item(util.english_list([x + 's' for x in names]), None)
    ]
)
for name in names:
    items.append(Item(name + 's', None))
    for action in ('add', 'edit', 'delete'):
        items.append(Item(f'{action.title()} {name}', f'{action}_', args=[name]))
    if name != 'ObjectType':
        items.append(Item(f'{name} Revisions', 'show_revisions', args=[name]))
items.extend(
    [
        Item('Rules', None),
        Item('Add Rule', 'add_', args=['Rule']),
        Item('Edit Rule', 'edit_', args=['Rule']),
        Item('Delete Rule', 'delete_', args=['Rule']),
        Item('Python Console', 'key', args=['BACKSPACE']),
        Item('Administrative Actions', None),
        Item('Bring Player', 'bring_object'),
        Item('Join Player', 'join_object'),
        Item('Make an Announcement', 'announce'),
        Item('Manage Connections', 'manage_connections'),
        Item('Shutdown', 'shutdown'),
        Item('Programming', None)
    ]
)
for name in ('Action', 'Hotkey'):
    for action in ('bind', 'unbind'):
        items.append(Item(f'{action.title()} {name}', action, args=[name]))
menu(con, Menu('Administration', items, escapable=True))