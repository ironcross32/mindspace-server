def entry_string(entry, staff=player.is_staff, CopyItem=CopyItem):
    return CopyItem(f'{entry.owner.get_name(staff)}: {entry.text} ({entry.created.ctime()})')

if a:
    start = a[0]
else:
    start = 0
items = [LabelItem('Changelog')]
if player.is_staff:
    items.append(Item('Add Change', 'add_change'))
items.extend(
    Page(
        ChangelogEntry.query().order_by(ChangelogEntry.created.desc()), start=start
    ).get_items(entry_string, __name__)
)
menu(con, Menu('Changelog Entries', items, escapable=True))
