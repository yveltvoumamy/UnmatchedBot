import pygame


class Board:
    i = 0

    def __init__(self, sc, main_hero):
        self.main_hero = main_hero
        self.sc = sc
        self.board_img = pygame.image.load('pictures/board.png')
        self.move_options = []

        self.color_directions = {
            'lightgreen': (1, 18, 19, 20, 21, 22), 'red': (1, 2, 3, 4, 5, 6), 'green': (4, 5, 6, 7, 8, 9),
            'grey': (6, 8, 9, 10, 12), 'yellow': (10, 11, 12, 13, 14, 15, 16, 17, 18, 25, 26, 27),
            'brown': (22, 23, 24, 25, 26, 27), 'blue': (3, 26, 27, 28, 29, 30)
        }
        self.cells_color = [[], ['lightgreen', 'red'], ['red'], ['red', 'blue'], ['red', 'green'], ['red', 'green'],
                            ['red', 'green', 'grey'], ['green'], ['green', 'grey'], ['green', 'grey'],
                            ['yellow', 'grey'],
                            ['yellow'], ['yellow', 'grey'], ['yellow'], ['yellow'], ['yellow'], ['yellow'], ['yellow'],
                            ['yellow', 'lightgreen'], ['lightgreen'], ['lightgreen'], ['lightgreen'],
                            ['lightgreen', 'brown'], ['brown'], ['brown'], ['brown', 'yellow'],
                            ['brown', 'yellow', 'blue'],
                            ['brown', 'yellow', 'blue'], ['blue'], ['blue'], ['blue']]

        self.cells_ways = [(), (2, 22), (1, 3), (2, 4, 30), (3, 5), (4, 6, 7), (5, 7, 8), (5, 6, 8), (6, 7, 9), (8, 10),
                           (11, 12, 9), (10, 12, 13, 27), (10, 11, 13), (11, 12, 14), (13, 15), (14, 16, 17),
                           (15, 17, 25),
                           (15, 16, 18), (17, 19), (18, 20), (19, 21), (20, 22), (1, 21, 23), (22, 24), (23, 25),
                           (16, 24, 26),
                           (25, 27, 29), (26, 28, 11), (27, 29), (26, 28, 30), (29, 3)]

        self.cells_coord = [[], [338, 135], [546, 56], [753, 41], [965, 38], [1172, 48], [1403, 38], [1308, 215],
                            [1535, 215], [1630, 401], [1602, 612], [1395, 642], [1507, 815], [1279, 831], [1072, 851],
                            [861, 851], [749, 682], [636, 840], [432, 820], [228, 780], [77, 642], [88, 442], [238, 305],
                            [417, 406],
                            [607, 470], [810, 490], [1004, 543], [1198, 603], [1178, 410], [992, 332], [832, 218]]

    def render(self):  # надо переписать чтобы все персонажи рендерились
        self.sc.blit(self.board_img, (0, 0))
        places = self.main_hero.places
        for character in places:
            cell = places[character]
            print(cell)
            rect = pygame.Rect(*self.cells_coord[cell], 100, 100)
            print(rect)
            print(character.img)
            self.sc.blit(character.img, rect)
        pygame.display.flip()
        main_hero_id = self.main_hero.id
        pygame.image.save(self.sc, f"pictures/boards_in_game/current_board{main_hero_id}.jpg".format(main_hero_id))

    def search_ways(self, current_cell, num, through=False, hero=None):
        places = self.main_hero.places
        reversed_places = {places[x]: x for x in places}
        if num == 0: return
        for x in self.cells_ways[current_cell]:
            if through or (hero is not None and reversed_places[x] in hero.characters):
                self.search_ways(x, num - 1, through)
            if x not in places.values():
                if not through and not (hero is not None and reversed_places[x] in hero.characters):
                    self.search_ways(x, num - 1, through)
                self.move_options += [x]
