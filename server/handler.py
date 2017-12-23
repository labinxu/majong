#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
@author LBX
copyright
"""

import socketserver
class ServerHandler(socketserver.BaseRequestHandler):
    """
    inherit from baserequesthandler
    """
    # def __init__(self, request, client_address, server):
    #     super().__init__(request, client_address, server)
    #
    def setup(self):
        print('New player %s', self.client_address)
        self.server.add_player(self.client_address, self.request)

    def handle(self):
        self.server.player(self.client_address).run()
        # while True:
        #     # get action
        #     accept_data = str(conn.recv(1024), encoding='utf8')
        #     print(accept_data)
        #     conn.sendall(bytes(accept_data, encoding='utf8'))
        #     print("send %s"% accept_data)
        #     #self.do(accept_data)
        # conn.close()
