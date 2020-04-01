import slixmpp
import time
import json
import joblib
import logging
import pandas as pd
from os import path
from gdr_bot import GdrBot
from multiprocessing import Queue
import traceback
from singleton import Singleton

class XMPPBot(slixmpp.ClientXMPP, metaclass=Singleton):

    """
    TODO: Document
    """

    def __init__(self, gb, q_xmpp, q_send):
        
        slixmpp.ClientXMPP.__init__(self, gb.get_jid(), gb.get_xmpp_token())

        self.recipient=''
        self.q_xmpp = q_xmpp
        self.q_send = q_send
        self.gb = gb

        self.add_event_handler("message", self.message)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler('chatstate_composing', self.composing)
        self.add_event_handler('chatstate_active', self.active)

    def composing(self, msg):
        pass
        #logging.debug(f'<{msg}>')

    def active(self, msg):
        pass
        #logging.debug(f'[{msg}]')


    def start(self, event):
        #print("Started")
        #self.log('Started')
        self.send_presence()
        self.schedule(name ='send_chat', callback=self.chat_send, seconds=1, repeat=True)
        #self.schedule(name ='update_grid', callback=self.update_grid, seconds=600, repeat=True)


    def chat_send(self):

        '''
        Continuously check if there are any messages to be sent.
        If any, dispatches them to their targets.
        '''
        try:
            message = self.q_send.get(block=False) 
            self.my_send(message)
        except Exception as e:
            if e != '':
                self.log(traceback.format_exc())


    def log(self, e):
        '''
        Logs a text in a specific file
        e<str> -> text to be written
        '''
        with open('./debug/bot_log.log', 'a') as f:
            f.write(f'{e}\n')


    def my_send(self, msg):
        '''
        Sends a message from the current client to a given recipient
        recipient <str or int> : jid of the recipient (jid = jabber id, e.g. 12345@domain.com/12345_optional)
        '''

        my_msg = self.gb.make_message(msg)
        del my_msg['recv']

        try:
            self.gb.save_message(my_msg)
        except:
            raise
        
        self.send_message(mto=msg['targetProfileId'], mfrom=self.boundjid.bare, #If doesnt work, remove recv from gb.make_message
            mbody=json.dumps(my_msg), mtype='chat')
        print("Sent message: ", my_msg)
        #self.disconnect(wait = True, reconnect=True, send_close=False)


    def message(self, msg):
        x = {'from':str(msg['from']), 'body':json.loads(msg['body'])}
        x['body']['recv'] = True
        if str(msg['from']) != str(self.boundjid.bare):
            self.q_xmpp.put(x['body'])
        self.log(str(x))
        try:
            self.gb.save_message(x['body'])
        except Exception as e:
            raise e
        print("Received message: ", msg)

