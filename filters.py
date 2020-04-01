from flask import Blueprint, render_template, abort, request, redirect, jsonify
from jinja2 import TemplateNotFound
import json
import math
from datetime import datetime
import time

filters_template = Blueprint('filters_template', __name__)

@filters_template.app_template_filter('image_message')
def image_message(a):
    return json.loads(a)['imageHash']

@filters_template.app_template_filter('named_field')
def named_field_filter(fvalue,field):
    x = json.load(open('./confs/filters.json', 'r'))
    
    if type(fvalue) == str and fvalue[0] == '[':
        fvalue = fvalue[1,-1].replace(' ','').split(',')
    
    elif type(fvalue) == list:
        ret = [x[field]['fields'][i] for i in fvalue]
        try:
            return ', '.join(ret)
        except:
            return ""
    
    try:
        return x[field]['fields'][fvalue]
    except:
        return ""


@filters_template.app_template_filter('display_name')
def display_name_filter(a):
    try:
        return '' if math.isnan(a) else a
    except:
        return a


@filters_template.app_template_filter('to_int')
def to_int(a):
    if math.isnan(a): return ''
    return int(a)


@filters_template.app_template_filter('distance_filter')
def distance_filter(a):
    # return a
    if a == None: return '? m'
    if math.isnan(a): return '? m'
    if a > 1000:
        km = int(a // 1000)
        m = int(a - 1000 * km)
        return f'{km}km {m}m'
    return f'{int(a)}m'

@filters_template.app_template_filter('to_date')
def to_date(a):
    try:
        a = int(a)
        return datetime.fromtimestamp(a//1000).strftime('%m-%d %H:%M')
    except:
        return datetime.fromtimestamp(time.time()//1000).strftime('%m-%d %H:%M')


@filters_template.app_template_filter('elapsed_time')
def elapsed_time(a):
    if a == None or math.isnan(a): return ''
    delta = time.time() - int(a / 1000)
    days = delta // 86400
    if days > 0: return f"{int(days)} days"
    delta -= days * 86400
    hrs = int(delta // 3600)
    delta -= hrs * 3600
    mins = int(delta // 60)
    r =""
    if hrs > 0: r += f"{hrs}h "
    return r + f"{mins}m"


@filters_template.app_template_filter('height_meters')
def height_meters(a):
    if a != None:
        return round(a / 100, 3)


@filters_template.app_template_filter('to_kilos')
def to_kilos(a):
    if a != None:
        return a // 1000
    return -1
