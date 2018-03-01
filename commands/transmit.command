
def parse_args(id, message=None):
    return (id, message)

id, message = parse_args(*a)

c = s.query(CommunicationChannel).get(id)
if c is None:
    player.message('Invalid channel.')
elif message is None:
    get_text(con, c.get_name(player.is_builder or player.is_admin), __name__, args=[c.id])
elif not message:
    player.message('You transmit nothing.')
else:
    s.add(c.transmit(player, message))