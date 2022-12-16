from random import randint
from src.auxiliary_objects.command_parent import Commands


class DefaultCommands(Commands):

    def check_actions(self, hero, show=True):
        if hero.actions == 2:
            if hero.str == 'bigfoot':
                hero.effect()
                hero.enemy.effect()
                while not hero.enemy.effect_done:
                    if not randint(0, 100):
                        print('hero effect')
            hero.your_turn = False
            hero.enemy.your_turn = True
            hero.actions = 0
            self.bot.send_message(hero.id, 'Ваш ход окончен')
            self.check_cards_in_hand(hero)
            self.bot.send_message(hero.enemy.id, 'Ваш ход !\nВоспользуйтесь командой /turn, чтобы выбрать действие')
            return True
        if hero.actions == 1 and show:
            self.bot.send_message(hero.id,
                                  'У вас есть еще 1 действие, воспользуйтесь коммандой /turn чтобы продолжить ход')
            return False
        if hero.actions == 0:
            for character in hero.characters:
                character.last_cell = character.current_cell
        return False

    def check_cards_in_hand(self, hero):
        count = len(hero.hand)
        if count <= 7:
            return
        else:
            count -= 7
            if count == 1:
                self.bot.send_message(hero.id,
                                      'У вас на руке слишком много карт, выберите карту, которую хотите сбросить и '
                                      'отправьте ее номер')
            else:
                self.bot.send_message(hero.id,
                                      'У вас на руке слишком много карт, выберите карты, которые хотите сбросить и '
                                      'отправьте их номера\n' f'карты пронумерованы сверху вниз начиная с 1, вам нужно '
                                      f'сбросить {count} карт'.format(count))
            self.default_commands.show_hand(hero)
            message = self.users_message[hero.id]
            self.bot.register_next_step_handler(message, lambda message: self.choose_discard_cards(message, count))

    def choose_discard_cards(self, message, count):
        hero = self.heroes[message.chat.id]
        try:
            [int(num) for num in message.text.split()]
        except:
            self.bot.send_message(hero.id, 'Отправьте НОМЕРА карт')
            self.bot.register_next_step_handler(message, lambda message: self.choose_discard_cards(message, count))
            return
        discarding_cards = [int(num) for num in message.text.split()]
        if len(discarding_cards) != count:
            self.bot.send_message(hero.id,
                                  f'Вам нужно сбросить {count} карт, а вы выбрали {len(discarding_cards)} карт'.format(
                                      count, len(discarding_cards)))
            self.bot.register_next_step_handler(message, lambda message: self.choose_discard_cards(message, count))
            return
        for num in message.text.split():
            hero.discard_card(int(num) - 1)

    def show_hand(self, hero):
        hand = hero.hand
        for card in hand:
            card.show_card()

    def show_deck(self, hero):
        deck = hero.hand + hero.deck
        for card in deck:
            card.show_card()
