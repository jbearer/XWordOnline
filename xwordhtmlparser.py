import HTMLParser
import re
from square import Square
from grid import Grid

'''
Module containing classes to parse html files containing crossword data
Parses html files at urls like http://freecrosswordpuzzles.com.au/printablecrossword.aspx?cw=M2-5-2015
'''

DOWN = 'Down'
ACROSS = 'Across'

def parseHTMLFromSource(html):
        '''
        Take an html page formatted as those at
        http://freecrosswordpuzzles.com.au/printablecrossword.aspx?cw=M2-5-2015 and parse the data to
        return the various components of a crossword. Returns a tuple of the form
        (grid, across clues, down clues).

        Grid is a grid object
        Clues are lists of tuples of the form (n, t), where n is the number of the clue
        and t is the text of the clue
        '''

        print 'parsing across clues \n\n\n'
        acrossClues = []
        aParser = ParseClues(acrossClues, ACROSS)
        aParser.feed(html)
        aParser.close()

        print 'parsing down clues \n\n\n'
        downClues = []
        dParser = ParseClues(downClues, DOWN)
        dParser.feed(html)
        aParser.close()

        print 'parsing grid \n\n\n'
        grid = Grid()
        gParser = ParseGrid(grid)
        gParser.feed(html)
        gParser.close()

        return (grid, acrossClues, downClues)

class ParseClues(HTMLParser.HTMLParser):

    '''
    Constructs a list of (#, clue) pairs in _clueList
    '''
    class states:
        '''
        The parsing algorithm is implemented like a Turing machine
        with these states
        '''

        '''
        NEUTRAL state: in no particular class, looking for the clue class
            (characterized by <div id=<clueType>Clues)
        '''
        NEUTRAL = 0

        '''
        IN_CLUE_CLASS state: found the clue class, looking for individual clues
            (charcterized by <div id=divClue<clueNumber>>)
        '''
        IN_CLUE_CLASS = 1

        '''
        FOUND_CLUE state: now parsing an individual clue. The next two <data> will be:
           1. <clueNumber>:
           2. <whiteSpace><Clue>
        '''
        FOUND_CLUE = 2

        '''
        FOUND_CLUE_NUMBER state: found and wrote the clue number data, now looking for the clue
        '''
        FOUND_CLUE_NUMBER = 3

        '''
        FOUND_CLUE_TEXT state: found and wrote the clue data, now looking for a </div> to exit
            this individual clue
        '''
        FOUND_CLUE_TEXT = 4

        '''
        ACCEPTING state: entered, parsed, and exited the clue class. Parsing is done. Once entered,
            this state is permanent
        '''
        ACCEPTING = -1

    def __init__(self, clueList, clueType):
        '''
        :param clueList: an empty list into which to put the clues
        :param clueType: must be DOWN or ACROSS
        '''

        #super(ParseClues, self).__init__()
        HTMLParser.HTMLParser.__init__(self)

        self._clueList = clueList
        self._clueType = clueType
        self._state = self.states.NEUTRAL

        # used as a temporary variable for storing partial clue data
        # during parsing, before data is ready to be added to clueList
        self._currentClue = [None, None]

    def handle_starttag(self, tag, attrs):
        if self._state == self.states.NEUTRAL:
            # look for <div id=<clueType>Clues
            if tag == 'div' and ('id', self._clueType + 'Clues') in attrs:
                self._state = self.states.IN_CLUE_CLASS
                print 'entering IN_CLUE_CLASS state'

        elif self._state == self.states.IN_CLUE_CLASS:
            # look for <div id=divClue<clueNumber>>
            if tag == 'div':
                # all we know is that the id attribute should end in some number
                # since we don't know what the number is, use regex to parse and capture the number
                clueID = re.compile(r"divClue(\d+)")
                for attrib in attrs:
                    if attrib[0] == 'id':
                        print 'looking for clue #: ' + attrib[1]
                        match = re.match(clueID, attrib[1])
                        if match:
                            # we have the number now, so add it to currentClue
                            self._currentClue[0] = match.group(1)
                            self._state = self.states.FOUND_CLUE
                            'entering FOUND_CLUE state'
                            return
                        else:
                            raise HTMLParser.HTMLParseError('Expected clue number')

        # other states are looking for either endtags or data, not starttags

    def handle_endtag(self, tag):
        if self._state == self.states.IN_CLUE_CLASS:
            # look for </div> to finish parsing
            if tag == 'div':
                self._state = self.states.ACCEPTING
                print 'entering ACCEPTING state'

        elif self._state == self.states.FOUND_CLUE_TEXT:
            # look for </div> to exit this particular clue and return to
            # in_clue_class  state
            if tag == 'div':
                self._state = self.states.IN_CLUE_CLASS
                print 'reentering IN_CLUE_CLASS state'

        # other states are looking for either starttags or data, not endtags

    def handle_data(self, data):
        if self._state == self.states.FOUND_CLUE:
            # look for the number in the data
            # if all is well, we should already have the number stored in currentClue
            # from the regex in IN_CLUE_CLASS state
            # this state is largely redundant, included for robustness
            number = re.compile(r"(\d+):\s*")
            match = re.match(number, data)
            if match:
                if match.group(1) != self._currentClue[0]:
                    raise HTMLParser.HTMLParseError('Inconsistent clue numbers')
            else :
                raise HTMLParser.HTMLParseError('Expected clue number')

            self._state = self.states.FOUND_CLUE_NUMBER
            print 'entering FOUND_CLUE_NUMBER state'

        elif self._state == self.states.FOUND_CLUE_NUMBER:
            # look for the clue text, remove whitespace
            clue = re.compile(r"\s*(.+)\s*")
            match = re.match(clue, data)
            if match:
                self._currentClue[1] = match.group(1)
                self._clueList.append(tuple(self._currentClue))
                self._state = self.states.FOUND_CLUE_TEXT
                print 'entering FOUND_CLUE_TEXT state'
            else:
                raise HTMLParser.HTMLParseError('Expected clue')


