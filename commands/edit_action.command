check_admin(player)

def parse_args(id, data=None):
    return (id, data)

id, data = parse_args(*a)
action = s.query(Action).get(id)
valid_object(player, action)
if data is None:
    form(con, ObjectForm(action, __name__, args=[action.id], title=f'Edit {action.get_name(True)}', cancel='Cancel'))
else:
    for name, value in data.items():
        if name == 'error':
            continue
        else:
            setattr(action, name, value)
    try:
        action.set_code(action.code)
        s.add(action)
        s.commit()
        message(con, 'Done.')
    except Exception as e:
        f = ObjectForm(action, __name__, args=[action.id], title=f'Edit {action.get_name(True)}', cancel='Cancel')
        f.fields.insert(0, Label('Error:'))
        f.fields.insert(1, Field('error', str(e)))
        form(con, f)