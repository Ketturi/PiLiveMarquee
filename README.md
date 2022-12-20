
# PiLiveMarquee
 App for showing arcade art on separate display using RPi and HTTP api

## HTTP API

Set image to be shown on the screen:
`http://<hostname>/marquee/<emulator>/<romname>`
where emulator and romname tags are send by attract mode front-end.
If image file corresponding to romname is not found, 
default image for the emulator given is shown.

Exit application:
`http://<hostname>/quit`
Shuts down screen server gracefully, so that service manager can restart it

Forcibly reload application:
`http://<hostname>/reload`
Application is forcibly killed and relaunched by os services.

## Images

Put PNG image files under resources directory. Image file can be located anywhere,
so long as it is named same as the romname for the game. Application builds resource tree when launched.

Example directory structure:
```
Application Directory
  └───LiveMarquee.py
      resources/
      ├───MAME/
      │   ├───flyer/
      │   │   └───tempest.png
      │   ├───instruction/
      │   │   └───invaders.png <-API example: http://localhost/marquee/MAME/invaders
      │   └───default.png      <-This is shown, if romname given does not match any files on resources, and emulator is MAME
      ├───NES/
      │   └───default.png
      ├───SNES/
      │   └───default.png
      └───startupimage.png     <-This is shown at the start of the application before image is set through API
```
	
## Installation

Use minimal installation of raspbian lite. Application is made
to be used with KMS, so no graphical environment or X11 is needed.
Preferably set static network address, and directly connect to machine
running the GroovyArcade OS / Attract Mode frontend

###Add optimizations to RPi config.txt:
```
# Enable DRM VC4 V3D driver
dtoverlay=vc4-fkms-v3d,nocomposite,noaudio
#dtoverlay=vc4-kms-dsi-7inch
max_framebuffers=2

# Disable compensation for displays with overscan
disable_overscan=1

# Disable Bluetooth
dtoverlay=disable-bt

# Disable WiFi
dtoverlay=disable-wifi

# Disable nags n' splash
disable_splash=1
avoid_warnings=1

#Overclock SD card for speed
dtoverlay=sdhost,overclock_50=100

# No boot delay
boot_delay=0

#No HDMI
hdmi_blanking=2

#Disable leds
#dtparam=act_led_trigger=none
#dtparam=act_led_activelow=on

gpu_mem=128
```

Make RPi boot silently and rotate display by adding following
to the cmdline.txt
```
quiet splash logo.nologo vt.global_cursor_default=0 loglevel=0 fbcon=rotate:3
```

###Compile SDL2 with KMSDRM support: 
Currently, libsdl2 from raspbian repository does not support kmsdrm.
SDL2 has to be compiled, if x11 is not used.
Install needed libraries and build environment:
`sudo apt install -y build-essential git libasound2-dev libsamplerate0-dev libibus-1.0-dev libdbus-1-dev libudev-dev libgles2-mesa-dev libdrm-dev libgbm-dev`

`wget https://github.com/libsdl-org/SDL/archive/refs/tags/release-2.0.22.tar.gz`
`tar -zxf release-2.0.22.tar.gz`
`cd SDL-release-2.0.22`
`CFLAGS='-mfpu=neon -mtune=cortex-a72 -march=armv8-a' ./configure --prefix=/usr --disable-video-x11 --disable-video-wayland --disable-video-rpi --disable-rpath --disable-esd --disable-oss --disable-sndio --disable-pulseaudio --disable-nas --enable-video-kmsdrm --enable-arm-neon`
`make -j4`
`sudo make install`

###Clone git to raspberry pi's home directory:
`wget https://github.com/Ketturi/PiLiveMarquee/archive/main.tar.gz`
`tar -zxf main.tar.gz`

###Install python libraries from requirements.txt:
`cd PiLiveMarquee`
`sudo pip install -r requrements.txt`

###Create service for launching application:
```
chmod +x LiveMarquee.py

sudo cp livemarquee.service /lib/systemd/system/livemarquee.service
sudo systemctl daemon-reload
sudo systemctl enable livemarquee.service
sudo systemctl start livemarquee.service
```
