"""Provides decorators to check permissions."""


def required_login(func=None, builder=None, admin=None):
    """Require a user to login and have the provided credentials."""

    def decorate(func):
        def inner(request, *args, **kwargs):
            return func(request, *args, **kwargs)
        return inner
    if func is None:
        return decorate
    else:
        return decorate(func)
