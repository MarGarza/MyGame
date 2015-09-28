__author__ = 'mgarza'

import JurassicParkTemplate
import curses,time, traceback, logging, sys

class jurassicpark (object):

    def __init__(self):
        logging.basicConfig(filename='JP.log', level=logging.DEBUG)
        self.game = self.grab_game_objects()
        self.dims = [50, 150]
        self.player_room_name = self.game.player[0].attrs['position']
        self.player_room_index = 0
        self.player_position = [1, 1]
        self.treasures = {}
        self.doors = {}
        self.separate_line_y = 1
        self.player_piece, self.treasure_symbol, self.door_symbol = '@', 'T', 'D'

    def main(self, screen):
        sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=self.dims[0], cols=self.dims[1]))
        curses.curs_set(0)
        curses.noecho()
        screen.keypad(1)
        screen.border()
        self.screen = screen
        self.main_menu()

    def grab_game_objects(self):
        """Grabs all game objects for use in game returns game object"""
        with open('JurassicParkObjects.xml') as f:
            xml_data = f.read()
        successful, game = JurassicParkTemplate.obj_wrapper(xml_data)
        if not successful:
            raise game
        return game

    def load_game(self):
        """Displays the instructions to the game"""
        pass

    def intro(self):
        """Displays the intro to the game"""
        jpLogo = self.read_text('ASCII/jp_logo.txt')
        jpLogo_height = len(jpLogo)
        start_height = 2
        spacing = 2
        for text_index in range(len(self.game._intro[0].text)):
            self.screen.clear()
            start_text=start_height+jpLogo_height+spacing
            for line_index in range(len(jpLogo)):
                jpLogo_width = len(jpLogo[line_index])
                if self.dims[0]>jpLogo_height and self.dims[1]> jpLogo_width:
                    self.screen.addstr(line_index+start_height, (self.dims[1]/2)-(jpLogo_width/2), jpLogo[line_index], curses.A_BOLD)
            for t_id,text in enumerate(self.game._intro[0].text[text_index].value.split('\n')):
                text_len=len(text)
                self.screen.addstr(start_text+t_id, (self.dims[1]/2)-(text_len/2), text.lstrip(), curses.A_BOLD)
            action = self.screen.getch()

    def play(self):
        """runs game"""
        self.intro()
        action = 0
        self.player_position = self.display_room()
        while action != ord('q'):
            self.screen.addch(self.player_position[0], self.player_position[1], self.player_piece)
            self.screen.refresh()
            action = self.screen.getch()
            if action == curses.KEY_UP and self.screen.inch(self.player_position[0]-1, self.player_position[1]) == ord(' '):
                self.screen.addch(self.player_position[0], self.player_position[1], ' ')
                self.player_position[0] -= 1
            elif action == curses.KEY_DOWN and self.screen.inch(self.player_position[0]+1, self.player_position[1]) == ord(' '):
                self.screen.addch(self.player_position[0], self.player_position[1], ' ')
                self.player_position[0] += 1
            elif action == curses.KEY_LEFT and self.screen.inch(self.player_position[0], self.player_position[1]-1) == ord(' '):
                self.screen.addch(self.player_position[0], self.player_position[1], ' ')
                self.player_position[1] -= 1
            elif action == curses.KEY_RIGHT and self.screen.inch(self.player_position[0], self.player_position[1]+1) == ord(' '):# and self.screen.inch(self.player_position[0], self.player_position[1]+2) == ord(' '):
                self.screen.addch(self.player_position[0], self.player_position[1], ' ')
                self.player_position[1] += 1
            elif action == ord(' '):
                self.interact()
            elif action == ord('m'):
                self.game_menu()

    def display_room(self):
        """Displays room on screen with treasures and doors"""
        self.treasures = {}
        map_buffer = 5
        spacing =5
        self.doors = {}
        room_image = []
        player_start = False
        self.screen.clear()
        for room_idx, room in enumerate(self.game.room):    #Finds the current room index
            if room.attrs['id'] == self.player_room_name:
                self.player_room_index = room_idx
                room_image = room.image[0].value.split('\n')

        room_len = len(room_image)
        for idx, line in enumerate(room_image):     #Adds ascii image of room onto screen
            line = line.strip()
            line_len = len(line.strip())
            self.screen.addstr((self.dims[0]/2)-(room_len/2)+idx-map_buffer, (self.dims[1]/2)-(line_len/2), line)

            if self.game.room[self.player_room_index].attrs['player_piece'] in line:    #Gets the players starting position in the room
                player_start = [(self.dims[0]/2)-(room_len/2)+idx-map_buffer, (self.dims[1]/2)-(line_len/2)+line.index(self.game.room[self.player_room_index].attrs['player_piece'])]

        for t_index, treasure in enumerate(self.game.room[self.player_room_index].treasure):#Displays treasure in room
            treasure_id = self.game.room[self.player_room_index].treasure[t_index].attrs['id']
            treasure_loc = treasure.location[0].value.strip()
            treasure_y, treasure_x = treasure_loc.split(',')
            treasure_y, treasure_x = int(treasure_y), int(treasure_x)
            row_text = [row_text for row, row_text in enumerate(self.game.room[self.player_room_index].image[0].value.split('\n')) if row == treasure_y]
            row_len = len(row_text[0].strip())
            if treasure.attrs['status'] == u'full':
                self.screen.addch((self.dims[0]/2)-(room_len/2)+treasure_y-map_buffer, (self.dims[1]/2)-(row_len/2)+treasure_x, self.treasure_symbol)
            self.treasures[treasure_id] = [(self.dims[0]/2)-(room_len/2)+treasure_y-map_buffer, (self.dims[1]/2)-(row_len/2)+treasure_x] #Adds treasure locations and ids to dictionary

        for d_index, door in enumerate(self.game.room[self.player_room_index].door):       #Displays doors in room
            door_id = self.game.room[self.player_room_index].door[d_index].attrs['id']
            door_loc = door.location[0].value.strip()
            door_y, door_x = door_loc.split(',')
            door_y, door_x = int(door_y), int(door_x)
            row_text = [row_text for row, row_text in enumerate(self.game.room[self.player_room_index].image[0].value.split('\n')) if row == door_y]
            row_len = len(row_text[0].strip())
            self.screen.addch((self.dims[0]/2)-(room_len/2)+door_y-map_buffer, (self.dims[1]/2)-(row_len/2)+door_x, self.door_symbol)
            self.doors[door_id] = [(self.dims[0]/2)-(room_len/2)+door_y-map_buffer, (self.dims[1]/2)-(row_len/2)+door_x] #Adds door locations and ids to dictionary

        self.screen.addstr(1, (self.dims[1]/2)-(len(self.player_room_name)/2), self.player_room_name, curses.A_BOLD)
        self.separate_line_y=(self.dims[0]/2)+(room_len/2)-map_buffer+spacing
        self.screen.hline(self.separate_line_y, 0, ord('_'), self.dims[1])
        return player_start

    def change_room(self, y, x):
        """Changes the player's current room"""
        new_room = False
        result = ''
        for key in self.doors:
            value = self.doors[key]
            if value == [y, x]:
                new_room = key
        for door in self.game.room[self.player_room_index].door:
            if new_room == door.attrs['id'] and door.attrs['condition'] == 'open':
                logging.debug(self.player_room_index)
                self.player_room_name = door.attrs['connect_to']
                logging.debug(self.player_room_name)
                new_room = True
            elif new_room == door.attrs['id'] and door.attrs['condition'] == 'locked':
                inventory_items = ''
                for item in self.game.player[0].item:
                    inventory_items += item.attrs['name']
                if door.attrs['requirements'] in inventory_items:
                    door.attrs['condition'] = 'open'
                    result += 'You unlocked this door with '
                    result += door.attrs['requirements']
                    self.print_to_dialog(result)
                    time.sleep(0.02)
                    self.change_room(y, x)
                else:
                    result += 'You cannot open this door you need '
                    result += door.attrs['requirements']
                    self.print_to_dialog(result)
        return new_room


    def open_treasure(self, y, x):
        """Opens treasure chest and retrieves items"""
        treasure_id = False
        result = ''
        for key in self.treasures:
            value = self.treasures[key]
            if value == [y, x]:
                treasure_id = key
        for treasure in self.game.room[self.player_room_index].treasure:
            if treasure_id == treasure.attrs['id'] and treasure.attrs['condition'] == 'open':
                result += 'You have received '
                treasure_len=len(treasure.item)
                treasure.attrs['status'] = 'empty'
                for item_index, item in enumerate(treasure.item):
                    self.game.player[0].item.append(item)
                    if item_index == treasure_len-1:
                        result += item.attrs['name'] + '.'
                    elif item_index == treasure_len-2:
                        result += item.attrs['name'] + ' and '
                    else:
                        result += item.attrs['name'] + ', '
                self.screen.addch(y, x, ' ')
                self.print_to_dialog(result)

            elif treasure_id == treasure.attrs['id'] and treasure.attrs['condition'] == 'locked':
                inventory_items = ''
                for item in self.game.player[0].item:
                    inventory_items += item.attrs['name']
                if treasure.attrs['requirements'] in inventory_items:
                    treasure.attrs['condition'] = 'open'
                    result += 'You unlocked this treasure chest with '
                    result += treasure.attrs['requirements']
                    self.print_to_dialog(result)
                    time.sleep(0.02)
                    self.open_treasure(y, x)
                else:
                    result += 'You cannot open this treasure chest you need '
                    result += treasure.attrs['requirements']
                    self.print_to_dialog(result)

    def interact(self):
        """Player interaction with doors and items"""
        neighbors = []
        neighbors.append([self.player_position[0]-1, self.player_position[1], self.screen.inch(self.player_position[0]-1, self.player_position[1])])
        neighbors.append([self.player_position[0]+1, self.player_position[1], self.screen.inch(self.player_position[0]+1, self.player_position[1])])
        neighbors.append([self.player_position[0], self.player_position[1]+1, self.screen.inch(self.player_position[0], self.player_position[1]+1)])
        neighbors.append([self.player_position[0], self.player_position[1]-1, self.screen.inch(self.player_position[0], self.player_position[1]-1)])
        for y, x, char in neighbors:
            if char == ord(self.treasure_symbol):
                self.open_treasure(y, x)
            elif char == ord(self.door_symbol):
                result = self.change_room(y, x)
                logging.debug(result)
                if result:
                    self.player_position = self.display_room()
                    logging.debug(self.player_room_index)

    def print_to_dialog(self, text):
        """Prints to area below the map and separating line"""
        text_len = len(text)
        spacing = 5
        self.screen.hline(self.separate_line_y+spacing, 0, ord(' '), self.dims[1])
        self.screen.addstr(self.separate_line_y+spacing, (self.dims[1]/2)-(text_len/2), text, curses.A_BOLD)


    def game_menu(self):
        """Game menu"""
        pass

    def main_menu(self):
        """Main menu to the game to get started"""
        self.screen.nodelay(0)
        self.dims = self.screen.getmaxyx()
        selection = -1
        option = 0

        while selection != 2:                   #while exit has not been selected
            self.screen.clear()
            graphics = [0]*3
            graphics[option] = curses.A_REVERSE
            self.screen.addstr(self.dims[0]/2-2, self.dims[1]/2-5, 'Begin Game', graphics[0]|curses.A_BOLD)
            self.screen.addstr(self.dims[0]/2-1, self.dims[1]/2-4, 'Load Game', graphics[1]|curses.A_BOLD)
            self.screen.addstr(self.dims[0]/2, self.dims[1]/2-2, 'Exit', graphics[2]|curses.A_BOLD)
            self.screen.refresh()
            action = self.screen.getch()

            if action == curses.KEY_UP:
                option = (option -1) % 3
            elif action == curses.KEY_DOWN:
                option = (option +1) % 3
            elif action == ord('\n'):
                selection = option
            elif action == ord('q'):
                break

            if selection == 0:
                self.play()
            elif selection == 1:
                self.load_game()
            elif selection == 2:
                break

    def read_text(self, file_name):
        """Reads in text file and returns it as a list of strings"""
        fh = open(file_name, 'r')
        lines = [line.lstrip() for line in fh.readlines()]
        fh.close()
        return lines

if __name__ == '__main__':
    jp = jurassicpark()
    try:
        curses.wrapper(jp.main)
    except:
        out=traceback.format_exc()
        logging.debug(out)
        curses.endwin()
