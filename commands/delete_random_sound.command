check_builder(player)
type, id = a
obj = s.query(Base._decl_class_registry[type]).get(id)
if obj is None or not hasattr(obj, 'random_sounds'):
    player.message('Invalid object.')
    end()
items = [Item('Select Sound', None)]
for sound in obj.random_sounds:
    items.append(Item(sound.get_name(True), 'delete_', args=[sound.__class__.__name__, sound.id]))
menu(con, Menu('Delete Random Sound', items, escapable=True))