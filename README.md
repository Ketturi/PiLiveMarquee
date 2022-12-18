# PiLiveMarquee
 App for showing arcade art on separate display using RPi and HTTP api

## HTTP API

Set image to be shown on the screen:
http://"hostname"/marquee/"emulator"/"romname"
where emulator and romname tags are send by attract mode front-end.
If image file corresponding to romname is not found, 
default image for the emulator given is shown.

Exit application:
http://"hostname"/quit 
Shuts down screen server gracefully, so that service manager can restart it

Forcibly reload application:
http://"hostname"/reload
Application is forcibly killed and relaunched by os services.

## Images

Put PNG image files under resources directory. Image file can be located anywhere,
so long as it is named same as the romname for the game. Application builds resource tree when launched.

Example directory structure:
Application Directory
	LiveMarquee.py
	resources/
		MAME
			flyer/
				tempest.png
			instruction/
				invaders.png	<-API example: http://localhost/marquee/MAME/invaders
			default.png 		<-This is shown, if romname given does not match any files on resources, and emulator is MAME
		NES
			default.png
		SNES
			default.png
		startupimage.png 		<-This is shown at the start of the application before image is set through API
	
## Installation

Use minimal installation of raspbian. Application is made
to be used with KMS, so no graphical environment or X11 is needed.
Preferably set static network address, and directly connect to machine
running the GroovyArcade OS / Attract Mode frontend

Clone git to raspberry pi's home directory:

Install python libraries from requirements.txt:

Create service for launcing application:
