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

logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')
class XServer(object):
    def __init__(self, ip, port, player_number):
        # define four players
        mgr = Manager()
        self.ip = ip
        self.port = port
        self.player_number = player_number

        self.players = []#mgr.list()
        self.status = None
        self.card_count = 13
        self.logger = logging.getLogger('XServer')
        self.eready = multiprocessing.Event()
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)
        self.initcards()

    def initcards(self):
        self.cards = [i for i in range(1, 109)]
        shuffle(self.cards)
        self.index_player = -1

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
            current_card = self.cards[card_index]

        elif action.action_type == Action.ACT_WIN:
            pass
        return action

    def playing(self, e, players):
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

        while True:
            active_player, player_index = self.get_next_player(player_index)
            #post a card to first player
            act = Action()
            act.id = active_player.id
            act.action_type = Action.ACT_POST
            act.message = 'POST'
            current_card = str(self.cards.pop())
            act.data = current_card
            active_player.send_action(act)

            # waiting for next action
            act = active_player.get_next_action()
            self.logger.debug(active_player.act2string(act))
            act = self.parser_action(act)
            if act.action_type == Action.ACT_WIN:
                break

            round_index = player_index
            # round play
            while True:
                next_player, round_index = self.get_next_player(round_index)
                #print('player index %s, round index %s' % (player_index, round_index))
                if round_index == player_index:
                    # next round
                    self.drop_cards.append(int(act.data))
                    break

                act.id = next_player.id
                act.action_type = Action.ACT_POST
                act.message = 'POST'
                next_player.send_action(act)
                act =next_player.get_next_action()
                # default pass
                continue
                # if act.action_type == Action.ACT_PASS:
                #     continue
                # elif act.action_type == Action.ACT_EAT:
                #     player_index = round_index
                #     break

    def start(self):
        # waiting for every one ready
        threading.Thread(target=self.is_ready,
                         args=(self.eready, self.players,)).start()
        threading.Thread(target=self.playing,
                         args=(self.eready, self.players,)).start()

        threading.Thread(target=self.listenling).start()

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

            action = Action()
            action.id = i
            action.direct = 0
            #init
            action.action_type = Action.ACT_INIT
            action.message = 'init player'
            player.send_action(action)
            self.players.append(player)
            player.start()
            i += 1

def command_line():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--ip' ,default='127.0.0.1',
                        help='Linstening to ip address')
    parser.add_argument('-p', '--port',default='20000', type=int, help='port')
    parser.add_argument('-P', '--players',default=2, type=int, help='Player number')
    return parser.parse_args()

if __name__=="__main__":
    args = command_line()
    print(args.ip, args.port)
    xserver = XServer(args.ip, args.port, args.players)
    xserver.start()
