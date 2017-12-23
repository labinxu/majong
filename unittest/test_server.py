#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
@author LBX
copyright
"""
import sys
if '..' not in sys.path:
    sys.path.append('..')
import unittest
from server.server import Server


class Stub_Server(unittest.TestCase):
    def test_assign（self):
        
if __name__=='__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(Stub_Server)
    unittest.TextTestRunner(verbosity=2).run(suite)
