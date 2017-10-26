"""Provides various form classes for use with the web server."""

from wtforms import Form, TextField, PasswordField
from wtforms.validators import required


class LoginForm(Form):
    username = TextField(validators=[required])
    password = PasswordField(validators=[required])
