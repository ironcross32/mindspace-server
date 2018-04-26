from pytest import raises
from server.db import CreditCard, CreditCardError
from .conftest import Message, CustomPlayer

c = CreditCard.first()


p = CustomPlayer()


def test_stupidity():
    assert isinstance(c, CreditCard)
    assert c.password is None


def test_initial():
    assert c.currency_id == 1
    assert c.incorrect_password_attempts == 0
    assert not c.transfers
    assert c.max_password_attempts == 3


def test_locked():
    assert not c.locked
    assert c.incorrect_password_attempts == 0
    with raises(Message) as exc:
        c.authenticate(p, 'test')
    assert exc.value.args == (c.incorrect_password_msg,)
    assert c.incorrect_password_attempts == 1
    assert not c.locked
    with raises(Message):
        c.authenticate(p, 'test')
    with raises(Message):
        c.authenticate(p, 'test')
    assert c.locked
    with raises(CreditCardError) as exc:
        c.transfer(c.currency, 0, 'testing')
    assert exc.value.args == (c.locked_msg,)
