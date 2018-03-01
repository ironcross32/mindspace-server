items = [
    Item('Mail', None),
    Item('Compose', 'compose_mail'),
    Item('Inbox', 'mail_folder', args=['inbox']),
    Item('Sent', 'mail_folder', args=['sent'])
]
menu(con, Menu('Mail', items, escapable=True))