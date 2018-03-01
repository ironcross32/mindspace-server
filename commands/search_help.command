if a:
    term = a[0]
    results = HelpTopic.search(term)
    items = [Item('Search Results', None)]
    if not results:
        player.message(f'No results found for "{term}".')
    else:
        for result in results:
            items.append(Item(result.get_name(player.is_builder), 'view_help', args=[result.id]))
        menu(con, Menu('Help', items, escapable=True))
else:
    get_text(con, 'Enter search terms', __name__)