#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
@author LBX
copyright
"""



import time, sys
if '..' not in sys.path:
    sys.path.append('..')
from core import ServerStatus
from multiprocessing import Queue, Manager
from multiprocessing.managers import BaseManager
import logging
import threading

def init_logging(filename):
    pass
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='log.log',
                filemode='w')

class Player():
    """
    """
    def __init__(self):
        """
        """
        self.mahjongs = []
        self.server = '127.0.0.1'
        self.port = 8001
        self.player_number = 1
        self.user_id = None
        self.authkey = 'mahjong'.encode(encoding='ascii')
        self.round_player = False

    def regester_functions(self):
        BaseManager.register('get_player_id')
        BaseManager.register('get_status')
        BaseManager.register('get_turn_player')
        BaseManager.register('get_play_queue')
        BaseManager.register('set_current_card')
        BaseManager.register('get_current_card')
        BaseManager.register('get_new_card')

        for i in range(self.player_number):
            BaseManager.register('get_player_queue%s' % i)

    def connect(self):
        """
        """
        logging.info('Connecting to server %s' % self.server)
        self.regester_functions()
        manager = BaseManager(address=(self.server, self.port), authkey=self.authkey)
        manager.connect()
        self.play_queue = manager.get_play_queue()

        return manager

    def start(self):
        """
        """
        if not self.user_id:
            manager = self.connect()
            self.manager = manager

            ids = manager.get_player_id()
            if ids.empty():
                logging.error('The player is enught...')
                return
            self.user_id = ids.get(timeout=2)

        #init_logging('player%s.log' % self.id)
        logging.info('Player id %s' % self.user_id)

        ### init the mahjong list
        while True:
            status = manager.get_status()
            if status.lower() == 'assign':
                self.player_queue = eval('manager.get_player_queue%s()'%self.user_id)
                while not self.player_queue.empty():
                    mahjong = self.player_queue.get()
                    self.mahjongs.append(mahjong)
                self.debug(self.mahjongs)

            elif status.lower() == 'start':
                t = threading.Thread(target=self.play)
                t.start()
                t.join()

            time.sleep(1)

    def get_new_card(self):
        card = self.manager.get_new_card()
        print('new card %s' % card)

    def play_card(self):

        pass
    def check_usable(self, card):
        pass

    def play(self):
        """
        playing the game
        """
        # the the round master id
        while True:
            turn_player = self.manager.get_turn_player()
            self.debug('Round player is %s' % turn_player)
            if turn_player.lower() != str(self.user_id):
                time.sleep(1)
                continue
            status = self.manager.get_status().lower()

            if status == 'get':
                self.get_new_card()

            elif status == 'play':
                # send card
                pass
            elif status == 'usable':
                # eat card
                pass
            else:
                pass
            # # check the curent card is usable
            # usable = False
            # card = self.manager.get_current_card()
            # # the first player
            # if card.lower() == 'none':
            #     # get a new card
            #     pass
            # else:
            #     # check the usable
            #     pass

            # self.debug('current card %s' % card)
            # if usable:
            #     # put the card to cards list
            #     self.mahjongs.append(int(card.lower()))
            #     self.manager.set_status('wait')
            # else:
            #     # get the new card
                
            # # play card
            # self.manager.set_current_card(str(self.mahjongs[1]))

            # waiting

            time.sleep(1)

    def info(self, message):
        msg ='player %s: %s' % (self.user_id, message)
        logging.info(msg)
        print(msg)

    def debug(self, message):
        msg ='player %s: %s' % (self.user_id, message)
        logging.debug(msg)
        print(msg)

if __name__=='__main__':
    p = Player()
    p.start()
