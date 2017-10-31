"""Utility functions."""

from time import time
from datetime import datetime
from emote_utils import NoMatchError
from attr import attrs, attrib
from twisted.internet.task import LoopingCall
from .distance import pc, kpc, mpc, au, ly, light_speed
from .sound import get_sound, empty_room, nonempty_room
from . import db
from .protocol import interface_sound
from .socials import factory


def now():
    """Returns datetime.utcnow()."""
    return datetime.utcnow()


def directions(c1, c2):
    """Return the textual directions between c1 and c2."""
    results = []
    x1, y1, z1 = c1
    x2, y2, z2 = c2
    if x1 != x2:
        diff = max(x1, x2) - min(x1, x2)
        if x2 > x1:
            direction = 'east'
        elif x2 < x1:
            direction = 'west'
        results.append('%d %s' % (diff, direction))
    if y1 != y2:
        diff = max(y1, y2) - min(y1, y2)
        if y2 > y1:
            direction = 'north'
        else:
            direction = 'south'
        results.append('%d %s' % (diff, direction))
    if z1 != z2:
        diff = max(z1, z2) - min(z1, z2)
        if z2 > z1:
            direction = 'up'
        else:
            direction = 'down'
        results.append('%d %s' % (diff, direction))
    if results:
        return ', '.join(results)
    else:
        return 'here'


def format_timedelta(td):
    """Format timedelta td."""
    fmt = []  # The format as a list.
    seconds = td.total_seconds()
    years, seconds = divmod(seconds, 31536000)
    if years:
        fmt.append('%d %s' % (years, 'year' if years == 1 else 'years'))
    months, seconds = divmod(seconds, 2592000)
    if months:
        fmt.append('%d %s' % (months, 'month' if months == 1 else 'months'))
    days, seconds = divmod(seconds, 86400)
    if days:
        fmt.append('%d %s' % (days, 'day' if days == 1 else 'days'))
    hours, seconds = divmod(seconds, 3600)
    if hours:
        fmt.append('%d %s' % (hours, 'hour' if hours == 1 else 'hours'))
    minutes, seconds = divmod(seconds, 60)
    if minutes:
        fmt.append(
            '%d %s' % (
                minutes,
                'minute' if minutes == 1 else 'minutes'
            )
        )
    if seconds:
        fmt.append('%.2f seconds' % seconds)
    return english_list(fmt)


def pluralise(n, singular, plural=None):
    """Return singular if n == 1 else plural."""
    if plural is None:
        plural = singular + 's'
    return singular if n == 1 else plural


def english_list(
    l,
    empty='nothing',
    key=str,
    sep=', ',
    and_='and '
):
    """Return a decently-formatted list."""
    results = [key(x) for x in l]
    if not results:
        return empty
    elif len(results) == 1:
        return results[0]
    else:
        res = ''
        for pos, item in enumerate(results):
            if pos == len(results) - 1:
                res += '%s%s' % (sep, and_)
            elif res:
                res += sep
            res += item
        return res


def show_objects(player, f=None):
    """Shows what's in the room. Only objects for whom f(obj) evaluates to
    True."""
    con = player.get_connection()
    if f is None:

        def f(obj):
            return True

    shown = 0
    for obj in player.get_visible():
        if obj is not player and f(obj):
            shown += 1
            name = obj.get_full_name(player.is_admin)
            dirs = directions(player.coordinates, obj.coordinates)
            player.message(f'{name}: {dirs}.')
    if shown:
        sound = nonempty_room
    else:
        sound = empty_room
        player.message('Nothing found.')
    interface_sound(con, sound)


def walk(player, x=0, y=0, z=0, observe_speed=True, sound=None):
    """Walk player by the amount specified. If observe does not evaluate to
    True then the maximum speed of the player is ignored (used by WalkTask). If
    sound is None then the default walk sound for the current room will be
    used."""
    s = db.Session
    if sound is None:
        sound = player.location.get_walk_sound()
    players = [player]
    players.extend(player.followers)
    now = time()
    if not observe_speed or now - player.last_walked >= player.speed:
        px, py, pz = player.coordinates
        px += x
        py += y
        pz += z
        if player.location.coordinates_ok((px, py, pz)):
            if player.following is not None:
                who = player.following.get_name(player.is_staff)
                player.message(f'You stop following {who}.')
                player.following_id = None
            player.last_walked = now
            for obj in players:
                obj.steps += 1
                obj.recent_exit_id = None
                obj.coordinates = (px, py, pz)
                obj.update_neighbours()
                if obj is player:
                    wsound = sound
                else:
                    wsound = obj.location.get_walk_sound()
                if wsound is not None:
                    obj.sound(wsound)
            s.add_all(players)
            return True
        else:
            player.message('You cannot go that way.')
            player.sound(get_sound('cantgo'), private=True)
            return False


