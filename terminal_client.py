#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
@author LBX
copyright
"""

import logging
import time
from transitions import Machine, State
import socket

logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s: %(message)s')


class Client(object):
    states = ['init0','init', 'ready', 'run']

    def __init__(self, host='127.0.0.1', port=20000):
        self.host = host
        self.port = port
        self.id = -1
        self.logger = logging.getLogger('XClient')
        self.machine = Machine(model=self, states=Client.states,
                               initial='init0')

        ## transitions
        self.machine.add_transition(trigger='Init', source='init0',
                                    dest='init')

        self.machine.add_transition(trigger='Ready',
                                    source='init', dest='ready')

        self.machine.add_transition(trigger='Run',
                                    source='ready', dest='run')

        self.machine.on_enter_init(self.init)
        self.machine.on_enter_ready(self.ready)
        self.machine.on_enter_run(self.run)

    def init(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

        self.sock.setsockopt(socket.SOL_SOCKET,
                             socket.SO_REUSEADDR,
                             1)
        self.trigger('Ready')

    def ready(self):
        self.logger.debug('CONNECTING...')
        i = 0
        while i < 5:
            self.logger.debug('Ready...')
            time.sleep(1)
            i += 1
        self.Run()

    def event_loop(self):
        """
        received the message from server
        """

    def run(self):
        i = 0
        while i < 10:
            self.logger.debug('RUNNING...')
            i += 1
            time.sleep(1)
        self.Ready()
