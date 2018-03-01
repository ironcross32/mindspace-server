check_builder(player)
def parse_args(id, name=None):
    return (id, name)

id, name = parse_args(*a)

obj = Object.get(id)
valid_object(player, obj)
if obj.transit_route is not None:
    player.message(f'This object is already linked to transit route {obj.transit.get_name(True)}.')
elif not name:
    get_text(con, 'Enter the name for the new transport route', __name__, value=obj.name, args=[id])
else:
    t = TransitRoute(name=name)
    obj.transit_route = t
    s.add_all([obj, t])
    s.commit()
    player.message(f'Created transit route {t.get_name(True)}.')