#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
@author LBX
copyright
"""

from player import Player
import logging
import socket
import multiprocessing
import threading
import time
import signal
from random import shuffle
from multiprocessing import Manager
from protos.action_pb2 import Action
from base import Base

logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')
class XServer(object):
    def __init__(self, ip, port, player_number):
        # define four players
        mgr = Manager()
        self.ip = ip
        self.port = port
        self.player_number = player_number
        self.index_player = -1

        self.players = []#mgr.list()
        self.status = None
        self.card_count = 13
        self.logger = logging.getLogger('XServer')

        self.next_step = threading.Event()

        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)
        self.card_utils = Base()
        #self.initcards()

    def initcards(self):
        self.cards = [i for i in range(1, 27)]*4
        shuffle(self.cards)

    def exit(self):
        self.logger.debug('Close server socket')
        self.sock.close()

    def is_ready(self, e, players):
        self.logger.debug('checking players status')
        while True:
            if len(players) != self.player_number:
                time.sleep(1)
                continue
            r = [p for p in players if not p.is_ready()]
            if not r:
                e.set()
                break
            time.sleep(1)

    def get_next_player(self, index_player):
        i = index_player + 1
        if i >= self.player_number:
            i = i % self.player_number

        # player and index
        return self.players[i], i

    def parser_action(self, action):
        # set the player id to unknown
        action.id = -1

        if action.action_type == Action.ACT_POST:
            # send the card to next player
            pass

        elif action.action_type == Action.ACT_PASS:
            pass

        elif action.action_type == Action.ACT_EAT:
            pass

        elif action.action_type == Action.ACT_FOUR:
             # 杠
            #current_card = self.cards[card_index]
            pass
        elif action.action_type == Action.ACT_WIN:
            pass
        return action

    def _playing(self, e, players):
        self.logger.info('Waiting players')
        e.wait()
        self.logger.debug('Game is beging...')
        # assign card
        act = Action()
        act.action_type = Action.ACT_ASSIGN
        for i, player in enumerate(players):
            act.id = player.id
            act.message = 'assigned card'
            beg = i * self.card_count
            end = (i+1) * self.card_count
            tmpcards = [str(j) for j in self.cards[beg:end] ]
            act.data = ','.join(tmpcards)
            self.logger.debug(act.data)
            player.send_action(act)
            if player.get_next_action().action_type != Action.ACT_DONE:
                self.logger.error('ASSIGN CARD FAILED')
                return

        # assign done
        current_index_card = self.player_number*self.card_count
        self.cards = self.cards[current_index_card:]
        self.cards.reverse()

        current_card = ''
        self.drop_cards = []
        player_index = -1
        # index play
        while True:
            active_player, player_index = self.get_next_player(player_index)
            #post a card to first player
            act = Action()
            act.id = active_player.id
            act.action_type = Action.ACT_GET
            tmpcard = self.cards.pop()
            current_card = str(tmpcard)
            act.message = 'GET@%s' % self.card_utils.get_card_string(tmpcard)
            act.data = current_card
            active_player.send_action(act)

            # waiting for next action
            act = active_player.get_next_action()
            self.logger.debug(active_player.act2string(act))
            act = self.parser_action(act)
            if act.action_type == Action.ACT_WIN:
                self.win_game(active_player, player_index)
                break

            round_index = player_index
            # round play
            while True:
                next_player, round_index = self.get_next_player(round_index)
                if round_index == player_index:
                    # next round
                    self.drop_cards.append(int(act.data))
                    break
                act.id = next_player.id
                act.action_type = Action.ACT_LOOK
                act.message = 'LOOK@%s' % self.card_utils.get_card_string(tmpcard)
                next_player.send_action(act)
                act =next_player.get_next_action()
                continue

    def win_game(self, active_player, player_index, card):
        #active_player.win()
        round_index = player_index
        while True:
            next_player, round_index = self.get_next_player(round_index)
            if round_index == player_index:
                # next round
                break
            act = Action()
            act.id = next_player.id
            act.dest_player = active_player.id
            act.action_type = Action.ACT_WIN
            card_string = self.card_utils.get_card_string(card)
            act.message = 'WIN@%s' % card_string
            next_player.send_action(act)
        self.restart()

    def check_players_status(self):
        self.logger.debug('checking players status')
        while True:
            if len(self.players) != self.player_number:
                time.sleep(1)
                continue
            r = [p for p in self.players if not p.is_ready()]
            if not r:
                break
            time.sleep(1)

    def init_players(self):
        """
        """
        for player in self.players:
            action = Action()
            action.id = player.id
            #init
            action.action_type = Action.ACT_INIT
            action.message = 'Init...'
            player.send_action(action)
            player.start()

        t = threading.Thread(target=self.check_players_status)
        t.start()
        t.join()

    def restart(self):
        """
        """
        self.init_players()
        if not self.assign_card():
            return
        self.run()

    def start(self):
        self.next_step.clear()
        t = threading.Thread(target=self.listenling)
        t.start()
        self.next_step.wait()
        self.next_step.clear()
        self.init_players()
        if not self.assign_card():
            return
        self.run()

    def assign_card(self):
        """
        assign the cards
        """
        self.initcards()
        act = Action()
        act.action_type = Action.ACT_ASSIGN
        for i, player in enumerate(self.players):
            act.id = player.id
            act.message = 'Assigning card'
            beg = i * self.card_count
            end = (i+1) * self.card_count
            tmpcards = [str(j) for j in self.cards[beg:end] ]
            act.data = ','.join(tmpcards)
            self.logger.debug(act.data)
            player.send_action(act)
            next_action = player.get_next_action()
            if next_action.action_type != Action.ACT_DONE:
                self.logger.error('ASSIGN CARD FAILED')
                return False

        return True

    def run(self):
        # assign done
        self.logger.debug('Running...')
        current_index_card = self.player_number*self.card_count
        self.cards = self.cards[current_index_card:]
        self.cards.reverse()

        current_card = ''
        self.drop_cards = []
        player_index = -1

        # index play
        while True:
            active_player, player_index = self.get_next_player(player_index)
            #post a card to first player
            act = Action()
            act.id = active_player.id
            act.action_type = Action.ACT_GET
            tmpcard = self.cards.pop()
            current_card = str(tmpcard)
            act.message = 'GET@%s' % self.card_utils.get_card_string(tmpcard)
            act.data = current_card
            active_player.send_action(act)

            # waiting for next action
            act = active_player.get_next_action()
            self.logger.debug(active_player.act2string(act))
            act = self.parser_action(act)
            if act.action_type == Action.ACT_WIN:
                print('Act WIN...')
                self.win_game(active_player, player_index, tmpcard)
                break

            round_index = player_index
            # round play
            while True:
                next_player, round_index = self.get_next_player(round_index)
                if round_index == player_index:
                    # next round
                    self.drop_cards.append(int(act.data))
                    break
                act.id = next_player.id
                act.action_type = Action.ACT_LOOK
                act.message = 'LOOK@%s' % self.card_utils.get_card_string(tmpcard)
                next_player.send_action(act)
                act =next_player.get_next_action()
                continue

    def listenling(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
        sock.bind((self.ip, self.port))
        sock.listen(self.player_number)
        self.sock = sock
        self.logger.info('starting the server %s %s' % (self.ip, self.port))
        i = 1
        while True:
            s, addr = sock.accept()
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            player = Player(s, addr, i, self)
            self.players.append(player)
            i += 1
            if self.player_number == len(self.players):
                self.next_step.set()

def command_line():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--ip' ,default='127.0.0.1',
                        help='Linstening to ip address')
    parser.add_argument('-p', '--port',default='20000', type=int, help='port')
    parser.add_argument('-P', '--players',default=1, type=int, help='Player number')
    return parser.parse_args()

if __name__=="__main__":
    args = command_line()
    print(args.ip, args.port)
    xserver = XServer(args.ip, args.port, args.players)
    signal.signal(signal.SIGINT, xserver.exit)
    signal.signal(signal.SIGTERM, xserver.exit)
    xserver.start()
