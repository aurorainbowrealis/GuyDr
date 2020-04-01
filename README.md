# GuyDR

A client to a geolocation based app.
Developed using Python, Flask, XMPP and Sockets.

This is NOT final, and a lot of work needs to be done, specially on the front end.

If you are a company and is interested in this work, please get in touch, I have a data analytics advanced version of this client.
I have released only a simplified version of this client, as the full version provides too much information that could expose users.

Please use this client for on an ethical manner. 
Avoid using this to create bots and other similar paraphernalia.
Have fun with it.

Contributions and improvements are always welcome.

## Dependencies:
- Flask
- Python SocketIO (not flask-socketio)
- SliXMPP
- PyGeoHash
- Waitress
- Pandas 
- Numpy
- Jinja2

## Instructions

1. I can't give you my device information nor keys. You will have to fill the files in *./conf* by yourself.
2. Go to *app.py* and insert a login and password
3. Go to *gdr_bot* and insert a valid geohash
4. Run *app.py* by issuing:

[//]: # (Hello)

    python app.py

or run using waitress

    waitress-serve --listen 0.0.0.0:8000 --call "app:create_app"


## Credits:

Sound Fx:
[SpiceProgram](https://freesound.org/people/SpiceProgram/)
		
Chat CSS which inspired me:
		[Sunil Rajput] (https://bootsnipp.com/snippets/1ea0N)

Contributors: [@fanti1](https://github.com/fanti1)
