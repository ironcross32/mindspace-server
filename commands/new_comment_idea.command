def parse_args(id, text=None):
    return (id, text)

id, text = parse_args(*a)
if text is None:
    get_text(con, 'Enter the text of your comment', __name__, multiline=True, args=[id])
else:
    if text:
        comment = IdeaComment(idea_id=id, owner_id=player.id, text=text)
        s.add(comment)
        player.message('Comment posted.')
    else:
        player.message('Canceled.')
    con.handle_command('comments_idea', id)
