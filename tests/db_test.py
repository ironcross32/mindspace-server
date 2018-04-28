from server.db import (
    Object, ServerOptions, CommunicationChannel, CommunicationChannelMessage,
    session
)


def test_system():
    assert Object.get(0) is not None


def test_system_object():
    o = ServerOptions.get()
    assert o.system_object_id == 0
    assert o.system_object is Object.get(0)


def test_delete_communication_channel():
    with session() as s:
        c = CommunicationChannel.count()
        assert CommunicationChannel.query().delete() == c
        # Make new channels.
        c1 = CommunicationChannel(name='Test1')
        c2 = CommunicationChannel(name='Test 2')
        s.add_all((c1, c2))
        s.commit()
        for x in range(10):
            for channel in (c1, c2):
                s.add(
                    CommunicationChannelMessage(
                        channel_id=channel.id, text=f'Message {x}.'
                    )
                )
        s.commit()
        c = CommunicationChannelMessage.count()
        assert c != 0
        deleted = len(c1.messages)
        s.delete(c1)
        s.commit()
        assert CommunicationChannelMessage.count() == (c - deleted)
        assert not CommunicationChannelMessage.query(channel_id=c1.id).count()
