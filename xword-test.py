from crossword import Crossword
from grid import Grid
from square import Square
import pyglet

if __name__ == '__main__':
	xword = Crossword('http://freecrosswordpuzzles.com.au/printablecrossword.aspx?cw=M2-5-2015', False)

	pyglet.app.run()
