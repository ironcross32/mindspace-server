"""Provides the Menu and Item classes."""

from attr import attrs, attrib, Factory
from .db import Object
from .sound import nonempty_room, empty_room
from .protocol import interface_sound, menu
from .util import pluralise


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


class LabelItem(Item):
    def __init__(self, text):
        return super().__init__(text, None)


class CopyItem(Item):
    def __init__(self, text):
        return super().__init__(text, 'copy', args=[text])


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


def objects_menu(
    player, objects=True, exits=True, command_name='interact_object',
    *command_args, **command_kwargs
):
    """Present a list of objects and / or exits close to a player. Send a
    single id with command_args and command_kwargs to command_name."""
    con = player.get_connection()
    if con is None:
        return
    args = player.same_coordinates()
    args.extend(
        [
            Object.location_id == player.location_id,
            Object.id != player.id
        ]
    )
    if not objects:
        args.append(Object.exit_id.isnot(None))
    if not exits:
        args.append(Object.exit_id.is_(None))
    q = Object.query(*args)
    c = q.count()
    if not c:
        interface_sound(con, empty_room)
        player.message('There is nothing at your current coordinates.')
    elif c == 1:
        id = q.first().id
        con.handle_command(command_name, id, *command_args, **command_kwargs)
    else:
        interface_sound(con, nonempty_room)
        items = [Item('Objects', None)]
        for obj in q:
            items.append(
                Item(
                    f'{obj.get_name(player.is_staff)} ({obj.get_type()})',
                    command_name, args=[obj.id, *command_args],
                    kwargs=command_kwargs
                )
            )
        m = Menu('Objects Menu', items, escapable=True)
        return menu(con, m)


@attrs
class Page:
    """A page of results."""

    query = attrib()
    start = attrib(default=Factory(int))
    count = attrib(default=Factory(lambda: 20))

    def __attrs_post_init__(self):
        self.results = self.query.slice(
            self.start, min(self.start + self.count, self.query.count())
        )

    def get_items(self, func, name, *args, **kwargs):
        """Convert this page of results to a list of items which can be used as
        the base for creating a Menu instance. All items are passed through
        func which should return an instance of Item, and name, args, and
        kwargs are used for next and previous entries."""
        c = self.query.count()
        items = []
        for result in self.results:
            items.append(func(result))
        actions = []
        if self.start > 0:
            end = min(self.count, self.start)
            actions.append(
                Item(
                    f'Previous {end} {pluralise(end, "entry", "entries")}',
                    name, args=args + (max(0, self.start - self.count),),
                    kwargs=kwargs
                )
            )
        next_start = self.start + self.count
        if next_start < c:
            end = min(c - next_start, self.count)
            actions.append(
                Item(
                    f'Next {end} {pluralise(end, "entry", "entries")}',
                    name, args=args + (next_start,), kwargs=kwargs
                )
            )
        if actions:
            items.append(LabelItem('Pagination'))
            items.extend(actions)
        return items
