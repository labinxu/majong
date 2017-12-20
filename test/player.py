import logging
import multiprocessing
import time
logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s')


class Player(object):
    def __init__(self, sock, addr, id, serv):
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
        print(self.playerinfo.status)
        #self.logger.debug('%s %s checking ready' % self.address)
        return self.playerinfo.status
    def send(self, activemsg):
        """
        """
        self.logger.debug('Send %s' % activemsg)
        self.sock.sendall(activemsg)

    def do_start(self):
        while True:
            data = self.sock.recv(1024)
            if data and data=='ready'.encode('ascii'):
                #self.logger.debug('player %s %s is ready' % self.address
                print('set status to True')
                self.playerinfo.status = True
                break
            time.sleep(1)

        p = multiprocessing.Process(target=self.playing,
                                    args=(self.sock, logging.getLogger('Player')))
        p.start()
        p.join()

    def new_card(self, newcard):
        """
        """
        self.sock.sendall(newcard.encode('ascii'))

    def get_active(self):
        return self.active_queue.get()

    def playing(self, sock, logger):
        logger.debug('%s %s playing...' % self.address)
        while True:
            data = sock.recv(1024)
            if data:
                #self.logger.debug(data)
                logger.debug('%s %s: %s...' % (self.address[0],
                                                         self.address[1],
                                                         data))
                self.active_queue.put(data)

            #time.sleep(1)
            #sock.sendall(data)


