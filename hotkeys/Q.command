items = [Item('Statistics:', None)]
for stat in server_info():
    items.append(Item(stat, 'copy', args=[stat]))
m = Menu('Server Statistics', items, escapable=True)
menu(con, m)