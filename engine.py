__author__ = 'mgarza'
# coding=UTF-8

import curses, logging, sys, subprocess, threading, time, math, random
import ui, JurassicParkTemplate, ending


class Gameplay(object):
    """
    This class holds all the mechanics for playing the Jurassic Park Shooting Adventure
    """

    def __init__(self, screen, file='JurassicParkObjects.xml'):
        logging.basicConfig(filename='engine.log', level=logging.DEBUG)
        self.display = ui.Display(screen)
        self._game = self._grab_game_objects(file)
        self.rooms = {room.attrs['id']: index for (index, room) in enumerate(self._game.room)}
        self.current_room_id = self._game.player[0].attrs['position']
        self._current_room_index = int(self.rooms[self.current_room_id])
        self._current_room = self._game.room[self._current_room_index]
        self._treasures, self._doors, self._movement_calls, = {}, {}, {}
        self.player_health = self._set_health()
        self.inventory = [item for item in self._game.player[0].item]
        self.separate_line_y = False
        self.player_piece, self.replace_space = 2097728, 1049390
        self.treasure_symbol, self.door_symbol, self.interactive_item = 2097444, 2097477, 2097513
        self.enemy_V, self.enemy_D, self.enemy_C = 2098774, 2098756, 2098755
        self._potion_power = 25
        self.facing_direction = 'right'
        self.game_status = 'alive'
        self.weapon_name = ''

    def change_game_status(self, status):
        self.game_status = status

    def _grab_game_objects(self, file, desc=JurassicParkTemplate):
        """Grabs all game objects from xml provided, returns game object"""
        with open(file) as f:
            xml_data = f.read()
        successful, game = desc.obj_wrapper(xml_data)
        if not successful:
            raise game
        return game

    def _set_health(self):
        """Sets player's health to max for the player's level"""
        for index, level in enumerate(self._game.player[0].level):
            if level.attrs['level'] == str(self._game.player[0].attrs['level']):
                return int(level.attrs['max_health'])

    def _update_player_stats(self, health_diff=0, defense_diff=0, strength_diff=0, experience_diff=0):
        '''Updates player stats and info on screen returns string if leveling occured'''
        out_message = ''
        self._game.player[0].attrs['experience'] = int(self._game.player[0].attrs['experience']) + int(experience_diff)
        for index, level in enumerate(self._game.player[0].level):
            if level.attrs['level'] == str(self._game.player[0].attrs['level']):
                new_health = int(self.player_health) + int(health_diff)
                self.player_health = new_health if new_health <= int(level.attrs['max_health']) else int(
                    level.attrs['max_health'])
                level.attrs['defense'] = int(level.attrs['defense']) + int(defense_diff)
                level.attrs['strength'] = int(level.attrs['strength']) + int(strength_diff)
                exp_points = int(level.attrs['exp_to_next'])
                if int(self._game.player[0].attrs['experience']) >= exp_points:
                    thread = threading.Thread(target=subprocess.call, args=[['afplay', 'Sound/level.wav']])
                    thread.deamon = True
                    thread.start()
                    self._game.player[0].attrs['level'] = int(self._game.player[0].attrs['level']) + 1
                    self.player_health = self._game.player[0].level[index + 1].attrs['max_health']
                    out_message = 'Huzzah you have leveled up to level ' + str(self._game.player[0].attrs['level'])
        num_potions = len([item.attrs['name'] for item in self.inventory if item.attrs['type'] == 'potion'])

        weapons = [[item.attrs['name'], item.attrs['strength']] for item in self.inventory if
                   item.attrs['type'] == 'weapon']
        weapon_strength = 0
        for weapon in weapons:
            if int(weapon[1]) >= weapon_strength:
                weapon_strength = int(weapon[1])
                self.weapon_name = weapon[0]

        player_stats = 'Health: ' + str(self.player_health) + '    Potions: ' + str(num_potions) + '    Level: ' + str(
            self._game.player[0].attrs['level'])
        player_stats_cont = 'Experience Points: ' + str(
            self._game.player[0].attrs['experience']) + '    Weapon: ' + self.weapon_name
        text = [player_stats, player_stats_cont]
        self.display.text_to_dialog(text, 5)
        if self.player_health <= 0:
            self.game_status = 'dead'
        return out_message

    def _player_stats(self):
        '''Returns player's health strength experience and defense'''
        player_stats = []
        player_level = str(self._game.player[0].attrs['level'])
        weapon_strength = 0
        weapons = [[item.attrs['name'], item.attrs['strength']] for item in self.inventory if
                   item.attrs['type'] == 'weapon']
        for weapon in weapons:
            if int(weapon[1]) >= weapon_strength:
                weapon_strength = int(weapon[1])
        for level in self._game.player[0].level:
            if level.attrs['level'] == player_level:
                max_health = level.attrs['max_health']
                defense = level.attrs['defense']
                strength = int(level.attrs['strength']) + weapon_strength
                exp_to_next = level.attrs['exp_to_next']
                player_stats = [max_health, defense, strength, exp_to_next]
        return player_stats

    def _enemy_stats(self, enemy):
        '''returns enemy stats in a list for enemy level'''
        enemy_stats = []
        enemy_y, enemy_x = enemy.attrs['coordinates'].split(',')
        enemy_coord = [int(enemy_y), int(enemy_x)]

        if enemy.attrs['type'] == 'Compsognathus':
            enemy_symbol = self.enemy_C
        elif enemy.attrs['type'] == 'Dilophosaurus':
            enemy_symbol = self.enemy_D
        else:
            enemy_symbol = self.enemy_V

        for enemy_group in self._game.enemy:
            if enemy_group.attrs['name'] == enemy.attrs['type']:
                enemy_speed = enemy_group.attrs['movement_interval']
                for level in enemy_group.level:
                    if level.attrs['level'] == enemy.attrs['level']:
                        enemy_health = level.attrs['health']
                        enemy_strength = level.attrs['strength']
                        enemy_exp_points = level.attrs['exp_points']
                        enemy_stats = [enemy_health, enemy_coord, enemy_strength, enemy_exp_points, enemy_speed,
                                       enemy_symbol]

        return enemy_stats

    def _check_inventory(self, object):
        """Checks inventory for items that unhide doors or treasures"""
        if object.attrs['hidden'] == 'True':
            requirement = object.attrs['unhide'].split(',')
            inventory = [item.attrs['name'] for item in self.inventory]
            if set(requirement).issubset(set(inventory)):
                thread = threading.Thread(target=subprocess.call, args=[['afplay', 'Sound/door_unlock.wav']])
                thread.deamon = True
                thread.start()
                object.attrs['hidden'] = 'False'

    def _setup_room(self, player_position):
        """Sets up parameters needed for current room"""
        self._movement_calls = {}
        self._treasures = {treasure.attrs['id']: [treasure.attrs['coordinates'], indx] for indx, treasure in
                           enumerate(self._current_room.treasure) if treasure}
        self._doors = {door.attrs['id']: [door.attrs['coordinates'], indx] for indx, door in
                       enumerate(self._current_room.door) if door}
        self.shots = 0

        for treasure_id, treasure_info in self._treasures.items():  # Add treasures to room
            treasure_coord, indx = treasure_info
            y, x = treasure_coord.split(',')
            coord = [int(y), int(x)]
            self._check_inventory(self._current_room.treasure[indx])
            hidden = self._current_room.treasure[indx].attrs['hidden']
            id = self._current_room.treasure[indx].attrs['id']
            if 'bones' in id and hidden == 'False' or 'computer' in id and hidden == 'False':
                self._treasures[treasure_id] = [self.display.add_char(coord, self.interactive_item, modify=True), indx]
            elif self._current_room.treasure[indx].attrs['status'] == 'full' and hidden == 'False':
                self._treasures[treasure_id] = [self.display.add_char(coord, self.treasure_symbol, modify=True), indx]
            else:
                self._treasures[treasure_id] = [self.display.add_char(coord, self.replace_space, modify=True), indx]

        for door_id, door_info in self._doors.items():  # Add doors to room
            door_coord, indx = door_info
            y, x = door_coord.split(',')
            coord = [int(y), int(x)]
            self._check_inventory(self._current_room.door[indx])
            hidden = self._current_room.door[indx].attrs['hidden']
            if hidden == 'False':
                self._doors[door_id] = [self.display.add_char(coord, self.door_symbol, modify=True), indx]
            else:
                self._doors[door_id] = [self.display.add_char(coord, self.replace_space, modify=True), indx]

        update_time = time.time() + 0.5
        for enemy in self._current_room.enemy:
            enemy_id = 'enemy.' + enemy.attrs['id']
            enemy_health, enemy_coord, enemy_strength, enemy_exp_points, enemy_speed, enemy_symbol = self._enemy_stats(
                enemy)
            new_coord = self.display.add_char(enemy_coord, enemy_symbol, modify=True)
            self._enemy_movement(enemy_id, new_coord, player_position, enemy_symbol, enemy_strength, enemy_health,
                                 enemy_exp_points, enemy_speed, update_time)
        self._update_player_stats()

    def _process_input(self, command, player_position):
        """Takes input and reacts to command"""
        new_position = player_position
        neighbors = self.display.get_neighbors(player_position)

        if command == curses.KEY_UP:
            if self.facing_direction == 'up' and neighbors['up'][0] == self.replace_space:
                self.display.add_char(player_position, self.replace_space)
                new_position[0] -= 1
                self.display.add_char(new_position, self.player_piece)
            else:
                self.facing_direction = 'up'
        elif command == curses.KEY_DOWN:
            if self.facing_direction == 'down' and neighbors['down'][0] == self.replace_space:
                self.display.add_char(player_position, self.replace_space)
                new_position[0] += 1
                self.display.add_char(new_position, self.player_piece)
            else:
                self.facing_direction = 'down'
        elif command == curses.KEY_LEFT:
            if self.facing_direction == 'left' and neighbors['left'][0] == self.replace_space:
                self.display.add_char(player_position, self.replace_space)
                new_position[1] -= 1
                self.display.add_char(new_position, self.player_piece)
            else:
                self.facing_direction = 'left'
        elif command == curses.KEY_RIGHT:
            if self.facing_direction == 'right' and neighbors['right'][0] == self.replace_space:
                self.display.add_char(player_position, self.replace_space)
                new_position[1] += 1
                self.display.add_char(new_position, self.player_piece)
            else:
                self.facing_direction = 'right'

        elif command == ord('c'):
            new_position = self._interact(player_position)
        elif command == ord('x'):
            cured = self._heal()
            if cured:
                thread = threading.Thread(target=subprocess.call, args=[['afplay', 'Sound/cure.wav']])
                thread.deamon = True
                thread.start()
        elif command == ord(' '):
            bullet_id = 'bullet' + str(self.shots)
            soundfile = 'Sound/' + self.weapon_name + '.wav'
            thread = threading.Thread(target=subprocess.call, args=[['afplay', soundfile]])
            thread.deamon = True
            thread.start()
            player_stats = self._player_stats()
            player_strength = int(player_stats[2])
            self._shoot(bullet_id, player_position, self.facing_direction, player_strength)
            self.shots += 1
        elif command == ord('p'):
            self._pause()

        return new_position

    def _re_display(self):
        """re-displays treasure and door icons in room"""
        for treasure_id, treasure_info in self._treasures.items():  # Add treasures to room
            treasure_coord, indx = treasure_info
            y, x = treasure_coord
            treasure_coord = [int(y), int(x)]
            self._check_inventory(self._current_room.treasure[indx])
            hidden = self._current_room.treasure[indx].attrs['hidden']
            id = self._current_room.treasure[indx].attrs['id']
            if 'bones' in id and hidden == 'False' or 'computer' in id and hidden == 'False':
                self._treasures[treasure_id] = [self.display.add_char(treasure_coord, self.interactive_item), indx]
            elif self._current_room.treasure[indx].attrs['status'] == 'full' and hidden == 'False':
                self._treasures[treasure_id] = [self.display.add_char(treasure_coord, self.treasure_symbol), indx]
        for door_id, door_info in self._doors.items():  # Add doors to room
            door_coord, indx = door_info
            y, x = door_coord
            door_coord = [int(y), int(x)]
            self._check_inventory(self._current_room.door[indx])
            hidden = self._current_room.door[indx].attrs['hidden']
            id = self._current_room.door[indx].attrs['id']
            if hidden == 'False':
                self._doors[door_id] = [self.display.add_char(door_coord, self.door_symbol), indx]

    def _change_room(self, coord):
        """Changes the player's current room"""
        new_room = False
        player_start = []
        for door_id, door_info in self._doors.items():
            door_coord, door_index = door_info
            if door_coord == coord:
                if self._current_room.door[door_index].attrs['condition'] == 'open' and \
                                self._current_room.door[door_index].attrs['hidden'] == 'False':
                    player_start = str(self._current_room.door[door_index].attrs['player_start']).split(',')
                    player_start = [int(player_start[0]), int(player_start[1])]
                    new_room = True
                    self.current_room_id = self._current_room.door[door_index].attrs['connect_to']
                    if self.current_room_id == 'Exit':
                        return new_room, player_start
                    self._current_room_index = int(self.rooms[self.current_room_id])
                    self._current_room = self._game.room[self._current_room_index]
                    thread = threading.Thread(target=subprocess.call, args=[['afplay', 'Sound/BOUNCE1.wav']])
                    thread.deamon = True
                    thread.start()
                elif self._current_room.door[door_index].attrs['condition'] == 'locked' and \
                                self._current_room.door[door_index].attrs['hidden'] == 'False':
                    inventory_items = [item.attrs['name'] for item in self.inventory]
                    if self._current_room.door[door_index].attrs['requirements'] in inventory_items:
                        self._current_room.door[door_index].attrs['condition'] = 'open'
                        thread = threading.Thread(target=subprocess.call, args=[['afplay', 'Sound/door_unlock.wav']])
                        thread.deamon = True
                        thread.start()
                        result = ['You have unlocked the door with ' + str(
                            self._current_room.door[door_index].attrs['requirements'])]
                        self.display.text_to_dialog(result, self.display.separate_line_y + 4, clear_low=True)
                    else:
                        result = ['You cannot open this door you need the ' + str(
                            self._current_room.door[door_index].attrs['requirements'])]
                        self.display.text_to_dialog(result, self.display.separate_line_y + 4, clear_low=True)
        return new_room, player_start

    def _add_inventory(self, coord, treasure_index, type):
        """Adds items in treasure to player inventory returns response in a string"""
        result = ''
        thread = threading.Thread(target=subprocess.call, args=[['afplay', 'Sound/open.wav']])
        thread.deamon = True
        thread.start()
        treasure_len = len(self._current_room.treasure[treasure_index].item)
        self._current_room.treasure[treasure_index].attrs['status'] = 'empty'
        result += 'You have received '
        for item_index, item in enumerate(self._current_room.treasure[treasure_index].item):
            self.inventory.append(item)
            if item_index == treasure_len - 1:
                result += item.attrs['name'] + '.'
            elif item_index == treasure_len - 2:
                result += item.attrs['name'] + ' and '
            else:
                result += item.attrs['name'] + ', '
            if item.attrs['type'] == 'weapon':
                result += ' It adds ' + item.attrs['strength'] + ' points to your strength!'
        if type == 'treasure':
            self.display.add_char(coord, self.replace_space)
        self._update_player_stats()

        return result

    def _open_treasure(self, coord, type='treasure'):
        """Opens treasure chest and retrieves items"""
        result = []
        for treasure_id, treasure_info in self._treasures.items():  # Add treasures to room
            treasure_coord, indx = treasure_info
            if coord == treasure_coord:
                condition = self._current_room.treasure[indx].attrs['condition']
                status = self._current_room.treasure[indx].attrs['status']
                id = str(self._current_room.treasure[indx].attrs['id'])
                if 'computer' in id:
                    type = 'computer'
                if condition == 'open' and status == 'full':
                    result.append(self._add_inventory(coord, indx, type))
                elif condition == 'locked' and status == 'full':
                    inventory_items = [item.attrs['name'] for item in self.inventory]
                    requirement = self._current_room.treasure[indx].attrs['requirements']
                    if requirement in inventory_items:
                        thread = threading.Thread(target=subprocess.call, args=[['afplay', 'Sound/door_unlock.wav']])
                        thread.deamon = True
                        thread.start()
                        self._current_room.treasure[indx].attrs['condition'] = 'open'
                        if type == 'treasure':
                            result.append('You unlocked this treasure chest with ' + requirement)
                        elif type == 'computer':
                            result.append('You used ' + requirement + ' to log in as John Hammond')
                        elif type == 'bones':
                            result.append('You added the ' + requirement + ' to the display')
                        result.append(self._add_inventory(coord, indx, type))
                    else:
                        if type == 'treasure':
                            result.append('You cannot open this treasure chest you need the ' + requirement)
                        elif type in ('bones', 'computer'):
                            text = [text.value for text in self._current_room.treasure[indx].include if
                                    text.attrs['id'] == condition][0]
                            result.append(text)
                elif type in ('bones', 'computer'):
                    text = \
                    [text.value for text in self._current_room.treasure[indx].include if text.attrs['id'] == condition][
                        0]
                    result.append(text)
            self._re_display()
            self.display.text_to_dialog(result, self.display.separate_line_y + 4, clear_low=True)

    def _interact(self, player_position):
        """Player interaction with doors and items"""
        new_position = player_position
        neighbors = self.display.get_neighbors(player_position)

        for key, cell in neighbors.items():
            if key == 'up':
                interact_cell = [player_position[0] - 1, player_position[1]]
            elif key == 'down':
                interact_cell = [player_position[0] + 1, player_position[1]]
            elif key == 'left':
                interact_cell = [player_position[0], player_position[1] - 1]
            else:
                interact_cell = [player_position[0], player_position[1] + 1]

            if cell[0] == self.treasure_symbol:
                self._open_treasure(interact_cell)
            elif cell[0] == self.interactive_item:
                self._open_treasure(interact_cell, type='bones')
            elif cell[0] == self.door_symbol:
                result, player_start = self._change_room(interact_cell)
                if result:
                    if self.current_room_id == 'Exit':
                        win_type = len(
                            [item.attrs['name'] for item in self.inventory if item.attrs['name'] == 'Dinosaur Embryos'])
                        self.game_status = 'win' + str(win_type)
                    else:
                        new_position = self.display.display_room(self._current_room, player_start)
                        self._setup_room(new_position)
                        self.display.add_char(new_position, self.player_piece)
        return new_position

    def _shoot(self, bullet_id, start_coord, direction, strength, last_update=0):
        """Rifle always shoots right """
        if 'bullet' in bullet_id:
            interval = 0.025
            turnRed = 0
        else:
            interval = 0.05
            turnRed = 1024

        current_space = self.display.get_char(start_coord)
        bullet = 2097709
        bullet_coord = [start_coord[0], start_coord[1] + 1]  # default right

        if direction == 'up':
            interval = interval * 2
            bullet = 2097788
            bullet_coord = [start_coord[0] - 1, start_coord[1]]
        elif direction == 'down':
            interval = interval * 2
            bullet = 2097788
            bullet_coord = [start_coord[0] + 1, start_coord[1]]
        elif direction == 'left':
            bullet = 2097709
            bullet_coord = [start_coord[0], start_coord[1] - 1]

        next_space = self.display.get_char(bullet_coord)

        if current_space == bullet + turnRed:
            self.display.add_char(start_coord, self.replace_space)
        if next_space == self.replace_space:
            self.display.add_char(bullet_coord, bullet + turnRed)
            self._movement_calls[bullet_id] = [bullet_coord, interval, last_update, direction, self._shoot, '',
                                               strength, 0, 0]
        elif next_space in (self.enemy_V, self.enemy_D, self.enemy_C):
            self._player_attack(bullet_coord, strength)
            self._movement_calls.pop(bullet_id, None)
        elif next_space == self.player_piece:
            self._enemy_attack(strength)
            self._movement_calls.pop(bullet_id, None)
        else:
            self._movement_calls.pop(bullet_id, None)

    def _heal(self):
        '''Uses potion in inventory to increase player's health'''
        num_potions = len([item.attrs['name'] for item in self.inventory if item.attrs['type'] == 'potion'])
        player_stats = self._player_stats()
        max_health = player_stats[0]
        cured = False
        if num_potions:
            if self.player_health < int(max_health):
                potion = [item for item in self.inventory if item.attrs['type'] == 'potion'][0]
                self.inventory.remove(potion)
                t = self._update_player_stats(health_diff=self._potion_power)
                self.display.text_to_dialog(['You have used a potion'], self.display.separate_line_y + 4)
                cured = True
            else:
                self.display.text_to_dialog(['Your health is already maxed'], self.display.separate_line_y + 4)
        else:
            self.display.text_to_dialog(['You do not have any potions'], self.display.separate_line_y + 4)
        return cured

    def _player_attack(self, coord, strength):
        '''Handles attack for player to enemy'''
        for moving_id, moving_info in self._movement_calls.items():
            enemy_coord, interval, last_update, direction, function, enemy_symbol, enemy_strength, enemy_health, enemy_exp_points = moving_info
            if enemy_symbol == self.enemy_C:
                enemy_type = 'Compsognathus'
            elif enemy_symbol == self.enemy_D:
                enemy_type = 'Dilophosaurus'
            else:
                enemy_type = 'Velociraptor'
            if 'enemy' in moving_id and enemy_coord == coord:
                new_enemy_health = int(enemy_health) - int(strength)
                leveled = []
                if new_enemy_health <= 0:
                    thread = threading.Thread(target=subprocess.call, args=[['afplay', 'Sound/kill.wav']])
                    thread.deamon = True
                    thread.start()
                    self._movement_calls.pop(moving_id, None)
                    self.display.add_char(coord, self.replace_space)
                    leveled.append(
                        'You killed a ' + enemy_type + ' and received ' + enemy_exp_points + ' experience points ')
                    leveled.append(self._update_player_stats(experience_diff=enemy_exp_points))
                    enemies = len([obj for obj, move in self._movement_calls.items() if 'enemy' in obj])
                    # if no enemies check for hidden treasures or doors
                    if enemies == 0:
                        hidden = False
                        for treasure_id, treasure_info in self._treasures.items():  #Add treasures to room
                            coord, indx = treasure_info
                            if self._current_room.treasure[indx].attrs['hidden'] == 'True':
                                hidden = True
                                unhide = self._current_room.treasure[indx].attrs['unhide']
                                self._current_room.treasure[indx].attrs[
                                    'hidden'] = 'False' if unhide == 'no enemies' else 'True'

                        for door_id, door_info in self._doors.items():  #Add treasures to room
                            coord, indx = door_info
                            if self._current_room.door[indx].attrs['hidden'] == 'True':
                                hidden = True
                                unhide = self._current_room.treasure[indx].attrs['unhide']
                                self._current_room.treasure[indx].attrs[
                                    'hidden'] = 'False' if unhide == 'no enemies' else 'True'
                        if hidden:
                            thread = threading.Thread(target=subprocess.call,
                                                      args=[['afplay', 'Sound/door_unlock.wav']])
                            thread.deamon = True
                            thread.start()
                            self._re_display()

                    self.display.text_to_dialog(leveled, self.display.separate_line_y + 4)
                else:
                    self._movement_calls[moving_id] = [coord, interval, last_update, direction, function, enemy_symbol,
                                                       enemy_strength, new_enemy_health, enemy_exp_points]

    def _enemy_attack(self, enemy_strength):
        """Reduce players health by strength provided"""
        thread = threading.Thread(target=subprocess.call, args=[['afplay', 'Sound/hit.wav']])
        thread.deamon = True
        thread.start()
        self._update_player_stats(health_diff=-(int(enemy_strength)))

    def _enemy_movement(self, enemy_id, enemy_position, player_position, enemy_symbol, enemy_strength, enemy_health,
                        enemy_exp_points, enemy_speed, last_update=0):
        """Looks at neighbors and if player is spot player will take some damage"""
        move = True
        choices = []
        neighbors = self.display.get_neighbors(enemy_position)
        speed = float(enemy_speed)

        for key in neighbors:
            if neighbors[key][0] == self.player_piece:
                self._enemy_attack(enemy_strength)
                move = False
            elif neighbors[key][0] == self.replace_space:
                if key == 'up':
                    choices.append([enemy_position[0] - 1, enemy_position[1]])
                elif key == 'down':
                    choices.append([enemy_position[0] + 1, enemy_position[1]])
                elif key == 'left':
                    choices.append([enemy_position[0], enemy_position[1] - 1])
                else:
                    choices.append([enemy_position[0], enemy_position[1] + 1])

        if enemy_symbol == self.enemy_D and move:
            spit = self._enemy_spit(enemy_position, enemy_strength)
            if spit:
                move = False

        distance = math.hypot(player_position[1] - enemy_position[1], player_position[0] - enemy_position[0])
        if distance > 30 and last_update:
            move = False

        if move:  # move towards player if possible
            step = self.display.find_enemy_move(enemy_position, player_position, self.replace_space, enemy_symbol,
                                                self.player_piece)
            if step and self.display.get_char(step) == self.replace_space:
                self.display.add_char(enemy_position, self.replace_space)
                self.display.add_char(step, enemy_symbol)
                self._movement_calls[enemy_id] = [step, speed, last_update, None, self._enemy_movement, enemy_symbol,
                                                  enemy_strength, enemy_health,
                                                  enemy_exp_points]  #add to movement_calls
            else:
                self.display.add_char(enemy_position, enemy_symbol)
                self._movement_calls[enemy_id] = [enemy_position, speed, last_update, None, self._enemy_movement,
                                                  enemy_symbol, enemy_strength, enemy_health, enemy_exp_points]
        else:
            choice = random.choice(choices) if choices else enemy_position
            self.display.add_char(enemy_position, self.replace_space)
            self.display.add_char(choice, enemy_symbol)
            self._movement_calls[enemy_id] = [choice, speed, last_update, None, self._enemy_movement, enemy_symbol,
                                              enemy_strength, enemy_health, enemy_exp_points]

    def _enemy_spit(self, coord, enemy_strength):
        '''For enemy to spit at player'''
        y, x = coord
        direction = None
        neighbors = self.display.get_neighbors(coord, 0)

        for key, cells in neighbors.items():
            for cell in cells:
                if cell == self.replace_space or cell == self.player_piece:
                    if cell == self.player_piece:
                        direction = key
                        spit_id = 'spit' + str(self.shots)
                        self._shoot(spit_id, [y, x], direction, enemy_strength)
                        self.shots += 1
                else:
                    break
        return direction

    def _pause(self):
        """Throws game into while loop till user enters key"""
        action = self.display.get_input()
        while action != ord('p') or action != ord('q'):
            text = ['The game is paused', 'p: continue game    q: quit game']
            self.display.text_to_dialog(text, self.display.separate_line_y + 4, clear_low=True)
            action = self.display.get_input()
            if action == ord('q'):
                self.game_status = 'quit'
                break
            elif action == ord('p'):
                self.display.text_to_dialog([''], self.display.separate_line_y + 4, clear_low=True)
                break
            elif action != ord('s'):
                self._save()

    def _save(self):
        """Saves game state"""
        pass

    def _intro(self):
        """Displays the intro to the game"""
        image_file = str(self._game.intro[0].include[0].value.strip())  # add if type = image
        jpLogo = self.display.read_text(image_file)

        image_start = 2
        spacing = 2
        image_height = len(jpLogo)
        start_text = image_start + image_height + spacing

        thread = threading.Thread(target=subprocess.call, args=[['afplay', 'Sound/welcome.wav']])
        thread.deamon = True
        thread.start()

        for text_index in range(len(self._game.intro[0].text)):
            self.display.clear()
            text = [text.strip() for text in self._game.intro[0].text[text_index].value.split('\n')]
            self.display.ascii_to_screen(image_start, jpLogo, 4)
            self.display.ascii_to_screen(start_text, text)
            action = self.display.get_input()

    def _game_Over(self):
        """Runs game over screen"""
        action = True
        thread = threading.Thread(target=subprocess.call, args=[['afplay', 'Sound/cleaver.wav']])
        thread.deamon = True
        thread.start()
        top = self.display.read_text('ASCII/gameover.txt', strip=False)
        buffer = 12
        spacing = 4

        self.display.ascii_to_screen(buffer, top, 4, 57)
        message = ['Press Enter to go back to the main menu']
        self.display.text_to_dialog(message, buffer + spacing + len(top))
        while action:
            action = self.display.get_input()
            if action == ord('\n'):
                action = False

    def _ending(self, type='bad'):
        """Runs screen ending"""
        if type == 'bad':
            end_idx = 0
            width = 47
        else:
            end_idx = 1
            width = 60
        buffer = 5
        spacing = 2
        endings = self._grab_game_objects('endingcontent.xml', desc=ending)
        top = self.display.read_text('ASCII/escaped.txt', strip=False)

        action = -1
        thread = threading.Thread(target=subprocess.call, args=[['afplay', 'Sound/trex.wav']])
        thread.deamon = True
        thread.start()

        while action != ord('\n'):
            for image in endings.ending[end_idx].image:
                if action == ord('\n'):
                    break
                self.display.clear()
                self.display.ascii_to_screen(buffer, top, 4, 78)
                i = image.value.split('\n')
                self.display.ascii_to_screen(buffer + len(top) + spacing, i, 1, width)
                time.sleep(.10)
                action = self.display.get_input()

    def play(self, intro=True):
        """runs game"""
        if intro:
            self._intro()
        else:
            self.current_room_id = self._game.player[0].attrs['position']
            self._current_room_index = int(self.rooms[self.current_room_id])
            self._current_room = self._game.room[self._current_room_index]
            self.player_health = self._set_health()

        self.display.set_timeout(0)
        player_position = self.display.display_room(self._current_room)
        self._setup_room(player_position)
        self.display.add_char(player_position, self.player_piece)
        self._update_player_stats()

        while self.game_status == 'alive':
            action = self.display.get_input()
            if action != -1:
                player_position = self._process_input(action, player_position)

            if self._movement_calls:
                for object, moves in self._movement_calls.items():
                    ntime = time.time()
                    coord, interval, last_update, direction, function, enemy_symbol, strength, enemy_health, enemy_exp_points = moves

                    if ntime > last_update:
                        if 'bullet' in object or 'spit' in object:
                            last_update = time.time() + interval
                            function(object, coord, direction, strength, last_update)
                        else:
                            last_update = time.time() + interval
                            function(object, coord, player_position, enemy_symbol, strength, enemy_health,
                                     enemy_exp_points, interval, last_update)

        if self.game_status == 'dead':
            self.display.set_timeout(-1)
            self.display.clear()
            self._game_Over()
        elif self.game_status == 'win0':
            self.display.set_timeout(0)
            self.display.clear()
            self._ending()
        elif self.game_status == 'win1':
            self.display.set_timeout(0)
            self.display.clear()
            self._ending('good')