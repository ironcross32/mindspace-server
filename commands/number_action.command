def on_error(player, e):
    """There was an error with the social."""
    player.message(f'There was a problem with your social: {e}')

def parse_args(number, modifiers, id=None):
    return (number, modifiers, id)

number, modifiers, id = parse_args(*a)
for name in ('scrolllock', 'numlock'):
    if name in modifiers:
        modifiers.remove(name)
modifiers = sorted(modifiers)
if number:
    number -= 1
    if modifiers:
        try:
            social = player.socials[number]
        except IndexError:
            if 'ctrl' in modifiers:
                social = Social(object_id=player.id, name='Untitled Social', first='', second='', third='')
                s.add(social)
                s.commit()
            else:
                player.message(f'No social at position {number + 1}.')
                end()
        if modifiers == ['alt']:
            try:
                player.do_social(social.first)
            except SocialsError as e:
                on_error(player, e)
        elif modifiers == ['ctrl']:
            f = ObjectForm(social, 'edit_', title='Edit Social', args=['Social', social.id], cancel='Cancel')
            form(con, f)
        elif modifiers == ['shift']:
            if id is None:
                items = [Item(f'Select Object for {social.get_name(player.is_staff)}', None)]
                for obj in player.get_visible():
                    items.append(Item(obj.get_name(player.is_staff), __name__, args=[number + 1, modifiers, obj.id]))
                menu(con, Menu('Social', items, escapable=True))
            else:
                obj = player.get_visible(Object.id == id).first()
                if obj is None:
                    player.message('Invalid object.')
                else:
                    if obj is player:
                        text = social.second
                    else:
                        text = social.third
                    try:
                        player.do_social(text, _others=[obj], _channel='social')
                    except SocialsError as e:
                        on_error(player, e)
    else:
        try:
            channel = player.communication_channels[number]
            con.handle_command('transmit', channel.id)
        except IndexError:
            player.message(f'No channel at position {number + 1}.')
else:
    if not modifiers:
        items = [Item('Communication Channels', None)]
        for c in player.possible_communication_channels():
            if player in c.listeners:
                items.append(Item(c.get_name(player.is_staff), 'transmit', args=[c.id]))
        menu(con, Menu('Transmit Message', items, escapable=True))
    elif modifiers == ['shift']:
        items = [Item('Social Suffixes.', None)]
        for string in (
            'Format: %[index[formatter]]',
            'Your player is always first in the list, so %1.',
            'In the second form of the social your player is also in the second position, so %2.',
            'In the third form the object you choose is in the second position.',
            'You can put the formatter in upper case to capitalise the first letter of the resulting string.',
            'For example:',
            '%1N should be used at the start of each social string.'
        ):
            items.append(Item(string, 'copy', args=[string]))
        items.append(Item('Suffixes:', None))
        for suffix in socials.get_suffixes():
            names = util.english_list(suffix.names)
            docstring = suffix.func.__doc__
            text = f'{names}: {docstring}'
            items.append(Item(text, 'copy', args=[text]))
        items.append(Item('emote-utils on Github', 'show_url', args=['emote-utils', 'https://github.com/chrisnorman7/emote-utils']))
        menu(con, Menu('Socials Help', items, escapable=True))
    elif modifiers == ['ctrl']:
        if id:
            try:
                other = Object.first()
                strings = socials.get_strings(id, [player, other])
            except SocialsError as e:
                player.message(str(e))
                con.handle_command(__name__, number, modifiers)
                end()
            l = [
                f'Social string: {id}',
                f'You would see: {strings[0]}',
                f'The second object would see ({other.get_name(player.is_staff)} in this case): {strings[1]}',
                f'Everyone else will see: {strings[2]}'
            ]
            items = []
            for string in l:
                items.append(Item(string, 'copy', args=[string]))
            items.append(Item('Try again', __name__, args=[number, modifiers]))
            menu(con, Menu('Social String Example', items, escapable=True))
        else:
            get_text(con, 'Enter a social string to test or press escape to exit', __name__, args=[number, modifiers])