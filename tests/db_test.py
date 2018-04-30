from datetime import datetime, timedelta
from server.db import (
    Object, ServerOptions, CommunicationChannel, CommunicationChannelMessage,
    session, Player, Shop, ShopItem, TextStyle
)

now = datetime.utcnow()


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


def test_delete_object():
    with session() as s:
        c = CommunicationChannel(name='Test Channel')
        o = Object(name='Test Player')
        s.add_all([o, c])
        s.commit()
        o.player = Player(username='test')
        s.add(o.player)
        s.commit()
        i = o.player_id
        c.banned.append(o)
        c.listeners.append(o)
        s.commit()
        s.delete(o)
        assert Player.get(i) is None
        assert not c.listeners
        assert not c.banned


def test_delete_shop():
    with session() as s:
        o = Object(name='Test Shop Object')
        s.add(o)
        s.commit()
        shop = Shop()
        o.shop = shop
        s.add(shop)
        s.commit()
        item = Object(name='Test Item', fertile=True)
        s.add(item)
        s.commit()
        s.add(shop.add_item(item, 1.0))
        s.commit()
        s.delete(shop)
        s.commit()
        assert shop.id is not None
        assert Shop.get(shop.id) is None
        assert not ShopItem.query(shop_id=shop.id).count()


def test_can_change_name():
    o = Object()
    assert o.last_name_change is None
    assert o.can_change_name() is None
    o.last_name_change = now - ServerOptions.get().name_change_interval
    assert o.can_change_name() is None
    i = timedelta(days=1)
    o.last_name_change += i
    assert o.can_change_name() <= i


def test_set_name():
    name = 'Changing now'
    o = Object()
    o.set_name(name)
    assert o.last_name_change >= now
    assert o.name == name


def test_get_channel():
    with session() as s:
        o = Object(name='Test Object')
        assert o.get_channel('test') == 'test-None'
        s.add(o)
        s.commit()
        assert o.get_channel('test') == f'test-{o.id}'


def test_get_style():
    with session() as s:
        o = Object(name='Test Player')
        p = Player(username='test styles')
        s.add(o)
        s.commit()
        o.player = p
        s.commit()
        assert not p.text_styles
        s = o.get_style(None)
        assert len(p.text_styles) == 1
        assert s == TextStyle.style.default.arg
