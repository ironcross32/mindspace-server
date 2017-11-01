"""Provides the Object class."""

import os.path
from sqlalchemy import (
    Column, Integer, ForeignKey, Boolean, Float, func, or_, and_, String
)
from sqlalchemy.orm import relationship, backref
from attrs_sqlalchemy import attrs_sqlalchemy
from .base import (
    Base, CoordinatesMixin, NameMixin, AmbienceMixin, LocationMixin,
    DescriptionMixin, OwnerMixin, RandomSoundMixin, RandomSoundContainerMixin
)
from .session import Session
from .communication import CommunicationChannel
from ..protocol import (
    object_sound, location, message, identify, delete, zone, random_sound
)
from .. import server
from ..forms import Label, Field
from ..sound import get_sound, get_ambience
from ..socials import factory

teleport_sound = get_sound(os.path.join('exits', 'teleport.wav'))
connections = {}


@attrs_sqlalchemy
class ObjectRandomSound(RandomSoundMixin, Base):
    """A random sound for objects."""

    __tablename__ = 'object_random_sounds'
    object_id = Column(Integer, ForeignKey('objects.id'), nullable=False)
    object = relationship('Object', backref='random_sounds')


@attrs_sqlalchemy
class Object(
    Base, NameMixin, CoordinatesMixin, AmbienceMixin, LocationMixin,
    DescriptionMixin, OwnerMixin, RandomSoundContainerMixin
):
    """An object or player."""
    __tablename__ = 'objects'
    log = Column(Boolean, nullable=False, default=False)
    connected = Column(Boolean, nullable=False, default=False)
    anchored = Column(Boolean, nullable=False, default=True)
    steps = Column(Integer, nullable=False, default=0)
    holder_id = Column(Integer, ForeignKey('objects.id'), nullable=True)
    holder = relationship(
        'Object', backref='holding', foreign_keys=[holder_id],
        remote_side='Object.id'
    )
    player_id = Column(Integer, ForeignKey('players.id'), nullable=True)
    player = relationship('Player', backref=backref('object', uselist=False))
    mobile_id = Column(Integer, ForeignKey('mobiles.id'), nullable=True)
    mobile = relationship('Mobile', backref=backref('object', uselist=False))
    exit_id = Column(Integer, ForeignKey('entrances.id'), nullable=True)
    exit = relationship('Entrance', backref=backref('object', uselist=False))
    recent_exit_id = Column(Integer, ForeignKey('objects.id'), nullable=True)
    recent_exit = relationship(
        'Object', backref='recent_users', foreign_keys=[recent_exit_id],
        remote_side='Object.id'
    )
    window_id = Column(Integer, ForeignKey('windows.id'), nullable=True)
    window = relationship('Window', backref=backref('object', uselist=False))
    hidden = Column(Boolean, nullable=False, default=False)
    monitor_transmitions = Column(Boolean, nullable=False, default=False)
    speed = Column(Float, nullable=False, default=0.5)
    last_walked = Column(Float, nullable=False, default=0.0)
    following_id = Column(Integer, ForeignKey('objects.id'), nullable=True)
    following = relationship(
        'Object', backref='followers', foreign_keys=[following_id],
        remote_side='Object.id'
    )
    pose = Column(String(20), nullable=True)
    follow_msg = Column(
        String(200), nullable=False, default='%1N start%1s to follow %2n.'
    )
    unfollow_msg = Column(
        String(200), nullable=False, default='%1N stop%1s following %2n.'
    )
    ditch_msg = Column(
        String(200), nullable=False, default='%1N ditch%1e %2n.'
    )
    start_use_msg = Column(
        String(200), nullable=False, default='%1N start%1s using %2n.'
    )
    stop_use_msg = Column(
        String(200), nullable=False, default='%1N stop%1s using %2n.'
    )
    get_msg = Column(String(200), nullable=False, default='%1N get%1s %2n.')
    drop_msg = Column(String(200), nullable=False, default='%1N drop%1s %2n.')
    give_msg = Column(
        String(200), nullable=False, default='%1N give%1s %2n to %3n.'
    )
    get_sound = Column(String(200), nullable=True)
    drop_sound = Column(String(200), nullable=True)
    give_sound = Column(String(200), nullable=True)

    def same_coordinates(self):
        """Returns a set of sqlalchemy filters which expect the same
        coordinates as this object."""
        args = []
        for name in ('x', 'y', 'z'):
            args.append(getattr(Object, name) == getattr(self, name))
        return args

    def get_actions(self):
        """Return all actions attached to this object."""
        a = self.actions.copy()
        for type in self.types:
            a.extend(type.actions)
        return a

    def get_hotkeys(self):
        """Return all hotkeys attached to this object."""
        h = self.hotkeys.copy()
        for type in self.types:
            h.extend(type.hotkeys)
        return h

    def get_full_name(self, *args, **kwargs):
        """Get name including pose."""
        name = self.get_name(*args, **kwargs)
        if self.pose:
            name = f'{name} {self.pose}'
        return name

    def get_type(self):
        """Returns a human-readable type for this object."""
        if self.is_player:
            if self.is_admin:
                return 'Admin'
            elif self.is_builder:
                return 'Builder'
            else:
                return 'Player'
        elif self.is_window:
            return 'Window'
        elif self.is_mobile:
            return 'Mobile'
        elif self.is_exit:
            return 'Exit'
        else:
            return 'Object'

    def identify(self, con):
        """Identify this object to connection con."""
        identify(con, self)

    def get_all_fields(self):
        fields = super().get_all_fields()
        fields.append(self.make_field('pose'))
        for name in ('hidden', 'anchored', 'log_commands'):
            fields.append(self.make_field(name, type=bool))
        for name in (
            'start_use_msg', 'stop_use_msg', 'get_msg', 'drop_msg', 'give_msg',
            'get_sound', 'drop_sound', 'give_sound', 'follow_msg',
            'unfollow_msg', 'ditch_msg'
        ):
            fields.append(self.make_field(name))
        for name in ('window', 'exit', 'mobile', 'player'):
            obj = getattr(self, name)
            if obj is not None:
                fields.append(Label(name.title()))
                for field in obj.get_all_fields():
                    if isinstance(field, Field):
                        field.name = f'{name}.{field.name}'
                    fields.append(field)
        return fields + RandomSoundContainerMixin.get_all_fields(self)

    @property
    def log_commands(self):
        return self.id in server.server.logged_players

    @log_commands.setter
    def log_commands(self, value):
        if value:
            server.server.logged_players.add(self.id)
        else:
            server.server.logged_players.remove(self.id)

    @property
    def is_window(self):
        return self.window is not None

    @property
    def is_player(self):
        return self.player is not None

    @property
    def is_mobile(self):
        return self.mobile is not None

    @property
    def is_builder(self):
        """Return whether or not this player is a builder."""
        return self.is_player and self.player.builder

    @property
    def is_admin(self):
        """Return whether or not this player is an admin."""
        return self.is_player and self.player.admin

    @property
    def is_exit(self):
        return self.exit is not None

    @property
    def is_staff(self):
        return self.is_builder or self.is_admin

    def register_connection(self, con):
        """Assign connection con to this object."""
        if self.get_connection() is not None:
            old = connections.pop(self.id)
            old.player_id = None
            old.disconnect('Reconnecting from somewhere else.')
        if con is not None:
            con.player_id = self.id
            con.locked = self.player.locked
            connections[self.id] = con

    def get_connection(self):
        """Get the connection associated with this object."""
        return connections.get(self.id)

    def message(self, *args, **kwargs):
        """Send a message to this object."""
        con = self.get_connection()
        if con is not None:
            return message(con, *args, **kwargs)
        return False

    def identify_location(self):
        """Notify this object of its location."""
        con = self.get_connection()
        if con is not None:
            zone(con, self.location.zone)
            location(con, self.location)
            for obj in self.location.objects:
                if obj is not self:
                    obj.identify(con)

    def beep(self, private=False):
        """Make this object beep."""
        return self.sound(get_sound('beeps'), private=private)

    def sound(self, sound, private=False):
        """This object has made a sound. If private evaluates to True only tell
        this object. Otherwise tell everyone."""
        args = (self.id, sound)
        if private:
            con = self.get_connection()
            if con is not None:
                object_sound(con, *args)
        else:
            if self.location is not None:
                self.location.broadcast_command(object_sound, *args, _who=self)

    def teleport(self, location, coordinates, sound=None):
        """Teleport this object to a new location."""
        if sound is None:
            sound = teleport_sound
        location.broadcast_command(
            message, f'{self.get_name()} appears.', _who=self
        )
        old = self.location
        self.location = location
        self.message(f'You appear at {location.get_name()}.')
        old.broadcast_command(object_sound, self.id, sound, _who=self)
        old.broadcast_command(
            message, f'{self.get_name()} vanishes.', _who=self
        )
        old.broadcast_command(delete, self.id)
        self.coordinates = coordinates
        con = self.get_connection()
        if con is not None:
            for obj in old.objects:
                delete(con, obj.id)
        self.identify_location()
        self.update_neighbours()
        self.sound(sound)

    def possible_communication_channels(self):
        """Return a query object representing all the channels this player can
        access."""
        args = []
        if self.is_builder:
            args.append(CommunicationChannel.builder.in_([True, False]))
        else:
            args.append(CommunicationChannel.builder.is_(False))
        if self.is_admin:
            args.append(CommunicationChannel.admin.in_([True, False]))
        else:
            args.append(CommunicationChannel.admin.is_(False))
        return Session.query(CommunicationChannel).filter(*args)

    def do_social(self, string, _others=None, _channel=None, *args, **kwargs):
        """Get social strings and send them out to players within visual range.
        This object will be the first object in the perspectives list, that
        list will be extended by _others. The message channel will be set to
        _channel."""
        perspectives = [self]
        if _others is not None:
            perspectives.extend(_others)
        strings = factory.get_strings(string, perspectives, **kwargs)
        for obj in self.get_visible():
            if obj in perspectives:
                msg = strings[perspectives.index(obj)]
            else:
                msg = strings[-1]
            obj.message(msg, channel=_channel)

    def match(self, string):
        """Match a string with an object from this room."""
        if self.is_admin and string.startswith('#'):
            return Session.query(Object).get(string[1:])
        else:
            return self.get_visible(
                func.lower(Object.name).like(f'{string}%')
            ).first()

    def get_visible(self, *args, **kwargs):
        """Get the objects in visual range of this object."""
        query_args = [Object.location_id == self.location_id]
        if not self.is_staff:
            query_args.extend(
                [
                    or_(
                        Object.hidden.is_(False),
                        and_(
                            Object.x == self.x,
                            Object.y == self.y,
                            Object.z == self.z
                        )
                    )
                ]
            )
            for name in ('x', 'y', 'z'):
                query_args.append(
                    getattr(Object, name).between(
                        getattr(self, name) - self.location.visibility,
                        getattr(self, name) + self.location.visibility
                    )
                )
        query_args.extend(args)
        q = Session.query(Object).filter(*query_args)
        if kwargs:
            q = q.filter_by(**kwargs)
        return q

    def use_exit(self, player):
        """Move player and their followers through this object if it is an
        exit."""
        entrance = self.exit
        assert entrance
        con = player.get_connection()
        other_side = Object.query(
            Object.location_id == entrance.location_id, Object.x == entrance.x,
            Object.y == entrance.y, Object.z == entrance.z,
            Object.exit_id.isnot(None)
        ).first()
        if other_side is None:
            recent_exit_id = self.id
            msg = '%1N arrive%1s.'
        else:
            if other_side.exit.ambience is not None:
                other_side.sound(get_ambience(other_side.exit.ambience))
            recent_exit_id = other_side.id
            msg = other_side.exit.arrive_msg
        entrance.location.broadcast_command(
            message, factory.get_strings(msg, [player, other_side])[-1],
            _who=other_side
        )
        for follower in player.followers:
            s = follower.is_staff
            follower.message(
                f'You follow {player.get_name(s)} through {self.get_name(s)}.'
            )
            entrance.location.broadcast_command(
                message,
                f'{follower.get_name()} arrives behind {player.get_name()}.',
                _who=other_side
            )
        player.steps += 1
        player.location_id = entrance.location_id
        player.recent_exit_id = recent_exit_id
        player.coordinates = entrance.coordinates
        Session.add(player)
        for follower in player.followers:
            follower.steps += 1
            follower.location_id = player.location_id
            follower.recent_exit_id = recent_exit_id
            follower.coordinates = player.coordinates
            Session.add(follower)
        Session.commit()
        self.location.broadcast_command(delete, player.id)
        self.location.broadcast_command(
            message,
            factory.get_strings(entrance.leave_msg, [player, self])[-1],
            _who=self
        )
        for follower in player.followers:
            self.location.broadcast_command(delete, follower.id)
            self.location.broadcast_command(
                message,
                f'{follower.get_name()} leaves behind {player.get_name()}.',
                _who=self
            )
        if entrance.ambience is not None:
            sound = get_ambience(entrance.ambience)
            self.sound(sound)
        else:
            sound = None
        player.message(
            f'You arrive at {player.location.get_name(player.is_staff)}.'
        )
        for old_object in self.location.objects:
            if con is not None:
                delete(con, old_object.id)
            for follower in player.followers:
                c = follower.get_connection()
                if c is not None:
                    delete(c, old_object.id)
        player.identify_location()
        player.update_neighbours()
        for follower in player.followers:
            follower.identify_location()
            follower.update_neighbours()
        if sound is not None and con is not None:
            random_sound(con, sound, *player.coordinates, 1.0)

    def make_random_sound(self, name):
        """Make an instance of ObjectRandomSound."""
        return ObjectRandomSound(object_id=self.id, name=name)

    def duplicate(self):
        obj = super().duplicate()
        for name in ('actions', 'keys'):
            getattr(obj, name).extend(getattr(self, name))
        for s in self.random_sounds:
            sound = s.duplicate()
            obj.random_sounds.append(sound)
        for thing in ('exit', 'mobile', 'window'):
            original = getattr(self, thing)
            if original is not None:
                setattr(obj, thing, original.duplicate())
        return obj