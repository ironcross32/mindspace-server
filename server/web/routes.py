"""The web server."""

import os
import os.path
from twisted.web.static import File
from werkzeug import abort
from .app import app
from .renderer import render_template
from .forms import LoginForm
from ..db import HelpTopic, HelpKeyword, Rule, Credit


@app.route('/')
def index(request):
    """Home page."""
    return render_template(request, 'index.html')


@app.route('/sounds/', branch=True)
def sounds(request):
    """Return the sounds directory."""
    return File('sounds')


@app.route('/static/', branch=True)
def static(request):
    """Return the static directory."""
    return File('static')


@app.route('/help/')
def help_index(request):
    """Return the main help page."""
    return render_template(
        request, 'help.html', page=None,
        pages=HelpTopic.query().all(),
        keywords=HelpKeyword.query().all()
    )


@app.route('/help/keyword/<id>/')
def help_keyword(request, id):
    """Return help topics for a specific keyword."""
    keyword = HelpKeyword.query(id=id).first()
    if keyword is None:
        return abort(404)
    return render_template(
        request, 'help.html', pages=keyword.help_topics, keywords=None,
        page=None
    )


@app.route('/help/<id>/')
def help_page(request, id):
    """Return a specific help page."""
    page = HelpTopic.query(id=id).first()
    if page is None:
        return abort(404)
    return render_template(
        request, 'help.html', page=page, keywords=page.keywords, pages=None
    )


@app.route('/rules/')
def rules(request):
    """Return the main rule page."""
    return render_template(request, 'rules.html', rules=Rule.query().all())


@app.route('/rules/<id>/')
def rule(request, id):
    """Return a specific rule."""
    rule = Rule.query(id=id).first()
    if rule is None:
        return abort(404)
    else:
        return render_template(request, 'rule.html', rule=rule)


@app.route('/login/')
def login(request):
    form = LoginForm()
    return render_template(request, 'login.html', form=form)


@app.route('/credits/')
def credits(request):
    """Show credits."""
    return render_template(request, 'credits.html', credits=Credit.query())


@app.route('/client/')
def client(request):
    """Show the web-based client."""
    name = os.path.join('static', 'js', 'client.js')
    stat = os.stat(name)
    stamp = stat.st_mtime
    return render_template(request, 'client.html', stamp=stamp)
