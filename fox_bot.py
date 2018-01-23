#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from bs4 import BeautifulSoup
import requests
import telebot
import time
import datetime
import json
import random
import io


my_id = 105698410
admin_ids = [my_id]
# token = '464405818:AAFnJH_fXXWZckK6hOM5wadXulKMKp4w3jE'  # test token
token = '481006531:AAG4WhndJD3mowdu1GpbbtfgKUOY969EA5Q'  # work token

message_file = 'all_messages.txt'
# 407850900: 'Паллада-5'

links = {
    'Foxes': {
        'schedule': 'http://volleymsk.ru/ap/rasp.php?id=728',
        'stats': 'http://volleymsk.ru/ap/trntable.php?trn=728'},
    'Антигравитация': {
        'schedule': 'http://volleymsk.ru/ap/rasp.php?id=702',
        'stats': 'http://volleymsk.ru/ap/trntable.php?trn=702'},
    'Паллада-5': {
        'schedule': 'http://volleymsk.ru/ap/rasp.php?id=735',
        'stats': 'http://volleymsk.ru/ap/trntable.php?trn=735'},
    'Иствуд-2': {
        'schedule': 'http://volleymsk.ru/ap/rasp.php?id=728',
        'stats': 'http://volleymsk.ru/ap/trntable.php?trn=728'},
    'ВК "Русская Рулетка"': {
        'schedule': 'http://volleymsk.ru/ap/rasp.php?id=705',
        'stats': 'http://volleymsk.ru/ap/trntable.php?trn=705'}
}


bot = telebot.TeleBot(token)


class TeamTracker():

    def __init__(self):
        self.DEF_TEAM = 'Foxes'
        self.FILE_NAME = 'current_teams.json'
        self.current_teams = self.read_current_teams_from_file()

    def set_team(self, uid, team):
        if team in links.keys():
            uid = str(uid)
            self.current_teams[uid] = team
            self.update_dictionary()
        else:
            raise('Invalid team')

    def set_deafault_team(self, uid):
        uid = str(uid)
        self.current_teams[uid] = self.DEF_TEAM
        self.update_dictionary()
        self.send_file(my_id, self.FILE_NAME)

    def get_team(self, uid):
        uid = str(uid)
        return self.current_teams.get(uid)

    def update_dictionary(self):
        with open(self.FILE_NAME, 'w') as f:
            json.dump(self.current_teams, f)

    def read_current_teams_from_file(self):
        try:
            with open(self.FILE_NAME, 'r') as f:
                return json.load(f)
        except Exception:
            print('No file')
            return {}

    def if_exist(self, uid):
        uid = str(uid)
        if self.current_teams.get(uid):
            return True
        return False

    def delete_user(self, uid):
        uid = str(uid)
        result = self.current_teams.pop(uid, False)
        if result:
            self.update_dictionary()
            self.send_file(my_id, self.FILE_NAME)
            return True
        return False

    def send_file(self, uid, file):
        document = open(file, 'rb')
        bot.send_chat_action(uid, 'upload_document')
        bot.send_document(uid, document)
        document.close()

    def clear_file(self, file):
        with open(file, 'w') as f:
            f.write('')


# =============== Bot info class ======================


