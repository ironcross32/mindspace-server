loc = player.location
size = ' X '.join([str(int(x)) for x in loc.size])
objects = 0
exits = 0
players = 0
for obj in loc.objects:
    if obj is player:
        continue
    elif obj.is_exit:
        exits += 1
    elif obj.is_player:
        players += 1
    else:
        objects += 1
player.message(f'Size: {size}.\nObjects: {objects}.\nPlayers: {players}.\nExits: {exits}.')