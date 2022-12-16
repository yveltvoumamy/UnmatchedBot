from random import randint
from src.auxiliary_objects.command_parent import Commands
from src.auxiliary_objects.default_commands import DefaultCommands
from src.data_objects.data_base import DataBase

data_base = DataBase()
default_commands = DefaultCommands()


class Sheme(Commands):
    def start_action(self, message):
        hero = data_base.heroes[message.chat.id]
        if message.text == 'Прием':
            self.bot.send_message(hero.enemy.id, 'Ваш противник играет карту приема')
            self.update(data_base.heroes, data_base.users_message, data_base.users_id)
            self.check_scheme(message)
            return True
        return False

    def check_scheme(self, message):
        hero = self.heroes[message.chat.id]
        hand = hero.hand
        pool = []
        for card in hand:
            if card.type == 'scheme':
                self.bot.send_message(message.chat.id, str(hand.index(card) + 1))
                card.show_card()
                pool.append(card)
        if len(pool) == 0:
            self.bot.send_message(hero.id, 'У вас нет карт приемов')
            return
        self.bot.send_message(hero.id, 'Выберите карту, которую хотите разыграть и отправьте ее номер')
        self.bot.register_next_step_handler(message, self.play_scheme)

    def play_scheme(self, message):
        hero = self.heroes[message.chat.id]
        hand = hero.hand
        try:
            int(message.text)
        except:
            self.bot.send_message(hero.id, 'Отправьте НОМЕР карты')
            self.bot.register_next_step_handler(message, self.play_scheme)
            return
        num = int(message.text) - 1
        if 0 > num or num >= len(hand):
            self.bot.send_message(hero.id, 'У вас в руке нет карты с таким номером')
            self.bot.register_next_step_handler(message, self.play_scheme)
            return
        if hand[num].type != 'scheme':
            self.bot.send_message(hero.id, 'Выбранная карта не является картой маневра')
            self.bot.register_next_step_handler(message, self.play_scheme)
            return
        hand[num].effect()
        while not hero.effect_done:
            if not randint(0, 100):
                print('waiting for playing scheme')
        hero.effect_done = False
        hero.actions += 1
        hand[num].show_card(hero.enemy)
        hand.pop(num)
        self.bot.send_message(hero.enemy.id,
                         f'Ваш противник разыграл карту приема, это было его {hero.actions}е действие'.format(
                             hero.actions))
        default_commands.update(self.heroes, self.users_message, self.users_id)
        default_commands.check_actions(hero)