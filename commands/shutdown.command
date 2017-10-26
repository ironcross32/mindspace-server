player = con.get_player()
if player.is_admin:
        for connection in server.connections:
            message(connection, 'The server will shutdown in 5 seconds.')
            interface_sound(
                con, get_sound(os.path.join('notifications', 'shutdown.wav'))
            )
        reactor.callLater(5.0, reactor.stop)
