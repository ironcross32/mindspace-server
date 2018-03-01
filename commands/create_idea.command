def parse_args(name=None, body=None):
    return (name, body)

name, body= parse_args(*a)
if not name:
    get_text(con, 'Enter a title for your idea', __name__, escapable=True)
elif not body:
    get_text(con, 'Enter the text of your new idea', __name__, args=[name], multiline=True)
else:
    i = Idea(owner_id=player.id, name=name, body=body)
    s.add(i)
    player.message('Idea created.')
    con.handle_command('ideas')
