check_admin(player)

def parse_args(t, data={}):
    return (t, data)

type, data = parse_args(*a)
cls = Base._decl_class_registry[type]
thing = cls()
for name in ('builder', 'admin', 'reusable', 'disabled'):
    if hasattr(thing, name) and getattr(thing, name) is None:
        setattr(thing, name, False)
if data:
    try:
        for name, value in data.items():
            setattr(thing, name, value)
        s.add(thing)
        s.commit()
        player.message(f'Created {type} {thing.name}.')
        end()
    except Exception as e:
        if isinstance(e, OK):
            raise e
        logger.warning('Failed to ass %r with data: %s.', cls, data)
        logger.exception(e)
        player.message(str(e))
form(con, ObjectForm(thing, __name__, title=f'New {cls.__name__}', args=[type], cancel='Cancel'))