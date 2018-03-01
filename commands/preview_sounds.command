check_staff(player)

if a:
    path = a[0]
else:
    path = 'sounds'

if os.path.isfile(path):
    copy(con, path)
    sound = get_sound(path)
    path = os.path.split(path)[0]
    interface_sound(con, sound)
items = [Item(path, None)]
updir = os.path.split(path)[0]
if updir:
    items.append(Item('..', __name__, args=[updir]))
for name in sorted(os.listdir(path)):
    full = os.path.join(path, name)
    items.append(Item(name, __name__, args=[full]))
menu(con, Menu('Preview Sounds', items, escapable=True))