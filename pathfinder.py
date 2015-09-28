import numpy, curses, logging
from heapq import *

class astar(object):
    '''This class uses the A* algorithm to return list of tuples on shortest path from start to goal. Note: coordinates are x,y'''

    def __init__(self, screen, start, goal, map_dims, space, enemy_symbol, player_symbol):
        self._screen = screen
        self._start = start
        self._goal = goal
        self._map_dims = map_dims
        self._space = space
        self._enemy_symbol = enemy_symbol
        self._player_symbol = player_symbol


    def get_shortest_path(self):
        yrange, xrange = self._map_dims
        map = self._make_array(self._screen, yrange, xrange, self._space, self._enemy_symbol, self._player_symbol)
        new_start = (self._start[0]-yrange[0], self._start[1]-xrange[0])
        new_goal = (self._goal[0]-yrange[0], self._goal[1]-xrange[0])
        data = self._astar(map, new_start, new_goal)
        if data:
            next_step = data[-1]
            step = [next_step[0]+yrange[0], next_step[1]+xrange[0]]
            return step
        else:
            return None


    def _heuristic(self, a, b):
        '''returns distance from cell a to cell b'''
        return (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2

    def _astar(self, array, start, goal):
        '''returns list of tuples shortest distance from start cell to goal cell'''
        neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]  #for 4 directions #,(1,1),(1,-1),(-1,1),(-1,-1)] #for all 8 directions
        close_set = set()                        #walls or already checked cells
        came_from = {}
        gscore = {start: 0}
        fscore = {start: self._heuristic(start, goal)} #distance from start to end
        oheap = []
        heappush(oheap, (fscore[start], start))  #push fscore to oheap

        while oheap:
            current = heappop(oheap)[1]          #return smallest fscore
            if current == goal:                  #when goal has been reached
                data = []
                while current in came_from:
                    data.append(current)
                    current = came_from[current]
                return data
            close_set.add(current)               #add position to closed set
            for i, j in neighbors:
                neighbor = current[0] + i, current[1] + j   #gets neighboring cells
                tentative_g_score = gscore[current] + self._heuristic(current, neighbor)
                if 0 <= neighbor[0] < array.shape[0]:   #if neighbor in map
                    if 0 <= neighbor[1] < array.shape[1]:
                        if array[neighbor[0]][neighbor[1]] == 1:
                            continue
                    else:
                        # array bound y walls
                        continue
                else:
                    # array bound x walls
                    continue
                if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                    continue

                if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1]for i in oheap]:
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + self._heuristic(neighbor, goal)
                    heappush(oheap, (fscore[neighbor], neighbor))

        return False                            #returns false if no path is found

    def _make_array(self, screen, yrange, xrange, space, enemy_symbol, player_symbol):
        map = []
        for row in range(int(yrange[0]), int(yrange[1]), 1):
            current_row = []
            for column in range(int(xrange[0]), int(xrange[1]), 1):
                cell = screen.inch(row, column)
                if cell == space or cell == enemy_symbol or cell == player_symbol:
                    current_row.extend([0])
                else:
                    current_row.extend([1])
            map.append(current_row)
        nmap = numpy.array(map)
        return nmap
