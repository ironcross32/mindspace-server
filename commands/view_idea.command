id = a[0]
idea = Idea.get(id)
valid_object(idea, player)
items = [
    LabelItem('View Idea'),
    CopyItem(f'Name: {idea.get_name(player.is_staff)}'),
    CopyItem(f'Created: {idea.created.ctime()}'),
    CopyItem(f'ID: {idea.id}'),
    Item(f'Votes: {util.english_list(idea.votes, empty="None", key=lambda voter, staff=player.is_staff: voter.get_name(staff))} ({len(idea.votes)})', 'vote_idea', args=[idea.id]),
    Item(f'Comments: {len(idea.comments)})', 'comments_idea', args=[idea.id])
]
for line in Idea.first().body.splitlines():
    items.append(CopyItem(line))
items.append(Item('Back to Ideas', 'ideas'))
menu(con, Menu('Idea', items, escapable=True))
