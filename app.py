import requests
import json
from flask import Flask, render_template, request, redirect, jsonify
import os
import math
import pygeohash as pgh
import numpy as np
import time
from multiprocessing import Pool, Queue
import multiprocessing
import socketio
from xmpp_client import *
import socket_server
from gdr_bot import GdrBot
from waitress import serve
from pathlib import Path


def start_sio_client(q_xmpp, q_send):
    sio_client = socketio.Client(reconnection=True, reconnection_delay=3)


    @sio_client.event
    def connect():
        sio_client.emit('message', {'body':'local_connected'})


    @sio_client.event
    def message(data={}):   
        pass


    sio_client.connect('http://localhost:8000')
    while True:
        try:
            x = q_xmpp.get()
            sio_client.emit('message', x)
        except:
            pass


def create_app(gb=None, q_send=None):

    if gb is None: gb = GdrBot('LOGIN', 'PASSWORD')
    if q_send is None: q_send = Queue() #stores messages received from socket to be sent to xmpp
    
    q_xmpp = Queue() #stores messages received from xmpp server to local

    p = multiprocessing.Process(target=xmpp_worker, 
                                args=(gb, q_xmpp, q_send), 
                                daemon=True)

    d = multiprocessing.Process(target=start_sio_client, 
                                args=(q_xmpp, q_send), 
                                daemon=True)
    
    app = socket_server.create_app(gb, q_send)
    
    p.start()
    d.start()

    return app


if __name__ == '__main__':
    app = create_app(GdrBot('LOGIN', 'PASSWORD'))
    Path(f"./chats").mkdir(parents=True, exist_ok=True)
    Path(f"./data").mkdir(parents=True, exist_ok=True)
    Path(f"./debug").mkdir(parents=True, exist_ok=True)
    #app.run( host='0.0.0.0', port=8000)#, threads=os.cpu_count(), expose_tracebacks=True)
    serve(app, host='0.0.0.0', port=8000, threads=os.cpu_count(), expose_tracebacks=True)
