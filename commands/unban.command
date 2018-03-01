check_admin(player)
ip = a[0]
q = BannedIP.query(ip=ip)
c = q.delete()
if c:
    logger.info('IP address %s has been unbanned by %s.', ip, player.get_name(True))
    player.message(f'{c} {util.pluralise(c, "row")} affected.')
else:
    player.message('That IP address is not banned.')