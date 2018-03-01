def parse_args(mode='recent', start=0):
    return (mode, start)

mode, start = parse_args(*a)

def idea_string(idea, staff=player.is_staff, Item=Item):
    return Item(idea.get_name(staff), 'view_idea', args=[idea.id])

items = [
    LabelItem('Ideas'),
    Item('New Idea', 'create_idea'),
    LabelItem('Reorder')
]

for name in ('recent', 'oldest', 'votes'):
    items.append(Item(f'({"*" if mode == name else " "}) Order by {name.title()}', __name__, args=[name, start]))

q = Idea.query()
if mode == 'recent':
    q = q.order_by(Idea.created.desc())
elif mode == 'oldest':
    q = q.order_by(Idea.created.asc())
elif mode == 'votes':
    q = q.join(IdeaVote).group_by(Idea).order_by(sqlalchemy.func.count(IdeaVote.__table__.c.idea_id).desc())
else:
    player.message(f'Unsupported mode: {mode}.')
c = q.count()
if c:
    items.append(LabelItem(f'Ideas ({c})'))
    page = Page(q, start=start)
    items.extend(page.get_items(idea_string, __name__, mode))
else:
    items.append(LabelItem('No ideas to show'))
menu(con, Menu('Ideas', items, escapable=True))
