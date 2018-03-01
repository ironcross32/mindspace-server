def parse_args(name, start=0):
    return (name, start)

name, start = parse_args(*a)

def message_string(message, staff=player.is_staff, Item=Item, name=name):
    return Item(f'{message.get_name(staff)}: {message.created.ctime()}', 'read_mail', args=[message.id, name])

if name == 'inbox':
    messages = MailMessage.query(to_id=player.id)
elif name == 'sent':
    messages = MailMessage.query(owner_id=player.id)
messages = messages.order_by(MailMessage.read, MailMessage.created.desc())
items = [Item(f'{name.title()} Mail', None)]
page = Page(messages, start=start)
items.extend(
    page.get_items(message_string, __name__, name)
)
items.append(Item('Back To Mail Menu', 'mail'))
menu(con, Menu('Mail Folder', items, escapable=True))