def parse_args(type, id=None, data=None):
    return (type, id, data)

type, id, data = parse_args(*a)
cls = Base._decl_class_registry[type]
if cls not in (Social,):
    check_builder(player)
if id is None:
    items = [Item(f'Edit {cls.__name__}', None)]
    for thing in cls.query().order_by(cls.name):
        if hasattr(thing, 'get_description'):
            description = f': {thing.get_description()}'
        else:
            description = ''
        items.append(Item(f'{thing.get_name(True)}{description}', __name__, args=[type, thing.id]))
    m = Menu(f'Choose {cls.__name__.lower()}', items, escapable=True)
    menu(con, m)
    end()
obj = cls.get(id)
valid_object(player, obj)
if not hasattr(obj, 'owner') or obj.owner is not player:
    check_admin(player)
try:
    if data:
        for name, value in data.items():
            if '.' in name:
                where, name = name.split('.')
                where = getattr(obj, where)
            else:
                where = obj
            setattr(where, name, value)
        s.add(obj)
        s.commit()
        if isinstance(obj, Object) and obj.location is not None:
            obj.update_neighbours()
        elif isinstance(obj, Zone):
            obj.update_occupants()
        player.message('Edits saved.')
        end()
except Exception as e:
    if isinstance(e, OK):
        raise e
    player.message(repr(e))
    logger.warning(
        '%s caused an error while editing %s:',
        player.get_name(True), obj.get_name(True) if hasattr(obj, 'get_name') else repr(obj))
    logger.exception(e)
form(con, ObjectForm(obj, __name__, args=[type, obj.id], cancel='Cancel'))