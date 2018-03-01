def comment_string(comment, staff=player.is_staff, Item=Item, util=util):
    text = util.truncate(comment.text)
    return Item(f'#{comment.id}: {comment.owner.get_name(staff)}: {text} ({comment.created.ctime()})', 'view_comment_idea', args=[comment.id])

def parse_args(id, start=0):
    return (id, start)
id, start = parse_args(*a)
obj = Object.get(id)
valid_object(player, obj)
q = IdeaComment.query(owner_id=id).order_by(IdeaComment.created.desc())
page = Page(q, start=start)
items = [LabelItem(f'Comments by {obj.get_name(player.is_staff)}')]
items.extend(page.get_items(comment_string, __name__, id))
menu(con, Menu('Comments', items, escapable=True))
