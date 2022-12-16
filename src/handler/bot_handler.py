import telebot
from telebot import types
import pygame
from random import randint
from src.data_objects.config import TOKEN
from src.data_objects.data_base import *
from src.handler.start_game import StartGame
from src.auxiliary_objects.default_commands import DefaultCommands
from src.turn.maneuver import Maneuver
from src.turn.attack import Attack
from src.turn.sheme import Sheme
from src.auxiliary_objects.command_parent import CommandComposite

bot = telebot.TeleBot(TOKEN)
pygame.init()
sc = pygame.display.set_mode((1800, 1000))
default_commands = DefaultCommands()
start_game = StartGame()
maneuver = Maneuver()
attack = Attack()
sheme = Sheme()
data_base = DataBase()
commands = [sheme, attack, maneuver, start_game, default_commands]
actions = CommandComposite()
actions.add(maneuver)
actions.add(attack)
actions.add(sheme)
print(actions.get_list())
setattr(data_base, 'bot',  bot)
for command in commands:
    setattr(command, 'bot', bot)
    setattr(command, 'sc', sc)


def start_bot():
    data_base.update_database()
    bot.infinity_polling(none_stop=True)


@bot.message_handler(commands=['help'])
def helping(message):
    bot.send_message(message.chat.id, 'Добро пожаловать !\nС помощью меня можно играть в настольную игру Unmatched\n'
                     '\nСписок команд:\n/rules - правила игры\n/register - регистрация '
                     '(нужна для начала игры)\n/game_start - начало игры, выбор противника и персонажей\n'
                     '/turn - выполнить действие (в свой ход)\n/board - показать игровго поля\n/hp - показаь ваше здоровья'
                     '\n/concede - закночить игру, \n/change_nickname - изменить никнейм')


@bot.message_handler(commands=['board'])
def show_board(message):
    users_nicknames = {data_base.users_id[x]: x for x in data_base.users_id}
    if message.chat.id not in users_nicknames:
        bot.send_message(message.chat.id, 'Вы еще не зарегистрированы, воспользуйтесь коммандой /register')
        return
    if message.chat.id not in data_base.heroes:
        bot.send_message(message.chat.id, 'Вы не находитесь в игре, создайте игру командой /game_start')
        return
    hero = data_base.heroes[message.chat.id]
    main_hero = hero.main_hero
    board_img = open(f"pictures/boards_in_game/current_board{main_hero.id}.jpg".format(main_hero.id), 'rb')
    bot.send_photo(hero.id, board_img)
    board_img.close()


@bot.message_handler(commands=['hp'])
def show_heroes_hp(message):
    users_nicknames = {data_base.users_id[x]: x for x in data_base.users_id}
    if message.chat.id not in users_nicknames:
        bot.send_message(message.chat.id, 'Вы еще не зарегистрированы, воспользуйтесь коммандой /register')
        return
    if message.chat.id not in data_base.heroes:
        bot.send_message(message.chat.id, 'Вы не находитесь в игре, создайте игру командой /game_start')
        return
    hero = data_base.heroes[message.chat.id]
    hero.show_hp()


@bot.message_handler(commands=['rules'])
def show_rules(message):
    markup = types.InlineKeyboardMarkup()
    btn_my_site = types.InlineKeyboardButton(text='Правила', url='https://pre.gaga.ru/wp-content/uploads/2020/08/'
                                                        'unmatched-bol-1_rulebook_ru_v1.pdf?ysclid=lb44bcb1x2524589211')
    markup.add(btn_my_site)
    bot.send_message(message.chat.id, "Нажми на кнопку чтобы прочитать правила.", reply_markup=markup)


@bot.message_handler(commands=['concede'])
def concede(message):
    users_nicknames = {data_base.users_id[x]: x for x in data_base.users_id}
    if message.chat.id not in users_nicknames:
        bot.send_message(message.chat.id, 'Вы еще не зарегистрированы, воспользуйтесь коммандой /register')
        return
    if message.chat.id not in data_base.heroes:
        bot.send_message(message.chat.id, 'Вы не находитесь в игре, создайте игру командой /game_start')
        return
    attack.update(data_base.heroes, data_base.users_message, data_base.users_id)
    attack.end_game(message)


@bot.message_handler(commands=['register'])
def registration(message):
    users_nicknames = {data_base.users_id[x]: x for x in data_base.users_id}
    print(users_nicknames)
    print(type(message))
    if message.chat.id in users_nicknames:
        nickname = users_nicknames[message.chat.id]
        bot.send_message(message.chat.id, 'Ваш никнейм ' + str(nickname))
        return
    bot.send_message(message.chat.id, 'Введите ваш никнейм')
    bot.register_next_step_handler(message, data_base.registr_in_database)


@bot.message_handler(commands=['change_nickname'])
def change_nickname(message):
    users_nicknames = {data_base.users_id[x]: x for x in data_base.users_id}
    if message.chat.id not in users_nicknames:
        bot.send_message(message.chat.id, 'Вы еще не зарегистрированы')
        return
    old_nickname = users_nicknames[message.chat.id]
    del data_base.users_id[old_nickname]
    bot.send_message(message.chat.id, 'Ваш старый никнейм ' + str(old_nickname) + '\nВведите новый')
    bot.register_next_step_handler(message, data_base.change_in_data_base)


