"""The socials framework."""

from emote_utils import SocialsFactory

factory = SocialsFactory()


@factory.suffix('name', 'n')
def name(obj, suffix):
    """"you" or name."""
    return 'you', obj.get_name()


@factory.suffix('s')
def get_s(obj, suffix):
    """"" or "s"."""
    return '', 's'


@factory.suffix('e', 'es')
def get_es(obj, suffix):
    """"" or "es"."""
    return '', 'es'


@factory.suffix('y', 'ies')
def get_y(obj, suffix):
    """"y" or "ies"."""
    return 'y', 'ies'


@factory.suffix('are', 'is')
def are(obj, suffix):
    """"are" or "is"."""
    return ('are', 'is')
