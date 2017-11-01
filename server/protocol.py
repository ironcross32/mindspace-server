"""The commands that clients should understand. Use these functions instead of
hard-coding."""

import os.path
from .sound import get_sound

reverb_property_names = (
    'cutoff_frequency', 'delay_modulation_depth', 'delay_modulation_frequency',
    'density', 't60', 'mul'
)


def message(con, message, channel=None):
    """Get the client to display a message."""
    con.send('message', message, channel)


def url(con, title, url):
    """Request the client open a URL."""
    return con.send('url', title, url)


def character_id(con, id):
    """Tell the client what their character's ID is."""
    return con.send('character_id', id)


def location(con, obj):
    """Tell the client about the player's location."""
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
    d = {
        name: getattr(
            obj, name
        ) for name in reverb_property_names
    }
    con.send(
        'location', obj.name, sound, obj.ambience_volume, music,
        obj.max_distance, d
    )
    if obj.description is not None:
        message(con, obj.description)


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
    return con.send(
        'identify', obj.id,
        getattr(obj, 'x', 0.0),
        getattr(obj, 'y', 0.0),
        getattr(obj, 'z', 0.0),
        sound, obj.ambience_volume
    )


def options(con, obj):
    """Send player options to the client."""
    con.send(
        'options', obj.username, obj.transmition_id,
        obj.recording_threshold, obj.sound_volume, obj.ambience_volume,
        obj.music_volume
    )
    mute_mic(con, obj.mic_muted)


def hidden_sound(con, sound, coordinates, is_dry):
    """Tell the client to play a sound at the given coordinates."""
    return con.send(
        'hidden_sound', sound.path, sound.sum, *coordinates, is_dry
    )


def form(con, form):
    """Tell the client to display form."""
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


def zone(con, zone):
    """Tell connection con about a zone."""
    if zone.background_sound is None:
        sound = None
    else:
        sound = get_sound(os.path.join('zones', zone.background_sound))
        sound = (sound.path, sound.sum)
    con.send('zone', sound, zone.background_rate, zone.background_volume)


def random_sound(con, sound, x, y, z, volume):
    """Send a random sound to the client."""
    con.send('random_sound', *sound.dump(), x, y, z, volume)