@bot.message_handler(commands=['game_start'])
def checking_current_games(message):
    users_nicknames = {data_base.users_id[x]: x for x in data_base.users_id}
    if message.chat.id not in users_nicknames:
        bot.send_message(message.chat.id, 'Вы еще не зарегистрированы, воспользуйтесь коммандой /register')
        return
    if message.chat.id in data_base.heroes:
        bot.send_message(message.chat.id, 'Вы не можете начать новую партию, так как не окончили предыдущую, '
                                          'воспользуйтесь командой /concede')
        return
    bot.send_message(message.chat.id, 'Введите никнейм вашего противника')
    bot.register_next_step_handler(message, search_opponent)


def search_opponent(message):
    opponent = message.text
    if opponent not in data_base.users_id:
        bot.send_message(message.chat.id, 'Ваш противник не зарегистрирован, либо вы неправильно ввели его никнейм')
        return
    if opponent in data_base.heroes:
        bot.send_message(message.chat.id, 'Ваш противник сейчас в игре, дождитесь окончания партии')
        return
    if data_base.users_id[opponent] == message.chat.id:
        bot.send_message(message.chat.id, 'Вы не можете играть сами с собой')
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    medusa_button = types.KeyboardButton('Медуза')
    bigfoot_button = types.KeyboardButton('Бигфут')
    markup.add(medusa_button, bigfoot_button)
    bot.send_message(message.chat.id, 'Выберите персонажа из списка', reply_markup=markup)
    start_game.update(data_base.heroes, data_base.users_message, data_base.users_id)
    print('имя бота ', bot)
    bot.register_next_step_handler(message, lambda message: start_game.pick_heroes(message, data_base.users_id[opponent]))


@bot.message_handler(commands=['hand'])
def show_hand_command(message):
    users_nicknames = {data_base.users_id[x]: x for x in data_base.users_id}
    if message.chat.id not in users_nicknames:
        bot.send_message(message.chat.id, 'Вы еще не зарегистрированы, воспользуйтесь коммандой /register')
        return
    if message.chat.id not in data_base.heroes:
        bot.send_message(message.chat.id, 'Вы не находитесь в игре, создайте игру командой /game_start')
        return
    bot.send_message(message.chat.id, 'Карты на вашей руке:')
    default_commands.update(data_base.heroes, data_base.users_message, data_base.users_id)
    default_commands.show_hand(data_base.heroes[message.chat.id])


@bot.message_handler(commands=['turn'])
def start_turn(message):
    users_nicknames = {data_base.users_id[x]: x for x in data_base.users_id}
    if message.chat.id not in users_nicknames:
        bot.send_message(message.chat.id, 'Вы еще не зарегистрированы, воспользуйтесь коммандой /register')
        return
    if message.chat.id not in data_base.heroes:
        bot.send_message(message.chat.id, 'Вы не находитесь в игре, создайте игру командой /game_start')
        return
    hero = data_base.heroes[message.chat.id]
    if not hero.your_turn:
        bot.send_message(hero.id, 'Сейчас не ваш ход, дождитесь окончания хода противника')
        return
    default_commands.update(data_base.heroes, data_base.users_message, data_base.users_id)
    if default_commands.check_actions(hero, False): return
    attack.update(data_base.heroes, data_base.users_message, data_base.users_id)
    if attack.check_deth(hero): return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    maneuver_button = types.KeyboardButton('Маневр')
    scheme_button = types.KeyboardButton('Прием')
    attack_button = types.KeyboardButton('Атака')
    markup.add(maneuver_button, scheme_button, attack_button)
    bot.send_message(hero.id, 'Выберите действие', reply_markup=markup)
    bot.register_next_step_handler(message, choose_action)


def choose_action(message):
    hero = data_base.heroes[message.chat.id]
    attack.check_deth(hero)
    hero.do_effect = True
    for action in actions.get_list():
        try:
            action.update(data_base.heroes, data_base.users_message, data_base.users_id)
            if action.start_action(message):
                break
        except:
            ...
    else:
        bot.send_message(hero.enemy.id, 'Ваш противник придурок')
        bot.send_message(message.chat.id, 'Неизвестная комманда')
    # if message.text == 'Маневр':
    #     bot.send_message(hero.enemy.id, 'Ваш противник совершает маневр')
    #     hero.draw_card()
    #     bot.send_message(hero.id, 'Отправьте номер карты, которой хотите сбросить для усиления маневра\nВ вашей руке '
    #                               'карты пронумерованы сверху вниз начиная с 1\nОтправь 0 если не хочешь усилять маневр')
    #     maneuver.update(bot, data_base.heroes, sc, data_base.users_message, data_base.users_id)
    #     bot.register_next_step_handler(message, maneuver.increase_maneuver)
    # elif message.text == 'Прием':
    #     bot.send_message(hero.enemy.id, 'Ваш противник играет карту приема')
    #     sheme.update(bot, data_base.heroes, sc, data_base.users_message, data_base.users_id)
    #     sheme.check_scheme(message)
    # elif message.text == 'Атака':
    #     bot.send_message(hero.enemy.id, 'Ваш противник атакует вас !')
    #     attack.update(bot, data_base.heroes, sc, data_base.users_message, data_base.users_id)
    #     attack.check_attack(hero)
    # else:
    #     bot.send_message(hero.enemy.id, 'Ваш противник придурок')
    #     bot.send_message(message.chat.id, 'Неизвестная комманда')