class ParseGrid(HTMLParser.HTMLParser):

    '''
    Constructs a grid
    '''

    class states:
        '''
        The parsing algorithm is implemented like a Turing machine
        with these states
        '''

        '''
        NEUTRAL state: in no particular class, looking for the xword table
            (characterized by <table id=tblCrossword)
        '''
        NEUTRAL = 0

        '''
        IN_XWORD state: in the crossword table, looking for a row of squares
            (characterized by <tr>)
        '''
        IN_XWORD = 1

        '''
        IN_ROW state: in a row, looking for an individual square
            (characterized by <td id=T<col>x<row>>)
        '''
        IN_ROW = 2

        '''
        WHITE_SQUARE state: in a white square, looking for the square's #
        '''
        WHITE_SQUARE = 3

        '''
        ACCEPTING state: entered, parsed, and exited the grid. Parsing is done. Once entered,
            this state is permanent
        '''
        ACCEPTING = -1


    def __init__(self, emptyGrid):
        '''
        :param clueList: an empty list into which to put the clues
        :param clueType: must be DOWN or ACROSS
        '''

        HTMLParser.HTMLParser.__init__(self)

        self._grid = emptyGrid
        self._state = self.states.NEUTRAL

        self._row = None
        self._col = None

    def handle_starttag(self, tag, attrs):
        if self._state == self.states.NEUTRAL:
            if tag == 'table' and ('id', 'tblCrossword') in attrs:
                self._state = self.states.IN_XWORD
                print 'entering IN_XWORD state'

        elif self._state == self.states.IN_XWORD:
            if tag == 'tr':
                self._state = self.states.IN_ROW
                print 'entering IN_ROW state'

        elif self._state == self.states.IN_ROW:
            if tag == 'td':
                idPat = re.compile(r"T(\d+)x(\d+)")
                for attrib in attrs:
                    if attrib[0] == 'id':
                        match = re.match(idPat, attrib[1])
                        if match:
                            self._row = int(match.group(2)) - 1
                            self._col = int(match.group(1)) - 1
                            print 'found square: ' + str((self._row, self._col))

                            if ('bgcolor', 'black') in attrs:
                                print 'adding black square'

                                self._grid.setSquare(self._row, self._col, Square(self._grid, self._row, self._col))
                                self._state = self.states.IN_ROW
                                print 'reentering IN_ROW state'

                            else:
                                self._state = self.states.WHITE_SQUARE
                                print 'entering WHITE_SQUARE state'
                            return

    def handle_endtag(self, tag):
        if self._state == self.states.IN_ROW:
            if tag == 'tr':
                self._state = self.states.IN_XWORD
                print 'reentering IN_XWORD state'
        elif self._state == self.states.IN_XWORD:
            if tag == 'table':
                self._state = self.states.ACCEPTING
                print 'entering ACCEPTING state'

    def handle_data(self, data):
        if self._state == self.states.WHITE_SQUARE:
            numPat = re.compile(r"\D*(\d*)")
            match = re.match(numPat, data)
            if match:
                print 'Adding white square: ' + match.group(1)
                self._grid.setSquare(self._row, self._col, Square(self._grid, self._row, self._col, letter='', number=match.group(1)))
                self._state = self.states.IN_ROW
                print 'reentering IN_ROW state'
            else:
                raise HTMLParser.HTMLParseError('Expected number or blank')

