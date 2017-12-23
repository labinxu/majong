#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
@author LBX
copyright
"""
import random
import time
import multiprocessing
from multiprocessing import Queue, Manager
from multiprocessing.managers import BaseManager
import logging
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='server.log',
                filemode='w')


class MahjongServer():
    def __init__(self):
        self.__init_member_data()

    def __init_member_data(self):
        self.address = '127.0.0.1'
        self.port = 8001
        self.authkey = 'mahjong'.encode(encoding='ascii')
        self.player_queues = []
        self.message_q = Queue()
        self.player_ids = Queue()
        self.play_queue = []
        self.player_number = 1

        ## manager values
        self.status = 'idle'
        self.current_card = 'None'

        ## the first player for turn
        self.turn_player = None

        self.mahjongs = []
        self.plaied_cards = []
        self.__init_player_ids()

    def __init_player_ids(self):
        for i in range(0, self.player_number):
            self.player_queues.append(Queue())
            self.player_ids.put(i)

    def shuffle_cards(self):
        """
        shuffle the mahjong
        """
        self.mahjongs = [i for i in range(1, 108)]
        #random.shuffle(self.mahjongs)
        return self.mahjongs

    def set_status(self, sat):
        self.status = sat

    def assign_card(self, pid):
        """
        assign card to player
        """
        assert(pid < self.player_number)
        self.shuffle_cards()

        player_queue = eval('self.manager.get_player_queue%s()' % pid)
        cards = self.mahjongs[0:13]
        for card in cards:
            print('assign %s' % card)
            player_queue.put(card)

        logging.debug('player %s cards: %s' % (str(pid), str(cards)))
        # remove the assigned cards
        self.mahjongs = self.mahjongs[12:]
        time.sleep(1)
        while True:
            if not player_queue.empty():
                print('Waiting player %s get cards...' % str(pid))
            else:
                logging.debug('player %s assigned' % str(pid))
                break
            time.sleep(1)

    def set_turn_player(self, turn_player):
        self.turn_player = turn_player
        print('Round player %s' % turn_player)

    def get_new_card(self):
        card = self.mahjongs[0]
        self.mahjongs = self.mahjongs[1:]
        self.manager.set_status('play')
        return card

    def set_current_card(self, card):
        self.current_card = card

    def register_functions(self):
        BaseManager.register('get_new_card',
                             callable=self.get_new_card)
        BaseManager.register('get_turn_player',
                             callable=lambda:self.turn_player)

        BaseManager.register('set_turn_player',
                             callable=self.set_turn_player)

        BaseManager.register('get_current_card',
                             callable=lambda:self.current_card)

        BaseManager.register('set_current_card',
                             callable=self.set_current_card)

        ####
        BaseManager.register('get_message_queue', callable=lambda:self.message_q)
        BaseManager.register('get_player_id', callable=lambda:self.player_ids)
        BaseManager.register('get_play_queue', callable=lambda:self.play_queue)

        ## player queue
        for i in range(self.player_number):
            BaseManager.register('get_player_queue%s' % i,
                                 callable=lambda:self.player_queues[i])

        BaseManager.register('get_status', callable=lambda: self.status)
        BaseManager.register('set_status', callable=self.set_status)

    def start(self):
        """
        start the server
        """
        logging.info('starting the server...')
        self.register_functions()
        self.manager = BaseManager(address=(self.address, self.port),
                                   authkey=self.authkey)
        self.manager.start()
        self.player_ids = self.manager.get_player_id()
        self.status = self.manager.get_status()

        while True:
            if self.player_ids.empty():
                logging.info('Starting game...')
                self.play()
                break
            else:
                print('waiting...')
            time.sleep(1)

        return self.manager

    def play(self):
        # send the mahjong
        logging.info('Assign cards')
        turn_player = 0 # random.randint(0, 3)
        self.manager.set_turn_player(str(turn_player))

        self.manager.set_status('assign')
        for i in range(self.player_number):
            self.assign_card(i)
        
        self.manager.set_status('start')
        time.sleep(1)
        precard = 'None'
        while True:




            self.manager.set_status('get')
            # waiting player
            time.sleep(1)
            card = self.manager.get_current_card()
            while not card and precard == card.lower():
                print('waiting player %s' % self.manager.get_turn_player())
                time.sleep(1)
                continue
            time.sleep(1)

    def play_mahjong():
        while True:
            pass

def main():
    server = MahjongServer()
    server.start()

if __name__ == '__main__':
    main()

