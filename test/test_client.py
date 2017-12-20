# -*- coding: utf-8 -*-
import socket
import multiprocessing
import time
import logging

logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s')

class Client(object):
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 20000
        self.logger = logging.getLogger('Client')

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            playing = False
            while True:
                msg = input('Enter Step:\n')
                sock.sendall(msg.encode('ascii'))
                if not playing:
                    p = multiprocessing.Process(target=self.playing,
                                                args=(sock, self.logger))
                    p.start()
                    playing = True
                time.sleep(1)

        except socket.error:
            print('close')
            sock.close()

    def playing(self, sock, logger):
        print('playing')
        while True:
            msg = sock.recv(1024)
            if msg:
                logger.debug('Received %s' %msg)
            time.sleep(1)

if __name__ == '__main__':

    Client().start()
