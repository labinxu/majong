# -*- coding: utf-8 -*-
import socket
import multiprocessing
import threading
import time
import logging

logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s')

class Client(object):
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 20000
        self.logger = logging.getLogger('Client')
        self.action_queue = multiprocessing.Queue()

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            playing = False
            while True:
                msg = input('Enter Action:')
                sock.sendall(msg.encode('ascii'))

                if not playing:
                    p = multiprocessing.Process(target=self.playing,
                                                args=(sock, self.logger))
                    p.start()

                    do_active = multiprocessing.Process(target=self.do_active)
                    do_active.start()

                    playing = True
                time.sleep(1)

        except socket.error:
            print('close')
            sock.close()

    def _parse_action(self, action_data):
        """
        """
        pass

    def do_active(self):
        """
        get the action data from server
        """

        while True:
            active = self.action_queue.get()
            if active:
                self.logger.debug("Received :%s" % active)

            time.sleep(1)

    def playing(self, sock, logger):
        print('playing')
        while True:
            # waiting active command
            msg = sock.recv(1024)
            if msg:
                self.action_queue.put(msg)
            time.sleep(1)

if __name__ == '__main__':

    Client().start()
