player = con.get_player()
if not player.is_admin:
    end()
if a:
    code = a[0]
else:
    player.message('You must enter some code.')
    end()
if con.shell is None:
    con.shell = PythonShell(con)
with redirect_stdout(
    con.shell
), redirect_stderr(
    con.shell
):
    con.shell.locals.update(
        player=player,
        here=player.location,
        s=s
    )
    if con.shell.push(code):
        player.message('...')
    else:
        player.message('>>>')
for name in ('s', 'player', 'here'):
    del con.shell.locals[name]
