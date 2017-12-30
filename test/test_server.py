import sys
if '..' not in sys.path:
    sys.path.append('..')
import socket
from xserver import XServer
from player import Player
from protos.action_pb2 import Action

class Test_server(XServer):
    def __init__(self, host,ip,players):
        # define four players
        super().__init__(host, ip, players)

    def initcards(self):
        """
        """
        self.cards = [1 ,1 ,1 ,2 ,2 ,3 ,3 ,4 ,4 ,4 ,5 ,7 ,6,
                      1 ,7 ,2 ,3 ,9, 5, 6, 7, 8, 9,7,3]

    def __listenling(self):
        """
        """
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

if __name__=="__main__":
    xserver = Test_server('127.0.0.1', 20000, 1)
    xserver.start()

