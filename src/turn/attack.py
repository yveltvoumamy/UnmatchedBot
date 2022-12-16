from src.auxiliary_objects.command_parent import Commands
from src.auxiliary_objects.default_commands import DefaultCommands
from src.data_objects.data_base import DataBase
from random import randint

default_commands = DefaultCommands()
data_base = DataBase()


class Attack(Commands):
    def start_action(self, message):
        hero = data_base.heroes[message.chat.id]
        if message.text == 'Атака':
            self.bot.send_message(hero.enemy.id, 'Ваш противник атакует вас !')
            self.check_attack(hero)
            return True
        return False

    def check_attack(self, hero):
        variants = {}
        places = hero.main_hero.places
        board = hero.main_hero.board
        reverse_places = {places[x]: x for x in places}
        for character in hero.characters:
            if character.type == 'melee':
                directions = board.cells_ways[character.current_cell]
                for enemy_cell in directions:
                    if enemy_cell in reverse_places:
                        enemy = reverse_places[enemy_cell]
                        if enemy in hero.enemy.characters:
                            self.bot.send_message(hero.id,
                                             'Ваш ' + character.str + ' может атаковать ' + enemy.str + ' противника')
                            variants[character] = enemy
            if character.type == 'distance':
                directions = []
                for color in board.cells_color[character.current_cell]:
                    directions += board.color_directions[color]
                for enemy_cell in directions:
                    if enemy_cell in reverse_places:
                        enemy = reverse_places[enemy_cell]
                        if enemy in hero.enemy.characters:
                            self.bot.send_message(hero.id,
                                             'Ваш ' + character.str + ' может атаковать ' + enemy.str + ' противника')
                            variants[character] = enemy
        if len(variants) == 0:
            self.bot.send_message(hero.id, 'Вам некого атаковать, поэтому ваша атака заменена на маневр с передвижением на '
                                      '0 ячеек')
            hero.draw_card()
            hero.actions += 1
            self.bot.send_message(hero.enemy.id, 'Ваш противник не смог никого атаковать и вместо атаки совершил маневр с '
                                            f'передвижением на 0 ячеек, это было его {hero.actions} действие'.format(
                hero.actions))
            default_commands.default_commands.update(self.bot, self.heroes, self.sc, self.users_message)
            default_commands.default_commands.check_actions(hero)
            return
        if all(card.who != 'all' and card.who != attacking.str for card in hero.hand if card.type != 'scheme'
                                                                                        and card.type != 'defence' for
               attacking in variants):
            self.bot.send_message(hero.id,
                             'У вас нет карт для атаки в таком положении, поэтому ваша атака заменена на маневр с передвижением на '
                             '0 ячеек')
            hero.draw_card()
            hero.actions += 1
            self.bot.send_message(hero.enemy.id, 'Ваш противник не смог атаковать и вместо атаки совершил маневр с '
                                            f'передвижением на 0 ячеек, это было его {hero.actions} действие'.format(
                hero.actions))
            default_commands.update(self.heroes, self.users_message, self.users_id)
            default_commands.check_actions(hero)
            return
        self.bot.send_message(hero.id,
                         'Выберите персонажа, которым будете атаковать и противника, которого будете атаковать\n'
                         'через пробел сначала напишите имя своего персонажа, потом имя персонажа протиника.'
                         'Указывать надо имена персонажей в таком же формате как в вышеперечисленных вариантах')
        self.bot.register_next_step_handler(self.users_message[hero.id],
                                       lambda message: self.choose_attack_character(message, variants))

    def choose_attack_character(self, message, variants):
        hero = self.heroes[message.chat.id]
        ans = message.text.split()
        if len(ans) != 2:
            self.bot.send_message(hero.id, 'Оправьте ДВА слова: имя вашего атакующего персонажа и имя персонажа противника, '
                                      'которого будете атаковать, попробуйте еще раз')
            self.bot.register_next_step_handler(message, lambda message: self.choose_attack_character(message, variants))
            return
        friends_str = [x.str for x in variants.keys()]
        enemies_str = [x.str for x in variants.values()]
        if ans[0] not in friends_str and ans[1] not in enemies_str:
            self.bot.send_message(hero.id,
                             'Имена персонажей отправлены некоректно\nУказывать имена персонажей надо в таком же '
                             'формате как в вышеперечисленных вариантах, попробуйте еще раз')
            self.bot.register_next_step_handler(message, lambda message: self.choose_attack_character(message, variants))
            return
        if ans[0] not in friends_str:
            self.bot.send_message(hero.id,
                             'Имя вашего атакующего персонажа указано неверно\nУказывать имена персонажей надо в '
                             'таком же формате как в вышеперечисленных вариантах, попробуйте еще раз')
            self.bot.register_next_step_handler(message, lambda message: self.choose_attack_character(message, variants))
            return
        if ans[1] not in enemies_str:
            self.bot.send_message(hero.id,
                             'Имя персонажа противника, которого вы хотите атаковать указано неверно\nУказывать '
                             'имена персонажей надо в таком же формате как в вышеперечисленных вариантах, '
                             'попробуйте еще раз')
            self.bot.register_next_step_handler(message, lambda message: self.choose_attack_character(message, variants))
            return
        attacking = None
        defending = None
        for x in variants:
            if x.str == ans[0] and variants[x].str == ans[1]:
                attacking = x
                defending = variants[x]
        if attacking is None or defending is None:
            self.bot.send_message(hero.id, 'Эти персонажи не могут биться друг с другом, выберите других персонажей')
            self.bot.register_next_step_handler(message, lambda message: self.choose_attack_character(message, variants))
            return
        self.bot.send_message(hero.enemy.id,
                         f'Ваш противник атакует {defending.str} своим {attacking.str}'.format(defending.str,
                                                                                               attacking.str))
        defending.hero.is_defence = defending
        self.bot.send_message(hero.id,
                         f'Отлично, персонаж {attacking.str} атакует персонажа {defending.str} '.format(defending.str,
                                                                                                        attacking.str))
        default_commands.update(self.heroes, self.users_message, self.users_id)
        default_commands.show_hand(hero)
        self.bot.send_message(hero.id, 'Отправьте номер карты, которой хотите атаковать')
        self.bot.register_next_step_handler(message, lambda message: self.choose_attack_card(message, attacking, defending))

    def choose_attack_card(self, message, attacking, defending):
        hero = self.heroes[message.chat.id]
        hand = hero.hand
        try:
            int(message.text)
        except:
            self.bot.send_message(hero.id, 'Отправьте НОМЕР карты')
            self.bot.register_next_step_handler(message, lambda message: self.choose_attack_card(message, attacking, defending))
            return
        num = int(message.text) - 1
        if 0 > num or num >= len(hand):
            self.bot.send_message(hero.id, 'У вас в руке нет карты с таким номером, попробуйте еще раз')
            self.bot.register_next_step_handler(message, lambda message: self.choose_attack_card(message, attacking, defending))
            return
        card = hand[num]
        if card.type != 'attack' and card.type != 'versatile':
            self.bot.send_message(hero.id,
                             'Выбранная карта не является картой атаки или универсальной картой, попробуйте еще раз')
            self.bot.register_next_step_handler(message, lambda message: self.choose_attack_card(message, attacking, defending))
            return
        if card.who != attacking.str and card.who != 'all':
            self.bot.send_message(hero.id,
                             f'Вы не можете использовать эту карту за {attacking.str}, эта карта для {card.who}'.format(
                                 attacking.str, card.who))
            self.bot.register_next_step_handler(message, lambda message: self.choose_attack_card(message, attacking, defending))
            return
        hero.played_card = card
        hero.hand.pop(num)
        self.bot.send_message(hero.id, 'Карта выбрана, ждем пока ваш противник выберет карту')
        enemy_message = self.users_message[hero.enemy.id]
        default_commands.update(self.heroes, self.users_message, self.users_id)
        default_commands.show_hand(hero.enemy)
        self.bot.send_message(hero.enemy.id,
                         'Отправьте номер карты, которой хотите защищаться, отправьте 0 если не хотите защищаться')
        self.bot.register_next_step_handler(enemy_message,
                                       lambda enemy_message: self.choose_defence_card(enemy_message, attacking, defending))

    def choose_defence_card(self, message, attacking, defending):
        hero = self.heroes[message.chat.id]
        hand = hero.hand
        try:
            int(message.text)
        except:
            self.bot.send_message(hero.id, 'Отправьте НОМЕР карты')
            self.bot.register_next_step_handler(message, lambda message: self.choose_defence_card(message, attacking, defending))
            return
        num = int(message.text) - 1
        if num == -1:
            hero.played_card = None
            hero.is_defence = None
            self.playing_battle(hero.enemy, attacking, defending)
            return

        if 0 > num or num >= len(hand):
            self.bot.send_message(hero.id, 'У вас в руке нет карты с таким номером, попробуйте еще раз')
            self.bot.register_next_step_handler(message, lambda message: self.choose_defence_card(message, attacking, defending))
            return
        card = hand[num]
        if card.type != 'defence' and card.type != 'versatile':
            self.bot.send_message(hero.id,
                             'Выбранная карта не является картой защиты или универсальной картой, попробуйте еще раз')
            self.bot.register_next_step_handler(message, lambda message: self.choose_defence_card(message, attacking, defending))
            return
        if card.who != defending.str and card.who != 'all':
            self.bot.send_message(hero.id,
                             f'Вы не можете использовать эту карту за {defending.str}, эта карта для {card.who}'.format(
                                 attacking.str, card.who))
            self.bot.register_next_step_handler(message, lambda message: self.choose_defence_card(message, attacking, defending))
            return
        hero.played_card = card
        hero.hand.pop(num)
        hero.is_defence = None
        self.playing_battle(hero.enemy, attacking, defending)

    def playing_battle(self, hero, attacking, defending):
        hero.hero.hero_in_battle = attacking
        hero.hero.enemy.hero_in_battle = defending
        if defending.hero.played_card is None:
            self.bot.send_message(hero.id, 'Ваш противник не защищается')
            self.bot.send_message(hero.enemy.id, 'Вскрываем карты !')
            attack_card = hero.played_card
            attack_card.show_card(hero.enemy)
            attack_card.show_card()
            if 1 <= attack_card.effect_moment <= 2:
                attack_card.effect()
                while not attacking.hero.effect_done:
                    if not randint(0, 100):
                        print('attacking effect')
            hero.win = True
            hero.enemy.win = False
            damage = attack_card.value
            self.bot.send_message(hero.enemy.id, 'Вы проиграли в бою')
            self.bot.send_message(hero.id, 'Вы победили в бою !')
            defending.deal_damage(damage)
            self.bot.send_message(hero.enemy.id, f'Ваш персонаж {defending.str} получил {damage} урона'.format(damage))
            '''if attack_card.effect_moment == 3 and attacking.hp > 0:
                attack_card.effect()
                while not attacking.hero.effect_done:
                    ...'''
        else:
            attack_card = hero.played_card
            defence_card = hero.enemy.played_card
            self.bot.send_message(hero.id, 'Вскрываем карты !')
            attack_card.show_card()
            defence_card.show_card(hero)
            self.bot.send_message(hero.enemy.id, 'Вскрываем карты !')
            attack_card.show_card(hero.enemy)
            defence_card.show_card()
            if defence_card.effect_moment == 1 and hero.enemy.do_effect:
                defence_card.effect()
                while not defending.hero.effect_done:
                    ...
            if attack_card.effect_moment == 1 and hero.do_effect:
                attack_card.effect()
                while not attacking.hero.effect_done:
                    ...
            if defence_card.effect_moment == 2 and hero.enemy.do_effect:
                defence_card.effect()
                while not defending.hero.effect_done:
                    ...
            if attack_card.effect_moment == 2 and hero.do_effect:
                attack_card.effect()
                while not attacking.hero.effect_done:
                    ...
            damage = 0 if attack_card.value <= defence_card.value else attack_card.value - defence_card.value
            if damage == 0:
                hero.enemy.win = True
                self.bot.send_message(hero.id, 'Вы проиграли в бою')
                self.bot.send_message(hero.enemy.id, 'Вы победили в бою !')
            else:
                hero.win = True
                self.bot.send_message(hero.enemy.id, 'Вы проиграли в бою')
                self.bot.send_message(hero.id, 'Вы победили в бою !')
            defending.deal_damage(damage)
            self.bot.send_message(hero.enemy.id, f'Ваш персонаж {defending.str} получил {damage} урона'.format(damage))
            if defence_card.effect_moment == 3 and hero.enemy.do_effect:
                defence_card.effect()
                while not defending.hero.effect_done:
                    ...
        if attack_card.effect_moment == 3 and hero.do_effect:
            attack_card.effect()
            while not attacking.hero.effect_done:
                ...

        hero.do_effect = True
        hero.enemy.do_effect = True
        hero.played_card = None
        hero.enemy.played_card = None
        hero.win = False
        hero.enemy.win = False
        hero.hero.hero_in_battle = None
        hero.hero.enemy.hero_in_battle = None
        hero.effect_done = False
        hero.enemy.effect_done = False
        hero.actions += 1
        self.bot.send_message(hero.enemy.id,
                         f'Ваш противник закончил атаку, это было его {hero.actions} действие'.format(hero.actions))
        self.bot.send_message(hero.id, f'Это было ваше {hero.actions} действие'.format(hero.actions))
        default_commands.update(self.heroes, self.users_message, self.users_id)
        default_commands.check_actions(hero)
        self.check_deth(hero.enemy)

    def check_deth(self, hero):
        if hero.hp <= 0:  # на случай смерти от фатига
            self.bot.send_message(hero.id, 'Вы проиграли')
            self.bot.send_message(hero.enemy.id, 'Вы выиграли')
            message = data_base.users_message[hero.id]
            self.end_game(message)
            return True
        return False

    def end_game(self, message):
        hero = data_base.heroes[message.chat.id]
        del data_base.heroes[hero.id]
        del data_base.heroes[hero.enemy.id]