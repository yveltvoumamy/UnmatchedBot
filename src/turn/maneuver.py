from src.auxiliary_objects.default_commands import DefaultCommands
from src.auxiliary_objects.command_parent import Commands
from src.data_objects.data_base import DataBase

default_commands = DefaultCommands()
data_base = DataBase()


class Maneuver(Commands):
    def start_action(self, message):
        hero = data_base.heroes[message.chat.id]
        if message.text == 'Маневр':
            self.bot.send_message(hero.enemy.id, 'Ваш противник совершает маневр')
            hero.draw_card()
            self.bot.send_message(hero.id, 'Отправьте номер карты, которой хотите сбросить для усиления маневра\nВ вашей руке '
                                      'карты пронумерованы сверху вниз начиная с 1\nОтправь 0 если не хочешь усилять маневр')
            self.update(data_base.heroes, data_base.users_message, data_base.users_id)
            self.bot.register_next_step_handler(message, self.increase_maneuver)
            return True
        return False

    def increase_maneuver(self, message):
        if message.text == '0':
            self.play_maneuver(message, 0)
            return
        hero = self.heroes[message.chat.id]
        hand = hero.hand
        try:
            int(message.text)
        except:
            self.bot.send_message(hero.id, 'Отправьте НОМЕР карты')
            self.bot.register_next_step_handler(message, self.increase_maneuver)
            return
        num = int(message.text) - 1
        if 0 > num or num >= len(hand):
            self.bot.send_message(hero.id, 'У вас в руке нет карты с таким номером')
            self.bot.register_next_step_handler(message, self.increase_maneuver)
            return
        self.bot.send_message(hero.id, 'Сбрасываю карту')
        increasing = hero.discard_card(num)
        self.play_maneuver(message, increasing)

    def play_maneuver(self, message, increasing):
        hero = self.heroes[message.chat.id]
        board = hero.main_hero.board
        variants = [[] for i in range(len(hero.characters))]
        for character in hero.characters:
            hero.main_hero.places[character] = None
        places = hero.main_hero.places.values()
        board_img = open(f"pictures/boards_in_game/current_board{hero.main_hero.id}.jpg".format(hero.main_hero.id),
                         'rb')
        self.bot.send_photo(hero.id, board_img)
        board_img.close()
        for i, character in enumerate(hero.characters):
            board.move_options = []
            print(increasing)
            print(hero.move_value + increasing)
            board.search_ways(character.current_cell, hero.move_value + increasing)
            board.move_options = list(set(board.move_options))
            while any(x in places for x in board.move_options):
                for j in range(len(board.move_options)):
                    if board.move_options[j] in places:
                        board.move_options.pop(j)
                        break
            self.bot.send_message(hero.id,
                             'Выберите клетку на которую встанет ' + character.str + f'\n{board.move_options}'.format(
                                 board.move_options))
            variants[i] = board.move_options
        self.bot.send_message(hero.id,
                         'Отправьте номера клеток в том порядке, в котором получили варинты ходов, номера отделяйте побелом')
        self.bot.register_next_step_handler(message, lambda message: self.move_characters(message, variants))

    def move_characters(self, message, variants):
        hero = self.heroes[message.chat.id]
        try:
            cells = [int(x) for x in message.text.split()]
        except:
            self.bot.send_message(hero.id, 'Отправьте НОМЕРА клеток')
            self.bot.register_next_step_handler(message, lambda message: self.move_characters(message, variants))
            return
        cells = [int(x) for x in message.text.split()]
        if len(cells) > len(hero.characters):
            self.bot.send_message(hero.id, 'Выбрано слишком много клеток, попробуйте заново')
            self.bot.register_next_step_handler(message, lambda message: self.move_characters(message, variants))
            return
        if len(set(cells)) == len(cells) and all(x in variants[i] for i, x in enumerate(cells)) and len(cells) == len(
                hero.characters):
            main_hero = hero.main_hero
            places = main_hero.places
            for i, character in enumerate(hero.characters):
                places[character] = cells[i]
                character.current_cell = cells[i]
            hero.main_hero.board.render()
            board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
            self.bot.send_photo(hero.id, board_img)
            board_img.close()
            board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
            hero.actions += 1
            self.bot.send_message(hero.enemy.id,
                             f'Ваш противник закончил маневр, это было его {hero.actions}е действие'.format(
                                 hero.actions))
            default_commands.update(self.heroes, self.users_message, self.users_id)
            default_commands.check_actions(hero)
            self.bot.send_photo(hero.enemy.id, board_img)
            board_img.close()
        elif all(x in variants[i] for i, x in enumerate(cells)) and len(cells) == len(hero.characters):
            self.bot.send_message(hero.id, 'Нельзя ставить несколько персонажей на одну ячейку, попробуйте заново')
            self.bot.register_next_step_handler(message, lambda message: self.move_characters(message, variants))
        elif len(set(cells)) == len(cells) and len(cells) == len(hero.characters):
            for i, x in enumerate(cells):
                if x not in variants[i]:
                    self.bot.send_message(hero.id, 'Персонаж ' + hero.characters[i].str + ' не может дойти до клетки ' + str(
                        cells[i]))
            self.bot.send_message(hero.id, 'Попробуйте еще раз')
            self.bot.register_next_step_handler(message, lambda message: self.move_characters(message, variants))
        elif len(set(cells)) == len(cells) and all(x in variants[i] for i, x in enumerate(cells)):
            self.bot.send_message(hero.id, 'Укажите клетки для всех персонажей сразу')
            self.bot.register_next_step_handler(message, lambda message: self.move_characters(message, variants))
        else:
            self.bot.send_message(hero.id, 'Вы совершили несколько ошибок в расстановке персонажей, прочтите правила /rules')
            self.bot.register_next_step_handler(message, lambda message: self.move_characters(message, variants))
