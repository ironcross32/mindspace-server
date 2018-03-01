check_admin(player)
import re
if a:
    code = a[0]
    for full, id in re.findall('(#([0-9]+))', code):
        code = code.replace(full, f's.query(Object).get({id})')
else:
    player.message('You must enter some code.')
    end()
if con.shell is None:
    con.shell = PythonShell(con)
with redirect_stdout(con.shell), redirect_stderr(con.shell):
    con.shell.locals.update(
        player=player,
        here=player.location,
        s=s
    )
    if con.shell.push(code):
        msg = '...'
    else:
        msg = '>>>'
    message(con, msg)
for name in ('s', 'player', 'here'):
    del con.shell.locals[name]