check_admin(player)
type, id = a
cls = Base._decl_class_registry[type]
obj = cls.get(id)
valid_object(player, obj)
m = Menu(
    obj.get_name(True), [
        Item('Select Option', None),
        Item('Edit', 'edit_', args=[type, obj.id]),
        Item('Delete', 'delete_', args=[type, obj.id])
    ], escapable=True
)
menu(con, m)