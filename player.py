import logging
import multiprocessing
import time
from base import Base
from protos.action_pb2 import Action
logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s')


class Player(Base):
    def __init__(self, sock, addr, id, serv):
        super().__init__()

        self.sock = sock
        self.address = addr
        self.serv = serv
        self.id = id
        self.logger = logging.getLogger('Player')
        self.playerinfo = multiprocessing.Manager().Namespace()
        self.playerinfo.status=False
        self.active_queue = multiprocessing.Queue()

    def start(self):
        p = multiprocessing.Process(target=self.do_start)
        p.start()

    def is_ready(self):
        return self.playerinfo.status

    def send_action(self, action):
        """
        """
        action.direct = 0
        self.logger.debug('Send %s' % self.act2string(action))
        self.sock.sendall(action.SerializeToString())

    def do_start(self):
        p = multiprocessing.Process(target=self.playing,
                                    args=(self.sock, logging.getLogger('Player')))
        p.start()
        while True:
            act = self.get_next_action()
            if act.action_type == Action.ACT_READY:
                self.playerinfo.status = True
                break
            time.sleep(1)

    def new_card(self, newcard):
        """
        """
        self.sock.sendall(newcard.encode('ascii'))

    def get_next_action(self):
        act = self._parse_action(self.active_queue.get())
        self.logger.debug('geted :%s' % self.act2string(act))
        return act

    def playing(self, sock, logger):
        logger.debug('%s %s playing...' % self.address)
        while True:
            data = sock.recv(1024)
            if data:
                self.active_queue.put(data)
            time.sleep(1)


