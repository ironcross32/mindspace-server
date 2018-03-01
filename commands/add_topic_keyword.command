check_admin(player)

def parse_args(keyword_id=None, topic_id=None):
    return (keyword_id, topic_id)

keyword_id, topic_id = parse_args(*a)
if keyword_id is None:
    items = [Item('Keywords', None)]
    for keyword in HelpKeyword.query():
        items.append(Item(keyword.get_name(True), __name__, args=[keyword.id]))
    menu(con, Menu('Select Keyword', items, escapable=True))
elif topic_id is None:
    items = [Item('Topic', None)]
    for topic in HelpTopic.query():
        items.append(Item(topic.get_name(True), __name__, args=[keyword_id, topic.id]))
    menu(con, Menu('Select Topic', items, escapable=True))
else:
    keyword = HelpKeyword.get(keyword_id)
    topic = HelpTopic.get(topic_id)
    for thing in (keyword, topic):
        valid_object(player, thing)
    topic.keywords.append(keyword)
    s.add(topic)
    player.message(f'Added keyword {keyword.get_name(True)} to topic {topic.get_name(True)}.')