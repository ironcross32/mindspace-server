from pytest import raises
from server.db import CreditCard, CreditCardError, Object

p = Object.query(name='Test Player').first()
c = CreditCard.first()


def test_stupidity():
    assert isinstance(c, CreditCard)
    assert isinstance(p, Object)
    assert c.password is None


def test_initial():
    assert c.currency_id == 1
    assert c.incorrect_password_attempts == 0
    assert not c.transfers
    assert c.max_password_attempts == 3


def test_locked():
    assert not c.locked
    assert c.incorrect_password_attempts == 0
    c.authenticate(p, 'test')
    assert c.incorrect_password_attempts == 1
    assert not c.locked
    c.authenticate(p, 'test')
    c.authenticate(p, 'test')
    assert c.locked
    with raises(CreditCardError) as exc:
        c.transfer(c.currency, 0, 'testing')
    assert exc.value.args == (c.locked_msg,)