class BotInfo:

    def __init__(self):
        self.foxes_file = 'urls.txt'
        self.BIRTHDAY_FILE = 'birthdays.json'
        self.year = datetime.datetime.now().year
        self.TRAINING_FILE = 'trainings.json'
        self.message_count = 0

    def get_scores(self, link, uid):
        num_spaces = 15

        HTML_DOC = requests.get(link).content

        text = 'Место:' + '  ' + 'Команда' + ': ' + ' '*(num_spaces-7) + 'Очки:' + '\n'
        soup = BeautifulSoup(HTML_DOC, 'html.parser')
        all_teams = {}
        table = [s for s in soup(text=team_tracker.get_team(uid))][0]
        for chunk in [i for i in table.parent.parent.parent.parent.parent.parent.children if i != '\n'][1:]:
            for i, data in enumerate(chunk.children):
                if i == 0:
                    place = data.text
                elif i == 2:
                    team = data.text
                elif i == 4:
                    score = data.text
            all_teams[team] = {'place': place,
                               'score': score}
        sort = sorted(all_teams.keys(), key=lambda x: int(all_teams[x]['place']))
        for team in sort:
            text += str(all_teams[team]['place']) + 8*' ' + team + ': ' + ' '*2*(num_spaces-len(team)) + str(all_teams[team]['score']) + '\n'
        return text

    def get_schedule(self, link, uid):

        HTML_DOC = requests.get(link).content
        query_team = team_tracker.get_team(uid)
        soup = BeautifulSoup(HTML_DOC, 'html.parser')
        games = []

        for elem in soup(text=query_team):
            tag = elem.parent
            if tag.name != 'option':
                games.append(' => '.join((c.text) for c in tag.parent.parent.children if c != '\n'))

        return '\n\n'.join(games)

    def get_fox_picture(self):

        with open(self.foxes_file, 'r') as f:
            foxes = list(f.readlines())
        return random.choice(foxes)

    def nearest_date(self, base, dates):

            fourteen_hrs = 14*60*60
            nearness = {int(date.strftime("%s")) - int(base.strftime("%s")): date \
                for date in dates.keys() if (int(base.strftime("%s")) <= int(date.strftime("%s")) + fourteen_hrs)}
            if nearness:
                return dates[nearness[min(nearness.keys())]]
            return ''

    def get_birthday(self):

        with open(self.BIRTHDAY_FILE, 'r') as f:
            birthdays = json.load(f)
            dates = {datetime.datetime.strptime(key+'.'+str(self.year), '%d.%m.%Y'): key for key in birthdays.keys()}
            nearest = self.nearest_date(datetime.datetime.now(), dates)
            if nearest:
                return birthdays[nearest]['date'] + ':  \n' + birthdays[nearest]['name']
            return 'В этом году больше нет Дней Рождения :('

    def get_training(self):

        with open(self.TRAINING_FILE, 'r') as f:
            trainings = json.load(f)
            dates = {datetime.datetime.strptime(key+'.'+str(self.year), '%d.%m.%Y'): key for key in trainings.keys()}
            nearest = self.nearest_date(datetime.datetime.now(), dates)
            if nearest:
                return trainings[nearest]['day']
            return 'Тренировки пока не запланированы :('

    def add_training(self, date, text):

        try:
            with open(self.TRAINING_FILE, 'r') as f:
                trainings = json.load(f)

            trainings[date] = {'day': text}

            with open(self.TRAINING_FILE, 'w') as f:
                json.dump(trainings, f)
            return True
        except Exception as e:
            error = str(datetime.datetime.now()) + ': ' + str(e.args[-1])
            bot = telebot.TeleBot(token)
            bot.send_message(my_id, error)
            return False

    def add_birthday(self, date, text, name):

        try:
            with open(self.BIRTHDAY_FILE, 'r') as f:
                birthdays = json.load(f)
            if date in birthdays.keys():
                birthdays[date]['name'] += '\n' + name
            else:
                birthdays[date] = {'name': name, 'date': text}

            with open(self.BIRTHDAY_FILE, 'w') as f:
                json.dump(birthdays, f)
            return True
        except Exception as e:
            error = str(datetime.datetime.now()) + ': ' + str(e.args[-1])
            bot = telebot.TeleBot(token)
            bot.send_message(my_id, error)
            return False

# =====================================================

bot_info = BotInfo()
team_tracker = TeamTracker()

# =============== Start handlers ======================

def basic_start_handler(user_markup, team=None):
    func_dict = {
        None: my_start_handler,
        'Foxes': foxes_start_handler,
        'Антигравитация': common_start_handler,
        'Паллада-5': common_start_handler,
        'Иствуд-2': common_start_handler,
        'ВК "Русская Рулетка"': common_start_handler}
    if team in func_dict.keys():
        func_dict[team](user_markup)
    else:
        print(team, 'wrong team!')

