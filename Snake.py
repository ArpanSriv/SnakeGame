import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_DOWN, KEY_UP
from random import randint
import time
import sqlite3
from consolemenu import *
from consolemenu.items import *

WIDTH = 35
HEIGHT = 20
MAX_X = WIDTH - 2
MAX_Y = HEIGHT - 2
SNAKE_LENGTH = 1
SNAKE_X = SNAKE_LENGTH + 1
SNAKE_Y = 3
TIMEOUT = 100
PLAYER_NAME = "Anonymous"
conn = sqlite3.connect("highscores.db")
level = 0

class Snake(object):
    REV_DIR_MAP = {
        KEY_UP: KEY_DOWN, KEY_DOWN: KEY_UP,
        KEY_LEFT: KEY_RIGHT, KEY_RIGHT: KEY_LEFT,
    }

    def __init__(self, x, y, window):
        self.body_list = []
        self.hit_score = 0
        self.timeout = TIMEOUT

        for i in range(SNAKE_LENGTH, 0, -1):
            self.body_list.append(Body(x - i, y))

        self.body_list.append(Body(x, y, '0'))
        self.window = window
        self.direction = KEY_RIGHT
        self.last_head_coor = (x, y)
        self.direction_map = {
            KEY_UP: self.move_up,
            KEY_DOWN: self.move_down,
            KEY_LEFT: self.move_left,
            KEY_RIGHT: self.move_right
        }
        
    @property
    def get_score(self):
        return self.hit_score

    @property
    def score(self):
        return 'Score: {}'.format(self.hit_score)

    def add_body(self, body_list):
        self.body_list.extend(body_list)

    def eat_food(self, food):
        food.reset()
        body = Body(self.last_head_coor[0], self.last_head_coor[1])
        self.body_list.insert(-1, body)
        self.hit_score += 1
        if self.hit_score % 3 == 0:
            self.timeout -= 5
            self.window.timeout(self.timeout)

    @property
    def collided(self):
        return any([body.coor == self.head.coor
                    for body in self.body_list[:-1]])

    def update(self):
        last_body = self.body_list.pop(0)
        last_body.x = self.body_list[-1].x
        last_body.y = self.body_list[-1].y
        self.body_list.insert(-1, last_body)
        self.last_head_coor = (self.head.x, self.head.y)
        self.direction_map[self.direction]()

    def change_direction(self, direction):
        if direction != Snake.REV_DIR_MAP[self.direction]:
            self.direction = direction

    def render(self):
        for body in self.body_list:
            self.window.addstr(body.y, body.x, body.char)

    @property
    def head(self):
        return self.body_list[-1]

    @property
    def coor(self):
        return self.head.x, self.head.y

    def move_up(self):
        self.head.y -= 1
        if self.head.y < 1:
            self.head.y = MAX_Y

    def move_down(self):
        self.head.y += 1
        if self.head.y > MAX_Y:
            self.head.y = 1

    def move_left(self):
        self.head.x -= 1
        if self.head.x < 1:
            self.head.x = MAX_X

    def move_right(self):
        self.head.x += 1
        if self.head.x > MAX_X:
            self.head.x = 1


class Body(object):
    def __init__(self, x, y, char='='):
        self.x = x
        self.y = y
        self.char = char

    @property
    def coor(self):
        return self.x, self.y


class Food(object):
    def __init__(self, window, char='&'):
        self.x = randint(1, MAX_X)
        self.y = randint(1, MAX_Y)
        self.char = char
        self.window = window

    def render(self):
        self.window.addstr(self.y, self.x, self.char)

    def reset(self):
        self.x = randint(1, MAX_X)
        self.y = randint(1, MAX_Y)


        
def start_game(level):    
    
    if (level == 0): 
        TIMEOUT = 140
        
    elif (level == 1): 
        TIMEOUT = 120
        
    elif (level == 2): 
        TIMEOUT = 100
        
    elif (level == 3): 
        TIMEOUT = 80
        
    elif (level == 4): 
        TIMEOUT = 60
    
    curses.initscr()
    window = curses.newwin(HEIGHT, WIDTH, 0, 0)
    window.timeout(TIMEOUT)
    window.keypad(1)
    curses.noecho()
    curses.curs_set(0)
    window.border(0)

    snake = Snake(SNAKE_X, SNAKE_Y, window)
    food = Food(window, '*')
    
    start_time = time.time()
    
    while True:
        elapsed_time = time.time() - start_time
        
        window.clear()
        window.border(0)
        snake.render()
        food.render()

        window.addstr(0, 5, snake.score)
        window.addstr(0, 20, "Time: {0:.1f}".format(elapsed_time))
        event = window.getch()
        
        if event == 27:
            break

        if event in [KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT]:
            snake.change_direction(event)

        if snake.head.x == food.x and snake.head.y == food.y:
            snake.eat_food(food)

        if event == 32:
            key = -1
            while key != 32:
                key = window.getch()

        snake.update()
        if snake.collided:
            break


    curses.endwin()
    
    end_time = time.time()
#    print(elapsed_time)
#    
    PLAYER_NAME = raw_input("Please enter your name: ")
    
    conn.execute('''INSERT INTO player_scores (name, score, time) VALUES ("{}", {}, {})'''.format(PLAYER_NAME, snake.get_score, elapsed_time));
    conn.commit()  


def display_levels():
    levels = ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5"]
    
    menu = SelectionMenu(levels, "Select an option")
    menu.show()
    menu.join()
    level = menu.selected_option
    
    start_game(level)
    
    
    
def display_highscores():
    hs_tuple = []
    
    for row in cursor:
        hs_tuple.append("{0} scored {1} in {2:.1f}s".format(row[0], row[1], row[2]))
        
    highscore_submenu = SelectionMenu(hs_tuple, "Highscores")
    highscore_submenu.show()
    
if __name__ == '__main__':  
    
    cursor = conn.execute("SELECT name, score, time FROM player_scores;")

    main_menu = ['Start Game', 'Highscores']
    
    while True:
        
        selection_main = SelectionMenu.get_selection(main_menu)

        try:
            if (selection_main == 0):
                display_levels()

            elif (selection_main == 1):
                display_highscores()
                
            elif (selection_main == 2):
                break
                
        except KeyboardInterrupt: 
            print "Thank you!"
    
    conn.close()
