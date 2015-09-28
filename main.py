__author__ = 'mgarza'

import curses, traceback, logging, sys
import engine, ui


class Main(object):
    """
    This class is the main method used to run and play the Jurassic Park Shooting Adventure
    """

    def __init__(self, screen=curses.initscr()):
        logging.basicConfig(filename='main.log', level=logging.DEBUG)
        self._screen = screen
        self._game_progress = False
        self._main_menu()

    def _main_menu(self):
        """Main menu to the game to get started"""
        display = ui.Display(self._screen)

        selection = -1
        option = 0
        logging.debug('running main')
        game = engine.Gameplay(self._screen)
        logging.debug('passed initalizing with xml')
        title = display.read_text('ASCII/title.txt', strip=False)

        while selection != 2:  # while exit has not been selected
            display.set_timeout(-1)
            display.clear()
            display.ascii_to_screen(10, title, 4, 92)

            if self._game_progress:
                graphics = [1] * 3
                graphics[option] = 7
                display.text_to_dialog(['Created by: Marissa Garza'], 26, 1)
                display.text_to_dialog(['Continue'], 28, graphics[0])
                display.text_to_dialog(['New Game'], 29, graphics[1])
                display.text_to_dialog(['Exit'], 30, graphics[2])
                action = display.get_input()

                if action == curses.KEY_UP:
                    option = (option - 1) % 3
                elif action == curses.KEY_DOWN:
                    option = (option + 1) % 3
                elif action == ord('\n'):
                    selection = option

            else:
                graphics = [1] * 2
                graphics[option] = 7
                display.text_to_dialog(['Created by: Marissa Garza'], 26, 1)
                display.text_to_dialog(['New Game'], 28, graphics[0])
                display.text_to_dialog(['Exit'], 29, graphics[1])
                action = display.get_input()

                if action == curses.KEY_UP:
                    option = (option - 1) % 2
                elif action == curses.KEY_DOWN:
                    option = (option + 1) % 2
                elif action == ord('\n'):
                    selection = option + 1

            if selection == 1:
                game = engine.Gameplay(self._screen)
                game.play()
                self._game_progress = True
            elif selection == 0:
                game.change_game_status('alive')
                game.play(intro=False)
            elif selection == 2:
                sys.exit()

            selection = -1


    def _load_game(self):
        """Loads a saved game state"""
        pass

    def _save_game(self):
        """Saves a game state"""
        pass


if __name__ == '__main__':
    try:
        curses.wrapper(Main)
    except:
        out = traceback.format_exc()
        logging.debug(out)
        curses.endwin()