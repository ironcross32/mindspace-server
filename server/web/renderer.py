"""Provides functions for rendering templates."""

from platform import python_version
from klein import __version__
from .environment import environment


def render(request, template, *args, **kwargs):
    """Return a rendered string."""
    return template.render(
        *args,
        request=request,
        python_version=python_version(),
        klein_version=__version__,
        **kwargs
    )


def render_string(request, string, *args, **kwargs):
    """Render a string with args and kwargs."""
    return render(request, environment.from_string(string), *args, **kwargs)


def render_template(request, name, *args, **kwargs):
    """Render a template from the templates directory."""
    return render(request, environment.get_template(name), *args, **kwargs)
