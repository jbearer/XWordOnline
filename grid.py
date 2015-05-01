from square import Square
from pyglet.window import key

class Grid():
    '''
    Class representing the grid component of a crossword

    public interface:

    get(i, j): return the square ( a pyglet object ) at row i and column j
    set(i, j): set the contents of the square at row i and column j

    width
    height

    private:

    _squares: a 2D array of squares
    _focusedSquare: the square with the focus
    '''

    def __init__(self, width, height = None, x = 0, y = 0):
        '''
        Create a grid of width x height empty squares.
        If the argument height is absent, the grid is square with side length = width
        '''

        if height is None:
            height = width

        self.width = width * Square.WIDTH
        self.height = height * Square.HEIGHT
        self.numRows = height
        self.numCols = width
        self._squares = []
        self._focusedSquare = None

        self.x = x
        self.y = y

        for row in range(height):
            newRow = []
            for col in range(width):
                newRow.append(Square(self, row, col, ''))
            self._squares.append(newRow)

    def getSquare(self, row, col):
        return self._squares[row][col]

    def setSquare(self, row, col, square):
        self._squares[row][col] = square

    def getNumRows(self):
        return self.numRows

    def getNumCols(self):
        return self.numCols

    def setFocusedSquare(self, square):
        if self._focusedSquare:
            # force old focused square to release focus
            self._focusedSquare.hasFocus = False
        if square:
            square.hasFocus = True

        self._focusedSquare = square

    def draw(self, window):

        for row in self._squares:
            for square in row:
                if square != self._focusedSquare:
                    square.draw(window)

        # draw focused square last so red borders are in front
        if self._focusedSquare:
            self._focusedSquare.draw(window)

    def findSquare(self, target):
        '''
        Return a (row, col) tuple with the index of the given square. Return None if not found
        '''
        for row in range(self.numRows):
            for col in range(self.numCols):
                if self._squares[row][col] == target:
                    return (row, col)
        return None

    def hit_test(self, x, y):
        return (self.x < x < self.x + self.width and  
                self.y < y < self.y + self.height)

    def on_mouse_release(self, x, y, button, modifiers):
        x -= self.x
        y -= self.y
        for row in self._squares:
            for square in row:
                if square.hit_test(x, y):
                    square.on_mouse_release(x, y, button, modifiers)
                    break

    def on_key_press(self, symbol, modifiers):
        if self._focusedSquare:
            if symbol >= key.A and symbol <= key.Z:
                self._focusedSquare.setText(chr(symbol).upper())

            if self._focusedSquare:

                if (modifiers & key.MOD_SHIFT and symbol == key.TAB) or symbol == key.LEFT:
                    # move left one
                    row, col = self.findSquare(self._focusedSquare)
                    col -= 1
                    if col < 0:
                        col = self.numCols - 1
                        row -= 1
                    if row < 0:
                        row = self.numRows - 1

                    self.setFocusedSquare(self._squares[row][col])

                elif symbol == key.TAB or symbol == key.RIGHT:
                    # move right one 
                    row, col = self.findSquare(self._focusedSquare)
                    col += 1
                    if col > self.numCols - 1:
                        col = 0
                        row += 1
                    if row > self.numRows - 1:
                        row = 0

                    self.setFocusedSquare(self._squares[row][col])

                elif (modifiers & key.MOD_SHIFT and symbol == key.RETURN) or symbol == key.UP:
                    # move up one
                    row, col = self.findSquare(self._focusedSquare)
                    row -= 1
                    if row < 0:
                        row = self.numRows - 1
                        col -= 1
                    if col < 0:
                        col = self.numCols - 1

                    self.setFocusedSquare(self._squares[row][col])

                elif symbol == key.RETURN or symbol == key.DOWN:
                    # move down one
                    row, col = self.findSquare(self._focusedSquare)
                    row += 1
                    if row > self.numRows - 1:
                        row = 0
                        col += 1
                    if col > self.numCols - 1:
                        col = 0

                    self.setFocusedSquare(self._squares[row][col])

                elif symbol == key.BACKSPACE or symbol == key.DELETE:
                    # delete the text in the focused square
                    self._focusedSquare.setText('')

