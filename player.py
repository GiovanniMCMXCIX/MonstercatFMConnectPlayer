#!/usr/bin/python3
# -*- coding: utf-8 -*-
from multiprocessing import Process
import requests
import getpass
import socket
import json
import sys
import os
import re

try:
    import connect
except:
    raise ImportError("Module connect is missing please run 'python3 -m pip install -U connect.py'")

try:
    import pygame
except:
    raise ImportError("Module connect is missing please run 'python3 -m pip install -U pygame'")

DATA_PATH = os.path.dirname(os.path.abspath(__file__)) + "/data/"
DOWNLOAD_PATH = DATA_PATH + "downloads/"
CONFIG_PATH = DATA_PATH + "config.json"
substring = ":monstercat!monstercat@monstercat.tmi.twitch.tv PRIVMSG #monstercat :Now Playing:"
# substring = ":giovani1906!giovani1906@giovani1906.tmi.twitch.tv PRIVMSG #giovani1906 :Now Playing:"  # debug stuff


def header():
    print("    __  ___                 __                       __     ________  ___   ____  __                     \n"
          "   /  |/  /___  ____  _____/ /____  ______________ _/ /_   / ____/  |/  /  / __ \/ /___ ___  _____  _____\n"
          "  / /|_/ / __ \/ __ \/ ___/ __/ _ \/ ___/ ___/ __ `/ __/  / /_  / /|_/ /  / /_/ / / __ `/ / / / _ \/ ___/\n"
          " / /  / / /_/ / / / (__  ) /_/  __/ /  / /__/ /_/ / /_   / __/ / /  / /  / ____/ / /_/ / /_/ /  __/ /    \n"
          "/_/  /_/\____/_/ /_/____/\__/\___/_/   \___/\__,_/\__/  /_/   /_/  /_/  /_/   /_/\__,_/\__, /\___/_/     \n"
          "                                                                                      /____/           \n\n"
          "Created by GiovanniMCMXCIX                                                       [http://gio.mcmxcix.xyz]\n"
          "Source available on GitHub                        [https://github.com/GiovanniMCMXCIX/MonstercatFMPlayer]\n"
          "/////////////////////////////////////////////////////////////////////////////////////////////////////////\n")


def below_line():
    print("Songs that are playing will appear below.\n"
          "=========================================================================================================")


class Main:
    def __init__(self, sock):
        header()
        self.create_directories()
        self.login(sock)
        self.read_buffer = None

    @staticmethod
    def check_login_status(data):
        if re.match(r'^:tmi\.twitch\.tv NOTICE \* :Login authentication failed\r\n$', data):
            return False
        else:
            return True

    @staticmethod
    def send_irc(data, sock):
        sock.send(data.encode('utf-8'))

    def connect(self, nick, password, sock):
        host = "irc.twitch.tv"

        sock.settimeout(10)
        print("Connecting...\n")
        try:
            sock.connect((host, 6667))
        except:
            print('Connection failed.\n')
            sys.exit()
        print('Connected!\n')
        sock.settimeout(None)

        print('Logging in...\n')
        self.send_irc("PASS {}\r\n".format(password), sock)
        self.send_irc("NICK {}\r\n".format(nick), sock)
        self.send_irc("USER {} {} bla :{}\r\n".format(nick, host, nick), sock)

        if self.check_login_status(sock.recv(1024).decode("utf-8")):
            print('Login successful!\n')
        else:
            print('Login unsuccessful. (hint: make sure your oauth token is valid).\n')
            sys.exit(1)

    def login(self, sock):
        if not os.path.isfile(CONFIG_PATH):
            print("Config does not exist. Creating.")

            username = input("Enter your username: ")

            print('Right click and paste your oauth key beginning with "oath:"')
            password = getpass.getpass('(text hidden):')

            data = {'username': username, 'password': password}

            with open(CONFIG_PATH, 'w+') as config_file:
                json.dump(data, config_file)
                print('Config file was created successfully!')

            self.connect(username, password, sock)
            below_line()
            Process(target=self.play(sock)).start()
        elif os.path.isfile(CONFIG_PATH):
            with open(CONFIG_PATH) as config_file:
                config = json.load(config_file)

            self.connect(config['username'], config['password'], sock)
            below_line()
            Process(target=self.play(sock)).start()

    @staticmethod
    def create_directories():
        os.makedirs(DATA_PATH, exist_ok=True)
        os.makedirs(DOWNLOAD_PATH, exist_ok=True)

    @staticmethod
    def download(url, path):
        r = requests.Session().get(url, stream=True)

        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return True

    @staticmethod
    def _play(path):
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play()

    def play(self, sock):
        self.send_irc("JOIN {}\r\n".format('#monstercat'), sock)
        # self.send_irc("JOIN {}\r\n".format('#giovani1906'), sock)  # debug stuff
        init = 1
        song, artist, now_playing = "", "", ""
        current_song = now_playing
        while True:
            self.read_buffer = sock.recv(1024).decode("utf-8")

            if self.read_buffer.find('PING') != -1:
                self.send_irc('PONG ' + self.read_buffer.split()[1] + '\r\n', sock)

            if self.read_buffer.find(substring) != -1:
                results_1 = re.search("Now Playing: (.*) by (.*) - Listen", self.read_buffer)
                if results_1:
                    song, artist = results_1.groups()
                else:
                    results_2 = re.search("Now Playing: (.*) by (.*)\r\n", self.read_buffer)
                    if results_2:
                        song, artist = results_2.groups()
                    else:
                        print("\nError, can't get artist and song title in the line:\n{}\n".format(self.read_buffer))

                now_playing = "Now Playing: {} - {}".format(artist, song)

                if init or current_song != now_playing:
                    init = 0

                    track = connect.Client().search_track_advanced(song, artist)
                    if not track:
                        print("No track found.")
                        print("The track that was not found is: {} - {}".format(artist, song))
                        current_song = now_playing
                    else:
                        file_name = '{} - {}'.format(track[0].artists, track[0].title)
                        path = DOWNLOAD_PATH + file_name + ".mp3"

                        print("Now Playing: {}".format(file_name))

                        if os.path.isfile(path):
                            self._play(path)
                        else:
                            self.download(list(track[0].albums)[0].stream_url, path)
                            self._play(path)

                        current_song = now_playing


if __name__ == '__main__':
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        Main(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    except KeyboardInterrupt:
        pygame.mixer.music.stop()
        print("\nUser stopped script")
