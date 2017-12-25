# -*- coding: utf-8 -*-
import socket
import multiprocessing
import threading
import time
import logging
from protos.action_pb2 import Action
from base import Base
from multiprocessing import Manager

logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')

class Client(Base):
    def __init__(self, host='127.0.0.1', port=20000):
        super().__init__()
        self.host = host
        self.port = port
        self.logger = logging.getLogger('Client')
        self.action_queue = multiprocessing.Queue()
        self.mgr = Manager()
        self.cards = self.mgr.list()
        self.played_cards = []
        self.droped_cards = []

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        self.connect()

        p = multiprocessing.Process(target=self.loop)
        p.start()
        try:
            next_action = None
            act = self.get_next_action()
            assert(act != None)
            if act.action_type == Action.ACT_INIT:
                print('Player ID :%s' % act.id)
                msg = input('Ready:')
                while msg.lower() != 'y':
                    msg = input('Ready:')
                act.action_type = Action.ACT_READY
                next_action = self.send_action(act).get_next_action()
                if next_action.action_type == Action.ACT_ASSIGN:
                    for card in next_action.data.split(','):
                        self.cards.append(int(card))
                    self.cards.sort()

                    self.logger.debug('Assign done %s' % self.act2string(next_action))
                    next_action.action_type = Action.ACT_DONE
                    next_action.data = ''
                    next_action.message='Assign done'
                    self.send_action(next_action)
                else:
                    self.logger.error('Assign error')
                    return
            else:
                self.logger.error('Server send error action')
                return

            while True:
                action = self.get_next_action()
                self.play_card(action)

        except socket.error:
            print('close')
            self.sock.close()

    def play_card(self, act):
        print(' '.join([str(i) for i in self.cards]))
        if act.action_type == Action.ACT_POST:
            pass

        while True:
            data = input("%s@%s:" % (act.message, act.data))
            try:
                data = int(data)
                break
            except ValueError as e:
                continue

        if data:
            self.cards.append(int(act.data))
            self.cards.remove(data)
            # droped card
            self.droped_cards.append(data)

            act.data = str(data)
            
        self.send_action(act)
        #print(' '.join([str(i) for i in self.cards]))

    def send_action(self, action):
        """
        """
        action.direct = 1
        data = action.SerializeToString()
        self.logger.debug('Send: %s' % self.act2string(action))
        self.sock.sendall(data)
        return self

    def get_next_action(self):
        data = self.action_queue.get()
        act = self._parse_action(data)
        self.logger.debug('Received: %s' % self.act2string(act))
        return act

    def loop(self):
        self.logger.debug('playing the game')
        while True:
            # waiting active command
            msg = self.sock.recv(1024)
            if msg:
                self.action_queue.put(msg)

if __name__ == '__main__':

    Client().start()
