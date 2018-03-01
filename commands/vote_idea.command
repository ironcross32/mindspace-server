id = a[0]
idea = Idea.get(id)
valid_object(idea, player)
if player in idea.votes:
    idea.votes.remove(player)
    msg = 'Vote removed.'
else:
    idea.votes.append(player)
    msg = 'Vote added'
player.message(msg)
con.handle_command('view_idea', id)
