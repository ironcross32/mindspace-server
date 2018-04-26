from server.db import (
    Bank, BankAccount, BankAccountAccessor, Object, Session as s
)

b = Bank(name='Test Bank', description='This is a test bank')
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
