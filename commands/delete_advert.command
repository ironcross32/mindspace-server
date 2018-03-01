check_admin(player)

def parse_args(id=None, response=None):
    return (id, response)

id, response = parse_args(*a)
if id is None:
    items = [Item('Select an advert', None)]
    for ad in s.query(Advert).order_by(Advert.text.asc()):
        items.append(Item(ad.text, __name__, [ad.id]))
    menu(con, Menu('Delete Advert', items, escapable=True))
    end()
ad = s.query(Advert).get(id)
if ad is None:
    message(con, 'Invalid advert.')
    end()
if response is None:
    menu(
        con, Menu(
            'Are you sure you want to delete this advert? ' + ad.text,
            [
                Item('Yes', __name__, args=[id, True]),
                Item('No', __name__, args=[id, False])
            ], escapable=True
        )
    )
elif not response:
    message(con, 'Not deleting.')
else:
    if server.last_advert == ad.id:
        server.last_advert = None
    s.delete(ad)
    message(con, 'Deleted.')