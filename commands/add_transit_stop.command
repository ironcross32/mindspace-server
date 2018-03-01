check_builder(player)

if a:
    id = a[0]
    route = TransitRoute.get(id)
    valid_object(player, route)
    stop = TransitStop(location_id=player.location_id, transit_route_id=route.id)
    stop.coordinates = player.coordinates
    s.add(stop)
    s.commit()
    player.message('Stop added.')
else:
    items = [Item('Select Transit Route', None)]
    for route in TransitRoute.query():
        items.append(Item(route.get_name(True), __name__, args=[route.id]))
    menu(con, Menu('Select Transit Route', items, escapable=True))