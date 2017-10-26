name = a[0]
key = s.query(Hotkey).filter_by(name=name).first()
if key is not None:
    run_program(con, s, key)
