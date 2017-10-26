from server.forms import Form, Label, Field


def test_label():
    l = Label('Test')
    assert l.text == 'Test'
    assert l.dump() == dict(type=Label.__name__, values=[l.text])


def test_field():
    f = Field('test', 'test')
    assert f.title == 'Test'
    assert f.dump() == dict(
        type=Field.__name__, values=[f.name, f.value, 'str', f.title, f.hidden]
    )


def test_form():
    f = Form('test', [Field('test', 'test')], 'test')
    assert f.title == 'test'
    assert len(f.fields) == 1
    assert f.command == 'test'
    assert isinstance(f.fields[0], Field)
    assert f.ok == 'OK'
    assert f.cancel is None
    assert f.dump() == (
        f.title, [f.fields[0].dump()], f.command, f.args, f.kwargs, f.ok,
        f.cancel
    )
