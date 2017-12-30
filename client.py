# -*- coding: utf-8 -*-
import socket, sys
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
        self.id = -1
        self.logger = logging.getLogger('Client')
        self.action_queue = multiprocessing.Queue()
        self.mgr = Manager()
        self.cards = self.mgr.list()
        self.cards_for_show = []
        self.abandoned_cards = ["ABANDONED:"]

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
                self.id = act.id
                print('Player ID :%s' % act.id)
                msg = input('Ready:')
                while msg.lower() != 'y':
                    msg = input('Ready:')
                act.action_type = Action.ACT_READY
                next_action = self.send_action(act).get_next_action()
                if next_action.action_type == Action.ACT_ASSIGN:
                    for card in next_action.data.split(','):
                        self.cards.append(int(card))

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
                self.cards.sort()
                self.show_cards(self.cards)
                self.show_cards(self.cards_for_show)
                self.show_cards(self.abandoned_cards)
                self.play_card(action)

        except socket.error:
            print('close')
            self.sock.close()

    def insert_card(self, card):
        for i, c in enumerate(self.cards):
            pass
    def sort_cards(self, cards):
        wan_cards = []
        tong_cards = []
        tiao_cards = []
        for c in cards:
            if c <= 9:
                wan_cards.append(c)
            elif c <= 18:
                tong_cards.append(c)
            else:
                tiao_cards.append(c)
        wan_cards.sort()
        tong_cards.sort()
        tiao_cards.sort()
        result = wan_cards+tong_cards+tiao_cards
        return result

    def show_cards(self, cards):
        cardstring = [self.get_card_string(c) for c in cards]
        print(' '.join(cardstring))

    def valiable_action(self, act_data):
        if act_data >= Action.ACT_UNKNOWN:
            return False

        return act_data

    def parse_play_action(self, data):
        """
        """
        ret = Action()
        ret.id = self.id
        try:
            actives = data.split(' ')
            if len(actives) != 2:
                return
            act_str, card_str = actives
            active = self.valiable_action(int(act_str))
            if not active:
                return

            ret.action_type = int(act_str)
            ret.data = card_str
        except ValueError as e:
            self.logger.error(str(e))
            return None
        return ret

    def check_action(self, act):
        """
        """
        card = int(act.data)
        count = self.cards.count(card)
        actions = set()

        if act.action_type == Action.ACT_LOOK:
            if count > 1:
                # peng
                act.message = '%s|EAT-%s' % (self.get_card_string(card),
                                             Action.ACT_EAT)
                actions.add(Action.ACT_EAT)
            if count > 2:
                # gang
                act.message = '%s|EAT-%s|FOUR-%s' %(self.get_card_string(card),
                                                Action.ACT_EAT, Action.ACT_FOUR)
                actions.add(Action.ACT_FOUR)

        elif act.action_type == Action.ACT_GET:
            if count == 3:
                act.message = '%s|FOUR-%s' % (self.get_card_string(card),
                                              Action.ACT_FOUR)
                actions.add(Action.ACT_FOUR)

        if [c for c in self.cards if self.cards.count(c)==4]:
            act.message = '%s|FOUR-%s' % (self.get_card_string(card),
                                          Action.ACT_FOUR)
            actions.add(Action.ACT_FOUR)

        return act, actions

    def play_card(self, act):

        do_act = None
        play_card = None
        next_act, actions = self.check_action(act)
        while True:
            data = input("[%s]:" % next_act.message)
            try:
                do_act = self.parse_play_action(data)
                if not do_act:
                    continue
                break
            except ValueError as e:
                print(str(e))
                continue

        if act.action_type == Action.ACT_LOOK:
            if do_act.action_type == Action.ACT_EAT:
                self.eat_card(act, do_act)

            elif do_act.action_type == Action.ACT_PASS:
                do_act.data = act.data
                self.pass_card(do_act)

        elif act.action_type == Action.ACT_GET:
            if do_act.action_type == Action.ACT_ABANDON:
                if not self.abandon_card(act, do_act):
                    self.logger.error('%s not exists' % do_act.data)
                    return self.play_card(act)

            elif do_act.action_type == Action.ACT_FOUR:
                self.four_card(act, do_act)
            elif do_act.action_type == Action.ACT_WIN:
                self.logger.debug('WIN THE GAME')
                
        self.send_action(do_act)

    def four_card(self, p_act, c_act):
        """
        s_act: server action
        c_act: client action
        """
        card = int(c_act.data)
        p_card = int(p_act.data)
        self.cards.append(p_card)
        for i in range(0,4):
            self.cards.remove(card)
            self.cards_for_show.append(card)
        c_act.message = 'FOUR ACTION'

    def pass_card(self, act):
        """
        """
        pass

    def abandon_card(self, s_act, act):
        """
        """
        card = int(act.data)
        if card in self.cards:
            self.cards.append(int(s_act.data))
            self.cards.remove(card)
            act.message = 'ABANDON'
        else:
            if card != int(s_act.data):
                return False


        self.abandoned_cards.append(card)

        return True

    def eat_card(self, pre_act):
        card = int(pre_act.data)
        self.cards_for_show.append(card)
        # find another tmpcard in self.cards
        eat_cards = [c for c in self.cards if c== card][0:2]
        assert(len(eat_cards) == 2)
        map(lambda c:self.cards.remove(c), eat_cards)
        self.cards_for_show.extend(eat_cards)


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
