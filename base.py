#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
@author LBX
copyright
"""
from protos.action_pb2 import Action

class Base(object):
    def __init__(self):
        pass

    def act2string(self, act):
        s = 'ID :%s, ACT: %s, DIRECT:%s, MSG:%s, DATA:%s'%(act.id, act.action_type,act.direct, act.message, act.data)

        return s

    def _parse_action(self, action_data):
        """
        """
        act = Action.FromString(action_data)
        return act

    def get_card_string(self, card):
        try:
            card_c = card % 9

        except TypeError as e:
            return card

        card_c =  9 if card_c == 0 else card_c
        if card <= 9:
            return '%s万-%s' % (card_c, card)
        elif card <= 18:
            return '%s筒-%s' % (card_c, card)
        else:
            return '%s条-%s' % (card_c, card)




