"""Provides the Object class."""

import enum
import logging
import os.path
from datetime import datetime
from sqlalchemy import (
    Column, Integer, ForeignKey, Boolean, Float, func, or_, and_, Enum
)
from sqlalchemy.orm import relationship, backref
from .base import (
    Base, CoordinatesMixin, NameMixin, AmbienceMixin, LocationMixin,
    DescriptionMixin, OwnerMixin, RandomSoundMixin, RandomSoundContainerMixin,
    StarshipMixin, HiddenMixin, CreatedMixin, DataMixin, message, Sound
)
from .players import TextStyle
from .server_options import ServerOptions
from .session import Session
from .communication import CommunicationChannel
from ..util import directions
from ..protocol import (
    object_sound, location, message as _message, identify, delete, zone,
    random_sound, remember_quit, speak
)
from ..forms import Label, Field
from ..sound import Sound as _Sound, get_sound, nonempty_room
from ..socials import factory
from .phones import PhoneStates

logger = logging.getLogger(__name__)

connections = {}


class RestingStates(enum.Enum):
    """Possible values for sitting."""

    standing = 0
    sitting = 1
    lying = 2


class ObjectRandomSound(RandomSoundMixin, Base):
    """A random sound for objects."""

    __tablename__ = 'object_random_sounds'
    object_id = Column(Integer, ForeignKey('objects.id'), nullable=False)
    object = relationship(
        'Object',
        backref=backref('random_sounds', cascade='all, delete-orphan')
    )


