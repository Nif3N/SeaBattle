import pygame
import sys
import random
import copy

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

block_size = 50
left_margin = 200
upper_margin = 30

size = (left_margin + 30 * block_size, upper_margin + 15 * block_size)
LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
pygame.init()

screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
pygame.display.set_caption("Sea Battle")

font_size = int(block_size / 1.5)

font = pygame.font.SysFont('notosans', font_size)

computer_available_to_fire_set = set((a, b)
                                     for a in range(1, 11) for b in range(1, 11))
around_last_computer_hit_set = set()
hit_blocks = set()
dotted_set = set()
dotted_set_for_computer_not_to_shoot = set()
dotted_set_for_computer_to_shoot = set()
hit_blocks_for_computer_not_to_shoot = set()
last_hits_list = []
destroyed_ships_list = []

class Button():
	def __init__(self, image, pos, text_input, font, base_color, hovering_color):
		self.image = image
		self.x_pos = pos[0]
		self.y_pos = pos[1]
		self.font = font
		self.base_color, self.hovering_color = base_color, hovering_color
		self.text_input = text_input
		self.text = self.font.render(self.text_input, True, self.base_color)
		if self.image is None:
			self.image = self.text
		self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)

	def checkForInput(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			return True
		return False

	def changeColor(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.text_input, True, self.hovering_color)
		else:
			self.text = self.font.render(self.text_input, True, self.base_color)

class Grid:
    def __init__(self, title, offset):
        self.title = title
        self.offset = offset
        self.draw_grid()
        self.sign_grids()
        self.add_nums_letters_to_grid()

    def draw_grid(self):
        for i in range(11):
            # Horizontal lines
            pygame.draw.line(screen, BLACK, (left_margin+self.offset, upper_margin+i*block_size),
                             (left_margin+10*block_size+self.offset, upper_margin+i*block_size), 1)
            # Vertical lines
            pygame.draw.line(screen, BLACK, (left_margin+i*block_size+self.offset, upper_margin),
                             (left_margin+i*block_size+self.offset, upper_margin+10*block_size), 1)

    def add_nums_letters_to_grid(self):
        for i in range(10):
            num_ver = font.render(str(i+1), True, BLACK)
            letters_hor = font.render(LETTERS[i], True, BLACK)
            num_ver_width = num_ver.get_width()
            num_ver_height = num_ver.get_height()
            letters_hor_width = letters_hor.get_width()

            # Ver num grid1
            screen.blit(num_ver, (left_margin - (block_size//2+num_ver_width//2)+self.offset,
                                  upper_margin + i*block_size + (block_size//2 - num_ver_height//2)))
            # Hor letters grid1
            screen.blit(letters_hor, (left_margin + i*block_size + (block_size //
                                                                    2 - letters_hor_width//2)+self.offset, upper_margin + 10*block_size))

    def sign_grids(self):
        player = font.render(self.title, True, BLACK)
        sign_width = player.get_width()
        screen.blit(player, (left_margin + 5*block_size - sign_width //
                             2+self.offset, upper_margin - block_size//2 - font_size))

class ShipsOnGrid:
    def __init__(self):
        self.available_blocks = set((a, b)
                                    for a in range(1, 11) for b in range(1, 11))
        self.ships_set = set()
        self.ships = self.populate_grid()

    def create_start_block(self, available_blocks):
        x_or_y = random.randint(0, 1)
        str_rev = random.choice((-1, 1))
        x, y = random.choice(tuple(available_blocks))
        return x, y, x_or_y, str_rev

    def create_ship(self, number_of_blocks, available_blocks):
        ship_coordinates = []
        x, y, x_or_y, str_rev = self.create_start_block(available_blocks)
        for _ in range(number_of_blocks):
            ship_coordinates.append((x, y))
            if not x_or_y:
                str_rev, x = self.add_block_to_ship(
                    x, str_rev, x_or_y, ship_coordinates)
            else:
                str_rev, y = self.add_block_to_ship(
                    y, str_rev, x_or_y, ship_coordinates)
        if self.is_ship_valid(ship_coordinates):
            return ship_coordinates
        return self.create_ship(number_of_blocks, available_blocks)

    def add_block_to_ship(self, coor, str_rev, x_or_y, ship_coordinates):
        if (coor <= 1 and str_rev == -1) or (coor >= 10 and str_rev == 1):
            str_rev *= -1
            return str_rev, ship_coordinates[0][x_or_y] + str_rev
        else:
            return str_rev, ship_coordinates[-1][x_or_y] + str_rev

    def is_ship_valid(self, new_ship):
        ship = set(new_ship)
        return ship.issubset(self.available_blocks)

    def add_new_ship_to_set(self, new_ship):
        for elem in new_ship:
            self.ships_set.add(elem)

    def update_available_blocks_for_creating_ships(self, new_ship):
        for elem in new_ship:
            for k in range(-1, 2):
                for m in range(-1, 2):
                    if 0 < (elem[0]+k) < 11 and 0 < (elem[1]+m) < 11:
                        self.available_blocks.discard((elem[0]+k, elem[1]+m))

    def populate_grid(self):
        ships_coordinates_list = []
        for number_of_blocks in range(4, 0, -1):
            for _ in range(5-number_of_blocks):
                new_ship = self.create_ship(
                    number_of_blocks, self.available_blocks)
                ships_coordinates_list.append(new_ship)
                self.add_new_ship_to_set(new_ship)
                self.update_available_blocks_for_creating_ships(new_ship)
        return ships_coordinates_list


computer = ShipsOnGrid()
human = ShipsOnGrid()
computer_ships_working = copy.deepcopy(computer.ships)
human_ships_working = copy.deepcopy(human.ships)

def draw_ships(ships_coordinates_list):
    for elem in ships_coordinates_list:
        ship = sorted(elem)
        x_start = ship[0][0]
        y_start = ship[0][1]
        # Vert
        if len(ship) > 1 and ship[0][0] == ship[1][0]:
            ship_width = block_size
            ship_height = block_size * len(ship)
        # Hor and 1block
        else:
            ship_width = block_size * len(ship)
            ship_height = block_size
        x = block_size * (x_start - 1) + left_margin
        y = block_size * (y_start - 1) + upper_margin
        if ships_coordinates_list == human.ships:
            x += 15 * block_size
        pygame.draw.rect(
            screen, BLACK, ((x, y), (ship_width, ship_height)), width=block_size//10)
def draw_grid():
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    for i in range(11):
        # Hor grid1
        pygame.draw.line(screen, BLACK, (left_margin, upper_margin + i * block_size),
                         (left_margin + 10 * block_size, upper_margin + i * block_size), 1)
        # Vert grid1
        pygame.draw.line(screen, BLACK, (left_margin + i * block_size, upper_margin),
                         (left_margin + i * block_size, upper_margin + 10 * block_size), 1)
        # Hor grid2
        pygame.draw.line(screen, BLACK, (left_margin + 15 * block_size, upper_margin +
                                         i * block_size),
                         (left_margin + 25 * block_size, upper_margin + i * block_size), 1)
        # Vert grid2
        pygame.draw.line(screen, BLACK, (left_margin + (i + 15) * block_size, upper_margin),
                         (left_margin + (i + 15) * block_size, upper_margin + 10 * block_size), 1)

        if i < 10:
            num_ver = font.render(str(i + 1), True, BLACK)
            letters_hor = font.render(letters[i], True, BLACK)

            num_ver_width = num_ver.get_width()
            num_ver_height = num_ver.get_height()
            letters_hor_width = letters_hor.get_width()

            # Ver num grid1
            screen.blit(num_ver, (left_margin - (block_size // 2 + num_ver_width // 2),
                                  upper_margin + i * block_size + (block_size // 2 - num_ver_height // 2)))
            # Hor letters grid1
            screen.blit(letters_hor, (left_margin + i * block_size + (block_size //
                                                                      2 - letters_hor_width // 2),
                                      upper_margin + 10 * block_size))
            # Ver num grid2
            screen.blit(num_ver, (left_margin - (block_size // 2 + num_ver_width // 2) + 15 *
                                  block_size, upper_margin + i * block_size + (block_size // 2 - num_ver_height // 2)))
            # Hor letters grid2
            screen.blit(letters_hor, (left_margin + i * block_size + (block_size // 2 -
                                                                      letters_hor_width // 2) + 15 * block_size,
                                      upper_margin + 10 * block_size))

def sign_grids():
    player1 = font.render("COMPUTER", True, BLACK)
    player2 = font.render("HUMAN", True, BLACK)
    sign1_width = player1.get_width()
    sign2_width = player2.get_width()
    screen.blit(player1, (left_margin + 5*block_size - sign1_width //
                          2, upper_margin - block_size//2 - font_size))
    screen.blit(player2, (left_margin + 20*block_size - sign2_width //
                          2, upper_margin - block_size//2 - font_size))


def computer_shoots(set_to_shoot_from):
    pygame.time.delay(500)
    computer_fired_block = random.choice(tuple(set_to_shoot_from))
    computer_available_to_fire_set.discard(computer_fired_block)
    return check_hit_or_miss(computer_fired_block, human_ships_working, True)


def check_hit_or_miss(fired_block, opponents_ships_list, computer_turn, diagonal_only=True):
    for elem in opponents_ships_list:
        if fired_block in elem:
            update_dotted_and_hit_sets(
                fired_block, computer_turn, diagonal_only=True)
            ind = opponents_ships_list.index(elem)

            if len(elem) == 1:
                update_dotted_and_hit_sets(
                    fired_block, computer_turn, diagonal_only=False)

            elem.remove(fired_block)

            if computer_turn:
                last_hits_list.append(fired_block)
                human.ships_set.discard(fired_block)
                update_around_last_computer_hit(fired_block)
            else:
                computer.ships_set.discard(fired_block)

            if not elem:
                draw_destroyed_ships(ind, opponents_ships_list, computer_turn)
                if computer_turn:
                    last_hits_list.clear()
                    around_last_computer_hit_set.clear()
                else:
                    destroyed_ships_list.append(computer.ships[ind])

            return True
    put_dot_on_missed_block(fired_block, computer_turn)
    if computer_turn:
        update_around_last_computer_hit(fired_block, False)
    return False


def put_dot_on_missed_block(fired_block, computer_turn=False):
    if not computer_turn:
        dotted_set.add(fired_block)
    else:
        dotted_set.add((fired_block[0] + 15, fired_block[1]))
        dotted_set_for_computer_to_shoot.add(fired_block)


def draw_destroyed_ships(ind, opponents_ships_list, computer_turn, diagonal_only=False):
    if opponents_ships_list == computer_ships_working:
        ships_list = computer.ships
    elif opponents_ships_list == human_ships_working:
        ships_list = human.ships
    ship = sorted(ships_list[ind])
    for i in range(-1, 1):
        update_dotted_and_hit_sets(ship[i], computer_turn, diagonal_only)


def update_around_last_computer_hit(fired_block, computer_hits=True):
    global around_last_computer_hit_set, computer_available_to_fire_set
    if computer_hits and fired_block in around_last_computer_hit_set:
        around_last_computer_hit_set = computer_hits_twice()

    elif computer_hits and fired_block not in around_last_computer_hit_set:
        computer_first_hit(fired_block)

    elif not computer_hits:
        around_last_computer_hit_set.discard(fired_block)

    around_last_computer_hit_set -= dotted_set_for_computer_not_to_shoot
    around_last_computer_hit_set -= hit_blocks_for_computer_not_to_shoot
    computer_available_to_fire_set -= around_last_computer_hit_set
    computer_available_to_fire_set -= dotted_set_for_computer_not_to_shoot


def computer_first_hit(fired_block):
    xhit, yhit = fired_block
    if 1 < xhit:
        around_last_computer_hit_set.add((xhit-1, yhit))
    if xhit < 10:
        around_last_computer_hit_set.add((xhit+1, yhit))
    if 1 < yhit:
        around_last_computer_hit_set.add((xhit, yhit-1))
    if yhit < 10:
        around_last_computer_hit_set.add((xhit, yhit+1))


def computer_hits_twice():
    last_hits_list.sort()
    new_around_last_hit_set = set()
    for i in range(len(last_hits_list)-1):
        x1 = last_hits_list[i][0]
        x2 = last_hits_list[i+1][0]
        y1 = last_hits_list[i][1]
        y2 = last_hits_list[i+1][1]

        if x1 == x2:
            if y1 > 1:
                new_around_last_hit_set.add((x1, y1 - 1))
            if y2 < 10:
                new_around_last_hit_set.add((x1, y2 + 1))

        elif y1 == y2:
            if 1 < x1:
                new_around_last_hit_set.add((x1 - 1, y1))
            if x2 < 10:
                new_around_last_hit_set.add((x2 + 1, y1))

    return new_around_last_hit_set


def update_dotted_and_hit_sets(fired_block, computer_turn, diagonal_only=True):
    global dotted_set
    x, y = fired_block
    a, b = 0, 11
    if computer_turn:
        x += 15
        a += 15
        b += 15
        hit_blocks_for_computer_not_to_shoot.add(fired_block)
    hit_blocks.add((x, y))
    for i in range(-1, 2):
        for j in range(-1, 2):
            if diagonal_only:
                if i != 0 and j != 0 and a < x + i < b and 0 < y + j < 11:
                    dotted_set.add((x+i, y+j))
                    if computer_turn:
                        dotted_set_for_computer_not_to_shoot.add(
                            (fired_block[0]+i, y+j))
            else:
                if a < x + i < b and 0 < y + j < 11:
                    dotted_set.add((x+i, y+j))
                    if computer_turn:
                        dotted_set_for_computer_not_to_shoot.add((
                            fired_block[0]+i, y+j))
    dotted_set -= hit_blocks


def draw_from_dotted_set(dotted_set):
    for elem in dotted_set:
        pygame.draw.circle(screen, BLACK, (block_size*(
            elem[0]-0.5)+left_margin, block_size*(elem[1]-0.5)+upper_margin), block_size//6)


def draw_hit_blocks(hit_blocks):
    for block in hit_blocks:
        x1 = block_size * (block[0]-1) + left_margin
        y1 = block_size * (block[1]-1) + upper_margin
        pygame.draw.line(screen, BLACK, (x1, y1),
                         (x1+block_size, y1+block_size), block_size//6)
        pygame.draw.line(screen, BLACK, (x1, y1+block_size),
                         (x1+block_size, y1), block_size//6)

computer = ShipsOnGrid()
human = ShipsOnGrid()
computer_ships_working = copy.deepcopy(computer.ships)
human_ships_working = copy.deepcopy(human.ships)

SCREEN = pygame.display.set_mode(size, pygame.FULLSCREEN)
pygame.display.set_caption("Menu")
BG = pygame.image.load("assets/Background.jpg")

def get_font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/Seagull_Wine.ttf", size)

def options():
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("white")

        OPTIONS_TEXT = get_font(45).render("This is the OPTIONS screen.", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(640, 260))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_BACK = Button(image=None, pos=(640, 460),
                              text_input="Назад", font=get_font(75), base_color="Black", hovering_color="Green")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()

        pygame.display.update()

def main_menu():
    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("Главное меню", True, "Black")
        MENU_RECT = MENU_TEXT.get_rect(center=(960, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(960, 250),
                             text_input="Играть", font=get_font(75), base_color="Black", hovering_color="Red")
        OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(960, 400),
                                text_input="Настройки", font=get_font(75), base_color="Black", hovering_color="Red")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(960, 550),
                             text_input="Выход", font=get_font(75), base_color="Black", hovering_color="Red")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    main()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

def main():
    game_over = False
    computer_turn = False
    screen.fill(WHITE)
    computer_grid = Grid("Компьютер", 0)
    human_grid = Grid("Человек", 15 * block_size)
    KOMP_TEXT = get_font(35).render("Компьютер", True, "Black")
    KOMP_RECT = KOMP_TEXT.get_rect(center=(300, 15))
    SCREEN.blit(KOMP_TEXT, KOMP_RECT)
    USER_TEXT = get_font(35).render("Человек", True, "Black")
    USER_RECT = USER_TEXT.get_rect(center=(1020, 15))
    SCREEN.blit(USER_TEXT, USER_RECT)
    #draw_ships(computer.ships)
    draw_ships(human.ships)
    PLAY_BACK = Button(image=None, pos=(800, 640),
                       text_input="Назад", font=get_font(75), base_color="Black", hovering_color="Red")

    while not game_over:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()
        PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        PLAY_BACK.update(screen)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif not computer_turn and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if (left_margin <= x <= left_margin + 10 * block_size) and (
                        upper_margin <= y <= upper_margin + 10 * block_size):
                    fired_block = ((x - left_margin) // block_size + 1,
                                   (y - upper_margin) // block_size + 1)
                computer_turn = not check_hit_or_miss(fired_block, computer_ships_working, computer_turn)

            if computer_turn:
                if around_last_computer_hit_set:
                    computer_turn = computer_shoots(around_last_computer_hit_set)
                else:
                    computer_turn = computer_shoots(computer_available_to_fire_set)

            draw_from_dotted_set(dotted_set)
            draw_hit_blocks(hit_blocks)
            draw_ships(destroyed_ships_list)
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    main_menu()

main_menu()
pygame.quit()
