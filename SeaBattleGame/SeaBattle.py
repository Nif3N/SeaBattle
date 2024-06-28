import pygame
import sys
import random
import copy

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN_BLUE = (0, 153, 153)
LIGHT_GRAY = (192, 192, 192)
RED = (255, 0, 0)

block_size = 50
left_margin = 100
upper_margin = 80

size = (left_margin+30*block_size, upper_margin+15*block_size)
#LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
LETTERS = "АБВГДЕЖЗИК"

pygame.init()

screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
pygame.display.set_caption("Sea Battle")
game_over_font_size = 3 * block_size
game_over_font = pygame.font.Font("assets/Seagull_Wine.ttf", 50)

font_size = int(block_size / 1.5)
font = pygame.font.Font("assets/Seagull_Wine.ttf",25)
computer_available_to_fire_set = {(x, y) for x in range(16, 25) for y in range(1, 11)}
around_last_computer_hit_set = set()
hit_blocks = set()
dotted_set = set()
dotted_set_for_computer_not_to_shoot = set()
hit_blocks_for_computer_not_to_shoot = set()
last_hits_list = []
destroyed_computer_ships = []
destroyed_ships_list = []

class Button_MM():
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
    """Класс рисования сеток и добавления к ним заголовков, цифр и букв
    ----------
    Attributes:
        title (str): Имена игроков будут отображаться в верхней части его сетки
        offset (int): Где начинается сетка (в количестве блоков)
                            (обычно 0 для компьютера и 15 для человека)
    ----------
    Methods:
    __draw_grid(): Рисует две сетки для обоих игроков
    __add_nums_letters_to_grid(): Рисует цифры 1-10 по вертикали и добавляет буквы под горизонтальными
        линиями для обеих сеток
    __sign_grid(): Помещает имена игроков (заголовки) в центр над сетками
    """

    def __init__(self, title, offset):
        """
        title(str): Имена игроков будут отображаться в верхней части его сетки
        offset (int): Где начинается сетка (в количестве блоков)
                (обычно 0 для компьютера и 15 для человека)
        """
        self.title = title
        self.offset = offset
        self.__draw_grid()
        self.__add_nums_letters_to_grid()
        self.__sign_grid()

    def __draw_grid(self):
        """
        Рисует две сетки для обоих игроков
        """
        for i in range(11):
            # Horizontal lines
            pygame.draw.line(screen, BLACK, (left_margin + self.offset * block_size, upper_margin + i * block_size),
                             (left_margin + (10 + self.offset) * block_size, upper_margin + i * block_size), 1)
            # Vertical lines
            pygame.draw.line(screen, BLACK, (left_margin + (i + self.offset) * block_size, upper_margin),
                             (left_margin + (i + self.offset) * block_size, upper_margin + 10 * block_size), 1)

    def __add_nums_letters_to_grid(self):
        """
        Рисует цифры 1-10 по вертикали и добавляет буквы под горизонтальными
        линиями для обеих сеток
        """
        for i in range(10):
            num_ver = font.render(str(i + 1), True, BLACK)
            letters_hor = font.render(LETTERS[i], True, BLACK)
            num_ver_width = num_ver.get_width()
            num_ver_height = num_ver.get_height()
            letters_hor_width = letters_hor.get_width()

            # Numbers (vertical)
            screen.blit(num_ver, (left_margin - (block_size // 2 + num_ver_width // 2) + self.offset * block_size,
                                  upper_margin + i * block_size + (block_size // 2 - num_ver_height // 2)))
            # Letters (horizontal)
            screen.blit(letters_hor, (left_margin + i * block_size + (block_size // 2 -
                                                                      letters_hor_width // 2) + self.offset * block_size, upper_margin + 10 * block_size))

    def __sign_grid(self):
        """
        Помещает имена игроков (заголовки) в центр над сетками
        """
        player = font.render(self.title, True, BLACK)
        sign_width = player.get_width()
        screen.blit(player, (left_margin + 5 * block_size - sign_width // 2 +
                             self.offset * block_size, upper_margin - block_size // 2 - font_size))


class Button:
    """
    Создает кнопки и печатает пояснительное сообщение для них
    ----------
    Attributes:
        __title (str): Название кнопки (title)
        __message (str): пояснительное сообщение для печати на экране
        __x_start (int): кнопка "смещение по горизонтали" для начала рисования
        __y_start (int): кнопка "смещение по вертикали" для начала рисования
        rect_for_draw (tuple of four ints): прямоугольные кнопки, которые нужно нарисовать
        rect (pygame Rect): pygame Rect объект
        __rect_for_button_title (tuple of two ints): прямоугольник внутри кнопки для печати текста в нем
        __color (tuple): цвет кнопки (по умолчанию - ЧЕРНЫЙ, при наведении - ЗЕЛЕНО_СИНИЙ, при отключении - СВЕТЛО-СЕРЫЙ)
    ----------
    Methods:
    draw_button(): Рисует кнопку в виде цветного прямоугольника (по умолчанию - ЧЕРНЫЙ)
    change_color_on_hover(): Рисует кнопку в виде прямоугольника ЗЕЛЕНО_СИНЕГО цвета
    print_message_for_button(): Печатает пояснительное сообщение рядом с кнопкой
    """

    def __init__(self, x_offset, button_title, message_to_show):
        self.__title = button_title
        self.__title_width, self.__title_height = font.size(self.__title)
        self.__message = message_to_show
        self.__button_width = self.__title_width + block_size
        self.__button_height = self.__title_height + block_size
        self.__x_start = x_offset
        self.__y_start = upper_margin + 10 * block_size + self.__button_height
        self.rect_for_draw = self.__x_start, self.__y_start, self.__button_width, self.__button_height
        self.rect = pygame.Rect(self.rect_for_draw)
        self.__rect_for_button_title = self.__x_start + self.__button_width / 2 - \
            self.__title_width / 2, self.__y_start + \
            self.__button_height / 2 - self.__title_height / 2
        self.__color = BLACK

    def draw_button(self, color=None):
        """
        Рисует кнопку в виде цветного прямоугольника (по умолчанию - ЧЕРНЫЙ)
        Args:
            color (tuple, optional): Цвет кнопки. По умолчанию - Нет (ЧЕРНЫЙ).
        """
        if not color:
            color = self.__color
        pygame.draw.rect(screen, color, self.rect_for_draw)
        text_to_blit = font.render(self.__title, True, WHITE)
        screen.blit(text_to_blit, self.__rect_for_button_title)

    def change_color_on_hover(self):
        """
        Рисует кнопку в виде прямоугольника ЗЕЛЕНО_СИНЕГО цвета
        """
        mouse = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse):
            self.draw_button(GREEN_BLUE)

    def print_message_for_button(self):
        """
        Печатает пояснительное сообщение рядом с кнопкой
        """
        message_width, message_height = font.size(self.__message)
        rect_for_message = self.__x_start / 2 - message_width / \
            2, self.__y_start + self.__button_height / 2 - message_height / 2
        text = font.render(self.__message, True, BLACK)
        screen.blit(text, rect_for_message)


class AutoShips:
    """
    Случайным образом создайте все корабли игрока на сетке
    ----------
    Attributes:
        offset (int): Где начинается сетка (в количестве блоков)
                (обычно 0 для компьютера и 15 для человека)
        available_blocks (set of tuples): координаты всех блоков, доступных для создания кораблей (обновляются при каждом создании корабля)
        ships_set (set of tuples): все блоки, занятые кораблями
        ships (list of lists): список всех отдельных судов (в виде списков)
    ----------
    Methods:
        __create_start_block(available_blocks):
            Случайным образом выбирает блок, с которого нужно начать создание корабля.
            Случайным образом выбирает горизонтальный или вертикальный тип корабля
            Случайным образом выбирает направление (из стартового блока) - прямое или обратное
            Возвращает три случайно выбранных значения
        __create_ship(number_of_blocks, available_blocks):
            Создает корабль заданной длины (number_of_blocks), начиная с начального блока,
            возвращенного предыдущим методом, используя тип корабля и направление (изменяя его,
            если выходите за пределы сетки), возвращенные предыдущим методом.
            Проверяет, является ли корабль действительным (не находится рядом с другими кораблями и в пределах сетки)
            и добавляет его в список кораблей.
            Returns: список кортежей с координатами нового корабля
        __get_new_block_for_ship(self, coor, direction, orientation, ship_coordinates):
            Проверяет, находятся ли новые отдельные блоки, добавляемые к кораблю в предыдущем методе,
            в пределах сетки, в противном случае изменяет направление.
            Returns:
                direction (int): прямой или произвольный прирост/уменьшение координат последнего/первого блока в строящемся судне
        __is_ship_valid(new_ship):
            Проверьте, все ли координаты корабля находятся в пределах набора доступных блоков.
            Returns: Правда или ложь
        __add_new_ship_to_set(new_ship):
            Добавляет все блоки из списка кораблей в ships_set
        __update_available_blocks_for_creating_ships(new_ship):
            Удаляет все блоки, занятые кораблем и вокруг него, из набора доступных блоков
        __populate_grid():
            Создает необходимое количество кораблей каждого типа, вызывая метод create_ship.
            Добавляет каждый корабль в список ships, ships_set и обновляет доступные блоки.
            Returns: список всех кораблей
    """

    def __init__(self, offset):
        """
        Parameters:
            :offset (int): Где начинается сетка (в количестве блоков) (обычно 0 для компьютера и 15 для человека)
            :available_blocks (set of tuples): координаты всех блоков, доступных для создания кораблей (обновляются при каждом создании корабля)
            :ships_set (set of tuples): все блоки, занятые кораблями
            :ships (list of lists): список всех отдельных судов (в виде списков)"""

        self.offset = offset
        self.available_blocks = {(x, y) for x in range(
            1 + self.offset, 11 + self.offset) for y in range(1, 11)}
        self.ships_set = set()
        self.ships = self.__populate_grid()
        self.orientation = None
        self.direction = None

    def __create_start_block(self, available_blocks):
        """
        Случайным образом выбирается блок, с которого нужно начать создание корабля.
        Случайным образом выбирается горизонтальный или вертикальный тип корабля
        Случайным образом выбирается направление (из стартового блока) - прямое или обратное
        Args:
            available_blocks (set of tuples): координаты всех блоков, доступных для создания кораблей (обновляются при каждом создании корабля)
        Returns:
            int: координата x случайного блока
            int: координата y случайного блока
            int: 0=по горизонтали (изменение x), 1=по вертикали (изменение y)
            int: 1=прямой, -1=обратный
        """
        self.orientation = random.randint(0, 1)
        # -1 is left or down, 1 is right or up
        self.direction = random.choice((-1, 1))
        x, y = random.choice(tuple(available_blocks))
        return x, y, self.orientation, self.direction

    def __create_ship(self, number_of_blocks, available_blocks):
        """
        Создает корабль заданной длины (number_of_blocks), начиная с начального блока,
        возвращенного предыдущим методом, используя тип корабля и направление (изменяя его,
        если выходите за пределы сетки), возвращенные предыдущим методом.
        Проверяет, является ли корабль действительным (не находится рядом с другими кораблями и в пределах сетки)
        и добавляет его в список кораблей.
        Args:
            number_of_blocks (int): длина необходимого судна
            available_blocks (set): бесплатные блоки для создания кораблей
        Returns:
            list: список кортежей с координатами нового корабля
        """
        ship_coordinates = []
        x, y, self.orientation, self.direction = self.__create_start_block(
            available_blocks)
        for _ in range(number_of_blocks):
            ship_coordinates.append((x, y))
            if not self.orientation:
                self.direction, x = self.__get_new_block_for_ship(
                    x, self.direction, self.orientation, ship_coordinates)
            else:
                self.direction, y = self.__get_new_block_for_ship(
                    y, self.direction, self.orientation, ship_coordinates)
        if self.__is_ship_valid(ship_coordinates):
            return ship_coordinates
        return self.__create_ship(number_of_blocks, available_blocks)

    def __get_new_block_for_ship(self, coor, direction, orientation, ship_coordinates):
        """
        Проверяет, находятся ли новые отдельные блоки, добавляемые к кораблю в предыдущем методе,
        в пределах сетки, в противном случае изменяет направление.
        Args:
            coor (int): координата x или y для увеличения/уменьшения
            direction (int): 1 или -1
            orientation (int): 0 или 1
            ship_coordinates (list): координаты недостроенного корабля
        Returns:
            прямая или обратная
            увеличенная/уменьшенная координата последнего/первого блока в строящемся судне (int)
        """
        self.direction = direction
        self.orientation = orientation
        if (coor <= 1 - self.offset * (self.orientation - 1) and self.direction == -1) or (
                coor >= 10 - self.offset * (self.orientation - 1) and self.direction == 1):
            self.direction *= -1
            return self.direction, ship_coordinates[0][self.orientation] + self.direction
        else:
            return self.direction, ship_coordinates[-1][self.orientation] + self.direction

    def __is_ship_valid(self, new_ship):
        """
        Проверьте, все ли координаты корабля находятся в пределах набора доступных блоков.
        Args:
            new_ship (list): список кортежей с только что созданными координатами корабля
        Returns:
            bool: Правда или ложь
        """
        ship = set(new_ship)
        return ship.issubset(self.available_blocks)

    def __add_new_ship_to_set(self, new_ship):
        """
        Добавляет все блоки из списка кораблей в ships_set
        Args:
            new_ship (list): список кортежей с только что созданными координатами корабля
        """
        self.ships_set.update(new_ship)

    def __update_available_blocks_for_creating_ships(self, new_ship):
        """
        Удаляет все блоки, занятые кораблем и вокруг него, из набора доступных блоков
        Args:
            new_ship ([type]): список кортежей с только что созданными координатами корабля
        """
        for elem in new_ship:
            for k in range(-1, 2):
                for m in range(-1, 2):
                    if self.offset < (elem[0] + k) < 11 + self.offset and 0 < (elem[1] + m) < 11:
                        self.available_blocks.discard(
                            (elem[0] + k, elem[1] + m))

    def __populate_grid(self):
        """
        Создает необходимое количество кораблей каждого типа, вызывая метод create_ship.
        Добавляет каждый корабль в список ships, ships_set и обновляет доступные блоки.
        Returns:
            list: двумерный список всех кораблей
        """
        ships_coordinates_list = []
        for number_of_blocks in range(4, 0, -1):
            for _ in range(5 - number_of_blocks):
                new_ship = self.__create_ship(
                    number_of_blocks, self.available_blocks)
                ships_coordinates_list.append(new_ship)
                self.__add_new_ship_to_set(new_ship)
                self.__update_available_blocks_for_creating_ships(new_ship)
        return ships_coordinates_list

# ===========Shooting section==============


def computer_shoots(set_to_shoot_from):
    """
    Случайным образом выбирает блок из доступных для съемки из набора
    """
    pygame.time.delay(500)
    computer_fired_block = random.choice(tuple(set_to_shoot_from))
    computer_available_to_fire_set.discard(computer_fired_block)
    return computer_fired_block


def check_hit_or_miss(fired_block, opponents_ships_list, computer_turn, opponents_ships_list_original_copy,
                      opponents_ships_set):
    """
    Проверяет, был ли блок, по которому стрелял компьютер или человек, поражен или промахнулся.
    Обновляет наборы с точками (в пропущенных блоках или в диагональных блоках вокруг пораженного блока) и крестиками
    (в пораженных блоках).
    Удаляет уничтоженные корабли из списка кораблей.
    """
    for elem in opponents_ships_list:
        diagonal_only = True
        if fired_block in elem:
            # This is to put dots before and after a destroyed ship
            # and to draw computer's destroyed ships (which are hidden until destroyed)
            ind = opponents_ships_list.index(elem)
            if len(elem) == 1:
                diagonal_only = False
            update_dotted_and_hit_sets(
                fired_block, computer_turn, diagonal_only)
            elem.remove(fired_block)
            # This is to check who loses - if ships_set is empty
            opponents_ships_set.discard(fired_block)
            if computer_turn:
                last_hits_list.append(fired_block)
                update_around_last_computer_hit(fired_block, True)
            # If the ship is destroyed
            if not elem:
                update_destroyed_ships(
                    ind, computer_turn, opponents_ships_list_original_copy)
                if computer_turn:
                    last_hits_list.clear()
                    around_last_computer_hit_set.clear()
                else:
                    # Add computer's destroyed ship to the list to draw it (computer ships are hidden)
                    destroyed_computer_ships.append(computer.ships[ind])
            return True
    add_missed_block_to_dotted_set(fired_block)
    if computer_turn:
        update_around_last_computer_hit(fired_block, False)
    return False


def update_destroyed_ships(ind, computer_turn, opponents_ships_list_original_copy):
    """
    Добавляет блоки до и после корабля в dotted_set, чтобы нарисовать на них точки.
    Добавляет все блоки на корабле в hit_blocks, чтобы нарисовать крестики внутри уничтоженного корабля.
    """
    ship = sorted(opponents_ships_list_original_copy[ind])
    for i in range(-1, 1):
        update_dotted_and_hit_sets(ship[i], computer_turn, False)

def update_around_last_computer_hit(fired_block, computer_hits):
    """
    Обновляет параметр around_last_computer_hit_set (который используется для выбора компьютера для стрельбы), если снаряд
    попал в корабль, но не уничтожил его. Добавляет к этому набору вертикальные или горизонтальные блоки вокруг
    блока, в который был нанесен последний удар. Затем удаляет те блоки из этого набора, по которым стреляли, но промахнулись.
    around_last_computer_hit_set заставляет компьютер выбирать правильные блоки, чтобы быстро уничтожить корабль,
    вместо того, чтобы просто беспорядочно стрелять по совершенно случайным блокам.
    """
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
    """
    Добавляет блоки сверху, снизу, справа и слева от блока, по которому ударил
    компьютер, во временный набор, из которого компьютер выберет свой следующий выстрел.
    Args:
        fired_block (tuple): координаты блока, пораженного компьютером
    """
    x_hit, y_hit = fired_block
    if x_hit > 16:
        around_last_computer_hit_set.add((x_hit - 1, y_hit))
    if x_hit < 25:
        around_last_computer_hit_set.add((x_hit + 1, y_hit))
    if y_hit > 1:
        around_last_computer_hit_set.add((x_hit, y_hit - 1))
    if y_hit < 10:
        around_last_computer_hit_set.add((x_hit, y_hit + 1))


def computer_hits_twice():
    """
    Добавляет блоки до и после двух или более блоков корабля во временный список,
    чтобы компьютер мог быстрее завершить постройку корабля.
    Returns:
        set: временный набор блоков, где потенциально должен находиться человеческий корабль
    """
    last_hits_list.sort()
    new_around_last_hit_set = set()
    for i in range(len(last_hits_list) - 1):
        x1 = last_hits_list[i][0]
        x2 = last_hits_list[i + 1][0]
        y1 = last_hits_list[i][1]
        y2 = last_hits_list[i + 1][1]
        if x1 == x2:
            if y1 > 1:
                new_around_last_hit_set.add((x1, y1 - 1))
            if y2 < 10:
                new_around_last_hit_set.add((x1, y2 + 1))
        elif y1 == y2:
            if x1 > 16:
                new_around_last_hit_set.add((x1 - 1, y1))
            if x2 < 25:
                new_around_last_hit_set.add((x2 + 1, y1))
    return new_around_last_hit_set


def update_dotted_and_hit_sets(fired_block, computer_turn, diagonal_only=True):
    """
    Ставит точки в центре диагонали или вокруг блока, по которому был нанесен удар (человеком или
    компьютером). Добавляет все диагональные блоки или выбранный блок по периметру в отдельный набор
    block: hit block (tuple)
    """
    global dotted_set
    x, y = fired_block
    a = 15 * computer_turn
    b = 11 + 15 * computer_turn
    # Adds a block hit by computer to the set of his hits to later remove
    # them from the set of blocks available for it to shoot from
    hit_blocks_for_computer_not_to_shoot.add(fired_block)
    # Adds hit blocks on either grid1 (x:1-10) or grid2 (x:16-25)
    hit_blocks.add(fired_block)
    # Adds blocks in diagonal or all-around a block to repsective sets
    for i in range(-1, 2):
        for j in range(-1, 2):
            if (not diagonal_only or i != 0 and j != 0) and a < x + i < b and 0 < y + j < 11:
                add_missed_block_to_dotted_set((x + i, y + j))
    dotted_set -= hit_blocks


def add_missed_block_to_dotted_set(fired_block):
    """
    Добавляет fired_block к набору пропущенных выстрелов (если fired_block - это промах), чтобы затем нарисовать на них точки.
    Также необходимо, чтобы компьютер удалил эти точечные блоки из набора доступных блоков, из которых он может стрелять.
    """
    dotted_set.add(fired_block)
    dotted_set_for_computer_not_to_shoot.add(fired_block)


# ===========DRAWING SECTION==============

def draw_ships(ships_coordinates_list):
    """
    Рисует прямоугольники вокруг блоков, занятых кораблем
    Args:
        ships_coordinates_list (list of tuples): список координат кораблей
    """
    for elem in ships_coordinates_list:
        ship = sorted(elem)
        x_start = ship[0][0]
        y_start = ship[0][1]
        # Horizontal and 1block ships
        ship_width = block_size * len(ship)
        ship_height = block_size
        # Vertical ships
        if len(ship) > 1 and ship[0][0] == ship[1][0]:
            ship_width, ship_height = ship_height, ship_width
        x = block_size * (x_start - 1) + left_margin
        y = block_size * (y_start - 1) + upper_margin
        pygame.draw.rect(
            screen, BLACK, ((x, y), (ship_width, ship_height)), width=block_size // 10)


def draw_from_dotted_set(dotted_set_to_draw_from):
    """
    Рисует точки в центре всех блоков в наборе dotted_set
    """
    for elem in dotted_set_to_draw_from:
        pygame.draw.circle(screen, BLACK, (block_size * (
            elem[0] - 0.5) + left_margin, block_size * (elem[1] - 0.5) + upper_margin), block_size // 6)


def draw_hit_blocks(hit_blocks_to_draw_from):
    """
    Рисует "X" в блоках, которые были успешно поражены компьютером или человеком
    """
    for block in hit_blocks_to_draw_from:
        x1 = block_size * (block[0] - 1) + left_margin
        y1 = block_size * (block[1] - 1) + upper_margin
        pygame.draw.line(screen, BLACK, (x1, y1),
                         (x1 + block_size, y1 + block_size), block_size // 6)
        pygame.draw.line(screen, BLACK, (x1, y1 + block_size),
                         (x1 + block_size, y1), block_size // 6)


def show_message_at_rect_center(message, rect, which_font=font, color=RED):
    """
    Выводит сообщение на экран в заданном прямоугольном центре.
    Args:
        message (str): Сообщение для печати
        rect (tuple): прямоугольник в формате (x_start, y_start, width, height)
        which_font (pygame font object, optional): Какой шрифт использовать для печати сообщения.
        color (tuple, optional): Цвет сообщения. По умолчанию используется КРАСНЫЙ.
    """
    message_width, message_height = which_font.size(message)
    message_rect = pygame.Rect(rect)
    x_start = message_rect.centerx - message_width / 2
    y_start = message_rect.centery - message_height / 2
    background_rect = pygame.Rect(
        x_start - block_size / 2, y_start, message_width + block_size, message_height)
    message_to_blit = which_font.render(message, True, color)
    screen.fill(WHITE, background_rect)
    screen.blit(message_to_blit, (x_start, y_start))


def ship_is_valid(ship_set, blocks_for_manual_drawing):
    """
    Проверяет, не соприкасается ли корабль с другими кораблями
    Args:
        ship_set (set): Набор с помощью кортежей координат новых кораблей
        blocks_for_manual_drawing (set): Устанавливается вместе со всеми используемыми блоками для других кораблей, включая все блоки вокруг кораблей.

    Returns:
        Bool: Истинно, если корабли не соприкасаются, ложно в противном случае.
    """
    return ship_set.isdisjoint(blocks_for_manual_drawing)


def check_ships_numbers(ship, num_ships_list):
    """
    Проверяет, не превышает ли количество груза определенной длины (1-4) необходимое количество (4-1).

    Args:
        ship (list): Список с координатами новых судов
        num_ships_list (list): Список с номерами конкретных судов по соответствующим индексам.

    Returns:
        Bool: Верно, если количество судов определенной длины не превышает необходимого, Неверно, если таких судов достаточно.
    """
    return (5 - len(ship)) > num_ships_list[len(ship)-1]


def update_used_blocks(ship, method):
    for block in ship:
        for i in range(-1, 2):
            for j in range(-1, 2):
                method((block[0]+i, block[1]+j))


computer = AutoShips(0)
computer_ships_working = copy.deepcopy(computer.ships)

auto_button_place = left_margin + 17 * block_size
manual_button_place = left_margin + 20 * block_size
how_to_create_ships_message = "Как вы хотите создать корабли? Нажмите кнопку"
auto_button = Button(auto_button_place, "АВТО", how_to_create_ships_message)
manual_button = Button(manual_button_place, "ВРУЧНУЮ",
                       how_to_create_ships_message)
undo_message = "Для отмены последнего корабля нажмите кнопку"
undo_button_place = left_margin + 12 * block_size
undo_button = Button(undo_button_place, "ОТМЕНА", undo_message)

SCREEN = pygame.display.set_mode(size, pygame.FULLSCREEN)
pygame.display.set_caption("Menu")
BG = pygame.image.load("assets/Background.jpg")

def get_font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/Seagull_Wine.ttf", size)


def about():
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("white")

        RULES_HEAD_TEXT = get_font(50).render("Правила игры", True, "Red")
        RULES_HEAD_RECT = RULES_HEAD_TEXT.get_rect(center=(200, 50))

        RULES1_TEXT = get_font(25).render("Играют два игрока, каждый из которых размещает корабли на своем поле размером 10х10 клеток.", True, "Black")
        RULES1_RECT = RULES1_TEXT.get_rect(center=(700, 150))
        RULES2_TEXT = get_font(25).render("Корабли могут быть различных размеров: однопалубные - 4 штуки, двухпалубные - 3 штуки,", True, "Black")
        RULES2_RECT = RULES2_TEXT.get_rect(center=(660, 180))
        RULES2dop_TEXT = get_font(25).render("трехпалубные - 2 штуки, четырехпалубные - 1 штука. Игроки поочередно делают ходы, указывая",True, "Black")
        RULES2dop_RECT = RULES2dop_TEXT.get_rect(center=(695, 210))
        RULES3_TEXT = get_font(25).render("координаты атаки на поле противника. Если в указанных координатах стоит корабль противника,", True, "Black")
        RULES3_RECT = RULES3_TEXT.get_rect(center=(698, 240))
        RULES4_TEXT = get_font(25).render("то он считается потопленным. В противном случае игрок промахивается. Побеждает игрок,", True, "Black")
        RULES4_RECT = RULES4_TEXT.get_rect(center=(650, 270))
        RULES5_TEXT = get_font(25).render("первым потопивший все корабли противника.", True, "Black")
        RULES5_RECT = RULES5_TEXT.get_rect(center=(326, 300))

        RULESpromah_TEXT = get_font(40).render(" - промах", True,"Black")
        RULESpromah_RECT = RULESpromah_TEXT.get_rect(center=(230, 400))
        RULESpopal_TEXT = get_font(40).render(" - попадание", True, "Black")
        RULESpopal_RECT = RULESpopal_TEXT.get_rect(center=(265, 500))
        RULESpotoplen_TEXT = get_font(40).render(" - потоплен", True, "Black")
        RULESpotoplen_RECT = RULESpotoplen_TEXT.get_rect(center=(250, 600))

        promah = pygame.image.load('assets/promah.png')
        promah_rect = promah.get_rect(center=(100, 400))
        SCREEN.blit(promah, promah_rect)

        popal = pygame.image.load('assets/popal.png')
        popal_rect = popal.get_rect(center=(100, 500))
        SCREEN.blit(popal, popal_rect)

        potoplen = pygame.image.load('assets/potoplen.png')
        potoplen_rect = potoplen.get_rect(center=(100, 600))
        SCREEN.blit(potoplen, potoplen_rect)

        primer = pygame.image.load('assets/primer.png')
        primer_rect = primer.get_rect(center=(950, 600))
        SCREEN.blit(primer, primer_rect)

        SCREEN.blit(RULESpotoplen_TEXT, RULESpotoplen_RECT)
        SCREEN.blit(RULESpopal_TEXT, RULESpopal_RECT)
        SCREEN.blit(RULESpromah_TEXT, RULESpromah_RECT)
        SCREEN.blit(RULES_HEAD_TEXT, RULES_HEAD_RECT)
        SCREEN.blit(RULES1_TEXT, RULES1_RECT)
        SCREEN.blit(RULES2_TEXT, RULES2_RECT)
        SCREEN.blit(RULES2dop_TEXT, RULES2dop_RECT)
        SCREEN.blit(RULES3_TEXT, RULES3_RECT)
        SCREEN.blit(RULES4_TEXT, RULES4_RECT)
        SCREEN.blit(RULES5_TEXT, RULES5_RECT)
        OPTIONS_BACK = Button_MM(image=None, pos=(100, 870),
                              text_input="Назад", font=get_font(50), base_color="Black", hovering_color="Red")

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
        MENU_RECT = MENU_TEXT.get_rect(center=(820, 100))

        PLAY_BUTTON = Button_MM(image=pygame.image.load("assets/Play Rect.png"), pos=(820, 250),
                             text_input="Играть", font=get_font(75), base_color="Black", hovering_color="Red")
        ABOUT_BUTTON = Button_MM(image=pygame.image.load("assets/Play Rect.png"), pos=(820, 400),
                                   text_input="Об игре", font=get_font(75), base_color="Black", hovering_color="Red")
        QUIT_BUTTON = Button_MM(image=pygame.image.load("assets/Quit Rect.png"), pos=(820, 550),
                             text_input="Выход", font=get_font(75), base_color="Black", hovering_color="Red")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, ABOUT_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    main()
                if ABOUT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    about()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

def main():
    ships_creation_not_decided = True
    ships_not_created = True
    drawing = False
    game_over = False
    computer_turn = False
    start = (0, 0)
    ship_size = (0, 0)

    rect_for_grids = (0, 0, size[0], upper_margin + 12 * block_size)
    rect_for_messages_and_buttons = (
        0, upper_margin + 11 * block_size, size[0], 5 * block_size)
    message_rect_for_drawing_ships = (
    undo_button.rect_for_draw[0] + undo_button.rect_for_draw[2], upper_margin + 11 * block_size, size[0] - (
            undo_button.rect_for_draw[0] + undo_button.rect_for_draw[2]), 4 * block_size)
    message_rect_computer = (left_margin - 2 * block_size, upper_margin +
                             11 * block_size, 14 * block_size, 4 * block_size)
    message_rect_human = (left_margin + 15 * block_size, upper_margin +
                          11 * block_size, 10 * block_size, 4 * block_size)

    human_ships_to_draw = []
    human_ships_set = set()
    used_blocks_for_manual_drawing = set()
    num_ships_list = [0, 0, 0, 0]

    screen.fill(WHITE)

    computer_grid = Grid(" ", 0)
    human_grid = Grid(" ", 15)

    KOMP_TEXT = get_font(35).render("Компьютер", True, "Black")
    KOMP_RECT = KOMP_TEXT.get_rect(center=(350, 50))
    SCREEN.blit(KOMP_TEXT, KOMP_RECT)
    USER_TEXT = get_font(35).render("Человек", True, "Black")
    USER_RECT = USER_TEXT.get_rect(center=(1100, 50))
    SCREEN.blit(USER_TEXT, USER_RECT)
    #draw_ships(computer.ships)

    PLAY_QUIT = Button_MM(image=None, pos=(100, 870),
                       text_input="Выход", font=get_font(50), base_color="Black", hovering_color="Red")

    while ships_creation_not_decided:
        auto_button.draw_button()
        manual_button.draw_button()
        auto_button.change_color_on_hover()
        manual_button.change_color_on_hover()
        auto_button.print_message_for_button()

        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                ships_creation_not_decided = False
                ships_not_created = False
            # If AUTO button is pressed - create human ships automatically
            elif event.type == pygame.MOUSEBUTTONDOWN and auto_button.rect.collidepoint(mouse):
                print("Clicked AUTO!", event.pos)
                human = AutoShips(15)
                human_ships_to_draw = human.ships
                human_ships_working = copy.deepcopy(human.ships)
                human_ships_set = human.ships_set
                ships_creation_not_decided = False
                ships_not_created = False
            elif event.type == pygame.MOUSEBUTTONDOWN and manual_button.rect.collidepoint(mouse):
                ships_creation_not_decided = False

        pygame.display.update()
        screen.fill(WHITE, rect_for_messages_and_buttons)

    while ships_not_created:
        screen.fill(WHITE, rect_for_grids)
        computer_grid = Grid(" ", 0)
        human_grid = Grid(" ", 15)
        undo_button.draw_button()
        undo_button.print_message_for_button()
        undo_button.change_color_on_hover()
        mouse = pygame.mouse.get_pos()
        if not human_ships_to_draw:
            undo_button.draw_button(LIGHT_GRAY)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ships_not_created = False
                game_over = True
            elif undo_button.rect.collidepoint(mouse) and event.type == pygame.MOUSEBUTTONDOWN:
                if human_ships_to_draw:
                    screen.fill(WHITE, message_rect_for_drawing_ships)
                    deleted_ship = human_ships_to_draw.pop()
                    num_ships_list[len(deleted_ship) - 1] -= 1
                    update_used_blocks(
                        deleted_ship, used_blocks_for_manual_drawing.discard)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                x_start, y_start = event.pos
                start = x_start, y_start
                ship_size = (0, 0)
            elif drawing and event.type == pygame.MOUSEMOTION:
                x_end, y_end = event.pos
                end = x_end, y_end
                ship_size = x_end - x_start, y_end - y_start
            elif drawing and event.type == pygame.MOUSEBUTTONUP:
                x_end, y_end = event.pos
                drawing = False
                ship_size = (0, 0)
                start_block = ((x_start - left_margin) // block_size + 1,
                               (y_start - upper_margin) // block_size + 1)
                end_block = ((x_end - left_margin) // block_size + 1,
                             (y_end - upper_margin) // block_size + 1)
                if start_block > end_block:
                    start_block, end_block = end_block, start_block
                temp_ship = []
                if 15 < start_block[0] < 26 and 0 < start_block[1] < 11 and 15 < end_block[0] < 26 and 0 < end_block[
                    1] < 11:
                    screen.fill(WHITE, message_rect_for_drawing_ships)
                    if start_block[0] == end_block[0] and (end_block[1] - start_block[1]) < 4:
                        for block in range(start_block[1], end_block[1] + 1):
                            temp_ship.append((start_block[0], block))
                    elif start_block[1] == end_block[1] and (end_block[0] - start_block[0]) < 4:
                        for block in range(start_block[0], end_block[0] + 1):
                            temp_ship.append((block, start_block[1]))
                    else:
                        show_message_at_rect_center(
                            "КОРАБЛЬ СЛИШКОМ БОЛЬШОЙ!", message_rect_for_drawing_ships)
                else:
                    show_message_at_rect_center(
                        "КОРАБЛЬ ЗА ПРЕДЕЛАМИ СЕТКИ!", message_rect_for_drawing_ships)
                if temp_ship:
                    temp_ship_set = set(temp_ship)
                    if ship_is_valid(temp_ship_set, used_blocks_for_manual_drawing):
                        if check_ships_numbers(temp_ship, num_ships_list):
                            num_ships_list[len(temp_ship) - 1] += 1
                            human_ships_to_draw.append(temp_ship)
                            human_ships_set |= temp_ship_set
                            update_used_blocks(
                                temp_ship, used_blocks_for_manual_drawing.add)
                        else:
                            show_message_at_rect_center(
                                f"УЖЕ ДОСТАТОЧНО {len(temp_ship)}-ПАЛУБНЫХ КОРАБЛЕЙ", message_rect_for_drawing_ships)
                    else:
                        show_message_at_rect_center(
                            "КОРАБЛИ ПРИКАСАЮТСЯ!", message_rect_for_drawing_ships)
            if len(human_ships_to_draw) == 10:
                ships_not_created = False
                human_ships_working = copy.deepcopy(human_ships_to_draw)
                screen.fill(WHITE, rect_for_messages_and_buttons)
        pygame.draw.rect(screen, BLACK, (start, ship_size), 3)
        draw_ships(human_ships_to_draw)
        pygame.display.update()

    while not game_over:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()
        PLAY_QUIT.changeColor(PLAY_MOUSE_POS)
        PLAY_QUIT.update(screen)
        draw_ships(destroyed_computer_ships)
        draw_ships(human_ships_to_draw)
        pygame.display.update()
        if not (dotted_set | hit_blocks):
            show_message_at_rect_center(
                "ИГРА НАЧАЛАСЬ! ВАШ ХОД!", message_rect_computer)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif not computer_turn and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if (left_margin < x < left_margin + 10 * block_size) and (
                        upper_margin < y < upper_margin + 10 * block_size):
                    fired_block = ((x - left_margin) // block_size + 1,
                                   (y - upper_margin) // block_size + 1)
                    computer_turn = not check_hit_or_miss(fired_block, computer_ships_working, False, computer.ships,
                                                          computer.ships_set)
                    draw_from_dotted_set(dotted_set)
                    draw_hit_blocks(hit_blocks)
                    screen.fill(WHITE, message_rect_computer)
                    show_message_at_rect_center(
                        f"Ваш последний ход: {LETTERS[fired_block[0] - 1] + str(fired_block[1])}",
                        message_rect_computer, color=BLACK)
                else:
                    show_message_at_rect_center(
                        "ВЫСТРЕЛ ЗА ПРЕДЕЛЫ СЕТКИ!", message_rect_computer)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_QUIT.checkForInput(PLAY_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        if computer_turn:
            set_to_shoot_from = computer_available_to_fire_set
            if around_last_computer_hit_set:
                set_to_shoot_from = around_last_computer_hit_set

            fired_block = computer_shoots(set_to_shoot_from)
            screen.fill(WHITE, message_rect_human)
            show_message_at_rect_center(
                f"ПОСЛЕДНИЙ ХОД КОМПЬЮТЕРА: {LETTERS[fired_block[0] - 16] + str(fired_block[1])}", message_rect_human,
                color=BLACK)
            computer_turn = check_hit_or_miss(fired_block, human_ships_working, True, human_ships_to_draw, human_ships_set)
            draw_from_dotted_set(dotted_set)
            draw_hit_blocks(hit_blocks)

        if not computer.ships_set:
            show_message_at_rect_center(
                "ВЫ ВЫИГРАЛИ!", (0, 0, size[0], size[1]), game_over_font)
        if not human_ships_set:
            show_message_at_rect_center(
                "ВЫ ПРОИГРАЛИ!", (0, 0, size[0], size[1]), game_over_font)
        pygame.display.update()

main_menu()
pygame.quit()
