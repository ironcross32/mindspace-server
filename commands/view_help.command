if a:
    id = a[0]
    topic = s.query(HelpTopic).get(id)
    if topic is None:
        player.message('Invalid help topic.')
    else:
        items=[
            Item(topic.get_name(player.is_builder), 'copy', args=[topic.get_name(player.is_builder)]),
            Item(f'URL', 'show_url', args=[topic.get_name(player.is_builder), f'http://code-metropolis.com:{server_options().web_port}{topic.url}'])
        ]
        for line in topic.text.splitlines():
            items.append(Item(line, 'copy', args=[line]))
        items.append(Item(f'Keywords: {util.english_list(topic.keywords, key=lambda thing, staff=player.is_staff: thing.get_name(staff))}.', None))
        if topic.related_topics:
            for t in topic.related_topics:
                items.append(Item(t.get_name(player.is_builder), __name__, args=[t.id]))
        else:
            items.append(Item('No related topics.', None))
        menu(con, Menu('View Help Topic', items, escapable=True))
else:
    items = [Item('Help Topics', None)]
    kwargs = {}
    if not player.is_builder:
        kwargs['builder'] = False
    if not player.is_admin:
        kwargs['admin'] = False
    for topic in HelpTopic.query(**kwargs):
        items.append(Item(topic.get_name(player.is_staff), __name__, args=[topic.id]))
    menu(con, Menu('Select Help Topic', items, escapable=True))