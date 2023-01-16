#!/usr/bin/python3

import os, sys, logging, time
from threading import Thread, current_thread

import sdl2.ext

logging.basicConfig(stream=sys.stderr, level=logging.WARNING) #Change WARNING to DEBUG, if needed

def set_rom_name(emulator, romname):
    response = falcon.HTTP_500 #Things are bad, if this is returned for some reason
    try:
        sprite = factory.from_image(emulatos_dict[emulator].get_path(romname+".png"))
        response = falcon.HTTP_OK
    except KeyError: #Error is expected, not every game will have nice art. Try just showing default image.
        logging.debug("No such image file found as: " + romname +".png")
        try:
            response = falcon.HTTP_NO_CONTENT
            sprite = factory.from_image(os.path.join(resourcespath, emulator, "default.png"))
        except: #Ok, you are missing proper default emulator image
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
        logging.debug(" ".join([emulator, ":", romname]))
        if emulator == "":#Should not be empty, but accidents happen
            romname= "startimage"
            emulator == "AMUI"
        if romname == "":#Show default image if some reason left empty
            romname = "default"

        result = set_rom_name(emulator, romname) #This sets the image on screen from parameters
        logging.debug(result)
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
    resourcespath = os.path.join(apppath, "resources")
    emulatos_dict = {}
    RESOURCES = sdl2.ext.Resources(resourcespath)
    #Initialize SDL2 and create window
    sdl2.ext.init()
   
    window = sdl2.ext.Window("Marquee", size=(800, 480), flags=sdl2.SDL_WINDOW_BORDERLESS)
    sdl2.mouse.SDL_ShowCursor(0) #Hides the anoying mouse cursor
    window.show()
    #Create sprite engine and populate first image to be shown
    factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
    sprite = factory.from_image(RESOURCES.get_path("startimage.png"))
   
    spriterenderer = factory.create_sprite_render_system(window)
    spriterenderer.render(sprite)
    window.refresh()
    logging.debug("SDL2 started")
    
    #Add found subdirectories to list of emulators, and create resource tree with files in directiories
    for it in os.scandir(resourcespath):
        if it.is_dir():
            emulatos_dict[os.path.basename(os.path.normpath(it.path))] = sdl2.ext.Resources(it.path)

    from wsgiref.simple_server import make_server
    import falcon, re

    def imageHandler(req, resp, path):
        global resourcespath
        path = path.lstrip('/')
        ext = os.path.splitext(path)[1][1:]
        image_path = os.path.join(resourcespath, path)
        resp.content_type = 'image/' + ext
        resp.stream = open(image_path, 'rb')

    app = falcon.App()
    app.add_route('/', helpPageResource())
    app.add_route('/marquee/{emulator}/{romname}', romNameResource())
    app.add_sink(imageHandler, re.compile(r'/image(?P<path>/.*)'))
    app.add_route('/quit', quitResource())
    app.add_route('/reload', reloadResource())

    def http_server():
        logging.debug("HTTP server thread started")
        with make_server('', 8080, app) as httpd: 
            #Enter into http server loop
            global running
            while running:
                httpd.handle_request()
            logging.debug("HTTP server stopped")
            httpd.shutdown()
            httpd.socket.close() 

    running = True    
    thread = Thread(target=http_server, name="http_server")
    thread.daemon = True
    thread.start()
    logging.debug("HTTP server started") 
    
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break
        window.refresh()
        time.sleep(0.01) #Busywaitloop, make sure not to hog all cpu time
    logging.debug("bye!")
    sdl2.ext.quit()
    sys.exit()