check_admin(player)

def parse_args(t, id=None):
    return (t, id)

type, id = parse_args(*a)
cls = Base._decl_class_registry[type]
if id is None:
    items = []
    for thing in s.query(cls).order_by(cls.name):
        items.append(Item(thing.get_name(True), __name__, args=[type, thing.id]))
    m = Menu(f'Select {cls.__name__}', items, escapable=True)
    menu(con, m)
    end()
obj = s.query(cls).get(id)
if obj is None:
    player.message('Invalid object.')
    end()
fields = [Label(f'Revisions for {obj.get_name(True)}: {len(obj.revisions)}')]
for revision in reversed(obj.revisions):
    fields.append(Field(str(revision.created), revision.code, type='text'))
form(con, Form('Revisions', fields, 'done', cancel='Cancel'))