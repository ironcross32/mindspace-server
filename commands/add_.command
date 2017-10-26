player = con.get_player()
if not player.is_admin:
    end()
if len(a) == 1:
    a = (*a, {})
type, data = a
if type == 'hotkey':
    cls = Hotkey
elif type == 'command':
    cls = Command
else:
    raise RuntimeError('Invalid type %r.' % type)
thing = cls(**data)
if data and all(data.values()):
    try:
        thing.set_code(thing.code)
        s.add(thing)
        player.message(f'Created {type} {thing.name}.')
        end()
    except OK:
        end()
    except Exception as e:
        logger.exception(e)
        player.message(str(e))
if data:
    player.message('All fields are required.')
form(con, ObjectForm(thing, __name__, title=f'New {cls.__name__}', args=[type], cancel='Cancel'))
