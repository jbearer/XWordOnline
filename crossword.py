import urllib3
import certifi
import pyglet
from grid import Grid
from pyglet.gl import *

class Crossword(pyglet.window.Window):
    '''
    Class representing a crossword puzzle

    Private members:
    _grid: a grid object
    _acrossClues
    _downClues
    '''

    def __init__(self, url):
        '''
        Load a crossword puzzle from the specified url
        The url must lead to an html page formatted as those at 
        http://www.theguardian.com/crosswords/
        '''

        super(Crossword, self).__init__(resizable = True, width=1000, height = 750)

        http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED', # Force certificate check.
            ca_certs=certifi.where()  # Path to the Certifi bundle.
        )
        response = http.request('GET', url) 

        f = open('C:/Users/Jeb/Desktop/xword-test.txt', 'w')
        f.write(response.data)
        f.close()

        #self._grid, self._acrossClues, self._downClues = self.parseHTML(response.data)
        self._grid = Grid(15)
        self._grid.x = self.width - self._grid.width
        self._grid.y = self.height - self._grid.height

    def parseHTML(self, html):
        '''
        Take an html page formatted as those at
        http://www.theguardian.com/crosswords/ and parse the data to
        return the various components of a crossword. Returns a tuple of the form
        (grid, across clues, down clues).

        Grid is a grid object
        Clues are lists of tuples of the form (n, t), where n is the number of the clue
        and t is the text of the clue
        '''

        pass

    def on_mouse_release(self, x, y, button, modifiers):
        print 'click in xword'
        if self._grid.hit_test(x, y):
            self._grid.on_mouse_release(x, y, button, modifiers)
        else:
            self._grid.setFocusedSquare(None)

    def on_key_press(self, symbol, modifiers):
        self._grid.on_key_press(symbol, modifiers)

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)

        pyglet.gl.glClearColor(1.0,1.0,1.0,1.0)
        self.clear()

        self._grid.x = width - self._grid.width
        self._grid.y = height - self._grid.height
        self.on_draw()

    def on_draw(self):
        glViewport(0,0,self.width,self.height);
        glMatrixMode(GL_PROJECTION);
        glLoadIdentity();
        gluOrtho2D(0,self.width,0,self.height);
        glMatrixMode(GL_MODELVIEW);
        glLoadIdentity();

        pyglet.gl.glClearColor(1.0,1.0,1.0,1.0)
        self.clear()

        self._grid.draw(self)