from pytest import raises
from server.db import CommunicationChannel, Object, Player, session, \
     CommunicationChannelMessage, TransmitionError

with session() as s:
    c = CommunicationChannel(name='Test Channel')
    s.add(c)
    o = Object(name='Test Character', player=Player(username='test'))
    s.add(o)
    s.commit()
    cid = c.id
    oid = o.id


def test_transmit():
    with session() as s:
        c = s.query(CommunicationChannel).get(cid)
        o = s.query(Object).get(oid)
        assert isinstance(c.transmit(o, 'test'), CommunicationChannelMessage)


def test_possible_communication_channels():
    with session() as s:
        c = s.query(CommunicationChannel).get(cid)
        o = s.query(Object).get(oid)
        assert c in o.possible_communication_channels()
        c.builder = True
        s.commit()
        assert c not in o.possible_communication_channels()


def test_failing_transmit():
    with session() as s:
        c = s.query(CommunicationChannel).get(cid)
        o = s.query(Object).get(oid)
        with raises(TransmitionError):
            c.transmit(o, 'This should fail.')
