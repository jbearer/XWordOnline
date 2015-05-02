import urllib3
import certifi
import pyglet
from grid import Grid
from pyglet.gl import *
import xwordhtmlparser as parser

CLUE_WIDTH = 150
HORIZ_PADDING = 10
VERT_PADDING = 10
FONT_SIZE = 10

class Crossword(pyglet.window.Window):
    '''
    Class representing a crossword puzzle

    Private members:
    _grid: a grid object
    _acrossClues: a sorted list of across clues
    _downClues: a sorted list of down clues
    _clueLabels
    '''

    def __init__(self, url, fromSave):
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

        self._grid = None
        self._acrossClues = None
        self._downClues = None

        if not fromSave:
            self._grid, self._acrossClues, self._downClues = parser.parseHTMLFromSource(response.data)
        #self._grid.x = self.width - self._grid.width
        #self._grid.y = self.height - self._grid.height
        self._acrossClues.sort(key=lambda clue:int(clue[0]))
        self._downClues.sort(key=lambda clue:int(clue[0]))

        self._grid = Grid(15)
        self._grid.x = self.width - self._grid.width
        self._grid.y = self.height - self._grid.height

        self._clueLabels = []

        self._needsRedraw = True

    def parseHTMLFromSave(self, html):
        '''
        Take an html page from the svn repo and parse the data to
        return the various components of a crossword. Returns a tuple of the form
        (grid, across clues, down clues).

        Grid is a grid object
        Clues are lists of tuples of the form (n, t), where n is the number of the clue
        and t is the text of the clue
        '''

        pass

    def setUpClues(self):

        self._clueLabels = []

        xPos = HORIZ_PADDING
        yPos = self.height - 2*VERT_PADDING

        # draw the across label
        heading = pyglet.text.Label('Across', bold = True, color=(0,0,0,255), font_size = FONT_SIZE + 2, x = xPos, y = yPos)
        self._clueLabels.append(heading)

        yPos -= heading.content_height

        for i in range(len(self._acrossClues)):
            clue = pyglet.text.Label(str(self._acrossClues[i][0]) + '. ' + self._acrossClues[i][1], 
                                     width = CLUE_WIDTH, 
                                     multiline=True,
                                     color=(0,0,0,255),
                                     font_size = FONT_SIZE,
                                     x = xPos,
                                     y = yPos)
            self._clueLabels.append(clue)
            
            yPos -= (clue.content_height + VERT_PADDING)
            if yPos < VERT_PADDING:
                # move to the next row
                xPos += CLUE_WIDTH + HORIZ_PADDING
                if xPos + CLUE_WIDTH + HORIZ_PADDING >= self._grid.x:
                    # move below the grid
                    yPos = self._grid.y - 2*VERT_PADDING
                else:
                    yPos = self.height - 2*VERT_PADDING

        # draw the down label
        heading = pyglet.text.Label('Down', bold = True, color=(0,0,0,255), font_size = FONT_SIZE + 2, x = xPos, y = yPos)
        self._clueLabels.append(heading)

        yPos -= heading.content_height

        for i in range(len(self._acrossClues), len(self._acrossClues) + len(self._downClues)):
            clue = pyglet.text.Label(str(self._downClues[i - len(self._acrossClues)][0]) + '. ' + self._downClues[i - len(self._acrossClues)][1], 
                                     width = CLUE_WIDTH, 
                                     multiline=True,
                                     color=(0,0,0,255),
                                     font_size = FONT_SIZE,
                                     x = xPos,
                                     y = yPos)
            self._clueLabels.append(clue)
            
            yPos -= (clue.content_height + VERT_PADDING)
            if yPos < VERT_PADDING:
                # move to the next row
                xPos += CLUE_WIDTH + HORIZ_PADDING
                if xPos + CLUE_WIDTH + HORIZ_PADDING >= self._grid.x:
                    # move below the grid
                    yPos = self._grid.y - 2*VERT_PADDING
                else:
                    yPos = self.height - 2*VERT_PADDING

    def on_mouse_enter(self, x, y, lastSize = []):
        if lastSize != [self.width, self.height]:
            self._needsRedraw = True
            lastSize = [self.width, self.height]
        else:
            self._needsRedraw = False
                
    def on_mouse_release(self, x, y, button, modifiers):
        if self._grid.hit_test(x, y):
            self._grid.on_mouse_release(x, y, button, modifiers)
        else:
            self._grid.setFocusedSquare(None)

    def on_key_press(self, symbol, modifiers):
        self._grid.on_key_press(symbol, modifiers)

    def on_draw(self, lastSize = []):
        pyglet.gl.glClearColor(1.0,1.0,1.0,1.0)
        self.clear()

        if self._needsRedraw:
            glViewport(0,0,self.width,self.height);
            glMatrixMode(GL_PROJECTION);
            glLoadIdentity();
            gluOrtho2D(0,self.width,0,self.height);
            glMatrixMode(GL_MODELVIEW);
            glLoadIdentity();

            self._grid.x = self.width - self._grid.width
            self._grid.y = self.height - self._grid.height

            self.setUpClues()

            for label in self._clueLabels:
                label.draw()

            self._needsRedraw = False

        self._grid.draw(self)
