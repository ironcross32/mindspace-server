"""Utility functions."""

from time import time
from datetime import datetime
from math import sin, cos, radians, pi, degrees, atan2
from emote_utils import NoMatchError
from attr import attrs, attrib
from twisted.internet.task import LoopingCall
from .distance import pc, kpc, mpc, gpc, tpc, au, ly, km, light_speed
from .sound import get_sound, empty_room, nonempty_room
from . import db
from .protocol import interface_sound, message
from .socials import factory


def now(when=None):
    """Returns local game time according to ServerOptions.time_difference. If
    when is provided use that value as a base, otherwise use
    datetime.utcnow()."""
    if when is None:
        when = datetime.utcnow()
    return when - db.ServerOptions.get().time_difference


def directions(c1, c2, format=int):
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
        results.append('%s %s' % (format(diff), direction))
    if y1 != y2:
        diff = max(y1, y2) - min(y1, y2)
        if y2 > y1:
            direction = 'north'
        else:
            direction = 'south'
        results.append('%s %s' % (format(diff), direction))
    if z1 != z2:
        diff = max(z1, z2) - min(z1, z2)
        if z2 > z1:
            direction = 'up'
        else:
            direction = 'down'
        results.append('%s %s' % (format(diff), direction))
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
    if player.resting_state is not db.RestingStates.standing:
        player.message('You must stand up first.')
        return False  # Stop any walk task.
    loc = player.location
    s = db.Session
    players = [player]
    players.extend(player.followers)
    now = time()
    if not observe_speed or now - player.last_walked >= player.speed:
        px, py, pz = player.coordinates
        px += x
        py += y
        pz += z
        if loc.coordinates_ok((px, py, pz)):
            player.clear_following()
            player.last_walked = now
            direction = db.Direction.query(x=x, y=y, z=z).first()
            old_tile = loc.tile_at(*player.coordinates)
            new_tile = loc.tile_at(px, py, pz)
            if getattr(
                old_tile, 'name', None
            ) == getattr(new_tile, 'name', None):
                func = None
            elif new_tile is None:
                if old_tile is None:
                    func = None
                else:
                    func = old_tile.step_off
            else:
                func = new_tile.step_on
            default_walk_sound = loc.get_walk_sound(
                (px, py, pz), covering=new_tile
            )
            for obj in players:
                if obj.location is not loc:
                    continue
                obj.recent_direction = direction
                obj.steps += 1
                obj.recent_exit_id = None
                obj.coordinates = (px, py, pz)
                obj.update_neighbours()
                if func is not None:
                    func(obj, private=obj is not player)
                if obj is player:
                    wsound = sound
                    if wsound is None:
                        wsound = default_walk_sound
                else:
                    wsound = default_walk_sound
                if wsound is not None:
                    obj.sound(wsound)
            s.add_all(players)
            return True
        else:
            player.message(loc.cant_go_msg)
            player.sound(get_sound(loc.cant_go_sound), private=True)
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
        super().start(db.Object.get(self.id).speed)

    def walk(self):
        """Make the player walk."""
        with db.session() as s:
            obj = db.Object.get(self.id)
            if obj is None:
                return self.stop()
            obj.clear_following()
            kwargs = dict(observe_speed=False)
            if obj.speed != self.interval:
                self.stop()
                self.start(obj.speed)
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
                s.add(obj)
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
        player.do_social(string, _others=others[1:])
    except NoMatchError as e:
        player.message('Nothing found matching %s.' % e.args)


def percent(n, full):
    """Return the n as a percentage of full."""
    return (100.0 / full) * n


def direction_between(origin, target):
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
    return db.Direction.query(x=x, y=y, z=z).first()


def format_distance(
    units,
    show_tpcs=True,
    show_gpcs=True,
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
    if show_tpcs:
        tpcs, units = divmod(units, tpc * base)
        tpcs = round(tpcs, 2)
        if tpcs == int(tpcs):
            tpcs = int(tpcs)
        if tpcs:
            fmt.append('%r tpc' % round(tpcs, 2))
    if show_gpcs:
        gpcs, units = divmod(units, gpc * base)
        gpcs = round(gpcs, 2)
        if gpcs == int(gpcs):
            gpcs = int(gpcs)
        if gpcs:
            fmt.append('%r gpc' % round(gpcs, 2))
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


def format_distance_simple(d):
    """Format distance d in a simple way."""
    if d >= tpc:
        v = d / tpc
        u = 'tpc'
    elif d >= gpc:
        v = d / gpc
        u = 'gpc'
    elif d >= kpc:
        v = d / kpc
        u = 'kpc'
    elif d >= pc:
        v = d / pc
        u = 'pc'
    elif d >= ly:
        v = d / ly
        u = 'ly'
    elif d >= au:
        v = d / au
        u = 'au'
    elif d >= km:
        v = d / km
        u = 'km'
    else:
        v = d
        u = 'm'
    return '%.2f %s' % (v, u)


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


def angle_between(p1, p2):
    """Get the angle between p1 and p2. No clue what this is measured in.
    Code modified from:
    https://stackoverflow.com/questions/42258637/how-to-know-the-angle-between-
    two-points"""
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    return degrees(atan2(y2 - y1, x2 - x1))


def point_pos(c, d, theta):
    """Return the coordinates distance d units in theta direction."""
    x, y, z = c
    theta_rad = pi/2 - radians(theta)
    return x + d*cos(theta_rad), y + d*sin(theta_rad), z


def migrate(
    player, obj, destination, coordinates, leave_msg, leave_sound,
    arrive_msg, arrive_sound, follow_msg
):
    """Migrate a player from one room to another, doing all the necessaries."""
    player.clear_following()
    player.do_social(leave_msg, _others=[obj])
    player.move(destination, coordinates)
    if leave_sound is not None:
        obj.sound(get_sound(leave_sound))
    if destination is not None:
        string = factory.get_strings(arrive_msg, [player, obj])[-1]
        destination.broadcast_command_selective(
            lambda obj: obj is not player,
            message, string
        )
        if arrive_sound is not None:
            player.sound(get_sound(arrive_sound))
    for follower in player.followers:
        strings = factory.get_strings(follow_msg, [follower, player, obj])
        follower.message(strings[0])
        player.message(strings[1])
        follower.move(destination, coordinates)
        obj.location.broadcast_command(message, strings[-1], _who=obj)
        destination.broadcast_command_selective(
            lambda obj: obj is not player and obj not in player.followers,
            message, strings[-1]
        )


def truncate(s, n=80, after='...'):
    """Return string s truncated to n characters. If s is truncated, append
    after."""
    if not s:
        return ''
    s = s.splitlines()[0]
    if len(s) > n:
        s = s[:n] + after
    return s


def frange(start, stop, step):
    while start < stop:
        yield start
        start += step
