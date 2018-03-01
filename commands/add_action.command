check_admin(player)

def parse_args(id, action_id=None):
    return (id, action_id)

id, action_id = parse_args(*a)
obj = Object.get(id)
if obj is None:
    player.message('Invalid object.')
    end()
if action_id is None:
    items = [Item('Select Hotkey', None)]
    for a in Action.query().order_by(Action.name):
        items.append(Item(f'{a.get_name(True)}: {a.description}', __name__, args=[id, a.id]))
    menu(con, Menu('Add Action', items, escapable=True))
else:
    a = Action.get(action_id)
    if a is None:
        player.message('Invalid action.')
        end()
    oa = ObjectAction(object_id=obj.id, action_id=a.id)
    s.add(oa)
    s.commit()
    player.message(f'Added {a.get_name(True)} to {obj.get_name(True)}.')