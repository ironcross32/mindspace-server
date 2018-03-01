def parse_args(id, folder, body=None):
    return (id, folder, body)

id, folder, body = parse_args(*a)
staff = player.is_staff
obj = MailMessage.query(sqlalchemy.or_(MailMessage.to_id == player.id, MailMessage.owner_id == player.id), id=id).first()
valid_object(player, obj)
if body is None:
    get_text(con, 'Enter the body of your reply', __name__, multiline=True, args=[id, folder])
    end()
new = MailMessage.send(player, obj.owner, None, body)
new.parent = obj
s.add(new)
player.message('Reply sent.')
con.handle_command('mail_folder', folder)