class Object(
    Base, NameMixin, CoordinatesMixin, AmbienceMixin, LocationMixin,
    DescriptionMixin, OwnerMixin, RandomSoundContainerMixin, StarshipMixin,
    HiddenMixin, CreatedMixin, DataMixin
):
    """A player-facing object."""

    __tablename__ = 'objects'
    fertile = Column(Boolean, nullable=False, default=False)
    gender_id = Column(Integer, ForeignKey('genders.id'), nullable=True)
    gender = relationship('Gender', backref='objects')
    max_distance_multiplier = Column(Float, nullable=False, default=1.0)
    say_msg = message('%1N say%1s: "{text}"')
    say_sound = Column(
        Sound, nullable=False, default=os.path.join('players', 'say.wav')
    )
    teleport_msg = message('%1N vanish%1e in a column of light.')
    teleport_sound = Column(
        Sound, nullable=False,
        default=os.path.join('ambiences', 'teleport.wav')
    )
    transit_route_id = Column(
        Integer, ForeignKey('transit_routes.id'), nullable=True
    )
    transit_route = relationship(
        'TransitRoute', backref=backref('object', uselist=False)
    )
    scanned_id = Column(Integer, ForeignKey('objects.id'), nullable=True)
    scanned = relationship(
        'Object', backref='scanned_by', foreign_keys=[scanned_id],
        remote_side='Object.id'
    )
    recent_direction_id = Column(
        Integer, ForeignKey('directions.id'), nullable=True
    )
    recent_direction = relationship('Direction', backref='recently_traveled')
    log = Column(Boolean, nullable=False, default=False)
    connected = Column(Boolean, nullable=False, default=False)
    anchored = Column(Boolean, nullable=False, default=True)
    steps = Column(Integer, nullable=False, default=0)
    holder_id = Column(Integer, ForeignKey('objects.id'), nullable=True)
    holder = relationship(
        'Object', backref='holding', foreign_keys=[holder_id],
        remote_side='Object.id'
    )
    sitting_id = Column(Integer, ForeignKey('chairs.id'), nullable=True)
    sitting = relationship(
        'Chair', backref='occupants', foreign_keys=[sitting_id]
    )
    # None = standing, True = sitting, False = lying:
    resting_state = Column(
        Enum(RestingStates), nullable=False, default=RestingStates.standing
    )
    inside_id = Column(Integer, ForeignKey('containers.id'), nullable=True)
    inside = relationship(
        'Container', backref='contents', foreign_keys=[inside_id]
    )
    player_id = Column(Integer, ForeignKey('players.id'), nullable=True)
    player = relationship(
        'Player', backref=backref('object', uselist=False)
    )
    atm_id = Column(Integer, ForeignKey('atms.id'), nullable=True)
    atm = relationship('ATM', backref=backref('object', uselist=False))
    phone_id = Column(Integer, ForeignKey('phones.id'), nullable=True)
    phone = relationship(
        'Phone', backref=backref('object', uselist=False)
    )
    mobile_id = Column(Integer, ForeignKey('mobiles.id'), nullable=True)
    mobile = relationship(
        'Mobile', backref=backref('object', uselist=False)
    )
    credit_card_id = Column(
        Integer, ForeignKey('credit_cards.id'), nullable=True
    )
    credit_card = relationship(
        'CreditCard', backref=backref('object', uselist=False)
    )
    exit_id = Column(Integer, ForeignKey('entrances.id'), nullable=True)
    exit = relationship(
        'Entrance', backref=backref('object', uselist=False)
    )
    recent_exit_id = Column(Integer, ForeignKey('objects.id'), nullable=True)
    recent_exit = relationship(
        'Object', backref='recent_users', foreign_keys=[recent_exit_id],
        remote_side='Object.id'
    )
    window_id = Column(Integer, ForeignKey('windows.id'), nullable=True)
    window = relationship(
        'Window', backref=backref('object', uselist=False)
    )
    chair_id = Column(Integer, ForeignKey('chairs.id'), nullable=True)
    chair = relationship(
        'Chair', backref=backref('object', uselist=False),
        foreign_keys=[chair_id]
    )
    container_id = Column(Integer, ForeignKey('containers.id'), nullable=True)
    container = relationship(
        'Container', backref=backref('object', uselist=False),
        foreign_keys=[container_id]
    )
    shop_id = Column(Integer, ForeignKey('shops.id'), nullable=True)
    shop = relationship(
        'Shop', backref=backref('object', uselist=False)
    )
    speed = Column(Float, nullable=False, default=0.5)
    last_walked = Column(Float, nullable=False, default=0.0)
    following_id = Column(Integer, ForeignKey('objects.id'), nullable=True)
    following = relationship(
        'Object', backref='followers', foreign_keys=[following_id],
        remote_side='Object.id'
    )
    pose = message(None, nullable=True)
    follow_msg = message('%1N start%1s to follow %2n.')
    unfollow_msg = message('%1N stop%1s following %2n.')
    ditch_msg = message('%1N ditch%1e %2n.')
    start_use_msg = message('%1N start%1s using %2n.')
    stop_use_msg = message('%1N stop%1s using %2n.')
    get_msg = message('%1N get%1s %2n.')
    drop_msg = message('%1N drop%1s %2n.')
    give_msg = message('%1N give%1s %2n to %3n.')
    knock_msg = message('%1N knock%1s on %2n.')
    knock_sound = Column(Sound, nullable=True, default='objects/knock1.wav')
    get_sound = Column(Sound, nullable=True)
    drop_sound = Column(Sound, nullable=True)
    give_sound = Column(Sound, nullable=True)

    def can_change_name(self):
        """Returns a timedelta indicating when this object can change its own
        name or None."""
        if self.last_name_change is not None:
            elapsed = datetime.utcnow() - self.last_name_change
            i = ServerOptions.get().name_change_interval
            if elapsed < i:
                return i - elapsed

    def inspect(self, obj):
        """Used to quickly inspect any object."""
        con = self.get_connection()
        if con is None:
            return False
        dirs = directions(self.coordinates, obj.coordinates)
        max_distance = obj.location.max_distance
        max_distance_multiplier = obj.max_distance_multiplier
        random_sound(
            con, nonempty_room, *obj.coordinates,
            max_distance=max_distance * max_distance_multiplier
        )
        if obj.container:
            random_sound(
                con, get_sound('objects/container.wav'), *obj.coordinates,
                max_distance=max_distance * max_distance_multiplier
            )
        self.message(
            f'{obj.get_full_name(self.is_staff)}: {dirs}. '
            f'{obj.get_description()}'
        )
        return True

    def speak(self, data):
        """Allow this object to speak an arbitrary array of floats."""
        self.location.broadcast_command(speak, self.id, data, _who=self)

    def same_coordinates(self):
        """Returns a set of sqlalchemy filters which expect the same
        coordinates as this object."""
        args = []
        for name in ('x', 'y', 'z'):
            args.append(getattr(Object, name) == getattr(self, name))
        return args

    def get_credit_cards(self, *args, **kwargs):
        """Get a query containing any credit cards held by this object."""
        Object = self.__class__
        return Object.query(
            Object.holder_id == self.id, Object.credit_card_id.isnot(None),
            *args, **kwargs
        ).order_by(Object.name, Object.created)

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
        if self.sitting is None:
            if self.pose is None:
                msg = ''
            else:
                msg = self.pose
        else:
            msg = self.resting_state.name
            msg = getattr(self.sitting, f'{msg}_msg').format(
                self.sitting.object.get_name(self.is_staff)
            )
        name = f'{name} {msg}'.strip()
        return name

    def get_type(self):
        """Returns a human-readable type for this object."""
        t = 'object'
        if self.is_player:
            if self.is_admin:
                t = 'admin'
            elif self.is_builder:
                t = 'builder'
            else:
                t = 'player'
        prefix = 'is_'
        for name in dir(self):
            if not name.startswith(prefix):
                continue
            if getattr(self, name):
                t = name[len(prefix):]
                break
        return t.title()

    def identify(self, con):
        """Identify this object to connection con."""
        identify(con, self)

    def get_all_fields(self):
        fields = super().get_all_fields()
        for name in (
            'chair', 'window', 'exit', 'mobile', 'player', 'phone', 'atm'
        ):
            obj = getattr(self, name)
            if obj is not None:
                fields.append(Label(name.title()))
                for field in obj.get_all_fields():
                    if isinstance(field, Field):
                        field.name = f'{name}.{field.name}'
                    fields.append(field)
        return fields

    @property
    def log_commands(self):
        con = self.get_connection()
        if con is None:
            return False
        else:
            return con.logged

    @log_commands.setter
    def log_commands(self, value):
        con = self.get_connection()
        if con is not None:
            con.logged = value

    @property
    def is_atm(self):
        return self.atm is not None

    @property
    def is_shop(self):
        return self.shop is not None

    @property
    def is_credit_card(self):
        return self.credit_card is not None

    @property
    def is_phone(self):
        return self.phone is not None

    @property
    def is_transit(self):
        return self.transit_route is not None

    @property
    def is_window(self):
        return self.window is not None

    @property
    def is_chair(self):
        return self.chair is not None

    @property
    def is_container(self):
        return self.container is not None

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
        old = connections.pop(self.id, None)
        if old is not None:
            old.player_id = None
            remember_quit(old)
            old.disconnect('Reconnecting from somewhere else.')
        if con is None:
            # Remember how long we were connected for.
            self.player.last_disconnected = datetime.utcnow()
            recent = self.player.last_disconnected - self.player.last_connected
            if self.player.connected_time is None:
                self.player.connected_time = recent
            else:
                self.player.connected_time += recent
        else:
            self.player.last_connected = datetime.utcnow()
            self.player.last_host = con.host
            con.player_id = self.id
            con.locked = self.player.locked
            connections[self.id] = con

    def get_connection(self):
        """Get the connection associated with this object."""
        return connections.get(self.id)

    def message(self, text, channel=None, style=None):
        """Send a message to this object."""
        con = self.get_connection()
        if con is not None:
            if style is None:
                style = self.get_style(channel)
            if channel is not None and self.player is not None and \
               self.player.channel_notifications:
                self.message(f'Channel: {channel}')
            return _message(con, text, channel=channel, style=style)
        elif self.is_phone:
            phone = self.phone
            if channel == 'say' and phone.state is PhoneStates.connected and \
               not phone.muted:
                phone.transmit(text)
            return True
        else:
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
        return self.sound('beeps', private=private)

    def sound(self, sound, private=False):
        """This object has made a sound. If private evaluates to True only tell
        this object. Otherwise tell everyone. If sound is None then nothing
        happens."""
        if sound is None:
            return
        elif not isinstance(sound, _Sound):
            sound = get_sound(sound)
        args = [self.id, sound]
        if private:
            con = self.get_connection()
            if con is not None:
                object_sound(con, *args)
        else:
            if self.location is None and self.holder is not None:
                loc = self.holder.location
                who = self.holder
                # Play the sound as if it came from the player holding this
                # object:
                args[0] = who.id
            else:
                loc = self.location
                who = self
            if loc is not None:
                loc.broadcast_command(object_sound, *args, _who=who)

    def teleport(self, location, coordinates):
        """Teleport this object to a new location."""
        self.resting_state = RestingStates.standing
        self.sitting = None
        old_location = self.location
        old_coordinates = self.coordinates
        self.do_social(self.teleport_msg)
        sound = get_sound(self.teleport_sound)
        self.move(location, coordinates)
        old_location.broadcast_command(
            random_sound, sound, *old_coordinates, 1.0
        )
        self.location.broadcast_command_selective(
            lambda obj: obj is not self, _message,
            f'{self.get_name(False)} teleports in.'
        )
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

    def say(self, text):
        """Have this object say something."""
        self.sound(self.say_sound)
        channel = self.get_channel('say')
        self.do_social(self.say_msg, text=text, _channel=channel)

    def get_channel(self, channel):
        """Return a unique channel name for this object."""
        return f'{channel}-{self.id}'

    def get_style(self, channel, example=None):
        """Get an appropriate style for the provided channel."""
        if self.player is not None:
            style = TextStyle.query(
                player_id=self.player_id, name=channel
            ).first()
            if style is None:
                style = TextStyle(
                    player_id=self.player_id, name=channel,
                    example_text=example
                )
                Session.add(style)
                Session.commit()
            return style.style

    def do_social(self, string, _channel=None, _others=None, *args, **kwargs):
        """Get social strings and send them out to players within visual range.
        This object will be the first object in the perspectives list, that
        list will be extended by _others. If _channel is None then
        self.get_channel('emote') will be used."""
        perspectives = [self]
        if _channel is None:
            _channel = self.get_channel('emote')
        if _others is not None:
            perspectives.extend(_others)
        strings = factory.get_strings(string, perspectives, **kwargs)
        viewers = self.get_visible().all()
        viewers.extend(self.holding)
        for obj in viewers:
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
        if self.location_id is not None:
            this = self
        elif self.holder_id is not None:
            this = self.holder
        else:
            raise AssertionError(
                'This object (%r) has no location and is not being held.' % (
                    self
                )
            )
        loc = this.location
        query_args = [Object.location_id == loc.id]
        query_args.extend(args)
        if not self.is_staff:
            query_args.extend(
                [
                    or_(
                        Object.hidden.is_(False),
                        and_(*this.same_coordinates())
                    )
                ]
            )
            for name in ('x', 'y', 'z'):
                query_args.append(
                    getattr(Object, name).between(
                        getattr(this, name) - loc.visibility,
                        getattr(this, name) + loc.visibility
                    )
                )
        return Object.query(*query_args, **kwargs)

    def use_exit(self, player):
        """Move player and their followers through this object if it is an
        exit."""
        entrance = self.exit
        assert entrance is not None, '%s is not an exit.' % self
        con = player.get_connection()
        other_side = entrance.get_other_side()
        if other_side is None:
            recent_exit_id = self.id
            msg = '%1N arrive%1s.'
        else:
            other_side.sound(other_side.exit.ambience)
            recent_exit_id = other_side.id
            msg = other_side.exit.arrive_msg
        strings = factory.get_strings(msg, [player, other_side])
        string = strings[-1]
        entrance.location.broadcast_command(_message, string, _who=other_side)
        player.do_social(entrance.leave_msg, _others=[self])
        player.steps += 1
        player.move(entrance.location, entrance.coordinates)
        player.recent_exit_id = recent_exit_id
        Session.add(player)
        for follower in player.followers:
            follower.steps += 1
            follower.do_social(entrance.follow_msg, _others=[player, self])
            entrance.location.broadcast_command_selective(
                lambda obj: obj not in player.followers, message,
                f'{follower.get_name()} arrives behind {player.get_name()}.',
                _who=other_side
            )
            follower.steps += 1
            follower.move(player.location, player.coordinates)
            follower.recent_exit_id = recent_exit_id
            Session.add(follower)
            self.location.broadcast_command(
                message,
                f'{follower.get_name()} leaves behind {player.get_name()}.',
                _who=self
            )
        Session.commit()
        if entrance.ambience is not None:
            sound = get_sound(entrance.ambience)
            self.sound(sound)
        else:
            sound = None
        for old_object in self.location.objects:
            if con is not None:
                delete(con, old_object.id)
            for follower in player.followers:
                c = follower.get_connection()
                if c is not None:
                    delete(c, old_object.id)
        player.update_neighbours()
        for follower in player.followers:
            follower.update_neighbours()
        if sound is not None:
            everyone = player.followers.copy()
            everyone.append(player)
            for person in everyone:
                con = person.get_connection()
                if con is not None:
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

    def move(self, location, coordinates):
        """Move this object to the specified location with the specified
        coordinates."""
        con = self.get_connection()
        if self.location is not None:
            exclusions = self.followers.copy()
            exclusions.append(self)
            if self.following_id is not None:
                exclusions.append(self.following)
            if con is not None:
                for obj in self.location.objects:
                    if obj not in exclusions:
                        delete(con, obj.id)
            self.location.broadcast_command_selective(
                lambda obj: obj not in exclusions, delete, self.id
            )
        self.location = location
        self.coordinates = coordinates
        if self.location is not None:
            self.update_neighbours()
            self.identify_location()

    def clear_following(self):
        """Stop this object from following anyone."""
        if self.following is not None:
            self.do_social(self.unfollow_msg, _others=[self.following])
            self.following_id = None

    def get_corner_coordinates(self, direction):
        """Find the coordinates of the corner in the given direction."""
        coordinates = []
        for name in ('x', 'y', 'z'):
            diff = getattr(direction, name)
            old = getattr(self, name)
            size = getattr(self.location, f'size_{name}')
            if not diff:
                new = old
            elif diff < 0:
                new = 0.0
            else:  # diff > 0
                new = size
            coordinates.append(new)
        return coordinates

    def get_gender(self):
        if self.gender_id is None:
            gid = 1
        else:
            gid = self.gender_id
        return Base._decl_class_registry['Gender'].get(gid)
