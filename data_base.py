import csv
import telebot

users_id = {}
users_message = {}
heroes = {}
wins_count = {}


def update_database():
    with open("data_base/database.csv", newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for row in reader:
            nick, user_id = str(row['nickname']), int(row['id'])
            users_id[nick] = user_id

    with open("data_base/database.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(["nickname", "id", "message"])
        for nick in users_id:
            writer.writerow([nick, users_id[nick]])