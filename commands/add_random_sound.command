check_builder(player)
random_dir = os.path.join('sounds', 'random')

def parse_args(type, id, sound=None):
    return (type, id, sound)

type, id, sound = parse_args(*a)
obj = s.query(Base._decl_class_registry[type]).get(id)
if obj is None or not hasattr(obj, 'add_random_sound'):
    player.message('Invalid object.')
    end()
if sound is None:
    items = [Item('Select Sound', None)]
    for name in sorted(os.listdir(random_dir)):
        items.append(Item(name, __name__, args=[type, id, name]))
    menu(con, Menu('Add Random Sound', items, escapable=True))
    end()
interface_sound(con, get_sound(os.path.join(random_dir, sound)))
s.add(obj.add_random_sound(sound))
player.message('Done.')