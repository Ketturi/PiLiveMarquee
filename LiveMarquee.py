#!/usr/bin/python3

import os
import sys
import logging
import time
from threading import Thread, current_thread

import sdl2.ext

from wsgiref.simple_server import make_server
import falcon
import json

logging.basicConfig(stream=sys.stderr, level=logging.WARNING)

def set_rom_name(emulator, romname):
    response = ""
    try:
        if romname == "default":
            try:
                sprite = factory.from_image(os.path.join(apppath, "resources", emulator, "default.png"))
                response = falcon.HTTP_OK
            except:
                sprite = factory.from_image(RESOURCES.get_path("startimage.png"))
                response = falcon.HTTP_NOT_FOUND
        else:
            sprite = factory.from_image(RESOURCES.get_path(romname+".png"))
            response = falcon.HTTP_OK
    except KeyError:
        logging.debug("No such image file found as: " + romname +".png")
        try:
            response = falcon.HTTP_NO_CONTENT
            sprite = factory.from_image(os.path.join(apppath, "resources", emulator, "default.png"))
        except:
            response = falcon.HTTP_NOT_FOUND
            sprite = factory.from_image(RESOURCES.get_path("startimage.png"))
    spriterenderer.render(sprite)
    #window.refresh()
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
        logging.debug(emulator + ":" + romname)
        if emulator == "":
            romname= "startimage"
            emulator == "UI"
        if romname == "":
            romname = "default"

        result = set_rom_name(emulator, romname)
        logging.debug(result)
        #resp.text = result
        resp.status = result
    
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
   
    window = sdl2.ext.Window("Marquee", size=(800, 480), flags=sdl2.SDL_WINDOW_BORDERLESS)
    sdl2.mouse.SDL_ShowCursor(0)
    window.show()

    factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
    sprite = factory.from_image(RESOURCES.get_path("startimage.png"))

    spriterenderer = factory.create_sprite_render_system(window)
    spriterenderer.render(sprite)
    window.refresh()
    logging.debug("SDL2 started")

    app = falcon.App()
    app.add_route('/', helpPageResource())
    app.add_route('/marquee/{emulator}/{romname}', romNameResource())
    app.add_route('/quit', quitResource())
    app.add_route('/reload', reloadResource())

    def http_server():
        logging.debug("HTTP server thread started")
        with make_server('', 8080, app) as httpd: 
            #httpd.serve_forever()
            global running
            while running:
                httpd.handle_request()
            logging.debug("HTTP server stopped")
            httpd.shutdown()
            httpd.socket.close() 

    thread = Thread(target=http_server, name="http_server")
    thread.daemon = True
    thread.start()
    logging.debug("HTTP server started") 
    
    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
        window.refresh()
        time.sleep(0.01)
    logging.debug("bye!")
    sdl2.ext.quit()
    sys.exit()