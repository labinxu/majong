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