@attrs
class WalkTask(LoopingCall):
    """A task to automatically walk."""

    id = attrib()
    x = attrib()
    y = attrib()
    z = attrib()

    def __attrs_post_init__(self):
        super().__init__(self.walk)

    def start(self):
        super().start(0.0)

    def walk(self):
        """Make the player walk."""
        with db.session() as s:
            obj = s.query(db.Object).get(self.id)
            if obj is None:
                return self.stop()
            kwargs = dict(observe_speed=False)
            self.interval = obj.speed
            for name in ('x', 'y', 'z'):
                coord = getattr(self, name)
                current = getattr(obj, name)
                if coord > current:
                    value = 1
                elif coord == current:
                    value = 0
                else:
                    value = -1
                kwargs[name] = value
            if any(kwargs.values()):
                res = walk(obj, **kwargs)
            else:
                res = False
            if res is False:
                obj.message('You stop walking.')
                self.stop()
                con = obj.get_connection()
                if con is not None:
                    con.walk_task = None


def emote(player, string):
    """Perform an emote as player."""
    try:
        string, others = factory.convert_emote_string(
            string, player.match, [player]
        )
        player.do_social(string, _others=others[1:], _channel='emote')
    except NoMatchError as e:
        player.message('Nothing found matching %s.' % e.args)


def percent(n, full):
    """Return the n as a percentage of full."""
    return (100.0 / full) * n


def direction_between(origin, target, vehicle=True):
    """Get a Direction instance representing the distance between origin and
    target."""
    def get_difference(a, b):
        """Get the difference between a and b."""
        if a == b:
            return 0.0
        elif b > a:
            return 1.0
        else:
            return -1.0

    ox, oy, oz = origin
    tx, ty, tz = target
    x, y, z = (
        get_difference(ox, tx),
        get_difference(oy, ty),
        get_difference(oz, tz)
    )
    return db.Direction.query(x=x, y=y, z=z, vehicle=vehicle).first()


def format_distance(
    units,
    show_mpcs=True,
    show_kpcs=True,
    show_pcs=True,
    show_lys=True,
    show_aus=True
):
    """Convert distance measured in units to a human-readable string."""
    base = 1000000  # Multiplying just seemed to fix things...
    units = units * base
    fmt = []
    if show_mpcs:
        mpcs, units = divmod(units, mpc * base)
        mpcs = round(mpcs, 2)
        if mpcs == int(mpcs):
            mpcs = int(mpcs)
        if mpcs:
            fmt.append('%r mpc' % round(mpcs, 2))
    if show_kpcs:
        kpcs, units = divmod(units, kpc * base)
        kpcs = round(kpcs, 2)
        if kpcs == int(kpcs):
            kpcs = int(kpcs)
        if kpcs:
            fmt.append('%r kpc' % kpcs)
    if show_pcs:
        pcs, units = divmod(units, pc * base)
        pcs = round(pcs, 2)
        if pcs == int(pcs):
            pcs = int(pcs)
        if pcs:
            fmt.append('%r pc' % pcs)
    if show_lys:
        lys, units = divmod(units, ly * base)
        lys = round(lys, 2)
        if lys == int(lys):
            lys = int(lys)
        if lys:
            fmt.append('%r ly' % lys)
    if show_aus:
        aus, units = divmod(units, au * base)
        aus = round(aus, 2)
        if aus == int(aus):
            aus = int(aus)
        if aus:
            fmt.append('%r au' % aus)
    if units:
        units /= 10
        if units == int(units):
            units = int(units)
        else:
            units = round(units, 2)
        fmt.append('%r km' % units)
    return english_list(fmt)


def percentage_lightspeed(d):
    """Given a distance d as a speed in units / sec, return the percentage
    light speed."""
    return percent(d, light_speed)


def format_speed(s, include_percentage=True):
    """Format a speed measured in units per second. If include_percentage
    evaluates to True include the percentage of light speed."""
    res = '%s / sec' % format_distance(s)
    if include_percentage:
        res += ' (%.2f%% light)' % percentage_lightspeed(s)
    return res


def distance_between(c1, c2):
    """Return the distance between c1 and c2."""
    x1, y1, z1 = c1
    x2, y2, z2 = c2
    return max(
        max(x1, x2) - min(x1, x2),
        max(y1, y2) - min(y1, y2),
        max(z1, z2) - min(z1, z2),
    )
