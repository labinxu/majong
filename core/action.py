#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
@author LBX
copyright
"""

from enum import Enum
class ServerStatus(Enum):
    idle = 1
    ready = 2
    playing = 3
    over = 4

class Action:
    def __init__(self,server):
        self.server = server
        self.mahjongs = [x for x in range(1, 109)]

    def name(self, player, data):
        player.name = data

    def status(self, data):
        return data

    def ready(self, player):
        player.status = 'ready'
