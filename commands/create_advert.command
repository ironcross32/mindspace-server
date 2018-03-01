check_admin(player)
if a:
    data = a[0]
    a = Advert(owner=player, **data)
    s.add(a)
    s.commit()
    player.message(f'Created advert #{a.id}.')
else:
    form(con, ObjectForm(Advert(), __name__, title='Create Advert', cancel='Cancel'))