import requests
import json
import pandas as pd
import pygeohash as pgh
import time 
import uuid
import datetime
import base64
import numpy as np
from pathlib import Path
import os
import sys
from singleton import Singleton

class GdrBot(object, metaclass=Singleton):
    """
        Class that defines the connector to Grindr API
        email <str> : an email to login in the account
        password <str> : a password to the account
    """
    def __init__(self, email, password):
        self.unlimited = True
        self.MAIN_URL = "https://grindr.mobi/"
        self.__EMAIL = email
        self.__PASSWORD = password
        self.login_payload = {'email':email, 'password':password}
        self.profile_id = None
        self.xmpp_token = ''
        self.position = 'VALID_GEOHASH'
        self.chat_domain = '@chat.grindr.com'
        self.profile = None
        self.features = None

        #Headers used for login
        self.login_headers = json.load(open('./confs/login_headers.json', 'r'))
        #Headers used for all calls
        self.headers = json.load(open('./confs/all_headers.json', 'r'))
        #headers used to retrieve a GCM token
        self.gcm_headers = json.load(open('./confs/gcm_headers.json', 'r'))
        # parameters to collect a gcm token
        self.gcm_params = json.load(open('./confs/gcm_params.json', 'r'))
        #URLs used for requests
        self.urls = json.load(open('./confs/urls.json', 'r'))
        #Preferences used for search
        self.__preferences = json.load(open('./confs/preferences.json', 'r'))
        
        self.__latest_grid = None

        self.start()

    def get_my_profile(self):
        return self.get_result(self.urls['my_profile'])


    def get_preferences(self):
        '''Returns the filtering preferences'''
        return self.__preferences


    def set_preferences(self, pref):
        '''
        Receives a dictionary pref and updates the values in the filtering preferences then saves it
        pref <dict> : a dictionary of preferences
        '''
        for i in pref:
            assert i in self.__preferences.keys(), "Invalid Preferences"

        for i in pref:
            self.__preferences[i] = pref[i]

        self.save_preferences()


    def save_preferences(self):
        '''Saves the filtering preferences to a local file'''
        with open('./confs/urls.json', encoding='utf-8') as f:
            f.write(json.dumps(self.__preferences))


    def set_all_preferences(self, val):
        '''
        Sets all preferences at once, the whole preferences dictionary needs to be passed
        val <dict> : a dictionary of preferences
        '''
        assert len(val.keys()) == len(self.__preferences.keys()), 'Invalid preferences set'
        for i in val:
            assert i in self.__preferences.keys(), "Invalid preferences"

        for i in val:
            self.__preferences[i] = val[i]

        self.__preferences = val
        

    def get_position(self):
        '''Returns the geographic position as a geohash
        returns <str> : '''
        return self.position


    def get_jid(self):
        '''
        returns the jid for the agent
        returns <str> : jig e.g. 123456@bar.com
        '''
        return self.profile_id + self.chat_domain


    def get_pid(self):
        '''
        returns the pid for the agent
        returns <str> : pid e.g. 123456
        '''
        assert self.profile_id != None, "Invalid profile ID"
        return self.profile_id


    def get_user_profile(self, uid):
        '''
        collects tht profile for a single user
        uid <str> : the profileId of the user to be collected
        returns <dict> : profile information data
        '''
        return self.get_result(self.urls['user_profile'] + str(uid))


    def get_xmpp_token(self):
        '''
        returns the xmpp token for the session
        returns <str> : the xmpp token
        '''
        return self.xmpp_token
    
    def get_local_pid(self):
        x = json.loads(open('./login/users.json', 'r', encoding='utf-8').read())
        return x[f'{self.__EMAIL}{self.__PASSWORD}']


    def save_local_pid(self):
        x = json.loads(open('./login/users.json', 'r', encoding='utf-8').read())
        x.update({f'{self.__EMAIL}{self.__PASSWORD}':self.get_pid()})
        with open('./login/users.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(x))


    def get_token_features(self, token):
        x = json.loads(self.decrypt_token(token))
        return x['features']


    def decrypt_token(self, token, debug=False):
        if debug:
            self.log("Decrypting Token")
            self.log(token)
        token = token.split('.')
        base64_message = token[1]+'=='
        base64_bytes = base64_message.encode()
        message_bytes = base64.b64decode(base64_message)
        decrypted = message_bytes.decode()
        if debug:
            self.log("Decrypted token")
            self.log(decrypted)
        return decrypted


    def get_token_expiry(self, res, debug=False):
        if debug:
            self.log("Checking token expiry")
            self.log(res)
        features = json.loads(self.decrypt_token(res['xmppToken'], debug))
        return features['exp']


    def key_is_valid(self, res, debug=False):
        '''
        Decrypts and checks if a key is still valid
        res <dict> : a key to be validated
        returns <bool> : True if key is valid, false otherwise
        '''
        if debug:
            self.log("Checking key valid")
            self.log(res)
        return int(time.time()) < self.get_token_expiry(res, debug)


    def do_login(self):
        '''
            Login into grindr
        '''
        res = None

        try:
            pid = self.get_local_pid()
            res = json.load(open(f'./login/{pid}/login.json'))
            assert self.key_is_valid(res)
        except:
            gcm = self.get_gcm()
            res = self.get_result(self.urls['sessions'], headers_=self.login_headers, 
                            data_=json.dumps(self.login_payload), req_type='post')
            if "code" in res.keys() and res['code'] == 6:
                self.get_gcm(True)

            Path(f"./login/{res['profileId']}").mkdir(parents=True, exist_ok=True)
            with open(f"./login/{res['profileId']}/login.json", 'w', encoding='utf-8') as f:
                f.write(json.dumps(res))

        token = self.xmpp_token = res['sessionId']
        self.profile_id = res['profileId']
        self.headers['Authorization'] = f"Grindr3 {token}"
        self.save_local_pid() 

        return res


    def log(self, e):
        with open('./debug/gdr_bot.log', 'a', encoding='utf-8') as f:
            f.write(f'{e}\n')


    def get_gcm(self):
        '''
            Requests a gcm token from the google server.
            INPUT: NONE
            OUTPUT: dict<gcm_token: <str>, gcm_token_time:<int>>
        '''
        r = requests.post("https://android.clients.google.com/c2dm/register3",
                      headers = self.gcm_headers, data=self.gcm_params)
        self.login_payload['token'] = r.text[6:]

        return self.login_payload['token']



    def estimate_distances(self, a):
        dist = 0
        for i in range(len(a['profiles'])):
            a['profiles'][i]['isOnline'] = (time.time() - a['profiles'][i]['seen']//1000 < 600)

            if a['profiles'][i]['distance'] != None:
                dist = a['profiles'][i]['distance']
                a['profiles'][i]['distanceEstimated'] = False
            else:
                for j in a['profiles'][i+1:]:
                    if j['distance'] != None:
                        a['profiles'][i]['showDistance'] = True
                        a['profiles'][i]['distance'] = (dist + j['distance'])//2
                        dist = a['profiles'][i]['distance']
                        a['profiles'][i]['distanceEstimated'] = True
                        break
        return a


    def make_message(self, msg, debug=False):
        if msg is None: return
        if debug: self.log(msg)
        my_msg = dict()
        for i in ['body', 'type', 'timestamp', 'messageContext', 'messageId']:
            if i not in msg.keys():
                msg[i] = None

        if msg["type"] in ['received', 'displayed']:
            msg['body'] = False

        my_msg['body'] = msg['body'] or ""
        my_msg['targetProfileId'] = str(msg['targetProfileId']).split('@')[0]
        my_msg['recv'] = my_msg['targetProfileId'] == self.get_pid()
        
        if my_msg['recv']:
            my_msg['sourceProfileId'] = str(msg['sourceProfileId']).split('@')[0]
        else:
            my_msg['sourceProfileId'] = self.get_pid()
        
        my_msg['type'] = msg["type"] or "text"
        my_msg['messageId'] = msg['messageId'] or str(uuid.uuid1())
        my_msg['timestamp'] = msg['timestamp'] or int(time.time()) * 1000       #to milliseconds to comply with server
        my_msg['messageContext'] = msg['messageContext'] or ""
        my_msg['replyMessageBody'] = ""
        my_msg['replyMessageId'] = ""
        my_msg['replyMessageName'] = ""
        my_msg['replyMessageType'] = ""

        return my_msg


    def get_current_location(self):
        '''
        returns a tuple with the current location
        returns <tuple<str, tuple<float, float>>> : the string geohash of current location and a tuple with lat,lng
        '''
        return self.position, pgh.decode(self.position)


    def get_profile(self, profileId):
        '''
        returns the user profile for the profileId
        profileId <int>: the user profileId to be searched
        returns <dict> : the user profile
        '''
        return self.get_result(profile+f"/{profileId}")


    def set_incognito(self, status=True):
        '''
        only works if user is unlimited
        '''
        #print(self.get_result(self.urls['settings'], data_=json.dumps({"settings":{"incognito": status}}), req_type='put'))
        #print(self.get_result(self.urls['location'], data_=json.dumps({"geohash":self.position}), req_type='put'))
        pass


    def get_nearby(self, pos=None):
        '''
            Requests profiles nearby to the current location
            
            Params:
                pos <tuple>: a decoded geohash location that indicates the geo-center of the call
                unlimited <bool>: a boolean that indicates wether or not the member is Unlimited

            Preferences:
                Online: works anytime?
        '''
        _geohash = None
        grid = None

        if type(pos) is tuple or type(pos) is list:
            _geohash = pgh.encode(pos[0],pos[1], precision=12)
        elif pos is None: 
            _geohash = self.position#pgh.decode(self.position)
        else:
            _geohash = pos

        current_preferences = {i : j for i,j in self.__preferences.items() if j != ""}
        if self.unlimited:
            try:
                grid = self.get_result(
                    f'v4/locations/{_geohash}/unlimited-profiles?',
                    data_=current_preferences,
                    req_type='get')
                
                if "code" in grid.keys():
                    self.log("Problem Getting Grid")
                    self.log(grid)
                else:
                    self.log("Grid successfully retrieved!")

                grid = self.estimate_distances(grid)        
            except:
                self.do_login()
                grid = self.estimate_distances(self.get_result(f'v4/locations/{_geohash}/unlimited-profiles?',
                data_=current_preferences,req_type='get'))

            
        else:
            grid = self.get_result(
                f'v4/locations/{_geohash}/profiles',
                data_=current_preferences,
                req_type='get')

            if "code" in grid.keys():
                self.log("Problem Getting Grid")
                self.log(grid)
            else:
                self.log("Grid successfully retrieved!")

            grid = self.estimate_distances(grid)

        x = pd.DataFrame(grid['profiles'])
        x = x.set_index('profileId')
        now = datetime.datetime.now()
        x.to_csv(f'./data/{_geohash}_{int(time.time())}.csv', encoding='utf-8')
        self.__latest_grid = grid['profiles']
        return x


    def get_old_messages(self):
        return self.get_result(self.urls['messages'])


    def save_message(self, msg):

        msg = self.make_message(msg)
        Path(f'./chats/{self.get_pid()}').mkdir(parents=True, exist_ok=True)
        
        if int(msg['sourceProfileId']) != int(self.get_pid()):
            filename = msg['sourceProfileId']  
        else:
            filename = msg['targetProfileId']
        
        df = None
        address= f"./chats/{self.get_pid()}/{filename}.csv"

        try:
            df = pd.read_csv(address)
        except:
            df = pd.DataFrame(columns = msg.keys())

        df = df.append(msg, ignore_index = True)
        df.drop_duplicates('messageId', keep='last', inplace=True)              #needs optimization
        df.to_csv(address, index=False, encoding='utf-8')


    def save_multiple_messages(self, messages):
        for i in messages['messages']:
            self.save_message(i)


    def get_latest_grid(self):
        '''
        Returns the last set of profiles collected with get_nearby
        '''
        if self.__latest_grid is None:
            self.get_nearby()
        return self.__latest_grid


    def block_user(self, userid):
        '''
        Blocks the user "userid"
        userid <int> : profileId of the user to be blocked
        '''
        return self.get_result(self.urls['block_user'] + userid, req_type='post')


    def favorite_user(self, userid):
        '''
        Sets the user "userid" as a favorite
        userid <int>: profileId of the user to be favorited
        '''
        return self.get_result(self.urls['favorite'] + userid, req_type='post')


    def get_result(self, ext, headers_=None, data_={}, req_type='get'):
        '''
            executes a request to the server and saves it to a log
            INPUT:  ext<str> : the extension to a root api address
                    data<dict>: a dictionary of data to be sent
                    req_type<get>: the request type [get, post, put]

            OUTPUT: <dict> OR <str>
        '''
        if headers_ is None: headers_ = self.headers

        if req_type == 'get':
            r = requests.get(f'{self.urls["MAIN_URL"]}{ext}', headers = headers_, params=data_)
        elif req_type == 'post':
            r = requests.post(f'{self.urls["MAIN_URL"]}{ext}', headers = headers_, data=data_)
        elif req_type == 'put':
            r = requests.put(f'{self.urls["MAIN_URL"]}{ext}', headers = headers_, data=data_)
        try:
            return json.loads(r.text)
        except:
            return r.text


    def get_multiple_profiles(self, profiles):
        return self.get_result(self.urls['profiles'], None, json.dumps({'targetProfileIds':profiles}), 'post')


    def update_functionalities(self):
        self.unlimited = "Unlimited" in self.features


    def start(self):
        self.log("Started")
        self.do_login()
        msgs = self.get_old_messages()
        self.save_multiple_messages(msgs)
        self.features = self.get_token_features(self.xmpp_token)
        self.update_functionalities()


def main():
    gb = GdrBot('LOGIN', 'PASSWORD')
    print(gb.get_nearby())


if __name__ == '__main__':
    main()