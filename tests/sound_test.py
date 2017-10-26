import os
import os.path
from shutil import rmtree
from server.sound import get_sound, sounds_dir


def test_file():
    path = os.path.join(sounds_dir, 'test.wav')
    with open(path, 'w') as f:
        f.write('Pretend wavefile.')
    s = get_sound('test.wav')
    assert s.path == path
    os.remove(path)


def test_dir():
    p1 = os.path.join(sounds_dir, 'testing')
    p2 = os.path.join(p1, 'something')
    if os.path.isdir(p1):
        rmtree(p1)
    os.makedirs(p2)
    file = os.path.join(p2, 'file.wav')
    with open(file, 'w') as f:
        f.write('Pretend wave file.')
    s = get_sound(p1)
    assert s.path == file
    rmtree(p1)
