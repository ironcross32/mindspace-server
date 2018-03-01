id, folder = a
staff = player.is_staff
obj = MailMessage.query(sqlalchemy.or_(MailMessage.to_id == player.id, MailMessage.owner_id == player.id), id=id).first()
valid_object(player, obj)
obj.read = True
s.add(obj)
items = [
    Item(obj.get_name(staff), None),
    Item(f'From: {"System" if obj.owner_id is None else obj.owner.get_name(staff)}', 'compose_mail', args=[obj.owner_id]),
    Item(f'To: {obj.to.get_name(staff)}', 'compose_mail', args=[obj.to_id]),
    Item(f'Subject: {obj.get_name(staff)}', 'copy', args=[obj.get_name(staff)]),
    Item(f'Sent: {obj.created}', 'copy', args=[str(obj.created)])
]
if obj.parent is not None:
    items.append(Item(f'In reply to: {obj.parent.get_name(staff)}', __name__, args=[obj.parent_id, folder]))
items.extend(
    [
        Item('Mark Unread', 'mark_mail_unread', args=[obj.id, folder]),
        Item('Reply', 'reply_mail', args=[obj.id, folder])
    ]
)
for line in obj.text.splitlines():
    items.append(Item(line, 'copy', args=[line]))
items.append(Item(f'Back To {folder.title()} Folder', 'mail_folder', args=[folder]))
menu(con, Menu('Message', items, escapable=True))