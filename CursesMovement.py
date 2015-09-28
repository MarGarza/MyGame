__author__ = 'mgarza'

import curses,time

def lazer(y, x):
    screen.nodelay(1)
    #player=screen.getch(y,x)
    lazer=[y, x+1]
    end = False
    direction = 0
    toscreen='-'
    while not end:
        screen.addch(lazer[0], lazer[1], toscreen,curses.color_pair(1)|curses.A_BOLD)
        screen.refresh()
        if direction == 0:
            screen.addch(lazer[0], lazer[1], ' ')
            lazer[1] += 1
        if screen.inch(lazer[0], lazer[1]+len(toscreen)) != ord(' '):
            end = True
        time.sleep(0.025)

def player(y, x):
    piece = '@'
    q=-1
    player = [y, x]
    while q != ord('q'):
        screen.addch(player[0], player[1], piece)
        screen.refresh()
        q = screen.getch()        #gets user input
        if q == curses.KEY_UP and player[0] > 1:
            screen.addch(player[0], player[1], ' ')
            player[0] -= 1
        elif q == curses.KEY_DOWN and player[0] < dim[0]-2:
            screen.addch(player[0], player[1], ' ')
            player[0] += 1
        elif q == curses.KEY_LEFT and player[1] > 1:
            screen.addch(player[0], player[1], ' ')
            player[1] -= 2
        elif q == curses.KEY_RIGHT and player[1] < dim[1]-len(piece)-2:
            screen.addch(player[0], player[1], ' ')
            player[1] += 2
        elif q == ord(' '):
            lazer(player[0], player[1])

screen = curses.initscr()
screen.clear()
dim = screen.getmaxyx()
screen.keypad(1)
curses.curs_set(0)
curses.start_color()
curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
curses.noecho()
screen.border()

player(4, 4)
curses.endwin()