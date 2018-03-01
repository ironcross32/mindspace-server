obj = s.query(Object).get(a[0])
if obj is not None and obj.location is player.location:
    obj.identify(con)