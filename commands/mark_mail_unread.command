id, folder = a
staff = player.is_staff
obj = MailMessage.query(sqlalchemy.or_(MailMessage.to_id == player.id, MailMessage.owner_id == player.id), id=id).first()
valid_object(player, obj)
obj.read = False
s.add(obj)
player.message(f'Marked {obj.get_name(staff)} unread.')
con.handle_command('mail_folder', folder)