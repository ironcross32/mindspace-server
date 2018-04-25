from server.db import Base, Currency, Object, CreditCard, session


Base.metadata.create_all()
with session() as s:
    s.add(Currency(value=1.0))
    s.commit()
    c = CreditCard(value=5)
    s.add(c)
    s.commit()
    p = Object(name='Test Player')
    o = Object(name='Credit Card', holder=p, credit_card_id=c.id)
    s.add_all([p, o])
