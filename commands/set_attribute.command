type, id, name, value = a
if type == 'object':
    cls = Object
elif type == 'player':
    cls = Player
else:
    raise RuntimeError('Invalid type %r.' % type)
if not player.is_admin:
    end()
n = s.query(cls).filter_by(id=id).update(
    {getattr(cls, name): value}
)
player.message(f'{n} {util.pluralise(n, "row")} affected.')