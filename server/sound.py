"""Sound-related functions."""

import logging
import os
import os.path
from time import time
from random import choice
from attr import attrs, attrib, Factory

logger = logging.getLogger(__name__)

sounds_dir = 'sounds'

sounds = {}


class NoSuchSound(Exception):
    """The path provided is not a sound file or folder containing sound
    files."""


@attrs
class Sound:
    """A sound object."""

    path = attrib()
    sum = attrib(default=Factory(time))

    def dump(self):
        if os.path.sep != '/':
            self.path = self.path.replace(os.path.sep, '/')
        return [self.path, self.sum]


def get_sound(path):
    """Gets a Sound instance. The path argument can either be a file path, or a
    directory path. In both instances, a path relative to the sounds directory
    is expected. If a directory path is provided then a random file from that
    directory is chosen."""
    if not path.startswith('%s%s' % (sounds_dir, os.path.sep)):
        path = os.path.join(sounds_dir, path)
    if os.path.isdir(path):
        return get_sound(os.path.join(path, choice(os.listdir(path))))
    elif os.path.isfile(path):
        if path not in sounds:
            sounds[path] = Sound(path)
            logger.info('Registering %r.', sounds[path])
        return sounds[path]
    else:
        raise NoSuchSound(path)


nonempty_room = get_sound(
    os.path.join('notifications', 'look_objects.wav')
)
empty_room = get_sound(
    os.path.join('notifications', 'look_empty.wav')
)

connect_sound = get_sound(os.path.join('notifications', 'connect.wav'))

disconnect_sound = get_sound(os.path.join('notifications', 'disconnect.wav'))

motd_sound = get_sound(os.path.join('notifications', 'motd.wav'))
