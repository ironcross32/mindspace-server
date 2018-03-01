check_admin(player)

def parse_args(topic_id=None, keyword_id=None):
    return (topic_id, keyword_id)

topic_id, keyword_id = parse_args(*a)
if topic_id is None:
    items = [Item('Help Topics', None)]
    for topic in HelpTopic.query():
        items.append(Item(topic.get_name(True), __name__, args=[topic.id]))
    menu(con, Menu('Select Topic', items, escapable=True))
elif keyword_id is None:
    topic = HelpTopic.get(topic_id)
    valid_object(player, topic)
    if not topic.keywords:
        player.message(f'{topic.get_name(True)} has no keywords.')
    else:
        items = [Item('Keywords', None)]
        for keyword in topic.keywords:
            items.append(Item(keyword.get_name(True), __name__, args=[topic.id, keyword.id]))
        menu(con, Menu('Select Keyword', items, escapable=True))
else:
    topic = HelpTopic.get(topic_id)
    keyword = HelpKeyword.get(keyword_id)
    for thing in (topic, keyword):
        valid_object(player, thing)
    if keyword not in topic.keywords:
        player.message(f'{keyword.get_name(True)} is not in the list of keywords for {topic.get_name(True)}.')
    else:
        topic.keywords.remove(keyword)
        s.add(topic)
        player.message(f'Removed keyword {keyword.get_name(True)} from topic {topic.get_name(True)}.')