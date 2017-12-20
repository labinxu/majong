#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
@author LBX
copyright
"""
import requests
import json

def main():
    url = 'http://localhost:4000/jsonrpc'
    headers = {'content-type': 'application/json'}

    payload={
        'method':'echo',
        'params':"echome!",
        'jsonrpc':'2.0',
        'id:':0
    }

    response = requests.post(url, data=json.dumps(payload),headers=headers).json()
    print(response['result'])
main()
