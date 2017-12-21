"""Make a keyboard in a sensible way."""

import os.path
filename = os.path.join('templates', 'keyboard.html')

keyboard = [
    [
        'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11',
        'f12'
    ],
    ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '='],
    ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']'],
    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", '#'],
    ['tab', '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/'],
    [
        '.ctrl', '.shift', '.alt', 'backspace', 'delete', 'space', 'enter',
        '`', 'escape', 'home', 'end', ''
    ]
]

if __name__ == '__main__':
    s = ''
    for row in keyboard:
        assert len(
            row
        ) == 12, 'Rows must be formed of 12 keys, not %d.' % len(row)
        s += '<div class="row">\n'
        for key in row:
            s += '<div class="col-sm-1">\n'
            if key.startswith('.'):
                type = 'checkbox'
                cls = 'modifier'
                key = key[1:]
            else:
                type = 'button'
                cls = 'standard'
            key = key.upper()
            s += f'<input type="{type}" class="key-{cls}" value="{key}">'
            s += '\n</div>\n'
        s += '</div>\n'
    with open(filename, 'w') as f:
        f.write(s)
