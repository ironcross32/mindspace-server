id = a[0]
comment = IdeaComment.get(id)
valid_object(player, comment)
items = [
    LabelItem(f'Comment #{comment.id} on idea {comment.idea.get_name(player.is_staff)}'),
    Item(f'Author: {comment.owner.get_name(player.is_staff)}', 'author_comments_idea', args=[comment.owner_id]),
    Item(f'Idea: {comment.idea.get_name(player.is_staff)}', 'view_idea', args=[comment.idea_id]),
    CopyItem(f'Date: {comment.created.ctime()}')
]
for line in comment.text.splitlines():
    items.append(CopyItem(line))
items.append(Item('Back', 'comments_idea', args=[comment.idea_id]))
menu(con, Menu('Comment', items, escapable=True))
