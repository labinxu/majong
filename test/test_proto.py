#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
@author LBX
copyright
"""
import sys
if '..' not in sys.path:
    sys.path.append('..')
from protos import action_pb2

def test_proto(self):

    action = action_pb2.Action()
    action.id = 1
    action.direct = 1
    action.action_type = 2
    action.message = 'default'

    message = action.SerializeToString()
    
