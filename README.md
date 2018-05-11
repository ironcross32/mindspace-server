# mindspace-server
The Mindspace server

## Description
Mindspace is what I am calling an audio-first virtual reality. This is because it primarily uses audio to represent things to the player, with MUD-style text so that it is more obvious what is going on.

I am writing Mindspace to be an SF game, with starships and all the other minutiae that entails. It is not limited to this model though, as you could easily add or subtract things from the database to include whatever database tables you required for your game. Ultimately, as long as you don't break the `load_db` function you can do whatever you like.

## Connecting
I am running my own Mindspace instance on [mindspace.site](http://mindspace.site/client), but you can of course run your own.

Connection is done through a standard web browser: At this time I know that Firefox and Chrome have full support, with Apple Safari lagging slightly behind with no support for the APIs which allow players to send voice data.

Of course if you try another web browser and it works, drop me a line. Better still, if you manage to get other browsers working, please feel free to submit a pull request with the changes to `static/js/client.js` to make the magic happen.

## Running your own instance
If you wish to run your own instance of the Mindspace server, you will need a couple of things:

* A server that you can open 3 ports on and access from your client machine.
* An SSL certificate for this server. Help on how to generate these can be found [here](https://stackoverflow.com/questions/10175812/how-to-create-a-self-signed-certificate-with-openssl).
* Python >= 3.6.5. I always use the latest version so if you do that you should be good to go.
* Probably a vritualenv.
* All the dependencies installed (`pip install -Ur requirements.txt`).

Occasionally I dump a minimal version of the database I am using. This is my database with only credits, actions and hotkeys included. You can use the `extract-minimal-database.py` script for this purpose.

To run the server, try `python main.py -h`. Alternatively you can use the `start.sh` script which runs git pull before starting the server. Your certificate files are assumed to be in the certs directory.

## Problems
If you have any problems using Mindspace please either [submit an issue](https://github.com/chrisnorman7/mindspace-server/issues/new), or get in touch with me via [Twitter](https://twitter.com/chrisnorman7).