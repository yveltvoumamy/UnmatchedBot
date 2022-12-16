import csv
import telebot
import pickle


class DataBase():
    users_id = {}
    users_message = {}
    heroes = {}
    wins_count = {}
    bot = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DataBase, cls).__new__(cls)
        return cls.instance

    def update_database(self):
        ...
    #    with open("data_base/database.csv", newline="") as csvfile:
    #        reader = csv.DictReader(csvfile, delimiter=";")
    #        for row in reader:
    #            nick, user_id, message = str(row["nickname"]), int(row["id"]), bytes(row["message"])
    #            self.users_id[nick] = user_id
    #            self.users_message[user_id] = pickle.loads(message)
    #
    #    with open("data_base/database.csv", "w", newline="") as csvfile:
    #        writer = csv.writer(csvfile, delimiter=";")
    #        writer.writerow(["nickname", "id", "message"])
    #       for nick in self.users_id:
    #           writer.writerow([nick, self.users_id[nick], pickle.dumps(self.users_message[self.users_id[nick]])
    #

    def registr_in_database(self, message):
        if message.text not in self.users_id:
            self.users_id[message.text] = message.chat.id
            self.users_message[message.chat.id] = message
            self.update_database()
            self.wins_count[message.chat.id] = 0
            self.bot.send_message(message.chat.id, 'Вы успешно зарегистрированы')
        else:
            self.bot.send_message(message.chat.id, 'Такой никнейм уже зарегистрирован, выберите другой')

    def change_in_data_base(self, message):
        new_nickname = message.text
        self.users_id[new_nickname] = message.chat.id
        self.bot.send_message(self.users_id[new_nickname], 'Ваш никнейм успешно изменен')

