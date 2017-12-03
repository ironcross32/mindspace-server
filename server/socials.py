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


@factory.suffix('ss', 'your')
def your(obj, suffix):
    """"your" or "name's"."""
    return ('your', f"{obj.get_name()}'s")


@factory.suffix('he', 'she', 'it', 'subjective')
def subjective(obj, suffix):
    """"you" or the object's subjective pronoun."""
    return ('you', obj.get_gender().subjective)


@factory.suffix('him', 'her', 'o', 'objective')
def objective(obj, suffix):
    """"you" or the object's objective pronoun."""
    return ('you', obj.get_gender().objective)


@factory.suffix('his', 'its', 'p', 'pa')
def possessive_adjective(obj, suffix):
    """"your" or the object's possessive adjective."""
    return ('your', obj.get_gender().possessive_adjective)


@factory.suffix('hers', 'pn')
def possessive_noun(obj, suffix):
    """"your" or the object's possessive noun. Exactly the same as the your and
    ss suffixes."""
    return your(obj, suffix)


@factory.suffix('himself', 'herself', 'itself', 'r', 'reflexive')
def reflexive(obj, suffix):
    """"yourself" or the object's reflexive pronoun."""
    return ('yourself', obj.get_gender().reflexive)
