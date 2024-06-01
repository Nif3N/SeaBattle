import pygame
import sys
import random

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

block_size = 50
left_margin = 200
upper_margin = 30

size = (left_margin + 30 * block_size, upper_margin + 15 * block_size)

pygame.init()

screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
pygame.display.set_caption("Sea Battle")

font_size = int(block_size / 1.5)

font = pygame.font.SysFont('notosans', font_size)

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
    screen.fill(WHITE)
    draw_grid()
    draw_ships(computer.ships)
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
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    main_menu()

main_menu()
pygame.quit()
