from multiprocessing import Queue
import requests
import json
import time
from xmpp_bot import XMPPBot
from gdr_bot import GdrBot
import logging
from gdr_bot import GdrBot

def xmpp_worker(gb, q, q_send):
    '''
    threaded function that runs a xmpp client
    q <Queue>: A queue shared by multiple threads
    '''
    #logging.basicConfig(level=logging.DEBUG,format='%(levelname)-8s %(message)s')

    global my_profile_id
    global my_xmpp_token

    xmpp = XMPPBot(gb, q, q_send)

    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping
    xmpp.register_plugin('xep_0012') # Last Activity
    xmpp.register_plugin('xep_0085') # Chat State
    xmpp.register_plugin('xep_0108') # User Activity
    
    xmpp.connect(address=('chat.grindr.com', 5222))
    xmpp.process(timeout=None, forever=True)

def main():
    q1 = Queue()
    q2 = Queue()
    gb = GdrBot('LOGIN', 'PASSWORD')

    chat_agent = xmpp_worker(gb, q1, q2)

if __name__ == '__main__':
    main()