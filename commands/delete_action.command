check_admin(player)

def parse_args(object_id, id=None, response=None):
    return (object_id, id, response)

object_id, id, response = parse_args(*a)
obj = Object.get(object_id)
valid_object(player, obj)
if id is None:
    items = [Item('Select Action', None)]
    for thing in ObjectAction.query(object_id=object_id):
        items.append(Item(Action.query(id=thing.action_id).first().get_name(True), __name__, args=[object_id, thing.id]))
    menu(con, Menu('Delete Action', items, escapable=True))
    end()
oa = ObjectAction.get(id)
valid_object(player, oa)
action = Action.get(oa.action_id)
if response is None:
    menu(
        con, Menu(
            f'Are you sure you want to delete {action.get_name(True)} from {obj.get_name(True)}?',
            [
                Item('Yes', __name__, args=[object_id, id, True]),
                Item('No', __name__, args=[id, False])
            ], escapable=True
        )
    )
elif not response:
    player.message('Not deleting.')
else:
    s.delete(oa)
    player.message('Done.')