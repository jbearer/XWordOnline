import HTMLParser
import re
#from enum import Enum

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

        acrossClues = []
        aParser = ParseClues(acrossClues, ACROSS)
        aParser.feed(html)

        downClues = []
        dParser = ParseClues(downClues, DOWN)
        dParser.feed(html)

        grid = None # TODO

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
    def handle_starttag(self, tag, attrs):
        print "Encountered a start tag:", tag
    def handle_endtag(self, tag):
        print "Encountered an end tag :", tag
    def handle_data(self, data):
        print "Encountered some data  :", data
