items = [Item('Rules', None)]
for rule in Rule.query().order_by(Rule.name):
    text = f'{rule.get_name(player.is_staff)}: {rule.get_description()}'
    items.append(CopyItem(text))
if player.is_admin:
    items.append(LabelItem('Actions'))
    for name in ('add', 'edit', 'delete'):
        items.append(Item(f'{name.title()} Rule', f'{name}_', args=['Rule']))
menu(con, Menu('Game Rules', items, escapable=True))