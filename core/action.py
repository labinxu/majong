#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
@author LBX
copyright
"""

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
