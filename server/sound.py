"""Sound-related functions."""

import logging
import os
import os.path
from hashlib import md5
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
    sum = attrib(default=Factory(lambda: None))

    def __attrs_post_init__(self):
        with open(self.path, 'rb') as f:
            self.sum = md5(f.read()).hexdigest()

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


def get_ambience(path):
    if path.startswith('/'):
        path = path[1:]
    else:
        path = os.path.join('ambiences', path)
    return get_sound(path)


nonempty_room = get_sound(
    os.path.join('notifications', 'look_objects.wav')
)
empty_room = get_sound(
    os.path.join('notifications', 'look_empty.wav')
)
