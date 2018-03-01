check_builder(player)
q = RoomFloorType.query(room_id=player.location.id)
if a:
    if a[0]:
        player.message(f'Rows affected: {q.delete()}.')
    else:
        player.message('Aborted.')
else:
    c = q.count()
    if not c:
        player.message('There are no floor coverings to delete.')
    else:
        menu(
            con, Menu(
                'Delete Floor Coverings', [
                    Item(f'Delete {c} floor {util.pluralise(c, "covering")}?', None),
                    Item('Yes', __name__, args=[True]),
                    Item('No', __name__, args=[False])
                ], escapable=True
            )
        )