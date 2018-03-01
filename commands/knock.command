obj = Object.get(*a)
valid_object(player, obj)
if obj.coordinates != player.coordinates or obj.location != player.location:
    player.message('You cannot possibly knock on that.')
else:
    player.do_social(obj.knock_msg, _others=[obj])
    if obj.knock_sound:
        sound = get_sound(obj.knock_sound)
        obj.sound(sound)
        if obj.is_exit:
            other_side = obj.exit.get_other_side()
            if other_side is not None:
                other_side.sound(sound)
        if obj.transit_route is not None and obj.transit_route.room is not None:
            for person in obj.transit_route.room.objects:
                person.sound(sound, private=True)