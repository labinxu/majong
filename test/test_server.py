from player import Player
import logging
import socket
import multiprocessing
import threading
import time
import signal
from multiprocessing import Manager


logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s')
class XServer(object):
    def __init__(self):
        # define four players
        mgr = Manager()
        self.player_number = 1
        self.players = []#mgr.list()
        self.status = None
        self.logger = logging.getLogger('XServer')
        self.eready = multiprocessing.Event()
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)

    def exit(self):
        self.logger.debug('Close server socket')
        self.sock.close()

    def is_ready(self, e, players):
        self.logger.debug('checking players status')
        while True:
            if len(players) != self.player_number:
                time.sleep(1)
                continue
            self.logger.debug('checking')
            r = [p for p in players if not p.is_ready()]
            if not r:
                e.set()
                break
            time.sleep(1)

    def playing(self, e, players):
        self.logger.info('Waiting players')
        e.wait()
        self.logger.debug('Game is beging...')
        active_player = players[0]
        while True:
            time.sleep(1)
            active = active_player.get_active()
            active_player.send(active)
            #self.logger.debug('Game is continue...')

    def start(self):
        # waiting for every one ready
        threading.Thread(target=self.is_ready, args=(self.eready, self.players,)).start()
        threading.Thread(target=self.playing, args=(self.eready, self.players,)).start()
        threading.Thread(target=self.listenling).start()

    def listenling(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0.1', 20000))
        sock.listen(self.player_number)
        self.sock = sock
        self.logger.info('starting the server')
        i = 1
        while True:
            s, addr = sock.accept()
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            player = Player(s, addr, i, self)
            self.players.append(player)
            player.start()
            i += 1

if __name__=="__main__":
    xserver = XServer()

    xserver.start()
