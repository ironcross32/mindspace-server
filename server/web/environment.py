"""Jinja2 environment."""

from jinja2 import Environment, FileSystemLoader
from markdown import markdown
from ..util import english_list, format_timedelta, pluralise, percent

environment = Environment(loader=FileSystemLoader('templates'))


def render_form(form):
    """Render a form to save on typing."""
    strings = []
    if form.errors:
        strings.extend(['<h2>Errors</h2>', '<dl>'])
        for name, errors in form.errors.items():
            strings.extend([f'<dt>{name}</dt>', '<dd>', '<ol>'])
            for error in errors:
                strings.append(f'<li>{error}</li>')
            strings.extend(['</ol>', f'</dd>'])
    for field in form:
        label = field.label
        strings.append(f'<p>{label} {field}')
    return '\n'.join(strings)


for func in [
    english_list, format_timedelta, pluralise, percent, markdown, render_form
]:
    environment.filters[func.__name__] = func
