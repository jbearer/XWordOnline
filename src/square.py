import sys

from pyglet.gl import *
import pyglet
from pyglet.window import key

class Square():
    '''
    Class representing a single square in a crossword grid

    public interface:
        letter: the letter in the square. Will be '' if the square is blank or None is the square is black
        number: the number of the square, or '' if the square has no number
        row
        col
        x
        y

        const:
        WIDTH: the size of the square on the screen
        HEIGHT

        private:
        _lblLetter
        _lblNumber


    '''

    WIDTH = 50
    HEIGHT = 50
    PADDING = 10

    def __init__(self, parent, row, col, letter = None, number = '', updated = True, answer = ''):
        number = str(number)
        self.parent = parent
        self.row = row
        self.col = col
        self.letter = letter
        self.number = number
        self.x = col * self.WIDTH
        self.y = (parent.getNumRows() - row - 1) * self.HEIGHT
        self.hasFocus = False

        if letter is not None:
            self._lblLetter = pyglet.text.Label(letter, anchor_x = 'center', anchor_y = 'center', font_size = 12)
            self._lblLetter.color = (0,0,0,255)
        else:
            self._lblLetter = None

        self._lblNumber = pyglet.text.Label(number, anchor_x='left', anchor_y='top', font_size = 8)
        self._lblNumber.color = (0,0,0,255)

    def draw_rect_outline(self, x, y, width, height, window):

        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()

    def draw_rect_filled(self, x, y, width, height, window):

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glBegin(GL_POLYGON)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()

    def hit_test(self, x, y):
        return (self.x < x < self.x + self.WIDTH and  
                self.y < y < self.y + self.HEIGHT)

    def draw(self, window):
        self.x = self.col * self.WIDTH
        self.y = (self.parent.getNumRows() - self.row - 1) * self.HEIGHT

        if self.letter is None:
            # black square
            self.draw_rect_filled(self.x + self.parent.x, self.y + self.parent.y, self.WIDTH, self.HEIGHT, window)

        else:
            # white square
            if self.hasFocus:
                glColor3f(1, 0, 0)
            self.draw_rect_outline(self.x + self.parent.x, self.y + self.parent.y, self.WIDTH, self.HEIGHT, window)
            glColor3f(0, 0, 0)

            if self._lblLetter:
                self._lblLetter.x = self.x + self.parent.x + self.WIDTH / 2
                self._lblLetter.y = self.y + self.parent.y + self.HEIGHT / 2
                self._lblLetter.draw()

            self._lblNumber.x = self.x + self.parent.x + self.PADDING / 2
            self._lblNumber.y = self.y + self.parent.y + self.HEIGHT - self.PADDING / 2
            self._lblNumber.draw()

    def on_mouse_release(self, x, y, button, modifiers):
        if self.letter is not None:
            if self.hit_test(x, y):
                self.parent.setFocusedSquare(self)

    def setText(self, text):
        if self._lblLetter:
            self._lblLetter.text = text
            self._updated = True

    def __repr__(self):
        if self._lblLetter:
            return str({'row':self.row, 'col':self.col, 'letter':self._lblLetter.text, 'number':self._lblNumber.text})
        else:
            return str({'row':self.row, 'col':self.col, 'letter':None, 'number':self._lblNumber.text})
