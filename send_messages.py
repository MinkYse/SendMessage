from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

import PySimpleGUI as sg

from time import sleep
from datetime import datetime, timedelta, time
from random import randint, uniform
import sys
import shutil
import os
import re
import logging
from configparser import ConfigParser

import name_synonim
import text_randomizer


logging.basicConfig(format='[%(levelname)s] - [%(asctime)s] -  %(message)s', datefmt='%d.%m.%y %H:%M:%S',
                    level=logging.INFO)


class VKSendMessage:

    def __init__(self, list_name, pause_area, message_text_file):
        self.browser = None
        self.message_text_file = f'Сообщения-список\{message_text_file}'
        self.list_name = f'Абоненты-список\{list_name}'
        self.pause_area = pause_area
        self.settings = ConfigParser()
        self.chrome_profiles_dst = fr'C:\Users\{os.getlogin()}\AppData\Local\Google\Chrome\User Data'
        self.copy_profiles_dst = fr'{os.path.abspath("send_messages.py").replace("send_messages.py", "Profiles_VK")}'
        self.settings.read(r'send_messages_config.cfg', encoding='utf-8')
        self.url = 'https://vk.com/im?sel='
        self.pause_between_symbol = self.settings['time']['pause_between_symbol']

        if self.settings['path']['chrome_profile_name'] == 'Default' \
                or self.settings['path']['chrome_profile_name'] == '':
            logging.warning('Вы зашли со стандартного профиля, если вы хотите поменять профиль, измените его '
                            'название в конфигурационном файле')

    def get_users_id(self):
        with open(self.list_name, 'r') as file:
            users_id = file.read().split('\n')
            users_id = [user[2:] for user in users_id if user != '']

        return users_id

    def click(self, button):
        ActionChains(self.browser).move_to_element(button).click().perform()
        sleep(2)

    @staticmethod
    def string_randomize(string):
        try:
            randomized_string = text_randomizer.handle_text(string)
            return randomized_string
        except text_randomizer.FormatException:
            logging.error(f'Некорректный ти сообщения {string}')

    @staticmethod
    def copy_directory(src, dst, symlinks=False, ignore=None):
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                try:
                    shutil.copytree(s, d, symlinks, ignore)
                except:
                    continue
            else:
                try:
                    shutil.copy2(s, d)
                except:
                    continue

    def copy_profile_directory(self):
        if os.path.exists(self.copy_profiles_dst):
            date_creation = os.path.getctime(self.copy_profiles_dst)
            date_creation = datetime.fromtimestamp(date_creation)
            date_creation = timedelta(days=date_creation.day, hours=date_creation.hour,
                                      minutes=date_creation.minute, seconds=date_creation.second)

            date_now = datetime.now()
            date_now = timedelta(days=date_now.day, hours=date_now.hour,
                                 minutes=date_now.minute, seconds=date_now.second)

            if (date_now - date_creation).seconds > 18000:
                try:
                    logging.info('Начало копирование папки профилей')
                    shutil.rmtree(self.copy_profiles_dst)
                    self.copy_directory(self.chrome_profiles_dst, self.copy_profiles_dst)
                    logging.info('Копирование завершено')
                except Exception as message:
                    logging.error(
                        'Не удается скопировать папку с профилями, проверьте путь к директории и попробуйте снова')
                    input('Нажмите любую клавишу для выхода: ')
                    sys.exit()
            else:
                pass
        else:
            try:
                logging.info('Начало копирование папки профилей')
                self.copy_directory(self.chrome_profiles_dst, self.copy_profiles_dst)
                logging.info('Копирование завершено')
            except Exception as message:
                logging.error(
                    'Не удается скопировать папку с профилями, проверьте путь к директории и попробуйте снова')
                input('Нажмите любую клавишу для выхода: ')
                sys.exit()

    def get_random_string(self):
        with open(self.message_text_file, 'r', encoding='utf-8') as file:
            lines = file.read().split('\n')
        lines = [line.strip() for line in lines if line != '']

        return lines[randint(0, len(lines) - 1)]

    def create_list(self, users_id):
        with open(self.list_name, 'w') as file:
            for user in users_id:
                file.write(f'{user}\n')

    @staticmethod
    def get_name_synonim(user_name):
        name = user_name.lower()
        name = name_synonim.transliterateAndCut(name)
        filename = 'Name_Synonim.txt'
        synonims = name_synonim.readSynonimFile(filename)
        name = list(name_synonim.findSynonimAndUpdateObject(name, synonims))
        name[0] = name[0].upper()
        name = "".join(name)
        name_synonim.writeBack(filename, synonims)

        return "".join(name)

    @staticmethod
    def get_pause(pause_range):
        pause_time_range = pause_range.split(',')
        pause = uniform(float(pause_time_range[0]), float(pause_time_range[1]))
        return float('{:.1f}'.format(pause))

    def send_message(self, input_field, message, click_button, user_id):
        input_field.clear()
        new_message = message.replace('\\n', '^')
        for letter in new_message:
            if letter == '^':
                input_field.send_keys(Keys.SHIFT, Keys.ENTER)
                continue
            input_field.send_keys(letter)
            symbol_pause = self.get_pause(self.pause_between_symbol)
            sleep(symbol_pause)
        self.click(click_button)
        pause = self.get_pause(self.pause_area)
        logging.info(f'Пользователю с ID [ {user_id} ] отправка: {message} [ пауза {pause} ]')
        sleep(pause)

    @staticmethod
    def get_list_messages_pauses(randomized_string):
        time_sleep_list = re.findall(r'\<(.*?)\>', randomized_string.replace(' ', ''))
        messages_list = re.split(r'\<.*?\>', randomized_string)

        messages_list = [message.strip() for message in messages_list]

        return time_sleep_list, messages_list

    def change_user_status(self, user, status):
        with open(self.list_name, 'r+') as file:
            content = file.read()
            file.seek(0)
            file.write(re.sub(fr'id{user}', f'id{user};{status}', content))

    def start_browser(self):
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument('--log-level=3')
        options.add_argument(fr'--user-data-dir={self.copy_profiles_dst}')
        if self.settings["path"]["chrome_profile_name"] == '':
            options.add_argument(f'--profile-directory=Default')
        else:
            options.add_argument(f'--profile-directory={self.settings["path"]["chrome_profile_name"]}')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.browser = webdriver.Chrome(service=service, options=options)
        self.browser.implicitly_wait(10)

    def main(self):
        self.copy_profile_directory()
        self.start_browser()
        users_id = self.get_users_id()
        try:
            for user_id in users_id:
                if user_id[-1].isalpha():
                    continue
                self.browser.get(f'{self.url}{user_id}')

                try:
                    user_information = self.browser.find_element(by=By.XPATH,
                                                                 value="//span[@class='im-page--title-main']").get_attribute(
                        'title')
                except Exception:
                    logging.error(f'Не удалось определить имя пользователя')
                    self.change_user_status(user_id, 'error')
                    continue

                past_user_name = user_information.split(' ')[0].strip()
                user_name = self.get_name_synonim(past_user_name)

                logging.info(f'Имя пользователя с ID [ {user_id} ] [ {past_user_name} / {user_name} ]')

                string = self.get_random_string().replace('*name*', user_name)
                try:
                    randomized_string = self.string_randomize(string)
                except Exception:
                    logging.error(f'Некорректный тип сообщения {string}')
                    self.change_user_status(user_id, 'error')
                    continue

                time_sleep_list, messages_list = self.get_list_messages_pauses(randomized_string)
                try:
                    input_field = self.browser.find_element(by=By.XPATH,
                                                            value="//div[contains(@class, 'im_editable')]")
                except Exception:
                    logging.error(f'Ошибка при отправке сообщения')
                    self.change_user_status(user_id, 'error')
                    continue
                click_button = self.browser.find_element(by=By.XPATH,
                                                         value="//button[contains(@class, 'im-chat-input--send')]")
                try:
                    for count_message, message in enumerate(messages_list):
                        if message.strip() == '':
                            continue

                        if count_message == len(messages_list) - 1:
                            self.send_message(input_field, message.strip(), click_button, user_id)

                            self.change_user_status(user_id, 'send')

                        else:
                            self.send_message(input_field, message.strip(), click_button, user_id)

                except Exception:
                    logging.error(f'Ошибка при отправке сообщения')
                    self.change_user_status(user_id, 'error')
                    continue

            logging.info('Работа программы завершена')

        except KeyboardInterrupt:
            logging.error('Работа программы прервана')
            sys.exit()

        except WebDriverException:
            logging.error('Работа программы прервана')
            sys.exit()


