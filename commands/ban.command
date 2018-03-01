check_admin(player)
ip = a[0]
if BannedIP.query(ip=ip).count():
    player.message('That IP address is already banned.')
else:
    s.add(BannedIP(ip=ip, owner_id=player.id))
    logger.info('IP address %s has been banned by %s.', ip, player.get_name(True))
    player.message(f'All future connections from {ip} will be blocked.')
