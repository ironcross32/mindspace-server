"""Contains the Form, Label, and Field classes."""

from attr import attrs, attrib, Factory


class text(type):
    """For multiline text fields."""
    pass


@attrs
class Label:
    """A label in a menu."""

    text = attrib()

    def dump(self):
        """Prepare for transmition."""
        return {'type': self.__class__.__name__, 'values': [self.text]}


@attrs
class Field:
    """A form field."""

    name = attrib()
    value = attrib()
    type = attrib(default=Factory(lambda: str))
    title = attrib(default=Factory(lambda: None))
    hidden = attrib(default=Factory(bool))

    def __attrs_post_init__(self):
        if self.title is None:
            self.title = self.name.replace(
                '_', ' '
            ).title()

    def dump(self):
        """Return this object as a dict."""
        return {
            'type': self.__class__.__name__,
            'values': [
                self.name, self.value, getattr(
                    self.type, '__name__', self.type
                ), self.title,
                self.hidden
            ]
        }


@attrs
class Form:
    """A form to send to a connection."""

    title = attrib()
    fields = attrib()
    command = attrib()
    args = attrib(default=Factory(list))
    kwargs = attrib(default=Factory(dict))
    ok = attrib(default=Factory(lambda: 'OK'))
    cancel = attrib(default=Factory(lambda: None))

    def dump(self):
        """Prepare this form for sending."""
        fields = []
        for field in self.fields:
            fields.append(field.dump())
        return (
            self.title, fields, self.command, self.args, self.kwargs, self.ok,
            self.cancel
        )


class ObjectForm(Form):
    """Make a form out of an object."""

    def __init__(self, obj, command, title=None, **kwargs):
        """Create with an object and an optional list of classes to ignore when
        searching bases."""
        fields = obj.get_all_fields()
        if title is None:
            if hasattr(obj, 'name'):
                name = obj.get_name()
            else:
                name = obj.__class__.__name__
            title = f'Configure {name}'
        super().__init__(title, fields, command, **kwargs)
