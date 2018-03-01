def parse_args(id, start=0):
    return (id, start)
id, start = parse_args(*a)
channel = CommunicationChannel.get(id)
valid_object(player, channel)
if not channel.messages:
    player.message('Nothing to display.')
    end()
items = [LabelItem(f'{channel.get_name(player.is_staff)} History ({len(channel.messages)})')]

def message_string(message, CopyItem=CopyItem, now=datetime.datetime.utcnow(), staff=player.is_staff, util=util):
    sender = message.owner.get_name(staff)
    when = now - message.created
    when = util.format_timedelta(when)
    return CopyItem(f'{sender} ({when} ago): {message.text}')

page = Page(CommunicationChannelMessage.query(channel_id=id).order_by(CommunicationChannelMessage.created.desc()), start=start)
items.extend(page.get_items(message_string, __name__, id))
menu(con, Menu('Communication History', items, escapable=True))