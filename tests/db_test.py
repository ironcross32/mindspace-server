from server.db import Object, ServerOptions


def test_system():
    assert Object.get(0) is not None


def test_transmit_as():
    o = ServerOptions.get()
    assert o.transmit_as_id == 0
    assert o.transmit_as is Object.get(0)