def get_list_dir(dir):
    dirname = dir
    dirfiles = os.listdir(dirname)
    list = []
    for file in dirfiles:
        if file.endswith('txt'):
            list.append(file)
    return list


def simple_gui():
    sg.theme('LightBrown11')

    list = get_list_dir('Абоненты-список')
    list2 = get_list_dir('Сообщения-список')

    layout = [
        [sg.Text('Выберите файл с пользователями в папке Абоненты-список')],
        [sg.Combo(values=list, size=15)],
        [sg.Text('Выберите файл с сообщениями в папке Сообщения-список')],
        [sg.Combo(values=list2, size=15)],
        [sg.Text('Выберите паузу между отправлениями сообщений\nразным анкетам')],
        [sg.InputText(default_text=3, size=3), sg.InputText(default_text=9, size=3)],
        [sg.Text('от     до     (в секундах)')],
        [sg.Submit(button_text='Разослать'), sg.Cancel(button_text='Выход')]
    ]
    window = sg.Window('Рассыльщик сообщений', layout)

    while True:
        event, values = window.read()
        if event == 'Разослать':
            if values[0] == '' or values[1] == '':
                logging.warning('Пожалуйста выберите все необходимые файлы')
            else:
                window.close()
                return values
        if event in (None, 'Выход', 'Cancel'):
            sys.exit()


def main():
    values = simple_gui()
    list_name = values[0]
    message_text_file = values[1]
    pause_area = values[2] + ',' + values[3]
    VKSendMessage(list_name=list_name,
                  message_text_file=message_text_file,
                  pause_area=pause_area).main()


if __name__ == '__main__':
    main()