id, value = a
check_perms(player, admin=True)
account = s.query(Player).filter_by(id=id).first()
if account is None:
    message(con, 'Invalid account.')
else:
    account.locked = value
    s.add(account)
    if account.locked:
        obj_con = account.object.get_connection()
        if obj_con is not None:
            obj_con.set_locked(value)
    message(con, f'Account {"locked" if account.locked else "unlocked"}.')
