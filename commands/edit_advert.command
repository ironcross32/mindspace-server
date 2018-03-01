check_admin(player)

def parse_args(id=None, data=None):
    return (id, data)

id, data = parse_args(*a)
if id is None:
    items = [Item('Adverts', None)]
    for ad in s.query(Advert).order_by(Advert.text.asc()):
        items.append(Item(ad.text, __name__, args=[ad.id]))
    menu(con, Menu('Select Advert', items, escapable=True))
    end()
ad = s.query(Advert).get(id)
if ad is None:
    player.message('Invalid advert.')
    end()
if data is None:
    form(con, ObjectForm(ad, __name__, args=[id], title='Edit Advert', cancel='Cancel'))
    end()
for name, value in data.items():
    setattr(ad, name, value)
s.add(ad)
player.message('Done.')