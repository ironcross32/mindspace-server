"""The commands that clients should understand. Use these functions instead of
hard-coding."""

import os.path
from .sound import get_sound


def message(con, message, channel=None):
    """Get the client to display a message."""
    con.send('message', message, channel)


def url(con, title, url):
    """Request the client open a URL."""
    return con.send('url', title, url)


def character_id(con, id):
    """Tell the client what their character's ID is."""
    return con.send('character_id', id)


def location(con, obj=None):
    """Tell the client about the player's location."""
    if obj is None:
        obj = con.get_player().location
    if obj.ambience is None:
        sound = None
    else:
        sound = get_sound(
            os.path.join('ambiences', obj.ambience)
        )
        sound = sound.dump()
    if obj.music is None:
        music = None
    else:
        music = get_sound(os.path.join('music', obj.music))
        music = music.dump()
    con.send('location', obj.name, sound, obj.ambience_volume, music)
    if obj.description is not None:
        message(con, obj.description)
    convolver(con, obj.convolver, obj.convolver_volume)


def object_sound(con, id, sound):
    """An object made a sound."""
    return con.send('object_sound', id, sound.path, sound.sum)


def interface_sound(con, sound):
    """Tell the client to play an interface sound effect."""
    return con.send('interface_sound', sound.path, sound.sum)


def identify(con, obj):
    """Tell the client about an object obj."""
    if not hasattr(obj, 'ambience') or obj.ambience is None:
        sound = None
    else:
        if obj.ambience.startswith('/'):
            sound = get_sound(obj.ambience[1:])
        else:
            sound = get_sound(os.path.join('ambiences', obj.ambience))
        sound = sound.dump()
    if obj.location is None:
        max_distance = 0.0
    else:
        max_distance = obj.location.max_distance * obj.max_distance_multiplier
    return con.send(
        'identify', obj.id,
        getattr(obj, 'x', 0.0),
        getattr(obj, 'y', 0.0),
        getattr(obj, 'z', 0.0),
        sound, obj.ambience_volume, max_distance
    )


def options(con, obj):
    """Send player options to the client."""
    con.send(
        'options', obj.username, obj.transmition_id,
        obj.recording_threshold, obj.sound_volume, obj.ambience_volume,
        obj.music_volume
    )
    mute_mic(con, obj.mic_muted)


def hidden_sound(
    con, sound, coordinates, is_dry=False, volume=1.0, max_distance=100
):
    """Tell the client to play a sound at the given coordinates."""
    return con.send(
        'hidden_sound', sound.path, sound.sum, *coordinates, is_dry, volume,
        max_distance
    )


def form(con, form):
    """Tell the client to display form."""
    interface_sound(con, get_sound(os.path.join('notifications', 'form.wav')))
    return con.send('form', *form.dump())


def menu(con, menu):
    """Tell the client to display menu."""
    con.send('menu', *menu.dump())


def remember_quit(con):
    """Tell the client to remember they quit."""
    con.send('remember_quit')


def delete(con, id):
    """Tell the client to forget about the object with the given id."""
    con.send('delete', id)


def get_text(
    con, message, command, value='', multiline=False, escapable=True,
    args=None, kwargs=None
):
    """Tell the client to return a line of text to the server."""
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    con.send(
        'get_text', message, command, value, multiline, escapable, args, kwargs
    )


def copy(con, text):
    """Tell the client to copy the text to the clipboard."""
    con.send('copy', text)


def mute_mic(con, value):
    """Mute or unmute the player's microphone."""
    con.send('mute_mic', value)


def zone(con, zone=None):
    """Tell connection con about a zone."""
    if zone is None:
        zone = con.get_player().location.zone
    if zone.background_sound is None:
        sound = None
    else:
        sound = get_sound(os.path.join('zones', zone.background_sound))
        sound = (sound.path, sound.sum)
    con.send('zone', sound, zone.background_rate, zone.background_volume)


def random_sound(con, sound, x, y, z, volume=1.0, max_distance=100):
    """Send a random sound to the client."""
    con.send('random_sound', *sound.dump(), x, y, z, volume, max_distance)


def convolver(con, filename, volume):
    """Tell con about a Convolver instance."""
    if filename is None:
        c = None
    else:
        c = get_sound(os.path.join('impulses', filename)).dump()
    con.send('convolver', c, volume)
