__author__ = 'mgarza'
# coding=UTF-8

import curses, logging, sys, subprocess, threading, time, math, random
import pathfinder


class Display (object):
    """
    This class is used to when any method needs to print to the curses screen
    """

    def __init__(self, screen=curses.initscr()):
        logging.basicConfig(filename='ui.log', level=logging.DEBUG)
        curses.curs_set(0)
        curses.noecho()
        screen.keypad(1)
        screen.border(1)
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        self._screen = screen
        self._dims = self._size_term()
        self._map_dims = []
        self.separate_line_y = 0

    def clear(self):
        """Clears screen"""
        self._screen.clear()

    def set_timeout(self, wait):
        """Sets screen timeout to integer given in wait, 0 to not wait, -1 to wait"""
        self._screen.timeout(wait)

    def get_input(self):
        """Returns user input"""
        return self._screen.getch()

    def _size_term(self):
        """Resize terminal, returns terminal size as [y,x]"""
        curr_dim = self._screen.getmaxyx()
        dims = [50, 150]
        if curr_dim[0] < dims[0] or curr_dim[1] < dims[1]:
            sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=dims[0], cols=dims[1]))
            curses.resize_term(dims[0], dims[1])
            return dims
        else:
            return curr_dim

    def read_text(self, file_name, strip=True):
        """Reads in text file and returns it as a list of strings"""
        fh = open(file_name, 'r')
        lines=[]
        for line in fh.readlines():
            if strip:
                lines.append(line.strip())
            else:
                lines.append(line)
        fh.close()
        return lines

    def add_char(self, coord, char, modify=False):
        """Adds char to screen at modified y, modified x and returns modified coordinates"""
        if modify:
            range_y, range_x = self._map_dims
            new_coord = [coord[0]+range_y[0]-1, coord[1]+range_x[0]-1]
            self._screen.addch(new_coord[0], new_coord[1], char)
            self._screen.refresh()
            return new_coord
        else:
            self._screen.addch(coord[0], coord[1], char)
            self._screen.refresh()
            return coord

    def get_char(self, coord):
        """return cell in coord given from the screen"""
        return self._screen.inch(coord[0], coord[1])

    def get_neighbors(self, coord, radius=1):
        """Returns a list of the cells surrounding y, x at the radius given"""
        y, x = coord
        neighbors = {}
        if radius == 1:
            neighbors['right'] = [self._screen.inch(y, x+1)]
            neighbors['left'] = [self._screen.inch(y, x-1)]
            neighbors['up'] = [self._screen.inch(y-1, x)]
            neighbors['down'] = [self._screen.inch(y+1, x)]
        else:
            range_y, range_x = self._map_dims
            right, left, up, down = [], [], [], []
            for x_right in range(x+1, range_x[1], 1):
                char = self._screen.inch(y, x_right)
                right.append(char)
            for x_left in range(x-1, range_x[0], -1):
                char = self._screen.inch(y, x_left)
                left.append(char)
            for y_down in range(y+1, range_y[1], 1):
                char = self._screen.inch(y_down, x)
                down.append(char)
            for y_up in range(y-1, range_y[0], -1):
                char = self._screen.inch(y_up, x)
                up.append(char)

            neighbors['right'] = right
            neighbors['left'] = left
            neighbors['up'] = up
            neighbors['down'] = down
        return neighbors

    def ascii_to_screen_map(self, y, text):
        """Prints to input given y is the coordinate of first line,
        x is the center coordinate for the text to be printed
        text is a list of text to be written"""
        text_height = len(text)
        for line_index, line in enumerate(text):
            text_width = len(line)
            x_start = (self._dims[1]/2) - (text_width/2)
            for char_index, char in enumerate(line):
                if char == u'.':
                    self._screen.addstr(y+line_index, x_start+char_index, char, curses.A_DIM|curses.color_pair(3))
                else:
                    self._screen.addstr(y+line_index, x_start+char_index, char, curses.A_BOLD|curses.color_pair(5))
        self._screen.refresh()

    def ascii_to_screen(self, y, text, color=1, width=0):
        """Prints to input given y is the coordinate of first line,
        x is the center coordinate for the text to be printed
        text is a list of text to be written"""
        text_height = len(text)
        for line_index in range(len(text)):
            text_width = len(text[line_index]) if not width else width
            self._screen.hline(y+line_index, 0, ord(' '), self._dims[1])
            if self._dims[0] > text_height and self._dims[1] > text_width:
                self._screen.addstr(y+line_index, (self._dims[1]/2)-(text_width/2), text[line_index], curses.A_BOLD|curses.color_pair(color))
        self._screen.refresh()

    def text_to_dialog(self, text, y=4, color=1, clear_low=False):
        """y is the spacing wanted for the text below the dialog line"""
        if clear_low:
            for cline in range(y, self._dims[0]):
                self._screen.hline(cline, 0, ord(' '), self._dims[1])

        for idx, line in enumerate(text):
            self._screen.hline(y+idx, 0, ord(' '), self._dims[1])
            self._screen.addstr(y+idx, (self._dims[1]/2)-(len(line)/2), line, curses.A_BOLD|curses.color_pair(color))
        self._screen.refresh()

    def display_room(self, room, player_start=[]):
        """Displays room on screen from room object given and returns player position"""
        map_start = 8
        self.clear()
        room_width = 0
        spacing = 3
        image_file = str(room.include[0].value.strip())
        room_tx = self.read_text(image_file)
        room_id = room.attrs['id']
        self.ascii_to_screen_map(map_start, room_tx)

        for line in room_tx:
            if len(line) > room_width:
                room_width = len(line)

        self._map_dims = [[map_start, map_start+len(room_tx)], [(self._dims[1]/2)-(room_width/2), (self._dims[1]/2)+(room_width/2)]]

        if player_start:
            player_y, player_x = player_start
            player_start = [int(player_y)+map_start-1, (self._dims[1]/2)-(room_width/2)+int(player_x)-1]
        else:
            player_y, player_x = str(room.attrs['player_start']).split(',')
            player_start = [int(player_y)+map_start-1, (self._dims[1]/2)-(room_width/2)+int(player_x)-1]

        self.text_to_dialog([room_id], 2)
        self.separate_line_y = len(room_tx)+map_start+spacing

        instruct = ['arrow keys: move around    c: interact    x: heal    space bar: shoot    p: pause game']
        self.text_to_dialog(instruct, self.separate_line_y-1)
        self._screen.hline(self.separate_line_y, 0, 2097503, self._dims[1])
        self._screen.refresh()

        return player_start

    def find_enemy_move(self, start, goal, space, enemy_symbol, player_symbol):
        """uses input to run pathfinder and return next move"""
        path = pathfinder.astar(self._screen, start, goal, self._map_dims, space, enemy_symbol, player_symbol)
        return path.get_shortest_path()
