from pytest import raises
from server.db import (
    Bank, BankAccount, BankAccountAccessor, Object, Session as s, ATM,
    Currency, CreditCard, ATMError
)


currency = Currency(name='Tests', value=1.0)
s.add(currency)
s.commit()
b = Bank(
    name='Test Bank', description='This is a test bank', currency=currency
)
s.add(b)
s.commit()
p = Object.query(name='Test Player').first()


def bank_test():
    assert b.accounts == []


def test_account():
    a = BankAccount(bank_id=b.id, name='Test Account')
    s.add(a)
    s.commit()
    assert a.get_accessor(p) is None
    s.add(a.add_accessor(p))
    s.commit()
    accessor = a.get_accessor(p)
    assert isinstance(accessor, BankAccountAccessor)


def test_atm():
    atm = Object(name='Test ATM')
    s.add(atm)
    s.commit()
    atm.atm = ATM(bank=b)
    assert atm.is_atm
    assert atm.atm.bank is b
    assert atm.atm in b.atms
    assert atm.atm.object is atm


def test_withdraw():
    obj = Object(name='Test ATM')
    atm = ATM(bank=b)
    obj.atm = atm
    a = BankAccount(bank=b)
    s.add_all([atm, obj, a])
    s.commit()
    amount = 5.0
    accessor = a.add_accessor(p, can_withdraw=False)
    assert isinstance(accessor, BankAccountAccessor)
    s.add(accessor)
    with raises(ATMError) as exc:
        atm.withdraw(p, a, currency, amount)
    assert exc.value.args == (a.insufficient_perms_msg,)
    accessor.can_withdraw = True
    with raises(ATMError) as exc:
        atm.withdraw(p, a, currency, -1)
    assert exc.value.args == (atm.overflow_msg,)
    with raises(ATMError) as exc:
        atm.withdraw(p, a, currency, amount)
    assert exc.value.args == (a.insufficient_funds_msg,)
    a.balance += amount
    res = atm.withdraw(p, a, currency, amount)
    assert isinstance(res, Object)
    assert isinstance(res.card, CreditCard)