def my_start_handler(user_markup):
    user_markup.row('/start', '/stop')
    user_markup.row('Иствуд-2', 'Паллада-5', 'Foxes')
    user_markup.row('Антигравитация', 'ВК "Русская Рулетка"')
    user_markup.row('Commands')
    return

def foxes_start_handler(user_markup):
    user_markup.row('/start', '/stop')
    user_markup.row('Расписание', 'Статистика')
    user_markup.row('Ближайший День Рождения', 'Ближайшая тренировка')
    user_markup.row('Хочу картинку Лисички!')
    return

def common_start_handler(user_markup):
    user_markup.row('/start', '/stop')
    user_markup.row('Расписание')
    user_markup.row('Статистика')
    return

def claim_new_user(user):
    text = 'NEW USER: \n' + str(user)
    bot.send_message(my_id, text)

# =====================================================

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    uid = message.from_user.id
    if uid in admin_ids:
        team = None

    elif team_tracker.if_exist(uid):
        team = team_tracker.get_team(uid)

    else:
        team_tracker.set_deafault_team(uid)
        team = team_tracker.get_team(uid)
        claim_new_user(message.from_user)

    basic_start_handler(user_markup, team)
    try:
        if message.from_user.first_name:
            bot.send_message(message.from_user.id, 'Привет, ' + message.from_user.first_name + ' :)', reply_markup=user_markup)
        else:
            bot.send_message(message.from_user.id, 'Привет! :)', reply_markup=user_markup)
    except UnicodeEncodeError:
        bot.send_message(message.from_user.id, 'Привет! :)', reply_markup=user_markup)

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    hide_markup = telebot.types.ReplyKeyboardHide()
    bot.send_message(message.from_user.id, 'Пока :)', reply_markup=hide_markup)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        with io.open(message_file, 'a', encoding='utf8') as f:
            log = u'{} -- {} {}: {}\n'.format(str(datetime.datetime.now()), message.from_user.first_name, message.from_user.last_name, message.text)
            f.write(log)
    except Exception as e:
        bot.send_message(my_id, 'Writing message to file FAILED:\n{}'.format(str(e)))

    print(message.text, '  ', message.from_user)

    try:
        bot_info.message_count += 1
        if bot_info.message_count % 40 == 0:
            team_tracker.send_file(my_id, message_file)
    except Exception as e:
        bot.send_message(my_id, 'Sending message file FAILED:\n{}'.format(str(e)))


    if message.from_user.id != my_id:
        bot.send_message(my_id, 'New message: \n{} {}:\n{}'.format(message.from_user.first_name, message.from_user.last_name, message.text))
    
    if message.text == u'Расписание':
        try:
            uid = message.from_user.id
            schedule_link = links[team_tracker.get_team(uid)]['schedule']
            text = bot_info.get_schedule(schedule_link, uid)
            bot.send_message(message.from_user.id, text)
        except KeyError:
            pass

    elif message.text == u'Хочу картинку Лисички!':
        text = bot_info.get_fox_picture()
        bot.send_message(message.from_user.id, text)

    elif message.text == u'Ближайший День Рождения':
        text = bot_info.get_birthday()
        bot.send_message(message.from_user.id, text)

    elif message.text == u'Ближайшая тренировка':
        text = bot_info.get_training()
        bot.send_message(message.from_user.id, text)

    elif message.text == u'Статистика':
        try:
            uid = message.from_user.id
            stats_link = links[team_tracker.get_team(uid)]['stats']
            text = bot_info.get_scores(stats_link, uid)
            bot.send_message(message.from_user.id, text)
        except KeyError:
            pass

    elif message.text in links.keys():
        uid = message.from_user.id
        team = message.text
        team_tracker.set_team(uid, team)
        hide_markup = telebot.types.ReplyKeyboardHide()
        bot.send_message(uid, 'Инфо о следующей команде: ', reply_markup=hide_markup)
        user_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        basic_start_handler(user_markup, team)
        bot.send_message(uid, '______' + team + '______', reply_markup=user_markup)



    # ================ ## private ## ===========================
    else:
        if message.from_user.id == my_id:
            if message.text.split(' ')[0] == 'Set':
                try:
                    uid, team = message.text.split(' ')[1], message.text.split(' ')[2]
                    team_tracker.set_team(uid, team)
                    bot.send_message(my_id, 'Team has been updated successfully!')
                    team_tracker.send_file(my_id, team_tracker.FILE_NAME)
                except:
                    bot.send_message(message.my_id, 'Invalid TEAM')

            elif message.text.split(' ')[0] == 'Delete':
                uid = message.text.split(' ')[1]
                if team_tracker.delete_user(uid):
                    bot.send_message(my_id, 'User {} deleted.'.format(uid))
                else:
                    bot.send_message(my_id, 'User {} does not exist.'.format(uid))
            
            elif message.text.split(' ')[0] == 'Add_training':
                try:
                    date, text = message.text.split(' ')[1], ' '.join(message.text.split(' ')[2:])
                    bot_info.add_training(date, text)
                    bot.send_message(my_id, 'Training has been added successfully!\ndate: {}\ntext: {}'.format(date, text))
                    team_tracker.send_file(my_id, bot_info.TRAINING_FILE)
                except Exception as e:
                    print(e)
                    bot.send_message(my_id, 'Training adding failed')

            elif message.text.split(' ')[0] == 'Add_birthday':
                try:
                    date, name, text = message.text.split(' ')[1], ' '.join(message.text.split(' ')[2:4]), ' '.join(message.text.split(' ')[4:])
                    bot_info.add_birthday(date, text, name)
                    bot.send_message(my_id, 'Birthday has been added successfully!\nname: {}\ndate: {}\ntext: {}'.format(name, date, text))
                    team_tracker.send_file(my_id, bot_info.BIRTHDAY_FILE)
                except Exception as e:
                    print(e)
                    bot.send_message(my_id, 'Birthday adding failed')
            
            elif message.text == 'Commands':
                text = 'COMMANDS:\n\nSet (uid) (team)\nDelete (uid)\nAdd_training (date (e.g. 24.01)) (text(e.g. 24 января, СР 18.30))\
                \nAdd_birthday (date (e.g. 26.08)) (name(e.g. Кухарева Даша)) (text(e.g.26 августа))\nClear message file\
                \n\nTEAMS:\n\nFoxes\nАнтигравитация\nИствуд-2\nПаллада-5\nВК "Русская Рулетка"\
                \n\nOPTIONS:\n\nРасписание\nСтатистика\nБлижайший День Рождения\
                \nБлижайшая тренировка\nХочу картинку Лисички'
                bot.send_message(my_id, text)

            elif message.text == 'Clear message file':
                try:
                    team_tracker.send_file(my_id, message_file)
                    team_tracker.clear_file(message_file)
                    bot.send_message(my_id, 'The message file has been cleared successfully.')
                except Exception as e:
                    print(e)
                    bot.send_message(my_id, 'Error. Message file has not been cleared.')

            else:
                bot.send_message(my_id, 'Artem, I don\'t know this command!')
        else:
            bot.send_message(message.from_user.id, 'То, что ты пишешь - полная чушь!')


#bot.polling(none_stop=True, interval=0)

while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=60)
    except Exception as e:
        print(e, e.args[-1])
        with open('bot_logger.txt', 'a') as f:
            error = str(datetime.datetime.now()) + ': ' + str(e.args[-1]) + '\n'
            f.write(error)

        bot = telebot.TeleBot(token)
        bot.send_message(my_id, error)
        bot.stop_polling()
        time.sleep(5)

