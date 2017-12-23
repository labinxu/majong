from player import Player
import logging
import socket
import multiprocessing
import threading
import time
import signal
from multiprocessing import Manager
from protos.action_pb2 import Action

logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s')
class XServer(object):
    def __init__(self):
        # define four players
        mgr = Manager()
        self.player_number = 1
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
            tmpcards = [str(i) for i in self.cards[beg:end] ]
            act.data = ','.join(tmpcards)
            self.logger.debug(act.data)
            player.send_action(act)

        self.cards = self.cards[self.player_number*self.card_count:]
        # assign done

        active_player = players[0]
        act = Action()
        while True:
            time.sleep(1)
            #play
            act.id = active_player.id
            act.action_type = Action.ACT_POST
            act.message = 'POST CARD'
            active_player.send_action(act)
            next_act = active_player.get_next_action()

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
        sock.bind(('127.0.0.1', 20000))
        sock.listen(self.player_number)
        self.sock = sock
        self.logger.info('starting the server')
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

if __name__=="__main__":
    xserver = XServer()

    xserver.start()
