def parse_args(id, start=0):
    return (id, start)
id, start = parse_args(*a)
idea = Idea.get(id)
valid_object(idea, player)
items = [
    LabelItem(f'Comments on {idea.get_name(player.is_staff)}'),
    Item('Add Comment', 'new_comment_idea', args=[id]),
    CopyItem(f'Comments ({len(idea.comments)})')
]

def comment_string(comment, staff=player.is_staff, Item=Item, util=util):
    text = util.truncate(comment.text)
    return Item(f'#{comment.id}: {comment.owner.get_name(staff)}: {text} ({comment.created.ctime()})', 'view_comment_idea', args=[comment.id])

page = Page(IdeaComment.query(idea_id=id).order_by(IdeaComment.created.desc()), start=start)
items.extend(page.get_items(comment_string, __name__, id))
items.append(Item('Back', 'view_idea', args=[id]))
menu(con, Menu('Comments', items, escapable=True))
