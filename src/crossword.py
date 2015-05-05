import urllib3
import certifi
import pyglet
from grid import Grid
from pyglet.gl import *
import xwordhtmlparser as parser
from menubutton import MenuButton

CLUE_WIDTH = 150
HORIZ_PADDING = 10
VERT_PADDING = 10
FONT_SIZE = 10
BUTTON_HEIGHT = 40
BUTTON_WIDTH = 150

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

        super(Crossword, self).__init__(resizable = True, width=1000, height = 750, caption = 'XWord Online')

        self._grid = None
        self._acrossClues = None
        self._downClues = None
        self._clueLabels = []

        self._btnRefresh = MenuButton(self)
        self._btnRefresh.x = HORIZ_PADDING
        self._btnRefresh.y = self.height - VERT_PADDING - BUTTON_HEIGHT
        self._btnRefresh.width = BUTTON_WIDTH
        self._btnRefresh.height = BUTTON_HEIGHT
        self._btnRefresh.text = 'Refresh'
        self._btnRefresh.on_press = self.refresh

        self._btnLoadSaved = MenuButton(self)
        self._btnLoadSaved.x = self._btnRefresh.x + BUTTON_WIDTH + HORIZ_PADDING
        self._btnLoadSaved.y = self._btnRefresh.y
        self._btnLoadSaved.width = BUTTON_WIDTH
        self._btnLoadSaved.height = BUTTON_HEIGHT
        self._btnLoadSaved.text = 'Load Saved Puzzle'
        self._btnLoadSaved.on_press = self.loadPuzzleFromSave

        self._btnLoadFromSource = MenuButton(self)
        self._btnLoadFromSource.x = self._btnLoadSaved.x + BUTTON_WIDTH + HORIZ_PADDING
        self._btnLoadFromSource.y = self._btnLoadSaved.y
        self._btnLoadFromSource.width = BUTTON_WIDTH
        self._btnLoadFromSource.height = BUTTON_HEIGHT
        self._btnLoadFromSource.text = 'Load New Puzzle'
        self._btnLoadFromSource.on_press = self.loadPuzzleFromSource

        self._btnRand = MenuButton(self)
        self._btnRand.x = self._btnLoadFromSource.x + BUTTON_WIDTH + HORIZ_PADDING
        self._btnRand.y = self._btnLoadFromSource.y
        self._btnRand.width = BUTTON_WIDTH
        self._btnRand.height = BUTTON_HEIGHT
        self._btnRand.text = 'Random Puzzle'
        self._btnRand.on_press = self.loadRandomPuzzle

        self._controls = [self._btnRefresh,
                          self._btnLoadSaved,
                          self._btnLoadFromSource,
                          self._btnRand]

        if not fromSave:
            self.loadPuzzleFromSource(url)

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

    def loadPuzzleFromSource(self, url):
        http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED', # Force certificate check.
            ca_certs=certifi.where()  # Path to the Certifi bundle.
        )
        response = http.request('GET', url) 

        f = open('C:/Users/Jeb/Desktop/xword-test.html', 'w')
        f.write(response.data)
        f.close()

        self._grid, self._acrossClues, self._downClues = parser.parseHTMLFromSource(response.data)
        self._grid.x = self.width - self._grid.width - HORIZ_PADDING
        self._grid.y = self._btnRefresh.y - VERT_PADDING - self._grid.height

        self._acrossClues.sort(key=lambda clue:int(clue[0]))
        self._downClues.sort(key=lambda clue:int(clue[0]))

    def loadPuzzleFromSave(self):
        pass

    def loadRandomPuzzle(self):
        pass

    def setUpButtons(self):
        self._btnRefresh.x = HORIZ_PADDING
        self._btnRefresh.y = self.height - VERT_PADDING - BUTTON_HEIGHT

        self._btnLoadSaved.x = self._btnRefresh.x + BUTTON_WIDTH + HORIZ_PADDING
        self._btnLoadSaved.y = self._btnRefresh.y

        self._btnLoadFromSource.x = self._btnLoadSaved.x + BUTTON_WIDTH + HORIZ_PADDING
        self._btnLoadFromSource.y = self._btnLoadSaved.y

        self._btnRand.x = self._btnLoadFromSource.x + BUTTON_WIDTH + HORIZ_PADDING
        self._btnRand.y = self._btnLoadFromSource.y

    def setUpClues(self):

        if self._acrossClues is None or self._downClues is None:
            return

        self._clueLabels = []

        xPos = HORIZ_PADDING
        yPos = self._btnRefresh.y - VERT_PADDING

        # draw the across label
        heading = pyglet.text.Label('Across', bold = True,
                                    color=(0,0,0,255),
                                    font_size = FONT_SIZE + 2,
                                    anchor_x = 'left',
                                    anchor_y = 'top',
                                    x = xPos,
                                    y = yPos)

        self._clueLabels.append(heading)

        yPos -= heading.content_height

        for i in range(len(self._acrossClues)):
            clue = pyglet.text.Label(str(self._acrossClues[i][0]) + '. ' + self._acrossClues[i][1], 
                                     width = CLUE_WIDTH, 
                                     multiline=True,
                                     color=(0,0,0,255),
                                     font_size = FONT_SIZE,
                                     anchor_x = 'left',
                                     anchor_y = 'top',
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
                    yPos = self._btnRefresh.y - VERT_PADDING

        # draw the down label
        heading = pyglet.text.Label('Down',
                                    bold = True,
                                    color=(0,0,0,255),
                                    font_size = FONT_SIZE + 2,
                                    anchor_x = 'left',
                                    anchor_y = 'top',
                                    x = xPos,
                                    y = yPos)
        self._clueLabels.append(heading)

        yPos -= heading.content_height

        for i in range(len(self._acrossClues), len(self._acrossClues) + len(self._downClues)):
            clue = pyglet.text.Label(str(self._downClues[i - len(self._acrossClues)][0]) + '. ' + self._downClues[i - len(self._acrossClues)][1], 
                                     width = CLUE_WIDTH, 
                                     multiline=True,
                                     color=(0,0,0,255),
                                     font_size = FONT_SIZE,
                                     anchor_x = 'left',
                                     anchor_y = 'top',
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
                    yPos = self._btnRefresh.y - VERT_PADDING

    lastSize = []
    def on_mouse_enter(self, x, y):
        if self.lastSize != [self.width, self.height]:
            self.on_draw()
            self.lastSize = [self.width, self.height]

    def on_mouse_press(self, x, y, button, modifiers):
        for control in self._controls:
            if control.hit_test(x, y):
                control.on_mouse_press(x, y, button, modifiers)
                return
                
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

        glViewport(0,0,self.width,self.height);
        glMatrixMode(GL_PROJECTION);
        glLoadIdentity();
        gluOrtho2D(0,self.width,0,self.height);
        glMatrixMode(GL_MODELVIEW);
        glLoadIdentity();

        self._grid.x = self.width - self._grid.width - HORIZ_PADDING
        self._grid.y = self._btnRefresh.y - VERT_PADDING - self._grid.height

        self.setUpClues()

        for label in self._clueLabels:
            label.draw()

        self.setUpButtons()
        for control in self._controls:
            control.draw()

        self._grid.draw(self)

    def refresh(self):
        pass
