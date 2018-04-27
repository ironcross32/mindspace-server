from server.db import Object, ServerOptions


def test_system():
    assert Object.get(0) is not None


def test_system_object():
    o = ServerOptions.get()
    assert o.system_object_id == 0
    assert o.system_object is Object.get(0)
