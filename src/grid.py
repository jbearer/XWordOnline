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

    def __init__(self, width = 0, height = None, x = 0, y = 0, squares = []):
        '''
        Create a grid of width x height empty squares.
        If the argument height is absent, the grid is square with side length = width
        '''
        print 'grid constrcutor called'

        if height is None:
            height = width

        self.width = width * Square.WIDTH
        self.height = height * Square.HEIGHT
        self.numRows = height
        self.numCols = width
        self._squares = squares
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
        while row >= self.getNumRows():
            self.addRow()
        
        while col >= self.getNumCols():
            self.addCol()
        
        self._squares[row][col] = square

    def getNumRows(self):
        return self.numRows

    def getNumCols(self):
        return self.numCols

    def addRow(self):
        '''
        Append a row of black squares to the bottom of the grid
        '''

        self.numRows += 1
        self.height += Square.HEIGHT

        newRow = []
        for col in range(self.getNumCols()):
            newRow.append(Square(self, self.getNumRows(), col, ''))

        self._squares.append(newRow)

    def addCol(self):
        '''
        Append a column of black squares to the right of the grid
        '''

        self.numCols += 1
        self.width += Square.WIDTH

        for row in range(self.getNumRows()):
            self._squares[row].append(Square(self,row,self.getNumCols(), ''))


    def setFocusedSquare(self, square):
        if square and square.letter is None:
            # black square cannot have focus
            return

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
        print 'got key press'
        if self._focusedSquare:
            print 'focused square'
            if symbol >= key.A and symbol <= key.Z:
                self._focusedSquare.setText(chr(symbol).upper())

            if self._focusedSquare:

                if (modifiers & key.MOD_SHIFT and symbol == key.TAB) or symbol == key.LEFT:
                    # move left one
                    row, col = self._focusedSquare.row, self._focusedSquare.col
                    col -= 1
                    if col < 0:
                        col = self.numCols - 1
                        row -= 1
                    if row < 0:
                        row = self.numRows - 1

                    self.setFocusedSquare(self._squares[row][col])

                elif symbol == key.TAB or symbol == key.RIGHT:
                    # move right one 
                    row, col = self._focusedSquare.row, self._focusedSquare.col
                    col += 1
                    if col > self.numCols - 1:
                        col = 0
                        row += 1
                    if row > self.numRows - 1:
                        row = 0

                    self.setFocusedSquare(self._squares[row][col])

                elif (modifiers & key.MOD_SHIFT and symbol == key.RETURN) or symbol == key.UP:
                    # move up one
                    row, col = self._focusedSquare.row, self._focusedSquare.col
                    row -= 1
                    if row < 0:
                        row = self.numRows - 1
                        col -= 1
                    if col < 0:
                        col = self.numCols - 1

                    self.setFocusedSquare(self._squares[row][col])

                elif symbol == key.RETURN or symbol == key.DOWN:
                    # move down one
                    print 'finding square'
                    row, col = self._focusedSquare.row, self._focusedSquare.col
                    print (row, col)
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

    def _makeSquares(self, squares):
        '''
        Copy a list of square data (row, col, letter, and number) into self's squares, updating each square's parent.
        Return self.
        Used by repr
        '''
        print 'in make squares'
        for square in squares:
            print 'setting square'
            self.setSquare(square['row'], square['col'], Square(self, square['row'], square['col'], square['letter'], square['number']))
            print 'square set'
        print 'returning'
        return self

    def __repr__(self):
        squareL = '['
        for row in self._squares:
            for square in row:
                squareL += repr(square) + ','
        squareL = squareL[:-1]
        squareL += ']'
        gridCons = 'Grid(' + str(self.width / Square.WIDTH) + ',' + str(self.height / Square.HEIGHT) + ',' + str(self.x) + ',' + str(self.y) + ')'
        return '[newGrid._makeSquares(' + squareL + ') for newGrid in [' + gridCons + ']][0]'