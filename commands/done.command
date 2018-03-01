if not a or not isinstance(a[-1], str):
    text = 'Done.'
else:
    text = a[-1]
message(con, text)