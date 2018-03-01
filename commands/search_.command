def parse_args(type, command, text=None):
    return (type, command, text)

type, command, text = parse_args(*a)
cls = Base._decl_class_registry[type]
if text is not None:
    if text.startswith('#') and len(text) >= 2:
        kwargs = dict(id=text[1:])
    else:
        kwargs = dict(name=text)
    q = cls.query(**kwargs)
    c = q.count()
    if not c:
        player.message(f'{type} not found.')
    elif c is 1:
        con.search_string = text
        obj = q.first()
        con.handle_command(command, type, obj.id)
    else:
        items = [Item(f'Select {type}', None)]
        for obj in q:
            items.append(Item(obj.get_name(True), command, args=[type, obj.id]))
        menu(con, Menu('Results', items, escapable=True))
else:
    get_text(con, 'Enter search', __name__, value=con.search_string, args=[type, command])