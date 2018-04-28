from server.db import CommunicationChannel
from server.program import handle_traceback


def test_handle_traceback():
    e = ValueError('Testing.')
    assert not CommunicationChannel.count()
    handle_traceback(e, 'Test Program', 'py.test', 'Nowhere')
    channel = CommunicationChannel.first()
    assert CommunicationChannel.count() == 1
    assert channel is not None
    assert len(channel.messages) == 1
    handle_traceback(
        RuntimeError('Another Error'), 'Test Program', 'py.test', 'Nowhere'
    )
    assert CommunicationChannel.count() == 1
    assert len(channel.messages) == 2
