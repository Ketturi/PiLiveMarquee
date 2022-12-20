#!/usr/bin/python3

import os
import sys
import time
from threading import Thread, current_thread

import sdl2.ext

from wsgiref.simple_server import make_server
import falcon
import json

def set_rom_name(emulator, romname):
    try:
        response = RESOURCES.get_path(romname+".png")
        sprite = factory.from_image(RESOURCES.get_path(romname+".png"))
    except KeyError:
        response = "No such image file found as: " + romname +".png"
        emupath = apppath + "\\resources\\" + emulator + "\\"
        try:
            sprite = factory.from_image(emupath + "default.png")
        except KeyError:
            sprite = factory.from_image(RESOURCES.get_path("startimage.png"))
    spriterenderer.render(sprite)
    window.refresh()
    return response

class helpPageResource:
    
    def on_get(self, req, resp):
        resp.content_type = falcon.MEDIA_TEXT
        resp.text = ('This is LiveMarquee API. Use GET requests on:\n'+
        req.url + 'marquee/<emulator>/<romname>\n\n'+
        req.url + 'quit' + '   - shuts down the server application\n'+ 
        req.url + 'reload' + ' - forcibly restarts server application\n'
        )

class romNameResource:
    def on_get(self, req, resp, emulator, romname):
        print(emulator + ":" + romname)
        if emulator == "":
            romname= "startimage"
        if romname == "":
            romname = "default"

        result = set_rom_name(emulator, romname)
        print(result)
        resp.text = result
        resp.status = falcon.HTTP_200
    
class quitResource:
    def on_get(self, req, resp):
        resp.media = ('Closing server')
        global running 
        running = False
       
class reloadResource:
    def on_get(self, req, resp):
        resp.media = ('Reloading program')
        os.execl(sys.executable, sys.executable, *sys.argv)

if __name__ == '__main__':
# Create a resource container. 
    apppath = os.path.dirname(os.path.abspath(__file__))
    RESOURCES = sdl2.ext.Resources(os.path.join(apppath, "resources"))

    sdl2.ext.init()
   
    window = sdl2.ext.Window("Marquee", size=(480, 800), flags=sdl2.SDL_WINDOW_BORDERLESS)
    sdl2.mouse.SDL_ShowCursor(0)
    window.show()

    factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
    sprite = factory.from_image(RESOURCES.get_path("startimage.png"))

    spriterenderer = factory.create_sprite_render_system(window)
    spriterenderer.render(sprite)
    print("SDL2 started")

    app = falcon.App()
    app.add_route('/', helpPageResource())
    app.add_route('/marquee/{emulator}/{romname}', romNameResource())
    app.add_route('/quit', quitResource())
    app.add_route('/reload', reloadResource())

    def http_server():
        print("HTTP server thread started")
        with make_server('', 80, app) as httpd: 
            #httpd.serve_forever()
            global running
            while running:
                httpd.handle_request()
            print("HTTP server stopped")
            httpd.shutdown()
            httpd.socket.close() 

    thread = Thread(target=http_server, name="http_server")
    thread.daemon = True
    thread.start()
    print("HTTP server started") 
    
    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
        window.refresh()
        time.sleep(0.1)
    print("bye!")
    sdl2.ext.quit()
    sys.exit()