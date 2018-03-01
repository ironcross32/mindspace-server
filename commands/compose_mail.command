def parse_args(id=None, subject=None, body=None):
    return (id, subject, body)

id, subject, body = parse_args(*a)
q = Object.query(Object.player_id.isnot(None))
if id is None:
    items = [Item('Select Player', None)]
    for obj in q:
        items.append(Item(obj.get_name(player.is_staff), __name__, args=[obj.id]))
    menu(con, Menu('Compose Mail', items, escapable=True))
    end()
obj = q.filter_by(id=id).first()
valid_object(player, obj)
if subject is None:
    get_text(con, 'Enter a subject for your mail', __name__, args=[id])
    end()
if body is None:
    get_text(con, 'Enter the body of your message', __name__, multiline=True, args=[id, subject])
    end()
s.add(MailMessage.send(player, obj, subject, body))
player.message('Message sent.')