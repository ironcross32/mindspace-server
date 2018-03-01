check_admin(player)

def parse_args(text=None, id=None):
    return (text, id)

text, id = parse_args(*a)
if text is None:
    get_text(con, 'Enter part of the object\'s name', __name__)
elif id is None:
    q = Object.query(Object.name.like(f'%{text}%'))
    items = [Item(f'Results: {q.count()}', None)]
    for obj in q:
        items.append(Item(f'{obj.get_name(True)} ({obj.coordinates}) at {obj.location.get_name(True)}', __name__, args=[text, obj.id]))
    menu(con, Menu('Objects', items, escapable=True))
else:
    obj = Object.query(id=id).first()
    if obj is None:
        player.message('Invalid Object.')
    else:
        items = [
            Item('Object Actions', None),
            Item('Bring Object', 'bring_object', args=[obj.id]),
            Item('Join Object', 'join_object', args=[obj.id]),
            Item('Edit Object', 'edit_', args=['Object', obj.id])
        ]
        menu(con, Menu('Object', items, escapable=True))