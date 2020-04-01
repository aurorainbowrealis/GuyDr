import socketio
from flask import Flask, render_template, request, redirect, jsonify
import os
import pandas as pd
import math
import time
from multiprocessing import  Queue
import multiprocessing
import pygeohash as pgh
from my_utils import *
import json
from datetime import datetime
from routes import routes_template, register
from filters import filters_template
from gdr_bot import GdrBot
from waitress import serve

q_send = None

def create_app(gb=None, q=None):
    '''
    Creates the app for deployment
    g <GdrBot>: A bot to connect the API
    q <multiprocessing.Queue>: A queue that will be used to hold the messages to be sent
    '''
    assert gb is not None, "gb -> A GdrBot bot should be provided"
    assert q is not None, "q -> A Queue should be provided"
    
    sio = socketio.Server(async_mode='threading')
    app = Flask(__name__)

    app.register_blueprint(routes_template)
    app.register_blueprint(filters_template)

    app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)
    browser_id = ''
    q_send = None

    @sio.event
    def message(sid, data):
        with open('msg.txt', 'w') as f:
            f.write(f'{data}\n')
           
        if data['body'] == 'User Connected':
            global browser_id
            browser_id = sid
            sio.emit('set_sid')
        elif data['body'] == 'local_connected': return

        sio.emit('message', data, skip_sid=[sid], room=browser_id)

        if sid == browser_id:   
            try:
                q_send.put(data)
            except Exception as e:
                with open('bot_log.log', 'a', encoding='utf-8') as f:
                    f.write(f'{e}\n')
    q_send = q

    register(gb)
    return app


def main(gb=None, q=None):
    global q_send
    q_send = q
    assert gb is not None, 'gb object should be GdrBot'
    assert q is not None, 'q should be a multiprocessing.queue'        
    # if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    #    register(gb)
    app = create_app(gb, q)
    #app.run(host='0.0.0.0', port=8000, debug=True, threaded=False)              #I left debug and threaded because WERKZEUG is not to be deployed
    serve(app, host='0.0.0.0', port=8000, threads=os.cpu_count(), expose_tracebacks=True)

if __name__ == '__main__':
    main(GdrBot('LOGIN', 'PASSWORD'), Queue())