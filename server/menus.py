"""Provides the Menu and Item classes."""

from attr import attrs, attrib, Factory
from .db import Object
from .sound import nonempty_room, empty_room
from .protocol import interface_sound, menu


@attrs
class Item:
    """A menu item."""

    title = attrib()
    command = attrib()
    args = attrib(default=Factory(list))
    kwargs = attrib(default=Factory(dict))

    def dump(self):
        """Return this instance as a list."""
        return [self.title, self.command, self.args, self.kwargs]


@attrs
class Menu:
    """A menu."""

    title = attrib()
    items = attrib()
    escapable = attrib(default=Factory(bool))

    def dump(self):
        """Prepare this object for sending."""
        return [
            self.title, [item.dump() for item in self.items], self.escapable
        ]


def objects_menu(player, objects=True, exits=True):
    """Present a list of objects and / or exits close to a player."""
    con = player.get_connection()
    if con is None:
        return
    args = [
        getattr(
            Object, name
        ) == getattr(
            player, name
        ) for name in ('x', 'y', 'z', 'location_id')
    ]
    args.append(Object.id != player.id)
    if not objects:
        args.append(Object.exit_id.isnot(None))
    if not exits:
        args.append(Object.exit_id.is_(None))
    q = Object.query(*args)
    c = q.count()
    if not c:
        interface_sound(con, empty_room)
        return player.message(
            'There is nothing at your current coordinates.'
        )
    if c == 1:
        id = q.first().id
    else:
        interface_sound(con, nonempty_room)
        items = [Item('Objects', None)]
        for obj in q:
            items.append(
                Item(
                    f'{obj.get_name(player.is_staff)} ({obj.get_type()})',
                    'interact_object', args=[obj.id]
                )
            )
        m = Menu('Objects Menu', items, escapable=True)
        return menu(con, m)
    # Only one id left.
    return con.handle_command('interact_object', id)