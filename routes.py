from flask import Blueprint, render_template, abort, request, redirect, jsonify
from jinja2 import TemplateNotFound
import json
from pathlib import Path
from my_utils import *
import time
from multiprocessing import Pool
import multiprocessing
import os

main_df=None
gb = None 

routes_template = Blueprint('routes_template', __name__)


def register(bot):
    '''
    Registers the GdrBot Object as a global variable
    bot <GdrBot>: The bot to be used by routes
    '''
    assert bot is not None, 'Bot registered in routes is invalid.'
    global gb
    gb = bot 


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        else:
            return super(NpEncoder, self).default(obj)


@routes_template.route('/get_data')
def get_data():
    '''
        Open files in ./data and returns location and density
        INPUT: None
        OUTPUT: list<dict<location:tuple, weight:double>>
    '''
    max_age = 99#int(request.args.get('maxAge'))
    min_age = 18#int(request.args.get('minAge'))
    archives = os.listdir('./data')
    pool = Pool(processes=multiprocessing.cpu_count()-1)
    res = pool.map_async(process_file_density, archives).get()
    return jsonify(res)


def route_log(e):
    with open('./debug/routes.log', 'a', encoding='utf-8') as f:
        f.write(f'{e}\n')


@routes_template.route('/render_message', methods=['GET', 'POST'])
def render_message():
    res = gb.make_message(dict(request.args))
    return render_template('single_message.html', message=res)


@routes_template.route('/get_single_profile', methods=['GET'])
def get_user_profile():
    uid = request.args.get('uid')
    x = gb.get_user_profile(uid)
    return render_template("single_profile.html", info=x['profiles'][0])


@routes_template.route('/user_chats',methods=['GET'])
def get_user_chats():
    uid = request.args.get('uid')
    address = f'./chats/{gb.get_pid()}/{uid}.csv'
    try:
        address = f'./chats/{gb.get_pid()}/{uid}.csv'
        df = pd.read_csv(address)
    except:
        gb.save_message({
            'targetProfileId':f'{uid}@chat.grindr.com',
            'sourceProfileId':f'{gb.get_pid()}',
            'type':'received',
            'body':'initchat'
            })

    df = pd.read_csv(address)
    return render_template('chat_window.html', msgs=df.to_dict('records'))


@routes_template.route('/get_chat_heads', methods=['GET'])
def get_all_chat_heads():

    Path(f"./chats/{gb.get_pid()}").mkdir(parents=True, exist_ok=True)
    files = os.listdir(f'./chats/{gb.get_pid()}')

    ids = [i[:-4] for i in files]
    profiles_ = pd.DataFrame(gb.get_multiple_profiles(ids)['profiles'])

    _chats = []
    for i in ids:
        try:
            df = pd.read_csv(f'./chats/{gb.get_pid()}/{i}.csv')
            df = df[df['type'].isin(['text', 'image'])]
            df = df.sort_values(by=['timestamp'])
            
            assert df.shape[0] > 0, 'Empty DataFrame'
            
            last_msg = df.iloc[-1]
            last_msg = dict(last_msg)
            last_msg['chatId'] = i
            last_msg['profile'] = profiles_[profiles_['profileId'] == i]
            last_msg['profile'] = last_msg['profile'].to_dict('records')[0]
            _chats.append(last_msg)
        except:
            pass

    return render_template('chat_list.html',chats=sorted(_chats, 
                                            key=lambda i: -i['timestamp'] ))


@routes_template.route('/get_profile_grid', methods=['GET'])
def profile_grid():
    return render_template('profile_grid.html', 
        info = {'profiles':gb.get_latest_grid()})


@routes_template.route('/', methods=['POST', 'GET'])
def main_route():
    if request.method == 'POST' or 'GET':
        main_df = gb.get_nearby()
        return render_template( 'index.html',
                                inbox_panel=get_all_chat_heads())


@routes_template.route('/create_filters', methods=['GET'])
def create_filters():
    filters = json.load(open('./confs/filters.json', 'r'))
    prefs = json.load(open('./confs/preferences.json', 'r'))

    return render_template("filters.html", info=filters)